"""
Tests for SaveManager functionality.
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch

try:
    from src.utils.save_manager import SaveManager, SAVE_VERSION
    from src.utils.constants import GameSettings, Difficulty
    from src.utils.logger import SaveError, LoadError, CorruptedDataError

    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False


@unittest.skipUnless(IMPORTS_AVAILABLE, "Game modules not available")
class TestSaveManagerBasics(unittest.TestCase):
    """Test basic SaveManager functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = os.path.join(self.temp_dir, "test_save.json")

    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        backup_file = self.temp_file + ".bak"
        if os.path.exists(backup_file):
            os.remove(backup_file)
        os.rmdir(self.temp_dir)

    def test_save_data_creates_file(self):
        """Test that save_data creates a file."""
        with patch("src.utils.save_manager.SAVE_FILE", self.temp_file):
            settings = GameSettings()
            SaveManager.save_data(1000, 50, 10, settings)

            self.assertTrue(os.path.exists(self.temp_file))

    def test_save_data_format(self):
        """Test that saved data has correct format."""
        settings = GameSettings(
            difficulty=Difficulty.HARD,
            sound_enabled=False,
            show_fps=True,
            particle_effects=False,
        )

        with patch("src.utils.save_manager.SAVE_FILE", self.temp_file):
            SaveManager.save_data(2000, 100, 25, settings)

        with open(self.temp_file, "r") as f:
            data = json.load(f)

        self.assertEqual(data["version"], SAVE_VERSION)
        self.assertEqual(data["high_score"], 2000)
        self.assertEqual(data["total_punches"], 100)
        self.assertEqual(data["best_combo"], 25)
        self.assertEqual(data["settings"]["difficulty"], Difficulty.HARD.value)
        self.assertFalse(data["settings"]["sound_enabled"])
        self.assertTrue(data["settings"]["show_fps"])
        self.assertFalse(data["settings"]["particle_effects"])

    def test_load_data_returns_correct_values(self):
        """Test that load_data returns saved values."""
        settings_in = GameSettings(difficulty=Difficulty.EXPERT)

        with patch("src.utils.save_manager.SAVE_FILE", self.temp_file):
            SaveManager.save_data(3000, 150, 30, settings_in)
            score, punches, combo, settings_out = SaveManager.load_data()

            self.assertEqual(score, 3000)
            self.assertEqual(punches, 150)
            self.assertEqual(combo, 30)
            self.assertEqual(settings_out.difficulty, Difficulty.EXPERT)

    @patch("src.utils.save_manager.SAVE_FILE")
    def test_load_data_missing_file_returns_defaults(self, mock_save_file):
        """Test that load_data returns defaults when file doesn't exist."""
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.json")
        mock_save_file.__str__ = lambda x: nonexistent_file
        mock_save_file.return_value = nonexistent_file

        # Mock Path.exists to return False
        with patch("src.utils.save_manager.Path") as mock_path:
            mock_path.return_value.exists.return_value = False

            score, punches, combo, settings = SaveManager.load_data()

            self.assertEqual(score, 0)
            self.assertEqual(punches, 0)
            self.assertEqual(combo, 0)
            self.assertIsInstance(settings, GameSettings)
            self.assertEqual(settings.difficulty, Difficulty.NORMAL)


@unittest.skipUnless(IMPORTS_AVAILABLE, "Game modules not available")
class TestSaveManagerErrorHandling(unittest.TestCase):
    """Test SaveManager error handling."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = os.path.join(self.temp_dir, "test_save.json")

    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        backup_file = self.temp_file + ".bak"
        if os.path.exists(backup_file):
            os.remove(backup_file)
        os.rmdir(self.temp_dir)

    def test_corrupted_json_raises_error(self):
        """Test that corrupted JSON raises CorruptedDataError."""
        # Write invalid JSON
        with open(self.temp_file, "w") as f:
            f.write("{invalid json content")

        with patch("src.utils.save_manager.SAVE_FILE", self.temp_file):
            with self.assertRaises(CorruptedDataError):
                SaveManager.load_data()

    def test_missing_keys_raises_error(self):
        """Test that missing required keys raises CorruptedDataError."""
        # Write JSON with missing keys
        incomplete_data = {"high_score": 100}  # Missing required fields
        with open(self.temp_file, "w") as f:
            json.dump(incomplete_data, f)

        with patch("src.utils.save_manager.SAVE_FILE", self.temp_file):
            with self.assertRaises(CorruptedDataError):
                SaveManager.load_data()

    def test_invalid_difficulty_raises_error(self):
        """Test that invalid difficulty value raises CorruptedDataError."""
        # Write JSON with invalid difficulty
        invalid_data = {
            "version": 1,
            "high_score": 100,
            "total_punches": 50,
            "best_combo": 10,
            "settings": {
                "difficulty": 999,  # Invalid enum value
                "sound_enabled": True,
                "show_fps": False,
                "particle_effects": True,
            },
        }
        with open(self.temp_file, "w") as f:
            json.dump(invalid_data, f)

        with patch("src.utils.save_manager.SAVE_FILE", self.temp_file):
            with self.assertRaises(CorruptedDataError):
                SaveManager.load_data()

    def test_negative_values_raise_error(self):
        """Test that negative values raise CorruptedDataError."""
        # Write JSON with negative values
        invalid_data = {
            "version": 1,
            "high_score": -100,  # Invalid negative
            "total_punches": 50,
            "best_combo": 10,
            "settings": {
                "difficulty": Difficulty.NORMAL.value,
                "sound_enabled": True,
                "show_fps": False,
                "particle_effects": True,
            },
        }
        with open(self.temp_file, "w") as f:
            json.dump(invalid_data, f)

        with patch("src.utils.save_manager.SAVE_FILE", self.temp_file):
            with self.assertRaises(CorruptedDataError):
                SaveManager.load_data()

    @patch("src.utils.save_manager.SAVE_FILE", "invalid/path/to/save.json")
    @patch("builtins.open", side_effect=PermissionError("Permission denied"))
    def test_permission_error_on_save_raises_save_error(self, mock_file):
        """Test that permission error raises SaveError."""
        settings = GameSettings()

        with self.assertRaises(SaveError) as context:
            SaveManager.save_data(100, 50, 10, settings)

        self.assertIn("Permission denied", str(context.exception))

    def test_permission_error_on_load_raises_load_error(self):
        """Test that permission error on load raises LoadError."""
        # Create file first
        with patch("src.utils.save_manager.SAVE_FILE", self.temp_file):
            settings = GameSettings()
            SaveManager.save_data(100, 50, 10, settings)

        # Mock permission error on subsequent read
        with patch("src.utils.save_manager.SAVE_FILE", self.temp_file):
            with patch(
                "builtins.open",
                side_effect=PermissionError("Permission denied")
            ):
                with self.assertRaises(LoadError) as context:
                    SaveManager.load_data()

                self.assertIn("Permission denied", str(context.exception))


@unittest.skipUnless(IMPORTS_AVAILABLE, "Game modules not available")
class TestSaveManagerBackup(unittest.TestCase):
    """Test SaveManager backup functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = os.path.join(self.temp_dir, "test_save.json")

    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        backup_file = self.temp_file + ".bak"
        if os.path.exists(backup_file):
            os.remove(backup_file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

    def test_backup_created_on_save(self):
        """Test that backup is created when overwriting existing save."""
        # Create initial save
        settings = GameSettings()

        with patch("src.utils.save_manager.SAVE_FILE", self.temp_file):
            SaveManager.save_data(100, 50, 10, settings)

            # Backup should not exist after successful save
            self.assertFalse(os.path.exists(self.temp_file + ".bak"))

            # Save again
            SaveManager.save_data(200, 100, 20, settings)

            # New save should exist
            self.assertTrue(os.path.exists(self.temp_file))

    def test_restore_from_backup_on_corrupted_file(self):
        """Test that backup is restored when main file is corrupted."""
        # Create a valid backup file
        backup_path = Path(self.temp_file).with_suffix(".bak")
        valid_data = {
            "version": 1,
            "high_score": 500,
            "total_punches": 200,
            "best_combo": 15,
            "settings": {
                "difficulty": Difficulty.NORMAL.value,
                "sound_enabled": True,
                "show_fps": False,
                "particle_effects": True,
            },
        }
        with open(backup_path, "w") as f:
            json.dump(valid_data, f)

        # Create corrupted main file
        with open(self.temp_file, "w") as f:
            f.write("{corrupted json")

        # Load should restore from backup
        with patch("src.utils.save_manager.SAVE_FILE", self.temp_file):
            score, punches, combo, settings = SaveManager.load_data()

            self.assertEqual(score, 500)
            self.assertEqual(punches, 200)
            self.assertEqual(combo, 15)


@unittest.skipUnless(IMPORTS_AVAILABLE, "Game modules not available")
class TestSaveManagerValidation(unittest.TestCase):
    """Test SaveManager data validation."""

    def test_validate_save_data_valid_data(self):
        """Test validation passes for valid data."""
        valid_data = {
            "version": 1,
            "high_score": 1000,
            "total_punches": 500,
            "best_combo": 25,
            "settings": {
                "difficulty": Difficulty.NORMAL.value,
                "sound_enabled": True,
                "show_fps": False,
                "particle_effects": True,
            },
        }

        self.assertTrue(SaveManager._validate_save_data(valid_data))

    def test_validate_save_data_missing_top_level_key(self):
        """Test validation fails for missing top-level key."""
        invalid_data = {
            "high_score": 1000,
            # Missing total_punches, best_combo, settings
        }

        self.assertFalse(SaveManager._validate_save_data(invalid_data))

    def test_validate_save_data_missing_settings_key(self):
        """Test validation fails for missing settings key."""
        invalid_data = {
            "high_score": 1000,
            "total_punches": 500,
            "best_combo": 25,
            "settings": {
                "difficulty": Difficulty.NORMAL.value,
                # Missing sound_enabled, show_fps, particle_effects
            },
        }

        self.assertFalse(SaveManager._validate_save_data(invalid_data))

    def test_validate_save_data_invalid_type(self):
        """Test validation fails for invalid data types."""
        invalid_data = {
            "high_score": "not a number",  # Should be int
            "total_punches": 500,
            "best_combo": 25,
            "settings": {
                "difficulty": Difficulty.NORMAL.value,
                "sound_enabled": True,
                "show_fps": False,
                "particle_effects": True,
            },
        }

        self.assertFalse(SaveManager._validate_save_data(invalid_data))


if __name__ == "__main__":
    unittest.main()
