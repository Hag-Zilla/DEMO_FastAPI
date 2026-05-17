---
applyTo: "**/*.ipynb,notebooks/**/*.py"
---

## Purpose

Guide Copilot for Jupyter notebook code with conventions that ensure reproducibility,
clarity, and maintainability.

## Guidelines

### Cell Organization

- Structure notebooks with clear sections: Imports, Configuration, Data Loading,
  Analysis, Conclusions.
- Keep cells short and single-purpose; split complex operations across multiple cells.
- Use markdown cells for section headers and to document intent before code cells.
- The notebook must run end-to-end with "Restart and Run All" without errors.

### Reproducibility

- Set all random seeds in a dedicated early cell (`random`, `numpy`, `torch` if used).
- Pin package versions in a `requirements.txt` or at the top of the notebook.
- Avoid absolute paths; use `pathlib.Path` relative to the project root.
- Clear all outputs before committing; never commit notebooks with embedded data.

### Output Management

- Do not use `print` for large outputs; use `display()` or log to a file.
- Limit cell output to what is necessary for the analysis narrative.
- Export final visualizations to `figures/`; do not rely on notebook-embedded images.

### Code Quality

- Apply the same PEP 8 and docstring standards as `.py` files.
- Refactor reusable logic into `.py` modules; notebooks orchestrate and narrate,
  they do not implement business logic.
- Avoid deeply nested loops or conditions in cells; extract them to functions.

## Examples

```python
# Cell 1 — Imports and seeds
import random
import numpy as np
import pandas as pd
from pathlib import Path

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# Cell 2 — Configuration
DATA_PATH = Path("data/raw/dataset.parquet")
FIGURES_DIR = Path("figures")
FIGURES_DIR.mkdir(exist_ok=True)

# Cell 3 — Data loading
df = pd.read_parquet(DATA_PATH)
print(f"Loaded {len(df):,} rows, {df.shape[1]} columns")
```
