---
applyTo: "src/**/validation/**/*.py,src/**/*validation*.py,src/**/*schema*.py,src/**/*quality*.py"
---

## Purpose

Guide Copilot for data validation code: schema enforcement, quality checks, and data
versioning patterns using Pydantic, Pandera, and DVC.

## Guidelines

### Schema Validation

- Define schemas with Pydantic v2 `BaseModel` for structured records; use `pandera`
  for DataFrame schemas.
- Validate at every data ingestion boundary; fail fast on schema violations.
- Log validation failures with full context (column, row index, expected vs actual)
  before raising.
- Version schemas alongside data artifacts; treat schema changes as breaking changes.

### Quality Checks

- Check for nulls, duplicates, and out-of-range values as a baseline suite.
- Define thresholds explicitly (e.g., `null_rate < 0.01`); document magic values.
- Run quality checks as part of the training pipeline, not only during ingestion.
- Emit data quality metrics (null rate, schema violations) to Prometheus or MLflow.

### Data Versioning

- Use DVC to version datasets and link them to model artifacts.
- Never commit raw data to git; use `.dvc` pointer files instead.
- Document data lineage (source → transform → artifact) in a `data/README.md`.

## Examples

```python
import pandera as pa
from pandera.typing import DataFrame, Series


class CustomerSchema(pa.DataFrameModel):
    """Schema for the customer features table."""

    customer_id: Series[int] = pa.Field(gt=0, unique=True)
    age: Series[float] = pa.Field(ge=0, le=150, nullable=False)
    churn: Series[int] = pa.Field(isin=[0, 1])

    class Config:
        """Pandera configuration."""

        strict = True
        coerce = True


@pa.check_types
def preprocess(df: DataFrame[CustomerSchema]) -> DataFrame[CustomerSchema]:
    """Validate and preprocess the customer features DataFrame.

    Args:
        df: Raw customer DataFrame; validated against CustomerSchema on entry.

    Returns:
        Preprocessed and validated DataFrame.

    Raises:
        pa.errors.SchemaError: If the DataFrame does not conform to the schema.
    """
    return df.dropna(subset=["age"])
```
