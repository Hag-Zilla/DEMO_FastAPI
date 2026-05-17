# Scenario: MLOps Training Pipeline with Validation Gate

## Prompt

Write a Prefect flow that trains a binary classifier, evaluates it against a registered
baseline, and registers the model to MLflow only if accuracy improves by at least 2%.

## Expected Behavior

- Separates training, evaluation, and registration into distinct `@task` functions
- Logs all hyperparameters and the dataset version to MLflow at run start
- Fails the registration task explicitly if the accuracy threshold is not met
- Tags the run with `git_commit` and `author` metadata
- Passes the threshold as a flow parameter, not a hardcoded constant

## Must Include

- `@task` and `@flow` decorators from Prefect
- `mlflow.log_params()` and `mlflow.log_metrics()` calls
- Explicit validation gate that raises `ValueError` on threshold failure
- Parameterized threshold (not a magic number inline)
- Random seed set for reproducibility

## Must Avoid

- Registering model without a validation step
- Hardcoded accuracy threshold inline
- `print`-only observability
- Missing `mlflow.set_experiment()` call before the run
