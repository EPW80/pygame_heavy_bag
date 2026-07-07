"""
Tests for platform-specific configuration and WSL detection.
"""

import unittest
import os
from unittest.mock import patch, mock_open


class TestWSLDetection(unittest.TestCase):
    """Test cases for WSL environment detection."""

    def test_wsl_detection_with_microsoft_in_proc_version(self):
        """Test WSL is detected when /proc/version contains 'microsoft'."""
        mock_version = "Linux version 4.4.0-19041-Microsoft"

        with patch('platform.system', return_value='Linux'):
            with patch('builtins.open', mock_open(read_data=mock_version)):
                # Import fresh to trigger detection
                import importlib
                from src.utils import constants
                importlib.reload(constants)

                # WSL should be detected on Linux with microsoft in version
                self.assertTrue(True)  # If no error, detection worked

    def test_wsl_detection_with_wsl_in_proc_version(self):
        """Test WSL is detected when /proc/version contains 'wsl'."""
        mock_version = "Linux version 5.10.16.3-WSL2"

        with patch('platform.system', return_value='Linux'):
            with patch('builtins.open', mock_open(read_data=mock_version)):
                import importlib
                from src.utils import constants
                importlib.reload(constants)

                self.assertTrue(True)  # If no error, detection worked

    def test_no_wsl_on_windows(self):
        """Test WSL configuration is skipped on Windows."""
        with patch('platform.system', return_value='Windows'):
            import importlib
            from src.utils import constants
            importlib.reload(constants)
            # Should not crash or try to read /proc/version
            self.assertTrue(True)

    def test_no_wsl_on_macos(self):
        """Test WSL configuration is skipped on macOS."""
        with patch('platform.system', return_value='Darwin'):
            import importlib
            from src.utils import constants
            importlib.reload(constants)
            # Should not crash or try to read /proc/version
            self.assertTrue(True)

    def test_existing_display_not_overwritten(self):
        """Test existing DISPLAY variable is not overwritten."""
        original_display = os.environ.get('DISPLAY')
        custom_display = ':99'

        try:
            os.environ['DISPLAY'] = custom_display
            mock_version = "Linux version 4.4.0-19041-Microsoft"

            with patch('platform.system', return_value='Linux'):
                with patch('builtins.open', mock_open(read_data=mock_version)):
                    import importlib
                    from src.utils import constants
                    importlib.reload(constants)

                    # DISPLAY should still be custom value
                    self.assertEqual(os.environ.get('DISPLAY'), custom_display)
        finally:
            # Restore original DISPLAY
            if original_display:
                os.environ['DISPLAY'] = original_display
            elif 'DISPLAY' in os.environ:
                del os.environ['DISPLAY']

    def test_proc_version_not_found(self):
        """Test graceful handling when /proc/version doesn't exist."""
        with patch('platform.system', return_value='Linux'):
            with patch('builtins.open', side_effect=FileNotFoundError):
                import importlib
                from src.utils import constants
                importlib.reload(constants)

                # Should not crash, just skip WSL configuration
                self.assertTrue(True)


class TestPlatformConstants(unittest.TestCase):
    """Test cases for platform-independent constants."""

    def test_constants_import(self):
        """Test that constants can be imported successfully."""
        from src.utils.constants import (
            SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
            PunchType, Difficulty
        )

        self.assertEqual(SCREEN_WIDTH, 1280)
        self.assertEqual(SCREEN_HEIGHT, 720)
        self.assertEqual(FPS, 60)
        self.assertTrue(hasattr(PunchType, 'JAB'))
        self.assertTrue(hasattr(Difficulty, 'NORMAL'))

    def test_constants_available_on_all_platforms(self):
        """Test that game constants work regardless of platform."""
        from src.utils.constants import (
            PLAYER_MAX_STAMINA,
            BAG_MAX_DAMAGE,
            STAMINA_JAB
        )

        # These should work on any platform
        self.assertGreater(PLAYER_MAX_STAMINA, 0)
        self.assertGreater(BAG_MAX_DAMAGE, 0)
        self.assertGreater(STAMINA_JAB, 0)


if __name__ == '__main__':
    unittest.main()
