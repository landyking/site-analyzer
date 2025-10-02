"""
Unit tests for app.api.deps module.

Tests dependency injection functions for authentication, authorization, database sessions.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from fastapi import HTTPException, status
from sqlmodel import Session

# Use patch context manager to handle circular imports
with patch('app.crud.get_user_by_id'), patch('app.crud.process_map_task'):
    from app.api.deps import (
        get_db,
        get_current_user,
        get_current_active_admin,
        reusable_oauth2,
        SessionDep,
        TokenDep,
        CurrentUser,
        CurrentAdminUser
    )
    from app.models import TokenPayload, UserDB, UserRole, UserStatus


class TestGetDb:
    """Test database session dependency."""
    
    def test_get_db_returns_generator(self):
        """Test that get_db returns a generator."""
        db_generator = get_db()
        
        # Verify it's a generator
        from types import GeneratorType
        assert isinstance(db_generator, GeneratorType)
    
    def test_get_db_yields_session_object(self):
        """Test that get_db yields a Session object."""
        db_generator = get_db()
        
        # Get the session
        session = next(db_generator)
        
        # Verify it's a Session instance
        assert isinstance(session, Session)
        
        # Verify we can close the generator
        try:
            next(db_generator)
        except StopIteration:
            # Expected - generator should be exhausted
            pass


class TestGetCurrentUser:
    """Test current user authentication dependency."""
    
    def test_get_current_user_valid_token(self):
        """Test successful user authentication with valid token."""
        # Setup mocks
        mock_session = Mock(spec=Session)
        mock_user = Mock(spec=UserDB)
        mock_user.status = UserStatus.ACTIVE
        mock_session.get.return_value = mock_user
        
        # Mock JWT decode
        mock_payload = {"sub": "123", "admin": False}
        
        with patch('app.api.deps.jwt.decode', return_value=mock_payload), \
             patch('app.api.deps.settings') as mock_settings, \
             patch('app.api.deps.security') as mock_security:
            
            mock_settings.SECRET_KEY = "test_secret"
            mock_security.ALGORITHM = "HS256"
            
            result = get_current_user(mock_session, "valid_token")
            
            assert result == mock_user
            mock_session.get.assert_called_once_with(UserDB, 123)
    
    def test_get_current_user_invalid_token_format(self):
        """Test authentication failure with invalid token format."""
        mock_session = Mock(spec=Session)
        
        with patch('app.api.deps.jwt.decode', side_effect=InvalidTokenError("Invalid token")):
            with pytest.raises(HTTPException) as exc_info:
                get_current_user(mock_session, "invalid_token")
            
            assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
            assert exc_info.value.detail == "Could not validate credentials"
    
    def test_get_current_user_validation_error(self):
        """Test authentication failure with token validation error."""
        mock_session = Mock(spec=Session)
        
        # Mock JWT decode to return invalid payload
        mock_payload = {"invalid": "payload"}
        
        with patch('app.api.deps.jwt.decode', return_value=mock_payload), \
             patch('app.api.deps.settings') as mock_settings, \
             patch('app.api.deps.security') as mock_security:
            
            mock_settings.SECRET_KEY = "test_secret"
            mock_security.ALGORITHM = "HS256"
            
            with pytest.raises(HTTPException) as exc_info:
                get_current_user(mock_session, "invalid_payload_token")
            
            assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
            assert exc_info.value.detail == "Could not validate credentials"
    
    def test_get_current_user_user_not_found(self):
        """Test authentication failure when user not found in database."""
        mock_session = Mock(spec=Session)
        mock_session.get.return_value = None
        
        mock_payload = {"sub": "123", "admin": False}
        
        with patch('app.api.deps.jwt.decode', return_value=mock_payload), \
             patch('app.api.deps.settings') as mock_settings, \
             patch('app.api.deps.security') as mock_security:
            
            mock_settings.SECRET_KEY = "test_secret"
            mock_security.ALGORITHM = "HS256"
            
            with pytest.raises(HTTPException) as exc_info:
                get_current_user(mock_session, "token_for_missing_user")
            
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "User not found"
    
    def test_get_current_user_inactive_user(self):
        """Test authentication failure for inactive user."""
        mock_session = Mock(spec=Session)
        mock_user = Mock(spec=UserDB)
        mock_user.status = UserStatus.LOCKED
        mock_session.get.return_value = mock_user
        
        mock_payload = {"sub": "123", "admin": False}
        
        with patch('app.api.deps.jwt.decode', return_value=mock_payload), \
             patch('app.api.deps.settings') as mock_settings, \
             patch('app.api.deps.security') as mock_security:
            
            mock_settings.SECRET_KEY = "test_secret"
            mock_security.ALGORITHM = "HS256"
            
            with pytest.raises(HTTPException) as exc_info:
                get_current_user(mock_session, "token_for_inactive_user")
            
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Inactive user"
    
    def test_get_current_user_with_admin_token(self):
        """Test successful authentication with admin token."""
        mock_session = Mock(spec=Session)
        mock_user = Mock(spec=UserDB)
        mock_user.status = UserStatus.ACTIVE
        mock_session.get.return_value = mock_user
        
        mock_payload = {"sub": "456", "admin": True}
        
        with patch('app.api.deps.jwt.decode', return_value=mock_payload), \
             patch('app.api.deps.settings') as mock_settings, \
             patch('app.api.deps.security') as mock_security:
            
            mock_settings.SECRET_KEY = "test_secret"
            mock_security.ALGORITHM = "HS256"
            
            result = get_current_user(mock_session, "admin_token")
            
            assert result == mock_user
            mock_session.get.assert_called_once_with(UserDB, 456)
    
    def test_get_current_user_string_subject_conversion(self):
        """Test that subject is properly converted to int for database lookup."""
        mock_session = Mock(spec=Session)
        mock_user = Mock(spec=UserDB)
        mock_user.status = UserStatus.ACTIVE
        mock_session.get.return_value = mock_user
        
        mock_payload = {"sub": "789", "admin": False}
        
        with patch('app.api.deps.jwt.decode', return_value=mock_payload), \
             patch('app.api.deps.settings') as mock_settings, \
             patch('app.api.deps.security') as mock_security:
            
            mock_settings.SECRET_KEY = "test_secret"
            mock_security.ALGORITHM = "HS256"
            
            result = get_current_user(mock_session, "string_subject_token")
            
            assert result == mock_user
            # Verify int conversion of subject
            mock_session.get.assert_called_once_with(UserDB, 789)


class TestGetCurrentActiveAdmin:
    """Test admin authorization dependency."""
    
    def test_get_current_active_admin_valid_admin(self):
        """Test successful admin authorization."""
        mock_user = Mock(spec=UserDB)
        mock_user.role = UserRole.ADMIN
        
        result = get_current_active_admin(mock_user)
        
        assert result == mock_user
    
    def test_get_current_active_admin_non_admin_user(self):
        """Test admin authorization failure for regular user."""
        mock_user = Mock(spec=UserDB)
        mock_user.role = UserRole.USER
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_active_admin(mock_user)
        
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "The user doesn't have enough privileges"
    
    def test_get_current_active_admin_none_user(self):
        """Test admin authorization handles user with None role."""
        mock_user = Mock(spec=UserDB)
        mock_user.role = None
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_active_admin(mock_user)
        
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "The user doesn't have enough privileges"
    
    def test_get_current_active_admin_invalid_role_value(self):
        """Test admin authorization with invalid role value."""
        mock_user = Mock(spec=UserDB)
        mock_user.role = 999  # Invalid role value
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_active_admin(mock_user)
        
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "The user doesn't have enough privileges"


class TestOAuth2Configuration:
    """Test OAuth2 configuration and dependencies."""
    
    def test_reusable_oauth2_configuration(self):
        """Test OAuth2 password bearer configuration."""
        from app.api.deps import reusable_oauth2
        from app.core.config import settings
        from fastapi.security import OAuth2PasswordBearer
        
        # Check that reusable_oauth2 is an OAuth2PasswordBearer instance
        assert isinstance(reusable_oauth2, OAuth2PasswordBearer)
        
        # Check the expected token URL - test that we can construct a valid URL
        expected_token_url = f"{settings.API_V1_STR}/user-login"
        assert expected_token_url == "/api/v1/user-login"
    
    def test_annotated_dependencies_types(self):
        """Test that annotated dependencies have correct types."""
        # These imports verify the dependencies are properly configured
        from app.api.deps import SessionDep, TokenDep, CurrentUser, CurrentAdminUser
        
        # Verify annotations exist (they will be used by FastAPI for dependency injection)
        assert SessionDep is not None
        assert TokenDep is not None
        assert CurrentUser is not None
        assert CurrentAdminUser is not None


class TestTokenPayloadValidation:
    """Test TokenPayload model validation in authentication flow."""
    
    def test_token_payload_valid_data(self):
        """Test TokenPayload model with valid data."""
        payload_data = {"sub": "123", "admin": False}
        token_payload = TokenPayload(**payload_data)
        
        assert token_payload.sub == "123"
        assert token_payload.admin is False
    
    def test_token_payload_missing_sub(self):
        """Test TokenPayload model validation with missing sub field."""
        payload_data = {"admin": True}
        
        with pytest.raises(ValidationError):
            TokenPayload(**payload_data)
    
    def test_token_payload_admin_default_false(self):
        """Test TokenPayload model admin field defaults to False."""
        payload_data = {"sub": "123"}
        token_payload = TokenPayload(**payload_data)
        
        assert token_payload.sub == "123"
        assert token_payload.admin is False
    
    def test_token_payload_admin_explicit_true(self):
        """Test TokenPayload model with explicit admin True."""
        payload_data = {"sub": "456", "admin": True}
        token_payload = TokenPayload(**payload_data)
        
        assert token_payload.sub == "456"
        assert token_payload.admin is True


class TestIntegrationScenarios:
    """Test integration scenarios combining multiple dependencies."""
    
    def test_full_authentication_flow(self):
        """Test complete authentication flow from token to user."""
        # Setup database mock
        mock_session = Mock(spec=Session)
        
        # Setup user mock
        mock_user = Mock(spec=UserDB)
        mock_user.status = UserStatus.ACTIVE
        mock_user.role = UserRole.USER
        mock_session.get.return_value = mock_user
        
        # Setup JWT mock
        mock_payload = {"sub": "123", "admin": False}
        
        with patch('app.api.deps.jwt.decode', return_value=mock_payload), \
             patch('app.api.deps.settings') as mock_settings, \
             patch('app.api.deps.security') as mock_security:
            
            mock_settings.SECRET_KEY = "test_secret"
            mock_security.ALGORITHM = "HS256"
            
            # Test user authentication with mock session
            user = get_current_user(mock_session, "valid_token")
            assert user == mock_user
            
            # Verify database query was made
            mock_session.get.assert_called_once_with(UserDB, 123)
    
    def test_dependency_chain_integration(self):
        """Test dependency chain works as expected."""
        # Test that dependency annotations exist and are configured
        assert SessionDep is not None
        assert TokenDep is not None
        assert CurrentUser is not None  
        assert CurrentAdminUser is not None
        
        # Test dependency functions are callable
        assert callable(get_db)
        assert callable(get_current_user)
        assert callable(get_current_active_admin)
    
    def test_authentication_error_chain(self):
        """Test error handling chain from invalid token to HTTP exception."""
        mock_session = Mock(spec=Session)
        
        with patch('app.api.deps.jwt.decode', side_effect=InvalidTokenError("Malformed token")):
            with pytest.raises(HTTPException) as exc_info:
                get_current_user(mock_session, "malformed_token")
            
            # Verify the error propagates correctly
            assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
            assert "Could not validate credentials" in exc_info.value.detail
    
    def test_authorization_error_chain(self):
        """Test authorization error chain from regular user to admin access."""
        mock_user = Mock(spec=UserDB)
        mock_user.role = UserRole.USER
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_active_admin(mock_user)
        
        # Verify the authorization error
        assert exc_info.value.status_code == 403
        assert "doesn't have enough privileges" in exc_info.value.detail


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and comprehensive error handling."""
    
    def test_get_current_user_jwt_decode_exception_types(self):
        """Test handling of different JWT decode exception types."""
        mock_session = Mock(spec=Session)
        
        # Test InvalidTokenError
        with patch('app.api.deps.jwt.decode', side_effect=InvalidTokenError("Invalid")):
            with pytest.raises(HTTPException) as exc_info:
                get_current_user(mock_session, "token")
            assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        
        # Test generic JWT exception
        with patch('app.api.deps.jwt.decode', side_effect=jwt.DecodeError("Decode error")):
            with pytest.raises(HTTPException) as exc_info:
                get_current_user(mock_session, "token")
            assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_current_user_database_session_error(self):
        """Test handling of database session errors."""
        mock_session = Mock(spec=Session)
        mock_session.get.side_effect = Exception("Database connection error")
        
        mock_payload = {"sub": "123", "admin": False}
        
        with patch('app.api.deps.jwt.decode', return_value=mock_payload), \
             patch('app.api.deps.settings') as mock_settings, \
             patch('app.api.deps.security') as mock_security:
            
            mock_settings.SECRET_KEY = "test_secret"
            mock_security.ALGORITHM = "HS256"
            
            # Database error should propagate
            with pytest.raises(Exception, match="Database connection error"):
                get_current_user(mock_session, "token")
    
    def test_token_payload_edge_cases(self):
        """Test TokenPayload with edge case values."""
        # Test with string representation of boolean
        payload_data = {"sub": "123", "admin": "true"}
        token_payload = TokenPayload(**payload_data)
        assert token_payload.admin is True
        
        # Test with string sub (standard case)
        payload_data = {"sub": "456", "admin": False}
        token_payload = TokenPayload(**payload_data)
        assert token_payload.sub == "456"
        assert token_payload.admin is False
    
    def test_user_status_enum_edge_cases(self):
        """Test UserStatus enum value comparisons."""
        mock_user = Mock(spec=UserDB)
        
        # Test exact enum match
        mock_user.status = UserStatus.ACTIVE
        mock_session = Mock()
        mock_payload = {"sub": "123", "admin": False}
        
        with patch('app.api.deps.jwt.decode', return_value=mock_payload), \
             patch('app.api.deps.settings') as mock_settings, \
             patch('app.api.deps.security') as mock_security:
            
            mock_settings.SECRET_KEY = "test_secret"
            mock_security.ALGORITHM = "HS256"
            mock_session.get.return_value = mock_user
            
            # Should succeed with exact enum match
            result = get_current_user(mock_session, "token")
            assert result == mock_user
        
        # Test with integer value instead of enum
        mock_user.status = 1  # UserStatus.ACTIVE value
        with patch('app.api.deps.jwt.decode', return_value=mock_payload), \
             patch('app.api.deps.settings') as mock_settings, \
             patch('app.api.deps.security') as mock_security:
            
            mock_settings.SECRET_KEY = "test_secret"
            mock_security.ALGORITHM = "HS256"
            mock_session.get.return_value = mock_user
            
            # Should succeed with integer value
            result = get_current_user(mock_session, "token")
            assert result == mock_user