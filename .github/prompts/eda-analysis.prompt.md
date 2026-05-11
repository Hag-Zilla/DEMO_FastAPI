# EDA Analysis

Perform exploratory data analysis on the provided dataset following these requirements:

1. **Data profiling**:
   - Shape, dtypes, null counts, and duplicate row count
   - Univariate statistics for all numeric columns (mean, std, quartiles, skewness)
   - Value counts for categorical columns (top 10 values)

2. **Visualizations** (save all figures to `figures/`):
   - Distribution plots for all numeric features
   - Correlation heatmap
   - Target variable distribution and class balance (if classification)
   - Top feature vs target relationships (top 10 by correlation or mutual information)

3. **Quality assessment**:
   - Flag columns with null rate > 1%
   - Flag columns with near-zero variance
   - Flag potential target leakage candidates

4. **Conclusions**:
   - Summarize key findings in a markdown cell
   - List recommended preprocessing steps
   - List features to investigate further or drop

Reference standards: #file:.github/copilot-instructions.md
Reference EDA rules: #file:.github/instructions/eda.instructions.md
