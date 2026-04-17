# Quick Start Guide

## Prerequisites

- Docker Desktop with WSL2 (for Windows) or Docker on macOS/Linux
- Python 3.10+
- PostgreSQL 14+ (or use docker-compose)
- Kubernetes cluster (kubectl configured)
- Git

## Local Development Setup

### 1. Clone and Setup

```bash
git clone <repo-url>
cd Containerization
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Start Services with Docker Compose

```bash
# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api
```

### 3. Initialize Database

```bash
python scripts/init_db.py
```

## Build Your First Image

### Via CLI

```bash
# Build Trace32 for Windows
python -m agent.cli build --tool trace32 --os windows

# Build Trace32 for Linux
python -m agent.cli build --tool trace32 --os linux

# View build status
python -m agent.cli status

# List all built images
python -m agent.cli images
```

### Via REST API

```bash
# Create build job
curl -X POST http://localhost:8080/api/builds \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "trace32",
    "os": "windows",
    "version": "latest"
  }'

# Get build status
curl http://localhost:8080/api/builds/<build-id>

# List images
curl http://localhost:8080/api/images
```

## Deploy to Kubernetes

### 1. Setup Argo CD

```bash
# Install Argo CD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Access Argo CD UI
kubectl -n argocd port-forward svc/argocd-server -:443
```

### 2. Deploy Image

```bash
# Via CLI
python -m agent.cli deploy --image automotive-trace32:latest --env production

# Via API
curl -X POST http://localhost:8080/api/deployments \
  -H "Content-Type: application/json" \
  -d '{
    "image_id": "automotive-trace32:latest",
    "replicas": 3,
    "env": "production"
  }'
```

### 3. Monitor Deployment

```bash
# Check Argo CD application
argocd app get automotive-trace32

# Check Kubernetes resources
kubectl get pods -n automotive-tools
kubectl get services -n automotive-tools

# View logs
kubectl logs -n automotive-tools <pod-name>
```

## Configuration

### Tool Configuration

Edit `config/tools/trace32.yaml` to customize:
- Base images
- Resource limits
- Ports and volumes
- Environment variables
- Dependencies

### Environment Configuration

Edit `config/environments/<env>.yaml`:
- Kubernetes cluster settings
- Registry endpoints
- Database configuration
- Feature flags

## Running Tests

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_orchestrator.py

# With coverage
pytest --cov=agent --cov=builders tests/
```

## Troubleshooting

### Docker Build Fails

```bash
# Check Docker daemon
docker ps

# Check image build logs
docker-compose logs orchestrator

# Manual build for debugging
cd templates
docker build -t trace32-test -f trace32_linux.dockerfile .
```

### Database Connection Error

```bash
# Check PostgreSQL
docker-compose logs postgres

# Reinitialize database
python scripts/init_db.py

# Check connection manually
psql postgresql://postgres:postgres@localhost:5432/automotive
```

### Kubernetes Deployment Issues

```bash
# Check pod status
kubectl describe pod <pod-name> -n automotive-tools

# Check events
kubectl get events -n automotive-tools

# Check Argo CD sync status
argocd app get automotive-trace32 --refresh
```

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│        Agentic AI Orchestrator                   │
│  - LLM-powered decision making                   │
│  - State management with PostgreSQL              │
│  - Container image generation                    │
└────────────┬────────────────────────────────────┘
             │
  ┌──────────┼──────────┬──────────────┐
  │          │          │              │
  ▼          ▼          ▼              ▼
Docker   Kubernetes  Argo CD      Registry
Images   Manifests   GitOps       (Images)
```

## Next Steps

1. Customize `config/tools/` for your tools
2. Set up production Kubernetes cluster
3. Configure container registry
4. Deploy first image to production
5. Monitor with Argo CD

---

For detailed documentation, see:
- [Agent Framework](docs/AGENT.md)
- [API Reference](docs/API.md)
- [Kubernetes Guide](docs/KUBERNETES.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
