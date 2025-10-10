"""
Unit tests for app.gis.engine module.

Tests the SiteSuitabilityEngine class including initialization, configuration,
data processing, and site suitability analysis workflow.
"""

import tempfile
from unittest.mock import MagicMock, patch

import pytest

from app.gis.engine import SiteSuitabilityEngine
from app.gis.engine_models import (
    EmptyTaskMonitor,
    EngineConfigs,
    EngineRestrictedFactor,
    EngineSuitabilityFactor,
)


class MockTaskMonitor:
    """Mock task monitor for testing."""

    def __init__(self, cancelled=False):
        self.cancelled = cancelled
        self.progress_calls = []
        self.error_calls = []
        self.file_calls = []

    def is_cancelled(self) -> bool:
        return self.cancelled

    def update_progress(self, percent: int, phase: str = None, description: str = None) -> None:
        self.progress_calls.append((percent, phase, description))

    def record_error(
        self, error_msg: str, phase: str = None, percent: int = None, description: str = None
    ) -> None:
        self.error_calls.append((error_msg, phase, percent, description))

    def record_file(self, file_type: str, file_path: str) -> None:
        self.file_calls.append((file_type, file_path))


@pytest.fixture
def temp_dirs():
    """Create temporary directories for testing."""
    with tempfile.TemporaryDirectory() as data_dir, tempfile.TemporaryDirectory() as output_dir:
        yield data_dir, output_dir


@pytest.fixture
def sample_engine_configs():
    """Create sample engine configurations for testing."""
    return EngineConfigs(
        restricted_factors=[
            EngineRestrictedFactor(kind="rivers", buffer_distance=500),
            EngineRestrictedFactor(kind="lakes", buffer_distance=500),
            EngineRestrictedFactor(kind="residential", buffer_distance=1000),
        ],
        suitability_factors=[
            EngineSuitabilityFactor(
                kind="slope", weight=1.5, ranges=[(0, 5, 10), (5, 10, 8), (10, 15, 5), (15, 90, 2)]
            ),
            EngineSuitabilityFactor(
                kind="roads",
                weight=1.5,
                ranges=[(0, 1000, 10), (1000, 2000, 8), (2000, 3000, 5), (3000, float("inf"), 2)],
            ),
            EngineSuitabilityFactor(
                kind="solar",
                weight=4.0,
                ranges=[
                    (115, 125, 2),
                    (125, 135, 4),
                    (135, 140, 6),
                    (140, 145, 8),
                    (145, 150, 9),
                    (150, 155, 10),
                ],
            ),
        ],
    )


@pytest.fixture
def mock_file_system():
    """Mock file system operations."""
    with (
        patch("os.makedirs"),
        patch("os.path.exists", return_value=True),
        patch("os.path.join", side_effect=lambda *args: "/".join(args)),
    ):
        yield


class TestSiteSuitabilityEngineInitialization:
    """Test SiteSuitabilityEngine initialization."""

    @patch("os.makedirs")
    @patch("os.path.join")
    def test_init_creates_directories(
        self, mock_join, mock_makedirs, temp_dirs, sample_engine_configs
    ):
        """Test that initialization creates necessary directories."""
        data_dir, output_dir = temp_dirs

        # Mock os.path.join to return predictable paths
        mock_join.side_effect = lambda *args: "/".join(args)

        engine = SiteSuitabilityEngine(data_dir, output_dir, sample_engine_configs)

        # Verify makedirs was called for output directories
        assert mock_makedirs.call_count >= 4  # output_dir, restrict_dir, clip_dir, score_dir

        # Verify attributes are set correctly
        assert engine.data_dir == data_dir
        assert engine.output_dir == output_dir
        assert len(engine.factors) == 6  # 3 restricted + 3 suitability factors

    def test_init_sets_input_paths(self, temp_dirs, sample_engine_configs):
        """Test that initialization sets correct input file paths."""
        data_dir, output_dir = temp_dirs

        with patch("os.makedirs"), patch("os.path.join", side_effect=lambda *args: "/".join(args)):
            engine = SiteSuitabilityEngine(data_dir, output_dir, sample_engine_configs)

            # Verify input paths are set
            assert engine.in_territorial_authority.startswith(data_dir)
            assert engine.in_lake_polygons.startswith(data_dir)
            assert engine.in_river_centerlines.startswith(data_dir)
            assert engine.in_solar_radiation.startswith(data_dir)

    def test_factor_initialization_restricted_only(self, temp_dirs):
        """Test factor initialization with only restricted factors."""
        data_dir, output_dir = temp_dirs
        configs = EngineConfigs(
            restricted_factors=[EngineRestrictedFactor(kind="rivers", buffer_distance=300)],
            suitability_factors=[],
        )

        with patch("os.makedirs"), patch("os.path.join", side_effect=lambda *args: "/".join(args)):
            engine = SiteSuitabilityEngine(data_dir, output_dir, configs)

            assert len(engine.factors) == 1
            assert engine.factors[0]["name"] == "rivers"
            assert engine.factors[0]["buffer_distance"] == 300

    def test_factor_initialization_suitability_only(self, temp_dirs):
        """Test factor initialization with only suitability factors."""
        data_dir, output_dir = temp_dirs
        configs = EngineConfigs(
            restricted_factors=[],
            suitability_factors=[EngineSuitabilityFactor(kind="slope", weight=2.0)],
        )

        with patch("os.makedirs"), patch("os.path.join", side_effect=lambda *args: "/".join(args)):
            engine = SiteSuitabilityEngine(data_dir, output_dir, configs)

            assert len(engine.factors) == 1
            assert engine.factors[0]["name"] == "slope"
            assert engine.factors[0]["score_weight"] == 2.0


class TestSiteSuitabilityEngineDataProcessing:
    """Test data processing methods."""

    @pytest.fixture
    def engine(self, temp_dirs, sample_engine_configs):
        """Create engine instance for testing."""
        data_dir, output_dir = temp_dirs
        with patch("os.makedirs"), patch("os.path.join", side_effect=lambda *args: "/".join(args)):
            return SiteSuitabilityEngine(data_dir, output_dir, sample_engine_configs)

    @patch("app.gis.engine.RPL_Clip_analysis")
    @patch("app.gis.engine.logger")
    def test_clip_data_shapefile(self, mock_logger, mock_clip, engine):
        """Test clipping shapefile data."""
        factor = {"name": "rivers", "dataset": "input.shp"}
        prepared_data = {}
        district_name = "Test District"
        district_boundary_shp = "boundary.shp"
        district_boundary_bbox_shp = "bbox.shp"

        result = engine._clip_data(
            factor, prepared_data, district_name, district_boundary_shp, district_boundary_bbox_shp
        )

        mock_clip.assert_called_once()
        mock_logger.info.assert_called()
        assert result.endswith(".shp")

    @patch("app.gis.engine.RPL_ExtractByMask")
    @patch("app.gis.engine.tools.get_data_range")
    @patch("app.gis.engine.logger")
    def test_clip_data_raster(self, mock_logger, mock_get_range, mock_extract, engine):
        """Test clipping raster data."""
        factor = {"name": "solar", "dataset": "input.tif"}
        prepared_data = {}
        district_name = "Test District"
        district_boundary_shp = "boundary.shp"
        district_boundary_bbox_shp = "bbox.shp"

        mock_get_range.return_value = (0, 100, -9999)

        result = engine._clip_data(
            factor, prepared_data, district_name, district_boundary_shp, district_boundary_bbox_shp
        )

        mock_extract.assert_called_once()
        assert mock_get_range.call_count == 2  # Called for input and output
        assert result.endswith(".tif")

    @patch("app.gis.engine.RPL_Buffer_analysis")
    @patch("app.gis.engine.RPL_Clip_analysis")
    @patch("app.gis.engine.logger")
    def test_create_restricted_area(self, mock_logger, mock_clip, mock_buffer, engine):
        """Test creating restricted areas with buffers."""
        factor = {"name": "rivers", "buffer_distance": 500}
        prepared_data = {"rivers": "rivers_clipped.shp"}
        district_name = "Test District"
        district_boundary_shp = "boundary.shp"
        district_boundary_bbox_shp = "bbox.shp"

        result = engine._create_restricted_area(
            factor, prepared_data, district_name, district_boundary_shp, district_boundary_bbox_shp
        )

        mock_buffer.assert_called_once_with("rivers_clipped.shp", mock_buffer.call_args[0][1], 500)
        mock_clip.assert_called_once()
        mock_logger.info.assert_called()
        assert "buffer_clipped_rivers.shp" in result


class TestSiteSuitabilityEngineEvaluation:
    """Test evaluation methods."""

    @pytest.fixture
    def engine(self, temp_dirs, sample_engine_configs):
        """Create engine instance for testing."""
        data_dir, output_dir = temp_dirs
        with patch("os.makedirs"), patch("os.path.join", side_effect=lambda *args: "/".join(args)):
            return SiteSuitabilityEngine(data_dir, output_dir, sample_engine_configs)

    @patch("app.gis.engine.RPL_PolygonToRaster_conversion")
    @patch("app.gis.engine.RPL_DistanceAccumulation")
    @patch("app.gis.engine.RPL_Reclassify")
    @patch("app.gis.engine.tools.get_data_range")
    def test_evaluate_distance_vector(
        self, mock_get_range, mock_reclassify, mock_distance, mock_poly_to_raster, engine
    ):
        """Test evaluating distance to vector features."""
        factor = {"name": "roads", "evaluate_rules": [(0, 1000, 10), (1000, 2000, 8)]}
        prepared_data = {"roads": "roads.shp", "slope": "slope.tif"}
        district_name = "Test District"
        district_boundary = "boundary.shp"

        mock_get_range.return_value = (0, 100, -9999)

        result = engine._evaluate_distance_vector(
            factor, prepared_data, district_name, district_boundary
        )

        mock_poly_to_raster.assert_called_once()
        mock_distance.assert_called_once()
        mock_reclassify.assert_called_once()
        assert "score_roads.tif" in result

    @patch("app.gis.engine.RPL_Reclassify")
    @patch("app.gis.engine.tools.get_data_range")
    def test_evaluate_slope(self, mock_get_range, mock_reclassify, engine):
        """Test evaluating slope suitability."""
        factor = {"name": "slope", "evaluate_rules": [(0, 5, 10), (5, 10, 8)]}
        prepared_data = {"slope": "slope.tif"}
        district_name = "Test District"
        district_boundary = "boundary.shp"

        mock_get_range.return_value = (0, 45, -9999)

        result = engine._evaluate_slope(factor, prepared_data, district_name, district_boundary)

        mock_reclassify.assert_called_once()
        assert "score_slope.tif" in result

    @patch("app.gis.engine.RPL_Reclassify")
    @patch("app.gis.engine.tools.get_data_range")
    def test_evaluate_radiation(self, mock_get_range, mock_reclassify, engine):
        """Test evaluating solar radiation suitability."""
        factor = {"name": "solar", "evaluate_rules": [(115, 125, 2), (125, 135, 4)]}
        prepared_data = {"solar": "solar.tif"}
        district_name = "Test District"
        district_boundary = "boundary.shp"

        mock_get_range.return_value = (100, 160, -9999)

        result = engine._evaluate_radiation(factor, prepared_data, district_name, district_boundary)

        mock_reclassify.assert_called_once()
        assert "score_solar.tif" in result

    @patch("app.gis.engine.RPL_Reclassify")
    @patch("app.gis.engine.tools.get_data_range")
    def test_evaluate_temperature(self, mock_get_range, mock_reclassify, engine):
        """Test evaluating temperature suitability."""
        factor = {"name": "temperature", "evaluate_rules": [(-70, 0, 2), (0, 50, 5)]}
        prepared_data = {"temperature": "temp.tif"}
        district_name = "Test District"
        district_boundary = "boundary.shp"

        mock_get_range.return_value = (-50, 200, -9999)

        result = engine._evaluate_temperature(
            factor, prepared_data, district_name, district_boundary
        )

        mock_reclassify.assert_called_once()
        assert "score_temperature.tif" in result


class TestSiteSuitabilityEngineRasterTemplate:
    """Test raster template selection."""

    @pytest.fixture
    def engine(self, temp_dirs, sample_engine_configs):
        """Create engine instance for testing."""
        data_dir, output_dir = temp_dirs
        with patch("os.makedirs"), patch("os.path.join", side_effect=lambda *args: "/".join(args)):
            return SiteSuitabilityEngine(data_dir, output_dir, sample_engine_configs)

    @patch("os.path.exists")
    @patch("app.gis.engine.logger")
    def test_raster_template_existing_solar(self, mock_logger, mock_exists, engine):
        """Test template selection when solar raster exists."""
        prepared_data = {"solar": "solar.tif", "temperature": "temp.tif"}
        district_boundary_shp = "boundary.shp"

        mock_exists.return_value = True

        result = engine._raster_template(prepared_data, district_boundary_shp)

        assert result == "solar.tif"
        mock_logger.info.assert_called_with("Using existing solar raster as template")

    @patch("os.path.exists")
    @patch("app.gis.engine.logger")
    def test_raster_template_existing_temperature(self, mock_logger, mock_exists, engine):
        """Test template selection when temperature raster exists."""
        prepared_data = {"temperature": "temp.tif", "slope": "slope.tif"}
        district_boundary_shp = "boundary.shp"

        # Mock exists to return True only for temperature file
        def mock_exists_side_effect(path):
            return "temp.tif" in path

        mock_exists.side_effect = mock_exists_side_effect

        result = engine._raster_template(prepared_data, district_boundary_shp)

        assert result == "temp.tif"
        mock_logger.info.assert_called_with("Using existing temperature raster as template")

    @patch("os.path.exists")
    @patch("app.gis.engine.RPL_ExtractByMask")
    @patch("app.gis.engine.logger")
    def test_raster_template_create_default(self, mock_logger, mock_extract, mock_exists, engine):
        """Test template creation when no suitable raster exists."""
        prepared_data = {"rivers": "rivers.shp"}
        district_boundary_shp = "boundary.shp"

        mock_exists.return_value = False

        result = engine._raster_template(prepared_data, district_boundary_shp)

        mock_extract.assert_called_once_with(
            engine.in_solar_radiation, district_boundary_shp, result
        )
        mock_logger.info.assert_called_with(
            "No suitable raster found for template; using solar radiation raster by default"
        )
        assert "template_raster.tif" in result


class TestSiteSuitabilityEngineProcessDistrict:
    """Test district processing workflow."""

    @pytest.fixture
    def engine(self, temp_dirs, sample_engine_configs):
        """Create engine instance for testing."""
        data_dir, output_dir = temp_dirs
        with patch("os.makedirs"), patch("os.path.join", side_effect=lambda *args: "/".join(args)):
            return SiteSuitabilityEngine(data_dir, output_dir, sample_engine_configs)

    def test_process_district_cancelled_early(self, engine):
        """Test processing cancellation at the beginning."""
        monitor = MockTaskMonitor(cancelled=True)

        result = engine.process_district("001", "Test District", monitor)

        assert result is None
        assert len(monitor.progress_calls) == 0

    @patch("app.gis.engine.RPL_Select_analysis")
    @patch("app.gis.engine.gen_bounding_box")
    @patch("app.gis.engine.logger")
    def test_process_district_preparation_phase(
        self, mock_logger, mock_gen_bbox, mock_select, engine
    ):
        """Test district processing preparation phase."""
        monitor = MockTaskMonitor()

        # Mock factor methods to avoid complex setup
        for factor in engine.factors:
            factor["method_prepare"] = MagicMock(return_value=f"{factor['name']}_prepared.tif")
            factor["method_restricted_zone"] = MagicMock(return_value=None)
            factor["method_evaluate"] = MagicMock(return_value=None)

        with patch.object(engine, "_raster_template", return_value="template.tif"):
            result = engine.process_district("001", "Test District", monitor)

        mock_select.assert_called_once()
        mock_gen_bbox.assert_called_once()
        assert len(monitor.progress_calls) >= 2  # At least boundary and bbox progress

    @patch("app.gis.engine.RPL_Select_analysis")
    @patch("app.gis.engine.gen_bounding_box")
    @patch("app.gis.engine.RPL_Union_analysis")
    @patch("app.gis.engine.RPL_PolygonToRaster_conversion")
    @patch("app.gis.engine.RPL_Combine_rasters")
    @patch("app.gis.engine.RPL_Apply_mask")
    def test_process_district_full_workflow(
        self,
        mock_apply_mask,
        mock_combine,
        mock_poly_to_raster,
        mock_union,
        mock_gen_bbox,
        mock_select,
        engine,
    ):
        """Test complete district processing workflow."""
        monitor = MockTaskMonitor()

        # Mock factor methods
        for i, factor in enumerate(engine.factors):
            factor["method_prepare"] = MagicMock(return_value=f"{factor['name']}_prepared.tif")
            if i < 3:  # First 3 are restricted factors
                factor["method_restricted_zone"] = MagicMock(
                    return_value=f"restricted_{factor['name']}.shp"
                )
            else:
                factor["method_restricted_zone"] = MagicMock(return_value=None)
            if "score_weight" in factor:
                factor["method_evaluate"] = MagicMock(return_value=f"score_{factor['name']}.tif")
            else:
                factor["method_evaluate"] = MagicMock(return_value=None)

        with patch.object(engine, "_raster_template", return_value="template.tif"):
            result = engine.process_district("001", "Test District", monitor)

        # Verify the full workflow was executed
        mock_select.assert_called_once()
        mock_gen_bbox.assert_called_once()
        mock_union.assert_called_once()  # Restricted zones union
        mock_poly_to_raster.assert_called()  # Convert union to raster
        mock_combine.assert_called_once()  # Combine weighted scores
        mock_apply_mask.assert_called_once()  # Apply restricted mask

        # Verify final result
        assert result is not None
        assert "zone_masked.tif" in result

    def test_process_district_no_restricted_zones(self, engine):
        """Test processing when no restricted zones are created."""
        monitor = MockTaskMonitor()

        # Mock factor methods - no restricted zones
        for factor in engine.factors:
            factor["method_prepare"] = MagicMock(return_value=f"{factor['name']}_prepared.tif")
            factor["method_restricted_zone"] = MagicMock(return_value=None)
            if "score_weight" in factor:
                factor["method_evaluate"] = MagicMock(return_value=f"score_{factor['name']}.tif")
            else:
                factor["method_evaluate"] = MagicMock(return_value=None)

        with (
            patch("app.gis.engine.RPL_Select_analysis"),
            patch("app.gis.engine.gen_bounding_box"),
            patch("app.gis.engine.RPL_Combine_rasters") as mock_combine,
            patch.object(engine, "_raster_template", return_value="template.tif"),
        ):
            result = engine.process_district("001", "Test District", monitor)

        # Should return weighted sum without masking
        mock_combine.assert_called_once()
        assert result is not None
        assert "zone_weighted.tif" in result

    def test_process_district_no_score_rasters(self, engine):
        """Test processing when no score rasters are generated."""
        monitor = MockTaskMonitor()

        # Mock factor methods - no scores
        for factor in engine.factors:
            factor["method_prepare"] = MagicMock(return_value=f"{factor['name']}_prepared.tif")
            factor["method_restricted_zone"] = MagicMock(return_value=None)
            factor["method_evaluate"] = MagicMock(return_value=None)

        with (
            patch("app.gis.engine.RPL_Select_analysis"),
            patch("app.gis.engine.gen_bounding_box"),
            patch.object(engine, "_raster_template", return_value="template.tif"),
        ):
            result = engine.process_district("001", "Test District", monitor)

        assert result is None

    def test_process_district_cancelled_during_preparation(self, engine):
        """Test processing cancellation during data preparation."""
        monitor = MockTaskMonitor()

        # Set up factors with one that will trigger cancellation
        def cancel_after_first_factor(*args):
            monitor.cancelled = True
            return "prepared.tif"

        engine.factors[0]["method_prepare"] = cancel_after_first_factor
        for factor in engine.factors[1:]:
            factor["method_prepare"] = MagicMock()

        with patch("app.gis.engine.RPL_Select_analysis"), patch("app.gis.engine.gen_bounding_box"):
            result = engine.process_district("001", "Test District", monitor)

        assert result is None

    def test_process_district_cancelled_during_restricted_zones(self, engine):
        """Test processing cancellation during restricted zone creation."""
        monitor = MockTaskMonitor()

        # Mock factor methods
        for factor in engine.factors:
            factor["method_prepare"] = MagicMock(return_value=f"{factor['name']}_prepared.tif")

        # Set up restricted zone method that will trigger cancellation
        def cancel_during_restriction(*args):
            monitor.cancelled = True
            return "restricted.shp"

        engine.factors[0]["method_restricted_zone"] = cancel_during_restriction
        for factor in engine.factors[1:]:
            factor["method_restricted_zone"] = MagicMock(return_value=None)

        with (
            patch("app.gis.engine.RPL_Select_analysis"),
            patch("app.gis.engine.gen_bounding_box"),
            patch.object(engine, "_raster_template", return_value="template.tif"),
        ):
            result = engine.process_district("001", "Test District", monitor)

        assert result is None

    def test_process_district_cancelled_during_evaluation(self, engine):
        """Test processing cancellation during factor evaluation."""
        monitor = MockTaskMonitor()

        # Mock factor methods
        for factor in engine.factors:
            factor["method_prepare"] = MagicMock(return_value=f"{factor['name']}_prepared.tif")
            factor["method_restricted_zone"] = MagicMock(return_value=None)

        # Set up evaluation method that will trigger cancellation
        def cancel_during_evaluation(*args):
            monitor.cancelled = True
            return "score.tif"

        # Find a factor with evaluation method and set cancellation
        for factor in engine.factors:
            if "score_weight" in factor:
                factor["method_evaluate"] = cancel_during_evaluation
                break

        with (
            patch("app.gis.engine.RPL_Select_analysis"),
            patch("app.gis.engine.gen_bounding_box"),
            patch.object(engine, "_raster_template", return_value="template.tif"),
        ):
            result = engine.process_district("001", "Test District", monitor)

        assert result is None

    def test_process_district_no_weighted_rasters(self, engine):
        """Test processing when no weighted rasters are created."""
        monitor = MockTaskMonitor()

        # Mock factor methods - no weighted rasters
        for factor in engine.factors:
            factor["method_prepare"] = MagicMock(return_value=f"{factor['name']}_prepared.tif")
            factor["method_restricted_zone"] = MagicMock(return_value=None)
            # Remove score_weight so no weighted rasters are created
            if "score_weight" in factor:
                factor["method_evaluate"] = MagicMock(return_value=f"score_{factor['name']}.tif")
                del factor["score_weight"]  # Remove weight
            else:
                factor["method_evaluate"] = MagicMock(return_value=None)

        with (
            patch("app.gis.engine.RPL_Select_analysis"),
            patch("app.gis.engine.gen_bounding_box"),
            patch.object(engine, "_raster_template", return_value="template.tif"),
            patch("builtins.print") as mock_print,
        ):
            result = engine.process_district("001", "Test District", monitor)

        # Should print warning and return None
        mock_print.assert_called_with("Warning: No weighted rasters for Test District")
        assert result is None


class TestSiteSuitabilityEngineRun:
    """Test the main run method."""

    @pytest.fixture
    def engine(self, temp_dirs, sample_engine_configs):
        """Create engine instance for testing."""
        data_dir, output_dir = temp_dirs
        with patch("os.makedirs"), patch("os.path.join", side_effect=lambda *args: "/".join(args)):
            return SiteSuitabilityEngine(data_dir, output_dir, sample_engine_configs)

    @patch("app.gis.consts.districts", [("001", "District One"), ("002", "District Two")])
    def test_run_selected_districts(self, engine):
        """Test running analysis for selected districts."""
        monitor = MockTaskMonitor()

        with patch.object(engine, "process_district", return_value="result.tif") as mock_process:
            results = engine.run(selected_districts=["001"], monitor=monitor)

        assert len(results) == 1
        assert "District One" in results
        assert results["District One"] == "result.tif"
        mock_process.assert_called_once_with("001", "District One", monitor=monitor)

    @patch("app.gis.consts.districts", [("001", "District One"), ("002", "District Two")])
    def test_run_multiple_districts(self, engine):
        """Test running analysis for multiple districts."""
        monitor = MockTaskMonitor()

        with patch.object(engine, "process_district", return_value="result.tif") as mock_process:
            results = engine.run(selected_districts=["001", "002"], monitor=monitor)

        assert len(results) == 2
        assert "District One" in results
        assert "District Two" in results
        assert mock_process.call_count == 2

    def test_run_no_districts_found(self, engine):
        """Test error when no districts match the selected codes."""
        monitor = MockTaskMonitor()

        with pytest.raises(Exception, match="No districts found for the provided codes"):
            engine.run(selected_districts=["999"], monitor=monitor)

    @patch("app.gis.consts.districts", [("001", "District One"), ("002", "District Two")])
    def test_run_cancelled_during_processing(self, engine):
        """Test cancellation during district processing."""
        monitor = MockTaskMonitor()

        def cancel_after_first(*args, **kwargs):
            monitor.cancelled = True
            return "result.tif"

        with patch.object(
            engine, "process_district", side_effect=cancel_after_first
        ) as mock_process:
            results = engine.run(selected_districts=["001", "002"], monitor=monitor)

        # Should only process first district before cancellation
        assert len(results) == 1
        assert mock_process.call_count == 1


class TestEmptyTaskMonitor:
    """Test the EmptyTaskMonitor implementation."""

    def test_empty_task_monitor_not_cancelled(self):
        """Test EmptyTaskMonitor is never cancelled."""
        monitor = EmptyTaskMonitor()
        assert monitor.is_cancelled() is False

    @patch("app.gis.engine_models.logger")
    def test_empty_task_monitor_update_progress(self, mock_logger):
        """Test EmptyTaskMonitor logs progress updates."""
        monitor = EmptyTaskMonitor()
        monitor.update_progress(50, "test_phase", "test description")

        mock_logger.info.assert_called_once_with(
            "Progress update: 50% - Phase: test_phase - Description: test description"
        )

    @patch("app.gis.engine_models.logger")
    def test_empty_task_monitor_record_error(self, mock_logger):
        """Test EmptyTaskMonitor logs errors."""
        monitor = EmptyTaskMonitor()
        monitor.record_error("test error", "test_phase", 25, "test description")

        mock_logger.error.assert_called_once_with(
            "Error occurred: test error - Phase: test_phase - Percent: 25 - Description: test description"
        )


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling."""

    @pytest.fixture
    def engine(self, temp_dirs, sample_engine_configs):
        """Create engine instance for testing."""
        data_dir, output_dir = temp_dirs
        with patch("os.makedirs"), patch("os.path.join", side_effect=lambda *args: "/".join(args)):
            return SiteSuitabilityEngine(data_dir, output_dir, sample_engine_configs)

    def test_empty_configurations(self, temp_dirs):
        """Test initialization with empty configurations."""
        data_dir, output_dir = temp_dirs
        empty_configs = EngineConfigs(restricted_factors=[], suitability_factors=[])

        with patch("os.makedirs"), patch("os.path.join", side_effect=lambda *args: "/".join(args)):
            engine = SiteSuitabilityEngine(data_dir, output_dir, empty_configs)

            assert len(engine.factors) == 0

    def test_nonexistent_factor_kind(self, temp_dirs):
        """Test handling of non-existent factor kinds in configuration."""
        data_dir, output_dir = temp_dirs
        configs = EngineConfigs(
            restricted_factors=[
                EngineRestrictedFactor(kind="nonexistent_factor", buffer_distance=500)
            ],
            suitability_factors=[],
        )

        with patch("os.makedirs"), patch("os.path.join", side_effect=lambda *args: "/".join(args)):
            engine = SiteSuitabilityEngine(data_dir, output_dir, configs)

            # Should not add unknown factors
            assert len(engine.factors) == 0

    @patch("app.gis.engine.logger")
    def test_raster_template_no_prepared_data(self, mock_logger, engine):
        """Test raster template creation with no prepared data."""
        prepared_data = {}
        district_boundary_shp = "boundary.shp"

        with patch("app.gis.engine.RPL_ExtractByMask") as mock_extract:
            result = engine._raster_template(prepared_data, district_boundary_shp)

            mock_extract.assert_called_once()
            mock_logger.info.assert_called_with(
                "No suitable raster found for template; using solar radiation raster by default"
            )
            assert "template_raster.tif" in result


class TestIntegrationScenarios:
    """Test realistic integration scenarios."""

    @pytest.fixture
    def realistic_engine_configs(self):
        """Create realistic engine configurations."""
        return EngineConfigs(
            restricted_factors=[
                EngineRestrictedFactor(kind="rivers", buffer_distance=500),
                EngineRestrictedFactor(kind="lakes", buffer_distance=300),
                EngineRestrictedFactor(kind="residential", buffer_distance=1000),
            ],
            suitability_factors=[
                EngineSuitabilityFactor(
                    kind="slope",
                    weight=1.5,
                    ranges=[(0, 5, 10), (5, 15, 8), (15, 25, 5), (25, 45, 2), (45, 90, 1)],
                ),
                EngineSuitabilityFactor(
                    kind="solar",
                    weight=3.0,
                    ranges=[(100, 120, 3), (120, 135, 6), (135, 145, 9), (145, 160, 10)],
                ),
                EngineSuitabilityFactor(
                    kind="roads",
                    weight=2.0,
                    ranges=[
                        (0, 500, 10),
                        (500, 1000, 8),
                        (1000, 2000, 6),
                        (2000, 5000, 3),
                        (5000, float("inf"), 1),
                    ],
                ),
            ],
        )

    def test_realistic_factor_configuration(self, temp_dirs, realistic_engine_configs):
        """Test engine with realistic factor configuration."""
        data_dir, output_dir = temp_dirs

        with patch("os.makedirs"), patch("os.path.join", side_effect=lambda *args: "/".join(args)):
            engine = SiteSuitabilityEngine(data_dir, output_dir, realistic_engine_configs)

            # Verify all factors are configured
            assert len(engine.factors) == 6

            # Check restricted factors
            restricted_factors = [f for f in engine.factors if "buffer_distance" in f]
            assert len(restricted_factors) == 3

            # Check suitability factors
            suitability_factors = [f for f in engine.factors if "score_weight" in f]
            assert len(suitability_factors) == 3

            # Verify custom ranges are applied
            slope_factor = next(f for f in engine.factors if f["name"] == "slope")
            assert len(slope_factor["evaluate_rules"]) == 5  # Custom ranges
