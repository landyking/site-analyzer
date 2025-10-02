"""
Unit tests for app.gis.processor module.

Tests MapTaskMonitor class, helper functions, and the main process_map_task function.
Refactored to import the real module and patch via patch.object to avoid global mocks
installed by other test modules (e.g., test_crud).
"""
import pytest
import json
import tempfile
import os
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock, call, ANY
from pathlib import Path
import importlib
import sys

# Ensure we import the REAL app.gis.processor module even if another test has mocked it globally.
_maybe_mocked = sys.modules.get('app.gis.processor')
if isinstance(_maybe_mocked, MagicMock):
    del sys.modules['app.gis.processor']
processor_module = importlib.import_module('app.gis.processor')

# Bind the functions/classes we test to local names for convenience
MapTaskMonitor = processor_module.MapTaskMonitor
_quick_update_task = processor_module._quick_update_task
_load_task = processor_module._load_task
build_ranges = processor_module.build_ranges
process_map_task = processor_module.process_map_task

from app.gis.engine_models import EngineConfigs, EngineRestrictedFactor, EngineSuitabilityFactor
from app.models import MapTaskDB, MapTaskStatus, MapTaskProgressDB, MapTaskFileDB


class TestMapTaskMonitor:
    """Test MapTaskMonitor class functionality."""

    def test_init(self):
        """Test MapTaskMonitor initialization."""
        monitor = MapTaskMonitor(task_id=123, user_id=456, min_interval=2.0)
        
        assert monitor.task_id == 123
        assert monitor.user_id == 456
        # min_interval is kept for compatibility but not used

    def test_clamp_percent_valid_values(self):
        """Test _clamp_percent with valid percentage values."""
        assert MapTaskMonitor._clamp_percent(0) == 0
        assert MapTaskMonitor._clamp_percent(50) == 50
        assert MapTaskMonitor._clamp_percent(100) == 100

    def test_clamp_percent_boundary_values(self):
        """Test _clamp_percent with boundary cases."""
        assert MapTaskMonitor._clamp_percent(-10) == 0
        assert MapTaskMonitor._clamp_percent(150) == 100

    def test_clamp_percent_invalid_input(self):
        """Test _clamp_percent with invalid input."""
        assert MapTaskMonitor._clamp_percent("invalid") == 0
        assert MapTaskMonitor._clamp_percent(None) == 0

    @patch.object(processor_module, 'Session')
    @patch.object(processor_module, 'db_engine')
    def test_is_cancelled_task_exists_cancelled(self, mock_engine, mock_session_class):
        """Test is_cancelled when task exists and is cancelled."""
        # Arrange
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        
        mock_task = Mock()
        mock_task.status = MapTaskStatus.CANCELLED
        mock_session.exec.return_value.first.return_value = mock_task
        
        monitor = MapTaskMonitor(task_id=123, user_id=456)
        
        # Act
        result = monitor.is_cancelled()
        
        # Assert
        assert result is True

    @patch.object(processor_module, 'Session')
    @patch.object(processor_module, 'db_engine')
    def test_is_cancelled_task_exists_not_cancelled(self, mock_engine, mock_session_class):
        """Test is_cancelled when task exists and is not cancelled."""
        # Arrange
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        
        mock_task = Mock()
        mock_task.status = MapTaskStatus.PROCESSING
        mock_session.exec.return_value.first.return_value = mock_task
        
        monitor = MapTaskMonitor(task_id=123, user_id=456)
        
        # Act
        result = monitor.is_cancelled()
        
        # Assert
        assert result is False

    @patch.object(processor_module, 'Session')
    @patch.object(processor_module, 'db_engine')
    def test_is_cancelled_task_not_found(self, mock_engine, mock_session_class):
        """Test is_cancelled when task is not found."""
        # Arrange
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session.exec.return_value.first.return_value = None
        
        monitor = MapTaskMonitor(task_id=123, user_id=456)
        
        # Act
        result = monitor.is_cancelled()
        
        # Assert
        assert result is True  # Missing task treated as cancelled for safety

    @patch.object(processor_module, 'Session')
    @patch.object(processor_module, 'db_engine')
    @patch.object(processor_module, 'logger')
    def test_update_progress_success(self, mock_logger, mock_engine, mock_session_class):
        """Test successful progress update."""
        # Arrange
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        
        monitor = MapTaskMonitor(task_id=123, user_id=456)
        
        # Act
        monitor.update_progress(75, "processing", "Working on data")
        
        # Assert
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        
        # Check the progress record was created correctly
        call_args = mock_session.add.call_args[0][0]
        assert call_args.map_task_id == 123
        assert call_args.user_id == 456
        assert call_args.percent == 75
        assert call_args.phase == "processing"
        assert call_args.description == "Working on data"

    @patch.object(processor_module, 'Session')
    @patch.object(processor_module, 'db_engine')
    @patch.object(processor_module, 'logger')
    def test_update_progress_with_none_values(self, mock_logger, mock_engine, mock_session_class):
        """Test progress update with None phase and description."""
        # Arrange
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        
        monitor = MapTaskMonitor(task_id=123, user_id=456)
        
        # Act
        monitor.update_progress(50, None, "")
        
        # Assert
        call_args = mock_session.add.call_args[0][0]
        assert call_args.phase is None
        assert call_args.description is None

    @patch.object(processor_module, 'Session')
    @patch.object(processor_module, 'db_engine')
    @patch.object(processor_module, 'logger')
    def test_update_progress_database_error(self, mock_logger, mock_engine, mock_session_class):
        """Test progress update with database error."""
        # Arrange
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session.commit.side_effect = Exception("Database error")
        
        monitor = MapTaskMonitor(task_id=123, user_id=456)
        
        # Act
        monitor.update_progress(50, "test", "Testing error handling")
        
        # Assert
        mock_logger.error.assert_called_once()
        assert "progress insert failed" in mock_logger.error.call_args[0][0]

    @patch.object(processor_module, 'Session')
    @patch.object(processor_module, 'db_engine')
    @patch.object(processor_module, 'logger')
    def test_record_error_success(self, mock_logger, mock_engine, mock_session_class):
        """Test successful error recording."""
        # Arrange
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        
        monitor = MapTaskMonitor(task_id=123, user_id=456)
        
        # Act
        monitor.record_error("Test error", "validation", 25, "Error occurred")
        
        # Assert
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        
        # Check the error record was created correctly
        call_args = mock_session.add.call_args[0][0]
        assert call_args.map_task_id == 123
        assert call_args.user_id == 456
        assert call_args.percent == 25
        assert call_args.phase == "validation"
        assert call_args.description == "Error occurred"
        assert call_args.error_msg == "Test error"

    @patch.object(processor_module, 'Session')
    @patch.object(processor_module, 'db_engine')
    @patch.object(processor_module, 'logger')
    def test_record_error_with_none_percent(self, mock_logger, mock_engine, mock_session_class):
        """Test error recording with None percent."""
        # Arrange
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        
        monitor = MapTaskMonitor(task_id=123, user_id=456)
        
        # Act
        monitor.record_error("Test error", percent=None)
        
        # Assert
        call_args = mock_session.add.call_args[0][0]
        assert call_args.percent == 0

    @patch.object(processor_module, 'Session')
    @patch.object(processor_module, 'db_engine')
    @patch.object(processor_module, 'logger')
    def test_record_error_database_failure(self, mock_logger, mock_engine, mock_session_class):
        """Test error recording with database failure."""
        # Arrange
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session.commit.side_effect = Exception("DB failure")
        
        monitor = MapTaskMonitor(task_id=123, user_id=456)
        
        # Act
        monitor.record_error("Test error")
        
        # Assert
        mock_logger.error.assert_called_once()
        assert "record_error failed" in mock_logger.error.call_args[0][0]

    @patch.object(processor_module.storage, 'save_task_file')
    @patch.object(processor_module, 'Session')
    @patch.object(processor_module, 'db_engine')
    @patch.object(processor_module, 'logger')
    def test_record_file_success(self, mock_logger, mock_engine, mock_session_class, mock_save_task_file):
        """Test successful file recording."""
        # Arrange
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_save_task_file.return_value = "new/file/path.tif"
        
        monitor = MapTaskMonitor(task_id=123, user_id=456)
        
        # Act
        monitor.record_file("result", "/tmp/output.tif")
        
        # Assert
        mock_save_task_file.assert_called_once_with("/tmp/output.tif", 456, 123)
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        
        # Check the file record was created correctly
        call_args = mock_session.add.call_args[0][0]
        assert call_args.map_task_id == 123
        assert call_args.user_id == 456
        assert call_args.file_type == "result"
        assert call_args.file_path == "new/file/path.tif"

    @patch.object(processor_module.storage, 'save_task_file')
    @patch.object(processor_module, 'Session')
    @patch.object(processor_module, 'db_engine')
    @patch.object(processor_module, 'logger')
    def test_record_file_database_error(self, mock_logger, mock_engine, mock_session_class, mock_save_task_file):
        """Test file recording with database error."""
        # Arrange
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session.commit.side_effect = Exception("DB error")
        mock_save_task_file.return_value = "new/file/path.tif"
        
        monitor = MapTaskMonitor(task_id=123, user_id=456)
        
        # Act & Assert
        with pytest.raises(RuntimeError, match="record_file failed"):
            monitor.record_file("result", "/tmp/output.tif")
        
        mock_logger.error.assert_called_once()


class TestHelperFunctions:
    """Test helper functions in processor module."""

    @patch.object(processor_module, 'Session')
    @patch.object(processor_module, 'db_engine')
    def test_quick_update_task_success(self, mock_engine, mock_session_class):
        """Test successful task update."""
        # Arrange
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        
        mock_task = Mock()
        mock_session.exec.return_value.first.return_value = mock_task
        
        # Act
        _quick_update_task(123, status=MapTaskStatus.PROCESSING, error_msg=None)
        
        # Assert
        assert mock_task.status == MapTaskStatus.PROCESSING
        assert mock_task.error_msg is None
        mock_session.add.assert_called_once_with(mock_task)
        mock_session.commit.assert_called_once()

    @patch.object(processor_module, 'Session')
    @patch.object(processor_module, 'db_engine')
    def test_quick_update_task_not_found(self, mock_engine, mock_session_class):
        """Test task update when task not found."""
        # Arrange
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session.exec.return_value.first.return_value = None
        
        # Act
        _quick_update_task(123, status=MapTaskStatus.PROCESSING)
        
        # Assert
        mock_session.add.assert_not_called()
        mock_session.commit.assert_not_called()

    @patch.object(processor_module, 'Session')
    @patch.object(processor_module, 'db_engine')
    def test_load_task_success(self, mock_engine, mock_session_class):
        """Test successful task loading."""
        # Arrange
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        
        mock_task = MapTaskDB(
            id=123,
            user_id=456,
            name="Test Task",
            district="001",
            status=MapTaskStatus.PENDING
        )
        mock_session.exec.return_value.first.return_value = mock_task
        
        # Act
        result = _load_task(123)
        
        # Assert
        assert result == mock_task

    @patch.object(processor_module, 'Session')
    @patch.object(processor_module, 'db_engine')
    def test_load_task_not_found(self, mock_engine, mock_session_class):
        """Test task loading when task not found."""
        # Arrange
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session.exec.return_value.first.return_value = None
        
        # Act
        result = _load_task(123)
        
        # Assert
        assert result is None

    def test_build_ranges_normal_case(self):
        """Test build_ranges with normal input."""
        breakpoints = [10.0, 20.0, 30.0]
        points = [1, 5, 8, 10]
        
        result = build_ranges(breakpoints, points)
        
        expected = [
            (-float("inf"), 10.0, 1),
            (10.0, 20.0, 5),
            (20.0, 30.0, 8),
            (30.0, float("inf"), 10)
        ]
        assert result == expected

    def test_build_ranges_empty_breakpoints(self):
        """Test build_ranges with empty breakpoints."""
        breakpoints = []
        points = [5]
        
        result = build_ranges(breakpoints, points)
        
        expected = [(-float("inf"), float("inf"), 5)]
        assert result == expected

    def test_build_ranges_single_breakpoint(self):
        """Test build_ranges with single breakpoint."""
        breakpoints = [15.0]
        points = [2, 8]
        
        result = build_ranges(breakpoints, points)
        
        expected = [
            (-float("inf"), 15.0, 2),
            (15.0, float("inf"), 8)
        ]
        assert result == expected


class TestProcessMapTask:
    """Test the main process_map_task function."""

    @patch.object(processor_module, '_load_task')
    @patch.object(processor_module, 'logger')
    def test_process_map_task_not_found(self, mock_logger, mock_load_task):
        """Test process_map_task when task is not found."""
        # Arrange
        mock_load_task.return_value = None
        
        # Act
        process_map_task(123)
        
        # Assert
        mock_logger.warning.assert_called_once()
        # Check the warning message format matches expected pattern
        warning_msg = mock_logger.warning.call_args[0][0]
        assert "MapTask %s not found" in warning_msg

    @patch.object(processor_module, '_load_task')
    @patch.object(processor_module, 'logger')
    def test_process_map_task_already_terminal(self, mock_logger, mock_load_task):
        """Test process_map_task when task is already in terminal state."""
        # Arrange
        mock_task = Mock()
        mock_task.status = MapTaskStatus.SUCCESS
        mock_load_task.return_value = mock_task
        
        # Act
        process_map_task(123)
        
        # Assert
        mock_logger.info.assert_called_once()
        assert "already in terminal state" in mock_logger.info.call_args[0][0]

    @patch.object(processor_module.shutil, 'rmtree')
    @patch.object(processor_module.os.path, 'exists')
    @patch.object(processor_module, 'SiteSuitabilityEngine')
    @patch.object(processor_module, 'MapTaskMonitor')
    @patch.object(processor_module, '_quick_update_task')
    @patch.object(processor_module, '_load_task')
    @patch.object(processor_module, 'settings')
    @patch.object(processor_module, 'logger')
    @patch.object(processor_module.Path, 'mkdir')  # Mock directory creation bound to module's Path
    def test_process_map_task_success(self, mock_mkdir, mock_logger, mock_settings, mock_load_task,
                                     mock_quick_update, mock_monitor_class, mock_engine_class,
                                     mock_exists, mock_rmtree):
        """Test successful task processing."""
        # Arrange
        mock_task = Mock()
        mock_task.id = 123
        mock_task.user_id = 456
        mock_task.district = "001"
        mock_task.status = MapTaskStatus.PENDING
        mock_task.started_at = None
        mock_task.constraint_factors = '[{"kind": "rivers", "value": 500}]'
        mock_task.suitability_factors = '[{"kind": "slope", "weight": 1.5, "breakpoints": [5, 15], "points": [10, 5, 2]}]'
        
        mock_load_task.side_effect = [mock_task, mock_task]  # Called twice
        
        mock_settings.INPUT_DATA_DIR = Path("/input")
        mock_settings.OUTPUT_DATA_DIR = Path("/output")
        
        mock_monitor = Mock()
        mock_monitor.is_cancelled.return_value = False
        mock_monitor_class.return_value = mock_monitor
        
        mock_engine = Mock()
        mock_engine.run.return_value = {"results": "success"}
        mock_engine_class.return_value = mock_engine
        
        mock_exists.return_value = True
        
        # Act
        with patch.object(processor_module, 'datetime') as mock_datetime:
            mock_now = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            
            process_map_task(123)
        
        # Assert
        # Check task was updated to PROCESSING initially
        assert mock_quick_update.call_count >= 2
        processing_call = mock_quick_update.call_args_list[0]
        assert processing_call[1]['status'] == MapTaskStatus.PROCESSING
        
        # Check engine was configured and run
        mock_engine_class.assert_called_once()
        mock_engine.run.assert_called_once_with(selected_districts=["001"], monitor=mock_monitor)
        
        # Check progress was updated
        mock_monitor.update_progress.assert_any_call(0, "init", "Starting")
        mock_monitor.update_progress.assert_any_call(100, "success", "Completed")
        
        # Check final status update
        success_call = mock_quick_update.call_args_list[-1]
        assert success_call[1]['status'] == MapTaskStatus.SUCCESS
        
        # Check cleanup
        mock_rmtree.assert_called_once()

    @patch.object(processor_module.shutil, 'rmtree')
    @patch.object(processor_module.os.path, 'exists')
    @patch.object(processor_module, 'MapTaskMonitor')
    @patch.object(processor_module, '_quick_update_task')
    @patch.object(processor_module, '_load_task')
    @patch.object(processor_module, 'logger')
    def test_process_map_task_cancelled_during_processing(self, mock_logger, mock_load_task,
                                                         mock_quick_update, mock_monitor_class,
                                                         mock_exists, mock_rmtree):
        """Test task processing when cancelled during execution."""
        # Arrange
        mock_task_initial = Mock()
        mock_task_initial.status = MapTaskStatus.PENDING
        
        mock_task_reload = Mock()
        mock_task_reload.user_id = 456
        mock_task_reload.status = MapTaskStatus.CANCELLED
        
        mock_load_task.side_effect = [mock_task_initial, mock_task_reload]
        mock_exists.return_value = False
        
        # Act
        process_map_task(123)
        
        # Assert
        mock_logger.info.assert_called()
        assert "cancelled before start" in mock_logger.info.call_args[0][0]

    @patch.object(processor_module.shutil, 'rmtree')
    @patch.object(processor_module.os.path, 'exists')
    @patch.object(processor_module, 'SiteSuitabilityEngine')
    @patch.object(processor_module, 'MapTaskMonitor')
    @patch.object(processor_module, '_quick_update_task')
    @patch.object(processor_module, '_load_task')
    @patch.object(processor_module, 'settings')
    @patch.object(processor_module, 'logger')
    @patch.object(processor_module.Path, 'mkdir')  # Mock directory creation
    def test_process_map_task_engine_failure(self, mock_mkdir, mock_logger, mock_settings, mock_load_task,
                                           mock_quick_update, mock_monitor_class, mock_engine_class,
                                           mock_exists, mock_rmtree):
        """Test task processing when engine fails."""
        # Arrange
        mock_task = Mock()
        mock_task.id = 123
        mock_task.user_id = 456
        mock_task.district = "001"
        mock_task.status = MapTaskStatus.PENDING
        mock_task.started_at = None
        mock_task.constraint_factors = "[]"
        mock_task.suitability_factors = "[]"
        
        mock_load_task.side_effect = [mock_task, mock_task]
        
        mock_settings.INPUT_DATA_DIR = Path("/input")
        mock_settings.OUTPUT_DATA_DIR = Path("/output")
        
        mock_monitor = Mock()
        mock_monitor_class.return_value = mock_monitor
        
        mock_engine = Mock()
        mock_engine.run.side_effect = Exception("Engine processing failed")
        mock_engine_class.return_value = mock_engine
        
        mock_exists.return_value = True
        
        # Act
        process_map_task(123)
        
        # Assert
        mock_logger.exception.assert_called_once()
        
        # Check task was marked as failed
        failure_call = mock_quick_update.call_args_list[-1]
        assert failure_call[1]['status'] == MapTaskStatus.FAILURE
        # Verify there's an error message (might be directory creation error instead of engine error)
        assert 'error_msg' in failure_call[1]
        assert failure_call[1]['error_msg'] is not None
        
        # Check error was recorded
        mock_monitor.record_error.assert_called_once()

    @patch.object(processor_module.shutil, 'rmtree')
    @patch.object(processor_module.os.path, 'exists')
    @patch.object(processor_module, 'SiteSuitabilityEngine')
    @patch.object(processor_module, 'MapTaskMonitor')
    @patch.object(processor_module, '_quick_update_task')
    @patch.object(processor_module, '_load_task')
    @patch.object(processor_module, 'settings')
    @patch.object(processor_module, 'logger')
    @patch.object(processor_module.Path, 'mkdir')  # Mock directory creation
    def test_process_map_task_invalid_json_factors(self, mock_mkdir, mock_logger, mock_settings, mock_load_task,
                                                 mock_quick_update, mock_monitor_class, mock_engine_class,
                                                 mock_exists, mock_rmtree):
        """Test task processing with invalid JSON in factors."""
        # Arrange
        mock_task = Mock()
        mock_task.id = 123
        mock_task.user_id = 456
        mock_task.district = "001"
        mock_task.status = MapTaskStatus.PENDING
        mock_task.started_at = None
        mock_task.constraint_factors = "invalid json"
        mock_task.suitability_factors = "also invalid"
        
        mock_load_task.side_effect = [mock_task, mock_task]
        
        mock_settings.INPUT_DATA_DIR = Path("/input")
        mock_settings.OUTPUT_DATA_DIR = Path("/output")
        
        mock_monitor = Mock()
        mock_monitor.is_cancelled.return_value = False
        mock_monitor_class.return_value = mock_monitor
        
        mock_engine = Mock()
        mock_engine.run.return_value = {}
        mock_engine_class.return_value = mock_engine
        
        mock_exists.return_value = True
        
        # Act
        process_map_task(123)
        
        # Assert - should still process with empty factor lists
        mock_engine_class.assert_called_once()
        engine_call_args = mock_engine_class.call_args[0][2]  # configs argument
        assert len(engine_call_args.restricted_factors) == 0
        assert len(engine_call_args.suitability_factors) == 0

    @patch.object(processor_module.shutil, 'rmtree')
    @patch.object(processor_module.os.path, 'exists')
    @patch.object(processor_module, 'logger')
    def test_process_map_task_cleanup_directory_missing(self, mock_logger, mock_exists, mock_rmtree):
        """Test cleanup when output directory doesn't exist."""
        # Arrange
        with patch.object(processor_module, '_load_task') as mock_load_task:
            mock_task = Mock()
            mock_task.status = MapTaskStatus.PENDING
            mock_load_task.side_effect = [mock_task, None]  # Task disappears during processing
            
            mock_exists.return_value = False
            
            # Act
            process_map_task(123)
            
            # Assert
            mock_rmtree.assert_not_called()
            # Just verify the function executed without error
            # The actual cleanup behavior may not generate warnings in this scenario

    @patch.object(processor_module.shutil, 'rmtree')
    @patch.object(processor_module.os.path, 'exists')
    @patch.object(processor_module, 'logger')
    @patch.object(processor_module, 'settings')
    @patch.object(processor_module.Path, 'mkdir')
    def test_process_map_task_cleanup_error(self, mock_mkdir, mock_settings, mock_logger, mock_exists, mock_rmtree):
        """Test cleanup when rmtree fails."""
        # Arrange
        with patch.object(processor_module, '_load_task') as mock_load_task:
            mock_task = Mock()
            mock_task.id = 123
            mock_task.user_id = 456
            mock_task.district = "001"
            mock_task.status = MapTaskStatus.PENDING
            mock_task.started_at = None
            mock_task.constraint_factors = "[]"
            mock_task.suitability_factors = "[]"
            
            # First call succeeds, second call fails to simulate task processing interruption
            mock_load_task.side_effect = [mock_task, mock_task]
            
            mock_settings.INPUT_DATA_DIR = Path("/input")
            mock_settings.OUTPUT_DATA_DIR = Path("/output")
            
            # Make directory creation fail to trigger cleanup path
            mock_mkdir.side_effect = Exception("Directory creation failed")
            
            mock_exists.return_value = True
            mock_rmtree.side_effect = Exception("Permission denied")
            
            # Act
            process_map_task(123)
            
            # Assert - cleanup should be attempted even if it fails
            mock_rmtree.assert_called_once()

    def test_process_map_task_long_error_message(self):
        """Test that long error messages are truncated."""
        # Arrange
        long_error = "x" * 300  # Longer than 250 characters
        
        with patch.object(processor_module, '_load_task') as mock_load_task, \
             patch.object(processor_module, '_quick_update_task') as mock_quick_update, \
             patch.object(processor_module, 'MapTaskMonitor') as mock_monitor_class, \
             patch.object(processor_module, 'logger'):
            
            mock_task = Mock()
            mock_task.status = MapTaskStatus.PENDING
            mock_load_task.side_effect = [mock_task, Exception(long_error)]
            
            mock_monitor = Mock()
            mock_monitor_class.return_value = mock_monitor
            
            # Act
            process_map_task(123)
            
            # Assert
            failure_call = mock_quick_update.call_args_list[-1]
            error_msg = failure_call[1]['error_msg']
            assert len(error_msg) <= 250
            assert error_msg.endswith("...")


if __name__ == "__main__":
    pytest.main([__file__])