---
applyTo: "notebooks/**/*.ipynb,src/**/eda/**/*.py,src/**/*eda*.py,src/**/*analysis*.py"
---

## Purpose

Guide Copilot for exploratory data analysis code: loading, profiling, visualization,
and statistical interpretation with reproducible and communicable patterns.

## Guidelines

### Data Loading and Inspection

- Load data once and cache; avoid repeated disk reads within the same analysis.
- Call `df.info()`, `df.describe()`, and `df.isnull().sum()` immediately after loading.
- Assert expected column names and dtypes at the entry point.
- Document data provenance (source, date, version) in a markdown cell.

### Visualization

- Prefer `seaborn` or `plotly.express` over raw `matplotlib` for statistical plots.
- Always label axes, add a title, and include units where applicable.
- Save figures to a `figures/` directory with `fig.savefig()`; do not rely solely on
  inline display.
- Use consistent color palettes across related plots in the same notebook.

### Statistical Analysis

- Report distributions before means; check skewness and outliers first.
- Use non-parametric tests (Mann-Whitney, Spearman) when normality is not confirmed.
- Report confidence intervals alongside p-values; never report p-values alone.
- Record hypotheses and conclusions in markdown cells, not inline code comments.

### Feature Analysis

- Compute pairwise correlations; flag features with `|r| > 0.9` as redundancy
  candidates.
- Assess target leakage risk for each feature before any model training.
- Use SHAP values for model-agnostic feature importance in production-grade analysis.

## Examples

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def load_and_inspect(path: str) -> pd.DataFrame:
    """Load a dataset and print a concise quality report.

    Args:
        path: Path to a CSV or Parquet file.

    Returns:
        Loaded DataFrame.
    """
    df = pd.read_parquet(path) if path.endswith(".parquet") else pd.read_csv(path)
    print(f"Shape: {df.shape}")
    nulls = df.isnull().sum()
    if nulls.any():
        print(f"Nulls:\n{nulls[nulls > 0]}")
    return df


def plot_distribution(df: pd.DataFrame, column: str, out_dir: str = "figures") -> None:
    """Plot and save a histogram with KDE for a numeric column.

    Args:
        df: Source DataFrame.
        column: Column name to visualize.
        out_dir: Directory to save the figure.
    """
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.histplot(df[column].dropna(), kde=True, ax=ax)
    ax.set_title(f"Distribution of {column}")
    ax.set_xlabel(column)
    fig.tight_layout()
    fig.savefig(f"{out_dir}/{column}_distribution.png", dpi=150)
    plt.close(fig)
```
