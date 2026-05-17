# Scenario: Prometheus Instrumentation for FastAPI

## Prompt

Add Prometheus metrics to a FastAPI service: request count by endpoint and status code,
request latency histogram, and a gauge for currently active requests.

## Expected Behavior

- Defines all metrics at module level, not inside route handlers or functions
- Uses `Counter` for request count, `Histogram` for latency, `Gauge` for active requests
- Applies low-cardinality labels only (`method`, `endpoint`, `status_code`)
- Exposes `/metrics` endpoint using `prometheus_client`
- Does not mix `/metrics` with business API routes

## Must Include

- Module-level metric definitions with correct type and label list
- `/metrics` endpoint registration (via `make_asgi_app()` or equivalent)
- At least one test verifying metric registration on import without error
- Histogram with explicit bucket boundaries

## Must Avoid

- High-cardinality labels (user IDs, raw URLs, full query strings)
- Metric definitions inside route handlers or middleware bodies
- Missing `/metrics` endpoint
- `print` for instrumentation output
