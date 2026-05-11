# Scenario: Code Review Request

## Prompt

Review this FastAPI module and tell me if it is good.

## Expected Behavior

- Prioritizes findings over summary
- Orders findings by severity
- References concrete risks, regressions, or test gaps
- Notes if no findings are detected and states residual risk

## Must Include

- Actionable findings format
- Brief follow-up questions only if needed

## Must Avoid

- Purely stylistic feedback without risk relevance
- Long generic summary before findings
