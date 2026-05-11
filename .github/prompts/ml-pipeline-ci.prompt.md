# ML Training Pipeline (CI/CD)

Generate a GitHub Actions workflow for an ML training pipeline following these
requirements:

1. **Triggers**:
   - `workflow_dispatch` with `dataset_version` and `model_config` inputs
   - Optional: scheduled weekly retraining on a cron expression

2. **Jobs** (in dependency order):
   - `train`: Run training script, log to MLflow, export model artifact
   - `validate`: Check metrics against baseline thresholds; fail if below
   - `register`: Push model to registry if validation passes
   - `deploy` (manual approval gate): Deploy to staging environment

3. **Quality gates**:
   - Fail training if any metric is worse than the registered baseline by more than 5%
   - Run inference on a golden test set; assert output schema is unchanged

4. **Artifact management**:
   - Cache pip dependencies and model artifacts between jobs with `actions/cache`
   - Archive evaluation report and model card as workflow artifacts on every run

5. **Best practices**:
   - Pin all action versions to a semver tag; never use `@main` or `@latest`
   - Use `OIDC` for cloud credentials where possible; avoid static access keys

Reference standards: #file:.github/copilot-instructions.md
Reference pipeline rules: #file:.github/instructions/mlops-pipelines.instructions.md
