"""
Unit tests for app.models module.

Tests validation logic, data models, and business rules.
"""
import pytest
from datetime import datetime, timezone
from math import inf, nan
from typing import List
from pydantic import ValidationError

from app.models import (
    BaseResp,
    PageData,
    SelectOptionItem,
    SelectOptionListResp,
    DistrictHistogram,
    DistrictHistogramItem,
    DistrictHistogramsResp,
    LoginRequest,
    RegisterRequest,
    ConstraintFactor,
    SuitabilityFactor,
    CreateMapTaskReq,
    MapTask,
    MapTaskFile,
    MapTaskDetails,
    User4Admin,
    AdminUpdateUserStatusRequest,
    UserRole,
    UserStatus,
)


class TestBaseModels:
    """Test basic response and pagination models."""
    
    def test_base_resp_default_error(self):
        """Test BaseResp has default error value of 0."""
        resp = BaseResp()
        assert resp.error == 0
    
    def test_base_resp_custom_error(self):
        """Test BaseResp accepts custom error value."""
        resp = BaseResp(error=404)
        assert resp.error == 404
    
    def test_page_data_all_none_by_default(self):
        """Test PageData has all fields None by default."""
        page = PageData()
        assert page.total is None
        assert page.current_page is None
        assert page.page_size is None
    
    def test_page_data_with_values(self):
        """Test PageData accepts custom values."""
        page = PageData(total=100, current_page=2, page_size=10)
        assert page.total == 100
        assert page.current_page == 2
        assert page.page_size == 10


class TestSelectOption:
    """Test selector option models."""
    
    def test_select_option_item_creation(self):
        """Test SelectOptionItem creation with code and label."""
        item = SelectOptionItem(code="US", label="United States")
        assert item.code == "US"
        assert item.label == "United States"
    
    def test_select_option_list_resp(self):
        """Test SelectOptionListResp with list of items."""
        items = [
            SelectOptionItem(code="US", label="United States"),
            SelectOptionItem(code="CA", label="Canada")
        ]
        resp = SelectOptionListResp(list=items)
        assert len(resp.list) == 2
        assert resp.error == 0  # Inherited from BaseResp


class TestDistrictHistogram:
    """Test district histogram models."""
    
    def test_district_histogram_creation(self):
        """Test DistrictHistogram creation with valid data."""
        histogram = DistrictHistogram(
            frequency=[10, 20, 30],
            edges=[0.0, 1.0, 2.0, 3.0],
            min=0.0,
            max=3.0
        )
        assert histogram.frequency == [10, 20, 30]
        assert histogram.edges == [0.0, 1.0, 2.0, 3.0]
        assert histogram.min == 0.0
        assert histogram.max == 3.0
    
    def test_district_histogram_item(self):
        """Test DistrictHistogramItem with kind and histogram."""
        histogram = DistrictHistogram(
            frequency=[5, 15],
            edges=[0.0, 1.0, 2.0],
            min=0.0,
            max=2.0
        )
        item = DistrictHistogramItem(kind="elevation", histogram=histogram)
        assert item.kind == "elevation"
        assert item.histogram.frequency == [5, 15]
    
    def test_district_histograms_resp_empty_list(self):
        """Test DistrictHistogramsResp with empty list by default."""
        resp = DistrictHistogramsResp()
        assert resp.list == []
        assert resp.error == 0


class TestAuthModels:
    """Test authentication-related models."""
    
    def test_login_request_valid_email(self):
        """Test LoginRequest with valid email."""
        login = LoginRequest(email="user@example.com", password="password123")
        assert login.email == "user@example.com"
        assert login.password == "password123"
    
    def test_login_request_invalid_email(self):
        """Test LoginRequest raises error with invalid email."""
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(email="invalid-email", password="password123")
        
        error = exc_info.value.errors()[0]
        # Check that error is related to email field
        assert error["loc"] == ("email",)
        assert "value_error" in error["type"] or "email" in str(error["msg"]).lower()
    
    def test_register_request_valid_data(self):
        """Test RegisterRequest with valid email and password."""
        register = RegisterRequest(
            email="newuser@example.com", 
            password="securepass123"
        )
        assert register.email == "newuser@example.com"
        assert register.password == "securepass123"
    
    def test_register_request_password_too_short(self):
        """Test RegisterRequest rejects password shorter than 8 characters."""
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(email="user@example.com", password="short")
        
        errors = exc_info.value.errors()
        password_error = next(e for e in errors if e["loc"] == ("password",))
        assert "at least 8 characters" in password_error["msg"]
    
    def test_register_request_password_too_long(self):
        """Test RegisterRequest rejects password longer than 40 characters."""
        long_password = "a" * 41  # 41 characters
        with pytest.raises(ValidationError) as exc_info:
            RegisterRequest(email="user@example.com", password=long_password)
        
        errors = exc_info.value.errors()
        password_error = next(e for e in errors if e["loc"] == ("password",))
        assert "at most 40 characters" in password_error["msg"]


class TestConstraintFactor:
    """Test ConstraintFactor validation logic."""
    
    def test_constraint_factor_valid_kind_and_value(self):
        """Test ConstraintFactor with valid kind and value."""
        # Use actual constraint from ALLOWED_CONSTRAINTS: rivers, lakes, coastlines, residential
        constraint = ConstraintFactor(kind="rivers", value=100.0)
        assert constraint.kind == "rivers"
        assert constraint.value == 100.0
    
    def test_constraint_factor_zero_value_allowed(self):
        """Test ConstraintFactor allows zero value."""
        constraint = ConstraintFactor(kind="lakes", value=0.0)
        assert constraint.kind == "lakes"
        assert constraint.value == 0.0
    
    def test_constraint_factor_negative_value_rejected(self):
        """Test ConstraintFactor rejects negative values."""
        with pytest.raises(ValidationError) as exc_info:
            ConstraintFactor(kind="rivers", value=-1.0)
        
        errors = exc_info.value.errors()
        value_error = next(e for e in errors if e["loc"] == ("value",))
        assert "finite number >= 0" in value_error["msg"]
    
    def test_constraint_factor_nan_value_rejected(self):
        """Test ConstraintFactor rejects NaN values."""
        with pytest.raises(ValidationError) as exc_info:
            ConstraintFactor(kind="water", value=nan)
        
        errors = exc_info.value.errors()
        value_error = next(e for e in errors if e["loc"] == ("value",))
        assert "finite number >= 0" in value_error["msg"]
    
    def test_constraint_factor_infinity_value_rejected(self):
        """Test ConstraintFactor rejects infinite values."""
        with pytest.raises(ValidationError) as exc_info:
            ConstraintFactor(kind="water", value=inf)
        
        errors = exc_info.value.errors()
        value_error = next(e for e in errors if e["loc"] == ("value",))
        assert "finite number >= 0" in value_error["msg"]
    
    def test_constraint_factor_invalid_kind_rejected(self):
        """Test ConstraintFactor rejects invalid kind."""
        with pytest.raises(ValidationError) as exc_info:
            ConstraintFactor(kind="invalid_constraint", value=50.0)
        
        errors = exc_info.value.errors()
        kind_error = next(e for e in errors if e["loc"] == ("kind",))
        assert "Invalid constraint kind" in kind_error["msg"]


class TestSuitabilityFactor:
    """Test SuitabilityFactor validation logic."""
    
    def test_suitability_factor_valid_data(self):
        """Test SuitabilityFactor with valid data."""
        factor = SuitabilityFactor(
            kind="slope",
            weight=5.0,
            breakpoints=[10.0, 20.0, 30.0],
            points=[8, 5, 3, 1]  # len(breakpoints) + 1
        )
        assert factor.kind == "slope"
        assert factor.weight == 5.0
        assert factor.breakpoints == [10.0, 20.0, 30.0]
        assert factor.points == [8, 5, 3, 1]
    
    def test_suitability_factor_weight_validation(self):
        """Test SuitabilityFactor weight must be in (0, 10]."""
        # Valid weights
        SuitabilityFactor(
            kind="slope", weight=0.1, breakpoints=[5.0], points=[10, 0]
        )
        SuitabilityFactor(
            kind="slope", weight=10.0, breakpoints=[5.0], points=[10, 0]
        )
        
        # Invalid weights
        with pytest.raises(ValidationError) as exc_info:
            SuitabilityFactor(
                kind="slope", weight=0.0, breakpoints=[5.0], points=[10, 0]
            )
        assert "weight must be in the interval (0, 10]" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            SuitabilityFactor(
                kind="slope", weight=11.0, breakpoints=[5.0], points=[10, 0]
            )
        assert "weight must be in the interval (0, 10]" in str(exc_info.value)
    
    def test_suitability_factor_breakpoints_must_be_sorted(self):
        """Test SuitabilityFactor breakpoints must be in ascending order."""
        with pytest.raises(ValidationError) as exc_info:
            SuitabilityFactor(
                kind="slope",
                weight=5.0,
                breakpoints=[20.0, 10.0, 30.0],  # Not sorted
                points=[8, 5, 3, 1]
            )
        assert "breakpoints must be in ascending order" in str(exc_info.value)
    
    def test_suitability_factor_points_count_validation(self):
        """Test SuitabilityFactor points count must be breakpoints + 1."""
        with pytest.raises(ValidationError) as exc_info:
            SuitabilityFactor(
                kind="slope",
                weight=5.0,
                breakpoints=[10.0, 20.0],
                points=[8, 5]  # Should be 3 points for 2 breakpoints
            )
        assert "points count must be breakpoints+1" in str(exc_info.value)
    
    def test_suitability_factor_points_range_validation(self):
        """Test SuitabilityFactor points must be integers in [0, 10]."""
        with pytest.raises(ValidationError) as exc_info:
            SuitabilityFactor(
                kind="slope",
                weight=5.0,
                breakpoints=[10.0],
                points=[15, 5]  # 15 is > 10
            )
        assert "each point must be an integer in [0, 10]" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            SuitabilityFactor(
                kind="slope",
                weight=5.0,
                breakpoints=[10.0],
                points=[-1, 5]  # -1 is < 0
            )
        assert "each point must be an integer in [0, 10]" in str(exc_info.value)
    
    def test_suitability_factor_empty_breakpoints_rejected(self):
        """Test SuitabilityFactor rejects empty breakpoints."""
        with pytest.raises(ValidationError) as exc_info:
            SuitabilityFactor(
                kind="slope",
                weight=5.0,
                breakpoints=[],
                points=[5]
            )
        assert "breakpoints and points are required" in str(exc_info.value)
    
    def test_suitability_factor_invalid_kind_rejected(self):
        """Test SuitabilityFactor rejects invalid kind."""
        with pytest.raises(ValidationError) as exc_info:
            SuitabilityFactor(
                kind="invalid_suitability",
                weight=5.0,
                breakpoints=[10.0],
                points=[8, 5]
            )
        assert "Invalid suitability kind" in str(exc_info.value)


class TestMapTaskModels:
    """Test map task related models."""
    
    def test_map_task_creation(self):
        """Test MapTask model creation."""
        created_at = datetime.now(timezone.utc)
        task = MapTask(
            id=1,
            name="Test Task",
            user_id=123,
            district_code="D001",
            status=1,
            created_at=created_at
        )
        assert task.id == 1
        assert task.name == "Test Task"
        assert task.user_id == 123
        assert task.district_code == "D001"
        assert task.status == 1
        assert task.created_at == created_at
    
    def test_map_task_file_creation(self):
        """Test MapTaskFile model creation."""
        created_at = datetime.now(timezone.utc)
        file = MapTaskFile(
            id=1,
            map_task_id=123,
            file_type="output",
            file_path="/data/output.tif",
            created_at=created_at
        )
        assert file.id == 1
        assert file.map_task_id == 123
        assert file.file_type == "output"
        assert file.file_path == "/data/output.tif"
        assert file.created_at == created_at
    
    def test_map_task_details_with_factors(self):
        """Test MapTaskDetails with constraint and suitability factors."""
        created_at = datetime.now(timezone.utc)
        
        constraint = ConstraintFactor(kind="coastlines", value=100.0)
        suitability = SuitabilityFactor(
            kind="slope",
            weight=5.0,
            breakpoints=[10.0],
            points=[8, 2]
        )
        
        details = MapTaskDetails(
            id=1,
            name="Detailed Task",
            user_id=123,
            district_code="D001",
            status=1,
            created_at=created_at,
            constraint_factors=[constraint],
            suitability_factors=[suitability]
        )
        
        assert len(details.constraint_factors) == 1
        assert len(details.suitability_factors) == 1
        assert details.constraint_factors[0].kind == "coastlines"
        assert details.suitability_factors[0].kind == "slope"


class TestCreateMapTaskReq:
    """Test CreateMapTaskReq model and its validation methods."""
    
    def test_create_map_task_req_valid_data(self):
        """Test CreateMapTaskReq with valid data."""
        constraint = ConstraintFactor(kind="rivers", value=50.0)
        suitability = SuitabilityFactor(
            kind="slope", weight=3.0, breakpoints=[15.0], points=[9, 1]
        )
        
        req = CreateMapTaskReq(
            name="Test Analysis",
            district_code="076",  # Auckland
            constraint_factors=[constraint],
            suitability_factors=[suitability]
        )
        
        assert req.name == "Test Analysis"
        assert req.district_code == "076"
        assert len(req.constraint_factors) == 1
        assert len(req.suitability_factors) == 1
    
    def test_create_map_task_req_invalid_district_code(self):
        """Test CreateMapTaskReq rejects invalid district code."""
        constraint = ConstraintFactor(kind="lakes", value=25.0)
        suitability = SuitabilityFactor(
            kind="roads", weight=2.0, breakpoints=[10.0], points=[7, 3]
        )
        
        with pytest.raises(ValidationError) as exc_info:
            CreateMapTaskReq(
                name="Invalid District",
                district_code="INVALID",
                constraint_factors=[constraint],
                suitability_factors=[suitability]
            )
        
        error = exc_info.value.errors()[0]
        assert error["loc"] == ("district_code",)
        assert "Invalid district_code" in str(error["msg"])
    
    def test_create_map_task_req_empty_suitability_factors(self):
        """Test CreateMapTaskReq requires at least one suitability factor."""
        constraint = ConstraintFactor(kind="residential", value=100.0)
        
        with pytest.raises(ValidationError) as exc_info:
            CreateMapTaskReq(
                name="No Suitability",
                district_code="060",  # Christchurch
                constraint_factors=[constraint],
                suitability_factors=[]  # Empty list
            )
        
        assert "At least one suitability factor is required" in str(exc_info.value)
    
    def test_create_map_task_req_normalization_methods(self):
        """Test the normalization helper methods."""
        from app.models import CreateMapTaskReq
        
        # Test _unique_by_kind method
        constraint1 = ConstraintFactor(kind="rivers", value=50.0)
        constraint2 = ConstraintFactor(kind="rivers", value=75.0)  # Duplicate kind
        constraint3 = ConstraintFactor(kind="lakes", value=25.0)
        
        constraints = [constraint1, constraint2, constraint3]
        unique_constraints = CreateMapTaskReq._unique_by_kind(constraints)
        
        # Should keep only first occurrence of each kind
        assert len(unique_constraints) == 2
        kinds = [c.kind for c in unique_constraints]
        assert "rivers" in kinds
        assert "lakes" in kinds
        # Should keep the first rivers constraint
        rivers_constraint = next(c for c in unique_constraints if c.kind == "rivers")
        assert rivers_constraint.value == 50.0  # First occurrence
    
    def test_create_map_task_req_ordering_by_allowed(self):
        """Test the _order_by_allowed method."""
        from app.models import CreateMapTaskReq
        from app.gis.consts import ALLOWED_CONSTRAINTS
        
        # Create constraints in reverse order
        constraints = [
            ConstraintFactor(kind="residential", value=10.0),
            ConstraintFactor(kind="rivers", value=20.0),
            ConstraintFactor(kind="lakes", value=30.0),
        ]
        
        ordered = CreateMapTaskReq._order_by_allowed(constraints, ALLOWED_CONSTRAINTS)
        
        # Should be ordered according to ALLOWED_CONSTRAINTS order
        ordered_kinds = [c.kind for c in ordered]
        expected_order = [kind for kind in ALLOWED_CONSTRAINTS if kind in ordered_kinds]
        assert ordered_kinds == expected_order


class TestAdminModels:
    """Test admin-related models."""
    
    def test_user4admin_creation(self):
        """Test User4Admin model creation."""
        from app.models import User4Admin
        
        created_at = datetime.now(timezone.utc)
        user = User4Admin(
            id=123,
            provider="oauth",
            sub="user123",
            email="admin@example.com",
            role=1,  # ADMIN
            status=1,  # ACTIVE
            created_at=created_at,
            last_login=created_at
        )
        
        assert user.id == 123
        assert user.provider == "oauth"
        assert user.email == "admin@example.com"
        assert user.role == 1
        assert user.status == 1
    
    def test_user4admin_optional_fields(self):
        """Test User4Admin with optional fields as None."""
        from app.models import User4Admin
        
        user = User4Admin()
        
        assert user.id is None
        assert user.provider is None
        assert user.email is None
        assert user.role is None
        assert user.status is None
    
    def test_admin_update_user_status_request(self):
        """Test AdminUpdateUserStatusRequest model."""
        from app.models import AdminUpdateUserStatusRequest, UserStatus
        
        request = AdminUpdateUserStatusRequest(
            user_id=456,
            status=UserStatus.LOCKED
        )
        
        assert request.user_id == 456
        assert request.status == UserStatus.LOCKED
        assert request.status == 2  # LOCKED value
    
    def test_user_enums(self):
        """Test UserRole and UserStatus enums."""
        from app.models import UserRole, UserStatus
        
        # Test UserRole enum
        assert UserRole.ADMIN == 1
        assert UserRole.USER == 2
        
        # Test UserStatus enum
        assert UserStatus.ACTIVE == 1
        assert UserStatus.LOCKED == 2