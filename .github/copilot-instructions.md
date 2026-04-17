# Agentic AI Containerization Platform

This workspace contains an intelligent agent system for building and deploying scalable Docker containers in Kubernetes environments, designed for Automotive development tools like Trace32 (Lauterbach) and CANoe (Vector).

## Project Overview
- **Core Framework**: Python-based agentic orchestration with LLM capabilities
- **Container Support**: Windows and Linux Docker images
- **Deployment**: Argo CD + Kubernetes with GitOps
- **State Management**: Argo DB + PostgreSQL
- **Scalability**: Template-based approach for multiple automotive tools

## Architecture Components
1. **Agent Framework** (`agent/`) - Orchestration engine with LLM integration
2. **Container Builders** (`builders/`) - Dynamic Dockerfile generators
3. **Kubernetes Manifests** (`kubernetes/`) - Deployment configs
4. **Argo CD** (`argo-cd/`) - GitOps deployment automation
5. **Database** (`database/`) - Argo DB + PostgreSQL schemas
6. **Templates** (`templates/`) - Reusable Dockerfile templates (Trace32, CANoe, etc.)
7. **Configuration** (`config/`) - Environment and tool configs for all supported tools

## Development Setup

### Prerequisites
- Python 3.10+
- Docker & Docker Desktop
- Kubernetes (minikube/kind for local dev)
- Argo CD CLI
- PostgreSQL 14+

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Set up local environment
python setup.py develop

# Initialize database
python scripts/init_db.py
```

## Usage

### Building a Docker Image
```bash
# Build Trace32 (Lauterbach) container
python -m agent.orchestrator --action build --tool trace32 --target windows

# Build CANoe (Vector) container
python -m agent.orchestrator --action build --tool canoe --target linux

# View build status
python -m agent.cli status --build-id <build-id>
```

### Deploying with Argo CD
```bash
# Deploy Trace32
python scripts/deploy.py --tool trace32 --env production

# Deploy CANoe
python scripts/deploy.py --tool canoe --env production

# Monitor deployments
argocd app get automotive-trace32
argocd app get automotive-canoe
```

## Supported Tools
- **Trace32 (Lauterbach)** - Professional debugging and trace tool
- **CANoe (Vector)** - CAN network analysis and simulation tool

## File Structure
- `agent/orchestrator.py` - Main agent orchestration engine
- `builders/dockerfile_generator.py` - Dynamic Dockerfile generation
- `builders/templates/` - Base Docker templates (trace32_*, canoe_*)
- `config/tools/` - Tool-specific configurations (trace32.yaml, canoe.yaml)
- `kubernetes/` - K8s manifests (Deployments, Services, ConfigMaps)
- `argo-cd/` - Argo CD applications and sync policies
- `database/` - Database schemas and migrations
- `config/` - Configuration files for tools and environments
- `tests/` - Unit and integration tests

## Next Steps
1. Configure tool templates in `config/tools/`
2. Set up PostgreSQL and Argo DB
3. Deploy Kubernetes cluster
4. Initialize Argo CD
5. Build first Docker image
