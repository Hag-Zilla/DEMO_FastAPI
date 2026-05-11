# Code Review Checklist

Review this code for:

1. **PEP 8 & Style**
   - Line length <= 120 chars
   - 2 blank lines between top-level definitions
   - Imports sorted (isort)
   - No trailing whitespace

2. **Type Hints & Docstrings**
   - All functions/classes have docstrings (Google style)
   - Parameters, returns, exceptions documented
   - Type hints on function signatures

3. **Security**
   - No hardcoded secrets (API keys, passwords, tokens)
   - No SQL injection risks (use parameterized queries)
   - CORS/Auth configured if applicable

4. **Tests & Coverage**
   - Unit tests for core logic
   - Edge cases covered
   - Minimum 80% coverage for critical modules

5. **Performance**
   - No obvious N+1 queries
   - Appropriate use of async/await
   - Caching where relevant

6. **Error Handling**
   - try/except with specific exceptions
   - Meaningful error messages
   - Logging at appropriate levels

Reference standards: #file:.github/copilot-instructions.md
Reference auth rules: #file:.github/instructions/auth-security.instructions.md
Reference API rules: #file:.github/instructions/fastapi-api.instructions.md
