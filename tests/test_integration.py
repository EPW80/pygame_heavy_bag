"""
Integration test example for Heavy Bag Training game.

This shows how to properly test the game modules by running them as a package.

Usage:
    cd /path/to/heavy_bag_game
    python -m pytest tests/test_integration.py
"""

import unittest

# This is the proper way to import when running as a package
try:
    from src.utils.constants import PunchType, Difficulty
    from src.game.player import Player
    from src.game.heavy_bag import HeavyBag
    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False


@unittest.skipUnless(IMPORTS_AVAILABLE, "Game modules not available")
class TestPlayerIntegration(unittest.TestCase):
    """Integration tests for Player class."""

    def setUp(self):
        """Set up test fixtures."""
        self.player = Player(100, 100, Difficulty.NORMAL)

    def test_player_initialization(self):
        """Test player initialization."""
        self.assertEqual(self.player.x, 100)
        self.assertEqual(self.player.y, 100)
        self.assertEqual(self.player.stamina, 100)
        self.assertEqual(self.player.score, 0)
        self.assertEqual(self.player.combo, 0)

    def test_punch_mechanics(self):
        """Test punch mechanics."""
        initial_stamina = self.player.stamina
        success = self.player.punch(PunchType.JAB)

        self.assertTrue(success)
        self.assertLess(self.player.stamina, initial_stamina)
        self.assertEqual(self.player.combo, 1)


@unittest.skipUnless(IMPORTS_AVAILABLE, "Game modules not available")
class TestHeavyBagIntegration(unittest.TestCase):
    """Integration tests for HeavyBag class."""

    def setUp(self):
        """Set up test fixtures."""
        self.bag = HeavyBag(200, 50, Difficulty.NORMAL)

    def test_bag_initialization(self):
        """Test bag initialization."""
        self.assertEqual(self.bag.x, 200)
        self.assertEqual(self.bag.y, 50)
        self.assertEqual(self.bag.angle, 0)
        self.assertEqual(self.bag.damage, 0)

    def test_hit_mechanics(self):
        """Test hit mechanics."""
        initial_damage = self.bag.damage
        self.bag.hit(5.0, PunchType.CROSS)

        self.assertGreater(self.bag.damage, initial_damage)
        self.assertNotEqual(self.bag.hit_force, 0)


if __name__ == '__main__':
    if not IMPORTS_AVAILABLE:
        print("Skipping integration tests - game modules not available")
        print("Run with: python -m pytest tests/test_integration.py")
    unittest.main()
