# Scenario: ML Training Function

## Prompt

Write a Python training function for binary classification and include model evaluation.
I need reproducible training, metrics logging, and minimal tests.

## Expected Behavior

- Mentions reproducibility via random seed setup
- Encourages or includes cross-validation
- Includes at least one metric such as accuracy or F1
- Suggests logging best practices
- Provides a minimal `pytest` test example

## Must Include

- Type hints
- Function docstring
- Clear train and validation evaluation step

## Must Avoid

- `print`-only observability recommendations
- Missing validation/test guidance
- Unexplained magic numbers for hyperparameters
