# Agentic AI Docker Container Management System

## Overview

This is a comprehensive platform for building, deploying, and managing scalable Docker containers using an intelligent agent system. Designed for Automotive development tools like **Trace32 (Lauterbach)** and **CANoe (Vector)**, with extensibility for other tools.

### Key Features

✅ **Agentic AI Orchestration** - LLM-powered agent for intelligent container management  
✅ **Generic Dockerfile Architecture** - Configuration-driven Dockerfiles using Jinja2 templates  
✅ **Multi-Platform Support** - Windows and Linux Docker images  
✅ **Kubernetes Native** - Full K8s integration with scaling policies  
✅ **Argo CD GitOps** - Declarative deployment automation  
✅ **State Tracking** - Argo DB + PostgreSQL for build/deployment history  
✅ **Template-Based** - Scalable approach for multiple automotive tools  
✅ **No Reconfiguration** - Deploy images across machines without setup  

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Agentic AI Orchestrator                    │
│  (Decision engine for container build & deployment)         │
└────────────────┬────────────────────────────────────────────┘
                 │
    ┌────────────┼────────────┬──────────────────┐
    │            │            │                  │
    ▼            ▼            ▼                  ▼
┌──────────┐ ┌──────────┐ ┌──────────┐    ┌───────────────┐
│ Builders │ │Kubernetes│ │ Argo CD  │    │ Argo DB/Pg   │
│  Engine  │ │ Manifests│ │  GitOps  │    │    (State)    │
└────┬─────┘ └────┬─────┘ └────┬─────┘    └───────────────┘
     │            │            │
     └────────────┼────────────┘
                  │
        ┌─────────▼─────────┐
        │   Docker Images   │
        │ (Win/Linux Ready) │
        └───────────────────┘
```

## Quick Start

### 1. Prerequisites
```bash
# Install required tools
brew install python@3.11 docker kubernetes-cli postgresql

# Clone and setup
cd Containerization
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python scripts/init_db.py --type postgres
```

### 3. Build First Image
```bash
python -m agent.orchestrator \
  --action build \
  --tool trace32 \
  --os windows \
  --version latest \
  --output my-trace32-image
```

### 4. Deploy to Kubernetes
```bash
python scripts/deploy.py \
  --image my-trace32-image:latest \
  --replicas 3 \
  --env production
```

## Project Structure

```
Containerization/
├── agent/                          # AI orchestration engine
│   ├── orchestrator.py            # Main agent logic
│   ├── llm_interface.py           # LLM integration (OpenAI/Claude)
│   └── state_manager.py           # Build/deploy state management
├── builders/                       # Docker image builders
│   ├── dockerfile_generator.py    # Dynamic Dockerfile creation
│   ├── image_builder.py           # Build orchestration
│   └── templates/                 # Base Docker templates
│       ├── trace32.dockerfile
│       └── automotive-base.dockerfile
├── kubernetes/                     # K8s manifests
│   ├── deployment.yaml            # Pod deployments
│   ├── service.yaml               # Service definitions
│   ├── configmap.yaml             # App configuration
│   └── statefulset.yaml           # Stateful components
├── argo-cd/                        # GitOps automation
│   ├── application.yaml           # Argo CD Application CRD
│   ├── sync-policy.yaml           # Auto-sync rules
│   └── repo-creds.yaml            # Repository credentials
├── database/                       # Data persistence
│   ├── schema.sql                 # Database schema
│   ├── migrations/                # Schema migrations
│   └── init_data.sql              # Seed data
├── config/                         # Configuration files
│   ├── tools/                     # Tool-specific configs
│   │   ├── trace32.yaml
│   │   └── generic_tool.yaml
│   └── environments/              # Env-specific configs
│       ├── dev.yaml
│       ├── staging.yaml
│       └── production.yaml
├── templates/                      # Template library
│   ├── dockerfile_templates/
│   └── k8s_templates/
├── scripts/                        # Utility scripts
│   ├── init_db.py                 # Database initialization
│   ├── deploy.py                  # Deployment script
│   └── cleanup.py                 # Resource cleanup
├── tests/                          # Test suite
├── requirements.txt                # Python dependencies
└── setup.py                        # Installation config
```

## Supported Tools

### Trace32 (Lauterbach)
- Professional debugging tool for automotive development
- Pre-configured template with Windows/Linux variants
- Automatic license injection support
- Real-time debug session management

### Generic Tool Support
- Template-based configuration
- Environment variable injection
- Volume mount management
- Network policy definition

## Database Schema

The system uses **PostgreSQL + Argo DB** for state management:

- **build_jobs**: Track container builds
- **deployments**: Deployment history
- **tool_configs**: Tool-specific configurations
- **image_registry**: Built image metadata
- **sync_logs**: Argo CD synchronization logs

## Deployment Scenarios

### Single Machine Development
```bash
# Build and run locally
python -m agent.orchestrator --local --tool trace32
```

### Multi-Server Production
```bash
# Deploy across Kubernetes cluster
python scripts/deploy.py --cluster prod-cluster --replicas 5
```

### Cross-Machine Deployment (No Reconfiguration)
```bash
# Image already has all configs baked in
docker run <registry>/automotive-trace32:latest
# Ready to use - no setup needed!
```

## API Endpoints

The agent system exposes REST APIs for integration:

- `POST /api/builds` - Create new build job
- `GET /api/builds/{id}` - Get build status
- `POST /api/deployments` - Deploy to Kubernetes
- `GET /api/deployments/{id}` - Get deployment status
- `GET /api/images` - List available images

## Configuration

### Tool Configuration
Edit `config/tools/trace32.yaml`:
```yaml
name: trace32
os_support:
  - windows
  - linux
docker:
  base_image: "windows:ltsc2022"
  version: "latest"
resources:
  cpu: "2"
  memory: "4Gi"
volumes:
  - /opt/trace32:/app/trace32
```

### Environment Configuration
Edit `config/environments/production.yaml`:
```yaml
kubernetes:
  cluster: "prod-cluster"
  namespace: "automotive-tools"
  replicas: 3
registry:
  endpoint: "private-registry.company.com"
  auth: enabled
database:
  url: "postgresql://prod-db:5432/automotive"
```

## Contributing

1. Create tool templates in `builders/templates/`
2. Add tool config in `config/tools/`
3. Write tests in `tests/`
4. Submit PR with documentation

## Support

For issues related to specific tools (Trace32, etc.), check `docs/tools/` directory.

## License

Proprietary - Automotive Development Team

## Next Steps

1. ✅ Set up PostgreSQL database
2. ✅ Configure Kubernetes cluster
3. ✅ Deploy Argo CD
4. ✅ Build first Trace32 image
5. ⏳ Scale to additional tools

---

**Start Building:** `python -m agent.orchestrator --help`
