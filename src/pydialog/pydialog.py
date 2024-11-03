from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import pygame

# Colors


RGBA = Tuple[int, int, int, int]
RGB = Tuple[int, int, int]
Coordinate = Tuple[int, int]


class DialogConfig:
    fail_flag: bool
    warn_flag: bool

    x: int
    y: int
    width: int
    height: int

    color: RGB
    opacity: int

    # snap_x: bool
    # snap_l: Optional[int] = None
    # snap_r: Optional[int] = None

    # snap_y: bool
    # snap_t: Optional[int] = None
    # snap_b: Optional[int] = None

    # def __init__(
    #     self,
    #     *,
    #     color: RGB,
    #     x: Optional[int],
    #     y: Optional[int],
    #     width: Optional[int],
    #     height: Optional[int],
    #     opacity: int = 255,
    #     snap_x: bool = False,
    #     snap_y: bool = False,
    #     snap_l: Optional[int] = None,
    #     snap_r: Optional[int] = None,
    #     snap_t: Optional[int] = None,
    #     snap_b: Optional[int] = None,
    # ) -> None:
    #     pass
        


def chat_dialog(screen: pygame.Surface):
    d = DialogConfig()
    screen_w, screen_h = (screen.get_width(), screen.get_height())
    d.width, d.height = screen_w - screen_w * 0.2, screen_h * 0.2
    d.x, d.y = screen_w * 0.1, screen_h * 0.75
    d.color = (0, 0, 0)
    d.opacity = 128
    return d


class DialogEventTypes(Enum):
    press_and_move = 1
    release = 2
    press = 3


class DialogEvent:
    dialog_event_type: DialogEventTypes

    def __init__(
        self, dialog_event_type: DialogEventTypes, event: pygame.event.Event
    ) -> None:
        self.event = event
        self.dialog_event_type = dialog_event_type


class DialogState:
    pressed: bool = False


class Dialog:
    surface: pygame.Surface
    width: int
    height: int
    coords: Tuple[int, int]
    color: pygame.Color
    event_queue: List[DialogEvent] = []

    state: DialogState

    def __init__(self, config: DialogConfig) -> None:
        self.coords = config.x, config.y
        self.width = config.width
        self.height = config.height
        self.color = (*config.color, config.opacity)
        self.surface = pygame.surface.Surface(
            (self.width, self.height), pygame.SRCALPHA
        )
        self.state = DialogState()

    def render(self, screen: pygame.Surface):
        self.surface.fill(self.color)
        screen.blit(self.surface, self.coords)

    def update_offset(self, event: pygame.event.Event):
        if event.type in [pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]:
            mx, my = event.pos
            x, y = self.coords
            self.state.mouse_offset_x = mx - x
            self.state.mouse_offset_y = my - y

    def event_checker(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            mx, my = mouse_pos
            x, y = self.coords
            w, h = self.width, self.height

            x_axis_flag = False
            y_axis_flag = False
            if mx > x and mx < x + w:  # between
                x_axis_flag = True
            if my > y and my < y + h:
                y_axis_flag = True
            if x_axis_flag and y_axis_flag:
                self.state.pressed = True
                self.event_queue.append(DialogEvent(DialogEventTypes.press, event))

        if event.type == pygame.MOUSEMOTION:
            if self.state.pressed:
                self.event_queue.append(
                    DialogEvent(DialogEventTypes.press_and_move, event)
                )

        if event.type == pygame.MOUSEBUTTONUP:
            if self.state.pressed:
                self.state.pressed = False
                self.event_queue.append(DialogEvent(DialogEventTypes.release, event))

    def emit_events(self):
        while len(self.event_queue) > 0:

            dialog_event = self.event_queue.pop()
            yield dialog_event


class TextBox:
    font_size: int
    font: pygame.font.Font
    color: RGB


class MoveDialog:
    def __init__(self, dialog: Dialog, dialog_event: DialogEvent) -> None:
        self.init = True
        self.offset = get_offset(dialog, dialog_event.event)
    
    def apply_offset(self, event: pygame.event.Event):
        off_x, off_y =self.offset
        mx, my = event.pos
        return mx - off_x, my - off_y
    
    def __reset__(self):
        self.init = False
        self.offset = 0, 0


# def init_dialog(screen: pygame.Surface, config: DialogConfig):
#     w, h = screen.get_width(), screen.get_height()
#     dialog_surface = pygame.Surface(
#         (w - config.right * 2, h - config.bottom * 2), pygame.SRCALPHA
#     )
#     dialog_surface.fill((0, 128, 255, 128))

#     screen.blit(dialog_surface, (config.left, config.top))
#     return dialog_surface

