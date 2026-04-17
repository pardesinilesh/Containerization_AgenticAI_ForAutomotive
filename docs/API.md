# API Reference

## REST API Endpoints

### Base URL
```
http://localhost:8080/api
```

### Authentication
Currently no authentication. In production, add API key or OAuth2.

## Endpoints

### Health Check

#### GET /health
Returns service health status.

**Response**:
```json
{
  "status": "healthy",
  "service": "container-orchestrator"
}
```

#### GET /ready
Readiness probe for Kubernetes.

**Response**:
```json
{
  "status": "ready"
}
```

---

### Builds

#### POST /builds
Create a new build job.

**Request**:
```json
{
  "tool": "trace32",
  "os": "windows",
  "version": "latest",
  "registry": "registry.example.com",
  "output_name": "my-trace32-image"
}
```

**Response** (201):
```json
{
  "build_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "Build job created and queued for processing"
}
```

#### GET /builds/{build_id}
Get build status and details.

**Response** (200):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "tool": "trace32",
  "os": "windows",
  "version": "latest",
  "status": "completed",
  "image_id": "automotive-trace32:latest",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:45:00Z"
}
```

#### GET /builds
List all builds with pagination.

**Query Parameters**:
- `skip`: Number of builds to skip (default: 0)
- `limit`: Max builds to return (default: 100)
- `status`: Filter by status (pending, building, completed, failed)

**Response** (200):
```json
[
  {
    "id": "...",
    "tool": "trace32",
    "status": "completed",
    ...
  }
]
```

---

### Deployments

#### POST /deployments
Create a new deployment.

**Request**:
```json
{
  "image_id": "automotive-trace32:latest",
  "replicas": 3,
  "env": "production",
  "namespace": "automotive-tools"
}
```

**Response** (201):
```json
{
  "deployment_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "pending",
  "message": "Deployment created and queued"
}
```

#### GET /deployments/{deployment_id}
Get deployment status.

**Response** (200):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "image_id": "automotive-trace32:latest",
  "env": "production",
  "replicas": 3,
  "status": "deployed",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

---

### Images

#### GET /images
List all available built images.

**Response** (200):
```json
{
  "count": 5,
  "images": [
    {
      "image_id": "automotive-trace32:1.0.0",
      "tool": "trace32",
      "os": "windows",
      "version": "1.0.0",
      "created_at": "2024-01-15T09:00:00Z"
    },
    {
      "image_id": "automotive-trace32:linux-1.0.0",
      "tool": "trace32",
      "os": "linux",
      "version": "1.0.0",
      "created_at": "2024-01-15T09:15:00Z"
    }
  ]
}
```

---

### Cleanup

#### POST /cleanup
Remove a resource.

**Query Parameters**:
- `resource_type`: "build" or "deployment"
- `resource_id`: ID of resource to delete

**Response** (200):
```json
{
  "success": true,
  "resource_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 404 Not Found
```json
{
  "detail": "Build not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error. Check logs for details."
}
```

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200  | OK - Request successful |
| 201  | Created - Resource created |
| 400  | Bad Request - Invalid parameters |
| 404  | Not Found - Resource doesn't exist |
| 500  | Internal Error - Server error |
| 503  | Service Unavailable - Database/dependencies down |

---

## Build Status States

| Status | Meaning |
|--------|---------|
| pending | Build queued, waiting to start |
| planning | LLM generating build plan |
| dockerfile_generated | Dockerfile ready |
| building | Docker image build in progress |
| completed | Build successful, image ready |
| pushed | Image pushed to registry |
| failed | Build failed |
| deleted | Build marked for deletion |

---

## Deployment Status States

| Status | Meaning |
|--------|---------|
| pending | Deployment queued |
| manifest_ready | K8s manifest prepared |
| deploying | Applying to Kubernetes |
| deployed | Successfully deployed |
| failed | Deployment failed |
| deleted | Deployment marked for deletion |

---

## Examples

### Build Trace32 Windows Image

```bash
curl -X POST http://localhost:8080/api/builds \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "trace32",
    "os": "windows",
    "version": "1.0.0",
    "registry": "myregistry.azurecr.io"
  }'
```

### Deploy Built Image

```bash
curl -X POST http://localhost:8080/api/deployments \
  -H "Content-Type: application/json" \
  -d '{
    "image_id": "automotive-trace32:1.0.0-windows",
    "replicas": 3,
    "env": "production"
  }'
```

### Check Deployment Status

```bash
curl http://localhost:8080/api/deployments/550e8400-e29b-41d4-a716-446655440001
```

---

For client libraries and SDKs, see separate documentation.
