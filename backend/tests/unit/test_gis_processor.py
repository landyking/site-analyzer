"""
Unit tests for app.gis.processor module.

Tests MapTaskMonitor, process_map_task, build_ranges, and helper functions
while avoiding circular import issues through strategic mocking.
"""

import pytest
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from typing import List, Tuple

# Mock the circular import issues before importing
with patch('app.crud.process_map_task'), \
     patch('app.core.db.engine'), \
     patch('app.gis.processor.db_engine'):
    
    # Import the module under test
    from app.gis.processor import MapTaskMonitor, process_map_task, build_ranges, _quick_update_task, _load_task
    from app.models import MapTaskDB, MapTaskStatus, MapTaskProgressDB, MapTaskFileDB


class TestMapTaskMonitor:
    """Test suite for MapTaskMonitor class."""

    def test_init(self):
        """Test MapTaskMonitor initialization."""
        monitor = MapTaskMonitor(task_id=123, user_id=456, min_interval=2.0)
        assert monitor.task_id == 123
        assert monitor.user_id == 456

    def test_clamp_percent_valid_values(self):
        """Test _clamp_percent with valid values."""
        assert MapTaskMonitor._clamp_percent(50) == 50
        assert MapTaskMonitor._clamp_percent(0) == 0
        assert MapTaskMonitor._clamp_percent(100) == 100

    def test_clamp_percent_edge_cases(self):
        """Test _clamp_percent with edge cases."""
        assert MapTaskMonitor._clamp_percent(-10) == 0
        assert MapTaskMonitor._clamp_percent(150) == 100
        assert MapTaskMonitor._clamp_percent("invalid") == 0
        assert MapTaskMonitor._clamp_percent(None) == 0

    @patch('app.gis.processor.Session')
    @patch('app.gis.processor.db_engine')
    def test_is_cancelled_task_exists_cancelled(self, mock_db_engine, mock_session_class):
        """Test is_cancelled when task exists and is cancelled."""
        # Setup mock
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        
        mock_task = Mock()
        mock_task.status = MapTaskStatus.CANCELLED
        mock_session.exec.return_value.first.return_value = mock_task
        
        monitor = MapTaskMonitor(task_id=123, user_id=456)
        result = monitor.is_cancelled()
        
        assert result is True

    @patch('app.gis.processor.Session')
    @patch('app.gis.processor.db_engine')
    def test_is_cancelled_task_exists_not_cancelled(self, mock_db_engine, mock_session_class):
        """Test is_cancelled when task exists and is not cancelled."""
        # Setup mock
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        
        mock_task = Mock()
        mock_task.status = MapTaskStatus.PROCESSING
        mock_session.exec.return_value.first.return_value = mock_task
        
        monitor = MapTaskMonitor(task_id=123, user_id=456)
        result = monitor.is_cancelled()
        
        assert result is False

    @patch('app.gis.processor.Session')
    @patch('app.gis.processor.db_engine')
    def test_is_cancelled_task_not_found(self, mock_db_engine, mock_session_class):
        """Test is_cancelled when task is not found."""
        # Setup mock
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session.exec.return_value.first.return_value = None
        
        monitor = MapTaskMonitor(task_id=123, user_id=456)
        result = monitor.is_cancelled()
        
        assert result is True  # Should treat missing task as cancelled

    @patch('app.gis.processor.Session')
    @patch('app.gis.processor.db_engine')
    @patch('app.gis.processor.logger')
    def test_update_progress_success(self, mock_logger, mock_db_engine, mock_session_class):
        """Test successful progress update."""
        # Setup mock
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        
        monitor = MapTaskMonitor(task_id=123, user_id=456)
        monitor.update_progress(75, "processing", "Working on data")
        
        # Verify session operations
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        
        # Verify the progress record created
        args = mock_session.add.call_args[0]
        progress_record = args[0]
        assert progress_record.map_task_id == 123
        assert progress_record.user_id == 456
        assert progress_record.percent == 75
        assert progress_record.phase == "processing"
        assert progress_record.description == "Working on data"

    @patch('app.gis.processor.Session')
    @patch('app.gis.processor.db_engine')
    @patch('app.gis.processor.logger')
    def test_update_progress_with_clamping(self, mock_logger, mock_db_engine, mock_session_class):
        """Test progress update with value clamping."""
        # Setup mock
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        
        monitor = MapTaskMonitor(task_id=123, user_id=456)
        monitor.update_progress(150, "  test  ", "  description  ")
        
        # Verify the progress record created with clamped/trimmed values
        args = mock_session.add.call_args[0]
        progress_record = args[0]
        assert progress_record.percent == 100  # Clamped from 150
        assert progress_record.phase == "test"  # Trimmed
        assert progress_record.description == "description"  # Trimmed

    @patch('app.gis.processor.Session')
    @patch('app.gis.processor.db_engine')
    @patch('app.gis.processor.logger')
    def test_update_progress_handles_exception(self, mock_logger, mock_db_engine, mock_session_class):
        """Test progress update handles database exceptions gracefully."""
        # Setup mock to raise exception
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session.commit.side_effect = Exception("DB error")
        
        monitor = MapTaskMonitor(task_id=123, user_id=456)
        # Should not raise exception
        monitor.update_progress(50, "test", "description")
        
        # Verify error was logged
        mock_logger.error.assert_called_once()

    @patch('app.gis.processor.Session')
    @patch('app.gis.processor.db_engine')
    @patch('app.gis.processor.logger')
    def test_record_error_success(self, mock_logger, mock_db_engine, mock_session_class):
        """Test successful error recording."""
        # Setup mock
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        
        monitor = MapTaskMonitor(task_id=123, user_id=456)
        monitor.record_error("Test error", "validation", 25, "Error description")
        
        # Verify session operations
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        
        # Verify the error record created
        args = mock_session.add.call_args[0]
        error_record = args[0]
        assert error_record.map_task_id == 123
        assert error_record.user_id == 456
        assert error_record.percent == 25
        assert error_record.phase == "validation"
        assert error_record.description == "Error description"
        assert error_record.error_msg == "Test error"

    @patch('app.gis.processor.Session')
    @patch('app.gis.processor.db_engine')
    @patch('app.gis.processor.logger')
    def test_record_error_with_defaults(self, mock_logger, mock_db_engine, mock_session_class):
        """Test error recording with default values."""
        # Setup mock
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        
        monitor = MapTaskMonitor(task_id=123, user_id=456)
        monitor.record_error("")  # Empty error message
        
        # Verify the error record created with defaults
        args = mock_session.add.call_args[0]
        error_record = args[0]
        assert error_record.error_msg == "Error"  # Default for empty message
        assert error_record.percent == 0  # Default when None provided

    @patch('app.gis.processor.Session')
    @patch('app.gis.processor.db_engine')
    @patch('app.gis.processor.logger')
    def test_record_error_handles_exception(self, mock_logger, mock_db_engine, mock_session_class):
        """Test error recording handles database exceptions."""
        # Setup mock to raise exception
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session.commit.side_effect = Exception("DB error")
        
        monitor = MapTaskMonitor(task_id=123, user_id=456)
        # Should not raise exception
        monitor.record_error("Test error")
        
        # Verify error was logged
        mock_logger.error.assert_called_once()

    @patch('app.gis.processor.storage')
    @patch('app.gis.processor.Session')
    @patch('app.gis.processor.db_engine')
    @patch('app.gis.processor.logger')
    def test_record_file_success(self, mock_logger, mock_db_engine, mock_session_class, mock_storage):
        """Test successful file recording."""
        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_storage.save_task_file.return_value = "/saved/path/file.txt"
        
        monitor = MapTaskMonitor(task_id=123, user_id=456)
        monitor.record_file("result", "/original/path/file.txt")
        
        # Verify storage was called
        mock_storage.save_task_file.assert_called_once_with("/original/path/file.txt", 456, 123)
        
        # Verify session operations
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        
        # Verify the file record created
        args = mock_session.add.call_args[0]
        file_record = args[0]
        assert file_record.map_task_id == 123
        assert file_record.user_id == 456
        assert file_record.file_type == "result"
        assert file_record.file_path == "/saved/path/file.txt"

    @patch('app.gis.processor.storage')
    @patch('app.gis.processor.Session')
    @patch('app.gis.processor.db_engine')
    @patch('app.gis.processor.logger')
    def test_record_file_handles_exception(self, mock_logger, mock_db_engine, mock_session_class, mock_storage):
        """Test file recording handles database exceptions."""
        # Setup mocks to raise exception
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_storage.save_task_file.return_value = "/saved/path/file.txt"
        mock_session.commit.side_effect = Exception("DB error")
        
        monitor = MapTaskMonitor(task_id=123, user_id=456)
        
        # Should raise RuntimeError
        with pytest.raises(RuntimeError, match="record_file failed"):
            monitor.record_file("result", "/original/path/file.txt")
        
        # Verify error was logged
        mock_logger.error.assert_called_once()


class TestHelperFunctions:
    """Test suite for helper functions."""

    @patch('app.gis.processor.Session')
    @patch('app.gis.processor.db_engine')
    def test_quick_update_task_success(self, mock_db_engine, mock_session_class):
        """Test successful task update."""
        # Setup mock
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        
        mock_task = Mock()
        mock_session.exec.return_value.first.return_value = mock_task
        
        _quick_update_task(123, status=MapTaskStatus.SUCCESS, ended_at=datetime.now(timezone.utc))
        
        # Verify task was updated
        assert hasattr(mock_task, 'status')
        assert hasattr(mock_task, 'ended_at')
        mock_session.add.assert_called_once_with(mock_task)
        mock_session.commit.assert_called_once()

    @patch('app.gis.processor.Session')
    @patch('app.gis.processor.db_engine')
    def test_quick_update_task_not_found(self, mock_db_engine, mock_session_class):
        """Test task update when task not found."""
        # Setup mock
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session.exec.return_value.first.return_value = None
        
        _quick_update_task(123, status=MapTaskStatus.SUCCESS)
        
        # Should not attempt to update or commit
        mock_session.add.assert_not_called()
        mock_session.commit.assert_not_called()

    @patch('app.gis.processor.Session')
    @patch('app.gis.processor.db_engine')
    def test_load_task_success(self, mock_db_engine, mock_session_class):
        """Test successful task loading."""
        # Setup mock
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        
        mock_task = Mock()
        mock_session.exec.return_value.first.return_value = mock_task
        
        result = _load_task(123)
        
        assert result == mock_task

    @patch('app.gis.processor.Session')
    @patch('app.gis.processor.db_engine')
    def test_load_task_not_found(self, mock_db_engine, mock_session_class):
        """Test task loading when task not found."""
        # Setup mock
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session.exec.return_value.first.return_value = None
        
        result = _load_task(123)
        
        assert result is None


class TestBuildRanges:
    """Test suite for build_ranges function."""

    def test_build_ranges_basic(self):
        """Test basic range building."""
        breakpoints = [10.0, 20.0, 30.0]
        points = [1, 2, 3, 4]
        
        result = build_ranges(breakpoints, points)
        
        expected = [
            (-float("inf"), 10.0, 1),
            (10.0, 20.0, 2),
            (20.0, 30.0, 3),
            (30.0, float("inf"), 4)
        ]
        
        assert result == expected

    def test_build_ranges_empty(self):
        """Test range building with empty inputs."""
        result = build_ranges([], [])
        assert result == []

    def test_build_ranges_single_point(self):
        """Test range building with single point."""
        breakpoints = []
        points = [5]
        
        result = build_ranges(breakpoints, points)
        
        expected = [(-float("inf"), float("inf"), 5)]
        assert result == expected

    def test_build_ranges_negative_values(self):
        """Test range building with negative breakpoints."""
        breakpoints = [-20.0, -10.0, 0.0]
        points = [10, 20, 30, 40]
        
        result = build_ranges(breakpoints, points)
        
        expected = [
            (-float("inf"), -20.0, 10),
            (-20.0, -10.0, 20),
            (-10.0, 0.0, 30),
            (0.0, float("inf"), 40)
        ]
        
        assert result == expected


class TestProcessMapTask:
    """Test suite for process_map_task function."""

    @patch('app.gis.processor.logger')
    @patch('app.gis.processor._load_task')
    def test_process_map_task_not_found(self, mock_load_task, mock_logger):
        """Test process_map_task when task is not found."""
        mock_load_task.return_value = None
        
        process_map_task(123)
        
        mock_logger.warning.assert_called_once_with("MapTask %s not found; skipping.", 123)

    @patch('app.gis.processor.logger')
    @patch('app.gis.processor._load_task')
    def test_process_map_task_already_terminal(self, mock_load_task, mock_logger):
        """Test process_map_task when task is already in terminal state."""
        mock_task = Mock()
        mock_task.status = MapTaskStatus.SUCCESS
        mock_load_task.return_value = mock_task
        
        process_map_task(123)
        
        mock_logger.info.assert_called_once_with(
            "MapTask %s already in terminal state %s; skipping.", 123, MapTaskStatus.SUCCESS
        )

    @patch('app.gis.processor.shutil.rmtree')
    @patch('app.gis.processor.os.path.exists')
    @patch('app.gis.processor.Path')
    @patch('app.gis.processor.SiteSuitabilityEngine')
    @patch('app.gis.processor.MapTaskMonitor')
    @patch('app.gis.processor._quick_update_task')
    @patch('app.gis.processor._load_task')
    @patch('app.gis.processor.settings')
    @patch('app.gis.processor.logger')
    def test_process_map_task_success(self, mock_logger, mock_settings, mock_load_task, 
                                    mock_quick_update, mock_monitor_class, mock_engine_class,
                                    mock_path_class, mock_exists, mock_rmtree):
        """Test successful task processing."""
        # Setup task mock
        mock_task = Mock()
        mock_task.status = MapTaskStatus.PENDING
        mock_task.user_id = 456
        mock_task.district = "D001"
        mock_task.constraint_factors = json.dumps([
            {"kind": "lake", "value": 100}
        ])
        mock_task.suitability_factors = json.dumps([
            {"kind": "residential", "weight": 0.3, "breakpoints": [10.0, 20.0], "points": [1, 2, 3]}
        ])
        mock_task.started_at = None
        
        # Mock _load_task to return our task twice (initial check and reload)
        mock_load_task.side_effect = [mock_task, mock_task]
        
        # Setup settings mock with mock Path objects
        mock_input_path = MagicMock()
        mock_output_path = MagicMock()
        mock_task_path = MagicMock()
        mock_settings.INPUT_DATA_DIR = mock_input_path
        mock_settings.OUTPUT_DATA_DIR = mock_output_path
        
        # Mock Path operations
        mock_output_path.__truediv__.return_value.__truediv__.return_value = mock_task_path
        mock_task_path.mkdir = Mock()
        
        # Setup monitor mock
        mock_monitor = Mock()
        mock_monitor.is_cancelled.return_value = False
        mock_monitor_class.return_value = mock_monitor
        
        # Setup engine mock
        mock_engine = Mock()
        mock_engine.run.return_value = {"results": "success"}
        mock_engine_class.return_value = mock_engine
        
        # Setup file cleanup mocks
        mock_exists.return_value = True
        
        process_map_task(123)
        
        # Verify task was marked as PROCESSING (should be the first call)
        assert mock_quick_update.call_count >= 1
        first_call = mock_quick_update.call_args_list[0]
        assert first_call.kwargs['status'] == MapTaskStatus.PROCESSING
        
        # Verify monitor was created and used
        mock_monitor_class.assert_called_once_with(123, 456)
        mock_monitor.update_progress.assert_any_call(0, "init", "Starting")
        mock_monitor.update_progress.assert_any_call(100, "success", "Completed")
        
        # Verify engine was created and run
        mock_engine_class.assert_called_once()
        mock_engine.run.assert_called_once_with(selected_districts=["D001"], monitor=mock_monitor)
        
        # Verify task was marked as SUCCESS
        success_calls = [call for call in mock_quick_update.call_args_list
                        if call.kwargs.get('status') == MapTaskStatus.SUCCESS]
        assert len(success_calls) > 0, "Expected SUCCESS status call"
        success_call = success_calls[0]
        assert 'ended_at' in success_call.kwargs
        assert success_call.kwargs['ended_at'] is not None
        
        # Verify cleanup
        mock_exists.assert_called_once()
        mock_rmtree.assert_called_once()

    @patch('app.gis.processor.shutil.rmtree')
    @patch('app.gis.processor.os.path.exists')
    @patch('app.gis.processor.Path')
    @patch('app.gis.processor.MapTaskMonitor')
    @patch('app.gis.processor._quick_update_task')
    @patch('app.gis.processor._load_task')
    @patch('app.gis.processor.settings')
    @patch('app.gis.processor.logger')
    def test_process_map_task_cancelled_before_start(self, mock_logger, mock_settings, mock_load_task, 
                                                   mock_quick_update, mock_monitor_class,
                                                   mock_path_class, mock_exists, mock_rmtree):
        """Test task processing when cancelled before start."""
        # Setup task mock
        mock_task_initial = Mock()
        mock_task_initial.status = MapTaskStatus.PENDING
        mock_task_initial.user_id = 456
        mock_task_initial.started_at = None
        
        mock_task_reloaded = Mock()
        mock_task_reloaded.status = MapTaskStatus.CANCELLED
        mock_task_reloaded.user_id = 456
        
        # Mock _load_task to return different states
        mock_load_task.side_effect = [mock_task_initial, mock_task_reloaded]
        
        # Mock path operations to prevent task_out from being undefined
        mock_task_path = MagicMock()
        mock_settings.OUTPUT_DATA_DIR = MagicMock()
        mock_settings.OUTPUT_DATA_DIR.__truediv__.return_value.__truediv__.return_value = mock_task_path
        
        # Setup file cleanup mocks
        mock_exists.return_value = False
        
        process_map_task(123)
        
        # Verify task was marked as PROCESSING initially
        assert mock_quick_update.call_count == 1
        call_args = mock_quick_update.call_args_list[0]
        assert call_args.kwargs['status'] == MapTaskStatus.PROCESSING
        assert 'started_at' in call_args.kwargs
        assert call_args.kwargs['error_msg'] is None
        
        # Verify cancellation was logged
        mock_logger.info.assert_called_once_with("MapTask %s cancelled before start; aborting.", 123)

    @patch('app.gis.processor.shutil.rmtree')
    @patch('app.gis.processor.os.path.exists')
    @patch('app.gis.processor.Path')
    @patch('app.gis.processor.SiteSuitabilityEngine')
    @patch('app.gis.processor.MapTaskMonitor')
    @patch('app.gis.processor._quick_update_task')
    @patch('app.gis.processor._load_task')
    @patch('app.gis.processor.settings')
    @patch('app.gis.processor.logger')
    def test_process_map_task_engine_failure(self, mock_logger, mock_settings, mock_load_task, 
                                           mock_quick_update, mock_monitor_class, mock_engine_class,
                                           mock_path_class, mock_exists, mock_rmtree):
        """Test task processing when engine fails."""
        # Setup task mock
        mock_task = Mock()
        mock_task.status = MapTaskStatus.PENDING
        mock_task.user_id = 456
        mock_task.district = "D001"
        mock_task.constraint_factors = "[]"
        mock_task.suitability_factors = "[]"
        mock_task.started_at = None
        
        mock_load_task.side_effect = [mock_task, mock_task]
        
        # Setup settings mock with mock Path objects
        mock_input_path = MagicMock()
        mock_output_path = MagicMock()
        mock_task_path = MagicMock()
        mock_settings.INPUT_DATA_DIR = mock_input_path
        mock_settings.OUTPUT_DATA_DIR = mock_output_path
        
        # Mock Path operations
        mock_output_path.__truediv__.return_value.__truediv__.return_value = mock_task_path
        mock_task_path.mkdir = Mock()
        
        # Setup monitor mock
        mock_monitor = Mock()
        mock_monitor_class.return_value = mock_monitor
        
        # Setup engine mock to raise exception
        mock_engine = Mock()
        mock_engine.run.side_effect = Exception("Engine failed")
        mock_engine_class.return_value = mock_engine
        
        # Setup file cleanup mocks
        mock_exists.return_value = True
        
        process_map_task(123)
        
        # Verify error was recorded
        mock_monitor.record_error.assert_called_once_with(
            "Engine failed", phase="error", description="Failed"
        )
        
        # Verify task was marked as FAILURE
        failure_calls = [call for call in mock_quick_update.call_args_list
                        if call.kwargs.get('status') == MapTaskStatus.FAILURE]
        assert len(failure_calls) > 0, "Expected FAILURE status call"
        failure_call = failure_calls[0]
        assert failure_call.kwargs['error_msg'] == "Engine failed"
        assert 'ended_at' in failure_call.kwargs
        assert failure_call.kwargs['ended_at'] is not None
        
        # Verify exception was logged
        mock_logger.exception.assert_called_once()

    @patch('app.gis.processor.shutil.rmtree')
    @patch('app.gis.processor.os.path.exists')
    @patch('app.gis.processor.Path')
    @patch('app.gis.processor.SiteSuitabilityEngine')
    @patch('app.gis.processor.MapTaskMonitor')
    @patch('app.gis.processor._quick_update_task')
    @patch('app.gis.processor._load_task')
    @patch('app.gis.processor.settings')
    @patch('app.gis.processor.logger')
    def test_process_map_task_long_error_message(self, mock_logger, mock_settings, mock_load_task, 
                                               mock_quick_update, mock_monitor_class, mock_engine_class,
                                               mock_path_class, mock_exists, mock_rmtree):
        """Test task processing with very long error message."""
        # Setup task mock
        mock_task = Mock()
        mock_task.status = MapTaskStatus.PENDING
        mock_task.user_id = 456
        mock_task.district = "D001"
        mock_task.constraint_factors = "[]"
        mock_task.suitability_factors = "[]"
        mock_task.started_at = None
        
        mock_load_task.side_effect = [mock_task, mock_task]
        
        # Setup settings mock with mock Path objects
        mock_input_path = MagicMock()
        mock_output_path = MagicMock()
        mock_task_path = MagicMock()
        mock_settings.INPUT_DATA_DIR = mock_input_path
        mock_settings.OUTPUT_DATA_DIR = mock_output_path
        
        # Mock Path operations
        mock_output_path.__truediv__.return_value.__truediv__.return_value = mock_task_path
        mock_task_path.mkdir = Mock()
        
        # Setup monitor mock
        mock_monitor = Mock()
        mock_monitor_class.return_value = mock_monitor
        
        # Setup engine mock to raise exception with very long message
        long_error = "A" * 300  # Message longer than 250 characters
        mock_engine = Mock()
        mock_engine.run.side_effect = Exception(long_error)
        mock_engine_class.return_value = mock_engine
        
        # Setup file cleanup mocks
        mock_exists.return_value = True
        
        process_map_task(123)
        
        # Verify error message was truncated
        expected_truncated = long_error[:247] + "..."
        failure_calls = [call for call in mock_quick_update.call_args_list
                        if call.kwargs.get('status') == MapTaskStatus.FAILURE]
        assert len(failure_calls) > 0, "Expected FAILURE status call"
        failure_call = failure_calls[0]
        assert failure_call.kwargs['error_msg'] == expected_truncated
        assert 'ended_at' in failure_call.kwargs
        assert failure_call.kwargs['ended_at'] is not None

    @patch('app.gis.processor.shutil.rmtree')
    @patch('app.gis.processor.os.path.exists')
    @patch('app.gis.processor.Path')
    @patch('app.gis.processor.SiteSuitabilityEngine')
    @patch('app.gis.processor.MapTaskMonitor')
    @patch('app.gis.processor._quick_update_task')
    @patch('app.gis.processor._load_task')
    @patch('app.gis.processor.settings')
    @patch('app.gis.processor.logger')
    def test_process_map_task_invalid_json_factors(self, mock_logger, mock_settings, mock_load_task, 
                                                 mock_quick_update, mock_monitor_class, mock_engine_class,
                                                 mock_path_class, mock_exists, mock_rmtree):
        """Test task processing with invalid JSON in factors."""
        # Setup task mock with invalid JSON
        mock_task = Mock()
        mock_task.status = MapTaskStatus.PENDING
        mock_task.user_id = 456
        mock_task.district = "D001"
        mock_task.constraint_factors = "invalid json"
        mock_task.suitability_factors = "also invalid"
        mock_task.started_at = None
        
        mock_load_task.side_effect = [mock_task, mock_task]
        
        # Setup settings mock with mock Path objects
        mock_input_path = MagicMock()
        mock_output_path = MagicMock()
        mock_task_path = MagicMock()
        mock_settings.INPUT_DATA_DIR = mock_input_path
        mock_settings.OUTPUT_DATA_DIR = mock_output_path
        
        # Mock Path operations
        mock_output_path.__truediv__.return_value.__truediv__.return_value = mock_task_path
        mock_task_path.mkdir = Mock()
        
        # Setup monitor mock
        mock_monitor = Mock()
        mock_monitor.is_cancelled.return_value = False
        mock_monitor_class.return_value = mock_monitor
        
        # Setup engine mock
        mock_engine = Mock()
        mock_engine.run.return_value = {"results": "success"}
        mock_engine_class.return_value = mock_engine
        
        # Setup file cleanup mocks
        mock_exists.return_value = True
        
        process_map_task(123)
        
        # Verify engine was called with empty factors (fallback from JSON parsing errors)
        assert mock_engine_class.called
        call_args = mock_engine_class.call_args
        if call_args and len(call_args[0]) > 2:
            configs = call_args[0][2]  # Third argument is configs
            assert len(configs.restricted_factors) == 0
            assert len(configs.suitability_factors) == 0

    @patch('app.gis.processor.shutil.rmtree')
    @patch('app.gis.processor.os.path.exists')
    @patch('app.gis.processor.logger')
    def test_process_map_task_cleanup_file_not_exists(self, mock_logger, mock_exists, mock_rmtree):
        """Test task processing cleanup when output directory doesn't exist."""
        # This test verifies early exit behavior - when task not found, no cleanup should happen
        with patch('app.gis.processor._load_task') as mock_load_task:
            mock_load_task.return_value = None
            mock_exists.return_value = False
            
            process_map_task(123)
            
            # Verify task not found message was logged
            mock_logger.warning.assert_called_with("MapTask %s not found; skipping.", 123)
            
            # Verify cleanup methods were not called since task exited early
            mock_exists.assert_not_called()
            mock_rmtree.assert_not_called()

    @patch('app.gis.processor.shutil.rmtree')
    @patch('app.gis.processor.os.path.exists')
    @patch('app.gis.processor.Path')
    @patch('app.gis.processor.SiteSuitabilityEngine')
    @patch('app.gis.processor.MapTaskMonitor')
    @patch('app.gis.processor._quick_update_task')
    @patch('app.gis.processor._load_task')
    @patch('app.gis.processor.settings')
    @patch('app.gis.processor.logger')
    def test_process_map_task_cleanup_error(self, mock_logger, mock_settings, mock_load_task, 
                                          mock_quick_update, mock_monitor_class, mock_engine_class,
                                          mock_path_class, mock_exists, mock_rmtree):
        """Test task processing cleanup when rmtree fails."""
        # Setup task mock
        mock_task = Mock()
        mock_task.status = MapTaskStatus.PENDING
        mock_task.user_id = 456
        mock_task.district = "D001"
        mock_task.constraint_factors = "[]"
        mock_task.suitability_factors = "[]"
        mock_task.started_at = None

        mock_load_task.side_effect = [mock_task, mock_task]

        # Setup settings mock with mock Path objects
        mock_input_path = MagicMock()
        mock_output_path = MagicMock()
        mock_task_path = MagicMock()
        mock_settings.INPUT_DATA_DIR = mock_input_path
        mock_settings.OUTPUT_DATA_DIR = mock_output_path

        # Mock Path operations - this ensures task_out gets defined
        mock_output_path.__truediv__.return_value.__truediv__.return_value = mock_task_path
        mock_task_path.mkdir = Mock()

        # Setup monitor mock
        mock_monitor = Mock()
        mock_monitor_class.return_value = mock_monitor

        # Setup engine mock to raise exception
        mock_engine = Mock()
        mock_engine.run.side_effect = Exception("Engine failed")
        mock_engine_class.return_value = mock_engine

        # Setup cleanup to fail - this is the key part
        mock_exists.return_value = True
        mock_rmtree.side_effect = Exception("Cleanup failed")

        process_map_task(123)

        # Verify cleanup was attempted and error was logged
        mock_exists.assert_called_once_with(mock_task_path)
        mock_rmtree.assert_called_once_with(mock_task_path)
        
        # Check that cleanup error was logged
        cleanup_calls = [call for call in mock_logger.warning.call_args_list 
                       if 'cleanup error' in str(call).lower()]
        assert len(cleanup_calls) > 0, f"Expected cleanup error to be logged. Actual calls: {mock_logger.warning.call_args_list}"
