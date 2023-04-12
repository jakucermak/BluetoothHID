import dbus
import dbus.service
import dbus.mainloop.glib
import time
import evdev  # used to get input from the mouse
from evdev import InputDevice, ecodes
import argparse

HID_DBUS = 'org.jc.btkbservice'
HID_SRVC = '/org/jc/btkbservice'


# define a client to listen to local mouse events
class Mouse:

    def __init__(self, mode: str, t: float = 0):
        # the structure for a bluetooth mouse input report (size is 6 bytes)

        print("Setting up DBus Client")

        self.bus = dbus.SystemBus()
        self.bluetoothservice = self.bus.get_object(HID_DBUS, HID_SRVC)
        self.iface = dbus.Interface(self.bluetoothservice, HID_DBUS)

        print("Waiting for mouse")

        # keep trying to find a mouse
        have_dev = False
        count = 0
        NUMBER_OF_TRIES = 100

        if mode == "mouse":
            while have_dev is False and count < NUMBER_OF_TRIES:
                try:
                    # try and get a mouse - loop through all devices and try to find a mouse
                    devices = [InputDevice(fn)
                               for fn in evdev.list_devices()]
                    for device in reversed(devices):
                        if "mouse" in device.name.lower():
                            print("Found a mouse with the keyword 'mouse'")
                            print("device name is " + device.name)
                            self.dev = InputDevice(device.path)
                            have_dev = True
                            break
                except OSError:
                    print("Mouse not found, waiting 3 seconds and retrying")
                    time.sleep(3)
                count += 1

            if not have_dev:
                print("Mouse not found after " +
                      str(NUMBER_OF_TRIES) + " tries.")
                return
            else:
                print("Mouse Found")
        self.t = t

    state = [
        0xA1,  # this is an input report
        0x02,  # Usage report = Mouse
        # Bit array for Buttons ( Bits 0...4 : Buttons 1...5, Bits 5...7 : Unused )
        0x00,
        0x00,  # Rel X
        0x00,  # Rel Y
        0x00,  # Mouse Wheel
    ]

    # take care of mouse buttons
    def change_state_button(self, event):
        if event.code == ecodes.BTN_LEFT:
            print(f'Button: {event.code}')
            print(f'Value {event.value}')
            self.state[2] = event.value
            print(f'State: {self.state[2]}')
        elif event.code == ecodes.BTN_RIGHT:
            print(f'Button: {event.code}')
            print(f'Value {event.value}')
            self.state[2] = 2 * event.value
            print(f'State: {self.state[2]}')
        elif event.code == ecodes.BTN_MIDDLE:
            print("Middle Mouse Button Pressed")
            self.state[2] = 3 * event.value
        self.state[3] = 0x00
        self.state[4] = 0x00
        self.state[5] = 0x00

    # take care of mouse movements
    def change_state_movement(self, event):
        if event.code == ecodes.REL_X:
            self.state[3] = event.value & 0xFF
        elif event.code == ecodes.REL_Y:
            self.state[4] = event.value & 0xFF
        elif event.code == ecodes.REL_WHEEL:
            self.state[5] = event.value & 0xFF

    # poll for mouse events
    def event_loop(self):
        for event in self.dev.read_loop():
            if event.type == ecodes.EV_KEY and event.value < 2:
                self.change_state_button(event)
            elif event.type == ecodes.EV_REL:
                self.change_state_movement(event)
            try:
                self.send_input()
            except Exception:

                print("Couldn't send mouse input")

    # simulate mouse movement using relative coordinates
    def simulate_move(self, rel_x, rel_y):

        self.state[3] = rel_x
        self.state[4] = rel_y

        try:
            time.sleep(self.t)
            self.send_input()
            self.state[3] = 0
            self.state[4] = 0
        except Exception as e:
            print(e)

    # simulate mouse click, parameter used to identify which button to use
    def simulate_click(self, button):

        if button > 0:
            self.state[2] = button * self.button_toggle(button)
        else:
            self.state[2] = self.button_toggle(button)
            pass

    def button_toggle(self, button):
        if self.state[2] / button == 0:
            return 1
        else:
            return 0

    # forward mouse events to the dbus service
    def send_input(self):
        self.iface.send_mouse(self.state)


parser = argparse.ArgumentParser(
    description="Creates mouse client for control device(computer, phone,..) connected over BT over mouse or simulate "
                "movement")
parser.add_argument('--dev', default="mouse", type=str, choices=[
    "mouse", "simulate"], help="set if you want to simulate mouse or use real device")

if __name__ == "__main__":
    print("Setting up mouse Client")

    args = parser.parse_args()
    if "mouse" == args.dev:
        mouse = Mouse("mouse")
        print("Starting mouse event loop")
        mouse.event_loop()
    elif "simulate" == args.dev:
        mouse = Mouse("simulate", args.t)
        print("Simulating mouse movement")
