"""
Menu system for the Heavy Bag Training game.

Redesigned per design_handoff_heavy_bag_ui (screen 1a): gym backdrop with a
left-to-right dark gradient, left-aligned title column and menu rows, save
stats bottom-right, keycap hints bottom-left.
"""

from __future__ import annotations  # lazy annotations: pygame attrs are unavailable at import time on web (pygbag)

import pygame

from src.utils import theme
from src.utils.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from src.utils.fonts import get_font
from src.game import ui


class Menu:
    """Main menu interface with navigation and options."""

    def __init__(self):
        self.selected_option = 0
        # Load-bearing strings: GameManager.handle_events dispatches on them.
        self.options = ["Start Game", "Tutorial", "Settings", "Quit"]
        self.high_score = 0
        self.total_punches = 0
        self.best_combo = 0
        self._backdrop = None

    def set_stats(self, high_score: int, total_punches: int, best_combo: int) -> None:
        self.high_score = high_score
        self.total_punches = total_punches
        self.best_combo = best_combo

    def handle_input(self, event: pygame.event.Event) -> str:
        """Handle keyboard input for menu navigation."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return self.options[self.selected_option]
        return None

    def _build_backdrop(self) -> pygame.Surface:
        """Gym scene at 50% + left->right dark gradient, built once."""
        from src.game.graphics import graphics_manager

        backdrop = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        backdrop.fill(theme.BG)
        gym = graphics_manager.get_background("gym")
        if gym:
            dimmed = gym.copy()
            dimmed.set_alpha(128)
            backdrop.blit(dimmed, (0, 0))
        backdrop.blit(
            ui.make_horizontal_alpha_gradient(
                (SCREEN_WIDTH, SCREEN_HEIGHT), (8, 9, 12), 240, 64
            ),
            (0, 0),
        )
        return backdrop

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the menu interface."""
        s = theme.s
        if self._backdrop is None:
            self._backdrop = self._build_backdrop()
        screen.blit(self._backdrop, (0, 0))

        left = s(theme.MARGIN_CONTENT)

        # Title block: chip + two display lines + menu rows, vertically centered
        font_title = get_font("bebas", 190)
        row_h = s(74)
        title_h = font_title.get_height()
        chip_h = s(50)
        block_h = chip_h + 2 * title_h + s(30) + row_h * len(self.options)
        y = (SCREEN_HEIGHT - block_h) // 2

        ui.draw_chip(screen, (left, y), "PRO EDITION", theme.GOLD, font_size=17)
        y += chip_h + s(10)

        heavy = font_title.render("HEAVY BAG", True, theme.TEXT_PRIMARY)
        screen.blit(heavy, (left - s(6), y))
        y += title_h - s(30)
        training = font_title.render("TRAINING", True, theme.GOLD)
        screen.blit(training, (left - s(6), y))
        y += title_h + s(10)

        # Menu rows (display uppercase; option strings stay untouched)
        row_w = s(480)
        for i, option in enumerate(self.options):
            rect = pygame.Rect(left, y + i * row_h, row_w, row_h - s(10))
            ui.draw_menu_row(screen, rect, option.upper(), i == self.selected_option)

        # Bottom-left key hints
        hint_y = SCREEN_HEIGHT - s(70)
        font_hint = get_font("barlow-medium", 18)
        x = left
        for cap, label in (("↑", None), ("↓", "NAVIGATE"), ("ENTER", "SELECT")):
            cap_rect = ui.draw_keycap(screen, (x + s(24), hint_y), cap, size=s(38))
            x = cap_rect.right + s(12)
            if label:
                text = font_hint.render(label, True, theme.TEXT_DIM)
                text.set_alpha(theme.TEXT_DIM_ALPHA)
                screen.blit(text, (x, hint_y - text.get_height() // 2))
                x += text.get_width() + s(36)

        # Bottom-right save stats
        stats = [
            ("BEST SCORE", f"{self.high_score:,}", theme.GOLD),
            ("TOTAL PUNCHES", f"{self.total_punches:,}", theme.TEXT_PRIMARY),
            ("BEST COMBO", f"{self.best_combo}×", theme.TEXT_PRIMARY),
        ]
        font_label = get_font("barlow-semibold", 16)
        font_value = get_font("bebas", 64)
        x = SCREEN_WIDTH - s(80)
        base_y = SCREEN_HEIGHT - s(64)
        for label, value, color in reversed(stats):
            value_surf = font_value.render(value, True, color)
            label_w = ui.tracked_label_width(label, font_label, s(3))
            col_w = max(value_surf.get_width(), label_w)
            x -= col_w
            ui.draw_tracked_label(
                screen,
                (x, base_y - font_value.get_height() - s(6)),
                label,
                font_label,
                theme.TEXT_DIM,
                s(3),
                alpha=theme.TEXT_DIM_ALPHA,
            )
            screen.blit(value_surf, (x, base_y - font_value.get_height() + s(8)))
            x -= s(56)
