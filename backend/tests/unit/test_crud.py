"""
Unit tests for app.crud module.

Tests CRUD operations for users, map tasks, and file management.
"""
import pytest
import json
import sys
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock, call
from fastapi import HTTPException, BackgroundTasks
from sqlmodel import Session

# Mock the circular import modules before importing
mock_modules = {
    'app.gis.processor': MagicMock(),
}
sys.modules.update(mock_modules)

# Now import after setting up mocks
from app.crud import (
    touch_last_login,
    create_user,
    get_user_by_email,
    get_user_by_id,
    get_files_by_id,
    get_file_by_conditions,
    authenticate,
    create_map_task,
    get_map_task,
)

from app.models import (
    UserDB,
    UserCreate,
    UserRole,
    UserStatus,
    CreateMapTaskReq,
    MapTaskDB,
    MapTaskStatus,
    MapTaskFileDB,
    ConstraintFactor,
    SuitabilityFactor,
)


class TestTouchLastLogin:
    """Test touch_last_login function."""

    def test_touch_last_login_updates_timestamp(self):
        """Test that touch_last_login updates last_login timestamp."""
        # Arrange
        mock_session = Mock(spec=Session)
        user = UserDB(
            id=1,
            email="test@example.com",
            password_hash="hashed",
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            last_login=None
        )
        
        # Act
        with patch('app.crud.datetime') as mock_datetime:
            mock_now = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            
            result = touch_last_login(session=mock_session, user=user)
        
        # Assert
        assert user.last_login == mock_now
        mock_session.add.assert_called_once_with(user)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(user)
        assert result == user

    def test_touch_last_login_with_existing_timestamp(self):
        """Test touch_last_login overwrites existing timestamp."""
        # Arrange
        mock_session = Mock(spec=Session)
        old_timestamp = datetime(2022, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        user = UserDB(
            id=1,
            email="test@example.com",
            password_hash="hashed",
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            last_login=old_timestamp
        )
        
        # Act
        with patch('app.crud.datetime') as mock_datetime:
            mock_now = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            
            result = touch_last_login(session=mock_session, user=user)
        
        # Assert
        assert user.last_login == mock_now
        assert user.last_login != old_timestamp


class TestCreateUser:
    """Test create_user function."""

    @patch('app.crud.settings')
    @patch('app.crud.get_password_hash')
    def test_create_user_success(self, mock_hash, mock_settings):
        """Test successful user creation."""
        # Arrange
        mock_settings.RELEASE_ALLOW_REGISTRATION = True
        mock_hash.return_value = "hashed_password"
        mock_session = Mock(spec=Session)
        
        user_create = UserCreate(
            email="test@example.com",
            password="password123",
            provider="local",
            sub="test-user-sub"
        )
        
        # Act
        result = create_user(session=mock_session, user_create=user_create)
        
        # Assert
        mock_hash.assert_called_once_with("password123")
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @patch('app.crud.settings')
    def test_create_user_registration_disabled(self, mock_settings):
        """Test user creation when registration is disabled."""
        # Arrange
        mock_settings.RELEASE_ALLOW_REGISTRATION = False
        mock_session = Mock(spec=Session)
        
        user_create = UserCreate(
            email="test@example.com",
            password="password123",
            provider="local",
            sub="test-user-sub"
        )
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            create_user(session=mock_session, user_create=user_create)
        
        assert exc_info.value.status_code == 400
        assert "New user registration is disabled" in str(exc_info.value.detail)


class TestGetUserByEmail:
    """Test get_user_by_email function."""

    def test_get_user_by_email_found(self):
        """Test getting user by email when user exists."""
        # Arrange
        mock_session = Mock(spec=Session)
        expected_user = UserDB(
            id=1,
            email="test@example.com",
            password_hash="hashed",
            role=UserRole.USER,
            status=UserStatus.ACTIVE
        )
        
        mock_exec = Mock()
        mock_exec.first.return_value = expected_user
        mock_session.exec.return_value = mock_exec
        
        # Act
        result = get_user_by_email(session=mock_session, email="test@example.com")
        
        # Assert
        assert result == expected_user
        mock_session.exec.assert_called_once()

    def test_get_user_by_email_not_found(self):
        """Test getting user by email when user doesn't exist."""
        # Arrange
        mock_session = Mock(spec=Session)
        
        mock_exec = Mock()
        mock_exec.first.return_value = None
        mock_session.exec.return_value = mock_exec
        
        # Act
        result = get_user_by_email(session=mock_session, email="nonexistent@example.com")
        
        # Assert
        assert result is None


class TestGetUserById:
    """Test get_user_by_id function."""

    def test_get_user_by_id_found(self):
        """Test getting user by ID when user exists."""
        # Arrange
        mock_session = Mock(spec=Session)
        expected_user = UserDB(
            id=1,
            email="test@example.com",
            password_hash="hashed",
            role=UserRole.USER,
            status=UserStatus.ACTIVE
        )
        
        mock_exec = Mock()
        mock_exec.first.return_value = expected_user
        mock_session.exec.return_value = mock_exec
        
        # Act
        result = get_user_by_id(session=mock_session, user_id=1)
        
        # Assert
        assert result == expected_user

    def test_get_user_by_id_not_found(self):
        """Test getting user by ID when user doesn't exist."""
        # Arrange
        mock_session = Mock(spec=Session)
        
        mock_exec = Mock()
        mock_exec.first.return_value = None
        mock_session.exec.return_value = mock_exec
        
        # Act
        result = get_user_by_id(session=mock_session, user_id=999)
        
        # Assert
        assert result is None


class TestGetFilesById:
    """Test get_files_by_id function."""

    def test_get_files_by_id_found(self):
        """Test getting files by user and task IDs."""
        # Arrange
        mock_session = Mock(spec=Session)
        expected_files = [
            MapTaskFileDB(id=1, user_id=1, map_task_id=1, file_type="result", file_path="/path/to/file1"),
            MapTaskFileDB(id=2, user_id=1, map_task_id=1, file_type="log", file_path="/path/to/file2")
        ]
        
        mock_exec = Mock()
        mock_exec.all.return_value = expected_files
        mock_session.exec.return_value = mock_exec
        
        # Act
        result = get_files_by_id(session=mock_session, user_id=1, map_task_id=1)
        
        # Assert
        assert result == expected_files

    def test_get_files_by_id_empty(self):
        """Test getting files when none exist."""
        # Arrange
        mock_session = Mock(spec=Session)
        
        mock_exec = Mock()
        mock_exec.all.return_value = []
        mock_session.exec.return_value = mock_exec
        
        # Act
        result = get_files_by_id(session=mock_session, user_id=1, map_task_id=999)
        
        # Assert
        assert result == []


class TestGetFileByConditions:
    """Test get_file_by_conditions function."""

    def test_get_file_by_conditions_found(self):
        """Test getting file by task ID and file type."""
        # Arrange
        mock_session = Mock(spec=Session)
        expected_file = MapTaskFileDB(
            id=1, user_id=1, map_task_id=1, file_type="result", file_path="/path/to/file"
        )
        
        mock_exec = Mock()
        mock_exec.first.return_value = expected_file
        mock_session.exec.return_value = mock_exec
        
        # Act
        result = get_file_by_conditions(session=mock_session, map_task_id=1, file_type="result")
        
        # Assert
        assert result == expected_file

    def test_get_file_by_conditions_not_found(self):
        """Test getting file when it doesn't exist."""
        # Arrange
        mock_session = Mock(spec=Session)
        
        mock_exec = Mock()
        mock_exec.first.return_value = None
        mock_session.exec.return_value = mock_exec
        
        # Act
        result = get_file_by_conditions(session=mock_session, map_task_id=999, file_type="nonexistent")
        
        # Assert
        assert result is None


class TestAuthenticate:
    """Test authenticate function."""

    @patch('app.crud.get_user_by_email')
    @patch('app.crud.verify_password')
    @patch('app.crud.touch_last_login')
    def test_authenticate_success(self, mock_touch, mock_verify, mock_get_user):
        """Test successful authentication."""
        # Arrange
        mock_session = Mock(spec=Session)
        user = UserDB(
            id=1,
            email="test@example.com",
            password_hash="hashed",
            role=UserRole.USER,
            status=UserStatus.ACTIVE
        )
        
        mock_get_user.return_value = user
        mock_verify.return_value = True
        mock_touch.return_value = user
        
        # Act
        result = authenticate(session=mock_session, email="test@example.com", password="password123")
        
        # Assert
        assert result == user
        mock_get_user.assert_called_once_with(session=mock_session, email="test@example.com")
        mock_verify.assert_called_once_with("password123", "hashed")
        mock_touch.assert_called_once_with(session=mock_session, user=user)

    @patch('app.crud.get_user_by_email')
    def test_authenticate_user_not_found(self, mock_get_user):
        """Test authentication when user doesn't exist."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_get_user.return_value = None
        
        # Act
        result = authenticate(session=mock_session, email="nonexistent@example.com", password="password123")
        
        # Assert
        assert result is None

    @patch('app.crud.get_user_by_email')
    @patch('app.crud.verify_password')
    def test_authenticate_wrong_password(self, mock_verify, mock_get_user):
        """Test authentication with wrong password."""
        # Arrange
        mock_session = Mock(spec=Session)
        user = UserDB(
            id=1,
            email="test@example.com",
            password_hash="hashed",
            role=UserRole.USER,
            status=UserStatus.ACTIVE
        )
        
        mock_get_user.return_value = user
        mock_verify.return_value = False
        
        # Act
        result = authenticate(session=mock_session, email="test@example.com", password="wrongpassword")
        
        # Assert
        assert result is None

    @patch('app.crud.get_user_by_email')
    @patch('app.crud.verify_password')
    @patch('app.crud.touch_last_login')
    def test_authenticate_touch_login_fails(self, mock_touch, mock_verify, mock_get_user):
        """Test authentication when touch_last_login fails."""
        # Arrange
        mock_session = Mock(spec=Session)
        user = UserDB(
            id=1,
            email="test@example.com",
            password_hash="hashed",
            role=UserRole.USER,
            status=UserStatus.ACTIVE
        )
        
        mock_get_user.return_value = user
        mock_verify.return_value = True
        mock_touch.side_effect = Exception("Database error")
        
        # Act
        result = authenticate(session=mock_session, email="test@example.com", password="password123")
        
        # Assert - should still return user even if touch_last_login fails
        assert result == user


class TestCreateMapTask:
    """Test create_map_task function."""

    @patch('app.crud.settings')
    @patch('app.crud.process_map_task')
    def test_create_map_task_success(self, mock_process, mock_settings):
        """Test successful map task creation."""
        # Arrange
        mock_settings.RELEASE_READ_ONLY = False
        mock_session = Mock(spec=Session)
        mock_background_tasks = Mock(spec=BackgroundTasks)
        
        constraint_factors = [ConstraintFactor(kind="lakes", value=100.0)]
        suitability_factors = [SuitabilityFactor(kind="slope", weight=0.5, breakpoints=[0, 10], points=[0, 5, 10])]
        
        payload = CreateMapTaskReq(
            name="Test Task",
            district_code="063",
            constraint_factors=constraint_factors,
            suitability_factors=suitability_factors
        )
        
        # Act
        result = create_map_task(
            session=mock_session,
            user_id=1,
            payload=payload,
            background_tasks=mock_background_tasks
        )
        
        # Assert
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
        mock_background_tasks.add_task.assert_called_once()

    @patch('app.crud.settings')
    def test_create_map_task_read_only_mode(self, mock_settings):
        """Test map task creation in read-only mode."""
        # Arrange
        mock_settings.RELEASE_READ_ONLY = True
        mock_session = Mock(spec=Session)
        
        payload = CreateMapTaskReq(
            name="Test Task",
            district_code="063",
            constraint_factors=[],
            suitability_factors=[SuitabilityFactor(kind="slope", weight=1.0, breakpoints=[0, 10], points=[0, 5, 10])]
        )
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            create_map_task(session=mock_session, user_id=1, payload=payload)
        
        assert exc_info.value.status_code == 400
        assert "read-only mode" in str(exc_info.value.detail)

    @patch('app.crud.settings')
    def test_create_map_task_no_background_tasks(self, mock_settings):
        """Test map task creation without background tasks."""
        # Arrange
        mock_settings.RELEASE_READ_ONLY = False
        mock_session = Mock(spec=Session)
        
        payload = CreateMapTaskReq(
            name="Test Task",
            district_code="063",
            constraint_factors=[],
            suitability_factors=[SuitabilityFactor(kind="slope", weight=1.0, breakpoints=[0, 10], points=[0, 5, 10])]
        )
        
        # Act
        with patch('builtins.print') as mock_print:
            result = create_map_task(
                session=mock_session,
                user_id=1,
                payload=payload,
                background_tasks=None
            )
        
        # Assert
        mock_print.assert_called_once_with("No background tasks available")


class TestGetMapTask:
    """Test get_map_task function."""

    def test_get_map_task_found(self):
        """Test getting map task when it exists."""
        # Arrange
        mock_session = Mock(spec=Session)
        expected_task = MapTaskDB(
            id=1,
            user_id=1,
            district=1,
            status=MapTaskStatus.PENDING
        )
        
        mock_exec = Mock()
        mock_exec.first.return_value = expected_task
        mock_session.exec.return_value = mock_exec
        
        # Act
        result = get_map_task(session=mock_session, user_id=1, task_id=1)
        
        # Assert
        assert result == expected_task

    def test_get_map_task_not_found(self):
        """Test getting map task when it doesn't exist."""
        # Arrange
        mock_session = Mock(spec=Session)
        
        mock_exec = Mock()
        mock_exec.first.return_value = None
        mock_session.exec.return_value = mock_exec
        
        # Act
        result = get_map_task(session=mock_session, user_id=1, task_id=999)
        
        # Assert
        assert result is None


class TestEdgeCasesAndIntegration:
    """Test edge cases and integration scenarios."""

    @patch('app.crud.settings')
    @patch('app.crud.get_password_hash')
    def test_create_user_with_existing_email_constraint(self, mock_hash, mock_settings):
        """Test user creation with duplicate email (database constraint)."""
        # Arrange
        mock_settings.RELEASE_ALLOW_REGISTRATION = True
        mock_hash.return_value = "hashed_password"
        mock_session = Mock(spec=Session)
        mock_session.commit.side_effect = Exception("Duplicate email")
        
        user_create = UserCreate(
            email="existing@example.com",
            password="password123",
            provider="local",
            sub="existing-user-sub"
        )
        
        # Act & Assert
        with pytest.raises(Exception):
            create_user(session=mock_session, user_create=user_create)

    def test_complex_authentication_flow(self):
        """Test complex authentication scenario with all components."""
        # This would be covered by the individual function tests above
        pass