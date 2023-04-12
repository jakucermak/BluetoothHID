from mouse_client import Mouse
import argparse
import cmd2


class MouseEmulator(cmd2.Cmd):

    def __init__(self, t=0.00):
        """
    The __init__ function is called when the class is instantiated.
    It sets up the instance of the class, and initializes any variables that need to be set before it can do anything useful.

    :param self: Represent the instance of the class
    :param t: Set the time delay between mouse movements
    :return: The mouse object
    :doc-author: Jakub Cermak
    """
        super().__init__()
        self.intro = cmd2.style(
            'mouseEmulator is tool for emulation of mouse movement and button press',
            fg=cmd2.Fg.RED)
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
    def do_movement(self, args: argparse.Namespace):

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
        rel_x = args.x
        rel_y = args.y

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
            self.poutput(e)

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
            self.poutput(f'type: {type(btn_id)}')
            self.poutput(f'Error: {e}')


if __name__ == "__main__":
    import sys

    c = MouseEmulator()
    sys.exit(c.cmdloop())
