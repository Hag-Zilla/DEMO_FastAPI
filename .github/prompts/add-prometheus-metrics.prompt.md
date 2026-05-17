# Add Prometheus Instrumentation

Add Prometheus metrics to the selected code following these requirements:

1. **Metric selection**:
   - `Counter` for events that only increase (requests, errors, predictions).
   - `Histogram` for latency or size distributions (response time, payload size).
   - `Gauge` for values that go up and down (queue depth, active connections).

2. **Naming convention** (`snake_case`, descriptive):
   - Pattern: `<service>_<noun>_<unit>_total` for counters (e.g., `api_requests_total`).
   - Pattern: `<service>_<noun>_<unit>` for histograms (e.g., `api_request_duration_seconds`).

3. **Labels**: use low-cardinality labels only (e.g., `method`, `endpoint`, `status_code`).
   Never use user IDs or raw query strings as labels.

4. **Placement**: define metrics at **module level**, never inside a function or class method.

5. **Expose**: ensure `/metrics` endpoint is registered and served by `prometheus_client.make_asgi_app()` or equivalent.

6. **Tests**: add a pytest test that imports the module and verifies the metric is registered without error.

Reference standards: #file:.github/copilot-instructions.md
Reference observability rules: #file:.github/instructions/observability.instructions.md
