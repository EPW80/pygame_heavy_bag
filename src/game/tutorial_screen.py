"""
Tutorial / Move List screen (design handoff screen 1g) — implements the
previously stubbed "Tutorial" menu option.

Static content generated from ATTACK_PROPERTIES, rendered once into a
cached surface.
"""

from __future__ import annotations  # lazy annotations: pygame attrs are unavailable at import time on web (pygbag)

import pygame

from src.utils import theme
from src.utils.constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    ATTACK_PROPERTIES,
    PunchType,
    STAMINA_SPECIAL_MOVE,
)
from src.utils.fonts import get_font
from src.game import ui

# Key bindings mirror GameManager.handle_events
_MOVES = [
    ("Z", PunchType.JAB, "Jab", "Fast range-finder off the lead hand"),
    ("X", PunchType.CROSS, "Cross", "Straight power shot from the rear"),
    ("C", PunchType.HOOK, "Hook", "Short arc, big force up close"),
    ("V", PunchType.UPPERCUT, "Uppercut", "Rising shot from under the guard"),
    ("Q", PunchType.FRONT_KICK, "Front Kick", "Longest reach — keep the bag away"),
    ("W", PunchType.ROUNDHOUSE_KICK, "Roundhouse", "Maximum force, full turn"),
    ("E", PunchType.LOW_KICK, "Low Kick", "Quick chopping kick at the base"),
]

_MAX_REACH = 50.0
_MAX_FORCE = 5.0


class TutorialScreen:
    """Static move-list reference screen."""

    def __init__(self):
        self._surface = None

    def handle_input(self, event: pygame.event.Event) -> str:
        if event.type == pygame.KEYDOWN and event.key in (
            pygame.K_ESCAPE,
            pygame.K_RETURN,
        ):
            return "back"
        return None

    def draw(self, screen: pygame.Surface) -> None:
        if self._surface is None:
            self._surface = self._render()
        screen.blit(self._surface, (0, 0))

    def _render(self) -> pygame.Surface:
        s = theme.s
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        surface.fill(theme.BG)
        left = s(theme.MARGIN_CONTENT)

        # Header
        font_eyebrow = get_font("barlow-semibold", 17)
        ui.draw_tracked_label(
            surface, (left, s(70)), "TUTORIAL", font_eyebrow, theme.GOLD, s(4)
        )
        header = get_font("bebas", 110).render("MOVE LIST", True, theme.TEXT_PRIMARY)
        surface.blit(header, (left - s(4), s(92)))
        esc_rect = ui.draw_keycap(
            surface, (SCREEN_WIDTH - s(230), s(100)), "ESC", size=s(38)
        )
        hint = get_font("barlow-medium", 18).render(
            "Back to menu", True, theme.TEXT_DIM
        )
        hint.set_alpha(theme.TEXT_DIM_ALPHA)
        surface.blit(hint, (esc_rect.right + s(14), s(100) - hint.get_height() // 2))

        # 4x2 grid of attack cards + gold SPECIAL card in the 8th cell
        grid_top = s(250)
        gap = s(20)
        card_w = (SCREEN_WIDTH - 2 * left - 3 * gap) // 4
        card_h = s(240)
        font_name = get_font("bebas", 44)
        font_desc = get_font("barlow", 14)
        font_cost = get_font("barlow-bold", 15)
        font_bar_label = get_font("barlow-semibold", 12)

        cells = list(_MOVES) + [None]  # None = SPECIAL card
        for i, move in enumerate(cells):
            col, row = i % 4, i // 4
            rect = pygame.Rect(
                left + col * (card_w + gap),
                grid_top + row * (card_h + gap),
                card_w,
                card_h,
            )
            if move is None:
                self._special_card(surface, rect)
                continue
            key, punch, name, desc = move
            props = ATTACK_PROPERTIES[punch]
            ui.draw_card(surface, rect)
            pad = s(22)
            cap_size = s(40)
            ui.draw_keycap(
                surface,
                (rect.left + pad + cap_size // 2, rect.top + pad + cap_size // 2),
                key,
                size=cap_size,
            )
            cost = font_cost.render(
                f"−{props.stamina_cost} STA", True, theme.STAMINA_GREEN
            )
            surface.blit(
                cost, (rect.right - pad - cost.get_width(), rect.top + pad + s(8))
            )
            name_surf = font_name.render(name.upper(), True, theme.TEXT_PRIMARY)
            surface.blit(name_surf, (rect.left + pad, rect.top + s(74)))
            desc_surf = font_desc.render(desc, True, theme.TEXT_DIM)
            desc_surf.set_alpha(theme.TEXT_DIM_ALPHA)
            surface.blit(desc_surf, (rect.left + pad, rect.top + s(130)))
            # REACH / FORCE mini bars
            bar_w = card_w - 2 * pad - s(60)
            for j, (label, value, maximum, color) in enumerate(
                (
                    ("REACH", props.reach, _MAX_REACH, theme.TEXT_PRIMARY),
                    ("FORCE", props.force, _MAX_FORCE, theme.GOLD),
                )
            ):
                bar_y = rect.top + s(170) + j * s(28)
                lbl = font_bar_label.render(label, True, theme.TEXT_DIM)
                lbl.set_alpha(theme.TEXT_DIM_ALPHA)
                surface.blit(lbl, (rect.left + pad, bar_y - s(3)))
                ui.draw_mini_bar(
                    surface,
                    pygame.Rect(rect.left + pad + s(60), bar_y, bar_w, s(5)),
                    value / maximum,
                    color,
                )

        # Bottom strip: SCORING + POWER-UPS
        strip_y = grid_top + 2 * card_h + gap + s(36)
        font_strip_label = get_font("barlow-semibold", 15)
        font_strip = get_font("barlow", 15)
        ui.draw_tracked_label(
            surface,
            (left, strip_y),
            "SCORING",
            font_strip_label,
            theme.TEXT_DIM,
            s(3),
            alpha=theme.TEXT_DIM_ALPHA,
        )
        scoring = font_strip.render(
            "PERFECT +50 — strike while the bag hangs steady   ·   COMBO +20%/hit — chain within one second   ·   SPECIAL +100",
            True,
            theme.TEXT_PRIMARY,
        )
        surface.blit(scoring, (left, strip_y + s(26)))

        pu_x = left + s(980)
        ui.draw_tracked_label(
            surface,
            (pu_x, strip_y),
            "POWER-UPS",
            font_strip_label,
            theme.TEXT_DIM,
            s(3),
            alpha=theme.TEXT_DIM_ALPHA,
        )
        x = pu_x
        for color, label in (
            (theme.STAMINA_GREEN, "Stamina"),
            (theme.POWER_BLUE, "Power"),
            (theme.GOLD, "2× Multiplier"),
            (theme.RAGE_RED, "Rage"),
        ):
            cy = strip_y + s(26) + font_strip.get_height() // 2
            pygame.draw.circle(surface, color, (x + s(6), cy), s(6))
            lbl = font_strip.render(label, True, theme.TEXT_PRIMARY)
            surface.blit(lbl, (x + s(20), strip_y + s(26)))
            x += s(20) + lbl.get_width() + s(28)
        walk = font_strip.render("— walk into them", True, theme.TEXT_DIM)
        walk.set_alpha(theme.TEXT_DIM_ALPHA)
        surface.blit(walk, (x, strip_y + s(26)))

        return surface

    def _special_card(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        s = theme.s
        ui.draw_card(surface, rect, gold=True)
        pad = s(22)
        cap_size = s(40)
        ui.draw_keycap(
            surface,
            (rect.left + pad + s(38), rect.top + pad + cap_size // 2),
            "SPACE",
            size=cap_size,
            gold=True,
        )
        cost = get_font("barlow-bold", 15).render(
            f"−{STAMINA_SPECIAL_MOVE} STA", True, theme.STAMINA_GREEN
        )
        surface.blit(cost, (rect.right - pad - cost.get_width(), rect.top + pad + s(8)))
        name = get_font("bebas", 44).render("SPECIAL", True, theme.GOLD)
        surface.blit(name, (rect.left + pad, rect.top + s(74)))
        font_desc = get_font("barlow", 14)
        line1 = font_desc.render("Needs full power meter", True, theme.TEXT_DIM)
        line1.set_alpha(theme.TEXT_DIM_ALPHA)
        surface.blit(line1, (rect.left + pad, rect.top + s(130)))
        line2 = font_desc.render(
            "+100 points, massive knockback", True, theme.TEXT_PRIMARY
        )
        surface.blit(line2, (rect.left + pad, rect.top + s(156)))
