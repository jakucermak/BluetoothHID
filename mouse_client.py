import dbus
import dbus.service
import dbus.mainloop.glib
import time
import evdev  # used to get input from the mouse
from evdev import InputDevice, ecodes
import argparse


HID_DBUS = 'org.yaptb.btkbservice'
HID_SRVC = '/org/yaptb/btkbservice'


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
                    devices = [evdev.InputDevice(fn)
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
            print("Left Mouse Button Pressed")
            self.state[2] = event.value
        elif event.code == ecodes.BTN_RIGHT:
            print("Right Mouse Button Pressed")
            self.state[2] = 2 * event.value
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

    # silmulate mouse movement using relative cooridinates
    def simulate_move(self, relX, relY):
        while relX != 0 or relY != 0:
            if relX > 0:
                self.state[3] = 1
                relX -= 1
            if relX < 0:
                self.state[3] = 255
                relX += 1
            
            if relY > 0:
                self.state[4] = 1
                relY -= 1
            if relY < 0:
                self.state[4]= 255
                relY += 1

            try:
                time.sleep(self.t)
                self.send_input()
                self.state[3] = 0
                self.state[4] = 0
            except Exception:
                print("Could not send mouse input.")
                break

    # forward mouse events to the dbus service
    def send_input(self):
        self.iface.send_mouse(self.state)


parser = argparse.ArgumentParser(
    description="Creates mouse client for control device(computer, phone,..) connected over BT over mouse or simulate movement")
parser.add_argument('--dev', default="mouse", type=str,choices=["mouse", "simulate"], help="set if you want to simulate mouse or use real device")
parser.add_argument('-x', default=0, type=int, help="Simulator only. Relative x position accepts positive and negative integers. Default is 0")
parser.add_argument('-y', default=0, type=int, help="Simulator only. Relative y position accepts positive and negative integers. Default is 0")
parser.add_argument('-t', default=0.05,type=float, help="Simulator only. Time in seconds. Acctepts Float. Higher number means \"pause\" between each steps is longer")

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
        mouse.simulate_move(args.x, args.y)
