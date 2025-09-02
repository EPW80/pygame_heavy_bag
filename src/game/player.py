"""
Player character with combat mechanics for the Heavy Bag Training game.
"""

import pygame
import math
from ..utils.constants import (
    RED,
    GOLD,
    YELLOW,
    BLUE,
    WHITE,
    BLACK,
    PunchType,
    Difficulty,
)
from .graphics import graphics_manager


class Player:
    """Player character with punching mechanics and stats."""

    def __init__(self, x: float, y: float, difficulty: Difficulty):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 80
        self.punch_cooldown = 0
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.combo_timer = 0
        self.power_meter = 0
        self.max_power = 100
        self.stamina = 100
        self.max_stamina = 100
        self.current_punch = None
        self.animation_frame = 0
        self.facing_right = True
        self.move_speed = 5
        self.total_punches = 0
        self.rage_mode = False
        self.rage_timer = 0
        self.multiplier = 1.0
        self.multiplier_timer = 0

        # Difficulty adjustments
        self.stamina_regen = {
            Difficulty.EASY: 0.5,
            Difficulty.NORMAL: 0.3,
            Difficulty.HARD: 0.2,
            Difficulty.EXPERT: 0.1,
        }[difficulty]

    def update(self) -> None:
        """Update player state, timers, and regeneration."""
        if self.punch_cooldown > 0:
            self.punch_cooldown -= 1

        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            if self.combo > self.max_combo:
                self.max_combo = self.combo
            self.combo = 0

        # Regenerate stamina
        if self.stamina < self.max_stamina:
            self.stamina = min(
                self.max_stamina, self.stamina + self.stamina_regen
            )

        # Build power meter
        if self.power_meter < self.max_power:
            self.power_meter += 0.5

        # Update animation
        if self.animation_frame > 0:
            self.animation_frame -= 1

        # Update rage mode
        if self.rage_timer > 0:
            self.rage_timer -= 1
            if self.rage_timer == 0:
                self.rage_mode = False

        # Update multiplier
        if self.multiplier_timer > 0:
            self.multiplier_timer -= 1
            if self.multiplier_timer == 0:
                self.multiplier = 1.0

    def punch(self, punch_type: PunchType) -> bool:
        """Attempt to throw a punch of the specified type."""
        stamina_cost = {
            PunchType.JAB: 5,
            PunchType.CROSS: 8,
            PunchType.HOOK: 10,
            PunchType.UPPERCUT: 12,
        }[punch_type]

        if self.rage_mode:
            stamina_cost = stamina_cost // 2

        if self.punch_cooldown == 0 and self.stamina >= stamina_cost:
            self.punch_cooldown = 15 if not self.rage_mode else 10
            self.stamina -= stamina_cost
            self.current_punch = punch_type
            self.animation_frame = 15
            self.combo += 1
            self.combo_timer = 60
            self.total_punches += 1
            return True
        return False

    def special_move(self) -> bool:
        """Execute a special attack if power meter is full."""
        if self.power_meter >= self.max_power and self.stamina >= 20:
            self.power_meter = 0
            self.stamina -= 20
            self.animation_frame = 20
            return True
        return False

    def activate_rage(self) -> None:
        """Activate rage mode for enhanced performance."""
        self.rage_mode = True
        self.rage_timer = 300  # 5 seconds

    def activate_multiplier(self) -> None:
        """Activate score multiplier power-up."""
        self.multiplier = 2.0
        self.multiplier_timer = 300

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the player character with enhanced sprite graphics."""
        head_x = self.x
        head_y = self.y

        # Determine which sprite to use
        sprite_name = "player_idle"
        if self.animation_frame > 10 and self.current_punch:
            punch_names = {
                PunchType.JAB: "jab",
                PunchType.CROSS: "cross",
                PunchType.HOOK: "hook",
                PunchType.UPPERCUT: "uppercut",
            }
            punch_name = punch_names.get(self.current_punch, 'idle')
            sprite_name = f"player_{punch_name}"

        # Get sprite from graphics manager
        sprite = graphics_manager.get_sprite(sprite_name)

        if sprite:
            # Apply transformations for facing direction
            display_sprite = sprite
            if not self.facing_right:
                display_sprite = pygame.transform.flip(sprite, True, False)

            # Apply rage mode effects
            if self.rage_mode:
                # Create rage aura effect
                aura_size = (
                    sprite.get_width() + 20,
                    sprite.get_height() + 20
                )
                aura_surface = pygame.Surface(aura_size, pygame.SRCALPHA)
                for i in range(3):
                    pygame.draw.circle(
                        aura_surface,
                        RED,
                        (aura_surface.get_width() // 2,
                         aura_surface.get_height() // 2),
                        40 + i * 10,
                        2,
                    )

                # Blit aura first
                aura_rect = aura_surface.get_rect(
                    center=(head_x, head_y + 20)
                )
                screen.blit(aura_surface, aura_rect)

                # Add red tint to sprite
                rage_sprite = display_sprite.copy()
                rage_overlay = pygame.Surface(
                    rage_sprite.get_size(), pygame.SRCALPHA
                )
                rage_overlay.fill((*RED, 80))
                rage_sprite.blit(
                    rage_overlay, (0, 0), special_flags=pygame.BLEND_ADD
                )
                display_sprite = rage_sprite

            # Add screen shake effect during powerful attacks
            offset_x = 0
            offset_y = 0
            if self.animation_frame > 10 and self.current_punch in [
                PunchType.CROSS,
                PunchType.UPPERCUT,
            ]:
                offset_x = math.sin(self.animation_frame * 0.5) * 2
                offset_y = math.cos(self.animation_frame * 0.3) * 1

            # Draw the sprite
            sprite_rect = display_sprite.get_rect(
                center=(head_x + offset_x, head_y + offset_y)
            )
            screen.blit(display_sprite, sprite_rect)

            # Add special effects based on state
            self._draw_special_effects(screen, head_x, head_y)
        else:
            # Fallback to original drawing method if sprite not found
            self._draw_fallback(screen, head_x, head_y)

    def _draw_special_effects(
        self, screen: pygame.Surface, x: float, y: float
    ) -> None:
        """Draw additional visual effects on the player."""
        # Power meter charging effect
        if self.power_meter >= self.max_power:
            # Golden glow when power is full
            glow_surface = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*GOLD, 60), (50, 50), 40)
            pygame.draw.circle(glow_surface, (*GOLD, 30), (50, 50), 50)
            glow_rect = glow_surface.get_rect(center=(x, y + 20))
            screen.blit(glow_surface, glow_rect)

        # Multiplier effect
        if self.multiplier > 1:
            mult_color = GOLD if self.multiplier >= 2 else YELLOW
            pygame.draw.circle(
                screen, mult_color, (int(x), int(y - 40)), 15, 3
            )
            font = pygame.font.Font(None, 24)
            mult_text = font.render(
                f"{self.multiplier:.1f}x", True, mult_color
            )
            mult_rect = mult_text.get_rect(center=(x, y - 40))
            screen.blit(mult_text, mult_rect)

        # Low stamina effect (breathing/panting)
        if self.stamina < 30:
            # Tired breathing effect
            ticks = pygame.time.get_ticks()
            breathing_alpha = int(50 + math.sin(ticks * 0.01) * 30)
            tired_overlay = pygame.Surface((80, 80), pygame.SRCALPHA)
            tired_overlay.fill((*BLUE, breathing_alpha))
            tired_rect = tired_overlay.get_rect(center=(x, y))
            screen.blit(tired_overlay, tired_rect)

        # Combo streak effect
        if self.combo >= 5:
            streak_effect = graphics_manager.create_combo_effect(self.combo)
            if streak_effect:
                streak_rect = streak_effect.get_rect(center=(x, y - 60))
                screen.blit(streak_effect, streak_rect)

    def _draw_fallback(
        self, screen: pygame.Surface, head_x: float, head_y: float
    ) -> None:
        """Fallback drawing method using basic shapes."""
        # Rage mode aura
        if self.rage_mode:
            for i in range(3):
                alpha = 100 - i * 30
                pygame.draw.circle(
                    screen, (255, 0, 0, alpha), (head_x, head_y + 20),
                    40 + i * 10, 2
                )

        # Head
        head_color = RED if self.rage_mode else WHITE
        pygame.draw.circle(screen, head_color, (head_x, head_y), 18)
        pygame.draw.circle(screen, BLACK, (head_x, head_y), 18, 2)

        # Eyes
        eye_offset = 5 if self.facing_right else -5
        eye_color = RED if self.rage_mode else BLACK
        pygame.draw.circle(
            screen, eye_color, (head_x + eye_offset, head_y - 3), 2
        )
        pygame.draw.circle(
            screen, eye_color, (head_x + eye_offset, head_y + 3), 2
        )

        # Body
        body_top = head_y + 18
        body_bottom = body_top + 35
        body_color = head_color
        pygame.draw.line(
            screen, body_color, (head_x, body_top), (head_x, body_bottom), 4
        )

        # Arms
        arm_y = body_top + 10
        punch_dir = 1 if self.facing_right else -1

        if self.animation_frame > 10:  # Punching animation
            punch_positions = {
                PunchType.JAB: (35, -5),
                PunchType.CROSS: (40, 0),
                PunchType.HOOK: (30, -15),
                PunchType.UPPERCUT: (25, -25),
            }

            if self.current_punch in punch_positions:
                px, py = punch_positions[self.current_punch]
                pygame.draw.line(
                    screen,
                    body_color,
                    (head_x, arm_y),
                    (head_x + px * punch_dir, arm_y + py),
                    4,
                )
                glove_color = GOLD if self.rage_mode else RED
                pygame.draw.circle(
                    screen,
                    glove_color,
                    (head_x + px * punch_dir, arm_y + py),
                    6
                )
        else:
            # Idle arms
            glove_color = GOLD if self.rage_mode else RED
            pygame.draw.line(
                screen,
                body_color,
                (head_x, arm_y),
                (head_x + 20 * punch_dir, arm_y + 5),
                4,
            )
            pygame.draw.line(
                screen,
                body_color,
                (head_x, arm_y),
                (head_x - 20 * punch_dir, arm_y + 5),
                4,
            )
            pygame.draw.circle(
                screen, glove_color, (head_x + 20 * punch_dir, arm_y + 5), 5
            )
            pygame.draw.circle(
                screen, glove_color, (head_x - 20 * punch_dir, arm_y + 5), 5
            )

        # Legs
        leg_top = body_bottom
        leg_bottom = leg_top + 25
        pygame.draw.line(
            screen, body_color, (head_x, leg_top), (head_x - 12, leg_bottom), 4
        )
        pygame.draw.line(
            screen, body_color, (head_x, leg_top), (head_x + 12, leg_bottom), 4
        )

        # Feet
        pygame.draw.ellipse(
            screen, body_color, (head_x - 18, leg_bottom - 3, 12, 6)
        )
        pygame.draw.ellipse(
            screen, body_color, (head_x + 6, leg_bottom - 3, 12, 6)
        )
