"""
Settings screen (design handoff screen 1f) — implements the previously
stubbed "Settings" menu option.

Row 0 is the difficulty card strip (←/→ cycles); the remaining rows are
pill toggles for GameSettings fields. Mutates the GameSettings instance
passed in; GameManager persists it when the screen is left.
"""

import pygame

from src.utils import theme
from src.utils.constants import (
    SCREEN_WIDTH,
    Difficulty,
    GameSettings,
    PLAYER_STAMINA_REGEN_EASY,
    PLAYER_STAMINA_REGEN_NORMAL,
    PLAYER_STAMINA_REGEN_HARD,
    PLAYER_STAMINA_REGEN_EXPERT,
)
from src.utils.fonts import get_font
from src.game import ui

_DIFFICULTIES = [
    (Difficulty.EASY, "EASY", "Forgiving bag physics, quick recovery", PLAYER_STAMINA_REGEN_EASY),
    (Difficulty.NORMAL, "NORMAL", "The intended training experience", PLAYER_STAMINA_REGEN_NORMAL),
    (Difficulty.HARD, "HARD", "Lively bag, slower recovery", PLAYER_STAMINA_REGEN_HARD),
    (Difficulty.EXPERT, "EXPERT", "Unforgiving physics, minimal rest", PLAYER_STAMINA_REGEN_EXPERT),
]

_TOGGLES = [
    ("sound_enabled", "Sound", "Punch impacts and UI feedback"),
    ("particle_effects", "Particle effects", "Sparks, dust and sweat on impact"),
    ("show_fps", "FPS counter", "Show frames per second while training"),
    ("hud_variant", "Minimal HUD", "Slim meters only — for players who know the moves"),
]


class SettingsScreen:
    """Interactive settings editor over the shared GameSettings."""

    def __init__(self, settings: GameSettings):
        self.settings = settings
        self.cursor = 0  # 0 = difficulty strip, 1.. = toggle rows

    def _row_count(self) -> int:
        return 1 + len(_TOGGLES)

    def _toggle(self, field: str) -> None:
        if field == "hud_variant":
            self.settings.hud_variant = (
                "minimal" if self.settings.hud_variant == "full" else "full"
            )
        else:
            setattr(self.settings, field, not getattr(self.settings, field))

    def _cycle_difficulty(self, direction: int) -> None:
        order = [d[0] for d in _DIFFICULTIES]
        i = order.index(self.settings.difficulty)
        self.settings.difficulty = order[(i + direction) % len(order)]

    def handle_input(self, event: pygame.event.Event) -> str:
        """Returns "back" when the screen should close."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"
            if event.key == pygame.K_UP:
                self.cursor = (self.cursor - 1) % self._row_count()
            elif event.key == pygame.K_DOWN:
                self.cursor = (self.cursor + 1) % self._row_count()
            elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                direction = 1 if event.key == pygame.K_RIGHT else -1
                if self.cursor == 0:
                    self._cycle_difficulty(direction)
                else:
                    self._toggle(_TOGGLES[self.cursor - 1][0])
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.cursor == 0:
                    self._cycle_difficulty(1)
                else:
                    self._toggle(_TOGGLES[self.cursor - 1][0])
        return None

    def draw(self, screen: pygame.Surface) -> None:
        s = theme.s
        screen.fill(theme.BG)
        left = s(theme.MARGIN_CONTENT)

        # Header
        font_eyebrow = get_font("barlow-semibold", 17)
        ui.draw_tracked_label(
            screen, (left, s(90)), "PRO EDITION", font_eyebrow, theme.GOLD, s(4)
        )
        header = get_font("bebas", 110).render("SETTINGS", True, theme.TEXT_PRIMARY)
        screen.blit(header, (left - s(4), s(112)))

        # ESC hint top-right
        esc_rect = ui.draw_keycap(
            screen, (SCREEN_WIDTH - s(230), s(120)), "ESC", size=s(38)
        )
        hint = get_font("barlow-medium", 18).render("Back to menu", True, theme.TEXT_DIM)
        hint.set_alpha(theme.TEXT_DIM_ALPHA)
        screen.blit(hint, (esc_rect.right + s(14), s(120) - hint.get_height() // 2))

        y = s(290)

        # DIFFICULTY section
        ui.draw_tracked_label(
            screen,
            (left, y),
            "DIFFICULTY",
            font_eyebrow,
            theme.TEXT_DIM,
            s(4),
            alpha=theme.TEXT_DIM_ALPHA,
        )
        y += s(40)
        card_gap = s(22)
        card_w = (SCREEN_WIDTH - 2 * left - 3 * card_gap) // 4
        card_h = s(190)
        font_card = get_font("bebas", 48)
        font_desc = get_font("barlow", 15)
        font_stat = get_font("barlow-semibold", 16)
        for i, (diff, name, desc, regen) in enumerate(_DIFFICULTIES):
            rect = pygame.Rect(left + i * (card_w + card_gap), y, card_w, card_h)
            selected = self.settings.difficulty == diff
            ui.draw_card(screen, rect, gold=selected)
            title = font_card.render(name, True, theme.GOLD if selected else theme.TEXT_PRIMARY)
            screen.blit(title, (rect.left + s(24), rect.top + s(20)))
            # One-line description, wrapped if needed
            desc_surf = font_desc.render(desc, True, theme.TEXT_DIM)
            desc_surf.set_alpha(theme.TEXT_DIM_ALPHA)
            screen.blit(desc_surf, (rect.left + s(24), rect.top + s(86)))
            stat = font_stat.render(f"+{regen}/sec stamina", True, theme.STAMINA_GREEN)
            screen.blit(stat, (rect.left + s(24), rect.bottom - s(44)))
            if selected:
                tab_font = get_font("barlow-bold", 13)
                tab_w = ui.tracked_label_width("SELECTED", tab_font, s(2)) + s(20)
                tab = pygame.Rect(rect.right - tab_w, rect.top, tab_w, s(28))
                pygame.draw.rect(screen, theme.GOLD, tab)
                ui.draw_tracked_label(
                    screen, (tab.left + s(10), tab.top + s(6)), "SELECTED", tab_font, theme.PANEL, s(2)
                )
        # Cursor highlight for the difficulty strip
        if self.cursor == 0:
            strip = pygame.Rect(left - s(14), y - s(14), SCREEN_WIDTH - 2 * left + s(28), card_h + s(28))
            pygame.draw.rect(screen, (*theme.GOLD, 90), strip, 1)
        y += card_h + s(56)

        # GAME section
        ui.draw_tracked_label(
            screen,
            (left, y),
            "GAME",
            font_eyebrow,
            theme.TEXT_DIM,
            s(4),
            alpha=theme.TEXT_DIM_ALPHA,
        )
        y += s(40)
        row_w = s(840)
        row_h = s(72)
        font_row = get_font("barlow-semibold", 20)
        font_sub = get_font("barlow", 14)
        for i, (field, label, sub) in enumerate(_TOGGLES):
            rect = pygame.Rect(left, y + i * (row_h + s(12)), row_w, row_h)
            selected = self.cursor == i + 1
            ui.draw_panel(screen, rect, alpha=140, border=True)
            if selected:
                pygame.draw.rect(screen, theme.GOLD, rect, 1)
                pygame.draw.rect(
                    screen, theme.GOLD, (rect.left, rect.top, s(4), rect.height)
                )
            name = font_row.render(label, True, theme.TEXT_PRIMARY)
            screen.blit(name, (rect.left + s(28), rect.top + s(12)))
            sub_surf = font_sub.render(sub, True, theme.TEXT_DIM)
            sub_surf.set_alpha(theme.TEXT_DIM_ALPHA)
            screen.blit(sub_surf, (rect.left + s(28), rect.top + s(40)))
            if field == "hud_variant":
                on = self.settings.hud_variant == "minimal"
            else:
                on = bool(getattr(self.settings, field))
            ui.draw_toggle(
                screen,
                (rect.right - s(92), rect.centery - s(16)),
                on,
            )

        # Footer hints
        hint_y = rect.bottom + s(46)
        font_hint = get_font("barlow-medium", 18)
        x = left
        for caps, label in ((("↑", "↓"), "Navigate"), (("←", "→"), "Adjust"), (("ENTER",), "Toggle")):
            for cap in caps:
                cap_rect = ui.draw_keycap(screen, (x + s(22), hint_y), cap, size=s(38))
                x = cap_rect.right + s(10)
            text = font_hint.render(label, True, theme.TEXT_DIM)
            text.set_alpha(theme.TEXT_DIM_ALPHA)
            screen.blit(text, (x + s(4), hint_y - text.get_height() // 2))
            x += text.get_width() + s(40)
