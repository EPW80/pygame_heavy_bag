"""
Graphics utilities for loading sprites, textures, and creating visual elements.
"""

import pygame
import math
import random
from typing import Optional, Dict, Tuple
from ..utils.constants import (
    BLACK,
    WHITE,
    RED,
    GREEN,
    BLUE,
    YELLOW,
    ORANGE,
    DARK_BROWN,
    GRAY,
    DARK_GRAY,
    LIGHT_GRAY,
    GOLD,
    DARK_RED,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)


class GraphicsManager:
    """Manages loading and caching of graphics assets."""

    def __init__(self) -> None:
        self.sprites: Dict[str, pygame.Surface] = {}
        self.backgrounds: Dict[str, pygame.Surface] = {}
        self.particles: Dict[str, pygame.Surface] = {}
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Ensure graphics are initialized (called when pygame is ready)."""
        if not self._initialized and pygame.get_init():
            self._init_procedural_graphics()
            self._initialized = True

    def _init_procedural_graphics(self) -> None:
        """Create procedural graphics when actual sprites aren't available."""
        # Create player sprite sheets
        self._create_player_sprites()

        # Create bag textures
        self._create_bag_textures()

        # Create particle textures
        self._create_particle_textures()

        # Create power-up sprites
        self._create_powerup_sprites()

        # Create backgrounds
        self._create_backgrounds()

    def _get_character_colors(self) -> dict:
        """Get color palette for character sprites.

        Returns:
            Dictionary of color names to RGB tuples
        """
        return {
            "skin": (255, 220, 177),
            "hair": (101, 67, 33),
            "shorts": (50, 50, 150),
            "tank": (200, 200, 200),
            "glove": (220, 20, 20),
        }

    def _draw_base_character(
        self, surface: pygame.Surface, colors: dict
    ) -> None:
        """Draw base character body on the given surface.

        Args:
            surface: Pygame surface to draw on
            colors: Dictionary of character colors
        """
        # Head with better proportions
        pygame.draw.circle(surface, colors["skin"], (40, 25), 20)
        pygame.draw.circle(surface, BLACK, (40, 25), 20, 2)

        # Hair
        pygame.draw.arc(
            surface, colors["hair"], (22, 7, 36, 30), 0, math.pi, 8
        )

        # Eyes with more detail
        pygame.draw.circle(surface, WHITE, (34, 22), 4)
        pygame.draw.circle(surface, WHITE, (46, 22), 4)
        pygame.draw.circle(surface, BLACK, (35, 22), 2)
        pygame.draw.circle(surface, BLACK, (45, 22), 2)
        pygame.draw.circle(surface, WHITE, (36, 21), 1)  # Eye highlights
        pygame.draw.circle(surface, WHITE, (46, 21), 1)

        # Nose and mouth
        pygame.draw.circle(surface, (200, 180, 150), (40, 28), 2)
        pygame.draw.arc(surface, BLACK, (37, 31, 6, 4), 0, math.pi, 1)

        # Neck
        pygame.draw.rect(surface, colors["skin"], (35, 44, 10, 8))

        # Tank top (torso)
        pygame.draw.rect(surface, colors["tank"], (25, 52, 30, 35))
        pygame.draw.rect(surface, DARK_GRAY, (25, 52, 30, 35), 2)

        # Arms with muscle definition
        pygame.draw.ellipse(surface, colors["skin"], (52, 55, 12, 25))
        pygame.draw.ellipse(surface, colors["skin"], (58, 75, 10, 20))
        pygame.draw.ellipse(surface, colors["skin"], (16, 55, 12, 25))
        pygame.draw.ellipse(surface, colors["skin"], (12, 75, 10, 20))

        # Boxing gloves with straps
        pygame.draw.circle(surface, colors["glove"], (63, 85), 8)
        pygame.draw.circle(surface, DARK_RED, (63, 85), 8, 2)
        pygame.draw.rect(surface, BLACK, (57, 82, 12, 3))

        pygame.draw.circle(surface, colors["glove"], (17, 85), 8)
        pygame.draw.circle(surface, DARK_RED, (17, 85), 8, 2)
        pygame.draw.rect(surface, BLACK, (11, 82, 12, 3))

        # Shorts
        pygame.draw.rect(surface, colors["shorts"], (28, 87, 24, 20))
        pygame.draw.rect(surface, DARK_GRAY, (28, 87, 24, 20), 2)

        # Legs with muscle definition
        pygame.draw.ellipse(surface, colors["skin"], (30, 105, 8, 18))
        pygame.draw.ellipse(surface, colors["skin"], (42, 105, 8, 18))

        # Boxing shoes
        pygame.draw.ellipse(surface, BLACK, (26, 118, 16, 8))
        pygame.draw.ellipse(surface, BLACK, (38, 118, 16, 8))
        pygame.draw.ellipse(surface, WHITE, (28, 119, 12, 4))
        pygame.draw.ellipse(surface, WHITE, (40, 119, 12, 4))

        # Sweat droplets
        pygame.draw.circle(surface, (150, 200, 255), (32, 15), 1)
        pygame.draw.circle(surface, (150, 200, 255), (48, 18), 1)

        # Muscle definition on arms
        pygame.draw.arc(
            surface, (200, 180, 150), (52, 60, 12, 15), 0, math.pi / 2, 1
        )
        pygame.draw.arc(
            surface,
            (200, 180, 150),
            (16, 60, 12, 15),
            math.pi / 2,
            math.pi,
            1,
        )

        # Tank top logo
        font = pygame.font.Font(None, 16)
        logo_text = font.render("FIGHT", True, DARK_GRAY)
        surface.blit(logo_text, (30, 65))

        # Wrist wraps
        pygame.draw.rect(surface, WHITE, (55, 78, 8, 4))
        pygame.draw.rect(surface, WHITE, (17, 78, 8, 4))
        pygame.draw.rect(surface, GRAY, (55, 78, 8, 4), 1)
        pygame.draw.rect(surface, GRAY, (17, 78, 8, 4), 1)

    def _create_player_sprites(self) -> None:
        """Create procedural player sprites."""
        colors = self._get_character_colors()

        # Extract color values from dictionary
        skin_color = colors["skin"]
        hair_color = colors["hair"]
        tank_color = colors["tank"]
        glove_color = colors["glove"]
        shorts_color = colors["shorts"]

        # Create idle sprite
        idle_surface = pygame.Surface((80, 120), pygame.SRCALPHA)
        self._draw_base_character(idle_surface, colors)

        # Add shorts stripe details (unique to idle sprite)
        pygame.draw.line(idle_surface, WHITE, (30, 92), (50, 92), 2)
        pygame.draw.line(idle_surface, WHITE, (30, 98), (50, 98), 2)

        self.sprites["player_idle"] = idle_surface

        # Punching sprites for different punch types
        for punch_type in [
            "jab",
            "cross",
            "hook",
            "uppercut",
            "front_kick",
            "roundhouse_kick",
            "low_kick",
        ]:
            punch_surface = pygame.Surface((120, 120), pygame.SRCALPHA)

            # Copy base body from idle sprite
            base_body = idle_surface.copy()
            punch_surface.blit(base_body, (20, 0))

            # Define extended arm positions and body dynamics
            if punch_type == "jab":
                # Quick straight punch - left hand extends
                # Redraw left arm in extended position
                pygame.draw.ellipse(
                    punch_surface, skin_color, (40, 75, 20, 8)
                )  # Upper arm
                pygame.draw.ellipse(
                    punch_surface, skin_color, (55, 70, 25, 8)
                )  # Forearm
                pygame.draw.circle(punch_surface, glove_color, (82, 74), 9)
                pygame.draw.circle(punch_surface, DARK_RED, (82, 74), 9, 2)
                # Add motion lines
                for i in range(3):
                    pygame.draw.line(
                        punch_surface,
                        (255, 255, 255, 100),
                        (75 - i * 5, 74),
                        (80 - i * 5, 74),
                        2,
                    )

            elif punch_type == "cross":
                # Power straight punch - right hand extends with body rotation
                # Slight body lean forward
                pygame.draw.ellipse(
                    punch_surface, skin_color, (15, 75, 20, 8)
                )  # Upper arm
                pygame.draw.ellipse(
                    punch_surface, skin_color, (5, 70, 25, 8)
                )  # Forearm
                pygame.draw.circle(punch_surface, glove_color, (2, 74), 9)
                pygame.draw.circle(punch_surface, DARK_RED, (2, 74), 9, 2)
                # Add impact burst effect
                for i in range(4):
                    angle = i * 90
                    end_x = 2 + math.cos(math.radians(angle)) * 15
                    end_y = 74 + math.sin(math.radians(angle)) * 15
                    pygame.draw.line(
                        punch_surface, YELLOW, (2, 74), (end_x, end_y), 3
                    )

            elif punch_type == "hook":
                # Wide circular punch - right hand swings around
                pygame.draw.ellipse(
                    punch_surface, skin_color, (25, 65, 8, 20)
                )  # Upper arm
                pygame.draw.ellipse(
                    punch_surface, skin_color, (15, 58, 20, 8)
                )  # Forearm
                pygame.draw.circle(punch_surface, glove_color, (12, 62), 9)
                pygame.draw.circle(punch_surface, DARK_RED, (12, 62), 9, 2)
                # Add arc motion trail
                pygame.draw.arc(
                    punch_surface,
                    (255, 255, 0, 150),
                    (10, 55, 30, 20),
                    0,
                    math.pi / 2,
                    3,
                )

            elif punch_type == "uppercut":
                # Upward punch from below - right hand comes up
                pygame.draw.ellipse(
                    punch_surface, skin_color, (30, 85, 8, 20)
                )  # Upper arm
                pygame.draw.ellipse(
                    punch_surface, skin_color, (35, 65, 8, 25)
                )  # Forearm
                pygame.draw.circle(punch_surface, glove_color, (39, 55), 9)
                pygame.draw.circle(punch_surface, DARK_RED, (39, 55), 9, 2)
                # Add upward motion lines
                for i in range(4):
                    pygame.draw.line(
                        punch_surface,
                        (255, 255, 255, 120),
                        (39, 60 + i * 5),
                        (39, 65 + i * 5),
                        2,
                    )

            elif punch_type == "front_kick":
                # Front kick - right leg extends forward
                # Redraw right leg in extended position
                pygame.draw.ellipse(
                    punch_surface, skin_color, (50, 105, 25, 8)
                )  # Thigh
                pygame.draw.ellipse(
                    punch_surface, skin_color, (70, 100, 20, 8)
                )  # Shin
                pygame.draw.ellipse(
                    punch_surface, BLACK, (85, 98, 18, 10)
                )  # Foot
                pygame.draw.ellipse(
                    punch_surface, WHITE, (87, 99, 14, 6)
                )  # Shoe detail
                # Add impact burst at foot
                for i in range(4):
                    angle = i * 90
                    end_x = 94 + math.cos(math.radians(angle)) * 12
                    end_y = 103 + math.sin(math.radians(angle)) * 12
                    pygame.draw.line(
                        punch_surface, YELLOW, (94, 103), (end_x, end_y), 2
                    )

            elif punch_type == "roundhouse_kick":
                # Roundhouse kick - right leg swings in an arc
                # Thigh
                pygame.draw.ellipse(punch_surface, skin_color, (35, 95, 8, 25))
                # Shin
                pygame.draw.ellipse(punch_surface, skin_color, (15, 85, 25, 8))
                # Foot
                pygame.draw.ellipse(punch_surface, BLACK, (10, 83, 18, 10))
                pygame.draw.ellipse(
                    punch_surface, WHITE, (12, 84, 14, 6)
                )  # Shoe detail
                # Add arc motion trail
                pygame.draw.arc(
                    punch_surface,
                    (255, 255, 0, 150),
                    (10, 80, 40, 30),
                    0,
                    math.pi / 3,
                    3,
                )

            elif punch_type == "low_kick":
                # Low kick - targeting lower area
                pygame.draw.ellipse(
                    punch_surface, skin_color, (35, 110, 8, 20)
                )  # Thigh
                # Shin
                pygame.draw.ellipse(
                    punch_surface, skin_color, (20, 118, 20, 8)
                )
                # Foot
                pygame.draw.ellipse(punch_surface, BLACK, (15, 116, 18, 10))
                pygame.draw.ellipse(
                    punch_surface, WHITE, (17, 117, 14, 6)
                )  # Shoe detail
                # Add sweeping motion lines
                for i in range(3):
                    pygame.draw.line(
                        punch_surface,
                        (255, 255, 255, 100),
                        (20 - i * 3, 122),
                        (25 - i * 3, 122),
                        2,
                    )

            self.sprites[f"player_{punch_type}"] = punch_surface

    def _create_bag_textures(self) -> None:
        """Create enhanced heavy bag textures."""
        bag_surface = pygame.Surface((80, 180), pygame.SRCALPHA)

        # Main bag body with gradient effect
        for y in range(180):
            intensity = int(139 + (y / 180) * 30)
            color = (
                intensity,
                max(0, 69 - (y / 180) * 20),
                max(0, 19 - (y / 180) * 10),
            )
            pygame.draw.line(bag_surface, color, (10, y), (70, y))

        # Add leather texture lines
        for i in range(0, 180, 20):
            pygame.draw.line(bag_surface, DARK_BROWN, (15, i), (65, i), 2)

        # Stitching details
        for i in range(3):
            y_offset = 45 + i * 45
            pygame.draw.arc(
                bag_surface, BLACK, (15, y_offset, 50, 20), 0, math.pi, 3
            )

        # Brand emblem
        font = pygame.font.Font(None, 24)
        text = font.render("HEAVY", True, GOLD)
        bag_surface.blit(text, (20, 85))

        # Highlight effects
        highlight = pygame.Surface((30, 60), pygame.SRCALPHA)
        pygame.draw.ellipse(highlight, (255, 255, 255, 60), (0, 0, 30, 60))
        bag_surface.blit(highlight, (20, 30))

        self.sprites["heavy_bag"] = bag_surface

        # Damaged bag variant
        damaged_bag = bag_surface.copy()
        # Add damage marks
        for _ in range(5):
            x = random.randint(15, 65)
            y = random.randint(20, 160)
            radius = random.randint(3, 8)
            pygame.draw.circle(damaged_bag, DARK_RED, (x, y), radius)

        self.sprites["heavy_bag_damaged"] = damaged_bag

    def _create_particle_textures(self) -> None:
        """Create enhanced particle textures."""
        # Spark particle
        spark = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(spark, YELLOW, (4, 4), 4)
        pygame.draw.circle(spark, WHITE, (4, 4), 2)
        self.particles["spark"] = spark

        # Dust particle
        dust = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(dust, (200, 200, 200, 128), (3, 3), 3)
        self.particles["dust"] = dust

        # Sweat drop
        sweat = pygame.Surface((4, 6), pygame.SRCALPHA)
        pygame.draw.ellipse(sweat, (100, 150, 255), (0, 0, 4, 6))
        pygame.draw.ellipse(sweat, (150, 200, 255), (1, 1, 2, 4))
        self.particles["sweat"] = sweat

        # Energy burst
        energy = pygame.Surface((12, 12), pygame.SRCALPHA)
        for i in range(3):
            color = (255, 255 - i * 50, 100 - i * 30, 200 - i * 60)
            pygame.draw.circle(energy, color[:3], (6, 6), 6 - i * 2)
        self.particles["energy"] = energy

    def _create_powerup_sprites(self) -> None:
        """Create enhanced power-up sprites."""

        # Base power-up glow effect
        def create_powerup(
            color: Tuple[int, int, int], icon_text: str
        ) -> pygame.Surface:
            surface = pygame.Surface((40, 40), pygame.SRCALPHA)

            # Outer glow
            for i in range(3):
                pygame.draw.circle(surface, color, (20, 20), 20 - i * 2)

            # Main circle
            pygame.draw.circle(surface, color, (20, 20), 15)
            pygame.draw.circle(surface, WHITE, (20, 20), 15, 3)

            # Inner highlight
            pygame.draw.circle(surface, (255, 255, 255, 100), (17, 17), 8)

            # Icon
            font = pygame.font.Font(None, 24)
            text = font.render(icon_text, True, WHITE)
            text_rect = text.get_rect(center=(20, 20))
            surface.blit(text, text_rect)

            return surface

        self.sprites["powerup_stamina"] = create_powerup(GREEN, "S")
        self.sprites["powerup_power"] = create_powerup(BLUE, "P")
        self.sprites["powerup_multiplier"] = create_powerup(GOLD, "2X")
        self.sprites["powerup_rage"] = create_powerup(RED, "R")

    def _create_backgrounds(self) -> None:
        """Create the gym backdrop per the design handoff (README §Assets)."""
        from src.utils import theme
        from src.game import ui

        s = theme.s
        gym_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        ui.draw_vertical_gradient(
            gym_bg,
            gym_bg.get_rect(),
            theme.SCENE_BG_TOP,
            theme.SCENE_BG_BOTTOM,
        )

        floor_y = SCREEN_HEIGHT - s(60)

        # Mirror strips along the back wall
        mirror_top, mirror_h = s(150), s(430)
        for x in range(s(60), SCREEN_WIDTH, s(290)):
            pygame.draw.rect(gym_bg, (46, 48, 58), (x, mirror_top, s(14), mirror_h))
            pygame.draw.rect(
                gym_bg, (66, 69, 82), (x + s(3), mirror_top, s(3), mirror_h)
            )

        # Weight-rack silhouette (left, on the floor)
        rack_w, rack_h = s(190), s(230)
        rack = pygame.Rect(s(70), floor_y - rack_h, rack_w, rack_h)
        pygame.draw.rect(gym_bg, (18, 19, 24), rack)
        for i in range(5):
            pygame.draw.circle(
                gym_bg,
                (28, 29, 35),
                (rack.left + s(28) + i * s(34), rack.top + s(34)),
                s(14),
            )
        pygame.draw.rect(
            gym_bg, (28, 29, 35), (rack.left, rack.top + s(70), rack_w, s(8))
        )

        # Ceiling lights: fixture + soft glow pool
        glow = ui.make_radial_glow(s(220), (255, 244, 200), 26)
        for cx in (SCREEN_WIDTH // 4, SCREEN_WIDTH // 2, SCREEN_WIDTH * 3 // 4):
            gym_bg.blit(glow, (cx - glow.get_width() // 2, -glow.get_height() // 3))
            fixture = pygame.Rect(0, s(18), s(150), s(14))
            fixture.centerx = cx
            pygame.draw.rect(gym_bg, (10, 10, 13), fixture.inflate(s(8), s(6)))
            pygame.draw.rect(gym_bg, (235, 226, 180), fixture)

        # Floor band with mat grid
        pygame.draw.rect(
            gym_bg, theme.FLOOR, (0, floor_y, SCREEN_WIDTH, SCREEN_HEIGHT - floor_y)
        )
        pygame.draw.line(gym_bg, (44, 46, 54), (0, floor_y), (SCREEN_WIDTH, floor_y), 2)
        for x in range(0, SCREEN_WIDTH + 1, s(96)):
            pygame.draw.line(
                gym_bg, (32, 33, 40), (x, floor_y + 2), (x, SCREEN_HEIGHT), 1
            )

        self.backgrounds["gym"] = gym_bg

    def get_sprite(self, sprite_name: str) -> Optional[pygame.Surface]:
        """Get a sprite by name."""
        self._ensure_initialized()
        return self.sprites.get(sprite_name)

    def get_background(self, bg_name: str) -> Optional[pygame.Surface]:
        """Get a background by name."""
        self._ensure_initialized()
        return self.backgrounds.get(bg_name)

    def get_particle_texture(
        self, texture_name: str
    ) -> Optional[pygame.Surface]:
        """Get a particle texture by name."""
        self._ensure_initialized()
        return self.particles.get(texture_name)

    def create_hit_burst_effect(
        self, x: float, y: float, power: float, color: Tuple[int, int, int]
    ) -> pygame.Surface:
        """Create a dynamic hit burst effect."""
        size = int(40 + power * 10)
        surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)

        # Multiple rings for burst effect
        for i in range(5):
            radius = size - i * (size // 6)
            if radius > 0:
                pygame.draw.circle(
                    surface, color, (size, size), radius, max(1, 3 - i)
                )

        # Add radiating lines
        for angle in range(0, 360, 30):
            end_x = size + math.cos(math.radians(angle)) * size * 0.8
            end_y = size + math.sin(math.radians(angle)) * size * 0.8
            pygame.draw.line(surface, color, (size, size), (end_x, end_y), 2)

        return surface

    def create_combo_effect(self, combo_count: int) -> pygame.Surface:
        """Create special effects for combo achievements."""
        size = 60 + combo_count * 10
        surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)

        # Color based on combo level
        if combo_count >= 10:
            colors = [GOLD, YELLOW, WHITE]
        elif combo_count >= 5:
            colors = [YELLOW, ORANGE, RED]
        else:
            colors = [WHITE, LIGHT_GRAY, GRAY]

        # Pulsing rings
        for i, color in enumerate(colors):
            radius = size - i * 15
            if radius > 0:
                pygame.draw.circle(surface, color, (size, size), radius, 4)

        # Add star burst for high combos
        if combo_count >= 5:
            for angle in range(0, 360, 45):
                start_radius = size * 0.6
                end_radius = size * 0.9
                start_x = size + math.cos(math.radians(angle)) * start_radius
                start_y = size + math.sin(math.radians(angle)) * start_radius
                end_x = size + math.cos(math.radians(angle)) * end_radius
                end_y = size + math.sin(math.radians(angle)) * end_radius
                pygame.draw.line(
                    surface, colors[0], (start_x, start_y), (end_x, end_y), 3
                )

        return surface


# Global graphics manager instance
graphics_manager = GraphicsManager()
