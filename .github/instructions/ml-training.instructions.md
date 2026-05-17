---
applyTo: "src/ml/training/**/*.py,src/ml/**/*train*.py"
---

## Purpose

Guide Copilot output for ML training code with reproducible and testable practices.

## Scope

Applies to training modules under `src/ml/training/` and files matching `src/ml/**/*train*.py`.

## Guidelines

### Data and Validation

- Prefer cross-validation (`cross_validate`, `KFold`, `StratifiedKFold`) for robust
  evaluation.
- Use at least a 70/15/15 train/validation/test split unless there is a documented reason
  not to.
- Validate dataset shape, null values, and obvious outliers before training.
- Set random seeds for reproducibility.

### Hyperparameters and Tracking

- Document hyperparameters in function docstrings or config objects.
- Prefer experiment tracking (MLflow or equivalent) for metrics, params, and artifacts.
- Consider early stopping for iterative training when validation loss can be monitored.

### Testing and Model Quality

- Add `pytest` tests for output shape and prediction type.
- Add checks to avoid NaN or Inf values in training outputs.
- Include a simple baseline comparison when feasible.
- Consider drift checks between training and validation distributions.

### Logging and Observability

- Use `logging` instead of print statements.
- Include meaningful context for progress, warnings, and failures.

## Examples

```python
import random
import numpy as np


def set_seed(seed: int = 42) -> None:
    """Set all reproducibility seeds used by the training pipeline."""
    random.seed(seed)
    np.random.seed(seed)
```
