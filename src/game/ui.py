"""
Stateless UI drawing helpers shared by every redesigned screen.

All position/size arguments are in window pixels (callers scale spec values
with theme.s()). Helpers that need per-pixel alpha build a small SRCALPHA
surface and blit it, so callers can draw straight onto the screen.
"""

from typing import Optional, Tuple

import pygame

from src.utils import theme
from src.utils.fonts import get_font

Color = Tuple[int, int, int]


def draw_panel(
    surface: pygame.Surface,
    rect: pygame.Rect,
    alpha: int = theme.PANEL_ALPHA,
    border: bool = True,
) -> None:
    """HUD panel: translucent dark fill + 1px light border, square corners."""
    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    panel.fill((*theme.PANEL, alpha))
    if border:
        pygame.draw.rect(panel, theme.PANEL_BORDER, panel.get_rect(), 1)
    surface.blit(panel, rect.topleft)


def draw_card(surface: pygame.Surface, rect: pygame.Rect, gold: bool = False) -> None:
    """Stat/settings card: faint white fill + 1px border (gold when selected)."""
    card = pygame.Surface(rect.size, pygame.SRCALPHA)
    if gold:
        card.fill((*theme.GOLD, 18))
        pygame.draw.rect(card, (*theme.GOLD, 255), card.get_rect(), 1)
    else:
        card.fill(theme.CARD_FILL)
        pygame.draw.rect(card, theme.CARD_BORDER, card.get_rect(), 1)
    surface.blit(card, rect.topleft)


# Arrow/return symbols are missing from every available font (they render as
# tofu), so they are drawn as vector shapes instead of text.
_SYMBOLS = ("↑", "↓", "←", "→", "↵")


def draw_symbol(
    surface: pygame.Surface,
    center: Tuple[int, int],
    symbol: str,
    color: Color,
    height: int,
) -> None:
    """Draw ↑ ↓ ← → ↵ as line art centered on `center`."""
    cx, cy = center
    h = height // 2
    w = max(2, height // 3)
    lw = max(2, height // 6)
    if symbol in ("↑", "↓"):
        d = -1 if symbol == "↑" else 1
        tip = (cx, cy + d * h)
        pygame.draw.line(surface, color, (cx, cy - d * h), tip, lw)
        pygame.draw.line(surface, color, (cx - w, cy + d * (h - w)), tip, lw)
        pygame.draw.line(surface, color, (cx + w, cy + d * (h - w)), tip, lw)
    elif symbol in ("←", "→"):
        d = -1 if symbol == "←" else 1
        tip = (cx + d * h, cy)
        pygame.draw.line(surface, color, (cx - d * h, cy), tip, lw)
        pygame.draw.line(surface, color, (cx + d * (h - w), cy - w), tip, lw)
        pygame.draw.line(surface, color, (cx + d * (h - w), cy + w), tip, lw)
    elif symbol == "↵":
        tip = (cx - h, cy + w)
        pygame.draw.line(
            surface, color, (cx + h, cy - h + w // 2), (cx + h, cy + w), lw
        )
        pygame.draw.line(surface, color, (cx + h, cy + w), tip, lw)
        pygame.draw.line(surface, color, (cx - h + w, cy), tip, lw)
        pygame.draw.line(surface, color, (cx - h + w, cy + 2 * w), tip, lw)


def draw_keycap(
    surface: pygame.Surface,
    center: Tuple[int, int],
    label: str,
    size: Optional[int] = None,
    gold: bool = False,
) -> pygame.Rect:
    """Keyboard keycap chip. Returns the keycap rect for layout chaining."""
    size = size or theme.s(theme.KEYCAP_SIZE)
    if label in _SYMBOLS:
        width = size
    else:
        width = max(size, theme.s(16) + get_font("bebas", 24).size(label)[0])
    rect = pygame.Rect(0, 0, width, size)
    rect.center = center
    cap = pygame.Surface(rect.size, pygame.SRCALPHA)
    radius = theme.s(7)
    if gold:
        pygame.draw.rect(cap, (*theme.GOLD, 40), cap.get_rect(), border_radius=radius)
        pygame.draw.rect(
            cap, (*theme.GOLD, 255), cap.get_rect(), 1, border_radius=radius
        )
        text_color = theme.GOLD
    else:
        pygame.draw.rect(cap, theme.KEYCAP_FILL, cap.get_rect(), border_radius=radius)
        pygame.draw.rect(
            cap, theme.KEYCAP_BORDER, cap.get_rect(), 1, border_radius=radius
        )
        text_color = theme.TEXT_PRIMARY
    if label in _SYMBOLS:
        draw_symbol(
            cap, (rect.width // 2, rect.height // 2), label, text_color, size // 3
        )
    else:
        text = get_font("bebas", 24).render(label, True, text_color)
        cap.blit(text, text.get_rect(center=(rect.width // 2, rect.height // 2)))
    surface.blit(cap, rect.topleft)
    return rect


def draw_tracked_label(
    surface: pygame.Surface,
    pos: Tuple[int, int],
    text: str,
    font: pygame.font.Font,
    color: Color,
    tracking: int = 0,
    alpha: int = 255,
) -> pygame.Rect:
    """Render uppercase label text with letter-spacing via per-char advance.

    Returns the bounding rect of what was drawn.
    """
    x, y = pos
    start_x = x
    height = font.get_height()
    for ch in text:
        glyph = font.render(ch, True, color)
        if alpha < 255:
            glyph.set_alpha(alpha)
        surface.blit(glyph, (x, y))
        x += glyph.get_width() + tracking
    return pygame.Rect(start_x, y, x - start_x - tracking, height)


def tracked_label_width(text: str, font: pygame.font.Font, tracking: int = 0) -> int:
    if not text:
        return 0
    return sum(font.size(ch)[0] for ch in text) + tracking * (len(text) - 1)


def draw_segmented_bar(
    surface: pygame.Surface,
    rect: pygame.Rect,
    fraction: float,
    color: Color,
    segments: int = 10,
) -> None:
    """Segmented meter: filled portion in color, dark track, 2px dividers."""
    fraction = max(0.0, min(1.0, fraction))
    bar = pygame.Surface(rect.size, pygame.SRCALPHA)
    bar.fill((255, 255, 255, 18))
    fill_width = int(rect.width * fraction)
    if fill_width > 0:
        pygame.draw.rect(bar, (*color, 255), pygame.Rect(0, 0, fill_width, rect.height))
    divider_w = 2
    for i in range(1, segments):
        x = int(rect.width * i / segments) - divider_w // 2
        pygame.draw.rect(
            bar, (*theme.PANEL, 255), pygame.Rect(x, 0, divider_w, rect.height)
        )
    surface.blit(bar, rect.topleft)


def draw_mini_bar(
    surface: pygame.Surface,
    rect: pygame.Rect,
    fraction: float,
    color: Color,
) -> None:
    """Thin stat bar (tutorial reach/force): dim track + colored fill."""
    fraction = max(0.0, min(1.0, fraction))
    bar = pygame.Surface(rect.size, pygame.SRCALPHA)
    bar.fill((255, 255, 255, 25))
    fill_width = int(rect.width * fraction)
    if fill_width > 0:
        pygame.draw.rect(bar, (*color, 255), pygame.Rect(0, 0, fill_width, rect.height))
    surface.blit(bar, rect.topleft)


def draw_chip(
    surface: pygame.Surface,
    pos: Tuple[int, int],
    text: str,
    color: Color = theme.GOLD,
    font_size: int = 17,
    dot: bool = False,
    filled: bool = False,
) -> pygame.Rect:
    """Small bordered pill/chip label (e.g. PRO EDITION, IN RANGE, AMAZING)."""
    font = get_font("barlow-semibold", font_size)
    tracking = theme.s(4)
    text_w = tracked_label_width(text, font, tracking)
    pad_x, pad_y = theme.s(18), theme.s(8)
    dot_space = theme.s(16) if dot else 0
    rect = pygame.Rect(
        pos[0], pos[1], text_w + 2 * pad_x + dot_space, font.get_height() + 2 * pad_y
    )
    chip = pygame.Surface(rect.size, pygame.SRCALPHA)
    radius = rect.height // 2
    if filled:
        pygame.draw.rect(chip, (*color, 255), chip.get_rect(), border_radius=radius)
        text_color = theme.PANEL
    else:
        pygame.draw.rect(
            chip, (*theme.PANEL, 200), chip.get_rect(), border_radius=radius
        )
        pygame.draw.rect(chip, (*color, 255), chip.get_rect(), 1, border_radius=radius)
        text_color = color
    x = pad_x
    if dot:
        pygame.draw.circle(
            chip, (*color, 255), (pad_x + theme.s(4), rect.height // 2), theme.s(4)
        )
        x += dot_space
    draw_tracked_label(chip, (x, pad_y), text, font, text_color, tracking)
    surface.blit(chip, rect.topleft)
    return rect


def draw_menu_row(
    surface: pygame.Surface,
    rect: pygame.Rect,
    text: str,
    selected: bool,
    hint: str = "↵",
) -> None:
    """Menu/pause/settings row: gold left bar + tint when selected."""
    font = get_font("bebas", 42)
    if selected:
        row = pygame.Surface(rect.size, pygame.SRCALPHA)
        row.fill((*theme.GOLD, 20))  # rgba(240,195,48,0.08)
        surface.blit(row, rect.topleft)
        pygame.draw.rect(
            surface,
            theme.GOLD,
            pygame.Rect(rect.left, rect.top, theme.s(4), rect.height),
        )
        color = theme.GOLD
    else:
        color = theme.TEXT_DIM
    label = font.render(text, True, color)
    if not selected:
        label.set_alpha(theme.TEXT_DIM_ALPHA)
    surface.blit(
        label, (rect.left + theme.s(24), rect.centery - label.get_height() // 2)
    )
    if selected and hint:
        if hint in _SYMBOLS:
            size = theme.s(22)
            draw_symbol(
                surface,
                (rect.right - theme.s(24) - size // 2, rect.centery),
                hint,
                theme.GOLD,
                size,
            )
        else:
            hint_surf = get_font("bebas", 30).render(hint, True, theme.GOLD)
            hint_surf.set_alpha(180)
            surface.blit(
                hint_surf,
                (
                    rect.right - theme.s(24) - hint_surf.get_width(),
                    rect.centery - hint_surf.get_height() // 2,
                ),
            )


def draw_toggle(
    surface: pygame.Surface,
    pos: Tuple[int, int],
    on: bool,
) -> pygame.Rect:
    """Pill toggle: gold with dark knob right when on; dim with knob left when off."""
    w, h = theme.s(64), theme.s(32)
    rect = pygame.Rect(pos[0], pos[1], w, h)
    pill = pygame.Surface(rect.size, pygame.SRCALPHA)
    radius = h // 2
    knob_r = max(2, h // 2 - theme.s(5))
    if on:
        pygame.draw.rect(
            pill, (*theme.GOLD, 255), pill.get_rect(), border_radius=radius
        )
        pygame.draw.circle(pill, (*theme.PANEL, 255), (w - radius, h // 2), knob_r)
    else:
        pygame.draw.rect(
            pill, (255, 255, 255, 36), pill.get_rect(), border_radius=radius
        )
        pygame.draw.circle(
            pill, (*theme.TEXT_DIM, theme.TEXT_DIM_ALPHA), (radius, h // 2), knob_r
        )
    surface.blit(pill, rect.topleft)
    return rect


def draw_vertical_gradient(
    surface: pygame.Surface, rect: pygame.Rect, top: Color, bottom: Color
) -> None:
    """Cheap vertical gradient: 1px-wide column scaled to the rect."""
    column = pygame.Surface((1, rect.height))
    for y in range(rect.height):
        t = y / max(1, rect.height - 1)
        column.set_at(
            (0, y),
            (
                int(top[0] + (bottom[0] - top[0]) * t),
                int(top[1] + (bottom[1] - top[1]) * t),
                int(top[2] + (bottom[2] - top[2]) * t),
            ),
        )
    surface.blit(pygame.transform.scale(column, rect.size), rect.topleft)


def make_horizontal_alpha_gradient(
    size: Tuple[int, int], color: Color, alpha_left: int, alpha_right: int
) -> pygame.Surface:
    """SRCALPHA surface fading left->right; build once, cache at the caller."""
    grad = pygame.Surface((size[0], 1), pygame.SRCALPHA)
    for x in range(size[0]):
        t = x / max(1, size[0] - 1)
        a = int(alpha_left + (alpha_right - alpha_left) * t)
        grad.set_at((x, 0), (*color, a))
    return pygame.transform.scale(grad, size)


def make_vertical_alpha_gradient(
    size: Tuple[int, int], color: Color, alpha_top: int, alpha_bottom: int
) -> pygame.Surface:
    grad = pygame.Surface((1, size[1]), pygame.SRCALPHA)
    for y in range(size[1]):
        t = y / max(1, size[1] - 1)
        a = int(alpha_top + (alpha_bottom - alpha_top) * t)
        grad.set_at((0, y), (*color, a))
    return pygame.transform.scale(grad, size)


def make_radial_glow(radius: int, color: Color, max_alpha: int) -> pygame.Surface:
    """Soft radial glow via concentric alpha circles; build once and cache."""
    size = radius * 2
    glow = pygame.Surface((size, size), pygame.SRCALPHA)
    steps = max(8, radius // 3)
    for i in range(steps, 0, -1):
        r = int(radius * i / steps)
        a = int(max_alpha * (1 - i / steps) ** 2)
        if a > 0:
            pygame.draw.circle(glow, (*color, a), (radius, radius), r)
    return glow
