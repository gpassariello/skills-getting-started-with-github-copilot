# Tests for High School Management System

This directory contains comprehensive tests for the High School Management System API built with FastAPI.

## Test Structure

### Test Files

- **`conftest.py`** - Pytest configuration and shared fixtures
- **`test_main_endpoints.py`** - Tests for basic API endpoints (`/`, `/activities`)
- **`test_signup.py`** - Tests for the signup functionality (`/activities/{name}/signup`)
- **`test_unregister.py`** - Tests for the unregister functionality (`/activities/{name}/unregister`)
- **`test_integration.py`** - Integration tests covering complete workflows

### Fixtures

- **`client`** - FastAPI test client for making HTTP requests
- **`reset_activities`** - Resets the activities database to initial state before each test
- **`sample_email`** - Provides a sample email for testing
- **`empty_activity`** - Creates an empty activity for testing

## Running Tests

### Option 1: Using the test runner script
```bash
python run_tests.py
```

### Option 2: Using pytest directly
```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_signup.py

# Run specific test
pytest tests/test_signup.py::TestSignupEndpoint::test_signup_success
```

## Test Coverage

The tests achieve **100% code coverage** of the main application code in `src/app.py`.

Coverage includes:
- All API endpoints
- All success and error paths
- Edge cases and boundary conditions
- URL encoding and special characters
- Data consistency after operations

## Test Categories

### Unit Tests
- Individual endpoint functionality
- Input validation and error handling
- Response format verification

### Integration Tests
- Complete activity lifecycle (signup → unregister)
- Multiple operations on same activity
- Cross-activity operations
- Data consistency verification

### Edge Cases
- Non-existent activities
- Duplicate signups
- Empty emails
- Special characters in emails
- URL encoding

## Dependencies

The tests require the following packages (included in `requirements.txt`):
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting
- `httpx` - HTTP client for FastAPI testing

## Configuration

Test configuration is in `pytest.ini`:
- Test discovery in `tests/` directory
- Verbose output by default
- Short traceback format
- Deprecation warning filtering