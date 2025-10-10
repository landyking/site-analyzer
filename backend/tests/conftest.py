"""
Test configuration and fixtures for the test suite.
"""

import os
import sys
from datetime import UTC, datetime

import pytest

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    from unittest.mock import MagicMock, patch

    settings_mock = MagicMock()
    settings_mock.SECRET_KEY = "test-secret-key-for-testing-only"
    settings_mock.ACCESS_TOKEN_EXPIRE_MINUTES = 30

    with patch("app.core.security.settings", settings_mock):
        yield settings_mock


@pytest.fixture
def sample_datetime():
    """Sample datetime for testing."""
    return datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)


@pytest.fixture
def mock_raster_data():
    """Mock raster data for GIS testing."""
    import numpy as np

    return {
        "data": np.array([[1, 2, 3], [4, -9999, 6], [7, 8, 9]]),
        "nodata": -9999,
        "min_value": 1,
        "max_value": 9,
    }


@pytest.fixture
def temp_shapefile_path(tmp_path):
    """Create a temporary shapefile path for testing."""
    return str(tmp_path / "test.shp")


@pytest.fixture
def temp_raster_path(tmp_path):
    """Create a temporary raster path for testing."""
    return str(tmp_path / "test.tif")


@pytest.fixture
def sample_geodataframe():
    """Create a sample GeoDataFrame for testing."""
    import geopandas as gpd
    from shapely.geometry import Point, Polygon

    # Create sample geometries
    points = [Point(0, 0), Point(1, 1), Point(2, 2)]
    polygons = [
        Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
        Polygon([(1, 1), (2, 1), (2, 2), (1, 2)]),
        Polygon([(2, 2), (3, 2), (3, 3), (2, 3)]),
    ]

    return gpd.GeoDataFrame(
        {"id": [1, 2, 3], "name": ["A", "B", "C"], "value": [10, 20, 30], "geometry": polygons},
        crs="EPSG:4326",
    )


@pytest.fixture
def sample_raster_metadata():
    """Sample raster metadata for testing."""
    return {
        "driver": "GTiff",
        "dtype": "uint8",
        "nodata": 255,
        "width": 10,
        "height": 10,
        "count": 1,
        "crs": "EPSG:4326",
        "transform": [1.0, 0.0, 0.0, 0.0, -1.0, 10.0],
    }


@pytest.fixture
def mock_transform():
    """Mock rasterio transform for testing."""
    from unittest.mock import MagicMock

    transform = MagicMock()
    transform.a = 30.0  # pixel size
    return transform


@pytest.fixture
def temp_raster_path(tmp_path):
    """Create a temporary raster path for testing."""
    return str(tmp_path / "test.tif")
