# Data Pipeline (ETL/ELT)

Generate a data pipeline for the described transformation following these requirements:

1. **Design principles**:
   - Idempotent: running twice must produce the same result
   - Incremental: process only new or changed records using a watermark or partition key
   - Atomic: writes must be transactional (all-or-nothing)

2. **Structure** (three distinct, testable functions):
   - `extract(source, watermark)` — fetch raw records since last run
   - `transform(records)` — validate schema, apply business rules, enrich
   - `load(records, target)` — write to destination with upsert semantics

3. **Observability**:
   - Log row counts at extract, transform, and load boundaries
   - Emit `pipeline_rows_processed_total` and `pipeline_errors_total` Prometheus
     metrics
   - Write failed records to a dead-letter table, not the main pipeline

4. **Error handling**:
   - Retry transient failures (network, DB lock) with exponential backoff (max 3
     retries)
   - Raise on schema violations; do not silently drop malformed records

5. **Testing**:
   - Unit test each stage with a small synthetic dataset
   - Test idempotency: run the pipeline twice and assert output equality

Reference standards: #file:.github/copilot-instructions.md
Reference data engineering rules: #file:.github/instructions/data-engineering.instructions.md
