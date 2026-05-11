# Scenario: Pandera Schema Validation

## Prompt

Add Pandera schema validation to a pipeline ingesting customer records. Enforce
non-null age between 0 and 150, unique customer IDs greater than zero, and a binary
churn label (0 or 1).

## Expected Behavior

- Defines a `pa.DataFrameModel` subclass with typed, annotated fields
- Uses `pa.Field()` with explicit constraints (`gt`, `ge`, `le`, `isin`, `nullable`)
- Applies `@pa.check_types` decorator to the ingestion function
- Treats schema violations as pipeline-stopping errors, not warnings
- Documents the schema contract in the class docstring

## Must Include

- `pa.DataFrameModel` subclass with at least 3 validated fields
- `strict = True` in the inner `Config` class
- `@pa.check_types` on the ingestion function signature
- Docstring describing the schema expectations

## Must Avoid

- Manual `if df["col"].isnull().any(): raise` checks replacing Pandera
- Silently dropping invalid rows instead of raising
- Missing `strict = True` (allows undeclared columns through unchecked)
- Validation only at ingestion boundary, skipping training pipeline
