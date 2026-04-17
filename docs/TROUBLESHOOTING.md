# Troubleshooting Guide

## Common Issues & Solutions

### Docker Build Fails

**Error**: `Docker daemon is not running`

```bash
# Solution: Start Docker
docker-compose up -d
# or
open -a Docker  # macOS
```

**Error**: `No space left on device`

```bash
# Solution: Clean Docker
docker system prune -a --volumes
```

### Database Connection Errors

**Error**: `postgresql://... - connection refused`

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# If not running, start it
docker-compose up -d postgres

# Verify connection
psql postgresql://postgres:postgres@localhost:5432/automotive
```

**Error**: `relation "build_jobs" does not exist`

```bash
# Initialize database schema
python scripts/init_db.py
```

### Image Build Fails

**Error**: `Base image not found`

Make sure base image exists in your environment:

```bash
# For Linux images
docker pull ubuntu:22.04

# For Windows images
docker pull mcr.microsoft.com/windows/servercore:ltsc2022
```

### API Connection Issues

**Error**: `Connection refused to localhost:8080`

```bash
# Make sure API service is running
docker-compose ps api

# Check logs
docker-compose logs api

# Alternatively, run directly
python -m agent.api
```

### Kubernetes Deployment Issues

**Error**: `Unable to connect to Kubernetes cluster`

```bash
# Check kubeconfig
kubectl config current-context

# Verify connection
kubectl cluster-info

# Or use local cluster
minikube start
```

**Error**: `ImagePullBackOff`

```bash
# Check image is pushed to registry
docker images

# Verify registry credentials
kubectl get secrets -n automotive-tools

# Check pod events
kubectl describe pod <pod-name> -n automotive-tools
```

### Argo CD Sync Issues

**Error**: `Application in OutOfSync state`

```bash
# Check Argo CD application status
argocd app get automotive-trace32

# Force sync
argocd app sync automotive-trace32 --force

# Check Argo CD logs
kubectl logs -n argocd deployment/argocd-application-controller
```

## Performance Issues

### Slow Builds

```bash
# Use Docker BuildKit for faster builds
export DOCKER_BUILDKIT=1

# Use layer caching effectively
# - Put expensive operations later in Dockerfile
# - Split layers to maximize cache hits
```

### High Memory Usage

```bash
# Limit Docker memory
docker system prune
docker image prune -a

# Check container memory
docker stats

# Increase Docker memory limit in settings
```

## Logs & Debugging

### View Application Logs

```bash
# Docker Compose
docker-compose logs -f api
docker-compose logs -f orchestrator

# Kubernetes
kubectl logs -f deployment/automotive-trace32 -n automotive-tools

# Database queries
psql postgresql://postgres:postgres@localhost:5432/automotive
\dt  # List tables
SELECT * FROM build_jobs;
```

### Enable Debug Logging

```bash
# Set environment variable
export LOG_LEVEL=DEBUG

# In docker-compose.yml
environment:
  LOG_LEVEL: DEBUG
```

### Test LLM Integration

```bash
# Test Claude connection
python -c "from agent.llm_interface import LLMInterface; \
    llm = LLMInterface(provider='anthropic'); \
    print(llm._call_llm('Hello'))"

# Test OpenAI connection
python -c "from agent.llm_interface import LLMInterface; \
    llm = LLMInterface(provider='openai'); \
    print(llm._call_llm('Hello'))"
```

## Cleanup

### Reset Everything

```bash
# Stop all services
docker-compose down

# Remove volumes (CAREFUL: deletes data)
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Clean Docker system
docker system prune -a --volumes

# Restart clean
docker-compose up -d
python scripts/init_db.py
```

## Getting Help

1. Check logs: `docker-compose logs <service>`
2. Verify configuration: `config/environments/<env>.yaml`
3. Test connectivity: `docker ps`, `kubectl get pods`
4. Review error messages carefully
5. Check GitHub issues for similar problems
6. Open an issue with:
   - OS and versions
   - Command/logs that failed
   - Configuration used
   - Expected vs actual behavior
