from typing import Union

from pygameextra import draw
from pygameextra.button import RectButton


class RectButtonExpansion(RectButton):
    @staticmethod
    def static_render(area: tuple, inactive_resource=None, active_resource=None, hovered: bool = False,
                      disabled: Union[bool, tuple] = None, shadow: bool = False,
                      shadow_color: tuple = (0, 0, 0, 50), shadow_offset: tuple = (2, 2),
                      edge_rounding: int = -1,
                      edge_rounding_topright: int = -1, edge_rounding_topleft: int = -1,
                      edge_rounding_bottomright: int = -1, edge_rounding_bottomleft: int = -1
                      ):
        color = active_resource if (hovered and not disabled) else (
            disabled if type(disabled) == tuple else inactive_resource)
        draw.rect(
            color, area,
            edge_rounding=edge_rounding,
            edge_rounding_topright=edge_rounding_topright,
            edge_rounding_topleft=edge_rounding_topleft,
            edge_rounding_bottomright=edge_rounding_bottomright,
            edge_rounding_bottomleft=edge_rounding_bottomleft
        )


button_expansion_map = {
    RectButton: RectButtonExpansion
}
