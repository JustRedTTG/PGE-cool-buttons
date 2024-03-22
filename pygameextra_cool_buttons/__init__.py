import pygameextra
import pygameextra_cool_buttons.buttons as cool_buttons
from pygameextra_cool_buttons.color import *


for attribute in dir(cool_buttons):
    if 'button' in attribute.lower():
        setattr(pygameextra, attribute, getattr(cool_buttons, attribute))