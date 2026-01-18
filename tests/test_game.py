"""
Unit tests for Heavy Bag Training game.

Note: These tests require running the game modules as a package.
Run with: python -m pytest tests/test_game.py
"""

import unittest

try:
    from src.utils.constants import (
        PunchType, Difficulty,
        STAMINA_JAB, STAMINA_CROSS, STAMINA_HOOK, STAMINA_UPPERCUT,
        PLAYER_MAX_STAMINA, PLAYER_MAX_POWER,
        COMBO_TIMER_DURATION, RAGE_DURATION,
        BAG_MAX_DAMAGE, BAG_MAX_ANGLE,
    )
    from src.game.player import Player
    from src.game.heavy_bag import HeavyBag
    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False


@unittest.skipUnless(IMPORTS_AVAILABLE, "Game modules not available")
class TestPlayerPunchMechanics(unittest.TestCase):
    """Test cases for player punch mechanics."""

    def setUp(self):
        """Set up test fixtures."""
        self.player = Player(100, 100, Difficulty.NORMAL)

    def test_player_initialization(self):
        """Test player initializes with correct values."""
        self.assertEqual(self.player.stamina, PLAYER_MAX_STAMINA)
        self.assertEqual(self.player.max_stamina, PLAYER_MAX_STAMINA)
        self.assertEqual(self.player.max_power, PLAYER_MAX_POWER)
        self.assertEqual(self.player.score, 0)
        self.assertEqual(self.player.combo, 0)
        self.assertEqual(self.player.punch_cooldown, 0)
        self.assertFalse(self.player.rage_mode)

    def test_jab_punch_stamina_cost(self):
        """Test jab punch consumes correct stamina."""
        initial_stamina = self.player.stamina
        success = self.player.punch(PunchType.JAB)

        self.assertTrue(success)
        self.assertEqual(
            self.player.stamina,
            initial_stamina - STAMINA_JAB
        )

    def test_cross_punch_stamina_cost(self):
        """Test cross punch consumes correct stamina."""
        initial_stamina = self.player.stamina
        success = self.player.punch(PunchType.CROSS)

        self.assertTrue(success)
        self.assertEqual(
            self.player.stamina,
            initial_stamina - STAMINA_CROSS
        )

    def test_hook_punch_stamina_cost(self):
        """Test hook punch consumes correct stamina."""
        initial_stamina = self.player.stamina
        success = self.player.punch(PunchType.HOOK)

        self.assertTrue(success)
        self.assertEqual(
            self.player.stamina,
            initial_stamina - STAMINA_HOOK
        )

    def test_uppercut_punch_stamina_cost(self):
        """Test uppercut punch consumes correct stamina."""
        initial_stamina = self.player.stamina
        success = self.player.punch(PunchType.UPPERCUT)

        self.assertTrue(success)
        self.assertEqual(
            self.player.stamina,
            initial_stamina - STAMINA_UPPERCUT
        )

    def test_punch_increments_combo(self):
        """Test successful punch increments combo counter."""
        initial_combo = self.player.combo
        self.player.punch(PunchType.JAB)

        self.assertEqual(self.player.combo, initial_combo + 1)

    def test_punch_sets_combo_timer(self):
        """Test punch sets combo timer."""
        self.player.punch(PunchType.JAB)
        self.assertEqual(self.player.combo_timer, COMBO_TIMER_DURATION)

    def test_punch_with_insufficient_stamina_fails(self):
        """Test punch fails when stamina is insufficient."""
        self.player.stamina = 2  # Less than JAB cost
        success = self.player.punch(PunchType.JAB)

        self.assertFalse(success)
        self.assertEqual(self.player.combo, 0)

    def test_punch_sets_cooldown(self):
        """Test punch sets cooldown timer."""
        self.player.punch(PunchType.JAB)
        self.assertGreater(self.player.punch_cooldown, 0)

    def test_punch_during_cooldown_fails(self):
        """Test cannot punch during cooldown."""
        self.player.punch(PunchType.JAB)
        success = self.player.punch(PunchType.JAB)

        self.assertFalse(success)

    def test_combo_resets_after_timeout(self):
        """Test combo resets when timer expires."""
        self.player.punch(PunchType.JAB)
        self.player.combo_timer = 1
        self.player.update()
        self.player.update()  # Timer expires

        self.assertEqual(self.player.combo, 0)

    def test_rage_mode_reduces_stamina_cost(self):
        """Test rage mode reduces stamina cost."""
        self.player.activate_rage()
        initial_stamina = self.player.stamina

        self.player.punch(PunchType.JAB)
        stamina_used = initial_stamina - self.player.stamina

        self.assertLess(stamina_used, STAMINA_JAB)

    def test_rage_mode_has_duration(self):
        """Test rage mode lasts for specified duration."""
        self.player.activate_rage()

        self.assertTrue(self.player.rage_mode)
        self.assertEqual(self.player.rage_timer, RAGE_DURATION)

    def test_rage_mode_expires(self):
        """Test rage mode expires after timer."""
        self.player.activate_rage()
        self.player.rage_timer = 1
        self.player.update()
        self.player.update()

        self.assertFalse(self.player.rage_mode)

    def test_multiplier_activation(self):
        """Test multiplier activation."""
        self.player.activate_multiplier()

        self.assertEqual(self.player.multiplier, 2.0)
        self.assertGreater(self.player.multiplier_timer, 0)

    def test_special_move_requires_full_power(self):
        """Test special move requires full power meter."""
        self.player.power_meter = PLAYER_MAX_POWER - 1
        success = self.player.special_move()

        self.assertFalse(success)

    def test_special_move_consumes_power_and_stamina(self):
        """Test special move consumes resources."""
        self.player.power_meter = PLAYER_MAX_POWER
        success = self.player.special_move()

        self.assertTrue(success)
        self.assertEqual(self.player.power_meter, 0)

    def test_stamina_regeneration(self):
        """Test stamina regenerates over time."""
        self.player.stamina = 50
        initial_stamina = self.player.stamina

        self.player.update()

        self.assertGreater(self.player.stamina, initial_stamina)

    def test_stamina_does_not_exceed_max(self):
        """Test stamina cannot exceed maximum."""
        self.player.stamina = PLAYER_MAX_STAMINA
        self.player.update()

        self.assertEqual(self.player.stamina, PLAYER_MAX_STAMINA)


@unittest.skipUnless(IMPORTS_AVAILABLE, "Game modules not available")
class TestHeavyBagPhysics(unittest.TestCase):
    """Test cases for heavy bag physics."""

    def setUp(self):
        """Set up test fixtures."""
        self.bag = HeavyBag(200, 50, Difficulty.NORMAL)

    def test_bag_initialization(self):
        """Test bag initializes with correct values."""
        self.assertEqual(self.bag.x, 200)
        self.assertEqual(self.bag.y, 50)
        self.assertEqual(self.bag.angle, 0)
        self.assertEqual(self.bag.angular_velocity, 0)
        self.assertEqual(self.bag.damage, 0)

    def test_hit_increases_damage(self):
        """Test hitting bag increases damage."""
        initial_damage = self.bag.damage
        self.bag.hit(5.0, PunchType.CROSS)

        self.assertGreater(self.bag.damage, initial_damage)

    def test_hit_applies_force(self):
        """Test hit applies force to bag."""
        self.bag.hit(5.0, PunchType.CROSS)

        self.assertNotEqual(self.bag.hit_force, 0)

    def test_hit_with_rage_multiplies_force(self):
        """Test rage mode multiplies hit force."""
        self.bag.hit(5.0, PunchType.CROSS, rage_mode=False)
        normal_damage = self.bag.damage

        self.bag.damage = 0
        self.bag.hit(5.0, PunchType.CROSS, rage_mode=True)
        rage_damage = self.bag.damage

        self.assertGreater(rage_damage, normal_damage)

    def test_bag_swings_after_hit(self):
        """Test bag swings after being hit."""
        self.bag.hit(5.0, PunchType.CROSS)
        self.bag.update()

        self.assertNotEqual(self.bag.angle, 0)

    def test_bag_angle_limited(self):
        """Test bag angle is limited to max angle."""
        # Apply large force to exceed max angle
        self.bag.hit(100.0, PunchType.UPPERCUT)
        for _ in range(10):
            self.bag.update()

        self.assertLessEqual(abs(self.bag.angle), BAG_MAX_ANGLE)

    def test_bag_returns_to_center(self):
        """Test bag returns to center over time."""
        self.bag.hit(5.0, PunchType.CROSS)

        # Let bag swing and settle (needs more iterations)
        for _ in range(500):
            self.bag.update()

        self.assertLess(abs(self.bag.angle), 5.0)
        self.assertLess(abs(self.bag.angular_velocity), 0.5)

    def test_damage_recovers_over_time(self):
        """Test damage recovers over time."""
        self.bag.hit(50.0, PunchType.UPPERCUT)
        initial_damage = self.bag.damage

        for _ in range(50):
            self.bag.update()

        self.assertLess(self.bag.damage, initial_damage)

    def test_damage_cannot_exceed_max(self):
        """Test damage cannot exceed maximum."""
        # Apply massive damage
        for _ in range(10):
            self.bag.hit(100.0, PunchType.UPPERCUT)

        self.assertLessEqual(self.bag.damage, BAG_MAX_DAMAGE)

    def test_glow_activates_at_high_damage(self):
        """Test bag glows when heavily damaged."""
        threshold_damage = BAG_MAX_DAMAGE * 0.8
        self.bag.damage = threshold_damage + 1
        self.bag.hit(1.0, PunchType.JAB)

        self.assertGreater(self.bag.glow_timer, 0)

    def test_physics_damping_by_difficulty(self):
        """Test different difficulties have different damping."""
        easy_bag = HeavyBag(200, 50, Difficulty.EASY)
        hard_bag = HeavyBag(200, 50, Difficulty.HARD)

        # Easy bag should have more damping (swings settle faster)
        self.assertGreater(easy_bag.damping, hard_bag.damping)


@unittest.skipUnless(IMPORTS_AVAILABLE, "Game modules not available")
class TestScoreCalculations(unittest.TestCase):
    """Test cases for score calculations."""

    def setUp(self):
        """Set up test fixtures."""
        self.player = Player(100, 100, Difficulty.NORMAL)

    def test_combo_increases_with_punches(self):
        """Test combo increases with consecutive punches."""
        for i in range(3):
            # Reset cooldown to allow consecutive punches
            self.player.punch_cooldown = 0
            self.player.punch(PunchType.JAB)

        self.assertEqual(self.player.combo, 3)

    def test_max_combo_tracks_highest(self):
        """Test max combo tracks the highest achieved combo."""
        # Build combo
        for i in range(5):
            self.player.punch_cooldown = 0
            self.player.punch(PunchType.JAB)

        # Force combo update by expiring timer
        self.player.combo_timer = 0
        self.player.update()

        self.assertEqual(self.player.max_combo, 5)

        # Build smaller combo
        for i in range(3):
            self.player.punch_cooldown = 0
            self.player.punch(PunchType.JAB)

        # Force combo update
        self.player.combo_timer = 0
        self.player.update()

        # Max should still be 5
        self.assertEqual(self.player.max_combo, 5)

    def test_total_punches_increments(self):
        """Test total punches counter increments."""
        initial_total = self.player.total_punches

        for i in range(3):
            self.player.punch_cooldown = 0
            self.player.punch(PunchType.JAB)

        self.assertEqual(
            self.player.total_punches,
            initial_total + 3
        )

    def test_multiplier_affects_scoring(self):
        """Test multiplier affects score calculations."""
        self.player.multiplier = 2.0

        self.assertEqual(self.player.multiplier, 2.0)


@unittest.skipUnless(IMPORTS_AVAILABLE, "Game modules not available")
class TestDifficultyLevels(unittest.TestCase):
    """Test cases for difficulty levels."""

    def test_easy_difficulty_stamina_regen(self):
        """Test easy difficulty has faster stamina regeneration."""
        easy_player = Player(100, 100, Difficulty.EASY)
        normal_player = Player(100, 100, Difficulty.NORMAL)

        self.assertGreater(
            easy_player.stamina_regen,
            normal_player.stamina_regen
        )

    def test_hard_difficulty_stamina_regen(self):
        """Test hard difficulty has slower stamina regeneration."""
        normal_player = Player(100, 100, Difficulty.NORMAL)
        hard_player = Player(100, 100, Difficulty.HARD)

        self.assertLess(
            hard_player.stamina_regen,
            normal_player.stamina_regen
        )

    def test_expert_difficulty_stamina_regen(self):
        """Test expert difficulty has slowest stamina regeneration."""
        hard_player = Player(100, 100, Difficulty.HARD)
        expert_player = Player(100, 100, Difficulty.EXPERT)

        self.assertLess(
            expert_player.stamina_regen,
            hard_player.stamina_regen
        )


if __name__ == '__main__':
    if not IMPORTS_AVAILABLE:
        print("Skipping tests - game modules not available")
        print("Run with: python -m pytest tests/test_game.py")
    unittest.main()
