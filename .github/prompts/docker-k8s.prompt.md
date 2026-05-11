# Docker & Kubernetes Best Practices

Generate Docker and Kubernetes manifests following these practices:

## Docker

1. **Multi-stage builds** to minimize image size:

   ```dockerfile
   FROM python:3.11 as builder
   # Install dependencies
   FROM python:3.11
   # Copy from builder
   ```

2. **Security**:
   - Use non-root user: `USER appuser`
   - Minimal base image (python:3.11-slim)
   - Pin package versions in requirements.txt

3. **Health checks**:

   ```dockerfile
   HEALTHCHECK --interval=30s CMD python /app/health_check.py
   ```

## Kubernetes

1. **Resource requests/limits**:

   ```yaml
   resources:
     requests:
       cpu: 100m
       memory: 256Mi
     limits:
       cpu: 500m
       memory: 512Mi
   ```

2. **Probes** (readiness + liveness):

   ```yaml
   livenessProbe:
     httpGet:
       path: /health
       port: 8000
     initialDelaySeconds: 10
   readinessProbe:
     httpGet:
       path: /ready
       port: 8000
     initialDelaySeconds: 5
   ```

3. **Rolling updates**:

   ```yaml
   strategy:
     type: RollingUpdate
     rollingUpdate:
       maxSurge: 1
       maxUnavailable: 0
   ```

4. **Environment & ConfigMap**:

   ```yaml
   envFrom:
     - configMapRef:
         name: app-config
   ```

5. **Secrets management**:
   - Use Kubernetes `Secret` for sensitive values; never put secrets in `ConfigMap`.
   - Reference secrets via `envFrom.secretRef` or mounted volumes, not inline `env`.
   - Prefer `external-secrets` operator with a vault backend in production.

   ```yaml
   envFrom:
     - secretRef:
         name: app-secrets
   ```

6. **Multi-environment pattern**:
   - Use Kustomize overlays (`base/`, `overlays/dev/`, `overlays/prod/`) or Helm
     values files to separate environment-specific config.
   - Never duplicate manifests across environments; patch only what differs.

Reference standards: #file:.github/copilot-instructions.md
Reference environment rules: #file:.github/instructions/environments.instructions.md
