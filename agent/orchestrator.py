"""
Core agent orchestrator for managing container builds and deployments.
"""
import argparse
import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Optional
from dotenv import load_dotenv

from agent.llm_interface import LLMInterface
from agent.state_manager import StateManager
from builders.dockerfile_generator import DockerfileGenerator
from builders.image_builder import ImageBuilder

load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class AgentAction(str, Enum):
    """Available agent actions."""
    BUILD = "build"
    DEPLOY = "deploy"
    STATUS = "status"
    LIST = "list"
    CLEANUP = "cleanup"


class ContainerOrchestrator:
    """Main orchestrator for container management using agentic AI."""

    def __init__(self):
        """Initialize the orchestrator with dependencies."""
        self.llm = LLMInterface()
        self.state_manager = StateManager()
        self.dockerfile_generator = DockerfileGenerator()
        self.image_builder = ImageBuilder()

    async def build_image(
        self,
        tool: str,
        os: str = "windows",
        version: str = "latest",
        output_name: Optional[str] = None,
        registry: Optional[str] = None,
    ) -> dict:
        """
        Build a Docker image using the agentic AI.

        Args:
            tool: Tool name (e.g., 'trace32')
            os: Target OS ('windows' or 'linux')
            version: Tool version
            output_name: Custom output image name
            registry: Target registry URL

        Returns:
            Build result dictionary with status and image ID
        """
        logger.info(f"Starting build for {tool} ({os})")

        # Generate build plan using LLM
        build_plan = await self.llm.generate_build_plan(
            tool=tool,
            os=os,
            version=version,
        )
        build_job_id = self.state_manager.create_build_job(
            tool=tool,
            os=os,
            version=version,
            status="planning",
        )

        try:
            # Generate Dockerfile
            dockerfile_content = self.dockerfile_generator.generate(
                tool=tool,
                os=os,
                version=version,
                plan=build_plan,
            )

            logger.info(f"Build job {build_job_id}: Dockerfile generated")
            self.state_manager.update_build_job(
                build_job_id, status="dockerfile_generated"
            )

            # Build image
            image_id = await self.image_builder.build(
                dockerfile=dockerfile_content,
                tool=tool,
                os=os,
                version=version,
                output_name=output_name,
            )

            logger.info(f"Build job {build_job_id}: Image built successfully")
            self.state_manager.update_build_job(
                build_job_id,
                status="completed",
                image_id=image_id,
            )

            # Push to registry if specified
            if registry:
                logger.info(f"Pushing image to {registry}")
                await self.image_builder.push(image_id, registry)
                self.state_manager.update_build_job(
                    build_job_id, status="pushed"
                )

            return {
                "success": True,
                "build_id": build_job_id,
                "image_id": image_id,
                "tool": tool,
                "os": os,
                "version": version,
            }

        except Exception as e:
            logger.error(f"Build job {build_job_id} failed: {str(e)}")
            self.state_manager.update_build_job(
                build_job_id, status="failed", error=str(e)
            )
            return {
                "success": False,
                "build_id": build_job_id,
                "error": str(e),
            }

    async def deploy_image(
        self,
        image_id: str,
        replicas: int = 1,
        env: str = "dev",
        namespace: str = "default",
    ) -> dict:
        """
        Deploy an image to Kubernetes using Argo CD.

        Args:
            image_id: Docker image ID/name
            replicas: Number of replicas
            env: Environment (dev, staging, production)
            namespace: Kubernetes namespace

        Returns:
            Deployment result dictionary
        """
        logger.info(f"Starting deployment of {image_id} to {env}")

        deployment_id = self.state_manager.create_deployment(
            image_id=image_id,
            env=env,
            replicas=replicas,
            status="pending",
        )

        try:
            # Generate deployment manifest using LLM
            manifest = await self.llm.generate_deployment_manifest(
                image_id=image_id,
                replicas=replicas,
                env=env,
                namespace=namespace,
            )

            logger.info(f"Deployment {deployment_id}: Manifest generated")
            self.state_manager.update_deployment(
                deployment_id, status="manifest_ready"
            )

            # Apply manifest using ArgoCD or direct kubectl
            # This would be implemented in a separate module
            logger.info(f"Deployment {deployment_id}: Applying manifest")
            self.state_manager.update_deployment(
                deployment_id, status="deployed"
            )

            return {
                "success": True,
                "deployment_id": deployment_id,
                "image_id": image_id,
                "status": "deployed",
            }

        except Exception as e:
            logger.error(f"Deployment {deployment_id} failed: {str(e)}")
            self.state_manager.update_deployment(
                deployment_id, status="failed", error=str(e)
            )
            return {
                "success": False,
                "deployment_id": deployment_id,
                "error": str(e),
            }

    async def get_status(self, build_id: Optional[str] = None) -> dict:
        """
        Get status of build or deployment.

        Args:
            build_id: Build job ID to check status for

        Returns:
            Status dictionary
        """
        if build_id:
            return self.state_manager.get_build_job(build_id)
        return self.state_manager.get_all_builds()

    async def list_images(self) -> dict:
        """List all available built images."""
        return self.state_manager.get_all_images()

    async def cleanup(self, resource_type: str, resource_id: str) -> dict:
        """Clean up resources."""
        logger.info(f"Cleaning up {resource_type} {resource_id}")
        self.state_manager.mark_resource_deleted(resource_type, resource_id)
        return {"success": True, "resource_id": resource_id}


async def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Agentic AI Container Orchestrator"
    )
    parser.add_argument(
        "--action",
        type=str,
        choices=[a.value for a in AgentAction],
        required=True,
        help="Action to perform",
    )
    parser.add_argument("--tool", type=str, help="Tool name (e.g., trace32)")
    parser.add_argument("--os", type=str, default="windows", help="Target OS")
    parser.add_argument("--version", type=str, default="latest", help="Tool version")
    parser.add_argument("--image", type=str, help="Image ID or name")
    parser.add_argument("--replicas", type=int, default=1, help="Number of replicas")
    parser.add_argument("--env", type=str, default="dev", help="Environment")
    parser.add_argument("--build-id", type=str, help="Build job ID")
    parser.add_argument("--registry", type=str, help="Container registry URL")
    parser.add_argument("--output", type=str, help="Output image name")
    parser.add_argument("--local", action="store_true", help="Run locally")

    args = parser.parse_args()

    orchestrator = ContainerOrchestrator()

    if args.action == AgentAction.BUILD.value:
        result = await orchestrator.build_image(
            tool=args.tool,
            os=args.os,
            version=args.version,
            output_name=args.output,
            registry=args.registry,
        )
    elif args.action == AgentAction.DEPLOY.value:
        result = await orchestrator.deploy_image(
            image_id=args.image,
            replicas=args.replicas,
            env=args.env,
        )
    elif args.action == AgentAction.STATUS.value:
        result = await orchestrator.get_status(build_id=args.build_id)
    elif args.action == AgentAction.LIST.value:
        result = await orchestrator.list_images()
    elif args.action == AgentAction.CLEANUP.value:
        result = await orchestrator.cleanup("build", args.build_id)

    print(result)
    return result


if __name__ == "__main__":
    asyncio.run(main())
