# Scenario: Incremental ETL Pipeline

## Prompt

Write a Python function that loads new customer events incrementally from PostgreSQL
to a data warehouse table. Use a watermark, ensure idempotency, and route failed
records to a dead-letter table.

## Expected Behavior

- Designs the pipeline as an idempotent, incremental operation
- Uses parameterized SQL (no string interpolation for values)
- Logs row counts at extract and load boundaries
- Routes malformed records to a dead-letter table, not silently discards them
- Wraps writes in a transaction or uses upsert semantics

## Must Include

- Watermark-based incremental load pattern
- Parameterized SQLAlchemy query with named parameters
- `logging` calls with row counts at each boundary
- Dead-letter handling for failed records

## Must Avoid

- Full reload pattern (`DELETE FROM` + full insert)
- String interpolation in SQL values (`f"... {user_input} ..."`)
- Silent exception swallowing
- `print` statements instead of `logging`
- Hardcoded connection strings
