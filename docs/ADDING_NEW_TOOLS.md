# How to Add a New Automotive Tool

This guide walks through adding a new automotive tool to the platform using the generic Dockerfile architecture.

## Quick Start

Adding a new tool requires only one file: a tool configuration file.

### Example: Adding SomeNewTool

#### Step 1: Create Configuration

Create `config/tools/newtools.yaml`:

```yaml
name: newtools
display_name: "New Tools (VendorName)"
vendor: vendorname
version: "1.0.0"
description: "Description of what the tool does"

supported_os:
  - windows
  - linux

docker:
  base_images:
    windows: "mcr.microsoft.com/windows/servercore:ltsc2022"
    linux: "ubuntu:22.04"
  
  ports:
    - 5432      # Primary service port
    - 8080      # HTTP API port (optional)
  
  volumes:
    - /app/newtools/data
    - /app/newtools/config
    - /app/newtools/logs

resources:
  cpu:
    request: "1000m"
    limit: "2000m"
  memory:
    request: "2Gi"
    limit: "4Gi"

features:
  feature1: true
  feature2: true

environment_variables:
  NEWTOOLS_PORT: "5432"
  NEWTOOLS_DEBUG: "0"
  NEWTOOLS_HOME: "/app/newtools"

dependencies:
  windows:
    - git
    - visualstudio2022community
    - dotnet-sdk
  
  linux:
    - build-essential
    - git
    - python3-dev
    - curl

python_dependencies:
  - pydantic
  - fastapi
  - uvicorn

health_check:
  enabled: true
  interval: "30s"
  timeout: "10s"
  retries: 3
```

#### Step 2: Build Container

```bash
# Build Linux container
python -m agent.cli build --tool newtools --os linux

# Build Windows container
python -m agent.cli build --tool newtools --os windows

# With custom registry
python -m agent.cli build --tool newtools --os linux --registry myregistry.com
```

#### Step 3: Deploy

```bash
# Deploy to production
python scripts/deploy.py --tool newtools --env production

# Monitor deployment
argocd app get automotive-newtools
kubectl logs -f deployment/automotive-newtools -n automotive-tools
```

## Configuration Reference

### Top-Level Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Tool identifier (lowercase, no spaces) |
| `display_name` | string | Yes | Human-readable tool name |
| `vendor` | string | Yes | Tool vendor/creator |
| `version` | string | No | Tool version |
| `description` | string | No | Tool description |

### Docker Configuration

```yaml
docker:
  base_images:
    windows: "image:tag"    # Windows Server base image
    linux: "image:tag"      # Linux base image
  
  ports:
    - 5432                  # Exposed ports in container
    - 8080
  
  volumes:
    - /app/tool/data        # Mount points in container
    - /app/tool/config
```

### Resources

Kubernetes resource requests/limits:

```yaml
resources:
  cpu:
    request: "500m"         # Requested CPU
    limit: "1000m"          # Max CPU
  memory:
    request: "1Gi"          # Requested memory
    limit: "2Gi"            # Max memory
```

### Dependencies

Third-party dependencies installed in container:

```yaml
dependencies:
  windows:
    - git
    - chocolatey_package_name
  
  linux:
    - apt_package_name
    - another_package

python_dependencies:
  - pip_package_name
  - another_pip_package
```

### Health Check

Container health monitoring:

```yaml
health_check:
  enabled: true               # Enable/disable
  interval: "30s"            # Check interval
  timeout: "10s"             # Timeout per check
  retries: 3                 # Retries before unhealthy
```

## Generated Dockerfile

When you build a tool, the generic template automatically generates a Dockerfile like:

```dockerfile
FROM ubuntu:22.04

LABEL tool="newtools" \
      vendor="vendorname" \
      version="latest"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/newtools/{config,data,logs,projects}

WORKDIR /app/newtools

ENV NEWTOOLS_PORT=5432 \
    NEWTOOLS_DEBUG=0 \
    NEWTOOLS_HOME=/app/newtools

RUN pip3 install --no-cache-dir \
    pydantic \
    fastapi \
    uvicorn

# ... health check, ports, startup logic
```

## Testing Locally

Before deploying to production:

```bash
# 1. Build the image
python -m agent.cli build --tool newtools --os linux

# 2. Run locally
docker run -it automotive-newtools:latest

# 3. Test ports/health
curl http://localhost:8080/health

# 4. Check logs
docker logs <container_id>
```

## Customization

For advanced customization:

### Add Environment-Specific Config

```yaml
environment_variables:
  NEWTOOLS_LOG_LEVEL: "INFO"
  NEWTOOLS_MAX_WORKERS: "4"
```

### Add Python Scripts

Place custom Python scripts in the image:

```yaml
# In dockerfile_generator.py, after template rendering
# Add logic to copy and run custom scripts
```

### Override Template Sections

For very custom logic, you can:

1. Extend `DockerfileGenerator` class
2. Override `generate()` method
3. Call generic template but customize output

## Common Scenarios

### Scenario 1: Tool with Database

```yaml
docker:
  ports:
    - 5432      # App port
    - 5433      # DB port
  
  volumes:
    - /app/tool/data
    - /app/tool/db           # Database storage

dependencies:
  linux:
    - postgresql-client

environment_variables:
  DB_HOST: "localhost"
  DB_PORT: "5433"
```

### Scenario 2: GPU-Enabled Tool

```yaml
resources:
  gpu: "1"                    # Request 1 GPU

requirements:
  linux:
    - nvidia-docker          # NVIDIA Docker runtime
```

### Scenario 3: Multi-Service Tool

```yaml
docker:
  ports:
    - 5432      # Main service
    - 8080      # API
    - 8443      # Secure API
```

## Best Practices

1. **Start with `generic_tool.yaml`** - Copy and modify as template
2. **Keep dependencies minimal** - Reduces image size
3. **Test locally first** - Before production deployment
4. **Version your tools** - Update version field for releases
5. **Document features** - Add to features section in YAML
6. **Set resource limits** - Prevent resource exhaustion
7. **Enable health checks** - For monitoring and auto-restart

## Troubleshooting

### Container won't start
- Check logs: `docker logs <container_id>`
- Verify ports aren't in use: `lsof -i :5432`
- Check dependencies installed correctly

### Build fails
- Review YAML syntax (must be valid YAML)
- Verify base image exists: `docker pull ubuntu:22.04`
- Check tool dependencies available in repos

### Deployment fails
- Check Kubernetes resources: `kubectl describe node`
- Verify registry credentials: `kubectl get secrets`
- Review pod events: `kubectl describe pod <pod_name>`

## Next Steps

- Review working examples: [trace32.yaml](../config/tools/trace32.yaml), [canoe.yaml](../config/tools/canoe.yaml)
- Check generic templates: [generic_linux.dockerfile.j2](../builders/templates/generic_linux.dockerfile.j2)
- Test build: `python -m agent.cli build --tool trace32 --os linux`

