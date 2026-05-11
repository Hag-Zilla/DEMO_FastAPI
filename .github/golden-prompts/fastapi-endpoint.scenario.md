# Scenario: FastAPI Endpoint

## Prompt

Create a FastAPI POST endpoint `/predict` for sentiment analysis with request and response models.
Include validation and a pytest TestClient test.

## Expected Behavior

- Uses Pydantic models for request and response
- Includes explicit status code
- Provides route docstring
- Suggests structured error handling with `HTTPException`
- Includes a basic `pytest` + `TestClient` test

## Must Include

- Type hints
- Model field validation guidance
- At least one test case

## Must Avoid

- Hardcoded secrets
- Vague pseudo-code without runnable structure
- Ignoring FastAPI path-specific instruction style
