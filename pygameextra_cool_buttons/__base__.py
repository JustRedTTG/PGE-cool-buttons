import pygameextra

from functools import lru_cache


class WrappedButtonClassBase:
    @classmethod
    @lru_cache
    def get_shadow_area(cls, area: tuple, shadow_offset: tuple) -> tuple:
        rect = pygameextra.Rect(*area)
        rect.move_ip(*shadow_offset)
        return rect
