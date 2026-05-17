---
applyTo: "src/**/dags/**/*.py,src/**/*dag*.py,src/**/*workflow*.py,src/**/workflows/**/*.py"
---

## Purpose

Guide Copilot for MLOps pipeline code: orchestration (Airflow, Prefect, Dagster),
CI/CD workflows, validation gates, and deployment strategies.

## Guidelines

### Workflow Structure

- Separate training, evaluation, and deployment into distinct tasks with explicit
  dependencies.
- Pass hyperparameters and dataset versions as pipeline parameters, not hardcoded
  constants.
- Cache expensive artifacts (model, preprocessor) between pipeline stages.
- Pin all dependency versions; never use floating tags in production pipelines.

### Training Pipelines

- Run training on GPU resources only when necessary; use CPU for unit tests.
- Log all hyperparameters and dataset versions to the experiment tracker at run start.
- Fail the pipeline if any training metric is worse than the registered baseline by
  more than a defined threshold.

### Validation Gates

- Add a model validation task that runs inference on a held-out golden dataset before
  any deployment task.
- Block deployment if latency P99 or accuracy thresholds are not met.
- Generate and archive an evaluation report as a pipeline artifact.

### Deployment Strategies

- Prefer rolling updates for stateless services; use canary deployment for model
  endpoints with traffic shifting.
- Automate rollback on health check failure; never require manual intervention.
- Tag deployed model versions in the registry with the Git SHA and pipeline run ID.

## Examples

```python
from prefect import flow, task
import mlflow


@task
def train_model(dataset_version: str, params: dict) -> str:
    """Train a model and return the MLflow run ID.

    Args:
        dataset_version: DVC tag of the dataset to train on.
        params: Hyperparameter dict to log and use for training.

    Returns:
        MLflow run ID for the completed training run.
    """
    with mlflow.start_run() as run:
        mlflow.log_params(params)
        mlflow.log_param("dataset_version", dataset_version)
        # ... training logic ...
        return run.info.run_id


@task
def validate_model(run_id: str, accuracy_threshold: float = 0.85) -> None:
    """Assert model metrics meet minimum thresholds before deployment.

    Args:
        run_id: MLflow run ID of the trained model.
        accuracy_threshold: Minimum acceptable accuracy.

    Raises:
        ValueError: If model accuracy is below the threshold.
    """
    client = mlflow.tracking.MlflowClient()
    metrics = client.get_run(run_id).data.metrics
    if metrics.get("accuracy", 0) < accuracy_threshold:
        raise ValueError(f"Accuracy {metrics['accuracy']:.3f} < {accuracy_threshold}")


@flow
def ml_training_pipeline(dataset_version: str = "latest") -> None:
    """End-to-end ML training pipeline with validation gate."""
    params = {"n_estimators": 100, "max_depth": 5, "seed": 42}
    run_id = train_model(dataset_version, params)
    validate_model(run_id)
```
