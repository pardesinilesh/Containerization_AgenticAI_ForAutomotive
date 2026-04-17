# Architecture & Design

## System Architecture

The Agentic AI Containerization Platform employs a modular architecture combining LLM-based decision making with container orchestration:

```
┌──────────────────────────────────────────────────────────────────┐
│                   REST API / CLI Interface                        │
│              (FastAPI + Click CLI)                               │
└────────────────────┬─────────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────────┐
│              Agentic Orchestrator                                 │
│  - RECEIVES build/deploy requests                                │
│  - GENERATES intelligent plans using LLM                         │
│  - EXECUTES build/deploy workflows                               │
│  - TRACKS state in PostgreSQL                                    │
└────────────────────┬─────────────────────────────────────────────┘
                     │
     ┌───────────────┼───────────────┬──────────────────┐
     │               │               │                  │
     ▼               ▼               ▼                  ▼
┌─────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Dockerfile  │ │ Kubernetes   │ │   Argo CD    │ │  Argo DB +   │
│ Generator   │ │  Manifests   │ │   GitOps     │ │  PostgreSQL  │
│ (Templated) │ │  (Templated) │ │  (Automated) │ │  (State)     │
└────┬────────┘ └──────┬───────┘ └──────┬───────┘ └──────────────┘
     │                 │                │
     └─────────────────┼────────────────┘
                       │
    ┌──────────────────▼──────────────────┐
    │      Docker Registry                 │
    │  (Container Images)                  │
    └──────────────────────────────────────┘
```

## Component Descriptions

### 1. Agentic Orchestrator (`agent/orchestrator.py`)
**Purpose**: Central decision-making engine
- Receives build/deploy requests
- Uses LLM to generate intelligent build/deploy plans
- Orchestrates Dockerfile generation and container builds
- Manages Kubernetes deployments
- Tracks all state changes

### 2. LLM Interface (`agent/llm_interface.py`)
**Purpose**: LLM-powered intelligence
- Generates optimized build plans
- Creates deployment manifests
- Suggests configuration optimizations
- Supports multiple providers (OpenAI, Claude)

### 3. State Manager (`agent/state_manager.py`)
**Purpose**: Persistent state and audit trail
- Tracks build jobs (status, image ID, errors)
- Tracks deployments (replicas, environment, status)
- Stores image metadata
- Enables rollback to previous configurations

### 4. Dockerfile Generator (`builders/dockerfile_generator.py`)
**Purpose**: Intelligent Dockerfile creation
- Loads templates for known tools (Trace32)
- Generates Dockerfiles from plans
- Validates Dockerfile syntax
- Supports multi-stage builds for optimization

### 5. Image Builder (`builders/image_builder.py`)
**Purpose**: Container image building & pushing
- Builds Docker images from Dockerfiles
- Pushes to registries
- Manages local/registry image lifecycle
- Falls back to CLI when SDK unavailable

## Data Flow

### Build Workflow
```
User Request
    │
    ▼
REST API / CLI
    │
    ▼
Orchestrator.build_image()
    ├─> LLM generates build plan
    │
    ├─> StateManager creates build job
    │
    ├─> DockerfileGenerator creates Dockerfile
    │
    ├─> ImageBuilder builds image
    │
    ├─> ImageBuilder pushes to registry (optional)
    │
    └─> StateManager updates job status
         │
         ▼
       Return to user
```

### Deploy Workflow
```
User Request
    │
    ▼
REST API / CLI
    │
    ▼
Orchestrator.deploy_image()
    ├─> LLM generates K8s manifest
    │
    ├─> StateManager creates deployment job
    │
    ├─> Apply manifest to Kubernetes
    │       ├─> Argo CD watches repo
    │       ├─> Auto-syncs on changes
    │       └─> Manages rollouts
    │
    └─> StateManager updates deployment status
         │
         ▼
       Return to user
```

## Scalability Design

### Multi-Tool Support
- **Template-based approach**: Each tool has a configuration in `config/tools/`
- **Generic tool fallback**: Unknown tools use generic template
- **Easy extension**: Add new tool by creating config + optional template

### Kubernetes Scaling
- **Horizontal**: Increase replicas via `replicas` parameter
- **Vertical**: Adjust resource requests/limits in manifests
- **Auto-scaling**: Kubernetes HPA can be configured per deployment

### Database Scaling
- **Read replicas**: PostgreSQL supports read replication
- **Connection pooling**: SQLAlchemy manages connection pools
- **Sharding**: Future - split builds by tool/environment

## Security Considerations

### Image Security
- Base images from trusted registries (MCR, Ubuntu Official)
- Minimal attack surface (remove unnecessary packages)
- Security scanning in CI/CD pipeline

### Kubernetes Security
- RBAC restricts orchestrator permissions
- Network policies limit pod-to-pod communication
- Secrets management for registry credentials
- TLS for all external communication

### Database Security
- Encrypted connections (SSL/TLS)
- Role-based access control
- Audit logging of state changes
- No credentials in code (environment variables)

## LLM Integration

### LLM Model Options
1. **Claude (Recommended)**
   - Superior long-context understanding
   - Better cost efficiency for complex tasks
   - Excellent for configuration optimization

2. **GPT-4/3.5**
   - Strong general performance
   - Well-documented API
   - Real-time updates

### LLM Tasks
1. **Build Plan Generation**: LLM analyzes tool requirements and generates optimized build steps
2. **Manifest Generation**: Creates Kubernetes manifests with proper resource specs
3. **Optimization Suggestions**: Recommends improvements to dockerfile/k8s configs

## Performance Optimization

### Build Optimization
- Multi-stage Dockerfiles to reduce image size
- Layer caching for faster rebuilds
- Parallel dependency installation

### Deployment Optimization
- Rolling updates to prevent downtime
- Resource limits prevent resource exhaustion
- Health checks enable fast failure detection

## Monitoring & Observability

### Metrics Tracked
- Build success/failure rates
- Build duration
- Image sizes
- Deployment duration
- Pod resource usage

### Audit Trail
- All builds logged to database
- All deployments tracked with timestamps
- Error messages stored for debugging
- Metadata available for cost analysis

---

For implementation details, see component-specific documentation in docs/
