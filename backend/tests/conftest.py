"""
Test configuration and fixtures for the test suite.
"""
import os
import sys
import pytest
from unittest.mock import Mock
from datetime import datetime, timezone, timedelta

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    from unittest.mock import patch, MagicMock
    
    settings_mock = MagicMock()
    settings_mock.SECRET_KEY = "test-secret-key-for-testing-only"
    settings_mock.ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    with patch('app.core.security.settings', settings_mock):
        yield settings_mock


@pytest.fixture
def sample_datetime():
    """Sample datetime for testing."""
    return datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def mock_raster_data():
    """Mock raster data for GIS testing."""
    import numpy as np
    return {
        'data': np.array([[1, 2, 3], [4, -9999, 6], [7, 8, 9]]),
        'nodata': -9999,
        'min_value': 1,
        'max_value': 9
    }


@pytest.fixture
def temp_shapefile_path(tmp_path):
    """Create a temporary shapefile path for testing."""
    return str(tmp_path / "test.shp")


@pytest.fixture
def temp_raster_path(tmp_path):
    """Create a temporary raster path for testing."""
    return str(tmp_path / "test.tif")