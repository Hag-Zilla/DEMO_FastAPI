---
applyTo: "src/**/pipelines/**/*.py,src/**/etl/**/*.py,src/**/*pipeline*.py,src/**/*etl*.py,dbt/**/*.sql"
---

## Purpose

Guide Copilot for data engineering code: ETL/ELT pipelines, SQL conventions, ORM
patterns, schema migrations, and stream processing.

## Guidelines

### Pipeline Design

- Design pipelines as idempotent operations; running them twice must produce the same
  result.
- Prefer incremental loads over full reloads; use watermarks or partition keys.
- Separate extraction, transformation, and loading into distinct, testable functions.
- Handle schema evolution explicitly; never silently drop or rename columns.

### SQL and ORM

- Use SQLAlchemy Core for performant bulk operations; use ORM for single-record CRUD.
- Parameterize all queries; never use string interpolation for SQL values.
- Name tables and columns in `snake_case`; use plural table names.
- Add indexes on all foreign keys and frequently filtered columns.

### Schema Migrations

- Use Alembic for all schema changes; never modify the database schema manually.
- Write reversible migrations (`upgrade` + `downgrade`) unless destructive by design.
- Test migrations on a copy of production data before applying to production.

### Error Handling and Observability

- Log row counts at the entry and exit of each pipeline step.
- Emit pipeline metrics (rows processed, errors, latency) to Prometheus.
- Route failed records to a dead-letter table; never silently drop them.

### Stream Processing

- Prefer exactly-once semantics when the framework supports it (Kafka + Spark/Flink).
- Commit offsets only after successful processing and downstream write.

## Examples

```python
import logging
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)


def load_incremental(
    source_conn_str: str,
    target_conn_str: str,
    watermark: str,
) -> int:
    """Load new records from source to target since the last watermark.

    Args:
        source_conn_str: SQLAlchemy connection string for the source DB.
        target_conn_str: SQLAlchemy connection string for the target DB.
        watermark: ISO timestamp of the last successful load.

    Returns:
        Number of rows inserted.
    """
    src = create_engine(source_conn_str)
    tgt = create_engine(target_conn_str)
    with src.connect() as conn:
        rows = conn.execute(
            text("SELECT * FROM events WHERE created_at > :wm"),
            {"wm": watermark},
        ).fetchall()
    logger.info("Fetched %d rows from source", len(rows))
    payload = [
        {
            "id": row.id,
            "created_at": row.created_at,
            "event_type": row.event_type,
            "payload": row.payload,
        }
        for row in rows
    ]
    with tgt.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO events (id, created_at, event_type, payload)
                VALUES (:id, :created_at, :event_type, :payload)
                """
            ),
            payload,
        )
    return len(payload)
```
