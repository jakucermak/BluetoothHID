from utils.config import Config
from utils.logger import Logger, LogLevels
from clients.mouse_client import Mouse
import math

__CONFIG = Config()
LOGGER = Logger("blehidd")

def move(point):
        """
    The do_movement function emulates mouse movement by sending a series of
    mouse events to the host. The function takes two arguments, x and y, which are relative
    coordinates that specify how far the mouse should move in each direction. The function then
    calculates how many steps it will take to reach those coordinates and sends a series of
    mouse events with step_x and step_y values set accordingly.

    :param self: Represent the instance of the class
    :param point: argparse.Namespace: Pass the arguments to the function
    :return: Nothing
    :doc-author: Jakub Cermak
    """
        
        step_coeficient = __CONFIG.step_coeficient
        rel_x = int(point.x * step_coeficient)
        rel_y = int(point.y * step_coeficient)
        
        LOGGER.log("Initiate mouse movement with x: {} and y: {}".format(rel_x,rel_y), LogLevels.INFO)

        step_size_x = 128 if rel_x < 0 else 127
        step_size_y = 128 if rel_y < 0 else 127

        while rel_x != 0 or rel_y != 0:

            (rel_x, step_x, step_size_x) = rel_move(step_size_x, rel_x)
            (rel_y, step_y, step_size_y) = rel_move(step_size_y, rel_y)

            send_mouse_movement(step_x, step_y * step_coeficient)

def rel_move(step_size, rel):

        if rel > 0:
            step = step_divider(rel, step_size)
            rel -= step
            step_x = step
            step_size = step
        elif rel < 0:
            step = step_divider(rel, step_size)
            rel += 256 - step
            step_x = step
            step_size = step
        else:
            step_x = 0

        return (rel, step_x, step_size)


def step_divider(rel, step, speed = 1.0):

        step = math.ceil(step * speed)

        LOGGER.log("Pre-divide -- rel: {} step: {}".format(rel, step), LogLevels.INFO)
        if abs(rel) < 1:
            return 0
        elif 1 <= rel < step:

            while 1 <= rel < step:
                LOGGER.log("rel: {} step: {}".format(rel, step - (step/2)), LogLevels.INFO)
                step = math.ceil(step - (step / 2 ))
            return step
        elif rel >= step:
            LOGGER.log("rel: {} step: {}".format(rel,step), LogLevels.INFO)
            return step
        return 0

# MOUSE = Mouse()
def send_mouse_movement(rel_x, rel_y):
        """
    The send_mouse_events function is used to simulate mouse movement.

    :param self: Represent the instance of the class
    :param rel_x: Move the mouse horizontally
    :param rel_y: Move the mouse up and down
    :return: The mouse
    :doc-author: Jakub Cermak
    """

        try:
            MOUSE.simulate_move(rel_x, rel_y)
        except Exception as e:
            LOGGER.log(e, LogLevels.ERR)


def btn_press(btn_id):

    """
The do_btn_press function is a function that emulates a mouse click.

:param self: Represent the instance of the class
:param args: argparse.Namespace: Pass the arguments from the command line to the function
:return: The exception if there is one
:doc-author: Jakub Cermak
"""

    try:
        MOUSE.simulate_click(int(btn_id))
    except Exception as e:
        LOGGER.log(e, LogLevels.ERR)

