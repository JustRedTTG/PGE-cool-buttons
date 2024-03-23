import logging
from functools import lru_cache, wraps
from typing import Type, Union

import pygameextra
import pygameextra.button as buttons
import pygameextra.settings as settings
from pygameextra import draw, mouse

from pygameextra_cool_buttons.color import UniqueColor
from pygameextra_cool_buttons.button_expansion import button_expansion_map

original_action = buttons.action
original_rect = buttons.rect
original_image = buttons.image


class WrappedButtonClass(buttons.Button):
    __base_button__ = buttons.Button

    def __init__(self, *args,
                 shadow: bool = False, shadow_color: tuple = (0, 0, 0, 50), shadow_offset: tuple = (2, 2),
                 edge_rounding: int = -1,
                 edge_rounding_topright: int = -1, edge_rounding_topleft: int = -1,
                 edge_rounding_bottomright: int = -1, edge_rounding_bottomleft: int = -1, **kwargs):
        self.infos = {}
        super().__init__(*args, **kwargs)
        self.edge_rounding = edge_rounding
        self.edge_rounding_topright = edge_rounding_topright
        self.edge_rounding_topleft = edge_rounding_topleft
        self.edge_rounding_bottomright = edge_rounding_bottomright
        self.edge_rounding_bottomleft = edge_rounding_bottomleft
        self.shadow = shadow
        self.shadow_color = shadow_color
        self.shadow_offset = shadow_offset

    def _color_translation(self, name: str, color: Union[bool, tuple, UniqueColor]):
        if not isinstance(color, UniqueColor):
            return color
        info = self.infos.get(name)
        if info is None:
            self.infos[name] = (info := color.Info())
        return color.get_color(info)

    @property
    def dynamic_area(self):
        return self.get_shadow_area(self.area, self.shadow_offset) \
            if self.shadow and mouse.clicked()[0] and self.hovered else None

    @staticmethod
    def _edge_rounding_translation(name: str, edge_rounding: int):
        if edge_rounding == -1:
            return getattr(settings, f'cb_default_{name}')
        return edge_rounding

    @classmethod
    @lru_cache
    def get_shadow_area(cls, area: tuple, shadow_offset: tuple) -> tuple:
        rect = pygameextra.Rect(*area)
        rect.move_ip(*shadow_offset)
        return rect

    @classmethod
    def static_render(cls, area: tuple, inactive_resource=None, active_resource=None, hovered: bool = False,
                      disabled: Union[bool, tuple] = None, shadow: bool = False,
                      shadow_color: tuple = (0, 0, 0, 50), shadow_offset: tuple = (2, 2),
                      edge_rounding: int = -1,
                      edge_rounding_topright: int = -1, edge_rounding_topleft: int = -1,
                      edge_rounding_bottomright: int = -1, edge_rounding_bottomleft: int = -1,
                      dynamic_area: tuple = None
                      ):
        edge_rounding = cls._edge_rounding_translation('edge_rounding', edge_rounding)
        edge_rounding_topright = cls._edge_rounding_translation('edge_rounding_topright', edge_rounding_topright)
        edge_rounding_topleft = cls._edge_rounding_translation('edge_rounding_topleft', edge_rounding_topleft)
        edge_rounding_bottomright = cls._edge_rounding_translation('edge_rounding_bottomright', edge_rounding_bottomright)
        edge_rounding_bottomleft = cls._edge_rounding_translation('edge_rounding_bottomleft', edge_rounding_bottomleft)


        if shadow:
            draw.rect(
                shadow_color, cls.get_shadow_area(area, shadow_offset), 0,
                edge_rounding=edge_rounding,
                edge_rounding_topright=edge_rounding_topright,
                edge_rounding_topleft=edge_rounding_topleft,
                edge_rounding_bottomright=edge_rounding_bottomright,
                edge_rounding_bottomleft=edge_rounding_bottomleft
            )

        if cls.__base_button__ in button_expansion_map:
            button_expansion_map[cls.__base_button__].static_render(
                dynamic_area or area, inactive_resource, active_resource,
                hovered, disabled, shadow, shadow_color, shadow_offset, edge_rounding,
                edge_rounding_topright, edge_rounding_topleft,
                edge_rounding_bottomright, edge_rounding_bottomleft
            )
        else:
            super().static_render(dynamic_area or area, inactive_resource, active_resource, hovered, disabled)

    def render(self, area: tuple = None, inactive_resource=None, active_resource=None,
               text: pygameextra.Text = None, disabled: Union[bool, tuple, UniqueColor] = False, shadow: bool = False,
               shadow_color: tuple = (0, 0, 0, 50), shadow_offset: tuple = (2, 2),
               edge_rounding: int = -1,
               edge_rounding_topright: int = -1, edge_rounding_topleft: int = -1,
               edge_rounding_bottomright: int = -1, edge_rounding_bottomleft: int = -1
               ):
        inactive_resource = self._color_translation('inactive_resource', inactive_resource)
        self_inactive_resource = self._color_translation('self_inactive_resource', self.inactive_resource)
        active_resource = self._color_translation('active_resource', active_resource)
        self_active_resource = self._color_translation('self_active_resource', self.active_resource)
        disabled = self._color_translation('disabled', disabled)
        self_disabled = self._color_translation('self_disabled', self.disabled)
        if shadow:
            shadow_color = self._color_translation('shadow_color', shadow_color)
            self_shadow_color = self._color_translation('self_shadow_color', self.shadow_color)

        self.static_render(area or self.area, inactive_resource or self_inactive_resource,
                           active_resource or self_active_resource, self.hovered, disabled or self_disabled,
                           shadow or self.shadow, shadow_color or self_shadow_color,
                           shadow_offset or self.shadow_offset,
                           edge_rounding or self.edge_rounding, edge_rounding_topright or self.edge_rounding_topright,
                           edge_rounding_topleft or self.edge_rounding_topleft,
                           edge_rounding_bottomright or self.edge_rounding_bottomright,
                           edge_rounding_bottomleft or self.edge_rounding_bottomleft,
                           self.dynamic_area)
        self.static_render_text(area or self.dynamic_area or self.area, text or self.text)


def button_class_wrapper(button_class: Type[buttons.Button]):
    class Wrapped(WrappedButtonClass, button_class):
        __base_button__ = button_class

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

    return Wrapped


def button_function_wrapper(func):
    @wraps(func)
    def wrapped(*args, shadow: bool = False, shadow_color: tuple = (0, 0, 0, 50), shadow_offset: tuple = (2, 2),
                edge_rounding: int = -1,
                edge_rounding_topright: int = -1, edge_rounding_topleft: int = -1,
                edge_rounding_bottomright: int = -1, edge_rounding_bottomleft: int = -1, **kwargs):
        func(*args, **kwargs)
        if not settings.game_context and not hasattr(settings, 'cb_warn_function_wrapper'):
            logging.warning("Using the pygameextra button functions without a game context will not work properly")
            setattr(settings, 'cb_warn_function_wrapper', True)
            return
        button = settings.game_context.buttons[-1]
        button.shadow = shadow
        button.shadow_color = shadow_color
        button.shadow_offset = shadow_offset
        button.edge_rounding = edge_rounding
        button.edge_rounding_topright = edge_rounding_topright
        button.edge_rounding_topleft = edge_rounding_topleft
        button.edge_rounding_bottomright = edge_rounding_bottomright
        button.edge_rounding_bottomleft = edge_rounding_bottomleft
        setattr(button, 'cool_button', True)

    return wrapped


def expanded_button_check(button: WrappedButtonClass):
    if not hasattr(button, 'cool_button'):
        return
    elif not settings.game_context and not hasattr(settings, 'cb_warn_button_check_wrapper'):
        logging.warning("Using the pygameextra button functions without a game context will not work properly")
        setattr(settings, 'cb_warn_button_check_wrapper', True)
        return
    elif not settings.game_context:
        return
    elif not isinstance(button, WrappedButtonClass):
        return

    if len(settings.game_context.previous_buttons) >= (buttons_length := len(settings.game_context.buttons)):
        button.hovered = settings.game_context.previous_buttons[buttons_length - 1].hovered
        button.infos = settings.game_context.previous_buttons[buttons_length - 1].infos
        button.render()
        button.hovered = False
    else:
        button.hovered = False
        button.render()


# Wrap pygameextra buttons with extended functionality

if not hasattr(settings, 'cool_buttons'):
    buttons.check_hover = expanded_button_check

    buttons.Button = button_class_wrapper(buttons.Button)
    buttons.RectButton = button_class_wrapper(buttons.RectButton)
    buttons.ImageButton = button_class_wrapper(buttons.ImageButton)

    buttons.action = button_function_wrapper(original_action)
    buttons.rect = button_function_wrapper(original_rect)
    buttons.image = button_function_wrapper(original_image)

    setattr(settings, 'cool_buttons', True)
    setattr(settings, 'cb_default_edge_rounding', -1)
    setattr(settings, 'cb_default_edge_rounding_topright', -1)
    setattr(settings, 'cb_default_edge_rounding_topleft', -1)
    setattr(settings, 'cb_default_edge_rounding_bottomright', -1)
    setattr(settings, 'cb_default_edge_rounding_bottomleft', -1)
