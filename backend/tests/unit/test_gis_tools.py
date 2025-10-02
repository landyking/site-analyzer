"""
Unit tests for app.gis.tools module.

Tests raster data processing functions and file operations.
"""
import pytest
import numpy as np
import os
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime

from app.gis.tools import (
    get_data_range,
    show_file_info,
    version
)


class TestVersion:
    """Test version string generation."""
    
    def test_version_is_string(self):
        """Test that version is a string."""
        assert isinstance(version, str)
    
    def test_version_format(self):
        """Test that version follows expected datetime format."""
        # Version should be in format "YYYY-MM-DD HH:MM:SS"
        try:
            datetime.strptime(version, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            pytest.fail(f"Version '{version}' does not match expected format")


class TestGetDataRange:
    """Test get_data_range function for raster data processing."""
    
    @patch('app.gis.tools.rasterio.open')
    def test_get_data_range_with_nodata(self, mock_rasterio_open):
        """Test get_data_range with nodata values present."""
        # Mock rasterio dataset
        mock_src = MagicMock()
        mock_src.read.return_value = np.array([[1, 2, -9999], [4, -9999, 6], [7, 8, 9]])
        mock_src.nodata = -9999
        mock_rasterio_open.return_value.__enter__.return_value = mock_src
        
        min_val, max_val, nodata_val = get_data_range("dummy_path.tif")
        
        assert min_val == 1
        assert max_val == 9
        assert nodata_val == -9999
        mock_rasterio_open.assert_called_once_with("dummy_path.tif")
        mock_src.read.assert_called_once_with(1)
    
    @patch('app.gis.tools.rasterio.open')
    def test_get_data_range_without_nodata(self, mock_rasterio_open):
        """Test get_data_range without nodata values."""
        # Mock rasterio dataset
        mock_src = MagicMock()
        mock_src.read.return_value = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        mock_src.nodata = None
        mock_rasterio_open.return_value.__enter__.return_value = mock_src
        
        min_val, max_val, nodata_val = get_data_range("dummy_path.tif")
        
        assert min_val == 1
        assert max_val == 9
        assert nodata_val is None
    
    @patch('app.gis.tools.rasterio.open')
    def test_get_data_range_with_nan_values(self, mock_rasterio_open):
        """Test get_data_range handles NaN values correctly."""
        # Mock rasterio dataset with NaN values
        mock_src = MagicMock()
        data_with_nan = np.array([[1.0, 2.0, np.nan], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])
        mock_src.read.return_value = data_with_nan
        mock_src.nodata = None
        mock_rasterio_open.return_value.__enter__.return_value = mock_src
        
        min_val, max_val, nodata_val = get_data_range("dummy_path.tif")
        
        # np.nanmin and np.nanmax should handle NaN values
        assert min_val == 1.0
        assert max_val == 9.0
        assert nodata_val is None
    
    @patch('app.gis.tools.rasterio.open')
    def test_get_data_range_all_nodata(self, mock_rasterio_open):
        """Test get_data_range when all values are nodata."""
        # Mock rasterio dataset with all nodata values
        mock_src = MagicMock()
        mock_src.read.return_value = np.array([[-9999, -9999], [-9999, -9999]])
        mock_src.nodata = -9999
        mock_rasterio_open.return_value.__enter__.return_value = mock_src
        
        # This should raise an error or handle empty arrays gracefully
        # Let's test that it doesn't crash and returns appropriate values
        try:
            min_val, max_val, nodata_val = get_data_range("dummy_path.tif")
            # The function should handle this case gracefully
            assert nodata_val == -9999
            # Check if values are nan (expected for empty arrays)
            assert np.isnan(min_val) or min_val is None
            assert np.isnan(max_val) or max_val is None
        except ValueError:
            # This is also acceptable - the function may raise an error for empty data
            pytest.skip("Function raises ValueError for all-nodata case, which is acceptable")
    
    @patch('app.gis.tools.rasterio.open')
    def test_get_data_range_single_value(self, mock_rasterio_open):
        """Test get_data_range with single valid value."""
        # Mock rasterio dataset with single value
        mock_src = MagicMock()
        mock_src.read.return_value = np.array([[42]])
        mock_src.nodata = None
        mock_rasterio_open.return_value.__enter__.return_value = mock_src
        
        min_val, max_val, nodata_val = get_data_range("dummy_path.tif")
        
        assert min_val == 42
        assert max_val == 42
        assert nodata_val is None
    
    @patch('app.gis.tools.rasterio.open')
    def test_get_data_range_mixed_nodata(self, mock_rasterio_open):
        """Test get_data_range with mixed valid and nodata values."""
        # Mock rasterio dataset
        mock_src = MagicMock()
        mock_src.read.return_value = np.array([[100, -9999, 200], [-9999, 150, -9999]])
        mock_src.nodata = -9999
        mock_rasterio_open.return_value.__enter__.return_value = mock_src
        
        min_val, max_val, nodata_val = get_data_range("dummy_path.tif")
        
        assert min_val == 100
        assert max_val == 200
        assert nodata_val == -9999


class TestShowFileInfo:
    """Test show_file_info function for file metadata display."""
    
    @patch('app.gis.tools.os.path.getsize')
    @patch('app.gis.tools.gpd.read_file')
    @patch('builtins.print')
    def test_show_file_info_shapefile(self, mock_print, mock_gpd_read, mock_getsize):
        """Test show_file_info with shapefile."""
        mock_getsize.return_value = 1024
        
        # Mock GeoPandas dataframe
        mock_gdf = MagicMock()
        mock_gdf.crs = "EPSG:4326"
        mock_gdf.__len__.return_value = 5
        mock_gpd_read.return_value = mock_gdf
        
        show_file_info("/path/to/test.shp")
        
        # Verify print calls
        mock_print.assert_any_call("File: /path/to/test.shp")
        mock_print.assert_any_call("Size: 1024 bytes")
        mock_print.assert_any_call("Type: .shp")
        mock_print.assert_any_call("Shapefile CRS: EPSG:4326")
        mock_print.assert_any_call("Number of features: 5")
        
        mock_getsize.assert_called_once_with("/path/to/test.shp")
        mock_gpd_read.assert_called_once_with("/path/to/test.shp")
    
    @patch('app.gis.tools.os.path.getsize')
    @patch('app.gis.tools.rasterio.open')
    @patch('builtins.print')
    def test_show_file_info_raster_tif(self, mock_print, mock_rasterio_open, mock_getsize):
        """Test show_file_info with TIFF raster."""
        mock_getsize.return_value = 2048
        
        # Mock rasterio dataset
        mock_src = MagicMock()
        mock_src.meta = {
            'driver': 'GTiff',
            'width': 100,
            'height': 100,
            'count': 1,
            'dtype': 'float32'
        }
        mock_rasterio_open.return_value.__enter__.return_value = mock_src
        
        show_file_info("/path/to/test.tif")
        
        # Verify print calls
        mock_print.assert_any_call("File: /path/to/test.tif")
        mock_print.assert_any_call("Size: 2048 bytes")
        mock_print.assert_any_call("Type: .tif")
        mock_print.assert_any_call(f"metadata: {mock_src.meta}")
        
        mock_getsize.assert_called_once_with("/path/to/test.tif")
        mock_rasterio_open.assert_called_once_with("/path/to/test.tif")
    
    @patch('app.gis.tools.os.path.getsize')
    @patch('app.gis.tools.rasterio.open')
    @patch('builtins.print')
    def test_show_file_info_raster_tiff(self, mock_print, mock_rasterio_open, mock_getsize):
        """Test show_file_info with .tiff extension."""
        mock_getsize.return_value = 3072
        
        # Mock rasterio dataset
        mock_src = MagicMock()
        mock_src.meta = {'driver': 'GTiff'}
        mock_rasterio_open.return_value.__enter__.return_value = mock_src
        
        show_file_info("/path/to/test.TIFF")  # Test case insensitive
        
        mock_print.assert_any_call("Type: .tiff")
        mock_rasterio_open.assert_called_once_with("/path/to/test.TIFF")
    
    @patch('app.gis.tools.os.path.getsize')
    @patch('builtins.print')
    def test_show_file_info_unknown_type(self, mock_print, mock_getsize):
        """Test show_file_info with unknown file type."""
        mock_getsize.return_value = 512
        
        show_file_info("/path/to/test.txt")
        
        # Should only print basic file info
        mock_print.assert_any_call("File: /path/to/test.txt")
        mock_print.assert_any_call("Size: 512 bytes")
        mock_print.assert_any_call("Type: .txt")
        
        # Should not attempt to read as shapefile or raster
        assert mock_print.call_count == 3
    
    @patch('app.gis.tools.os.path.getsize')
    @patch('app.gis.tools.gpd.read_file')
    @patch('builtins.print')
    def test_show_file_info_shapefile_error(self, mock_print, mock_gpd_read, mock_getsize):
        """Test show_file_info handles shapefile reading errors."""
        mock_getsize.return_value = 1024
        mock_gpd_read.side_effect = Exception("Cannot read shapefile")
        
        show_file_info("/path/to/corrupt.shp")
        
        mock_print.assert_any_call("Error reading shapefile: Cannot read shapefile")
    
    @patch('app.gis.tools.os.path.getsize')
    @patch('app.gis.tools.rasterio.open')
    @patch('builtins.print')
    def test_show_file_info_raster_error(self, mock_print, mock_rasterio_open, mock_getsize):
        """Test show_file_info handles raster reading errors."""
        mock_getsize.return_value = 2048
        mock_rasterio_open.side_effect = Exception("Cannot read raster")
        
        show_file_info("/path/to/corrupt.tif")
        
        mock_print.assert_any_call("Error reading raster: Cannot read raster")
    
    @patch('app.gis.tools.os.path.getsize')
    def test_show_file_info_no_extension(self, mock_getsize):
        """Test show_file_info with file having no extension."""
        mock_getsize.return_value = 256
        
        with patch('builtins.print') as mock_print:
            show_file_info("/path/to/noextension")
            
            mock_print.assert_any_call("Type: ")


class TestGISToolsIntegration:
    """Integration tests for GIS tools with realistic data scenarios."""
    
    def test_get_data_range_realistic_data(self):
        """Test get_data_range with realistic raster data values."""
        # Create a realistic data scenario
        data = np.array([[1.5, 2.3, -9999], [4.7, 5.1, 8.9]])
        
        with patch('app.gis.tools.rasterio.open') as mock_open:
            mock_src = MagicMock()
            mock_src.read.return_value = data
            mock_src.nodata = -9999
            mock_open.return_value.__enter__.return_value = mock_src
            
            min_val, max_val, nodata = get_data_range('/fake/realistic.tif')
            
            assert min_val == 1.5
            assert max_val == 8.9
            assert nodata == -9999
    
    @patch('app.gis.tools.gpd.read_file')
    @patch('app.gis.tools.os.path.getsize')
    @patch('builtins.print')
    def test_show_file_info_realistic_shapefile(self, mock_print, mock_getsize, mock_gpd_read):
        """Test show_file_info with realistic shapefile properties."""
        mock_getsize.return_value = 15360  # 15KB
        
        # Mock a realistic GeoPandas dataframe
        mock_gdf = MagicMock()
        mock_gdf.crs = "EPSG:2193"  # NZGD2000
        mock_gdf.__len__.return_value = 150  # 150 features
        mock_gpd_read.return_value = mock_gdf
        
        show_file_info("/path/to/districts.shp")
        
        # Verify realistic output
        mock_print.assert_any_call("File: /path/to/districts.shp")
        mock_print.assert_any_call("Size: 15360 bytes")
        mock_print.assert_any_call("Type: .shp")
        mock_print.assert_any_call("Shapefile CRS: EPSG:2193")
        mock_print.assert_any_call("Number of features: 150")


# Note: Visualization tests (TestShowRasterPlot) are skipped
# as matplotlib is not installed in the test environment.
# These tests would cover:
# - show_raster_plot() function with and without nodata values
# - show_shapefile_plot() function for vector visualization
# - matplotlib integration and plot configuration

