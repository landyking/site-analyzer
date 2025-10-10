"""
Unit tests for app.utils.consts module.

Tests utility constants and helper functions.
"""

from app.utils.consts import test_content


class TestUtilsConsts:
    """Test utility constants and functions."""

    def test_test_content_exists(self):
        """Test that test_content constant exists and is a string."""
        assert test_content is not None
        assert isinstance(test_content, str)
        assert len(test_content) > 0

    def test_test_content_value(self):
        """Test the specific value of test_content."""
        expected_content = "Hello world. From the backend app utils consts.py file."
        assert test_content == expected_content

    def test_test_content_format(self):
        """Test that test_content has expected format."""
        # Should contain greeting
        assert "Hello world" in test_content

        # Should contain file path reference
        assert "backend app utils consts.py" in test_content

        # Should end with period
        assert test_content.endswith(".")

        # Should not be empty or just whitespace
        assert test_content.strip() != ""
