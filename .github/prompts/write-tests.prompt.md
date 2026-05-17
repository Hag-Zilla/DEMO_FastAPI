# Write Unit Tests (pytest)

Generate unit tests for the following code using `pytest`:

1. **Test structure**:

   ```python
   def test_<function>_<scenario>():
       # Arrange
       input_data = ...

       # Act
       result = function(input_data)

       # Assert
       assert result == expected
   ```

   Name tests as `test_<function>_<scenario>` (e.g., `test_create_user_duplicate_username`).
   Group related tests in a `TestXxxClass` when testing a service or class.

2. **Coverage**:
   - Happy path (valid inputs)
   - Edge cases (empty, None, boundary values)
   - Error cases (invalid inputs, exceptions)

3. **Fixtures** for reusable setup — place shared fixtures in `conftest.py`:

   ```python
   # conftest.py
   import pytest

   @pytest.fixture
   def db():
       """Provide a clean in-memory DB session for each test."""
       Base.metadata.create_all(bind=engine)
       session = SessionLocal()
       yield session
       session.close()
       Base.metadata.drop_all(bind=engine)

   @pytest.fixture
   def sample_data():
       return {"id": 1, "name": "test"}
   ```

4. **Mocking** external dependencies (DB, API calls):

   ```python
   from unittest.mock import patch
   @patch('module.external_function')
   def test_with_mock(mock_func):
       ...
   ```

5. **Parametrization** for multiple inputs:

   ```python
   @pytest.mark.parametrize("input,expected", [...])
   def test_multiple(input, expected):
       ...
   ```

Ensure tests are concise and focused on one thing per test.

<!-- No domain-specific instruction file applies — this prompt is intentionally language- and domain-agnostic. -->
Reference standards: #file:.github/copilot-instructions.md
