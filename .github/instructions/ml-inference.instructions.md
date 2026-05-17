---
applyTo: "src/ml/inference/**/*.py,src/ml/**/*predict*.py,src/ml/**/*serve*.py"
---

## Purpose

Guide Copilot for ML inference and model serving code with production-ready defaults.

## Guidelines

### Model Loading

- Load models once at startup using FastAPI lifespan or a module-level singleton, never
  per-request.
- Validate that the loaded model artifact matches the expected version or schema before
  serving.
- Raise a clear error at startup if the model file is missing or incompatible.

### Prediction

- Validate and sanitize all inputs before passing them to the model (type, shape, range).
- Return structured prediction responses with at least `prediction`, `confidence`, and
  `model_version`.
- Catch and log model errors explicitly; never expose raw stack traces in API responses.

### Performance

- Prefer batch inference over single-sample loops when throughput matters.
- Use `async def` handlers to avoid blocking the event loop during I/O (model load, disk
  reads).
- Consider a request queue or semaphore to cap concurrent inference under load.

### Observability

- Record per-request latency and prediction distribution as Prometheus metrics.
- Log structured prediction events (input summary, output label, latency) at INFO level.
- Emit a warning log when prediction confidence falls below a configured threshold.

### Testing

- Add a `pytest` test that loads the model artifact and verifies output shape and dtype.
- Add a test for the invalid-input path (malformed payload should return HTTP 422, not
  500).

## Examples

```python
from functools import lru_cache


@lru_cache(maxsize=1)
def load_model(path: str):
    """Load and cache the ML model artifact from disk.

    Args:
        path: Absolute path to the serialized model file.

    Returns:
        The deserialized model object ready for inference.
    """
    import joblib
    return joblib.load(path)
```
