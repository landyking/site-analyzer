"""
Unit tests for app.api.routes._mappers module.

Tests mapping functions from database models to API models,
while avoiding circular import issues through strategic mocking.
"""
import pytest
import json
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock

# Import the module under test
from app.api.routes._mappers import (
    _ensure_list,
    as_aware_utc,
    _status_desc,
    to_map_task,
    to_map_task_details,
    _DISTRICT_CODE_TO_NAME,
)

from app.models import MapTaskStatus, ConstraintFactor, SuitabilityFactor


class TestEnsureList:
    """Test _ensure_list utility function."""
    
    def test_ensure_list_with_json_string(self):
        """Test _ensure_list parses JSON string to list."""
        json_str = '[{"kind": "lake", "value": 100}]'
        result = _ensure_list(json_str)
        expected = [{"kind": "lake", "value": 100}]
        assert result == expected
    
    def test_ensure_list_with_already_list(self):
        """Test _ensure_list returns list unchanged."""
        input_list = [{"kind": "residential", "weight": 0.3}]
        result = _ensure_list(input_list)
        assert result == input_list
    
    def test_ensure_list_with_empty_json_string(self):
        """Test _ensure_list handles empty JSON array string."""
        result = _ensure_list("[]")
        assert result == []
    
    def test_ensure_list_with_none(self):
        """Test _ensure_list handles None input."""
        result = _ensure_list(None)
        assert result is None
    
    def test_ensure_list_with_dict(self):
        """Test _ensure_list handles dict input."""
        input_dict = {"key": "value"}
        result = _ensure_list(input_dict)
        assert result == input_dict


class TestAsAwareUtc:
    """Test as_aware_utc datetime conversion function."""
    
    def test_as_aware_utc_with_none(self):
        """Test as_aware_utc returns None for None input."""
        result = as_aware_utc(None)
        assert result is None
    
    def test_as_aware_utc_with_naive_datetime(self):
        """Test as_aware_utc adds UTC timezone to naive datetime."""
        naive_dt = datetime(2023, 1, 15, 10, 30, 45)
        result = as_aware_utc(naive_dt)
        expected = datetime(2023, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
        assert result == expected
        assert result.tzinfo == timezone.utc
    
    def test_as_aware_utc_with_utc_datetime(self):
        """Test as_aware_utc handles UTC datetime correctly."""
        utc_dt = datetime(2023, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
        result = as_aware_utc(utc_dt)
        assert result == utc_dt
        assert result.tzinfo == timezone.utc
    
    def test_as_aware_utc_with_different_timezone(self):
        """Test as_aware_utc converts different timezone to UTC."""
        from datetime import timedelta
        other_tz = timezone(timedelta(hours=5))
        other_dt = datetime(2023, 1, 15, 15, 30, 45, tzinfo=other_tz)
        result = as_aware_utc(other_dt)
        expected = datetime(2023, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
        assert result == expected
        assert result.tzinfo == timezone.utc


class TestStatusDesc:
    """Test _status_desc status description function."""
    
    def test_status_desc_pending(self):
        """Test _status_desc returns 'Pending' for PENDING status."""
        result = _status_desc(MapTaskStatus.PENDING)
        assert result == "Pending"
    
    def test_status_desc_processing(self):
        """Test _status_desc returns 'Processing' for PROCESSING status."""
        result = _status_desc(MapTaskStatus.PROCESSING)
        assert result == "Processing"
    
    def test_status_desc_success(self):
        """Test _status_desc returns 'Success' for SUCCESS status."""
        result = _status_desc(MapTaskStatus.SUCCESS)
        assert result == "Success"
    
    def test_status_desc_failure(self):
        """Test _status_desc returns 'Failure' for FAILURE status."""
        result = _status_desc(MapTaskStatus.FAILURE)
        assert result == "Failure"
    
    def test_status_desc_cancelled(self):
        """Test _status_desc returns 'Cancelled' for CANCELLED status."""
        result = _status_desc(MapTaskStatus.CANCELLED)
        assert result == "Cancelled"
    
    def test_status_desc_invalid_status(self):
        """Test _status_desc returns None for invalid status."""
        result = _status_desc(999)
        assert result is None
    
    def test_status_desc_non_integer(self):
        """Test _status_desc handles non-integer input gracefully."""
        result = _status_desc("invalid")
        assert result is None


class TestDistrictCodeToName:
    """Test district code to name mapping."""
    
    def test_district_code_to_name_contains_expected_districts(self):
        """Test district mapping contains expected entries."""
        assert "063" in _DISTRICT_CODE_TO_NAME
        assert _DISTRICT_CODE_TO_NAME["063"] == "Ashburton District"
        assert "076" in _DISTRICT_CODE_TO_NAME
        assert _DISTRICT_CODE_TO_NAME["076"] == "Auckland"
    
    def test_district_code_to_name_is_dict(self):
        """Test district mapping is a dictionary."""
        assert isinstance(_DISTRICT_CODE_TO_NAME, dict)
        assert len(_DISTRICT_CODE_TO_NAME) > 0


class TestToMapTask:
    """Test to_map_task mapping function."""
    
    def test_to_map_task_success_with_user(self):
        """Test to_map_task maps data correctly with user found."""
        # Mock session and crud
        mock_session = Mock()
        mock_user = Mock()
        mock_user.email = "test@example.com"
        
        # Mock MapTaskDB data
        mock_data = Mock()
        mock_data.id = 123
        mock_data.name = "Test Task"
        mock_data.user_id = 456
        mock_data.district = "063"
        mock_data.status = MapTaskStatus.SUCCESS
        mock_data.started_at = datetime(2023, 1, 15, 10, 0, 0)
        mock_data.ended_at = datetime(2023, 1, 15, 11, 0, 0)
        mock_data.created_at = datetime(2023, 1, 15, 9, 0, 0)
        
        with patch('app.api.routes._mappers.crud') as mock_crud:
            mock_crud.get_user_by_id.return_value = mock_user
            
            result = to_map_task(mock_session, mock_data)
            
            assert result.id == 123
            assert result.name == "Test Task"
            assert result.user_id == 456
            assert result.user_email == "test@example.com"
            assert result.district_code == "063"
            assert result.district_name == "Ashburton District"
            assert result.status == MapTaskStatus.SUCCESS
            assert result.status_desc == "Success"
            assert result.started_at == datetime(2023, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
            assert result.ended_at == datetime(2023, 1, 15, 11, 0, 0, tzinfo=timezone.utc)
            assert result.created_at == datetime(2023, 1, 15, 9, 0, 0, tzinfo=timezone.utc)
            
            mock_crud.get_user_by_id.assert_called_once_with(session=mock_session, user_id=456)
    
    def test_to_map_task_success_without_user(self):
        """Test to_map_task handles missing user gracefully."""
        mock_session = Mock()
        
        mock_data = Mock()
        mock_data.id = 123
        mock_data.name = "Test Task"
        mock_data.user_id = 456
        mock_data.district = "076"
        mock_data.status = MapTaskStatus.PENDING
        mock_data.started_at = None
        mock_data.ended_at = None
        mock_data.created_at = datetime(2023, 1, 15, 9, 0, 0)
        
        with patch('app.api.routes._mappers.crud') as mock_crud:
            mock_crud.get_user_by_id.return_value = None
            
            result = to_map_task(mock_session, mock_data)
            
            assert result.user_email is None
            assert result.district_name == "Auckland"
            assert result.status_desc == "Pending"
            assert result.started_at is None
            assert result.ended_at is None
    
    def test_to_map_task_crud_exception(self):
        """Test to_map_task handles crud exception gracefully."""
        mock_session = Mock()
        
        mock_data = Mock()
        mock_data.id = 123
        mock_data.name = "Test Task"
        mock_data.user_id = 456
        mock_data.district = "999"  # Unknown district
        mock_data.status = MapTaskStatus.FAILURE
        mock_data.started_at = datetime(2023, 1, 15, 10, 0, 0)
        mock_data.ended_at = datetime(2023, 1, 15, 11, 0, 0)
        mock_data.created_at = datetime(2023, 1, 15, 9, 0, 0)
        
        with patch('app.api.routes._mappers.crud') as mock_crud:
            mock_crud.get_user_by_id.side_effect = Exception("Database error")
            
            result = to_map_task(mock_session, mock_data)
            
            assert result.user_email is None
            assert result.district_name is None  # Unknown district code
            assert result.status_desc == "Failure"
    
    def test_to_map_task_with_timezone_aware_dates(self):
        """Test to_map_task handles timezone-aware dates correctly."""
        mock_session = Mock()
        
        # Create timezone-aware datetimes
        from datetime import timedelta
        other_tz = timezone(timedelta(hours=5))
        
        mock_data = Mock()
        mock_data.id = 123
        mock_data.name = "Test Task"
        mock_data.user_id = 456
        mock_data.district = "063"
        mock_data.status = MapTaskStatus.SUCCESS
        mock_data.started_at = datetime(2023, 1, 15, 15, 0, 0, tzinfo=other_tz)
        mock_data.ended_at = datetime(2023, 1, 15, 16, 0, 0, tzinfo=other_tz)
        mock_data.created_at = datetime(2023, 1, 15, 14, 0, 0, tzinfo=other_tz)
        
        with patch('app.api.routes._mappers.crud') as mock_crud:
            mock_crud.get_user_by_id.return_value = None
            
            result = to_map_task(mock_session, mock_data)
            
            # Should be converted to UTC
            assert result.started_at == datetime(2023, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
            assert result.ended_at == datetime(2023, 1, 15, 11, 0, 0, tzinfo=timezone.utc)
            assert result.created_at == datetime(2023, 1, 15, 9, 0, 0, tzinfo=timezone.utc)


class TestToMapTaskDetails:
    """Test to_map_task_details mapping function."""
    
    def test_to_map_task_details_success(self):
        """Test to_map_task_details maps data correctly with files."""
        mock_session = Mock()
        mock_user = Mock()
        mock_user.email = "test@example.com"
        
        # Mock MapTaskDB data
        mock_data = Mock()
        mock_data.id = 123
        mock_data.name = "Test Task"
        mock_data.user_id = 456
        mock_data.district = "063"
        mock_data.status = MapTaskStatus.SUCCESS
        mock_data.started_at = datetime(2023, 1, 15, 10, 0, 0)
        mock_data.ended_at = datetime(2023, 1, 15, 11, 0, 0)
        mock_data.created_at = datetime(2023, 1, 15, 9, 0, 0)
        mock_data.constraint_factors = '[{"kind": "lakes", "value": 100}]'
        mock_data.suitability_factors = '[{"kind": "slope", "weight": 0.3, "breakpoints": [10.0, 20.0], "points": [1, 2, 3]}]'
        
        # Mock file data
        mock_file_db = Mock()
        mock_file_db.model_dump.return_value = {
            "id": 1,
            "map_task_id": 123,
            "file_path": "test/path/file.shp",
            "file_type": "shapefile",
            "created_at": datetime(2023, 1, 15, 9, 30, 0)
        }
        
        with patch('app.api.routes._mappers.crud') as mock_crud, \
             patch('app.api.routes._mappers.storage') as mock_storage:
            
            mock_crud.get_user_by_id.return_value = mock_user
            mock_crud.get_files_by_id.return_value = [mock_file_db]
            mock_storage.generate_presigned_url.return_value = "https://presigned.url/file.shp"
            
            result = to_map_task_details(mock_session, mock_data)
            
            assert result.id == 123
            assert result.name == "Test Task"
            assert result.user_email == "test@example.com"
            assert result.district_name == "Ashburton District"
            assert len(result.files) == 1
            assert result.files[0].file_path == "https://presigned.url/file.shp"
            assert result.constraint_factors == [ConstraintFactor(kind="lakes", value=100.0)]
            assert result.suitability_factors == [SuitabilityFactor(kind="slope", weight=0.3, breakpoints=[10.0, 20.0], points=[1, 2, 3])]
            
            mock_crud.get_files_by_id.assert_called_once_with(
                session=mock_session, user_id=456, map_task_id=123
            )
            mock_storage.generate_presigned_url.assert_called_once_with("test/path/file.shp")
    
    def test_to_map_task_details_no_files(self):
        """Test to_map_task_details handles no files correctly."""
        mock_session = Mock()
        
        mock_data = Mock()
        mock_data.id = 123
        mock_data.name = "Test Task"
        mock_data.user_id = 456
        mock_data.district = "076"
        mock_data.status = MapTaskStatus.PENDING
        mock_data.started_at = None
        mock_data.ended_at = None
        mock_data.created_at = datetime(2023, 1, 15, 9, 0, 0)
        mock_data.constraint_factors = "[]"
        mock_data.suitability_factors = "[]"
        
        with patch('app.api.routes._mappers.crud') as mock_crud, \
             patch('app.api.routes._mappers.storage') as mock_storage:
            
            mock_crud.get_user_by_id.return_value = None
            mock_crud.get_files_by_id.return_value = []
            
            result = to_map_task_details(mock_session, mock_data)
            
            assert result.files == []
            assert result.constraint_factors == []
            assert result.suitability_factors == []
    
    def test_to_map_task_details_with_list_factors(self):
        """Test to_map_task_details handles already parsed factors."""
        mock_session = Mock()
        
        mock_data = Mock()
        mock_data.id = 123
        mock_data.name = "Test Task"
        mock_data.user_id = 456
        mock_data.district = "063"
        mock_data.status = MapTaskStatus.SUCCESS
        mock_data.started_at = datetime(2023, 1, 15, 10, 0, 0)
        mock_data.ended_at = datetime(2023, 1, 15, 11, 0, 0)
        mock_data.created_at = datetime(2023, 1, 15, 9, 0, 0)
        # Already parsed as lists
        mock_data.constraint_factors = [{"kind": "lakes", "value": 100}]
        mock_data.suitability_factors = [{"kind": "slope", "weight": 0.3, "breakpoints": [10.0, 20.0], "points": [1, 2, 3]}]
        
        with patch('app.api.routes._mappers.crud') as mock_crud, \
             patch('app.api.routes._mappers.storage') as mock_storage:
            
            mock_crud.get_user_by_id.return_value = None
            mock_crud.get_files_by_id.return_value = []
            
            result = to_map_task_details(mock_session, mock_data)
            
            assert result.constraint_factors == [ConstraintFactor(kind="lakes", value=100.0)]
            assert result.suitability_factors == [SuitabilityFactor(kind="slope", weight=0.3, breakpoints=[10.0, 20.0], points=[1, 2, 3])]
    
    def test_to_map_task_details_multiple_files(self):
        """Test to_map_task_details handles multiple files correctly."""
        mock_session = Mock()
        
        mock_data = Mock()
        mock_data.id = 123
        mock_data.name = "Test Task"
        mock_data.user_id = 456
        mock_data.district = "063"
        mock_data.status = MapTaskStatus.SUCCESS
        mock_data.started_at = datetime(2023, 1, 15, 10, 0, 0)
        mock_data.ended_at = datetime(2023, 1, 15, 11, 0, 0)
        mock_data.created_at = datetime(2023, 1, 15, 9, 0, 0)
        mock_data.constraint_factors = "[]"
        mock_data.suitability_factors = "[]"
        
        # Mock multiple files
        mock_file1 = Mock()
        mock_file1.model_dump.return_value = {
            "id": 1,
            "map_task_id": 123,
            "file_path": "test/path/file1.shp",
            "file_type": "shapefile",
            "created_at": datetime(2023, 1, 15, 9, 30, 0)
        }
        mock_file2 = Mock()
        mock_file2.model_dump.return_value = {
            "id": 2,
            "map_task_id": 123,
            "file_path": "test/path/file2.tif",
            "file_type": "raster",
            "created_at": datetime(2023, 1, 15, 9, 35, 0)
        }
        
        with patch('app.api.routes._mappers.crud') as mock_crud, \
             patch('app.api.routes._mappers.storage') as mock_storage:
            
            mock_crud.get_user_by_id.return_value = None
            mock_crud.get_files_by_id.return_value = [mock_file1, mock_file2]
            mock_storage.generate_presigned_url.side_effect = [
                "https://presigned.url/file1.shp",
                "https://presigned.url/file2.tif"
            ]
            
            result = to_map_task_details(mock_session, mock_data)
            
            assert len(result.files) == 2
            assert result.files[0].file_path == "https://presigned.url/file1.shp"
            assert result.files[1].file_path == "https://presigned.url/file2.tif"
            assert mock_storage.generate_presigned_url.call_count == 2


class TestEdgeCasesAndIntegration:
    """Test edge cases and integration scenarios."""
    
    def test_ensure_list_invalid_json(self):
        """Test _ensure_list handles invalid JSON gracefully."""
        with pytest.raises(json.JSONDecodeError):
            _ensure_list('{"invalid": json}')
    
    def test_district_code_mapping_completeness(self):
        """Test district code mapping is populated."""
        assert len(_DISTRICT_CODE_TO_NAME) > 50  # Should have many districts
        
        # Test a few known districts
        known_districts = {
            "063": "Ashburton District",
            "076": "Auckland", 
            "001": "Far North District"
        }
        
        for code, name in known_districts.items():
            assert code in _DISTRICT_CODE_TO_NAME
            assert _DISTRICT_CODE_TO_NAME[code] == name
    
    def test_status_desc_all_valid_statuses(self):
        """Test _status_desc works for all valid MapTaskStatus values."""
        valid_statuses = [
            (MapTaskStatus.PENDING, "Pending"),
            (MapTaskStatus.PROCESSING, "Processing"),
            (MapTaskStatus.SUCCESS, "Success"),
            (MapTaskStatus.FAILURE, "Failure"),
            (MapTaskStatus.CANCELLED, "Cancelled"),
        ]
        
        for status, expected in valid_statuses:
            result = _status_desc(status)
            assert result == expected
    
    def test_datetime_conversion_edge_cases(self):
        """Test datetime conversion with various edge cases."""
        # Test epoch datetime
        epoch = datetime(1970, 1, 1, 0, 0, 0)
        result = as_aware_utc(epoch)
        assert result == datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        
        # Test far future datetime
        future = datetime(2100, 12, 31, 23, 59, 59)
        result = as_aware_utc(future)
        assert result == datetime(2100, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        
        # Test with microseconds
        micro = datetime(2023, 1, 15, 10, 30, 45, 123456)
        result = as_aware_utc(micro)
        assert result == datetime(2023, 1, 15, 10, 30, 45, 123456, tzinfo=timezone.utc)
    
    def test_to_map_task_comprehensive_integration(self):
        """Test to_map_task with comprehensive real-world scenario."""
        mock_session = Mock()
        mock_user = Mock()
        mock_user.email = "comprehensive@test.com"
        
        mock_data = Mock()
        mock_data.id = 999
        mock_data.name = "Comprehensive Integration Test"
        mock_data.user_id = 777
        mock_data.district = "072"  # Clutha District
        mock_data.status = MapTaskStatus.PROCESSING
        mock_data.started_at = datetime(2023, 6, 15, 14, 30, 45, 123456)
        mock_data.ended_at = None
        mock_data.created_at = datetime(2023, 6, 15, 14, 25, 30, 654321)
        
        with patch('app.api.routes._mappers.crud') as mock_crud:
            mock_crud.get_user_by_id.return_value = mock_user
            
            result = to_map_task(mock_session, mock_data)
            
            # Verify all fields are correctly mapped
            assert result.id == 999
            assert result.name == "Comprehensive Integration Test"
            assert result.user_id == 777
            assert result.user_email == "comprehensive@test.com"
            assert result.district_code == "072"
            assert result.district_name == "Clutha District"
            assert result.status == MapTaskStatus.PROCESSING
            assert result.status_desc == "Processing"
            assert result.started_at.microsecond == 123456
            assert result.ended_at is None
            assert result.created_at.microsecond == 654321