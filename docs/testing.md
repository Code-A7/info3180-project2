# Testing Guide

This document covers how to run and write tests for the DriftDater application.

## Overview

The application includes two types of tests:

- **Backend tests** - Python-based tests using [pytest](https://docs.pytest.org/) for testing Flask API endpoints, database models, and business logic
- **Frontend tests** - JavaScript-based tests using [Vitest](https://vitest.dev/) for unit testing Vue components and [Playwright](https://playwright.dev/) for end-to-end testing

## Directory Structure

```
tests/                    # Backend tests (Python)
├── conftest.py           # Shared fixtures and configuration
├── helpers.py            # Test helper functions
├── test_auth.py          # Authentication tests
├── test_profile.py       # Profile management tests
├── test_matches.py       # Match algorithm tests
├── test_likes.py         # Likes/dislikes tests
├── test_messaging.py     # Messaging tests
├── test_notifications.py # Notification tests
├── test_search.py        # Search functionality tests
├── test_integration.py   # Integration tests
├── test_migrations.py    # Database migration tests
├── test_seed.py          # Seed script tests
├── test_utils.py         # Utility function tests
└── test_views_utils.py   # View utility tests

src/__tests__/            # Frontend unit tests (JavaScript)
e2e/                      # End-to-end tests (Playwright)
```

## Running Tests

### Prerequisites

1. Set up your Python virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Install Node.js dependencies:
```bash
npm install
```

### Backend Tests (pytest)

Use the `run-tests.sh` script for running backend tests:

```bash
# Run all backend tests
./run-tests.sh

# Run specific test categories
./run-tests.sh --auth          # Authentication tests
./run-tests.sh --profile       # Profile management tests
./run-tests.sh --matches       # Match algorithm tests
./run-tests.sh --likes         # Likes/dislikes tests
./run-tests.sh --messaging     # Messaging tests
./run-tests.sh --notifications # Notification tests
./run-tests.sh --search        # Search tests
./run-tests.sh --integration   # Integration tests
./run-tests.sh --fast          # Core tests only (auth, seed, utils, migrations)
./run-tests.sh --coverage      # All tests with coverage report
```

You can also run tests directly with `pytest`:

```bash
# Activate virtual environment first
source .venv/bin/activate

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_auth.py -v

# Run specific test function
pytest tests/test_auth.py::test_register_success -v

# Run tests with verbose output and show all info
pytest tests/ -v --tb=short

# Run tests with coverage
pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing
```

### Frontend Tests (Vitest + Playwright)

```bash
# Unit tests with Vitest
npm run test              # Run unit tests
npm run test:watch        # Watch mode for development
npm run test:ui           # Run tests with Vitest UI
npm run test:coverage     # Run tests with coverage report
npm run lint              # Run ESLint

# E2E tests with Playwright
npm run test:e2e          # Run E2E tests
npm run test:e2e:ui       # Run E2E tests with Playwright UI
npm run test:e2e:headed   # Run E2E tests in headed mode (visible browser)
npm run test:e2e:all      # Run E2E tests with all browser configurations
```

### All Tests Together

```bash
# Run all tests (both frontend and backend)
npm run test:all          # This runs vitest AND playwright test
```

## Writing Tests

### Backend Test Structure

Backend tests follow a standard pytest structure:

```python
# tests/test_example.py
import pytest

def test_example(client):
    """Test description here."""
    # Test code here
    pass
```

### Frontend Test Structure

Frontend tests use Vue Test Utils with Vitest:

```javascript
// src/components/Example.spec.js
import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ExampleComponent from '../ExampleComponent.vue'

describe('ExampleComponent', () => {
  it('renders correctly', () => {
    const wrapper = mount(ExampleComponent)
    expect(wrapper.text()).toContain('Expected text')
  })
})
```

## Test Fixtures

### Backend Fixtures (conftest.py)

The `conftest.py` file defines shared fixtures:

| Fixture | Description |
|---------|-------------|
| `app` | Creates and configures a test Flask application instance |
| `client` | Creates a test client for the app |
| `runner` | Creates a test CLI runner for the app |
| `mock_socket_emit` | Mocks WebSocket emit function |
| `mock_socket_emit_direct` | Direct mock for socket_emit in matches module |
| `verified_user` | Creates a verified test user with login token |
| `user_with_profile` | Creates a verified user with complete profile |
| `second_user` | Creates a second verified test user |
| `second_user_with_profile` | Creates a second verified user with profile |
| `match_pair` | Creates a mutual match between two users |
| `third_user` | Creates a third verified test user |
| `third_user_with_profile` | Creates a third verified user with profile |
| `app_context` | Provides an app context for tests |

### Helper Functions (helpers.py)

The `helpers.py` file provides utility functions:

| Function | Description |
|----------|-------------|
| `create_user(app, email, is_verified, password)` | Create a test user |
| `create_profile(app, user_id, **kwargs)` | Create a test profile |
| `get_auth_token(client, email, password)` | Get authentication token for a user |
| `create_test_user(...)` | Create a complete test user with profile |
| `create_incompatible_profile(app, user_id)` | Create an incompatible profile for testing filters |
| `get_unverified_user(client, app, email)` | Create an unverified user |
| `create_mutual_match(client, app, user1_id, user2_id, token1)` | Create a mutual match between two users |
| `verify_user(app, email)` | Verify a user's email |

## Code Coverage

### Backend Coverage

```bash
# Run tests with coverage report
./run-tests.sh --coverage

# Or directly with pytest
pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing
```

The coverage report is generated at `htmlcov/index.html`.

### Frontend Coverage

```bash
# Run tests with coverage
npm run test:coverage
```

## Test Naming Convention

### Backend Tests
- File names: `test_*.py` (e.g., `test_auth.py`, `test_profile.py`)
- Function names: `test_*` (e.g., `test_register_success`, `test_login_invalid_credentials`)

### Frontend Tests
- File names: `*.spec.js` or `*.test.js` (e.g., `Button.spec.js`, `Login.test.js`)
- Describe blocks: `describe('ComponentName', () => { ... })`
- Test names: `it('should ...', () => { ... })`

## Continuous Integration

Tests are automatically run on GitHub Actions when pushing to the repository. The CI pipeline runs both frontend and backend tests to ensure code quality.

## Best Practices

1. **Test Isolation**: Each test should be independent and not depend on other tests
2. **Test Naming**: Use descriptive names that explain what is being tested
3. **Assertions**: Use clear assertions with meaningful error messages
4. **Fixtures**: Use fixtures to avoid code duplication
5. **Cleanup**: Always clean up after tests that modify data
6. **Coverage**: Aim for high test coverage, especially for critical business logic
7. **Mocking**: Use mocks for external dependencies (database, APIs, WebSocket)
8. **Test Data**: Use test-specific configurations to avoid modifying production data
```
