"""
Design tokens for the UI modernization.

All values come from design_handoff_heavy_bag_ui/README.md, which specifies
measurements in 1920x1080 space. Layout code writes the 1080p spec value and
wraps it in s() so the numbers stay diffable against the handoff.
"""

from src.utils.constants import SCREEN_HEIGHT

# Spec space is 1920x1080; the game window is 1280x720 (2/3 scale).
SCALE = SCREEN_HEIGHT / 1080


def s(px: float) -> int:
    """Scale a 1080p spec measurement to window pixels."""
    return max(1, int(round(px * SCALE))) if px > 0 else int(round(px * SCALE))


# --- Color tokens (README "Design Tokens" table) ---
BG = (11, 12, 16)  # #0B0C10
SCENE_BG_TOP = (13, 14, 19)  # #0D0E13
SCENE_BG_BOTTOM = (35, 36, 43)  # #23242B
FLOOR = (23, 24, 29)  # #17181D
PANEL = (13, 14, 17)  # #0D0E11 base for HUD panels
PANEL_ALPHA = 200  # ~ rgba(13,14,17,0.8); no blur in stock pygame
PANEL_BORDER = (255, 255, 255, 20)  # rgba(255,255,255,0.08)
CARD_FILL = (255, 255, 255, 8)  # rgba(255,255,255,0.03)
CARD_BORDER = (255, 255, 255, 26)  # rgba(255,255,255,0.10)
TEXT_PRIMARY = (242, 243, 245)  # #F2F3F5
TEXT_DIM = (235, 237, 240)  # use with DIM alphas below
TEXT_DIM_ALPHA = 140  # ~0.55 of the 0.45-0.6 range
GOLD = (240, 195, 48)  # #F0C330 accent
STAMINA_GREEN = (69, 212, 131)  # #45D483
POWER_BLUE = (61, 123, 255)  # #3D7BFF
RAGE_RED = (229, 67, 46)  # #E5432E
IMPACT_YELLOW = (245, 217, 10)  # #F5D90A

# --- Character palette ("Cel Classic") ---
CEL_OUTLINE = (36, 28, 18)  # #241C12
CEL_SKIN = (245, 200, 154)  # #F5C89A
CEL_HAIR = (107, 68, 35)  # #6B4423
CEL_TANK = (237, 234, 227)  # #EDEAE3
CEL_TANK_TRIM = (210, 59, 46)  # #D23B2E
CEL_SHORTS = (58, 68, 184)  # #3A44B8
CEL_WAISTBAND = GOLD
CEL_GLOVE = (210, 59, 46)  # #D23B2E
CEL_GLOVE_BAND = (163, 43, 34)  # #A32B22
CEL_SHOE = (27, 27, 31)  # #1B1B1F
CEL_SOLE = (230, 228, 220)

# --- Bag leather gradient ---
BAG_LEATHER_TOP = (90, 44, 22)  # #5A2C16
BAG_LEATHER_BOTTOM = (51, 21, 10)  # #33150A

# --- Spacing (1080p spec values; pass through s()) ---
MARGIN_HUD = 80
MARGIN_CONTENT = 160

# Keycap spec: 38-44px square, 1px border white@0.25, fill white@0.05
KEYCAP_SIZE = 42
KEYCAP_BORDER = (255, 255, 255, 64)
KEYCAP_FILL = (255, 255, 255, 13)

# Overlay used by pause screen: rgba(8,9,12,0.85)
OVERLAY_DARK = (8, 9, 12)
OVERLAY_ALPHA = 217
