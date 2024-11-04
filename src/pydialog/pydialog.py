import abc
from cmath import rect
from enum import Enum
from typing import Any, Dict, Generator, Iterable, Iterator, List, Optional, Tuple
import pygame

# Colors
pygame.font.init()
# font = pygame.font.Font(None, 36)

# Render the text (True enables anti-aliasing, color is white, background color is optional)
# text_surface = font.render("Hello, Pygame!", True, (0, 0, 0))


RGBA = Tuple[int, int, int, int]
RGB = Tuple[int, int, int]
Coordinate = Tuple[int, int]


class DialogConfig:

    x: int
    y: int
    width: int
    height: int

    color: RGBA
    opacity: int


class SnapToBottom(DialogConfig):
    def __init__(
        self, screen: pygame.Surface, height: int, padding_y: int, padding_x: int
    ) -> None:
        super().__init__()
        w, h = screen.get_size()
        self.x = padding_x
        self.height = height
        self.width = w - padding_x
        self.y = h - height - padding_y
        self.color = (0, 0, 0, 128)


def chat_dialog(screen: pygame.Surface):
    d = DialogConfig()
    screen_w, screen_h = (screen.get_width(), screen.get_height())
    d.width, d.height = int(screen_w - screen_w * 0.2), int(screen_h * 0.2)
    d.x, d.y = int(screen_w * 0.1), int(screen_h * 0.75)
    d.color = (0, 0, 0, 128)
    return d


class Renderable(abc.ABC):
    @abc.abstractmethod
    def get_surface(
        self, dialog_position: Tuple[int, int], dialog_surface: pygame.Surface
    ) -> Optional[Tuple[pygame.Surface, pygame.Rect]]:
        pass


class DialogWriter(Renderable):
    font: pygame.font.Font
    # text_surface: pygame.Surface
    text_overflow: int
    _text: str

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text_value: str):
        if len(text_value) > self.text_overflow:
            raise ValueError("Text overflow error")
        self._text = text_value


class DefaultWriter(DialogWriter):
    def __init__(self, font: pygame.font.Font = pygame.font.Font(None, 36)) -> None:
        super().__init__()
        self.text_overflow = 255
        self.text = ""
        self.font = font

    def get_surface(
        self, dialog_position: Tuple[int, int], dialog_surface: pygame.Surface
    ) -> Tuple[pygame.Surface, pygame.Rect]:
        x, y = dialog_position
        w, h = dialog_surface.get_size()
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_coords = text_surface.get_rect(center=(x + (w / 2), y + (h / 2)))
        return text_surface, text_coords


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
    open: bool = False
    pressed: bool = False


class ConfigError(AssertionError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Dialog(Renderable):
    surface: pygame.Surface
    config: DialogConfig
    writer: DialogWriter

    renderables: List[Renderable]
    state: DialogState = DialogState()
    event_queue: List[DialogEvent] = []

    @classmethod
    def validate_config(cls, config: DialogConfig):
        try:
            assert config.x, "Position value (x) missing"
            assert config.y, "Position value (y) missing"
            for color_value in config.color:
                assert color_value >= 0, "8-bit color underflow"
                assert color_value <= 255, "8-bit color overflow"

            assert config.width, "Volume value missing"
            assert config.height, "Volume value missing"
        except AssertionError as assert_exc:
            raise ConfigError(*assert_exc.args)

    def __init__(
        self, config: DialogConfig, writer: DialogWriter = DefaultWriter()
    ) -> None:
        self.validate_config(config)
        self.config = config
        self.writer = writer
        self.renderables = [writer]
        self.surface = pygame.surface.Surface(
            (self.config.width, self.config.height), pygame.SRCALPHA
        )
        pass

    def open(self):
        self.state.open = True

    def close(self):
        self.state.open = False

    def is_open(self):
        return self.state.open

    def write(self, text: str):
        self.writer.text = text

    def clear(self):
        self.writer.text = ""

    def get_surface(self):
        if self.state.open:
            self.surface.fill(self.config.color)
            return (
                self.surface,
                self.surface.get_rect(topleft=(self.config.x, self.config.y)),
            )

    def queue_surfaces(self) -> List[Tuple[pygame.Surface, pygame.Rect]]:
        surface_queue = []
        dialog_surface = self.get_surface()
        if dialog_surface:
            surface_queue.append(dialog_surface)
            for renderable in self.renderables:
                surface_rect = renderable.get_surface(
                    (self.config.x, self.config.y), self.surface
                )
                if surface_rect:
                    surface_queue.append(surface_rect)
        return surface_queue

    def render(self, screen: pygame.Surface):
        for surface, rect in self.queue_surfaces():
            screen.blit(surface, rect)

    def listen(self, events: Iterable[pygame.event.Event]):
        pass

    def emit(self) -> Iterator[DialogEvent]:
        while len(self.event_queue) > 0:
            yield self.event_queue.pop()


# class Dialog:
#     surface: pygame.Surface
#     width: int
#     height: int
#     coords: Tuple[int, int]
#     color: pygame.Color

#     event_queue: List[DialogEvent] = []
#     state: DialogState

#     def __init__(self, config: DialogConfig) -> None:
#         self.coords = config.x, config.y
#         self.width = config.width
#         self.height = config.height
#         self.color = (*config.color, config.opacity)
#         self.surface = pygame.surface.Surface(
#             (self.width, self.height), pygame.SRCALPHA
#         )
#         self.sub_surfaces = []
#         self.state = DialogState()

#     def render(self, screen: pygame.Surface):
#         self.surface.fill(self.color)
#         screen.blit(self.surface, self.coords)

#     def event_checker(self, event: pygame.event.Event):
#         if event.type == pygame.MOUSEBUTTONDOWN:
#             mouse_pos = event.pos
#             mx, my = mouse_pos
#             x, y = self.coords
#             w, h = self.width, self.height

#             x_axis_flag = False
#             y_axis_flag = False
#             if mx > x and mx < x + w:  # between
#                 x_axis_flag = True
#             if my > y and my < y + h:
#                 y_axis_flag = True
#             if x_axis_flag and y_axis_flag:
#                 self.state.pressed = True
#                 self.event_queue.append(DialogEvent(DialogEventTypes.press, event))

#         if event.type == pygame.MOUSEMOTION:
#             if self.state.pressed:
#                 self.event_queue.append(
#                     DialogEvent(DialogEventTypes.press_and_move, event)
#                 )

#         if event.type == pygame.MOUSEBUTTONUP:
#             if self.state.pressed:
#                 self.state.pressed = False
#                 self.event_queue.append(DialogEvent(DialogEventTypes.release, event))

#     def emit_events(self):
#         while len(self.event_queue) > 0:
#             dialog_event = self.event_queue.pop()
#             yield dialog_event


# class TextBox:
#     font_size: int
#     font: pygame.font.Font
#     color: RGB


# class MoveDialog:
#     def __init__(self, dialog: Dialog, dialog_event: DialogEvent) -> None:
#         self.init = True
#         self.offset = get_offset(dialog, dialog_event.event)

#     def apply_offset(self, event: pygame.event.Event):
#         off_x, off_y =self.offset
#         mx, my = event.pos
#         return mx - off_x, my - off_y

#     def __reset__(self):
#         self.init = False
#         self.offset = 0, 0


# def init_dialog(screen: pygame.Surface, config: DialogConfig):
#     w, h = screen.get_width(), screen.get_height()
#     dialog_surface = pygame.Surface(
#         (w - config.right * 2, h - config.bottom * 2), pygame.SRCALPHA
#     )
#     dialog_surface.fill((0, 128, 255, 128))

#     screen.blit(dialog_surface, (config.left, config.top))
#     return dialog_surface


# Dialog(
#     Draggable,
#     Text,
# )
