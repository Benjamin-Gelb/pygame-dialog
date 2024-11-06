import abc
from enum import Enum
import math
from re import L, S
from typing import Callable, Dict, List, Optional, Tuple, Union, Sequence
from pygame.math import Vector2
import pygame

from pydialog.pydialog import RGBA

Coordinate = Union[Tuple[float, float], Sequence[float], Vector2]
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

w, h = 400, 400
screen = pygame.display.set_mode((w, h))
clock = pygame.time.Clock()
framerate = 24

# event_map_handler : Dict[pygame.event.EventType, List[Callable[[pygame.event.Event]]]] = {}

# def add_event_handler(event_type: pygame.event.EventType, handler: Callable[[pygame.event.Event]]):
#     handler_list = event_map_handler.get(event_type, [])
#     handler_list.append()


# class EventHandler:
#     event_map : Dict[pygame.event.EventType, List[Callable[[pygame.event.Event]]]]

#     def __init__(self) -> None:
#         pass

#     def add_handler(self, ):


def frame_in_out(t):
    return t


# Define easing functions
def ease_in_out_cubic(t):
    return 3 * t**2 - 2 * t**3


def ease_in_out_sine(t):
    return 0.5 * (1 - math.cos(math.pi * t))


def interpolate_ease_in_out(start, end, t):
    # Apply ease-in-out function to t
    ease_t = ease_in_out_cubic(t)
    # Interpolate between start and end based on eased t
    return start + (end - start) * ease_t


def interpolate(start: int, end: int, t: float):
    return start + (end - start) * t


class DialogConfig:
    x: int
    y: int
    width: int
    height: int
    color: RGBA


class CenterConfig(DialogConfig):
    def __init__(
        self, screen: pygame.Surface, height: int, spacing: int, color: RGBA
    ) -> None:
        w, h = screen.get_size()
        self.height = height
        self.width = w - spacing * 2
        self.y = int((h / 2) - height)
        self.x = spacing
        self.color = color


class DialogEvent(Enum):
    open = 1
    close = 2
    selected = 3
    deselected = 4
    pressed = 5
    unpressed = 6


class Dialog:
    def __init__(self, config: DialogConfig) -> None:
        self.config = config
        # self.x, self.y = config.x, config.y
        # self.height, self.width = config.height, config.width
        # self.color = config.color
        self.active = False
        self.selected = False
        self.pressed = False

        self.pub_ref_map: Dict[DialogEvent, List[int]] = {}
        self.ref_sub_map: Dict[int, Callable[[pygame.event.Event]]] = {}
        self.deleted_ref_queue = []
        self.callback_increment = 0

    def on(
        self, event: DialogEvent, callback: Callable[[Optional[pygame.event.Event]]]
    ):
        callback_id = self.callback_increment
        ref_list = self.pub_ref_map.get(event, [])
        ref_list.append(callback_id)
        self.pub_ref_map[event] = ref_list
        self.ref_sub_map[callback_id] = callback
        self.callback_increment += 1
        return callback_id

    def off(self, callback_id: int):
        self.deleted_ref_queue.append(callback_id)
        del self.ref_sub_map[callback_id]

    def toggle(self):
        self.active = not self.active
        if self.active:
            self.emit(DialogEvent.open)
        else:
            self.emit(DialogEvent.close)

    def listen(self, event: pygame.event.Event):
        if not self.active:
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            x_axis_flag, y_axis_flag = False, False
            mx, my = event.pos
            if mx > self.config.x and mx < self.config.x + self.config.width:
                x_axis_flag = True

            if my > self.config.y and my < self.config.y + self.config.height:
                y_axis_flag = True

            if x_axis_flag and y_axis_flag:
                self.selected = True
                self.pressed = True
                self.emit(DialogEvent.selected, event)
                self.emit(DialogEvent.pressed, event)
            else:
                self.selected = False
                self.emit(DialogEvent.deselected, event)

        if event.type == pygame.MOUSEBUTTONUP:
            self.pressed = False
            self.emit(DialogEvent.unpressed)


    def emit(
        self,
        dialog_event: DialogEvent,
        event: pygame.event.Event = pygame.event.Event(type=pygame.NOEVENT),
    ):
        for ref in self.pub_ref_map.get(dialog_event, []):
            callback = self.ref_sub_map.get(ref)
            if callback:
                callback(event)


class Visual:
    @classmethod
    def derive_t_coefficient(
        cls, dt_ms: int, timing_function: Callable[[int], float]
    ) -> float:
        return timing_function(dt_ms)

    def __init__(
        self,
        animation_duration_ms: int,
        timing_function: Callable[[float], float],
        draw_function: Callable[
            ["Visual", Dialog, float], Tuple[pygame.Surface, Coordinate]
        ],
    ) -> None:
        self.active = False
        self.elapsed_time_ms = 0
        self.draw_function = draw_function
        self.timing_function = timing_function
        self.animation_duration_ms = animation_duration_ms
        self.infinite = False

    def start(self):
        print("start")
        self.active = True

    def stop(self):
        print("stop")
        self.active = False

    def reset(self):
        print("reset")
        self.elapsed_time_ms = 0

    def animate(self, dialog: Dialog, dt_ms: int) -> Tuple[pygame.Surface, Coordinate]:
        t = self.timing_function(
            min(self.elapsed_time_ms / self.animation_duration_ms, 1)
        )

        if self.elapsed_time_ms < self.animation_duration_ms:
            self.elapsed_time_ms += dt_ms
            return self.draw_function(self, dialog, t)

        if self.infinite:
            self.reset()
        else:
            self.stop()

        return self.draw_function(self, dialog, t)

    def static(self):
        return self.draw_function(self, dialog, 1)


def slide_to_the_right(
    animation: Visual, dialog: Dialog, t_coefficient: float
) -> Tuple[pygame.Surface, Coordinate]:
    surface = pygame.Surface(
        (interpolate(dialog.config.x, dialog.config.width, t_coefficient), dialog.config.height),
        pygame.SRCALPHA,
    )
    surface.fill((*BLACK, 128))
    return surface, (dialog.x, dialog.y)


dialog = Dialog(CenterConfig(screen, 40, 20, (*BLACK, 128)))
animation = Visual(250, frame_in_out, slide_to_the_right)


running = True
dt = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            match event.key:
                case pygame.K_h:
                    dialog.toggle()
                    animation.start()

    if dialog.active:
        if animation.active:
            screen.blit(*animation.animate(dialog, dt))
        else:
            animation.reset()
            screen.blit(*animation.static())

    dt = clock.tick(framerate)
    pygame.display.flip()
    screen.fill(WHITE)


pygame.quit()
