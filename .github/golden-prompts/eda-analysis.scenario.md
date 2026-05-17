# Scenario: EDA on a Classification Dataset

## Prompt

Perform exploratory data analysis on a customer churn dataset with 50k rows.
Include profiling, distribution plots, a correlation heatmap, and a summary of
preprocessing recommendations.

## Expected Behavior

- Calls `df.info()`, `df.describe()`, and `df.isnull().sum()` at the start
- Uses `seaborn` or `plotly.express` for visualizations, not raw matplotlib
- Labels all axes and adds a title to every plot
- Saves figures to a `figures/` directory
- Flags columns with null rate above 1% or near-zero variance
- Concludes with a markdown cell summarizing findings and recommended steps

## Must Include

- Profiling section (shape, nulls, dtypes, duplicates)
- At least one distribution plot and one correlation heatmap
- Markdown summary cell with actionable preprocessing recommendations

## Must Avoid

- Hardcoded absolute file paths
- Visualizations without axis labels or titles
- Skipping null or duplicate checks
- Reporting only p-values without confidence intervals for statistical tests
