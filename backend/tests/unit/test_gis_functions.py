"""
Unit tests for app.gis.functions module.

Tests all GIS analysis functions including vector and raster operations.
"""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from app.gis.functions import (
    DISTANCE_NODATA,
    SCORED_NODATA,
    Reclassify_NODATA,
    RPL_Apply_mask,
    RPL_Buffer_analysis,
    RPL_Clip_analysis,
    RPL_Combine_rasters,
    RPL_DistanceAccumulation,
    RPL_ExtractByMask,
    RPL_PolygonToRaster_conversion,
    RPL_Reclassify,
    RPL_Select_analysis,
    RPL_Union_analysis,
    gen_bounding_box,
)


class TestConstants:
    """Test module constants."""

    def test_constants_values(self):
        """Test that constants have expected values."""
        assert DISTANCE_NODATA == -9999
        assert Reclassify_NODATA == 255
        assert SCORED_NODATA == 255


class TestRPLSelectAnalysis:
    """Test RPL_Select_analysis function."""

    @patch("app.gis.functions.gpd.read_file")
    def test_select_analysis_basic(self, mock_read_file):
        """Test basic feature selection functionality."""
        # Mock geodataframe
        mock_gdf = MagicMock()
        mock_selected_gdf = MagicMock()
        mock_gdf.query.return_value = mock_selected_gdf
        mock_read_file.return_value = mock_gdf

        # Test function call
        RPL_Select_analysis("input.shp", "output.shp", "TA2025_V1_ == '001'")

        # Verify calls
        mock_read_file.assert_called_once_with("input.shp")
        mock_gdf.query.assert_called_once_with("TA2025_V1_ == '001'")
        mock_selected_gdf.to_file.assert_called_once_with("output.shp")

    @patch("app.gis.functions.gpd.read_file")
    def test_select_analysis_complex_expression(self, mock_read_file):
        """Test feature selection with complex expression."""
        mock_gdf = MagicMock()
        mock_selected_gdf = MagicMock()
        mock_gdf.query.return_value = mock_selected_gdf
        mock_read_file.return_value = mock_gdf

        complex_expr = "population > 1000 and area < 500"
        RPL_Select_analysis("input.shp", "output.shp", complex_expr)

        mock_gdf.query.assert_called_once_with(complex_expr)


class TestGenBoundingBox:
    """Test gen_bounding_box function."""

    @patch("app.gis.functions.gpd.read_file")
    @patch("app.gis.functions.gpd.GeoDataFrame")
    @patch("app.gis.functions.box")
    def test_gen_bounding_box(self, mock_box, mock_geodataframe, mock_read_file):
        """Test bounding box generation."""
        # Mock input geodataframe
        mock_gdf = MagicMock()
        mock_gdf.total_bounds = [10.0, 20.0, 30.0, 40.0]  # minx, miny, maxx, maxy
        mock_gdf.crs = "EPSG:4326"
        mock_read_file.return_value = mock_gdf

        # Mock box geometry
        mock_bbox_geom = MagicMock()
        mock_box.return_value = mock_bbox_geom

        # Mock output geodataframe
        mock_bbox_gdf = MagicMock()
        mock_geodataframe.return_value = mock_bbox_gdf

        # Test function call
        gen_bounding_box("input.shp", "output.shp")

        # Verify calls
        mock_read_file.assert_called_once_with("input.shp")
        mock_box.assert_called_once_with(10.0, 20.0, 30.0, 40.0)
        mock_geodataframe.assert_called_once_with({"geometry": [mock_bbox_geom]}, crs="EPSG:4326")
        mock_bbox_gdf.to_file.assert_called_once_with("output.shp")


class TestRPLClipAnalysis:
    """Test RPL_Clip_analysis function."""

    @patch("app.gis.functions.gpd.read_file")
    @patch("app.gis.functions.gpd.clip")
    def test_clip_analysis(self, mock_clip, mock_read_file):
        """Test clipping functionality."""
        # Mock geodataframes
        mock_whole_area_gdf = MagicMock()
        mock_boundary_gdf = MagicMock()
        mock_clipped_gdf = MagicMock()

        mock_read_file.side_effect = [mock_whole_area_gdf, mock_boundary_gdf]
        mock_clip.return_value = mock_clipped_gdf

        # Test function call
        RPL_Clip_analysis("output.shp", "whole_area.shp", "boundary.shp")

        # Verify calls
        assert mock_read_file.call_count == 2
        mock_read_file.assert_any_call("whole_area.shp")
        mock_read_file.assert_any_call("boundary.shp")
        mock_clip.assert_called_once_with(mock_whole_area_gdf, mock_boundary_gdf)
        mock_clipped_gdf.to_file.assert_called_once_with("output.shp")


class TestRPLBufferAnalysis:
    """Test RPL_Buffer_analysis function."""

    @patch("app.gis.functions.gpd.read_file")
    def test_buffer_analysis(self, mock_read_file):
        """Test buffer creation functionality."""
        # Mock geodataframe
        mock_gdf = MagicMock()
        mock_buffered_gdf = MagicMock()
        mock_gdf.buffer.return_value = mock_buffered_gdf
        mock_read_file.return_value = mock_gdf

        # Test function call
        buffer_distance = 100.0
        RPL_Buffer_analysis("input.shp", "output.shp", buffer_distance)

        # Verify calls
        mock_read_file.assert_called_once_with("input.shp")
        mock_gdf.buffer.assert_called_once_with(distance=buffer_distance)
        mock_buffered_gdf.to_file.assert_called_once_with("output.shp")


class TestRPLUnionAnalysis:
    """Test RPL_Union_analysis function."""

    @patch("app.gis.functions.gpd.read_file")
    @patch("app.gis.functions.gpd.GeoSeries")
    @patch("app.gis.functions.pd.concat")
    def test_union_analysis(self, mock_concat, mock_geoseries_class, mock_read_file):
        """Test union functionality with multiple shapefiles."""
        # Mock geodataframes and geometries
        mock_gdf1 = MagicMock()
        mock_gdf2 = MagicMock()
        mock_geom1 = MagicMock()
        mock_geom2 = MagicMock()
        mock_gdf1.geometry = mock_geom1
        mock_gdf2.geometry = mock_geom2
        mock_geom1.crs = "EPSG:4326"

        mock_read_file.side_effect = [mock_gdf1, mock_gdf2]

        # Mock pandas concat
        mock_concat_result = MagicMock()
        mock_concat.return_value = mock_concat_result

        # Mock GeoSeries instances
        mock_gs_all = MagicMock()
        mock_unioned_geom = MagicMock()
        mock_gs_all.union_all.return_value = mock_unioned_geom
        mock_gs_all.crs = "EPSG:4326"

        mock_unioned_gs = MagicMock()
        mock_geoseries_class.side_effect = [mock_gs_all, mock_unioned_gs]

        # Test function call
        inputs = ["input1.shp", "input2.shp"]
        RPL_Union_analysis(inputs, "output.shp")

        # Verify calls
        assert mock_read_file.call_count == 2
        mock_concat.assert_called_once_with([mock_geom1, mock_geom2], ignore_index=True)
        mock_gs_all.union_all.assert_called_once()
        mock_unioned_gs.to_file.assert_called_once_with("output.shp")


class TestRPLExtractByMask:
    """Test RPL_ExtractByMask function."""

    @patch("app.gis.functions.gpd.read_file")
    @patch("app.gis.functions.rasterio.open")
    @patch("app.gis.functions.mask")
    def test_extract_by_mask(self, mock_mask_func, mock_rasterio_open, mock_read_file):
        """Test raster extraction by mask."""
        # Mock shapefile
        mock_gdf = MagicMock()
        mock_geometries = [MagicMock(), MagicMock()]
        mock_gdf.geometry.values = mock_geometries
        mock_read_file.return_value = mock_gdf

        # Mock rasterio source
        mock_src = MagicMock()
        mock_src.meta = {"driver": "GTiff", "height": 100, "width": 100}
        mock_src.nodata = -9999

        # Mock mask function result
        mock_out_image = np.array([[[1, 2, 3], [4, 5, 6]]])
        mock_out_transform = MagicMock()
        mock_mask_func.return_value = (mock_out_image, mock_out_transform)

        # Mock destination
        mock_dest = MagicMock()

        # Setup rasterio.open context manager behavior
        src_context = MagicMock()
        src_context.__enter__ = lambda x: mock_src
        src_context.__exit__ = lambda x, y, z, w: None

        dest_context = MagicMock()
        dest_context.__enter__ = lambda x: mock_dest
        dest_context.__exit__ = lambda x, y, z, w: None

        mock_rasterio_open.side_effect = [src_context, dest_context]

        # Test function call
        RPL_ExtractByMask("input.tif", "mask.shp", "output.tif")

        # Verify calls
        mock_read_file.assert_called_once_with("mask.shp")
        # Don't check exact mock object reference, just that mask was called with correct arguments
        assert mock_mask_func.call_count == 1
        args, kwargs = mock_mask_func.call_args
        assert len(args) == 2
        assert args[1] == mock_geometries
        assert kwargs == {"crop": True}


class TestRPLPolygonToRasterConversion:
    """Test RPL_PolygonToRaster_conversion function."""

    @patch("app.gis.functions.gpd.read_file")
    @patch("app.gis.functions.rasterio.open")
    @patch("app.gis.functions.rasterio.features.rasterize")
    def test_polygon_to_raster_conversion(self, mock_rasterize, mock_rasterio_open, mock_read_file):
        """Test polygon to raster conversion."""
        # Mock shapefile
        mock_gdf = MagicMock()
        mock_geom1 = MagicMock()
        mock_geom2 = MagicMock()
        mock_gdf.geometry = [mock_geom1, mock_geom2]
        mock_read_file.return_value = mock_gdf

        # Mock template raster
        mock_template_src = MagicMock()
        mock_template_src.transform = MagicMock()
        mock_template_src.height = 100
        mock_template_src.width = 100
        mock_template_src.crs = "EPSG:4326"
        mock_template_src.nodata = 255  # Use uint8 compatible nodata
        mock_template_data = np.array([[1, 2, 255], [4, 5, 6]], dtype="uint8")
        mock_template_src.read.return_value = mock_template_data

        # Mock rasterize result
        mock_rasterized = np.array([[1, 1, 0], [0, 1, 1]], dtype="uint8")
        mock_rasterize.return_value = mock_rasterized

        # Mock destination
        mock_dest = MagicMock()

        # Setup rasterio.open context manager behavior
        mock_rasterio_open.side_effect = [
            MagicMock(__enter__=lambda x: mock_template_src, __exit__=lambda x, y, z, w: None),
            MagicMock(__enter__=lambda x: mock_dest, __exit__=lambda x, y, z, w: None),
        ]

        # Test function call
        RPL_PolygonToRaster_conversion("input.shp", "output.tif", "template.tif")

        # Verify calls
        mock_read_file.assert_called_once_with("input.shp")
        mock_rasterize.assert_called_once()
        mock_dest.write.assert_called_once()


class TestRPLDistanceAccumulation:
    """Test RPL_DistanceAccumulation function."""

    @patch("app.gis.functions.rasterio.open")
    @patch("app.gis.functions.distance_transform_edt")
    def test_distance_accumulation(self, mock_distance_transform, mock_rasterio_open):
        """Test euclidean distance accumulation."""
        # Mock source raster
        mock_src = MagicMock()
        mock_raster_data = np.array([[1, 0, 0], [0, 1, 0], [0, 0, -9999]], dtype="int16")
        mock_src.read.return_value = mock_raster_data
        mock_src.nodata = -9999
        # Create a proper transform mock with .a attribute
        mock_transform = MagicMock()
        mock_transform.a = 30.0  # 30m pixel size
        mock_src.transform = mock_transform
        mock_src.height = 3
        mock_src.width = 3
        mock_src.crs = "EPSG:32633"

        # Mock distance transform result
        mock_distance = np.array([[0.0, 1.0, 2.0], [1.0, 0.0, 1.0], [2.0, 1.0, 0.0]])
        mock_distance_transform.return_value = mock_distance

        # Mock destination
        mock_dest = MagicMock()

        # Setup rasterio.open context manager behavior
        mock_rasterio_open.side_effect = [
            MagicMock(__enter__=lambda x: mock_src, __exit__=lambda x, y, z, w: None),
            MagicMock(__enter__=lambda x: mock_dest, __exit__=lambda x, y, z, w: None),
        ]

        # Test function call
        RPL_DistanceAccumulation("input.tif", "output.tif")

        # Verify calls
        mock_distance_transform.assert_called_once()
        mock_dest.write.assert_called_once()

    @patch("app.gis.functions.rasterio.open")
    @patch("app.gis.functions.distance_transform_edt")
    def test_distance_accumulation_no_nodata(self, mock_distance_transform, mock_rasterio_open):
        """Test euclidean distance accumulation when nodata is None."""
        # Mock source raster without nodata
        mock_src = MagicMock()
        mock_raster_data = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype="int16")
        mock_src.read.return_value = mock_raster_data
        mock_src.nodata = None  # No nodata value
        # Create a proper transform mock with .a attribute
        mock_transform = MagicMock()
        mock_transform.a = 30.0  # 30m pixel size
        mock_src.transform = mock_transform
        mock_src.height = 3
        mock_src.width = 3
        mock_src.crs = "EPSG:32633"

        # Mock distance transform result
        mock_distance = np.array([[0.0, 1.0, 2.0], [1.0, 0.0, 1.0], [2.0, 1.0, 0.0]])
        mock_distance_transform.return_value = mock_distance

        # Mock destination
        mock_dest = MagicMock()

        # Setup rasterio.open context manager behavior
        mock_rasterio_open.side_effect = [
            MagicMock(__enter__=lambda x: mock_src, __exit__=lambda x, y, z, w: None),
            MagicMock(__enter__=lambda x: mock_dest, __exit__=lambda x, y, z, w: None),
        ]

        # Test function call
        RPL_DistanceAccumulation("input.tif", "output.tif")

        # Verify calls
        mock_distance_transform.assert_called_once()
        mock_dest.write.assert_called_once()


class TestRPLReclassify:
    """Test RPL_Reclassify function."""

    @patch("app.gis.functions.rasterio.open")
    def test_reclassify_basic(self, mock_rasterio_open):
        """Test basic reclassification functionality."""
        # Mock source raster
        mock_src = MagicMock()
        mock_data = np.array([[1, 3, 7], [12, 18, 25]], dtype="float32")
        mock_src.read.return_value = mock_data
        mock_src.nodata = -9999
        mock_src.height = 2
        mock_src.width = 3
        mock_src.crs = "EPSG:4326"
        mock_src.transform = MagicMock()
        mock_src.meta = {"driver": "GTiff"}

        # Mock destination
        mock_dest = MagicMock()

        # Setup rasterio.open context manager behavior
        mock_rasterio_open.side_effect = [
            MagicMock(__enter__=lambda x: mock_src, __exit__=lambda x, y, z, w: None),
            MagicMock(__enter__=lambda x: mock_dest, __exit__=lambda x, y, z, w: None),
        ]

        # Test remap range
        remap_range = [(0, 5, 10), (5, 10, 8), (10, 15, 5), (15, 30, 2)]

        # Test function call
        RPL_Reclassify("input.tif", "output.tif", remap_range)

        # Verify calls
        mock_dest.write.assert_called_once()

    @patch("app.gis.functions.rasterio.open")
    def test_reclassify_with_nodata(self, mock_rasterio_open):
        """Test reclassification with nodata values."""
        mock_src = MagicMock()
        mock_data = np.array([[1, -9999, 7], [12, 18, -9999]], dtype="float32")
        mock_src.read.return_value = mock_data
        mock_src.nodata = -9999
        mock_src.height = 2
        mock_src.width = 3
        mock_src.crs = "EPSG:4326"
        mock_src.transform = MagicMock()
        mock_src.meta = {"driver": "GTiff"}

        mock_dest = MagicMock()

        mock_rasterio_open.side_effect = [
            MagicMock(__enter__=lambda x: mock_src, __exit__=lambda x, y, z, w: None),
            MagicMock(__enter__=lambda x: mock_dest, __exit__=lambda x, y, z, w: None),
        ]

        remap_range = [(0, 20, 5), (20, 30, 2)]

        RPL_Reclassify("input.tif", "output.tif", remap_range)

        mock_dest.write.assert_called_once()

    @patch("app.gis.functions.rasterio.open")
    def test_reclassify_range_validation_error(self, mock_rasterio_open):
        """Test reclassification with invalid remap range."""
        mock_src = MagicMock()
        mock_data = np.array([[1, 3, 7], [12, 18, 25]], dtype="float32")
        mock_src.read.return_value = mock_data
        mock_src.nodata = None

        mock_rasterio_open.return_value.__enter__.return_value = mock_src

        # Remap range that doesn't cover data range
        remap_range = [(10, 20, 5)]  # Data has values 1-25, but range only covers 10-20

        with pytest.raises(ValueError, match="Remap range does not cover the data range"):
            RPL_Reclassify("input.tif", "output.tif", remap_range)


class TestRPLCombineRasters:
    """Test RPL_Combine_rasters function."""

    @patch("app.gis.functions.rasterio.open")
    def test_combine_rasters(self, mock_rasterio_open):
        """Test combining multiple rasters with weights."""
        # Mock first raster
        mock_src1 = MagicMock()
        mock_data1 = np.array([[10, 20], [30, 40]], dtype="uint8")
        mock_src1.read.return_value = mock_data1
        mock_src1.nodata = 255
        mock_src1.meta = {
            "driver": "GTiff",
            "height": 2,
            "width": 2,
            "crs": "EPSG:4326",
            "transform": MagicMock(),
        }

        # Mock second raster
        mock_src2 = MagicMock()
        mock_data2 = np.array([[5, 15], [25, 35]], dtype="uint8")
        mock_src2.read.return_value = mock_data2
        mock_src2.nodata = 255

        # Mock destination
        mock_dest = MagicMock()

        # Setup rasterio.open context manager behavior
        mock_rasterio_open.side_effect = [
            MagicMock(__enter__=lambda x: mock_src1, __exit__=lambda x, y, z, w: None),
            MagicMock(__enter__=lambda x: mock_src2, __exit__=lambda x, y, z, w: None),
            MagicMock(__enter__=lambda x: mock_dest, __exit__=lambda x, y, z, w: None),
        ]

        # Test input with weights
        inputs = [("raster1.tif", 0.6), ("raster2.tif", 0.4)]

        # Test function call
        RPL_Combine_rasters(inputs, "output.tif")

        # Verify calls
        mock_dest.write.assert_called_once()


class TestRPLApplyMask:
    """Test RPL_Apply_mask function."""

    @patch("app.gis.functions.rasterio.open")
    def test_apply_mask_basic(self, mock_rasterio_open):
        """Test applying binary mask to raster."""
        # Mock value raster
        mock_value_src = MagicMock()
        mock_value_data = np.array([[10, 20, 30], [40, 50, 60]], dtype="uint8")
        mock_value_src.read.return_value = mock_value_data
        mock_value_src.shape = (2, 3)
        mock_value_src.crs = "EPSG:4326"
        mock_value_src.nodata = 255
        mock_value_src.meta = {
            "driver": "GTiff",
            "height": 2,
            "width": 3,
            "crs": "EPSG:4326",
            "transform": MagicMock(),
        }

        # Mock mask raster
        mock_mask_src = MagicMock()
        mock_mask_data = np.array([[0, 1, 0], [1, 0, 1]], dtype="uint8")
        mock_mask_src.read.return_value = mock_mask_data
        mock_mask_src.shape = (2, 3)
        mock_mask_src.crs = "EPSG:4326"

        # Mock destination
        mock_dest = MagicMock()

        # Setup rasterio.open context manager behavior for multiple calls
        value_context = MagicMock()
        value_context.__enter__ = lambda x: mock_value_src
        value_context.__exit__ = lambda x, y, z, w: None

        mask_context = MagicMock()
        mask_context.__enter__ = lambda x: mock_mask_src
        mask_context.__exit__ = lambda x, y, z, w: None

        dest_context = MagicMock()
        dest_context.__enter__ = lambda x: mock_dest
        dest_context.__exit__ = lambda x, y, z, w: None

        mock_rasterio_open.side_effect = [value_context, mask_context, dest_context]

        # Test function call
        RPL_Apply_mask("value.tif", "mask.tif", "output.tif")

        # Verify calls
        assert mock_rasterio_open.call_count == 3
        mock_dest.write.assert_called_once()

    def test_apply_mask_shape_mismatch(self):
        """Test error when rasters have different shapes."""
        with patch("app.gis.functions.rasterio.open") as mock_rasterio_open:
            # Mock value raster
            mock_value_src = MagicMock()
            mock_value_src.shape = (2, 3)
            mock_value_src.crs = "EPSG:4326"

            # Mock mask raster with different shape
            mock_mask_src = MagicMock()
            mock_mask_src.shape = (3, 2)  # Different shape
            mock_mask_src.crs = "EPSG:4326"

            value_context = MagicMock()
            value_context.__enter__ = lambda x: mock_value_src
            value_context.__exit__ = lambda x, y, z, w: None

            mask_context = MagicMock()
            mask_context.__enter__ = lambda x: mock_mask_src
            mask_context.__exit__ = lambda x, y, z, w: None

            mock_rasterio_open.side_effect = [value_context, mask_context]

            with pytest.raises(ValueError, match="Input rasters must have the same shape"):
                RPL_Apply_mask("value.tif", "mask.tif", "output.tif")

    def test_apply_mask_crs_mismatch(self):
        """Test error when rasters have different CRS."""
        with patch("app.gis.functions.rasterio.open") as mock_rasterio_open:
            # Mock value raster
            mock_value_src = MagicMock()
            mock_value_src.shape = (2, 3)
            mock_value_src.crs = "EPSG:4326"

            # Mock mask raster with different CRS
            mock_mask_src = MagicMock()
            mock_mask_src.shape = (2, 3)
            mock_mask_src.crs = "EPSG:32633"  # Different CRS

            value_context = MagicMock()
            value_context.__enter__ = lambda x: mock_value_src
            value_context.__exit__ = lambda x, y, z, w: None

            mask_context = MagicMock()
            mask_context.__enter__ = lambda x: mock_mask_src
            mask_context.__exit__ = lambda x, y, z, w: None

            mock_rasterio_open.side_effect = [value_context, mask_context]

            with pytest.raises(ValueError, match="Input rasters must have the same CRS"):
                RPL_Apply_mask("value.tif", "mask.tif", "output.tif")


class TestEdgeCases:
    """Test edge cases and error conditions."""

    @patch("app.gis.functions.gpd.read_file")
    def test_empty_shapefile(self, mock_read_file):
        """Test handling of empty shapefiles."""
        # Mock empty geodataframe
        mock_gdf = MagicMock()
        mock_gdf.query.return_value = MagicMock()  # Empty result
        mock_read_file.return_value = mock_gdf

        # Should not raise an error
        RPL_Select_analysis("empty.shp", "output.shp", "field == 'value'")

        mock_gdf.query.assert_called_once_with("field == 'value'")

    @patch("app.gis.functions.rasterio.open")
    def test_raster_with_all_nodata(self, mock_rasterio_open):
        """Test handling raster with all nodata values."""
        mock_src = MagicMock()
        mock_data = np.full((3, 3), -9999, dtype="int16")
        mock_src.read.return_value = mock_data
        mock_src.nodata = -9999

        mock_dest = MagicMock()

        mock_rasterio_open.side_effect = [
            MagicMock(__enter__=lambda x: mock_src, __exit__=lambda x, y, z, w: None),
            MagicMock(__enter__=lambda x: mock_dest, __exit__=lambda x, y, z, w: None),
        ]

        # This should handle the all-nodata case gracefully
        with patch("app.gis.functions.distance_transform_edt") as mock_distance_transform:
            mock_distance_transform.return_value = np.zeros((3, 3))
            mock_src.height = 3
            mock_src.width = 3
            mock_src.crs = "EPSG:32633"
            # Create a proper transform mock with .a attribute
            mock_transform = MagicMock()
            mock_transform.a = 30.0
            mock_src.transform = mock_transform

            RPL_DistanceAccumulation("input.tif", "output.tif")

            mock_dest.write.assert_called_once()


# Integration-style tests with realistic data patterns
class TestIntegrationPatterns:
    """Test functions with more realistic data patterns."""

    @patch("app.gis.functions.gpd.read_file")
    def test_buffer_with_realistic_distance(self, mock_read_file):
        """Test buffer analysis with realistic distance values."""
        mock_gdf = MagicMock()
        mock_buffered = MagicMock()
        mock_gdf.buffer.return_value = mock_buffered
        mock_read_file.return_value = mock_gdf

        # Test with different realistic buffer distances
        distances = [10.0, 100.0, 1000.0, 0.001]  # meters, various scales

        for distance in distances:
            RPL_Buffer_analysis("input.shp", f"output_{distance}.shp", distance)
            mock_gdf.buffer.assert_called_with(distance=distance)

    @patch("app.gis.functions.rasterio.open")
    def test_reclassify_with_realistic_ranges(self, mock_rasterio_open):
        """Test reclassification with realistic value ranges."""
        mock_src = MagicMock()
        # Realistic elevation data
        mock_data = np.array([[850, 920, 1150], [1300, 1520, 1800]], dtype="float32")
        mock_src.read.return_value = mock_data
        mock_src.nodata = -9999
        mock_src.height = 2
        mock_src.width = 3
        mock_src.crs = "EPSG:32633"
        mock_src.transform = MagicMock()
        mock_src.meta = {"driver": "GTiff"}

        mock_dest = MagicMock()

        mock_rasterio_open.side_effect = [
            MagicMock(__enter__=lambda x: mock_src, __exit__=lambda x, y, z, w: None),
            MagicMock(__enter__=lambda x: mock_dest, __exit__=lambda x, y, z, w: None),
        ]

        # Realistic elevation classification
        elevation_classes = [
            (0, 1000, 1),  # Low elevation
            (1000, 1500, 2),  # Medium elevation
            (1500, 3000, 3),  # High elevation
        ]

        RPL_Reclassify("elevation.tif", "classified.tif", elevation_classes)

        mock_dest.write.assert_called_once()
