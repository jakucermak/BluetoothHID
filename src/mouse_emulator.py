from clients.mouse_client import Mouse
import argparse
import cmd2
from utils.logger import Logger 
from utils.enums import LogLevels, ConfigEnum as CE
from utils.config import Config

LOGGER = Logger("mouse_emulator")

class MouseEmulator(cmd2.Cmd):

    config = Config()

    def __init__(self, t=0.01):
        """
    The __init__ function is called when the class is instantiated.
    It sets up the instance of the class, and initializes any variables that need to be set before it can do anything useful.

    :param self: Represent the instance of the class
    :param t: Set the time delay between mouse movements
    :return: The mouse object
    :doc-author: Jakub Cermak
    """
        super().__init__()

        intro_string = """MouseEmulator is tool for emulation of mouse movement and button press.
        \nConfig file is set up for: {}""".format(CE.DEFAULT)
        print(self.config.get_device_os)
        if self.config.get_device_os != CE.DEFAULT:
            intro_string = """MouseEmulator is tool for emulation of mouse movement and button press.
         \nConfig file is set up for: \nOS: {} \nModel: {} """.format(self.config.get_device_os, self.config.get_device_model)

        self.intro = cmd2.style( intro_string, fg=cmd2.Fg.YELLOW)
        self.prompt = cmd2.style(
            'mouseEmulator>',
            fg=cmd2.Fg.BLUE)
        self.mouse = Mouse("simulate", t)

    # Argument parser for do_emulate_mouse_movement
    move_pars = cmd2.Cmd2ArgumentParser(description='Send mouse movement emulation')
    move_pars.add_argument('-x', default=0, type=int,
                           help="Simulator only. Relative x position accepts positive and negative integers. Default "
                                "is 0")

    move_pars.add_argument('-y', default=0, type=int,
                           help="Simulator only. Relative y position accepts positive and negative integers. Default "
                                "is 0")   

    @cmd2.with_argparser(move_pars)
    def do_move(self, args: argparse.Namespace):

        """
    The do_movement function emulates mouse movement by sending a series of
    mouse events to the host. The function takes two arguments, x and y, which are relative
    coordinates that specify how far the mouse should move in each direction. The function then
    calculates how many steps it will take to reach those coordinates and sends a series of
    mouse events with step_x and step_y values set accordingly.

    :param self: Represent the instance of the class
    :param args: argparse.Namespace: Pass the arguments to the function
    :return: Nothing
    :doc-author: Jakub Cermak
    """
        rel_x = int(args.x * self.config.get_step_coeficient)
        rel_y = int(args.y * self.config.get_step_coeficient)

        step_x = step_y = 0

        while rel_x != 0 or rel_y != 0:

            if rel_x > 0:
                rel_x -= self.config.step_size
                step_x = self.config.step_size
            if rel_x < 0:
                rel_x += self.config.step_size
                step_x = 256 - self.config.step_size
            if rel_y > 0:
                rel_y -= self.config.step_size
                step_y = self.config.step_size
            if rel_y < 0:
                rel_y += self.config.step_size
                step_y = 256 - self.config.step_size
            self.send_mouse_events(step_x, step_y)

            step_x = step_y = 0

    def send_mouse_events(self, rel_x, rel_y):
        """
    The send_mouse_events function is used to simulate mouse movement.

    :param self: Represent the instance of the class
    :param rel_x: Move the mouse horizontally
    :param rel_y: Move the mouse up and down
    :return: The mouse
    :doc-author: Jakub Cermak
    """
        try:
            self.mouse.simulate_move(rel_x, rel_y)
        except Exception as e:
            LOGGER.log(e, LogLevels.ERR)

    press_pars = cmd2.Cmd2ArgumentParser(description='Send mouse button press event')

    press_pars.add_argument('-b', '--button',
                            help="Select button no. to press [0 - for left click, 1 - for left click]. Same for button "
                                 "release")   

    @cmd2.with_argparser(press_pars)
    def do_btn_press(self, args: argparse.Namespace):

        """
    The do_btn_press function is a function that emulates a mouse click.

    :param self: Represent the instance of the class
    :param args: argparse.Namespace: Pass the arguments from the command line to the function
    :return: The exception if there is one
    :doc-author: Jakub Cermak
    """
        btn_id = args.button

        try:
            self.mouse.simulate_click(int(btn_id))
        except Exception as e:
            LOGGER.log(e, LogLevels.ERR)


if __name__ == "__main__":
    import sys

    c = MouseEmulator()
    sys.exit(c.cmdloop())
