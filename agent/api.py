"""
REST API for container orchestration.
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import asyncio
import logging
from agent.orchestrator import ContainerOrchestrator
from agent.state_manager import StateManager

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Automotive Container Orchestrator API",
    description="Agentic AI system for building and deploying containers",
    version="0.1.0",
)

orchestrator = ContainerOrchestrator()
state_manager = StateManager()


# Models
class BuildRequest(BaseModel):
    tool: str
    os: str = "windows"
    version: str = "latest"
    registry: str = None
    output_name: str = None


class DeployRequest(BaseModel):
    image_id: str
    replicas: int = 3
    env: str = "production"
    namespace: str = "automotive-tools"


class BuildResponse(BaseModel):
    build_id: str
    tool: str
    os: str
    version: str
    status: str


class ImageListResponse(BaseModel):
    count: int
    images: list


# Health check
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "container-orchestrator"}


@app.get("/ready")
async def ready():
    """Readiness check endpoint."""
    try:
        state_manager.init_db()
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


# Build endpoints
@app.post("/api/builds", response_model=dict)
async def create_build(request: BuildRequest, background_tasks: BackgroundTasks):
    """Create a new build job."""
    try:
        build_id = state_manager.create_build_job(
            tool=request.tool,
            os=request.os,
            version=request.version,
            status="queued",
        )

        # Schedule build in background
        background_tasks.add_task(
            orchestrator.build_image,
            tool=request.tool,
            os=request.os,
            version=request.version,
            registry=request.registry,
            output_name=request.output_name,
        )

        return {
            "build_id": build_id,
            "status": "queued",
            "message": "Build job created and queued for processing",
        }
    except Exception as e:
        logger.error(f"Build creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/builds/{build_id}")
async def get_build(build_id: str):
    """Get build status."""
    result = state_manager.get_build_job(build_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail="Build not found")
    return result


@app.get("/api/builds")
async def list_builds():
    """List all builds."""
    return state_manager.get_all_builds()


# Deployment endpoints
@app.post("/api/deployments", response_model=dict)
async def create_deployment(request: DeployRequest, background_tasks: BackgroundTasks):
    """Create a new deployment."""
    try:
        deployment_id = state_manager.create_deployment(
            image_id=request.image_id,
            env=request.env,
            replicas=request.replicas,
            status="pending",
        )

        # Schedule deployment in background
        background_tasks.add_task(
            orchestrator.deploy_image,
            image_id=request.image_id,
            replicas=request.replicas,
            env=request.env,
            namespace=request.namespace,
        )

        return {
            "deployment_id": deployment_id,
            "status": "pending",
            "message": "Deployment created and queued",
        }
    except Exception as e:
        logger.error(f"Deployment creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/deployments/{deployment_id}")
async def get_deployment(deployment_id: str):
    """Get deployment status."""
    result = state_manager.get_deployment(deployment_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return result


# Image endpoints
@app.get("/api/images", response_model=ImageListResponse)
async def list_images():
    """List available images."""
    result = state_manager.get_all_images()
    return ImageListResponse(
        count=result["count"],
        images=result["images"],
    )


# Utilities
@app.post("/api/cleanup")
async def cleanup(resource_type: str, resource_id: str):
    """Clean up resources."""
    try:
        result = await orchestrator.cleanup(resource_type, resource_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
    )
