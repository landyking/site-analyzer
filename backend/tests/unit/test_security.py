"""
Unit tests for app.core.security module.

Tests password hashing, JWT token operations, and signature generation.
"""

import base64
import hashlib
import hmac
from datetime import UTC, datetime, timedelta

import jwt

from app.core.security import (
    ALGORITHM,
    create_access_token,
    gen_tile_signature,
    get_password_hash,
    verify_password,
)


class TestPasswordHashing:
    """Test password hashing and verification functions."""

    def test_get_password_hash_creates_valid_hash(self):
        """Test that password hashing creates a valid bcrypt hash."""
        password = "test_password_123"
        hashed = get_password_hash(password)

        # Bcrypt hashes start with $2b$
        assert hashed.startswith("$2b$")
        assert len(hashed) == 60  # Standard bcrypt hash length
        assert hashed != password  # Should be different from original

    def test_get_password_hash_different_for_same_password(self):
        """Test that the same password produces different hashes (salt effect)."""
        password = "same_password"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2  # Different salts should produce different hashes

    def test_verify_password_correct_password(self):
        """Test password verification with correct password."""
        password = "correct_password"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect_password(self):
        """Test password verification with incorrect password."""
        correct_password = "correct_password"
        wrong_password = "wrong_password"
        hashed = get_password_hash(correct_password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty_password(self):
        """Test password verification with empty password."""
        password = "test_password"
        hashed = get_password_hash(password)

        assert verify_password("", hashed) is False


class TestJWTTokenOperations:
    """Test JWT token creation and validation."""

    def test_create_access_token_structure(self, mock_settings):
        """Test that JWT token is created with correct structure."""
        user_id = 12345
        admin = True
        expires_delta = timedelta(minutes=30)

        token = create_access_token(user_id, admin, expires_delta)

        # JWT tokens have 3 parts separated by dots
        parts = token.split(".")
        assert len(parts) == 3

        # Decode the token to verify structure
        decoded = jwt.decode(token, mock_settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == str(user_id)
        assert decoded["admin"] is admin
        assert "exp" in decoded

    def test_create_access_token_expiration(self, mock_settings):
        """Test that JWT token has correct expiration time."""
        user_id = 123
        admin = False
        expires_delta = timedelta(minutes=15)

        # Create token and decode to check structure
        token = create_access_token(user_id, admin, expires_delta)

        # Decode without verification to check structure
        decoded = jwt.decode(
            token, mock_settings.SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False}
        )

        # Check that expiration exists and is a valid timestamp
        assert "exp" in decoded
        exp_timestamp = decoded["exp"]
        assert isinstance(exp_timestamp, int)
        assert exp_timestamp > 0

        # Check that expiration is in the future (reasonable test)
        now = datetime.now(UTC).timestamp()
        assert exp_timestamp > now  # Token should expire in the future

    def test_create_access_token_different_users(self, mock_settings):
        """Test that different users get different tokens."""
        expires_delta = timedelta(minutes=30)

        token1 = create_access_token(subject=123, admin=False, expires_delta=expires_delta)
        token2 = create_access_token(subject=456, admin=True, expires_delta=expires_delta)

        assert token1 != token2

        decoded1 = jwt.decode(token1, mock_settings.SECRET_KEY, algorithms=[ALGORITHM])
        decoded2 = jwt.decode(token2, mock_settings.SECRET_KEY, algorithms=[ALGORITHM])

        assert decoded1["sub"] != decoded2["sub"]
        assert decoded1["admin"] != decoded2["admin"]

    def test_create_access_token_admin_flag(self, mock_settings):
        """Test that admin flag is correctly set in token."""
        user_id = 789
        expires_delta = timedelta(minutes=30)

        # Test admin=True
        admin_token = create_access_token(user_id, admin=True, expires_delta=expires_delta)
        admin_decoded = jwt.decode(admin_token, mock_settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert admin_decoded["admin"] is True

        # Test admin=False
        user_token = create_access_token(user_id, admin=False, expires_delta=expires_delta)
        user_decoded = jwt.decode(user_token, mock_settings.SECRET_KEY, algorithms=[ALGORITHM])
        assert user_decoded["admin"] is False


class TestTileSignatureGeneration:
    """Test tile signature generation function."""

    def test_gen_tile_signature_basic(self, mock_settings):
        """Test basic tile signature generation."""
        user = 123
        task = 456
        exp = 1672531200  # Example timestamp

        signature = gen_tile_signature(user, task, exp)

        # Should return a base64-encoded string without padding
        assert isinstance(signature, str)
        assert len(signature) > 0
        # Base64 without padding should not end with '='
        assert not signature.endswith("=")

    def test_gen_tile_signature_deterministic(self, mock_settings):
        """Test that same inputs produce same signature."""
        user = 123
        task = 456
        exp = 1672531200

        sig1 = gen_tile_signature(user, task, exp)
        sig2 = gen_tile_signature(user, task, exp)

        assert sig1 == sig2

    def test_gen_tile_signature_different_inputs(self, mock_settings):
        """Test that different inputs produce different signatures."""
        exp = 1672531200

        sig1 = gen_tile_signature(user=123, task=456, exp=exp)
        sig2 = gen_tile_signature(user=124, task=456, exp=exp)  # Different user
        sig3 = gen_tile_signature(user=123, task=457, exp=exp)  # Different task
        sig4 = gen_tile_signature(user=123, task=456, exp=exp + 1)  # Different exp

        signatures = [sig1, sig2, sig3, sig4]
        # All signatures should be unique
        assert len(set(signatures)) == len(signatures)

    def test_gen_tile_signature_algorithm(self, mock_settings):
        """Test that signature generation uses correct HMAC-SHA256 algorithm."""
        user = 100
        task = 200
        exp = 1672531200

        # Generate signature using our function
        actual_signature = gen_tile_signature(user, task, exp)

        # Generate expected signature manually
        message = f"{user}:{task}:{exp}".encode()
        key = mock_settings.SECRET_KEY.encode()
        expected_hmac = hmac.new(key, message, hashlib.sha256).digest()
        expected_signature = base64.urlsafe_b64encode(expected_hmac).rstrip(b"=").decode()

        assert actual_signature == expected_signature

    def test_gen_tile_signature_edge_cases(self, mock_settings):
        """Test tile signature generation with edge case values."""
        # Test with zero values
        sig_zero = gen_tile_signature(0, 0, 0)
        assert isinstance(sig_zero, str)
        assert len(sig_zero) > 0

        # Test with large numbers
        sig_large = gen_tile_signature(999999999, 888888888, 1999999999)
        assert isinstance(sig_large, str)
        assert len(sig_large) > 0

        # Test with negative numbers (if allowed by business logic)
        sig_negative = gen_tile_signature(-1, -2, 1672531200)
        assert isinstance(sig_negative, str)
        assert len(sig_negative) > 0
