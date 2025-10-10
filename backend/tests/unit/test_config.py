"""
Test cases for application configuration settings.

This module tests the Settings class from app.core.config, ensuring proper
configuration loading, validation, and environment variable handling.
"""

import os
from unittest.mock import patch

from app.core.config import Settings


class TestSettings:
    """Test Settings class configuration loading and validation."""

    def test_settings_default_values(self):
        """Test Settings with default values."""
        with patch.dict(os.environ, {}, clear=True):
            # Mock warnings to avoid actual warnings during testing
            with patch("warnings.warn") as mock_warn:
                # Need to provide required fields since they don't have defaults
                env_vars = {
                    "PROJECT_NAME": "Site Analyzer Test",
                    "FIRST_SUPERUSER": "admin@test.com",
                    "FIRST_SUPERUSER_PASSWORD": "test-password",
                    "GOOGLE_CLIENT_ID": "test-client-id",
                    "GOOGLE_CLIENT_SECRET": "test-client-secret",
                    "INPUT_DATA_DIR": "/tmp/input",
                    "OUTPUT_DATA_DIR": "/tmp/output",
                    "STORAGE_ENDPOINT": "http://localhost:9000",
                    "STORAGE_ACCESS_KEY": "test-access-key",
                    "STORAGE_SECRET_KEY": "test-secret-key",
                    "STORAGE_BUCKET": "test-bucket",
                    "STORAGE_REGION": "us-east-1",
                }
                with patch.dict(os.environ, env_vars, clear=True):
                    settings = Settings()

                    # Check default values
                    assert settings.PROJECT_NAME == "Site Analyzer Test"
                    assert settings.API_V1_STR == "/api/v1"
                    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60 * 24 * 8  # 8 days
                    assert settings.FRONTEND_HOST == "http://localhost:5173"
                    assert settings.ENVIRONMENT == "local"
                    assert settings.MYSQL_SERVER == "localhost"
                    assert settings.MYSQL_PORT == 3306
                    assert not settings.STORAGE_ENABLED
                    assert settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS == 48

    def test_settings_with_environment_variables(self):
        """Test Settings with custom environment variables."""
        env_vars = {
            "PROJECT_NAME": "test-project",
            "SECRET_KEY": "test-secret-key-123",
            "ACCESS_TOKEN_EXPIRE_MINUTES": "60",
            "FIRST_SUPERUSER": "test@example.com",
            "FIRST_SUPERUSER_PASSWORD": "secure-password-123",
            "BACKEND_CORS_ORIGINS": "http://localhost:3000,https://example.com",
            "GOOGLE_CLIENT_ID": "test-client-id",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
            "INPUT_DATA_DIR": "/tmp/input",
            "OUTPUT_DATA_DIR": "/tmp/output",
            "STORAGE_ENDPOINT": "http://localhost:9000",
            "STORAGE_ACCESS_KEY": "test-access-key",
            "STORAGE_SECRET_KEY": "test-secret-key",
            "STORAGE_BUCKET": "test-bucket",
            "STORAGE_REGION": "us-east-1",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()

            assert settings.PROJECT_NAME == "test-project"
            assert settings.SECRET_KEY == "test-secret-key-123"
            assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60
            assert settings.FIRST_SUPERUSER == "test@example.com"
            assert settings.FIRST_SUPERUSER_PASSWORD == "secure-password-123"

    def test_settings_cors_origins_parsing(self):
        """Test CORS origins string parsing."""
        # Test single origin
        env_vars = {
            "PROJECT_NAME": "test-project",
            "FIRST_SUPERUSER": "admin@test.com",
            "FIRST_SUPERUSER_PASSWORD": "test-password",
            "GOOGLE_CLIENT_ID": "test-client-id",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
            "INPUT_DATA_DIR": "/tmp/input",
            "OUTPUT_DATA_DIR": "/tmp/output",
            "STORAGE_ENDPOINT": "http://localhost:9000",
            "STORAGE_ACCESS_KEY": "test-access-key",
            "STORAGE_SECRET_KEY": "test-secret-key",
            "STORAGE_BUCKET": "test-bucket",
            "STORAGE_REGION": "us-east-1",
            "BACKEND_CORS_ORIGINS": "http://localhost:3000",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            assert len(settings.BACKEND_CORS_ORIGINS) == 1
            assert str(settings.BACKEND_CORS_ORIGINS[0]) == "http://localhost:3000/"

        # Test multiple origins
        env_vars["BACKEND_CORS_ORIGINS"] = "http://localhost:3000,https://example.com"
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            assert len(settings.BACKEND_CORS_ORIGINS) == 2

    def test_settings_database_url_construction(self):
        """Test database URL construction from components."""
        db_env = {
            "PROJECT_NAME": "test-project",
            "FIRST_SUPERUSER": "admin@test.com",
            "FIRST_SUPERUSER_PASSWORD": "test-password",
            "GOOGLE_CLIENT_ID": "test-client-id",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
            "INPUT_DATA_DIR": "/tmp/input",
            "OUTPUT_DATA_DIR": "/tmp/output",
            "STORAGE_ENDPOINT": "http://localhost:9000",
            "STORAGE_ACCESS_KEY": "test-access-key",
            "STORAGE_SECRET_KEY": "test-secret-key",
            "STORAGE_BUCKET": "test-bucket",
            "STORAGE_REGION": "us-east-1",
            "MYSQL_SERVER": "localhost",
            "MYSQL_PORT": "3306",
            "MYSQL_USER": "testuser",
            "MYSQL_PASSWORD": "testpass",
            "MYSQL_DB": "testdb",
        }

        with patch.dict(os.environ, db_env, clear=True):
            settings = Settings()

            expected_url = "mysql+pymysql://testuser:testpass@localhost:3306/testdb"
            assert str(settings.SQLALCHEMY_DATABASE_URI) == expected_url

    def test_settings_security_warnings(self):
        """Test security warnings for default values."""
        env_vars = {
            "PROJECT_NAME": "test-project",
            "SECRET_KEY": "changethis",  # Default value that should trigger warning
            "FIRST_SUPERUSER": "admin@test.com",
            "FIRST_SUPERUSER_PASSWORD": "changethis",  # Default value
            "MYSQL_PASSWORD": "changethis",  # Default value
            "GOOGLE_CLIENT_ID": "test-client-id",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
            "INPUT_DATA_DIR": "/tmp/input",
            "OUTPUT_DATA_DIR": "/tmp/output",
            "STORAGE_ENDPOINT": "http://localhost:9000",
            "STORAGE_ACCESS_KEY": "test-access-key",
            "STORAGE_SECRET_KEY": "test-secret-key",
            "STORAGE_BUCKET": "test-bucket",
            "STORAGE_REGION": "us-east-1",
            "ENVIRONMENT": "local",  # Should only warn in local environment
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with patch("warnings.warn") as mock_warn:
                Settings()
                # Should warn about default secrets in local environment
                assert mock_warn.call_count >= 1

    def test_settings_no_warnings_with_secure_values(self):
        """Test no warnings with secure values."""
        env_vars = {
            "PROJECT_NAME": "test-project",
            "SECRET_KEY": "secure-secret-key-123",
            "FIRST_SUPERUSER": "admin@test.com",
            "FIRST_SUPERUSER_PASSWORD": "secure-password-123",
            "MYSQL_PASSWORD": "secure-db-password",
            "GOOGLE_CLIENT_ID": "test-client-id",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
            "INPUT_DATA_DIR": "/tmp/input",
            "OUTPUT_DATA_DIR": "/tmp/output",
            "STORAGE_ENDPOINT": "http://localhost:9000",
            "STORAGE_ACCESS_KEY": "test-access-key",
            "STORAGE_SECRET_KEY": "test-secret-key",
            "STORAGE_BUCKET": "test-bucket",
            "STORAGE_REGION": "us-east-1",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with patch("warnings.warn") as mock_warn:
                Settings()
                # Should not warn with secure values
                mock_warn.assert_not_called()

    def test_settings_boolean_environment_variables(self):
        """Test boolean environment variable parsing."""
        env_vars = {
            "PROJECT_NAME": "test-project",
            "FIRST_SUPERUSER": "admin@test.com",
            "FIRST_SUPERUSER_PASSWORD": "test-password",
            "GOOGLE_CLIENT_ID": "test-client-id",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
            "INPUT_DATA_DIR": "/tmp/input",
            "OUTPUT_DATA_DIR": "/tmp/output",
            "STORAGE_ENDPOINT": "http://localhost:9000",
            "STORAGE_ACCESS_KEY": "test-access-key",
            "STORAGE_SECRET_KEY": "test-secret-key",
            "STORAGE_BUCKET": "test-bucket",
            "STORAGE_REGION": "us-east-1",
            "STORAGE_ENABLED": "true",
            "RELEASE_READ_ONLY": "false",
            "SMTP_TLS": "true",
            "SMTP_SSL": "false",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()

            assert settings.STORAGE_ENABLED is True
            assert settings.RELEASE_READ_ONLY is False
            assert settings.SMTP_TLS is True
            assert settings.SMTP_SSL is False

    def test_settings_integer_environment_variables(self):
        """Test integer environment variable parsing."""
        env_vars = {
            "PROJECT_NAME": "test-project",
            "FIRST_SUPERUSER": "admin@test.com",
            "FIRST_SUPERUSER_PASSWORD": "test-password",
            "GOOGLE_CLIENT_ID": "test-client-id",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
            "INPUT_DATA_DIR": "/tmp/input",
            "OUTPUT_DATA_DIR": "/tmp/output",
            "STORAGE_ENDPOINT": "http://localhost:9000",
            "STORAGE_ACCESS_KEY": "test-access-key",
            "STORAGE_SECRET_KEY": "test-secret-key",
            "STORAGE_BUCKET": "test-bucket",
            "STORAGE_REGION": "us-east-1",
            "ACCESS_TOKEN_EXPIRE_MINUTES": "120",
            "MYSQL_PORT": "5432",
            "SMTP_PORT": "25",
            "EMAIL_RESET_TOKEN_EXPIRE_HOURS": "24",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()

            assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 120
            assert settings.MYSQL_PORT == 5432
            assert settings.SMTP_PORT == 25
            assert settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS == 24

    def test_settings_model_config(self):
        """Test Settings model configuration."""
        env_vars = {
            "PROJECT_NAME": "test-project",
            "FIRST_SUPERUSER": "admin@test.com",
            "FIRST_SUPERUSER_PASSWORD": "test-password",
            "GOOGLE_CLIENT_ID": "test-client-id",
            "GOOGLE_CLIENT_SECRET": "test-client-secret",
            "INPUT_DATA_DIR": "/tmp/input",
            "OUTPUT_DATA_DIR": "/tmp/output",
            "STORAGE_ENDPOINT": "http://localhost:9000",
            "STORAGE_ACCESS_KEY": "test-access-key",
            "STORAGE_SECRET_KEY": "test-secret-key",
            "STORAGE_BUCKET": "test-bucket",
            "STORAGE_REGION": "us-east-1",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()

            # Should be a Pydantic model
            assert hasattr(settings, "model_config")

            # Should have expected attributes
            assert hasattr(settings, "PROJECT_NAME")
            assert hasattr(settings, "SECRET_KEY")
            assert hasattr(settings, "SQLALCHEMY_DATABASE_URI")


class TestSettingsIntegration:
    """Integration tests for Settings with realistic configurations."""

    def test_settings_realistic_production_config(self):
        """Test Settings with realistic production-like configuration."""
        prod_env = {
            "PROJECT_NAME": "Site Analyzer API",
            "SECRET_KEY": "super-secret-production-key-2024",
            "ACCESS_TOKEN_EXPIRE_MINUTES": "720",  # 12 hours
            "FIRST_SUPERUSER": "admin@siteanalyzer.com",
            "FIRST_SUPERUSER_PASSWORD": "SecureAdminPass2024!",
            "MYSQL_SERVER": "db.example.com",
            "MYSQL_PORT": "3306",
            "MYSQL_USER": "siteanalyzer",
            "MYSQL_PASSWORD": "DbPass2024!",
            "MYSQL_DB": "siteanalyzer_prod",
            "BACKEND_CORS_ORIGINS": "https://app.siteanalyzer.com,https://admin.siteanalyzer.com",
            "GOOGLE_CLIENT_ID": "prod-client-id",
            "GOOGLE_CLIENT_SECRET": "prod-client-secret",
            "INPUT_DATA_DIR": "/app/input",
            "OUTPUT_DATA_DIR": "/app/output",
            "STORAGE_ENDPOINT": "https://storage.example.com",
            "STORAGE_ACCESS_KEY": "prod-access-key",
            "STORAGE_SECRET_KEY": "prod-secret-key",
            "STORAGE_BUCKET": "siteanalyzer-prod",
            "STORAGE_REGION": "us-east-1",
        }

        with patch.dict(os.environ, prod_env, clear=True):
            settings = Settings()

            # Verify all settings are correctly parsed
            assert settings.PROJECT_NAME == "Site Analyzer API"
            assert settings.SECRET_KEY == "super-secret-production-key-2024"
            assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 720
            assert settings.FIRST_SUPERUSER == "admin@siteanalyzer.com"
            assert settings.FIRST_SUPERUSER_PASSWORD == "SecureAdminPass2024!"
            assert settings.MYSQL_SERVER == "db.example.com"
            assert settings.MYSQL_USER == "siteanalyzer"
            assert settings.MYSQL_DB == "siteanalyzer_prod"

            # Verify CORS origins
            assert len(settings.BACKEND_CORS_ORIGINS) == 2
            cors_origins_str = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]
            assert any("app.siteanalyzer.com" in origin for origin in cors_origins_str)
            assert any("admin.siteanalyzer.com" in origin for origin in cors_origins_str)

    def test_settings_development_config(self):
        """Test Settings with development configuration."""
        dev_env = {
            "PROJECT_NAME": "Site Analyzer Dev",
            "SECRET_KEY": "dev-secret-key-123",
            "ACCESS_TOKEN_EXPIRE_MINUTES": "60",
            "MYSQL_SERVER": "localhost",
            "MYSQL_PORT": "3306",
            "MYSQL_USER": "dev",
            "MYSQL_PASSWORD": "dev",
            "MYSQL_DB": "siteanalyzer_dev",
            "BACKEND_CORS_ORIGINS": "http://localhost:3000,http://localhost:8080",
            "FIRST_SUPERUSER": "dev@example.com",
            "FIRST_SUPERUSER_PASSWORD": "dev-password-123",
            "GOOGLE_CLIENT_ID": "dev-client-id",
            "GOOGLE_CLIENT_SECRET": "dev-client-secret",
            "INPUT_DATA_DIR": "/tmp/dev-input",
            "OUTPUT_DATA_DIR": "/tmp/dev-output",
            "STORAGE_ENDPOINT": "http://localhost:9000",
            "STORAGE_ACCESS_KEY": "dev-access-key",
            "STORAGE_SECRET_KEY": "dev-secret-key",
            "STORAGE_BUCKET": "siteanalyzer-dev",
            "STORAGE_REGION": "us-east-1",
        }

        with patch.dict(os.environ, dev_env, clear=True):
            settings = Settings()

            assert settings.PROJECT_NAME == "Site Analyzer Dev"
            assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 60
            assert "localhost" in str(settings.SQLALCHEMY_DATABASE_URI)
            # Check CORS origins contain localhost URLs
            cors_origins_str = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]
            assert any("localhost:3000" in origin for origin in cors_origins_str)
            assert any("localhost:8080" in origin for origin in cors_origins_str)
