import sys
import pygame
from scipy.interpolate import interp1d
from pydialog.pydialog import Dialog, DialogConfig, SnapToBottom, chat_dialog, DialogEventTypes
from typing import Optional, Tuple
import numpy as np

# Initialize Pygame
pygame.init()

# Set up display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
background_color = (255, 0, 0)  # Red
pygame.display.set_caption("Pygame Example")


d = Dialog(chat_dialog(screen))


def linear_interpolation(x, x1, y1, x2, y2):
    """
    Performs linear interpolation to find y at a given x.

    Args:
        x: The x-value for which to find the interpolated y-value.
        x1, y1: The coordinates of the first known point.
        x2, y2: The coordinates of the second known point.

    Returns:
        The interpolated y-value.
    """

    return y1 + (x - x1) * (y2 - y1) / (x2 - x1)

# def get_offset(d: Dialog, event: pygame.event.Event):
#     mx, my = event.pos
#     x, y = d.coords
#     offset_x = mx - x
#     offset_y = my - y
#     return offset_x, offset_y


prev_offset: Optional[Tuple[int, int]] = None


font = pygame.font.SysFont(None, 48)
# Main loop
off_x, off_y = None, None
queue = []
coords = []


class Draggable:
    def __init__():
        pass


dialog = dialog_config = SnapToBottom(screen=screen, height=40, padding_y=10, padding_x=10)
dialog = Dialog(dialog_config)

open_condition = False
while True:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:
                print("pressed h")
                if dialog.is_open():
                    open_condition = False
                else:
                    open_condition = True

        if open_condition:
            print("open")
            dialog.open() # Open Dialog
            dialog.write("Hello Dialog.") # Write text to dialog box.
        if not open_condition and dialog.is_open():
            dialog.clear() # empty text
            dialog.close() # close dialog box
    #     d.event_checker(event)
    #     if event.type == pygame.MOUSEMOTION:
    #         x, y = event.pos
    #         screen.blit(font.render(f"{event.pos}", True, (0, 0, 0)), event.pos)
    #     if event.type == pygame.QUIT:
    #         pygame.quit()
    #         sys.exit()

    # for dialog_event in d.emit_events():
    #     if dialog_event.dialog_event_type == DialogEventTypes.press:
    #         off_x, off_y = get_offset(d, dialog_event.event)
            
    #     if dialog_event.dialog_event_type == DialogEventTypes.press_and_move:
            # if len(queue) < 4:
            #     queue.append(event.pos)
            # else:
            #     linear_interp = interp1d([xy[0] for xy in queue], [xy[1] for xy in queue], kind="linear")
            #     x_new = np.linspace(queue[0], queue.pop(), 4)
            #     y_new = linear_interp(x_new)
            #     coords = list(zip(x_new, y_new))
            #     queue.clear()

            # if coords:
            # mx, my = event.pos
            # mx, my = event.pos
            # d.coords = mx - off_x, my - off_y

    screen.fill(background_color)

    d.render(screen)

    pygame.display.flip()
    pygame.time.Clock().tick(24)
