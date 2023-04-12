import dbus
import evdev
from evdev import InputDevice
import keymap

from sshkeyboard import listen_keyboard

from time import sleep

HID_DBUS = 'org.jc.btkbservice'
HID_SRVC = '/org/jc/btkbservice'


class Kbrd:
    """
    Take the events from a physically attached keyboard and send the
    HID messages to the keyboard D-Bus server.
    """

    def __init__(self):
        self.target_length = 6
        self.mod_keys = 0b00000000
        self.pressed_keys = []
        self.have_kb = False
        self.dev = None
        self.bus = dbus.SystemBus()
        self.btkobject = self.bus.get_object(HID_DBUS,
                                             HID_SRVC)
        self.btk_service = dbus.Interface(self.btkobject,
                                          HID_DBUS)
        self.wait_for_keyboard()

    def wait_for_keyboard(self, event_id=0):
        """
        Connect to the input event file for the keyboard.
        Can take a parameter of an integer that gets appended to the end of
        /dev/input/event
        :param event_id: Optional parameter if the keyboard is not event0
        """

        while self.have_kb is False:
            try:
                devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
                for device in reversed(devices):
                    if "keyboard" in device.name.lower():
                        print("Found a keyboard with the keyword 'keyboard'")
                        print("device name is " + device.name)
                        self.dev = InputDevice(device.path)
                        self.have_kb = True
                        break
            except OSError:
                print('Keyboard not found, waiting 3 seconds and retrying')
                sleep(3)

    def update_mod_keys(self, mod_key, value):
        """
        Which modifier keys are active is stored in an 8 bit number.
        Each bit represents a different key. This method takes which bit
        and its new value as input
        :param mod_key: The value of the bit to be updated with new value
        :param value: Binary 1 or 0 depending if pressed or released
        """
        bit_mask = 1 << (7 - mod_key)
        if value:  # set bit
            self.mod_keys |= bit_mask
        else:  # clear bit
            self.mod_keys &= ~bit_mask

    def update_keys(self, norm_key, value):
        if value < 1:
            self.pressed_keys.remove(norm_key)
        elif norm_key not in self.pressed_keys:
            self.pressed_keys.insert(0, norm_key)
        len_delta = self.target_length - len(self.pressed_keys)
        if len_delta < 0:
            self.pressed_keys = self.pressed_keys[:len_delta]
        elif len_delta > 0:
            self.pressed_keys.extend([0] * len_delta)

    @property
    def state(self):
        """
        property with the HID message to send for the current keys pressed
        on the keyboards
        :return: bytes of HID message
        """
        return [0xA1, 0x01, self.mod_keys, 0, *self.pressed_keys]

    def send_keys(self):
        self.btk_service.send_keys(self.state)

    def event_loop(self):
        """
        Loop to check for keyboard events and send HID message
        over D-Bus keyboard service when they happen
        """
        print('Listening...')
        for event in self.dev.read_loop():

            # only bother if we hit a key and its an up or down event
            if event.type == evdev.ecodes.EV_KEY and event.value < 2:
                key_str = evdev.ecodes.KEY[event.code]
                mod_key = keymap.modkey(key_str)
                if mod_key > -1:
                    self.update_mod_keys(mod_key, event.value)
                else:
                    self.update_keys(keymap.convert(key_str), event.value)
            self.send_keys()

    def onPress(self, key):
        self.update_keys(keymap.convert(f"KEY_{key.upper()}"), 1)
        self.send_keys()

    def onRelease(self, key):
        self.update_keys(keymap.convert(f"KEY_{key.upper()}"), 0)
        self.send_keys()

    def event_loop_term(self):
        listen_keyboard(on_press=self.onPress, on_release=self.onRelease)


if __name__ == '__main__':
    print('Setting up keyboard')
    kb = Kbrd()

    print('starting event loop')
    kb.event_loop()
