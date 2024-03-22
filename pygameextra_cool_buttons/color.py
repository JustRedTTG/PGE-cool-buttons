from abc import ABC, abstractmethod
from typing import List, Tuple

from pygameextra import settings


class UniqueColor(ABC):
    class Info(ABC):
        pass

    @abstractmethod
    def get_color(self, info: Info) -> tuple:
        raise NotImplementedError("Method get_next_color not implemented")


class ColorWithPercentageMixin:
    class Info:
        def __init__(self):
            self.percentage = 0


class ColorWithPercentage(UniqueColor, ColorWithPercentageMixin, ABC):
    pass


class Color(UniqueColor):

    def __init__(self, color: tuple):
        self.color = color

    def get_color(self, info) -> tuple:
        return self.color


class PartialGradientColor:
    def __init__(self, color: UniqueColor, percentage: float):
        self.color = color
        self.percentage = percentage


class GradientColor(ColorWithPercentage):
    class Info(ColorWithPercentageMixin.Info):
        def __init__(self):
            super().__init__()
            self.sub_infos = None


    def __init__(self, *colors: PartialGradientColor):
        self.colors: Tuple[PartialGradientColor, ...] = tuple(sorted(colors, key=lambda x: x.percentage))

    @staticmethod
    def _interpolate(color1: tuple, color2: tuple, percentage: float) -> tuple:
        return tuple(int(color1[i] * (1 - percentage) + color2[i] * percentage) for i in range(3))

    def get_color_at(self, percentage: float, info: Info) -> tuple:
        if percentage < 0 or percentage > 1:
            raise ValueError("Percentage should be between 0 and 1")
        for i in range(len(self.colors) - 1):
            if self.colors[i].percentage <= percentage <= self.colors[i + 1].percentage:
                return self._interpolate(self.colors[i].color.get_color(info.sub_infos[i]), self.colors[i + 1].color.get_color(info.sub_infos[i + 1]),
                                         (percentage - self.colors[i].percentage) / (
                                                 self.colors[i + 1].percentage - self.colors[i].percentage))

    def get_color(self, info: Info) -> tuple:
        if info.sub_infos is None:
            info.sub_infos = [color.color.Info() for color in self.colors]
        return self.get_color_at(info.percentage, info)


class PulsingColor(ColorWithPercentageMixin, UniqueColor):
    class Info(ColorWithPercentageMixin.Info):
        def __init__(self):
            super().__init__()
            self.pulse_state = 0
            self.time = 0

    def __init__(self, color: ColorWithPercentage, pulse_in: float, pulse_hold: float, pulse_out: float):
        self.color = color

        class CombinedInfo(color.Info, self.Info):
            pass
        self.Info = CombinedInfo
        self.pulse_in = pulse_in
        self.pulse_hold = pulse_hold
        self.pulse_out = pulse_out

    def get_color(self, info: Info) -> tuple:
        try:
            info.time += settings.game_context.delta_time
        except AttributeError:
            raise AttributeError("PulsingColor can only be used in a game context")

        if info.pulse_state == 0:
            if info.time >= self.pulse_in:
                info.time = 0
                info.percentage = 1
                info.pulse_state = 1
            else:
                info.percentage = info.time / self.pulse_in
        elif info.pulse_state == 1:
            if info.time >= self.pulse_hold:
                info.time = 0
                info.pulse_state = 2
        elif info.pulse_state == 2:
            if info.time >= self.pulse_out:
                info.time = 0
                info.percentage = 0
                info.pulse_state = 0
            else:
                info.percentage = 1 - info.time / self.pulse_out
        return self.color.get_color(info)
