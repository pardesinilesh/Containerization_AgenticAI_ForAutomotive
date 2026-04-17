"""
Deployment script for Kubernetes + Argo CD.
"""
import argparse
import asyncio
import logging
import yaml
from pathlib import Path
from agent.orchestrator import ContainerOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def deploy(
    image: str,
    replicas: int = 3,
    env: str = "production",
    cluster: str = "default",
    namespace: str = "automotive-tools",
):
    """
    Deploy image to Kubernetes cluster.

    Args:
        image: Docker image ID or name
        replicas: Number of replicas
        env: Environment name
        cluster: Kubernetes cluster name
        namespace: Kubernetes namespace
    """
    logger.info(f"Deploying {image} to {cluster}/{namespace}")

    orchestrator = ContainerOrchestrator()

    result = await orchestrator.deploy_image(
        image_id=image,
        replicas=replicas,
        env=env,
        namespace=namespace,
    )

    if result["success"]:
        logger.info(f"Deployment successful: {result['deployment_id']}")
    else:
        logger.error(f"Deployment failed: {result['error']}")

    return result


async def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Deploy to Kubernetes")
    parser.add_argument("--image", type=str, required=True, help="Image to deploy")
    parser.add_argument("--replicas", type=int, default=3, help="Number of replicas")
    parser.add_argument("--env", type=str, default="production", help="Environment")
    parser.add_argument("--cluster", type=str, default="default", help="Cluster name")
    parser.add_argument(
        "--namespace",
        type=str,
        default="automotive-tools",
        help="Kubernetes namespace",
    )

    args = parser.parse_args()

    result = await deploy(
        image=args.image,
        replicas=args.replicas,
        env=args.env,
        cluster=args.cluster,
        namespace=args.namespace,
    )

    print(f"Deployment Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
