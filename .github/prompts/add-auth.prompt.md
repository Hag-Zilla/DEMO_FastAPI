# Add Authentication and Authorization

Add JWT-based authentication and role-based authorization to the selected FastAPI
application following these requirements:

1. **Token endpoint** (`POST /auth/token`):
   - Accept `username` and `password` via OAuth2 password flow
   - Return `access_token` (15 min expiry) and `refresh_token` (7 day expiry)
   - Hash passwords with `bcrypt`; never store or log plaintext passwords

2. **Protected routes**:
   - Add `Depends(get_current_user)` to all non-public endpoints
   - Add `Depends(require_role("admin"))` to admin-only endpoints

3. **JWT validation**:
   - Validate signature, expiry, and issuer on every request
   - Return HTTP 401 for invalid or expired tokens; HTTP 403 for insufficient role

4. **Secrets**:
   - Load `SECRET_KEY` and `ALGORITHM` from environment via `pydantic-settings`
   - Never hardcode secrets; add `SECRET_KEY` to `.env.example` with a placeholder
   - Mark `SECRET_KEY` as `pydantic.SecretStr`

5. **Tests**:
   - Valid credentials → token → protected route access (HTTP 200)
   - Invalid credentials → HTTP 401
   - Expired token → HTTP 401
   - Insufficient role → HTTP 403

Reference standards: #file:.github/copilot-instructions.md
Reference auth rules: #file:.github/instructions/auth-security.instructions.md
