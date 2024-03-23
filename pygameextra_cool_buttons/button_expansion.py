from functools import lru_cache
from typing import Union

from pygameextra import draw
from pygameextra.button import RectButton
from pygameextra_cool_buttons.__base__ import WrappedButtonClassBase


class RectButtonExpansion(RectButton, WrappedButtonClassBase):
    __additional_attributes__ = {
        'inactive_resource_width': 0,
        'active_resource_width': 0,
    }

    @classmethod
    @lru_cache
    def get_w(cls, hovered: bool, disabled: bool, inactive_resource_width: int, active_resource_width: int):
        return active_resource_width if (hovered and not disabled) else inactive_resource_width

    @classmethod
    def static_render_shadow(cls, area: tuple, hovered: bool = False, disabled: Union[bool, tuple] = None,
                             shadow_color: tuple = None, shadow_offset: tuple = None,
                             edge_rounding: int = -1, edge_rounding_topright: int = -1,
                             edge_rounding_topleft: int = -1, edge_rounding_bottomright: int = -1,
                             edge_rounding_bottomleft: int = -1, **kwargs):
        draw.rect(
            shadow_color, cls.get_shadow_area(area, shadow_offset), cls.get_w(hovered, disabled, **kwargs),
            edge_rounding=edge_rounding,
            edge_rounding_topright=edge_rounding_topright,
            edge_rounding_topleft=edge_rounding_topleft,
            edge_rounding_bottomright=edge_rounding_bottomright,
            edge_rounding_bottomleft=edge_rounding_bottomleft
        )

    @classmethod
    def static_render(cls, area: tuple, inactive_resource=None, active_resource=None, hovered: bool = False,
                      disabled: Union[bool, tuple] = None, shadow: bool = False,
                      shadow_color: tuple = (0, 0, 0, 50), shadow_offset: tuple = (2, 2),
                      edge_rounding: int = -1,
                      edge_rounding_topright: int = -1, edge_rounding_topleft: int = -1,
                      edge_rounding_bottomright: int = -1, edge_rounding_bottomleft: int = -1,
                      **kwargs
                      ):
        color = active_resource if (hovered and not disabled) else (
            disabled if type(disabled) == tuple else inactive_resource)
        draw.rect(
            color, area, cls.get_w(hovered, disabled, **kwargs),
            edge_rounding=edge_rounding,
            edge_rounding_topright=edge_rounding_topright,
            edge_rounding_topleft=edge_rounding_topleft,
            edge_rounding_bottomright=edge_rounding_bottomright,
            edge_rounding_bottomleft=edge_rounding_bottomleft,
        )


button_expansion_map = {
    RectButton: RectButtonExpansion
}
