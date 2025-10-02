# Testing Guide

## 🚀 Quick Start

### Install Test Dependencies
```bash
uv sync --group test
```

### Running Tests

#### Basic Tests
```bash
# Run all unit tests
uv run pytest tests/unit/

# Verbose output
uv run pytest tests/unit/ -v
```

#### Tests with Coverage
```bash
# Terminal coverage report
uv run pytest tests/unit/ --cov=app --cov-report=term-missing

# Generate HTML coverage report
uv run pytest tests/unit/ --cov=app --cov-report=html:htmlcov

# Generate XML coverage report
uv run pytest tests/unit/ --cov=app --cov-report=xml
```

#### Specific Tests
```bash
# Run specific test file
uv run pytest tests/unit/test_security.py

# Run specific test class
uv run pytest tests/unit/test_models.py::TestSuitabilityFactor

# Run specific test method
uv run pytest tests/unit/test_security.py::TestPasswordHashing::test_get_password_hash_creates_valid_hash
```