"""
Menu system for the Heavy Bag Training game.
"""

import pygame
from ..utils.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    BLACK, WHITE, GOLD, LIGHT_GRAY
)


class Menu:
    """Main menu interface with navigation and options."""

    def __init__(self):
        self.font_title = pygame.font.Font(None, 72)
        self.font_option = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        self.selected_option = 0
        self.options = ["Start Game", "Tutorial", "Settings", "Quit"]

    def handle_input(self, event: pygame.event.Event) -> str:
        """Handle keyboard input for menu navigation."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                return self.options[self.selected_option]
        return None

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the menu interface."""
        # Background
        screen.fill(BLACK)

        # Title
        title = self.font_title.render("HEAVY BAG TRAINING", True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title, title_rect)

        subtitle = self.font_small.render("Pro Edition", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 200))
        screen.blit(subtitle, subtitle_rect)

        # Options
        for i, option in enumerate(self.options):
            color = GOLD if i == self.selected_option else WHITE
            text = self.font_option.render(option, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 300 + i * 80))
            screen.blit(text, text_rect)

            if i == self.selected_option:
                pygame.draw.rect(screen, GOLD, text_rect.inflate(20, 10), 3)

        # Instructions
        instructions = self.font_small.render(
            "Use Arrow Keys to Navigate, Enter to Select", True, LIGHT_GRAY
        )
        inst_rect = instructions.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        )
        screen.blit(instructions, inst_rect)
