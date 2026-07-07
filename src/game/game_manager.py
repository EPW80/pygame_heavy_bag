"""
Main game manager for the Heavy Bag Training game.
"""

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
from ..utils.save_manager import SaveManager
from ..utils.logger import get_logger, SaveError, LoadError, CorruptedDataError

logger = get_logger()
from .player import Player
from .heavy_bag import HeavyBag
from .menu import Menu
from .effects import (
    FloatingText,
    HitEffect,
    PowerUp,
    ComboEffect,
    particle_pool,
)
from .graphics import graphics_manager


class GameManager:
    """Main game loop and state management."""

    def __init__(self):
        # Initialize Pygame
        pygame.init()
        pygame.mixer.init()

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
        self.screen_shake = 0

        # Game timer
        self.game_timer = 0
        self.round_time = ROUND_TIME_FRAMES

    def start_game(self) -> None:
        """Initialize a new game session."""
        self.player = Player(
            SCREEN_WIDTH // 4, SCREEN_HEIGHT - 150, self.settings.difficulty
        )
        self.heavy_bag = HeavyBag(
            SCREEN_WIDTH * 3 // 4, 100, self.settings.difficulty
        )
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
                    logger.info("Tutorial not yet implemented")
                elif action == "Settings":
                    logger.info("Settings not yet implemented")
                elif action == "Quit":
                    self.running = False

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
        self,
        punch_type: PunchType = None,
        reach: float = None,
        tolerance: int = 20
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

        # Create hit effect
        self.create_hit_effect(bag_x, hit_height, force)

        # Create floating score text
        combo_bonus = ""
        if self.player.combo > 5:
            combo_bonus = " AMAZING!"
        elif self.player.combo > 3:
            combo_bonus = " GREAT!"

        text_color = GOLD if self.player.combo > 5 else YELLOW
        self.floating_texts.append(
            FloatingText(
                bag_x, hit_height, f"+{points}{combo_bonus}", text_color
            )
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

        # Screen shake
        self.screen_shake = min(10, int(force * 2))

        # Random power-up spawn (5% chance)
        if random.random() < 0.05:
            power_type = random.choice(
                ["stamina", "power", "multiplier", "rage"]
            )
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
            hit_landed, bag_x, bag_y = self._check_hit_detection(
                reach=50, tolerance=30
            )

            if hit_landed:
                force = 8.0 * self.player.multiplier
                self.heavy_bag.hit(
                    force, PunchType.CROSS, self.player.rage_mode
                )
                self.player.score += int(100 * self.player.multiplier)

                hit_height = bag_y + self.heavy_bag.height // 3
                for _ in range(20):
                    self.create_hit_effect(
                        bag_x, hit_height, force, special=True
                    )

                self.floating_texts.append(
                    FloatingText(
                        bag_x, hit_height, "SPECIAL ATTACK!", GOLD, 48, 90
                    )
                )

                self.screen_shake = 20

    def create_hit_effect(
        self, x: float, y: float, power: float, special: bool = False
    ) -> None:
        """Create visual effects for successful hits."""
        self.hit_effects.append(HitEffect(x, y, power))

        # Spawn particles
        if self.settings.particle_effects:
            particle_count = int(power * 5) if not special else 30
            for _ in range(particle_count):
                angle = random.uniform(0, math.pi * 2)
                speed = (
                    random.uniform(2, 8) if not special
                    else random.uniform(4, 12)
                )
                color = (
                    random.choice([YELLOW, RED, WHITE]) if special else WHITE
                )

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
        player_rect = pygame.Rect(
            self.player.x - 25, self.player.y - 40, 50, 80
        )

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
                    FloatingText(
                        self.player.x, self.player.y - 50, text, GREEN, 36, 60
                    )
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

        # Update screen shake
        if self.screen_shake > 0:
            self.screen_shake -= 1

        # Update high score
        if self.player.score > self.high_score:
            self.high_score = self.player.score

        # Update stats
        if self.player.combo > self.best_combo_all_time:
            self.best_combo_all_time = self.player.combo

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

    def draw_ui(self) -> None:
        """Draw the game user interface."""
        # Timer
        time_left = max(0, self.round_time - self.game_timer) // FPS
        minutes = time_left // 60
        seconds = time_left % 60
        timer_str = f"{minutes:02d}:{seconds:02d}"
        timer_text = self.font_large.render(timer_str, True, WHITE)
        timer_rect = timer_text.get_rect(center=(SCREEN_WIDTH // 2, 30))
        self.screen.blit(timer_text, timer_rect)

        # Score
        score_str = f"Score: {self.player.score}"
        score_text = self.font_large.render(score_str, True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # High Score
        high_score_text = self.font_medium.render(
            f"Best: {self.high_score}", True, GOLD
        )
        self.screen.blit(high_score_text, (10, 60))

        # Combo
        if self.player.combo > 1:
            combo_color = (
                GOLD
                if self.player.combo >= 10
                else YELLOW if self.player.combo >= 5 else WHITE
            )
            combo_text = self.font_large.render(
                f"{self.player.combo}x COMBO!", True, combo_color
            )
            combo_rect = combo_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
            self.screen.blit(combo_text, combo_rect)

        # Stamina bar
        self.draw_bar(
            SCREEN_WIDTH - 220,
            20,
            200,
            20,
            self.player.stamina,
            self.player.max_stamina,
            GREEN,
            "STAMINA",
        )

        # Power meter
        self.draw_bar(
            SCREEN_WIDTH - 220,
            60,
            200,
            20,
            self.player.power_meter,
            self.player.max_power,
            BLUE if self.player.power_meter < self.player.max_power else GOLD,
            "POWER",
        )

        # Rage mode indicator
        if self.player.rage_mode:
            rage_text = self.font_medium.render("RAGE MODE!", True, RED)
            rage_rect = rage_text.get_rect(center=(SCREEN_WIDTH // 2, 180))
            self.screen.blit(rage_text, rage_rect)

        # Multiplier indicator
        if self.player.multiplier > 1:
            mult_text = self.font_medium.render(
                f"{self.player.multiplier}x", True, GOLD
            )
            mult_rect = mult_text.get_rect(center=(SCREEN_WIDTH // 2, 210))
            self.screen.blit(mult_text, mult_rect)

        # Instructions
        instructions = [
            "A/D or ←/→: Move | Z: Jab | X: Cross | C: Hook | V: Uppercut",
            "SPACE: Special | ESC: Pause",
        ]

        for i, instruction in enumerate(instructions):
            text = self.font_small.render(instruction, True, LIGHT_GRAY)
            self.screen.blit(text, (10, SCREEN_HEIGHT - 60 + i * 25))

        # Range indicator
        bag_x, _ = self.heavy_bag.get_position()
        punch_dir = 1 if self.player.facing_right else -1
        fist_x = self.player.x + (40 * punch_dir)
        bag_left = bag_x - self.heavy_bag.width // 2
        bag_right = bag_x + self.heavy_bag.width // 2

        if fist_x >= bag_left - 20 and fist_x <= bag_right + 20:
            range_text = self.font_medium.render("IN RANGE!", True, GREEN)
            range_rect = range_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
            self.screen.blit(range_text, range_rect)

        # FPS counter
        if self.settings.show_fps:
            fps = int(self.clock.get_fps())
            fps_text = self.font_small.render(f"FPS: {fps}", True, GREEN)
            self.screen.blit(fps_text, (SCREEN_WIDTH - 80, 10))

    def draw_controls(self) -> None:
        """Draw clean, organized control labels on screen."""
        # Create compact semi-transparent background panel (top-left position)
        panel_width = 320
        panel_height = 155
        panel_x = 15
        panel_y = 15  # Top of screen instead of bottom

        # Draw background panel
        panel_surface = pygame.Surface(
            (panel_width, panel_height), pygame.SRCALPHA
        )
        pygame.draw.rect(
            panel_surface, (0, 0, 0, 140), (0, 0, panel_width, panel_height)
        )
        pygame.draw.rect(
            panel_surface, DARK_GRAY,
            (0, 0, panel_width, panel_height), 2
        )
        self.screen.blit(panel_surface, (panel_x, panel_y))

        # Control layout in organized columns with tighter spacing
        col1_x = panel_x + 12
        col2_x = panel_x + 170
        base_y = panel_y + 10

        controls = [
            # Left column
            ("MOVEMENT", col1_x, base_y, WHITE, True),
            ("A/D or ←→", col1_x, base_y + 25, LIGHT_GRAY, False),
            ("", col1_x, base_y + 45, WHITE, False),  # Spacer
            ("PUNCHES", col1_x, base_y + 50, GOLD, True),
            ("Z - Jab", col1_x, base_y + 72, LIGHT_GRAY, False),
            ("X - Cross", col1_x, base_y + 90, LIGHT_GRAY, False),
            ("C - Hook", col1_x, base_y + 108, LIGHT_GRAY, False),
            ("V - Uppercut", col1_x, base_y + 126, LIGHT_GRAY, False),
            # Right column
            ("ESC - Pause", col2_x, base_y, LIGHT_GRAY, False),
            ("SPACE - Special", col2_x, base_y + 20, LIGHT_GRAY, False),
            ("", col2_x, base_y + 45, WHITE, False),  # Spacer
            ("KICKS", col2_x, base_y + 50, GOLD, True),
            ("Q - Front Kick", col2_x, base_y + 72, LIGHT_GRAY, False),
            ("W - Roundhouse", col2_x, base_y + 90, LIGHT_GRAY, False),
            ("E - Low Kick", col2_x, base_y + 108, LIGHT_GRAY, False),
        ]

        for text, x, y, color, is_header in controls:
            if text:  # Skip empty spacers
                font = self.font_medium if is_header else self.font_small
                rendered_text = font.render(text, True, color)
                self.screen.blit(rendered_text, (x, y))

    def draw_bar(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        value: float,
        max_value: float,
        color: tuple,
        label: str,
    ) -> None:
        """Draw a progress bar with label."""
        pygame.draw.rect(
            self.screen, DARK_GRAY, (x - 2, y - 2, width + 4, height + 4)
        )
        pygame.draw.rect(self.screen, BLACK, (x, y, width, height))

        fill = int(width * (value / max_value))
        pygame.draw.rect(self.screen, color, (x, y, fill, height))

        label_text = self.font_small.render(label, True, WHITE)
        self.screen.blit(label_text, (x, y - 20))

    def draw_pause_menu(self) -> None:
        """Draw the pause menu overlay."""
        # Darken screen
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Pause text
        pause_text = self.font_large.render("PAUSED", True, WHITE)
        pause_rect = pause_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
        )
        self.screen.blit(pause_text, pause_rect)

        # Instructions
        instructions = ["Press ESC to Resume", "Press Q to Quit to Menu"]

        for i, text in enumerate(instructions):
            inst = self.font_medium.render(text, True, WHITE)
            inst_rect = inst.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + i * 40)
            )
            self.screen.blit(inst, inst_rect)

    def draw_game_over(self) -> None:
        """Draw the game over screen with statistics."""
        # Background
        self.screen.fill(BLACK)

        # Game Over text
        game_over_text = self.font_large.render("ROUND COMPLETE!", True, GOLD)
        go_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(game_over_text, go_rect)

        # Stats
        stats = [
            f"Final Score: {self.player.score}",
            f"High Score: {self.high_score}",
            f"Best Combo: {self.player.max_combo}",
            f"Total Punches: {self.player.total_punches}",
            "",
            "All-Time Stats:",
            f"Total Punches: {self.total_punches_all_time}",
            f"Best Combo Ever: {self.best_combo_all_time}",
        ]

        for i, stat in enumerate(stats):
            color = GOLD if stat.startswith("All-Time") else WHITE
            text = self.font_medium.render(stat, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 200 + i * 40))
            self.screen.blit(text, text_rect)

        # Instructions
        instructions = self.font_medium.render(
            "Press ENTER for Menu | Press R to Restart", True, LIGHT_GRAY
        )
        inst_rect = instructions.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        )
        self.screen.blit(instructions, inst_rect)

    def draw(self) -> None:
        """Main drawing method for all game states with enhanced graphics."""
        if self.state == GameState.MENU:
            self.menu.set_stats(
                self.high_score,
                self.total_punches_all_time,
                self.best_combo_all_time,
            )
            self.menu.draw(self.screen)

        elif self.state in [GameState.PLAYING, GameState.PAUSED]:
            # Apply screen shake
            shake_offset_x = 0
            shake_offset_y = 0
            if self.screen_shake > 0:
                shake_offset_x = random.randint(
                    -self.screen_shake, self.screen_shake
                )
                shake_offset_y = random.randint(
                    -self.screen_shake, self.screen_shake
                )

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
                    surface,
                    GRAY,
                    (i, SCREEN_HEIGHT - 40),
                    (i, SCREEN_HEIGHT),
                    1
                )

    def _draw_enhanced_range_indicator(self, surface: pygame.Surface) -> None:
        """Draw enhanced range indicator with visual effects."""
        bag_x, bag_y = self.heavy_bag.get_position()
        hit_zone_left = bag_x - self.heavy_bag.width // 2 - 60
        hit_zone_right = bag_x + self.heavy_bag.width // 2 + 20
        zone_width = hit_zone_right - hit_zone_left

        # Base zone
        zone_rect = (hit_zone_left, SCREEN_HEIGHT - 39, zone_width, 38)
        pygame.draw.rect(surface, (40, 40, 50), zone_rect)

        # Check if player is in range
        player_in_range = (
            self.player.x >= hit_zone_left and self.player.x <= hit_zone_right
        )

        if player_in_range:
            # Active zone with pulsing effect
            ticks = pygame.time.get_ticks()
            pulse_alpha = int(100 + math.sin(ticks * 0.01) * 50)
            pulse_surface = pygame.Surface((zone_width, 38), pygame.SRCALPHA)
            pulse_surface.fill((*GREEN, pulse_alpha))
            surface.blit(pulse_surface, (hit_zone_left, SCREEN_HEIGHT - 39))

            # Zone border
            pygame.draw.rect(surface, GREEN, zone_rect, 2)
        else:
            # Inactive zone
            pygame.draw.rect(surface, (60, 60, 60), zone_rect, 1)

    def run(self) -> None:
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        # Save before quitting
        if self.player:
            self.save_game()

        pygame.quit()
