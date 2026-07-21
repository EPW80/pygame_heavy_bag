"""
Heavy bag physics and rendering for the Heavy Bag Training game.
"""

from __future__ import annotations  # lazy annotations: pygame attrs are unavailable at import time on web (pygbag)

import pygame
import math
import random
from ..utils.constants import (
    BLACK,
    WHITE,
    RED,
    DARK_RED,
    GRAY,
    DARK_GRAY,
    ORANGE,
    YELLOW,
    BROWN,
    DARK_BROWN,
    PunchType,
    Difficulty,
    BAG_WIDTH,
    BAG_HEIGHT,
    BAG_MAX_ANGLE,
    BAG_CHAIN_LENGTH,
    BAG_MAX_DAMAGE,
    BAG_DAMAGE_RECOVERY,
    BAG_GLOW_THRESHOLD,
    BAG_GLOW_DURATION,
    BAG_DAMPING_EASY,
    BAG_DAMPING_NORMAL,
    BAG_DAMPING_HARD,
    BAG_DAMPING_EXPERT,
    BAG_SHAKE_DECAY,
    BAG_HIT_FORCE_DECAY,
    BAG_RAGE_MULTIPLIER,
    BAG_SHAKE_MULTIPLIER,
    BAG_DAMAGE_MULTIPLIER,
)
from .graphics import graphics_manager


class HeavyBag:
    """Physics-based heavy bag with realistic swinging motion."""

    def __init__(self, x: float, y: float, difficulty: Difficulty):
        self.x = x
        self.y = y
        self.width = BAG_WIDTH
        self.height = BAG_HEIGHT
        self.angle = 0
        self.angular_velocity = 0
        self.max_angle = BAG_MAX_ANGLE
        self.chain_length = BAG_CHAIN_LENGTH
        self.shake_offset = 0
        self.shake_intensity = 0
        self.damage = 0
        self.max_damage = BAG_MAX_DAMAGE

        # Difficulty adjustments
        self.damping = {
            Difficulty.EASY: BAG_DAMPING_EASY,
            Difficulty.NORMAL: BAG_DAMPING_NORMAL,
            Difficulty.HARD: BAG_DAMPING_HARD,
            Difficulty.EXPERT: BAG_DAMPING_EXPERT,
        }[difficulty]

        self.hit_force = 0
        self.is_glowing = False
        self.glow_timer = 0

        # Damped swing impulses: list of dicts {"t": seconds, "amp": degrees}
        # (design handoff §Combo animation spec)
        self._impulses = []
        # Map difficulty damping to the impulse decay rate so easier
        # difficulties settle faster (easy has the highest damping value).
        self._decay = 1.5 + 10 * (self.damping - BAG_DAMPING_EXPERT)

        # Font is created lazily: HeavyBag is constructed in tests without
        # pygame.font initialized.
        self._font_brand_cache = None

    def update(self) -> None:
        """Update bag physics and visual effects.

        Swing model per the design handoff: each hit adds a damped
        impulse angle(t) = A * sin(5.5t) * e^(-decay*t); concurrent
        impulses sum, and the result is clamped to the max angle.
        """
        prev_angle = self.angle
        total = 0.0
        alive = []
        for impulse in self._impulses:
            impulse["t"] += 1.0 / 60.0
            envelope = math.exp(-self._decay * impulse["t"])
            if envelope > 0.001:
                alive.append(impulse)
                total += impulse["amp"] * math.sin(5.5 * impulse["t"]) * envelope
        self._impulses = alive
        self.angle = max(-self.max_angle, min(self.max_angle, total))
        self.angular_velocity = self.angle - prev_angle

        # Update shake
        if self.shake_intensity > 0:
            self.shake_offset = random.uniform(
                -self.shake_intensity, self.shake_intensity
            )
            self.shake_intensity *= BAG_SHAKE_DECAY

        # Reset hit force
        self.hit_force *= BAG_HIT_FORCE_DECAY

        # Recover from damage
        if self.damage > 0:
            self.damage = max(0, self.damage - BAG_DAMAGE_RECOVERY)

        # Update glow
        if self.glow_timer > 0:
            self.glow_timer -= 1
            self.is_glowing = self.glow_timer % 10 < 5

    def hit(self, force: float, punch_type: PunchType, rage_mode: bool = False) -> None:
        """Apply a hit to the bag with physics and visual effects."""
        multiplier = BAG_RAGE_MULTIPLIER if rage_mode else 1.0
        self.hit_force = force * multiplier
        # Impulse amplitude fits the handoff anchors: jab 2.0 -> 9°,
        # cross 3.0 -> 17° (A = 8*force - 7, floor 6°).
        self._impulses.append(
            {"t": 0.0, "amp": max(6.0, 8.0 * force * multiplier - 7.0)}
        )
        self.shake_intensity = force * BAG_SHAKE_MULTIPLIER * multiplier
        self.damage = min(
            self.max_damage, self.damage + force * BAG_DAMAGE_MULTIPLIER * multiplier
        )

        if self.damage >= self.max_damage * BAG_GLOW_THRESHOLD:
            self.glow_timer = BAG_GLOW_DURATION

    def get_position(self) -> tuple[float, float]:
        """Get the current position of the bag considering swing and shake."""
        bag_x = self.x + self.chain_length * math.sin(math.radians(self.angle))
        bag_y = self.y + self.chain_length
        return bag_x + self.shake_offset, bag_y

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the enhanced heavy bag with sprite graphics and effects."""
        bag_x, bag_y = self.get_position()

        # Enhanced chain rendering with metallic effect
        self._draw_enhanced_chain(screen, bag_x, bag_y)

        # Draw mounting point with more detail
        self._draw_mounting_point(screen)

        # Get appropriate bag sprite based on damage
        damage_ratio = self.damage / self.max_damage
        sprite_name = "heavy_bag_damaged" if damage_ratio > 0.6 else "heavy_bag"
        bag_sprite = graphics_manager.get_sprite(sprite_name)

        if bag_sprite:
            # Apply damage effects to sprite
            display_sprite = self._apply_damage_effects(bag_sprite, damage_ratio)

            # Apply rotation based on angle
            if abs(self.angle) > 1:
                display_sprite = pygame.transform.rotate(display_sprite, -self.angle)

            # Glow effect when heavily damaged
            if self.is_glowing:
                self._draw_damage_glow(screen, bag_x, bag_y, display_sprite)

            # Draw the main bag sprite
            sprite_rect = display_sprite.get_rect(
                center=(bag_x, bag_y + self.height // 2)
            )
            screen.blit(display_sprite, sprite_rect)

            # Add additional visual effects
            self._draw_additional_effects(screen, bag_x, bag_y, damage_ratio)
        else:
            # Fallback to original drawing method
            self._draw_fallback_bag(screen, bag_x, bag_y)

    def _draw_enhanced_chain(
        self, screen: pygame.Surface, bag_x: float, bag_y: float
    ) -> None:
        """Draw enhanced chain with metallic effects."""
        segments = 8
        for i in range(segments):
            t = (i + 1) / segments
            chain_x = self.x + (bag_x - self.x) * t
            chain_y = self.y + (bag_y - self.y) * t
            prev_x = self.x if i == 0 else self.x + (bag_x - self.x) * (i / segments)
            prev_y = self.y if i == 0 else self.y + (bag_y - self.y) * (i / segments)

            # Main chain link
            pygame.draw.line(screen, DARK_GRAY, (prev_x, prev_y), (chain_x, chain_y), 6)
            # Highlight
            pygame.draw.line(
                screen, GRAY, (prev_x + 1, prev_y + 1), (chain_x + 1, chain_y + 1), 2
            )

            # Chain links (rectangles)
            if i % 2 == 0:
                link_rect = pygame.Rect(chain_x - 3, chain_y - 6, 6, 12)
                pygame.draw.rect(screen, DARK_GRAY, link_rect)
                pygame.draw.rect(screen, GRAY, link_rect, 1)

    def _draw_mounting_point(self, screen: pygame.Surface) -> None:
        """Draw enhanced mounting point with more detail."""
        # Main mounting bracket
        pygame.draw.circle(screen, DARK_GRAY, (int(self.x), int(self.y)), 15)
        pygame.draw.circle(screen, GRAY, (int(self.x), int(self.y)), 12)
        pygame.draw.circle(screen, (120, 120, 120), (int(self.x), int(self.y)), 8)

        # Bolts
        for angle in [0, 90, 180, 270]:
            bolt_x = self.x + math.cos(math.radians(angle)) * 10
            bolt_y = self.y + math.sin(math.radians(angle)) * 10
            pygame.draw.circle(screen, DARK_GRAY, (int(bolt_x), int(bolt_y)), 2)

    def _apply_damage_effects(
        self, sprite: pygame.Surface, damage_ratio: float
    ) -> pygame.Surface:
        """Apply visual damage effects to the bag sprite."""
        damaged_sprite = sprite.copy()

        if damage_ratio > 0.3:
            # Add red tint for damage
            damage_overlay = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
            red_intensity = int(damage_ratio * 100)
            damage_overlay.fill((red_intensity, 0, 0, int(damage_ratio * 80)))
            damaged_sprite.blit(damage_overlay, (0, 0), special_flags=pygame.BLEND_ADD)

        if damage_ratio > 0.7:
            # Add wear marks
            for _ in range(int(damage_ratio * 5)):
                x = random.randint(10, sprite.get_width() - 10)
                y = random.randint(10, sprite.get_height() - 10)
                pygame.draw.circle(
                    damaged_sprite, DARK_RED, (x, y), random.randint(2, 5)
                )

        return damaged_sprite

    def _draw_damage_glow(
        self, screen: pygame.Surface, x: float, y: float, sprite: pygame.Surface
    ) -> None:
        """Draw glowing effect for heavily damaged bag."""
        glow_surface = pygame.Surface(
            (sprite.get_width() + 20, sprite.get_height() + 20), pygame.SRCALPHA
        )

        # Multiple glow rings
        for i in range(3):
            center = (glow_surface.get_width() // 2, glow_surface.get_height() // 2)
            pygame.draw.ellipse(
                glow_surface,
                RED,
                (
                    center[0] - 50 - i * 5,
                    center[1] - 100 - i * 5,
                    100 + i * 10,
                    200 + i * 10,
                ),
                3,
            )

        glow_rect = glow_surface.get_rect(center=(x, y + self.height // 2))
        screen.blit(glow_surface, glow_rect)

    def _draw_additional_effects(
        self, screen: pygame.Surface, x: float, y: float, damage_ratio: float
    ) -> None:
        """Draw additional visual effects around the bag.

        The damage bar lives in the HUD's BAG chip now, and the swing
        reads through the bag's own motion — no extra trail overlay
        (design handoff screen 2).
        """

    def _draw_fallback_bag(
        self, screen: pygame.Surface, bag_x: float, bag_y: float
    ) -> None:
        """Fallback drawing method using basic shapes."""
        # Draw bag with damage visualization
        bag_rect = pygame.Rect(bag_x - self.width // 2, bag_y, self.width, self.height)

        # Glow effect when heavily damaged
        if self.is_glowing:
            glow_rect = bag_rect.inflate(10, 10)
            pygame.draw.ellipse(screen, (255, 100, 100), glow_rect, 2)

        # Main bag color (changes with damage)
        damage_ratio = self.damage / self.max_damage
        bag_color = (
            min(255, 139 + int(damage_ratio * 116)),
            max(0, 69 - int(damage_ratio * 69)),
            max(0, 19 - int(damage_ratio * 19)),
        )
        pygame.draw.ellipse(screen, bag_color, bag_rect)

        # Highlight
        highlight_rect = pygame.Rect(
            bag_x - self.width // 2 + 10, bag_y + 10, self.width // 3, self.height // 2
        )
        pygame.draw.ellipse(screen, BROWN, highlight_rect)

        # Stitching
        for i in range(3):
            y_offset = self.height // 4 + i * (self.height // 4)
            pygame.draw.arc(
                screen,
                BLACK,
                (bag_x - self.width // 2 + 5, bag_y + y_offset, self.width - 10, 20),
                0,
                math.pi,
                2,
            )

        # Brand text
        if self._font_brand_cache is None:
            from src.utils.fonts import get_font

            self._font_brand_cache = get_font("bebas", 30)
        text = self._font_brand_cache.render("HEAVY", True, DARK_BROWN)
        text_rect = text.get_rect(center=(bag_x, bag_y + self.height // 2))
        screen.blit(text, text_rect)
