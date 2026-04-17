"""
Docker image builder for compiling Dockerfiles into images.
"""
import subprocess
import logging
from typing import Optional
import docker

logger = logging.getLogger(__name__)


class ImageBuilder:
    """Builds Docker images from Dockerfiles."""

    def __init__(self):
        """Initialize Docker client."""
        try:
            self.client = docker.from_env()
        except Exception as e:
            logger.warning(f"Docker client initialization failed: {e}")
            self.client = None

    async def build(
        self,
        dockerfile: str,
        tool: str,
        os: str,
        version: str,
        output_name: Optional[str] = None,
        buildargs: Optional[dict] = None,
    ) -> str:
        """
        Build Docker image.

        Args:
            dockerfile: Dockerfile content as string
            tool: Tool name
            os: Target OS
            version: Tool version
            output_name: Custom output image name
            buildargs: Build arguments

        Returns:
            Image ID or name
        """
        import tempfile
        import os as os_module

        # Create temporary file for Dockerfile
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".dockerfile", delete=False
        ) as f:
            f.write(dockerfile)
            temp_dockerfile = f.name

        try:
            # Generate image name
            image_name = output_name or f"automotive-{tool}:{version}-{os}"

            logger.info(f"Building image: {image_name}")

            if self.client:
                # Use docker SDK
                try:
                    image, build_logs = self.client.images.build(
                        dockerfile=temp_dockerfile,
                        tag=image_name,
                        buildargs=buildargs or {},
                        rm=True,
                    )
                    logger.info(f"Image built successfully: {image.id}")
                    return image.id

                except Exception as e:
                    logger.error(f"Docker SDK build failed, falling back to CLI: {e}")

            # Fallback to CLI
            cmd = [
                "docker",
                "build",
                "-f", temp_dockerfile,
                "-t", image_name,
                ".",
            ]

            if buildargs:
                for key, value in buildargs.items():
                    cmd.extend(["--build-arg", f"{key}={value}"])

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                logger.info(f"Image built successfully: {image_name}")
                return image_name
            else:
                raise RuntimeError(f"Build failed: {result.stderr}")

        finally:
            # Cleanup temp file
            os_module.unlink(temp_dockerfile)

    async def push(
        self,
        image_id: str,
        registry: str,
        tag: str = "latest",
    ) -> bool:
        """
        Push image to registry.

        Args:
            image_id: Image ID or name
            registry: Registry URL
            tag: Image tag

        Returns:
            Success status
        """
        logger.info(f"Pushing {image_id} to {registry}")

        # Tag image for registry
        registry_image = f"{registry}/{image_id}:{tag}"

        try:
            if self.client:
                logger.info(f"Tagging {image_id} as {registry_image}")
                self.client.images.get(image_id).tag(registry_image)

                logger.info(f"Pushing to registry: {registry_image}")
                self.client.images.push(registry_image)
                logger.info(f"Push successful: {registry_image}")
                return True

        except Exception as e:
            logger.error(f"Docker SDK push failed, falling back to CLI: {e}")

        # Fallback to CLI
        try:
            subprocess.run(
                ["docker", "tag", image_id, registry_image],
                check=True,
                capture_output=True,
            )
            result = subprocess.run(
                ["docker", "push", registry_image],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                logger.info(f"Push successful: {registry_image}")
                return True
            else:
                logger.error(f"Push failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Push failed: {e}")
            return False

    async def list_images(self) -> list:
        """List all available images."""
        try:
            if self.client:
                images = self.client.images.list()
                return [
                    {
                        "id": img.id,
                        "tags": img.tags,
                        "size": img.attrs.get("Size", 0),
                    }
                    for img in images
                ]
        except Exception as e:
            logger.error(f"Failed to list images: {e}")

        return []

    async def clean(self, image_id: str) -> bool:
        """
        Remove a docker image.

        Args:
            image_id: Image ID or name

        Returns:
            Success status
        """
        try:
            if self.client:
                self.client.images.remove(image_id, force=True)
                logger.info(f"Image removed: {image_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to remove image: {e}")
            return False

        return False
