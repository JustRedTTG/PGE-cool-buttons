import glob
import math
import os
import tempfile
import threading
import time
import atexit
import shutil
import pygameextra as pe
import pygameextra_cool_buttons
from pygameextra_cool_buttons.color import *
from functools import wraps, lru_cache
from typing import Type, Generator, Tuple, Union
from PIL import Image

from pygameextra import Text

pe.init()

SCRIPT_DIR = os.path.dirname(__file__)
RECORDING_DIRECTORY = os.path.join(SCRIPT_DIR, 'recording')
os.makedirs(RECORDING_DIRECTORY, exist_ok=True)
RECORDING_IN_PROGRESS = False


class ButtonRecorderMixin(pe.Button):
    RECORDING_TEXT: str = 'Hello, PGE!'
    RECORDING_PADDING: Tuple[int, int] = (100, 100)
    RECORDING_SURFACE_AREA: Tuple[int, int] = (300, 150)
    RECORDING_SURFACE_BACKGROUND: Tuple[int, int, int] = pe.colors.darkgray
    RECORDING_FAKE_OUTLINE: int = 15
    RECORDING_FAKE_INLINE: int = 5
    RECORDING_FRAMES = 40
    RECORDING_TIME_IN = 4
    RECORDING_TIME_HOLD = 4
    RECORDING_CLICK_HOLD = .1
    RECORDING_TIME_OUT = 4
    RECORDING_TIME = RECORDING_TIME_IN + RECORDING_TIME_HOLD + RECORDING_TIME_OUT

    button_name: str
    recording: bool
    recording_state: int
    recording_start: float
    recording_capture_index: int
    recording_temp_dir: str
    _hovered: bool
    _area: Tuple[int, int, int, int]
    _surface: pe.Surface = None
    spoofed_mouse_position: Tuple[int, int] = None
    original_area: Tuple[int, int, int, int]

    # state 0: mouse going in
    # state 1: mouse in
    # state 2: mouse going out

    @property
    def elapsed(self):
        return time.time() - self.recording_start

    @property
    @lru_cache()
    def recording_area(self):
        return (
            *tuple(padding // 2 for padding in self.RECORDING_PADDING),
            *tuple(
                size - padding for size, padding in
                zip(self.RECORDING_SURFACE_AREA, self.RECORDING_PADDING)
            )
        )

    def handle_recording(self):
        global RECORDING_IN_PROGRESS
        if self.elapsed < self.RECORDING_TIME_IN:
            self.recording_state = 0
        elif self.elapsed < self.RECORDING_TIME_IN + self.RECORDING_TIME_HOLD:
            self.recording_state = 1
        elif self.elapsed < self.RECORDING_TIME:
            self.recording_state = 2
        elif self.elapsed >= self.RECORDING_TIME:
            self.recording = False
            self.recording_state = -1
            threading.Thread(target=self.save_gif, daemon=True).start()
            RECORDING_IN_PROGRESS = False

    def save_gif(self):
        frames = [
            Image.open(image)
            for image in sorted(
                glob.glob(
                    f"{self.recording_temp_dir}/*.png"),
                key=lambda x: int(os.path.basename(x).split('.')[0])
            )
        ]
        frame_one = frames[0]
        frame_one.save(os.path.join(RECORDING_DIRECTORY, f"{self.button_name}.gif"), format="GIF",
                       append_images=frames,
                       save_all=True, fps=self.RECORDING_FRAMES / 1.5,
                       loop=0)

    @property
    def area(self):
        return self._area if not self.recording else self.recording_area

    def _render(self, *args, **kwargs):
        super().render(*args, **kwargs)

    def _logic(self, *args, **kwargs):
        super().logic(*args, **kwargs)

    @property
    def surface(self):
        if not self._surface:
            self._surface = pe.Surface(self.RECORDING_SURFACE_AREA)
        pe.fill.full(self.RECORDING_SURFACE_BACKGROUND, self._surface)
        return self._surface

    def get_fake_mouse_position(self):
        t = 0
        if self.recording_state == 0:
            t = min(1, (self.elapsed / self.RECORDING_TIME_IN))
        elif self.recording_state == 1:
            t = 1
        else:
            t = 1 - min(1, (self.elapsed - self.RECORDING_TIME_IN - self.RECORDING_TIME_HOLD) / self.RECORDING_TIME_OUT)
        return pe.math.lerp(
            tuple(size - (padding // 4) for size, padding in
                  zip(self.RECORDING_SURFACE_AREA, self.RECORDING_PADDING)),
            tuple(size // 2 for size in self.RECORDING_SURFACE_AREA),
            t
        )

    def logic(self, *args, **kwargs):
        if not self.recording:
            self._logic(*args, **kwargs)
        else:
            fake_mouse_position = self.get_fake_mouse_position()

            @pe.mouse.offset_wrap(
                tuple(
                    -position + fake_position for position, fake_position in
                    zip(pe.mouse.pos(), fake_mouse_position)))
            def wrapped():
                self._logic(*args, **kwargs)
                self.spoofed_mouse_position = pe.mouse.pos()

            if self.spoof_mouse_click:
                pe.settings.spoof_mouse_clicked = (True, False, False)
            wrapped()
            pe.settings.spoof_mouse_clicked = None

    @property
    def spoof_mouse_click(self):
        return self.recording_state == 1 and self.elapsed < self.RECORDING_TIME_IN + self.RECORDING_CLICK_HOLD

    def render(self, *args, **kwargs):
        pe.draw.rect(pe.colors.black, self.original_area, 2)
        if not self.recording:
            self._render(*args, **kwargs)
        else:
            frame = int(self.RECORDING_FRAMES * (self.elapsed / self.RECORDING_TIME))

            @pe.display.context_wrap(self.surface)
            def wrapped():

                self._render(*args, **kwargs)

                if self.recording_capture_index < frame:
                    if self.spoof_mouse_click == 1:
                        pe.draw.circle(
                            (*pe.colors.black, 50),
                            self.spoofed_mouse_position or self.get_fake_mouse_position(),
                            self.RECORDING_FAKE_OUTLINE, 3
                        )
                    pe.draw.circle(
                        (*pe.colors.black, 50),
                        self.spoofed_mouse_position or self.get_fake_mouse_position(),
                        self.RECORDING_FAKE_INLINE, 0
                    )

                    self.recording_capture_index = frame
                    pe.pygame.image.save(self._surface.surface,
                                         os.path.join('recording',
                                                      os.path.join(self.recording_temp_dir, f'{frame}.png')))

            wrapped()

    @area.setter
    def area(self, value):
        self._area = value

    @property
    def hovered(self):
        return self._hovered

    @hovered.setter
    def hovered(self, value):
        self._hovered = value

    @staticmethod
    @lru_cache
    def _get_text(text, size):
        return pe.Text(text, font_size=size)

    @property
    def text(self):
        return self._get_text(
            self.button_name if not self.recording else self.RECORDING_TEXT,
            self.area[3] // 2
        )

    @text.setter
    def text(self, value):
        pass


def class_recordable_wrapper(cls: Type[pe.Button]):
    class RecordableButton(ButtonRecorderMixin, cls):
        # For anyone copying this, it only works within contexts
        def __init__(self, area, *args, **kwargs):
            super().__init__(area, *args, **kwargs)
            self.button_name = None
            self.recording_temp_dir = None
            self.recording = False
            self.recording_state = -1
            self.recording_start = 0
            self.recording_capture_index = -1
            self.original_area = area

        def logic(self, *args, **kwargs):
            global RECORDING_IN_PROGRESS
            super().logic(*args, **kwargs)
            if self.hovered and not self.recording and pe.settings.game_context.trigger_recording and not RECORDING_IN_PROGRESS:
                pe.settings.game_context.trigger_recording = False
                RECORDING_IN_PROGRESS = True
                self.recording = True
                self._hovered = False
                self.recording_state = 0
                self.recording_capture_index = -1
                self.recording_start = time.time()
            elif self.recording:
                self.handle_recording()

    return RecordableButton


def button_naming_wrapper(func):
    @wraps(func)
    def wrapper(*args, button_name=None, **kwargs):
        func(*args, **kwargs)

        # Retain buttons instead of generating new ones
        for previous_button in pe.settings.game_context.previous_buttons:
            if previous_button.button_name == button_name:
                del pe.settings.game_context.buttons[-1]
                pe.settings.game_context.buttons.append(previous_button)
                break
        if not pe.settings.game_context.buttons[-1].button_name:
            pe.settings.game_context.buttons[-1].button_name = button_name
            pe.settings.game_context.buttons[-1].recording_temp_dir = tempfile.mkdtemp()
            atexit.register(shutil.rmtree, pe.settings.game_context.buttons[-1].recording_temp_dir)
        pe.button.check_hover(pe.settings.game_context.buttons[-1])

    return wrapper


def button_check_hover_wrapper(func):
    @wraps(func)
    def wrapper(button):
        # Don't display buttons that are not named
        if not button.button_name:
            return
        func(button)

    return wrapper


# Wrap pygameextra button components to allow for button recording
if not hasattr(pe.settings, 'wrapped'):
    pe.button.check_hover = button_check_hover_wrapper(pe.button.check_hover)

    pe.button.Button = class_recordable_wrapper(pe.button.Button)
    pe.button.RectButton = class_recordable_wrapper(pe.button.RectButton)
    pe.button.ImageButton = class_recordable_wrapper(pe.button.ImageButton)

    pe.button.action = button_naming_wrapper(pe.button.action)
    pe.button.rect = button_naming_wrapper(pe.button.rect)
    pe.button.image = button_naming_wrapper(pe.button.image)
    setattr(pe.settings, 'wrapped', True)


class Context(pe.GameContext):
    AREA = (800, 500)
    BACKGROUND = pe.colors.gray
    TITLE = 'Cool Buttons Tester'
    BUTTON_SIZE = (120, 30)
    BUTTON_PADDING = 10
    positions: Generator[Tuple[int, int], None, None]
    COLOR_A = pe.colors.purple
    COLOR_B = pe.colors.darkaqua
    COLOR_B_PULSING = PulsingColor(GradientColor(
        PartialGradientColor(Color(pe.colors.verydarkaqua), 0),
        PartialGradientColor(Color(pe.colors.darkcyan), .5),
        PartialGradientColor(Color(pe.colors.aquamarine), 1)
    ), .1, 0, 1)
    COLOR_A_PULSING = PulsingColor(GradientColor(
        PartialGradientColor(Color(pe.colors.red), 0),
        PartialGradientColor(Color(pe.colors.orange), .5),
        PartialGradientColor(Color(pe.colors.red), 1)
    ), 2, .5, 2)
    IMAGE_A: pe.Image
    IMAGE_B: pe.Image
    FPS_LOGGER = True

    def __init__(self):
        super().__init__()
        self.trigger_recording = False
        self.IMAGE_A = pe.Image(os.path.join(SCRIPT_DIR, 'IMAGE_A.png'), self.BUTTON_SIZE)
        self.IMAGE_B = pe.Image(os.path.join(SCRIPT_DIR, 'IMAGE_B.png'), self.BUTTON_SIZE)

    def handle_event(self, _):
        super().handle_event(_)
        if pe.event.key_DOWN(pe.K_r):
            self.trigger_recording = True

    @classmethod
    def position_generator(cls):
        x_and_padding = cls.BUTTON_SIZE[0] + cls.BUTTON_PADDING
        y_and_padding = cls.BUTTON_SIZE[1] + cls.BUTTON_PADDING
        for x in range(cls.BUTTON_PADDING, cls.AREA[0] - x_and_padding, cls.BUTTON_SIZE[0] + cls.BUTTON_PADDING):
            for y in range(cls.BUTTON_PADDING, cls.AREA[1] - y_and_padding, cls.BUTTON_SIZE[1] + cls.BUTTON_PADDING):
                yield x, y

    @property
    def button_area(self):
        return *next(self.positions), *self.BUTTON_SIZE

    def loop(self):
        pe.button.action(self.button_area, button_name='pe.button.action')
        pe.button.rect(self.button_area, self.COLOR_A, self.COLOR_B, button_name='pe.button.rect')
        pe.button.image(self.button_area, self.IMAGE_A, self.IMAGE_B, button_name='pe.button.image')
        pe.button.rect(self.button_area, self.COLOR_A_PULSING, self.COLOR_B_PULSING, button_name='pulsing gradient')

    def pre_loop(self):
        super().pre_loop()
        self.positions = self.position_generator()


def run():
    context = Context()
    while True:
        context()


if __name__ == '__main__':
    run()
