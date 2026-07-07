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
        """Cel Classic palette (design handoff §Character)."""
        from ..utils import theme

        return {
            "skin": theme.CEL_SKIN,
            "hair": theme.CEL_HAIR,
            "tank": theme.CEL_TANK,
            "tank_trim": theme.CEL_TANK_TRIM,
            "shorts": theme.CEL_SHORTS,
            "waistband": theme.CEL_WAISTBAND,
            "glove": theme.CEL_GLOVE,
            "glove_band": theme.CEL_GLOVE_BAND,
            "shoe": theme.CEL_SHOE,
            "sole": theme.CEL_SOLE,
            "outline": theme.CEL_OUTLINE,
        }

    # ------------------------------------------------------------------
    # "Cel Classic" character (design handoff §Character).
    #
    # All coordinates are transcribed 1:1 from the SVG pose groups in
    # design_handoff_heavy_bag_ui/UI Redesign.dc.html (#celPoseIdle ..
    # #celPoseLowKick) on the 80-unit sprite grid, feet baseline y≈110.
    # Shapes are drawn supersampled (CEL_SS×) then smoothscaled down.
    # ------------------------------------------------------------------

    CEL_SS = 3  # supersample factor

    def _cel_capsule(self, surf, k, a, b, width, color):
        """SVG thick round-cap stroke -> line + endpoint circles."""
        r = max(1, round(width * k / 2))
        ax, ay, bx, by = (
            round(a[0] * k),
            round(a[1] * k),
            round(b[0] * k),
            round(b[1] * k),
        )
        pygame.draw.line(surf, color, (ax, ay), (bx, by), r * 2)
        pygame.draw.circle(surf, color, (ax, ay), r)
        pygame.draw.circle(surf, color, (bx, by), r)

    def _cel_polyline(self, surf, k, pts, width, color):
        r = max(1, round(width * k / 2))
        scaled = [(round(x * k), round(y * k)) for x, y in pts]
        for a, b in zip(scaled, scaled[1:]):
            pygame.draw.line(surf, color, a, b, r * 2)
        for p in scaled:
            pygame.draw.circle(surf, color, p, r)

    def _cel_circle(self, surf, k, c, radius, fill, outline=None, ow=1.5):
        center = (round(c[0] * k), round(c[1] * k))
        pygame.draw.circle(surf, fill, center, round(radius * k))
        if outline:
            pygame.draw.circle(
                surf, outline, center, round(radius * k), max(1, round(ow * k))
            )

    def _cel_rect(self, surf, k, rect, fill, outline=None, ow=1.0, radius=0):
        r = pygame.Rect(
            round(rect[0] * k),
            round(rect[1] * k),
            round(rect[2] * k),
            round(rect[3] * k),
        )
        br = round(radius * k)
        pygame.draw.rect(surf, fill, r, border_radius=br)
        if outline:
            pygame.draw.rect(surf, outline, r, max(1, round(ow * k)), border_radius=br)

    def _cel_polygon(self, surf, k, pts, fill, outline=None, ow=1.5):
        scaled = [(round(x * k), round(y * k)) for x, y in pts]
        pygame.draw.polygon(surf, fill, scaled)
        if outline:
            w = max(1, round(ow * k))
            pygame.draw.lines(surf, outline, True, scaled, w)
            for p in scaled:
                pygame.draw.circle(surf, outline, p, w // 2)

    @staticmethod
    def _qbezier(p0, p1, p2, n=12):
        """Sample a quadratic bezier into a point list."""
        pts = []
        for i in range(n + 1):
            t = i / n
            u = 1 - t
            pts.append(
                (
                    u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
                    u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1],
                )
            )
        return pts

    def _cel_shadow(self, surf, k, cx, rx):
        shadow = pygame.Surface((round(rx * 2 * k), round(7 * k)), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 102), shadow.get_rect())
        surf.blit(shadow, (round((cx - rx) * k), round((111 - 3.5) * k)))

    def _cel_glove(self, surf, k, cx, cy, c):
        self._cel_circle(surf, k, (cx, cy), 8.5, c["glove"], c["outline"], 1.8)
        self._cel_circle(surf, k, (cx + 5, cy + 5.5), 3, c["glove"], c["outline"], 1.4)
        band = self._qbezier((cx - 7, cy + 3), (cx, cy + 6.5), (cx + 7, cy + 3))
        self._cel_polyline(surf, k, band, 2, c["glove_band"])

    def _cel_head(self, surf, k, c):
        self._cel_rect(surf, k, (36, 29, 8, 7), c["skin"], c["outline"], 1.2)
        self._cel_circle(surf, k, (27.5, 21), 2.2, c["skin"], c["outline"], 1.2)
        self._cel_circle(surf, k, (52.5, 21), 2.2, c["skin"], c["outline"], 1.2)
        self._cel_circle(surf, k, (40, 20), 12, c["skin"], c["outline"], 1.8)
        # Hair: elliptical arc (29,14) -> (51,14), rx 12.5 ry 10, bulging up
        hair = []
        theta0 = math.acos(11 / 12.5)
        for i in range(13):
            t = theta0 + (math.pi - 2 * theta0) * i / 12
            hair.append((40 + 12.5 * math.cos(t), 18.75 - 10 * math.sin(t)))
        self._cel_polyline(surf, k, hair, 7, c["hair"])
        # Brows, eyes, mouth
        self._cel_capsule(surf, k, (33, 16.5), (38, 18), 1.5, c["outline"])
        self._cel_capsule(surf, k, (47, 16.5), (42, 18), 1.5, c["outline"])
        self._cel_circle(surf, k, (36, 20.5), 1.3, c["outline"])
        self._cel_circle(surf, k, (44, 20.5), 1.3, c["outline"])
        self._cel_capsule(surf, k, (37, 25.5), (43, 25.5), 1.5, c["outline"])

    def _cel_torso(self, surf, k, c):
        self._cel_circle(surf, k, (28, 40), 5, c["skin"], c["outline"], 1.5)
        self._cel_circle(surf, k, (52, 40), 5, c["skin"], c["outline"], 1.5)
        tank = [(27, 37), (53, 37), (56, 62)]
        tank += self._qbezier((56, 62), (40, 66), (24, 62))[1:]
        self._cel_polygon(surf, k, tank, c["tank"], c["outline"], 1.5)
        hem = self._qbezier((25, 60.5), (40, 64), (55, 60.5))
        self._cel_polyline(surf, k, hem, 1.5, c["tank_trim"])

    def _cel_shorts(self, surf, k, c):
        pts = [(26, 62), (54, 62), (55, 78), (43, 78), (40, 72), (37, 78), (25, 78)]
        self._cel_polygon(surf, k, pts, c["shorts"], c["outline"], 1.5)
        self._cel_rect(surf, k, (26, 60, 28, 3.5), c["waistband"], c["outline"], 1.0)
        self._cel_capsule(surf, k, (28, 65), (27, 76), 2, c["tank"])
        self._cel_capsule(surf, k, (52, 65), (53, 76), 2, c["tank"])

    def _cel_leg(self, surf, k, c, side):
        if side == "L":
            self._cel_capsule(surf, k, (33, 76), (32, 100), 7, c["skin"])
            self._cel_rect(
                surf, k, (24, 98, 15, 9), c["shoe"], c["outline"], 1.5, radius=3
            )
            self._cel_rect(
                surf, k, (23, 105.5, 17, 3.5), c["sole"], c["outline"], 1.0, radius=1.5
            )
        else:
            self._cel_capsule(surf, k, (47, 76), (48, 100), 7, c["skin"])
            self._cel_rect(
                surf, k, (41, 98, 15, 9), c["shoe"], c["outline"], 1.5, radius=3
            )
            self._cel_rect(
                surf, k, (40, 105.5, 17, 3.5), c["sole"], c["outline"], 1.0, radius=1.5
            )

    def _cel_guard_arm(self, surf, k, c, side):
        if side == "L":
            self._cel_capsule(surf, k, (28, 41), (20, 53), 7, c["skin"])
            self._cel_capsule(surf, k, (20, 53), (24, 38), 6, c["skin"])
            self._cel_glove(surf, k, 25, 33, c)
        else:
            self._cel_capsule(surf, k, (52, 41), (60, 53), 7, c["skin"])
            self._cel_capsule(surf, k, (60, 53), (56, 38), 6, c["skin"])
            self._cel_glove(surf, k, 55, 33, c)

    def _cel_kick_foot(self, surf, k, c, tx, ty, angle):
        """Rotated shoe+sole group used by the three kick poses."""
        pad = 14  # local units around the origin
        foot = pygame.Surface((round(pad * 2 * k), round(pad * 2 * k)), pygame.SRCALPHA)
        self._cel_rect(
            foot, k, (pad - 8, pad - 4.5, 15, 9), c["shoe"], c["outline"], 1.5, radius=3
        )
        self._cel_rect(
            foot,
            k,
            (pad + 6, pad - 5.5, 3.5, 11),
            c["sole"],
            c["outline"],
            1.0,
            radius=1.5,
        )
        rotated = pygame.transform.rotate(foot, -angle)
        surf.blit(rotated, rotated.get_rect(center=(round(tx * k), round(ty * k))))

    def _cel_body(
        self, surf, k, c, guards=("L", "R"), legs=("L", "R"), shadow_cx=42, shadow_rx=22
    ):
        """Shared paint order: shadow, legs, shorts, torso, head, guards."""
        self._cel_shadow(surf, k, shadow_cx, shadow_rx)
        for leg in legs:
            self._cel_leg(surf, k, c, leg)
        self._cel_shorts(surf, k, c)
        self._cel_torso(surf, k, c)
        self._cel_head(surf, k, c)
        for guard in guards:
            self._cel_guard_arm(surf, k, c, guard)

    WHITE_ACCENT = (255, 255, 255, 140)
    YELLOW_ACCENT = (245, 217, 10, 255)
    GOLD_TRAIL = (240, 195, 48, 217)

    def _cel_render(self, size, draw_fn):
        """Render a pose supersampled, then smoothscale to target size."""
        k = self.CEL_SS
        surf = pygame.Surface((size[0] * k, size[1] * k), pygame.SRCALPHA)
        draw_fn(surf, k)
        return pygame.transform.smoothscale(surf, size)

    def _create_player_sprites(self) -> None:
        """Create the Cel Classic sprite set (idle + 7 attacks).

        Idle stays 80x120. Attack poses extend to grid x≈109, so they
        render on 140x120 with the body shifted +30 to keep it aligned
        with idle under Player.draw's centered blit.
        """
        c = self._get_character_colors()

        def idle(surf, k):
            self._cel_body(surf, k, c)

        self.sprites["player_idle"] = self._cel_render((80, 120), idle)

        dx = 30  # attack-surface body offset (140/2 - grid body center 40)

        def attack(draw_fn):
            def wrapped(surf, k):
                shifted = pygame.Surface(
                    (surf.get_width(), surf.get_height()), pygame.SRCALPHA
                )
                draw_fn(shifted, k)
                surf.blit(shifted, (dx * k, 0))

            return self._cel_render((140, 120), wrapped)

        def jab(surf, k):
            self._cel_body(surf, k, c, guards=("L",))
            self._cel_capsule(surf, k, (52, 41), (78, 38), 6.5, c["skin"])
            self._cel_glove(surf, k, 84.5, 37.5, c)
            for a, b in (
                ((62, 31.5), (70, 31)),
                ((60, 38), (70, 38)),
                ((62, 44.5), (70, 44)),
            ):
                self._cel_capsule(surf, k, a, b, 2, self.WHITE_ACCENT)

        def cross(surf, k):
            self._cel_body(surf, k, c, guards=("R",))
            self._cel_capsule(surf, k, (28, 41), (80, 38), 6.5, c["skin"])
            self._cel_glove(surf, k, 86.5, 37.5, c)
            for a, b in (
                ((96, 31), (102, 26)),
                ((98, 37.5), (106, 37.5)),
                ((96, 44), (102, 49)),
                ((90, 28), (93, 21)),
            ):
                self._cel_capsule(surf, k, a, b, 2.5, self.YELLOW_ACCENT)

        def hook(surf, k):
            self._cel_body(surf, k, c, guards=("L",))
            self._cel_capsule(surf, k, (52, 41), (69, 47), 7, c["skin"])
            self._cel_capsule(surf, k, (69, 47), (77, 31), 6, c["skin"])
            self._cel_glove(surf, k, 79, 26, c)
            trail = self._qbezier((55, 14), (77, 13), (82, 25))
            self._cel_polyline(surf, k, trail, 2.5, self.GOLD_TRAIL)

        def uppercut(surf, k):
            self._cel_body(surf, k, c, guards=("L",))
            self._cel_capsule(surf, k, (52, 41), (61, 55), 7, c["skin"])
            self._cel_capsule(surf, k, (61, 55), (59.5, 29), 6, c["skin"])
            self._cel_glove(surf, k, 59, 21, c)
            for a, b in (
                ((50, 36), (50, 42)),
                ((68, 33), (68, 40)),
                ((59, 44), (59, 51)),
            ):
                self._cel_capsule(surf, k, a, b, 2, self.WHITE_ACCENT)

        def front_kick(surf, k):
            self._cel_shadow(surf, k, 48, 26)
            self._cel_leg(surf, k, c, "L")
            self._cel_capsule(surf, k, (46, 77), (64, 71), 7, c["skin"])
            self._cel_capsule(surf, k, (64, 71), (82, 66.5), 6, c["skin"])
            self._cel_kick_foot(surf, k, c, 87, 66, 8)
            self._cel_shorts(surf, k, c)
            self._cel_torso(surf, k, c)
            self._cel_head(surf, k, c)
            self._cel_guard_arm(surf, k, c, "L")
            self._cel_guard_arm(surf, k, c, "R")
            for a, b in (
                ((100, 58), (104, 53)),
                ((102, 65), (109, 65)),
                ((100, 72), (104, 77)),
            ):
                self._cel_capsule(surf, k, a, b, 2.5, self.YELLOW_ACCENT)

        def roundhouse_kick(surf, k):
            self._cel_shadow(surf, k, 46, 24)
            self._cel_leg(surf, k, c, "L")
            self._cel_capsule(surf, k, (46, 77), (63, 61), 7, c["skin"])
            self._cel_capsule(surf, k, (63, 61), (79, 50), 6, c["skin"])
            self._cel_kick_foot(surf, k, c, 84, 46.5, -30)
            trail = self._qbezier((60, 88), (92, 79), (84, 51))
            self._cel_polyline(surf, k, trail, 2.5, self.GOLD_TRAIL)
            self._cel_shorts(surf, k, c)
            self._cel_torso(surf, k, c)
            self._cel_head(surf, k, c)
            self._cel_guard_arm(surf, k, c, "L")
            self._cel_guard_arm(surf, k, c, "R")

        def low_kick(surf, k):
            self._cel_shadow(surf, k, 48, 26)
            self._cel_leg(surf, k, c, "L")
            self._cel_capsule(surf, k, (46, 77), (64, 86), 7, c["skin"])
            self._cel_capsule(surf, k, (64, 86), (82, 92), 6, c["skin"])
            self._cel_kick_foot(surf, k, c, 87, 92.5, 10)
            for a, b in (((62, 101), (70, 101)), ((66, 106), (74, 106))):
                self._cel_capsule(surf, k, a, b, 2, self.WHITE_ACCENT)
            self._cel_shorts(surf, k, c)
            self._cel_torso(surf, k, c)
            self._cel_head(surf, k, c)
            self._cel_guard_arm(surf, k, c, "L")
            self._cel_guard_arm(surf, k, c, "R")

        poses = {
            "jab": jab,
            "cross": cross,
            "hook": hook,
            "uppercut": uppercut,
            "front_kick": front_kick,
            "roundhouse_kick": roundhouse_kick,
            "low_kick": low_kick,
        }
        for name, fn in poses.items():
            self.sprites[f"player_{name}"] = attack(fn)

    def _create_bag_textures(self) -> None:
        """Leather heavy bag per the design handoff (§Assets)."""
        from ..utils import theme
        from ..utils.fonts import get_font
        from . import ui

        bag_surface = pygame.Surface((80, 180), pygame.SRCALPHA)

        # Rounded-rect leather body with vertical gradient
        body = pygame.Rect(8, 0, 64, 180)
        gradient = pygame.Surface(body.size)
        ui.draw_vertical_gradient(
            gradient, gradient.get_rect(), theme.BAG_LEATHER_TOP, theme.BAG_LEATHER_BOTTOM
        )
        mask = pygame.Surface(body.size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=18)
        gradient = gradient.convert_alpha()
        gradient.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        bag_surface.blit(gradient, body.topleft)

        # Vertical seam lines
        for x in (24, 40, 56):
            pygame.draw.line(bag_surface, (30, 13, 6), (x, 8), (x, 172), 1)
        # Top and bottom stitch bands
        pygame.draw.line(bag_surface, (30, 13, 6), (10, 14), (70, 14), 2)
        pygame.draw.line(bag_surface, (30, 13, 6), (10, 166), (70, 166), 2)

        # Left highlight
        highlight = pygame.Surface((14, 130), pygame.SRCALPHA)
        pygame.draw.ellipse(highlight, (255, 255, 255, 28), highlight.get_rect())
        bag_surface.blit(highlight, (12, 20))

        # Gold "HEAVY" branding
        brand = get_font("bebas", 34).render("HEAVY", True, theme.GOLD)
        bag_surface.blit(brand, brand.get_rect(center=(40, 90)))

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

    def get_particle_texture(self, texture_name: str) -> Optional[pygame.Surface]:
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
                pygame.draw.circle(surface, color, (size, size), radius, max(1, 3 - i))

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
