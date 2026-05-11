---
applyTo: "src/**/experiments/**/*.py,src/**/*experiment*.py,src/**/*tracking*.py,src/**/*mlflow*.py"
---

## Purpose

Guide Copilot for experiment tracking code using MLflow or equivalent tools, with
reproducible runs and structured artifact management.

## Guidelines

### Experiment Setup

- Name experiments with the pattern `<project>/<model>/<variant>` for clear hierarchy.
- Always call `mlflow.set_experiment()` before logging; never rely on the default
  experiment.
- Pass all hyperparameters as a dict to `mlflow.log_params()` at run start.
- Tag runs with `git_commit`, `dataset_version`, and `author` as minimum metadata.

### Metrics and Artifacts

- Log validation metrics at every epoch; log test metrics only once at run end.
- Use `mlflow.log_metric(key, value, step=epoch)` for time-series metrics.
- Log the trained model with `mlflow.sklearn.log_model()` or framework equivalent.
- Store preprocessing artifacts (scalers, encoders) alongside the model artifact.

### Model Registry

- Register models only when validation metrics pass defined thresholds.
- Use stages: `Staging` for validated candidates, `Production` for deployed versions.
- Never overwrite a registered model version; always create a new version.

### Reproducibility

- Log the full config object with `mlflow.log_dict()`; avoid logging individual params
  from scattered locations.
- Record the random seed as a tracked parameter, not a hardcoded constant.

## Examples

```python
import mlflow
import mlflow.sklearn


def run_experiment(
    params: dict,
    X_train,
    y_train,
    X_val,
    y_val,
) -> str:
    """Train a model and log the full run to MLflow.

    Args:
        params: Hyperparameter dict to log and pass to the model.
        X_train: Training features.
        y_train: Training labels.
        X_val: Validation features.
        y_val: Validation labels.

    Returns:
        MLflow run ID.
    """
    mlflow.set_experiment("myproject/random-forest/baseline")
    with mlflow.start_run() as run:
        mlflow.log_params(params)
        mlflow.set_tags({"git_commit": "abc123", "author": "user"})
        model = train(params, X_train, y_train)
        metrics = evaluate(model, X_val, y_val)
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(model, artifact_path="model")
        return run.info.run_id
```
