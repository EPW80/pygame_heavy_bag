"""
Main game manager for the Heavy Bag Training game.
"""

import asyncio

import pygame
import math
import random
from typing import List
from ..utils.constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    BLACK,
    WHITE,
    RED,
    GREEN,
    BLUE,
    YELLOW,
    ORANGE,
    GOLD,
    LIGHT_GRAY,
    DARK_GRAY,
    GRAY,
    ROUND_TIME_FRAMES,
    GameState,
    GameSettings,
    PunchType,
    ATTACK_PROPERTIES,
)
from ..utils import theme
from ..utils.constants import BAG_MAX_DAMAGE, ROUND_TIME_SECONDS
from ..utils.fonts import get_font
from ..utils.save_manager import SaveManager
from ..utils.logger import get_logger, SaveError, LoadError, CorruptedDataError
from . import ui

logger = get_logger()
from .player import Player
from .heavy_bag import HeavyBag
from .menu import Menu
from .settings_screen import SettingsScreen
from .tutorial_screen import TutorialScreen
from .effects import (
    FloatingText,
    HitEffect,
    ImpactRing,
    PowerUp,
    ComboEffect,
    particle_pool,
)
from .graphics import graphics_manager


class GameManager:
    """Main game loop and state management."""

    def __init__(self):
        # Initialize Pygame (pygame.init() covers the mixer where available;
        # an explicit mixer.init() can hang on audio-less hosts and on web)
        pygame.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Heavy Bag Training - Pro Edition")
        self.clock = pygame.time.Clock()
        self.running = True

        # Load save data
        try:
            (
                self.high_score,
                self.total_punches_all_time,
                self.best_combo_all_time,
                self.settings,
            ) = SaveManager.load_data()
            logger.info("Game initialized successfully")
        except CorruptedDataError as e:
            logger.warning(f"Save file corrupted, using defaults: {e}")
            # Use defaults but notify user
            self.high_score = 0
            self.total_punches_all_time = 0
            self.best_combo_all_time = 0
            self.settings = GameSettings()
        except LoadError as e:
            logger.warning(f"Could not load save data, using defaults: {e}")
            # Use defaults
            self.high_score = 0
            self.total_punches_all_time = 0
            self.best_combo_all_time = 0
            self.settings = GameSettings()

        # Game state
        self.state = GameState.MENU
        self.menu = Menu()
        self.menu.set_stats(
            self.high_score,
            self.total_punches_all_time,
            self.best_combo_all_time,
        )
        self.settings_screen = SettingsScreen(self.settings)
        self.tutorial_screen = TutorialScreen()

        # Game objects (initialized when game starts)
        self.heavy_bag = None
        self.player = None

        # Fonts - smaller for better layout
        self.font_small = pygame.font.Font(None, 16)
        self.font_medium = pygame.font.Font(None, 22)
        self.font_large = pygame.font.Font(None, 48)

        # Effects (using particle pool for performance)
        self.hit_effects: List[HitEffect] = []
        self.floating_texts: List[FloatingText] = []
        self.power_ups: List[PowerUp] = []
        self.combo_effects: List[ComboEffect] = []
        self.screen_shake = 0.0
        self._range_glow = None  # cached gradient for the in-range strip

        # Combo counter animation state (pop on hit, fade after lapse)
        self._last_combo = 0
        self._combo_pop = 0
        self._combo_fade = 0
        self._combo_display = 0

        # Game timer
        self.game_timer = 0
        self.round_time = ROUND_TIME_FRAMES

    def start_game(self) -> None:
        """Initialize a new game session."""
        # Spawn right of the HUD control card so the character is visible
        self.player = Player(
            SCREEN_WIDTH * 2 // 5, SCREEN_HEIGHT - 150, self.settings.difficulty
        )
        self.heavy_bag = HeavyBag(SCREEN_WIDTH * 3 // 4, 100, self.settings.difficulty)
        self.hit_effects.clear()
        self.floating_texts.clear()
        self.power_ups.clear()
        self.combo_effects.clear()
        particle_pool.clear()  # Clear particle pool instead of list
        self.game_timer = 0
        self.screen_shake = 0
        self.state = GameState.PLAYING

    def handle_events(self) -> None:
        """Handle all input events."""
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Menu handling
            if self.state == GameState.MENU:
                action = self.menu.handle_input(event)
                if action == "Start Game":
                    self.start_game()
                elif action == "Tutorial":
                    self.state = GameState.TUTORIAL
                elif action == "Settings":
                    self.state = GameState.SETTINGS
                elif action == "Quit":
                    self.running = False

            # Settings screen handling
            elif self.state == GameState.SETTINGS:
                if self.settings_screen.handle_input(event) == "back":
                    self.state = GameState.MENU
                    self._save_settings()

            # Tutorial screen handling
            elif self.state == GameState.TUTORIAL:
                if self.tutorial_screen.handle_input(event) == "back":
                    self.state = GameState.MENU

            # Game handling
            elif self.state == GameState.PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.PAUSED
                    elif event.key == pygame.K_z:
                        self.punch(PunchType.JAB)
                    elif event.key == pygame.K_x:
                        self.punch(PunchType.CROSS)
                    elif event.key == pygame.K_c:
                        self.punch(PunchType.HOOK)
                    elif event.key == pygame.K_v:
                        self.punch(PunchType.UPPERCUT)
                    elif event.key == pygame.K_q:
                        self.punch(PunchType.FRONT_KICK)
                    elif event.key == pygame.K_w:
                        self.punch(PunchType.ROUNDHOUSE_KICK)
                    elif event.key == pygame.K_e:
                        self.punch(PunchType.LOW_KICK)
                    elif event.key == pygame.K_SPACE:
                        self.special_attack()

            # Pause handling
            elif self.state == GameState.PAUSED:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_q:
                        self.state = GameState.MENU

            # Game over handling
            elif self.state == GameState.GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.state = GameState.MENU
                    elif event.key == pygame.K_r:
                        self.start_game()

        # Movement (only when playing)
        if self.state == GameState.PLAYING:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player.x -= self.player.move_speed
                self.player.x = max(50, self.player.x)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player.x += self.player.move_speed
                self.player.x = min(SCREEN_WIDTH - 50, self.player.x)

    def _check_hit_detection(
        self, punch_type: PunchType = None, reach: float = None, tolerance: int = 20
    ) -> tuple[bool, float, float]:
        """Check if punch hits the bag.

        Args:
            punch_type: Type of punch being thrown (used to get reach if not specified)
            reach: Override reach distance (defaults to punch_type reach)
            tolerance: Hit detection tolerance in pixels (default 20)

        Returns:
            Tuple of (hit_landed, bag_x, bag_y)
        """
        bag_x, bag_y = self.heavy_bag.get_position()

        # Determine reach from punch_type if not explicitly provided
        if reach is None:
            if punch_type is None:
                reach = 50  # Default reach
            else:
                attack_props = ATTACK_PROPERTIES[punch_type]
                reach = attack_props.reach

        punch_dir = 1 if self.player.facing_right else -1
        fist_x = self.player.x + (reach * punch_dir)

        bag_left = bag_x - self.heavy_bag.width // 2
        bag_right = bag_x + self.heavy_bag.width // 2

        hit_landed = fist_x >= bag_left - tolerance and fist_x <= bag_right + tolerance
        return hit_landed, bag_x, bag_y

    def _calculate_hit_force(self, punch_type: PunchType) -> float:
        """Calculate force of punch with all modifiers applied.

        Args:
            punch_type: Type of punch being thrown

        Returns:
            Final calculated force value
        """
        attack_props = ATTACK_PROPERTIES[punch_type]
        base_force = attack_props.force
        force = base_force + random.uniform(-0.5, 0.5)

        # Apply combo multiplier
        if self.player.combo > 1:
            force *= 1 + (self.player.combo * 0.1)

        # Apply player multiplier
        force *= self.player.multiplier

        return force

    def _apply_hit_damage(self, force: float, punch_type: PunchType) -> int:
        """Apply damage to bag and calculate score.

        Args:
            force: Force of the hit
            punch_type: Type of punch being thrown

        Returns:
            Points earned from the hit
        """
        self.heavy_bag.hit(force, punch_type, self.player.rage_mode)

        # Calculate and award points
        points = int(10 * force * (1 + self.player.combo * 0.2))
        self.player.score += points

        return points

    def _create_hit_feedback(
        self, bag_x: float, bag_y: float, force: float, points: int
    ) -> None:
        """Create visual and gameplay feedback for successful hit.

        Args:
            bag_x: X position of bag
            bag_y: Y position of bag
            force: Force of the hit
            points: Points earned
        """
        hit_height = bag_y + self.heavy_bag.height // 3

        # Create hit effect + expanding impact ring at the contact point
        self.create_hit_effect(bag_x, hit_height, force)
        self.hit_effects.append(ImpactRing(bag_x, hit_height))

        # Create floating score text
        combo_bonus = ""
        if self.player.combo > 5:
            combo_bonus = " AMAZING!"
        elif self.player.combo > 3:
            combo_bonus = " GREAT!"

        text_color = GOLD if self.player.combo > 5 else YELLOW
        self.floating_texts.append(
            FloatingText(bag_x, hit_height, f"+{points}{combo_bonus}", text_color)
        )

        # Perfect hit bonus
        if abs(self.heavy_bag.angle) < 5:
            self.floating_texts.append(
                FloatingText(bag_x, hit_height - 30, "PERFECT!", GOLD, 42)
            )
            self.player.score += 50

        # Sweat particles when low stamina
        if self.player.stamina < 30:
            for _ in range(3):
                particle_pool.get_particle(
                    self.player.x + random.randint(-10, 10),
                    self.player.y - 10,
                    random.uniform(-1, 1),
                    random.uniform(0, 2),
                    (100, 150, 255),
                    size=2,
                    lifetime=40,
                    gravity=0.5,
                    texture_name="sweat",
                )

        # Screen shake only on heavy hits (design handoff: cross-tier
        # strikes; ±6 spec-px decaying over ~0.3s)
        if force >= 3.0:
            self.screen_shake = float(theme.s(6))

        # Random power-up spawn (5% chance)
        if random.random() < 0.05:
            power_type = random.choice(["stamina", "power", "multiplier", "rage"])
            self.power_ups.append(
                PowerUp(
                    random.randint(100, SCREEN_WIDTH - 100),
                    SCREEN_HEIGHT - 100,
                    power_type,
                )
            )

    def punch(self, punch_type: PunchType) -> None:
        """Handle punch execution and hit detection.

        Args:
            punch_type: Type of punch to execute
        """
        if not self.player.punch(punch_type):
            return

        # Check if punch lands
        hit_landed, bag_x, bag_y = self._check_hit_detection(punch_type)

        if hit_landed:
            # Calculate force and apply damage
            force = self._calculate_hit_force(punch_type)
            points = self._apply_hit_damage(force, punch_type)

            # Create visual feedback
            self._create_hit_feedback(bag_x, bag_y, force, points)

    def special_attack(self) -> None:
        """Execute special attack if conditions are met."""
        if self.player.special_move():
            hit_landed, bag_x, bag_y = self._check_hit_detection(reach=50, tolerance=30)

            if hit_landed:
                force = 8.0 * self.player.multiplier
                self.heavy_bag.hit(force, PunchType.CROSS, self.player.rage_mode)
                self.player.score += int(100 * self.player.multiplier)

                hit_height = bag_y + self.heavy_bag.height // 3
                for _ in range(20):
                    self.create_hit_effect(bag_x, hit_height, force, special=True)

                self.hit_effects.append(ImpactRing(bag_x, hit_height))
                self.floating_texts.append(
                    FloatingText(bag_x, hit_height, "SPECIAL ATTACK!", GOLD, 48, 90)
                )

                self.screen_shake = float(theme.s(10))

    def create_hit_effect(
        self, x: float, y: float, power: float, special: bool = False
    ) -> None:
        """Create visual effects for successful hits.

        Normal hits are carried by the ImpactRing + particles per the
        design handoff; the heavier burst only fires on specials.
        """
        if special:
            self.hit_effects.append(HitEffect(x, y, power))

        # Spawn particles
        if self.settings.particle_effects:
            particle_count = int(power * 5) if not special else 30
            for _ in range(particle_count):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(2, 8) if not special else random.uniform(4, 12)
                color = random.choice([YELLOW, RED, WHITE]) if special else WHITE

                if self.player.rage_mode:
                    color = random.choice([RED, ORANGE, YELLOW])

                particle_pool.get_particle(
                    x,
                    y,
                    math.cos(angle) * speed,
                    math.sin(angle) * speed - 3,
                    color,
                    random.randint(2, 4),
                    random.randint(20, 40),
                )

    def check_power_up_collision(self) -> None:
        """Check for power-up collection by player."""
        player_rect = pygame.Rect(self.player.x - 25, self.player.y - 40, 50, 80)

        for power_up in self.power_ups[:]:
            power_rect = pygame.Rect(power_up.x - 15, power_up.y - 15, 30, 30)

            if player_rect.colliderect(power_rect):
                if power_up.type == "stamina":
                    self.player.stamina = min(
                        self.player.max_stamina, self.player.stamina + 50
                    )
                    text = "STAMINA BOOST!"
                elif power_up.type == "power":
                    self.player.power_meter = self.player.max_power
                    text = "POWER FULL!"
                elif power_up.type == "multiplier":
                    self.player.activate_multiplier()
                    text = "2X MULTIPLIER!"
                elif power_up.type == "rage":
                    self.player.activate_rage()
                    text = "RAGE MODE!"
                else:
                    text = "POWER UP!"

                self.floating_texts.append(
                    FloatingText(self.player.x, self.player.y - 50, text, GREEN, 36, 60)
                )
                self.power_ups.remove(power_up)

    def update(self) -> None:
        """Update game state and all game objects."""
        if self.state != GameState.PLAYING:
            return

        self.heavy_bag.update()
        self.player.update()

        # Update game timer
        self.game_timer += 1
        if self.game_timer >= self.round_time:
            self.state = GameState.GAME_OVER
            self.save_game()

        # Make player face the bag
        bag_x, _ = self.heavy_bag.get_position()
        self.player.facing_right = self.player.x < bag_x

        # Update effects
        if self.settings.particle_effects:
            particle_pool.update()  # Use particle pool update
        self.hit_effects = [h for h in self.hit_effects if h.update()]
        self.floating_texts = [t for t in self.floating_texts if t.update()]
        self.power_ups = [p for p in self.power_ups if p.update()]

        # Check power-up collisions
        self.check_power_up_collision()

        # Screen shake decays exponentially (~0.3s to settle)
        if self.screen_shake > 0:
            self.screen_shake *= 0.82
            if self.screen_shake < 0.5:
                self.screen_shake = 0.0

        # Combo counter animation: pop on each new hit, fade 0.4s after
        # the combo window lapses
        if self.player.combo > self._last_combo and self.player.combo > 1:
            self._combo_pop = 9
        if self._combo_pop > 0:
            self._combo_pop -= 1
        if self.player.combo > 1:
            self._combo_display = self.player.combo
            self._combo_fade = 24
        elif self._combo_fade > 0:
            self._combo_fade -= 1
        self._last_combo = self.player.combo

        # Update high score
        if self.player.score > self.high_score:
            self.high_score = self.player.score

        # Update stats
        if self.player.combo > self.best_combo_all_time:
            self.best_combo_all_time = self.player.combo

    def _save_settings(self) -> None:
        """Persist settings without touching session progress."""
        try:
            SaveManager.save_data(
                self.high_score,
                self.total_punches_all_time,
                self.best_combo_all_time,
                self.settings,
            )
        except SaveError as e:
            logger.error(f"Failed to save settings: {e}")

    def save_game(self) -> None:
        """Save current game progress."""
        self.total_punches_all_time += self.player.total_punches
        if self.player.max_combo > self.best_combo_all_time:
            self.best_combo_all_time = self.player.max_combo

        try:
            SaveManager.save_data(
                self.high_score,
                self.total_punches_all_time,
                self.best_combo_all_time,
                self.settings,
            )
            logger.info("Game saved successfully")
        except SaveError as e:
            logger.error(f"Failed to save game data: {e}")
            # Game continues, but user is notified via logs of save failure

    def _timer_state(self) -> tuple[str, float]:
        """Return (MM:SS remaining, elapsed fraction of the round)."""
        time_left = max(0, self.round_time - self.game_timer) // FPS
        timer_str = f"{time_left // 60:02d}:{time_left % 60:02d}"
        return timer_str, min(1.0, self.game_timer / self.round_time)

    def draw_ui(self) -> None:
        """Draw the in-round HUD (full or minimal variant)."""
        if self.settings.hud_variant == "minimal":
            self._draw_hud_minimal()
        else:
            self._draw_hud_full()

        if self.settings.show_fps:
            fps_text = get_font("barlow-semibold", 18).render(
                f"FPS: {int(self.clock.get_fps())}", True, theme.STAMINA_GREEN
            )
            self.screen.blit(
                fps_text,
                (SCREEN_WIDTH - fps_text.get_width() - theme.s(24), theme.s(14)),
            )

    def _draw_combo(self, size_1080: int, center_y: int) -> None:
        """Centered combo counter: pops on each hit, fades after the
        combo window lapses, AMAZING chip past 5."""
        s = theme.s
        combo = self.player.combo
        alpha = 255
        if combo <= 1:
            if self._combo_fade > 0 and self._combo_display > 1:
                combo = self._combo_display
                alpha = int(255 * self._combo_fade / 24)
            else:
                return
        cx = SCREEN_WIDTH // 2
        combo_surf = get_font("bebas", size_1080).render(f"{combo}×", True, theme.GOLD)
        if self._combo_pop > 0 and alpha == 255:
            pop = 1.0 + 0.35 * (self._combo_pop / 9)
            combo_surf = pygame.transform.smoothscale(
                combo_surf,
                (
                    int(combo_surf.get_width() * pop),
                    int(combo_surf.get_height() * pop),
                ),
            )
        glow = ui.make_radial_glow(combo_surf.get_height() // 2 + s(30), theme.GOLD, 28)
        if alpha < 255:
            glow.set_alpha(alpha)
            combo_surf.set_alpha(alpha)
        self.screen.blit(glow, glow.get_rect(center=(cx, center_y)))
        self.screen.blit(combo_surf, combo_surf.get_rect(center=(cx, center_y)))
        label_font = get_font("barlow-semibold", 18)
        label_w = ui.tracked_label_width("COMBO", label_font, s(5))
        ui.draw_tracked_label(
            self.screen,
            (cx - label_w // 2, center_y + combo_surf.get_height() // 2 - s(6)),
            "COMBO",
            label_font,
            theme.TEXT_DIM,
            s(5),
            alpha=min(theme.TEXT_DIM_ALPHA, alpha),
        )
        if combo > 5 and alpha == 255:
            chip_y = center_y + combo_surf.get_height() // 2 + s(34)
            # Draw chip centered: measure by drawing offscreen first is
            # wasteful; approximate width from the label instead.
            chip_font = get_font("barlow-semibold", 17)
            chip_w = ui.tracked_label_width("AMAZING", chip_font, s(4)) + 2 * s(18)
            ui.draw_chip(self.screen, (cx - chip_w // 2, chip_y), "AMAZING", theme.GOLD)

    def _draw_status_chips(self, y: int) -> None:
        """RAGE / multiplier chips under the timer."""
        s = theme.s
        chips = []
        if self.player.rage_mode:
            chips.append(("RAGE", theme.RAGE_RED))
        if self.player.multiplier > 1:
            chips.append((f"{self.player.multiplier}× SCORE", theme.GOLD))
        x = SCREEN_WIDTH // 2 - s(70) * len(chips)
        for text, color in chips:
            rect = ui.draw_chip(self.screen, (x, y), text, color, dot=True)
            x = rect.right + s(16)

    def _draw_hud_full(self) -> None:
        """Full dashboard HUD (design handoff screen 2)."""
        s = theme.s
        label_font = get_font("barlow-semibold", 16)
        margin = s(theme.MARGIN_HUD)

        # --- Top-left: score block ---
        x, y = margin, s(56)
        ui.draw_tracked_label(
            self.screen,
            (x, y),
            "SCORE",
            label_font,
            theme.TEXT_DIM,
            s(4),
            alpha=theme.TEXT_DIM_ALPHA,
        )
        score_surf = get_font("bebas", 96).render(
            f"{self.player.score:,}", True, theme.TEXT_PRIMARY
        )
        self.screen.blit(score_surf, (x, y + s(24)))
        best_surf = get_font("bebas", 32).render(
            f"BEST {self.high_score:,}", True, theme.GOLD
        )
        self.screen.blit(best_surf, (x, y + s(24) + score_surf.get_height()))

        # --- Top-center: timer + round progress ---
        timer_str, progress = self._timer_state()
        cx = SCREEN_WIDTH // 2
        timer_surf = get_font("bebas", 110).render(timer_str, True, theme.TEXT_PRIMARY)
        self.screen.blit(timer_surf, timer_surf.get_rect(midtop=(cx, s(40))))
        bar_rect = pygame.Rect(0, 0, s(360), s(4))
        bar_rect.midtop = (cx, s(40) + timer_surf.get_height() + s(10))
        ui.draw_mini_bar(self.screen, bar_rect, progress, theme.GOLD)
        round_label = (
            f"TRAINING ROUND — {ROUND_TIME_SECONDS // 60}:{ROUND_TIME_SECONDS % 60:02d}"
        )
        lbl_w = ui.tracked_label_width(round_label, label_font, s(3))
        ui.draw_tracked_label(
            self.screen,
            (cx - lbl_w // 2, bar_rect.bottom + s(12)),
            round_label,
            label_font,
            theme.TEXT_DIM,
            s(3),
            alpha=theme.TEXT_DIM_ALPHA,
        )
        self._draw_status_chips(bar_rect.bottom + s(46))

        # --- Top-right: meters panel ---
        panel = pygame.Rect(0, 0, s(360), s(158))
        panel.topright = (SCREEN_WIDTH - margin, s(56))
        ui.draw_panel(self.screen, panel)
        pad = s(24)
        value_font = get_font("bebas", 28)
        meters = [
            (
                "STAMINA",
                self.player.stamina,
                self.player.max_stamina,
                theme.STAMINA_GREEN,
            ),
            (
                "POWER",
                self.player.power_meter,
                self.player.max_power,
                (
                    theme.GOLD
                    if self.player.power_meter >= self.player.max_power
                    else theme.POWER_BLUE
                ),
            ),
        ]
        for i, (name, value, maximum, color) in enumerate(meters):
            row_y = panel.top + pad + i * s(52)
            ui.draw_tracked_label(
                self.screen,
                (panel.left + pad, row_y),
                name,
                label_font,
                theme.TEXT_DIM,
                s(3),
                alpha=theme.TEXT_DIM_ALPHA,
            )
            value_surf = value_font.render(str(int(value)), True, color)
            self.screen.blit(
                value_surf, (panel.right - pad - value_surf.get_width(), row_y - s(6))
            )
            ui.draw_segmented_bar(
                self.screen,
                pygame.Rect(
                    panel.left + pad,
                    row_y + s(24),
                    panel.width - 2 * pad - s(64),
                    s(10),
                ),
                value / maximum,
                color,
            )
        caption = "SPACE UNLOCKS SPECIAL AT 100"
        ui.draw_tracked_label(
            self.screen,
            (panel.left + pad, panel.bottom - pad - s(14)),
            caption,
            get_font("barlow-medium", 13),
            (
                theme.GOLD
                if self.player.power_meter >= self.player.max_power
                else theme.TEXT_DIM
            ),
            s(2),
            alpha=(
                255
                if self.player.power_meter >= self.player.max_power
                else theme.TEXT_DIM_ALPHA
            ),
        )

        # --- Center: combo ---
        self._draw_combo(200, s(330))

        # --- Bottom-left: control card ---
        self._draw_control_card()

        # --- Bottom-right: bag damage chip ---
        chip = pygame.Rect(0, 0, s(290), s(56))
        chip.bottomright = (SCREEN_WIDTH - margin, SCREEN_HEIGHT - margin + s(24))
        ui.draw_panel(self.screen, chip)
        ui.draw_tracked_label(
            self.screen,
            (chip.left + s(20), chip.centery - s(8)),
            "BAG",
            label_font,
            theme.TEXT_DIM,
            s(3),
            alpha=theme.TEXT_DIM_ALPHA,
        )
        damage_ratio = self.heavy_bag.damage / BAG_MAX_DAMAGE if self.heavy_bag else 0
        bar = pygame.Rect(chip.left + s(78), chip.centery - s(3), s(120), s(6))
        ui.draw_mini_bar(self.screen, bar, damage_ratio, theme.IMPACT_YELLOW)
        pct = get_font("bebas", 24).render(
            f"{int(damage_ratio * 100)}%", True, theme.TEXT_PRIMARY
        )
        self.screen.blit(pct, (bar.right + s(16), chip.centery - pct.get_height() // 2))

    def _draw_control_card(self) -> None:
        """Bottom-left move/keycap reference card."""
        s = theme.s
        margin = s(theme.MARGIN_HUD)
        panel = pygame.Rect(0, 0, s(560), s(286))
        panel.bottomleft = (margin, SCREEN_HEIGHT - margin + s(24))
        ui.draw_panel(self.screen, panel)
        pad = s(24)
        header_font = get_font("barlow-semibold", 14)
        name_font = get_font("barlow-semibold", 18)
        cost_font = get_font("barlow-bold", 15)

        columns = [
            (
                "PUNCHES",
                [
                    ("Z", "Jab", PunchType.JAB),
                    ("X", "Cross", PunchType.CROSS),
                    ("C", "Hook", PunchType.HOOK),
                    ("V", "Uppercut", PunchType.UPPERCUT),
                ],
            ),
            (
                "KICKS",
                [
                    ("Q", "Front Kick", PunchType.FRONT_KICK),
                    ("W", "Roundhouse", PunchType.ROUNDHOUSE_KICK),
                    ("E", "Low Kick", PunchType.LOW_KICK),
                ],
            ),
        ]
        col_w = (panel.width - 2 * pad) // 2
        for c, (title, moves) in enumerate(columns):
            cx0 = panel.left + pad + c * col_w
            ui.draw_tracked_label(
                self.screen,
                (cx0, panel.top + s(18)),
                title,
                header_font,
                theme.TEXT_DIM,
                s(3),
                alpha=theme.TEXT_DIM_ALPHA,
            )
            for r, (key, name, punch) in enumerate(moves):
                row_y = panel.top + s(48) + r * s(42)
                cap_size = s(34)
                ui.draw_keycap(
                    self.screen,
                    (cx0 + cap_size // 2, row_y + cap_size // 2),
                    key,
                    size=cap_size,
                )
                name_surf = name_font.render(name, True, theme.TEXT_PRIMARY)
                self.screen.blit(name_surf, (cx0 + cap_size + s(14), row_y + s(4)))
                cost = ATTACK_PROPERTIES[punch].stamina_cost
                cost_surf = cost_font.render(f"−{cost}", True, theme.STAMINA_GREEN)
                self.screen.blit(cost_surf, (cx0 + col_w - s(50), row_y + s(6)))
        # Gold SPACE special row along the bottom (below the longer column)
        row_y = panel.top + s(48) + 4 * s(42) + s(10)
        cap_rect = ui.draw_keycap(
            self.screen,
            (panel.left + pad + s(38), row_y + s(17)),
            "SPACE",
            size=s(34),
            gold=True,
        )
        special_surf = name_font.render("Special — full power meter", True, theme.GOLD)
        self.screen.blit(special_surf, (cap_rect.right + s(14), row_y + s(4)))

    def _draw_hud_minimal(self) -> None:
        """Minimal HUD (design handoff screen 3): no panels, slim bars."""
        s = theme.s
        margin = s(theme.MARGIN_HUD)

        # Score + BEST inline, top-left
        score_surf = get_font("bebas", 56).render(
            f"{self.player.score:,}", True, theme.TEXT_PRIMARY
        )
        self.screen.blit(score_surf, (margin, s(48)))
        best_surf = get_font("bebas", 28).render(
            f"BEST {self.high_score:,}", True, theme.GOLD
        )
        self.screen.blit(
            best_surf,
            (
                margin + score_surf.get_width() + s(20),
                s(48) + score_surf.get_height() - best_surf.get_height() - s(6),
            ),
        )

        # Timer + slim progress, top-center
        timer_str, progress = self._timer_state()
        cx = SCREEN_WIDTH // 2
        timer_surf = get_font("bebas", 64).render(timer_str, True, theme.TEXT_PRIMARY)
        self.screen.blit(timer_surf, timer_surf.get_rect(midtop=(cx, s(40))))
        bar_rect = pygame.Rect(0, 0, s(200), s(2))
        bar_rect.midtop = (cx, s(40) + timer_surf.get_height() + s(8))
        ui.draw_mini_bar(self.screen, bar_rect, progress, theme.GOLD)
        self._draw_status_chips(bar_rect.bottom + s(20))

        # Combo
        self._draw_combo(160, s(300))

        # Bottom-center slim meters
        label_font = get_font("barlow-semibold", 14)
        meters = [
            ("STA", self.player.stamina, self.player.max_stamina, theme.STAMINA_GREEN),
            (
                "PWR",
                self.player.power_meter,
                self.player.max_power,
                (
                    theme.GOLD
                    if self.player.power_meter >= self.player.max_power
                    else theme.POWER_BLUE
                ),
            ),
        ]
        for i, (name, value, maximum, color) in enumerate(meters):
            bar = pygame.Rect(0, 0, s(420), s(6))
            bar.midtop = (cx, SCREEN_HEIGHT - s(96) + i * s(26))
            lbl = label_font.render(name, True, theme.TEXT_DIM)
            lbl.set_alpha(theme.TEXT_DIM_ALPHA)
            self.screen.blit(lbl, (bar.left - lbl.get_width() - s(14), bar.top - s(6)))
            ui.draw_mini_bar(self.screen, bar, value / maximum, color)

        # One dim hint line bottom-right
        hint = get_font("barlow-medium", 15).render(
            "Z X C V punches · Q W E kicks · SPACE special · ESC pause",
            True,
            theme.TEXT_DIM,
        )
        hint.set_alpha(theme.TEXT_DIM_ALPHA)
        self.screen.blit(
            hint,
            (SCREEN_WIDTH - margin - hint.get_width(), SCREEN_HEIGHT - s(52)),
        )

    def draw_pause_menu(self) -> None:
        """Draw the pause overlay (design handoff screen 4)."""
        s = theme.s
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((*theme.OVERLAY_DARK, theme.OVERLAY_ALPHA))
        self.screen.blit(overlay, (0, 0))

        left = s(200)
        label_font = get_font("barlow-semibold", 17)
        timer_str, _ = self._timer_state()
        ui.draw_tracked_label(
            self.screen,
            (left, s(240)),
            f"TRAINING ROUND — {timer_str} LEFT",
            label_font,
            theme.TEXT_DIM,
            s(3),
            alpha=theme.TEXT_DIM_ALPHA,
        )
        paused = get_font("bebas", 220).render("PAUSED", True, theme.TEXT_PRIMARY)
        self.screen.blit(paused, (left - s(8), s(266)))

        rows_y = s(266) + paused.get_height() + s(30)
        row_w, row_h = s(520), s(74)
        for i, (text, key) in enumerate((("RESUME", "ESC"), ("QUIT TO MENU", "Q"))):
            rect = pygame.Rect(left, rows_y + i * row_h, row_w, row_h - s(10))
            ui.draw_menu_row(self.screen, rect, text, i == 0, hint="")
            ui.draw_keycap(
                self.screen,
                (rect.right - s(48), rect.centery),
                key,
                size=s(36),
                gold=i == 0,
            )

        # Right: THIS SESSION panel
        panel = pygame.Rect(0, 0, s(380), s(280))
        panel.topright = (SCREEN_WIDTH - s(160), s(300))
        ui.draw_panel(self.screen, panel)
        pad = s(28)
        ui.draw_tracked_label(
            self.screen,
            (panel.left + pad, panel.top + s(24)),
            "THIS SESSION",
            label_font,
            theme.TEXT_DIM,
            s(4),
            alpha=theme.TEXT_DIM_ALPHA,
        )
        session = [
            ("Score", f"{self.player.score:,}", theme.TEXT_PRIMARY),
            ("Best combo", f"{self.player.max_combo}×", theme.GOLD),
            ("Punches thrown", str(self.player.total_punches), theme.TEXT_PRIMARY),
        ]
        stat_label_font = get_font("barlow-medium", 17)
        value_font = get_font("bebas", 44)
        for i, (label, value, color) in enumerate(session):
            row_y = panel.top + s(76) + i * s(62)
            lbl = stat_label_font.render(label, True, theme.TEXT_DIM)
            lbl.set_alpha(theme.TEXT_DIM_ALPHA)
            self.screen.blit(lbl, (panel.left + pad, row_y + s(8)))
            val = value_font.render(value, True, color)
            self.screen.blit(val, (panel.right - pad - val.get_width(), row_y))

    def draw_game_over(self) -> None:
        """Draw the round-complete screen (design handoff screen 5)."""
        s = theme.s
        self.screen.fill((0, 0, 0))
        glow = ui.make_radial_glow(s(360), theme.GOLD, 36)
        self.screen.blit(glow, glow.get_rect(center=(SCREEN_WIDTH // 2, 0)))

        cx = SCREEN_WIDTH // 2
        label_font = get_font("barlow-semibold", 17)

        session_label = f"TRAINING SESSION — {ROUND_TIME_SECONDS // 60}:{ROUND_TIME_SECONDS % 60:02d}"
        lbl_w = ui.tracked_label_width(session_label, label_font, s(4))
        ui.draw_tracked_label(
            self.screen,
            (cx - lbl_w // 2, s(70)),
            session_label,
            label_font,
            theme.TEXT_DIM,
            s(4),
            alpha=theme.TEXT_DIM_ALPHA,
        )

        title = get_font("bebas", 130).render("ROUND COMPLETE", True, theme.GOLD)
        self.screen.blit(title, title.get_rect(midtop=(cx, s(100))))

        final_label_y = s(100) + title.get_height() + s(16)
        lbl_w = ui.tracked_label_width("FINAL SCORE", label_font, s(4))
        ui.draw_tracked_label(
            self.screen,
            (cx - lbl_w // 2, final_label_y),
            "FINAL SCORE",
            label_font,
            theme.TEXT_DIM,
            s(4),
            alpha=theme.TEXT_DIM_ALPHA,
        )
        score_surf = get_font("bebas", 250).render(
            f"{self.player.score:,}", True, theme.TEXT_PRIMARY
        )
        self.screen.blit(
            score_surf, score_surf.get_rect(midtop=(cx, final_label_y + s(20)))
        )

        # Three stat cards
        cards = [
            ("BEST COMBO", f"{self.player.max_combo}×", theme.GOLD),
            ("TOTAL PUNCHES", str(self.player.total_punches), theme.TEXT_PRIMARY),
            ("HIGH SCORE", f"{self.high_score:,}", theme.TEXT_PRIMARY),
        ]
        card_w, card_h, gap = s(300), s(150), s(24)
        cards_y = final_label_y + s(20) + score_surf.get_height() + s(20)
        total_w = 3 * card_w + 2 * gap
        value_font = get_font("bebas", 72)
        card_label_font = get_font("barlow-semibold", 15)
        for i, (label, value, color) in enumerate(cards):
            rect = pygame.Rect(
                cx - total_w // 2 + i * (card_w + gap), cards_y, card_w, card_h
            )
            ui.draw_card(self.screen, rect)
            lbl_w = ui.tracked_label_width(label, card_label_font, s(3))
            ui.draw_tracked_label(
                self.screen,
                (rect.centerx - lbl_w // 2, rect.top + s(24)),
                label,
                card_label_font,
                theme.TEXT_DIM,
                s(3),
                alpha=theme.TEXT_DIM_ALPHA,
            )
            val = value_font.render(value, True, color)
            self.screen.blit(val, val.get_rect(midtop=(rect.centerx, rect.top + s(52))))

        # All-time strip
        strip = (
            f"ALL-TIME · {self.total_punches_all_time:,} TOTAL PUNCHES · "
            f"{self.best_combo_all_time}× BEST COMBO"
        )
        strip_font = get_font("barlow-medium", 16)
        strip_w = ui.tracked_label_width(strip, strip_font, s(2))
        ui.draw_tracked_label(
            self.screen,
            (cx - strip_w // 2, cards_y + card_h + s(36)),
            strip,
            strip_font,
            theme.TEXT_DIM,
            s(2),
            alpha=theme.TEXT_DIM_ALPHA,
        )

        # Keycap hints
        hint_font = get_font("barlow-medium", 18)
        hint_y = SCREEN_HEIGHT - s(70)
        x = cx - s(160)
        for cap, label in (("ENTER", "Menu"), ("R", "Restart")):
            cap_rect = ui.draw_keycap(self.screen, (x, hint_y), cap, size=s(38))
            text = hint_font.render(label, True, theme.TEXT_DIM)
            text.set_alpha(theme.TEXT_DIM_ALPHA)
            self.screen.blit(
                text, (cap_rect.right + s(12), hint_y - text.get_height() // 2)
            )
            x = cap_rect.right + s(12) + text.get_width() + s(60)

    def draw(self) -> None:
        """Main drawing method for all game states with enhanced graphics."""
        if self.state == GameState.MENU:
            self.menu.set_stats(
                self.high_score,
                self.total_punches_all_time,
                self.best_combo_all_time,
            )
            self.menu.draw(self.screen)

        elif self.state == GameState.SETTINGS:
            self.settings_screen.draw(self.screen)

        elif self.state == GameState.TUTORIAL:
            self.tutorial_screen.draw(self.screen)

        elif self.state in [GameState.PLAYING, GameState.PAUSED]:
            # Apply screen shake
            shake_offset_x = 0
            shake_offset_y = 0
            if self.screen_shake >= 1:
                amp = int(self.screen_shake)
                shake_offset_x = random.randint(-amp, amp)
                shake_offset_y = random.randint(-amp, amp)

            # Create temporary surface
            temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

            # Draw enhanced background
            self._draw_enhanced_background(temp_surface)

            # Draw range indicator with enhanced styling
            if self.heavy_bag:
                self._draw_enhanced_range_indicator(temp_surface)

            # Draw objects
            if self.heavy_bag:
                self.heavy_bag.draw(temp_surface)
            if self.player:
                self.player.draw(temp_surface)

            # Draw power-ups
            for power_up in self.power_ups:
                power_up.draw(temp_surface)

            # Draw particles with enhanced textures using pool
            if self.settings.particle_effects:
                particle_pool.draw(temp_surface)

            # Draw hit effects
            for effect in self.hit_effects:
                effect.draw(temp_surface)

            # Draw combo effects
            for combo_effect in self.combo_effects:
                combo_effect.draw(temp_surface)

            # Apply shake
            self.screen.blit(temp_surface, (shake_offset_x, shake_offset_y))

            # Draw floating texts (no shake)
            for text in self.floating_texts:
                text.draw(self.screen)

            # Draw UI
            self.draw_ui()

            # Draw pause menu if paused
            if self.state == GameState.PAUSED:
                self.draw_pause_menu()

        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()

        pygame.display.flip()

    def _draw_enhanced_background(self, surface: pygame.Surface) -> None:
        """Draw enhanced gym background with atmosphere."""
        # Try to get background from graphics manager
        background = graphics_manager.get_background("gym")

        if background:
            surface.blit(background, (0, 0))
        else:
            # Fallback to procedural background
            surface.fill(BLACK)

            # Enhanced gradient background
            for i in range(SCREEN_HEIGHT):
                color_value = int(20 + (i / SCREEN_HEIGHT) * 30)
                pygame.draw.line(
                    surface,
                    (color_value, color_value, color_value + 10),
                    (0, i),
                    (SCREEN_WIDTH, i),
                )

            # Enhanced floor
            pygame.draw.rect(
                surface, DARK_GRAY, (0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40)
            )
            pygame.draw.line(
                surface,
                WHITE,
                (0, SCREEN_HEIGHT - 40),
                (SCREEN_WIDTH, SCREEN_HEIGHT - 40),
                3,
            )

            # Mat pattern
            for i in range(0, SCREEN_WIDTH, 50):
                pygame.draw.line(
                    surface, GRAY, (i, SCREEN_HEIGHT - 40), (i, SCREEN_HEIGHT), 1
                )

    def _draw_enhanced_range_indicator(self, surface: pygame.Surface) -> None:
        """Green glow strip rising from the floor under the bag while the
        player is in the hit zone (design handoff screen 2)."""
        s = theme.s
        bag_x, _ = self.heavy_bag.get_position()
        hit_zone_left = bag_x - self.heavy_bag.width // 2 - 60
        hit_zone_right = bag_x + self.heavy_bag.width // 2 + 20
        floor_y = SCREEN_HEIGHT - s(60)

        player_in_range = hit_zone_left <= self.player.x <= hit_zone_right
        if not player_in_range:
            # Faint resting marker so the zone stays discoverable
            pygame.draw.line(
                surface,
                (60, 64, 70),
                (hit_zone_left, floor_y),
                (hit_zone_right, floor_y),
                1,
            )
            return

        if self._range_glow is None:
            self._range_glow = ui.make_vertical_alpha_gradient(
                (s(360), s(180)), theme.STAMINA_GREEN, 0, 80
            )
        # Opacity pulse 0.55 -> 1.0 at ~1.6s period
        pulse = 0.775 + 0.225 * math.sin(pygame.time.get_ticks() * (2 * math.pi / 1600))
        glow = self._range_glow.copy()
        glow.set_alpha(int(255 * pulse))
        glow_rect = glow.get_rect(midbottom=(int(bag_x), floor_y))
        surface.blit(glow, glow_rect)
        pygame.draw.line(
            surface,
            theme.STAMINA_GREEN,
            (glow_rect.left, floor_y),
            (glow_rect.right, floor_y),
            3,
        )
        chip_font = get_font("barlow-semibold", 15)
        chip_w = ui.tracked_label_width("IN RANGE", chip_font, s(4)) + 2 * s(18) + s(16)
        ui.draw_chip(
            surface,
            (int(bag_x) - chip_w // 2, glow_rect.top - s(20)),
            "IN RANGE",
            theme.STAMINA_GREEN,
            font_size=15,
            dot=True,
        )

    async def run(self) -> None:
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            # Yield to the browser event loop (required by pygbag); no-op pacing
            # cost on desktop
            await asyncio.sleep(0)

        # Save before quitting
        if self.player:
            self.save_game()

        pygame.quit()
