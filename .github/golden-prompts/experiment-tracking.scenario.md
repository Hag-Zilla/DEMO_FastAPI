# Scenario: MLflow Experiment Tracking

## Prompt

Track a random forest cross-validation experiment in MLflow. Log all hyperparameters,
per-fold metrics, and register the model to the registry if mean F1 exceeds 0.80.

## Expected Behavior

- Calls `mlflow.set_experiment()` before opening the run
- Logs all hyperparameters as a dict via `mlflow.log_params()`
- Logs per-fold metrics with `step=fold_index` using `mlflow.log_metric()`
- Tags the run with `git_commit`, `dataset_version`, and `author`
- Registers the model only if the threshold is met; raises explicitly otherwise
- Uses `mlflow.sklearn.log_model()` for artifact persistence

## Must Include

- `mlflow.set_experiment()` call with a meaningful name (`project/model/variant`)
- Per-step metric logging with the `step=` argument
- Minimum metadata tags (`git_commit`, `author`)
- Conditional model registration with an explicit threshold check

## Must Avoid

- Relying on the default MLflow experiment (no `set_experiment` call)
- Logging individual params from scattered locations (use `log_params(dict)`)
- Hardcoded F1 threshold as a magic number inline in the function body
- Registering model unconditionally without metric validation
