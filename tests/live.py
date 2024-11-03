import sys
import pygame
from pydialog.pydialog import Dialog, chat_dialog, DialogEventTypes
from typing import Optional, Tuple

# Initialize Pygame
pygame.init()

# Set up display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
background_color = (255, 0, 0)  # Red
pygame.display.set_caption("Pygame Example")


d = Dialog(chat_dialog(screen))


def get_offset(d: Dialog, event: pygame.event.Event):
    mx, my = event.pos
    x, y = d.coords
    offset_x = mx - x
    offset_y = my - y
    return offset_x, offset_y


prev_offset: Optional[Tuple[int, int]] = None


font = pygame.font.SysFont(None, 48)
# Main loop
off_x, off_y = None, None
while True:
    # Handle events
    for event in pygame.event.get():
        d.event_checker(event)
        if event.type == pygame.MOUSEMOTION:
            x, y = event.pos
            screen.blit(font.render(f"{event.pos}", True, (0, 0, 0)), event.pos)
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    for dialog_event in d.emit_events():
        # if dialog_event.dialog_event_type == DialogEventTypes.press:
            
        if dialog_event.dialog_event_type == DialogEventTypes.press_and_move:
            print("press and move")
            if not off_x and not off_y:
                off_x, off_y = get_offset(d, dialog_event.event)
            mx, my = event.pos
            d.coords = mx - off_x, my - off_y

    screen.fill(background_color)

    d.render(screen)

    pygame.display.flip()
    pygame.time.Clock().tick(24)
