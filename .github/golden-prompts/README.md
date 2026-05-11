# Golden Prompts

This folder contains baseline prompt scenarios used to validate Copilot behavior over time.

## Goal

Detect behavior drift when instruction files change.

## How To Use

1. Open Copilot Chat in the repository workspace
2. Copy one scenario prompt from this folder
3. Submit the prompt without extra context
4. Compare Copilot output with expected behavior in the scenario file
5. Record pass or fail in your PR notes
6. Use the shared scorecard for consistent grading

## Evaluation Rule

Treat each scenario as a behavior contract:

- If required items are missing, mark fail
- If prohibited items appear, mark fail
- If tone or structure deviates significantly, mark warning

Use these supporting files:

- [SCORECARD.md](SCORECARD.md)
- [report-template.md](report-template.md)

## Scenarios

- [adversarial-ambiguous.scenario.md](adversarial-ambiguous.scenario.md)
- [code-review-request.scenario.md](code-review-request.scenario.md)
- [data-engineering.scenario.md](data-engineering.scenario.md)
- [data-validation.scenario.md](data-validation.scenario.md)
- [eda-analysis.scenario.md](eda-analysis.scenario.md)
- [environments-config.scenario.md](environments-config.scenario.md)
- [experiment-tracking.scenario.md](experiment-tracking.scenario.md)
- [fastapi-endpoint.scenario.md](fastapi-endpoint.scenario.md)
- [ml-training-function.scenario.md](ml-training-function.scenario.md)
- [mlops-pipeline.scenario.md](mlops-pipeline.scenario.md)
- [observability.scenario.md](observability.scenario.md)
- [security-sensitive-request.scenario.md](security-sensitive-request.scenario.md)
