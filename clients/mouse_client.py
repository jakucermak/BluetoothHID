import dbus
import dbus.service
import dbus.mainloop.glib
import time
import evdev  # used to get input from the mouse
from evdev import InputDevice, ecodes
import argparse
from utils.logger import Logger, LogLevels 

HID_DBUS = 'org.jc.btkbservice'
HID_SRVC = '/org/jc/btkbservice'
LOGGER = Logger("mouse_client")

class Mouse:

    def __init__(self, mode: str, t: float = 0):
        """
    The __init__ function is called when the class is instantiated.
    It sets up the DBus connection and waits for a mouse to be connected.
    If it can't find a mouse after 100 tries, it will exit.

    :param self: Represent the instance of the class
    :param mode: str: Determine whether the device is a mouse or keyboard
    :param t: float: Set the time between each mouse movement
    :doc-author: Jakub Cermak
    """
        LOGGER.log("Setting up DBus Client", LogLevels.INFO)

        self.bus = dbus.SystemBus()
        self.bluetoothservice = self.bus.get_object(HID_DBUS, HID_SRVC)
        self.iface = dbus.Interface(self.bluetoothservice, HID_DBUS)

        LOGGER.log("Waiting for mouse", LogLevels.INFO)

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
                            LOGGER.log("Found a mouse with the keyword 'mouse'", LogLevels.INFO)
                            LOGGER.log("device name is " + device.name, LogLevels.INFO)
                            self.dev = InputDevice(device.path)
                            have_dev = True
                            break
                except OSError:
                    LOGGER.log("Mouse not found, waiting 3 seconds and retrying", LogLevels.ERR)
                    time.sleep(3)
                count += 1

            if not have_dev:
                LOGGER.log("Mouse not found after " +
                      str(NUMBER_OF_TRIES) + " tries.", LogLevels.INFO)
                return
            else:
                LOGGER.log("Mouse Found", LogLevels.INFO)
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
        """
    The change_state_button function is called when the mouse button is pressed.
    It takes in an event as a parameter and checks to see if it's one of the three buttons on the mouse.
    If it is, then we change our state array to reflect that button being pressed.

    :param self: Represent the instance of the class
    :param event: Get the event code and value from the mouse
    :return: The state of the mouse
    :doc-author: Jakub Cermak
    """
        if event.code == ecodes.BTN_LEFT:
            self.state[2] = event.value
        elif event.code == ecodes.BTN_RIGHT:
            self.state[2] = 2 * event.value
        elif event.code == ecodes.BTN_MIDDLE:
            self.state[2] = 3 * event.value
        self.state[3] = 0x00
        self.state[4] = 0x00
        self.state[5] = 0x00

    # take care of mouse movements
    def change_state_movement(self, event):
        """
    The change_state_movement function is used to update the state of the mouse.
    The function takes in an event as a parameter and checks if it is a movement event.
    If so, then it updates the state of that particular axis with its value.

    :param self: Represent the instance of the class
    :param event: Get the event code and value from the mouse
    :return: The state of the mouse
    :doc-author: Jakub Cermak
    """
        if event.code == ecodes.REL_X:
            self.state[3] = event.value & 0xFF
        elif event.code == ecodes.REL_Y:
            self.state[4] = event.value & 0xFF
        elif event.code == ecodes.REL_WHEEL:
            self.state[5] = event.value & 0xFF

    # poll for mouse events
    def event_loop(self):
        """
    The event_loop function is the main function of this class. It reads events from the device and calls
    the change_state_button and change_state_movement functions to update the state of buttons and movement, respectively.
    It then sends input to a server using send_input.

    :param self: Refer to the current instance of a class
    :doc-author: Jakub Cermak
    """
        for event in self.dev.read_loop():
            if event.type == ecodes.EV_KEY and event.value < 2:
                self.change_state_button(event)
            elif event.type == ecodes.EV_REL:
                self.change_state_movement(event)
            try:
                self.send_input()
            except Exception:
                LOGGER.log("Couldn't send mouse input", LogLevels.ERR)

    def simulate_move(self, rel_x, rel_y):

        """
    The simulate_move function takes in two arguments, rel_x and rel_y.
    rel_x is the relative x-coordinate of the mouse movement, while rel_y is the relative y-coordinate of the mouse movement.
    The function then sets self.state[3] to be equal to rel_x and self.state[4] to be equal to rel_y (the 3rd and 4th elements in state are for x/y coordinates).
    It then sleeps for t seconds (t being a class variable) before sending input with send input().

    :param self: Access the attributes and methods of a class
    :param rel_x: Determine the relative x position of the mouse
    :param rel_y: Move the mouse up and down
    :return: The new state of the mouse
    :doc-author: Jakub Cermak
    """
        self.state[3] = rel_x
        self.state[4] = rel_y

        try:
            time.sleep(self.t)
            self.send_input()
            self.state[3] = 0
            self.state[4] = 0
        except Exception as e:
            LOGGER.log(e, LogLevels.ERR)

    def simulate_click(self, button):
        """
    The simulate_click function takes in a button number and simulates a click of that button.
        If the button is positive, it will toggle the state of that specific bit to 1.
        If the button is negative, it will toggle all bits to 0.

    :param self: Represent the instance of the class
    :param button: Determine which button is being pressed
    :return: The state of the mouse
    :doc-author: Jakub Cermak
    """
        if button > 0:
            self.state[2] = button * self.button_toggle(button)
        else:
            self.state[2] = self.button_toggle(button)

    def button_toggle(self, button):

        """
    The button_toggle function takes a button as an argument and returns the opposite of its current state.
        If the button is currently pressed, it will return 0 (unpressed).
        If the button is currently unpressed, it will return 1 (pressed).

    :param self: Access the attributes and methods of a class
    :param button: Determine which button is being pressed
    :return: The state of the button
    :doc-author: Jakub Cermak
    """
        if self.state[2] / button == 0:
            return 1
        else:
            return 0

    def send_input(self):
        """
    The send_input function is used to send the mouse state to the interface.
    The function takes no arguments and returns nothing. The function uses
    the iface variable from the class, which is an instance of a class that
    implements a method called send_mouse(state).

    :param self: Refer to the current instance of a class
    :return: The state of the mouse
    :doc-author: Jakub Cermak
    """
        LOGGER.log(self.state,LogLevels.INFO)
        self.iface.send_mouse(self.state)


parser = argparse.ArgumentParser(
    description="Creates mouse client for control device(computer, phone,..) connected over BT over mouse or simulate "
                "movement") #pyright: ignore [reportImplicitStringConcatenation]
parser.add_argument('--dev', default="mouse", type=str, choices=[
    "mouse", "simulate"], help="set if you want to simulate mouse or use real device")

if __name__ == "__main__":
    LOGGER.log("Setting up mouse Client", LogLevels.INFO)

    args = parser.parse_args()
    if "mouse" == args.dev:
        mouse = Mouse("mouse")
        LOGGER.log("Starting mouse event loop", LogLevels.INFO)
        mouse.event_loop()
    elif "simulate" == args.dev:
        mouse = Mouse("simulate", args.t)
        LOGGER.log("Simulating mouse movement", LogLevels.INFO)
