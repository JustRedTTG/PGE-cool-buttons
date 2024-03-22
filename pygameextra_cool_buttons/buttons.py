from typing import Type, Union

import pygameextra
import pygameextra.button as buttons
import pygameextra.settings as settings
from pygameextra_cool_buttons.color import UniqueColor

original_action = buttons.action
original_rect = buttons.rect
original_image = buttons.image


class WrappedButtonClass(buttons.Button):
    def __init__(self, *args, **kwargs):
        self.infos = {}
        super().__init__(*args, **kwargs)

    def _color_translation(self, name: str, color: Union[bool, tuple, UniqueColor]):
        if not isinstance(color, UniqueColor):
            return color
        info = self.infos.get(name)
        if info is None:
            self.infos[name] = (info := color.Info())
        return color.get_color(info)

    def render(self, area: tuple = None, inactive_resource=None, active_resource=None,
               text: pygameextra.Text = None, disabled: Union[bool, tuple, UniqueColor] = False):
        inactive_resource = self._color_translation('inactive_resource', inactive_resource)
        self_inactive_resource = self._color_translation('self_inactive_resource', self.inactive_resource)
        active_resource = self._color_translation('active_resource', active_resource)
        self_active_resource = self._color_translation('self_active_resource', self.active_resource)
        disabled = self._color_translation('disabled', disabled)
        self_disabled = self._color_translation('self_disabled', self.disabled)

        self.static_render(area or self.area, inactive_resource or self_inactive_resource,
                           active_resource or self_active_resource, self.hovered, disabled or self_disabled)
        self.static_render_text(area or self.area, text or self.text)

def button_class_wrapper(button_class: Type[buttons.Button]):
    class Wrapped(WrappedButtonClass, button_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

    return Wrapped


def expanded_button_check(button: WrappedButtonClass):
    if not settings.game_context:
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
    buttons.Button = button_class_wrapper(buttons.Button)
    buttons.RectButton = button_class_wrapper(buttons.RectButton)
    buttons.ImageButton = button_class_wrapper(buttons.ImageButton)

    setattr(settings, 'cool_buttons', True)
