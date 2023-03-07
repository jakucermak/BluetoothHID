from mouse_client import Mouse
import argparse


class MouseEmulator:

    def __init__(self, t = 0.05):

        self.mouse = Mouse("simulate", t)

    def emulate_mouse_movement(self, rel_x: int, rel_y: int):

        step_x = step_y = 0 

        while rel_x != 0 or rel_y != 0:

            if rel_x > 0:
                rel_x -= 1
                step_x = 1
            if rel_x < 0:
                rel_x += 1
                step_x = 255
            if rel_y > 0:
                rel_y -= 1
                step_y = 1
            if rel_y < 0:
                rel_y += 1
                step_y = 255
            self.send_mouse_emulator(step_x, step_y)

            step_x = step_y =  0

    def send_mouse_emulator(self, rel_x, rel_y):
        try:
            self.mouse.simulate_move(rel_x, rel_y)
        except Exception as e:
            print(e)

    def emulate_mouse_click():
        pass


parser = argparse.ArgumentParser()
parser.add_argument('-x', default=0, type=int,
                    help="Simulator only. Relative x position accepts positive and negative integers. Default is 0")
parser.add_argument('-y', default=0, type=int,
                    help="Simulator only. Relative y position accepts positive and negative integers. Default is 0")
parser.add_argument('-t', default=0.0, type=float,
                    help="Simulator only. Time in seconds. Acctepts Float. Higher number means \"pause\" between each steps is longer")

if __name__ == "__main__":
    print("Setting up mouse Emulator")

    args = parser.parse_args()

    try:
        mouse_emu = MouseEmulator()
        mouse_emu.emulate_mouse_movement(args.x, args.y)
    except Exception as e:
        print(e)
