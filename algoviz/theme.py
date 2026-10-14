"""Color themes. 'arcade' is the default; 'classic' reproduces the original look exactly.

Select with `--theme classic` or the ALGOVIZ_THEME environment variable.
"""
import os

CLASSIC = dict(
    BG=(13,20,32), PANEL=(22,33,49), TEXT=(230,238,246), MUTED=(157,177,196),
    ACCENT=(77,201,225), FRONT=(94,135,246), VISIT=(52,76,104), SETTLED=(56,130,119),
    CURRENT=(255,180,75), ROUTE=(255,222,111), WALL=(7,12,21), SWAMP=(145,98,162),
    BUTTON=(36,51,70), BUTTON_ON=(40,77,94), BUTTON_EDGE=(63,83,104), MODAL=(30,48,65),
    DIVIDER=(62,88,112), STATUS=(20,29,43), TOOLTIP=(47,68,86), CELL=(37,49,66),
    CELL_SEEN=(62,76,99), GRIDLINE=(42,58,76), ERROR=(255,153,137), HEADING=(255,222,111),
    ARCADE=False,
)

ARCADE = dict(
    BG=(12,10,32), PANEL=(26,23,62), TEXT=(242,240,255), MUTED=(168,164,214),
    ACCENT=(0,229,255), FRONT=(86,132,255), VISIT=(56,54,120), SETTLED=(0,184,148),
    CURRENT=(255,168,38), ROUTE=(255,226,72), WALL=(5,4,16), SWAMP=(178,88,214),
    BUTTON=(44,38,104), BUTTON_ON=(232,48,152), BUTTON_EDGE=(96,86,190), MODAL=(30,26,74),
    DIVIDER=(84,76,168), STATUS=(18,15,46), TOOLTIP=(70,58,150), CELL=(38,35,84),
    CELL_SEEN=(66,62,136), GRIDLINE=(52,48,110), ERROR=(255,112,140), HEADING=(255,226,72),
    ARCADE=True,
)

THEMES = {'classic': CLASSIC, 'arcade': ARCADE}


def palette(name=None):
    name = name or os.environ.get('ALGOVIZ_THEME', 'arcade')
    if name not in THEMES:
        raise ValueError(f'Unknown theme {name!r}; choose one of {sorted(THEMES)}')
    return THEMES[name]


def apply(name, *namespaces):
    """Rebind color constants in module namespaces (renderers read them at draw time)."""
    colors = palette(name)
    for namespace in namespaces:
        namespace.update(colors)
    return colors
