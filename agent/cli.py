"""
Command-line interface for the container orchestrator.
"""
import click
import asyncio
import json
from tabulate import tabulate
from agent.orchestrator import ContainerOrchestrator


@click.group()
def cli():
    """Agentic AI Container Orchestrator CLI."""
    pass


@cli.command()
@click.option("--tool", required=True, help="Tool name (e.g., trace32)")
@click.option("--os", default="windows", help="Target OS")
@click.option("--version", default="latest", help="Tool version")
@click.option("--registry", default=None, help="Container registry URL")
@click.option("--output", default=None, help="Output image name")
def build(tool, os, version, registry, output):
    """Build a Docker image."""
    click.echo(f"🔨 Building {tool} for {os}...")

    orchestrator = ContainerOrchestrator()
    result = asyncio.run(
        orchestrator.build_image(
            tool=tool,
            os=os,
            version=version,
            registry=registry,
            output_name=output,
        )
    )

    if result.get("success"):
        click.secho(
            f"✓ Build successful! Image ID: {result['image_id']}",
            fg="green",
        )
    else:
        click.secho(f"✗ Build failed: {result.get('error')}", fg="red")


@cli.command()
@click.option("--image", required=True, help="Docker image to deploy")
@click.option("--replicas", default=3, help="Number of replicas")
@click.option("--env", default="production", help="Environment")
@click.option("--namespace", default="automotive-tools", help="K8s namespace")
def deploy(image, replicas, env, namespace):
    """Deploy image to Kubernetes."""
    click.echo(f"🚀 Deploying {image} to {env}...")

    orchestrator = ContainerOrchestrator()
    result = asyncio.run(
        orchestrator.deploy_image(
            image_id=image,
            replicas=replicas,
            env=env,
            namespace=namespace,
        )
    )

    if result.get("success"):
        click.secho(
            f"✓ Deployment successful! ID: {result['deployment_id']}",
            fg="green",
        )
    else:
        click.secho(f"✗ Deployment failed: {result.get('error')}", fg="red")


@cli.command()
@click.option("--build-id", default=None, help="Specific build ID")
def status(build_id):
    """Check status of builds."""
    orchestrator = ContainerOrchestrator()
    result = asyncio.run(orchestrator.get_status(build_id=build_id))

    if isinstance(result, list):
        if result:
            headers = list(result[0].keys())
            click.echo(tabulate(result, headers=headers, tablefmt="grid"))
        else:
            click.echo("No builds found.")
    else:
        click.echo(json.dumps(result, indent=2))


@cli.command()
def images():
    """List available images."""
    orchestrator = ContainerOrchestrator()
    result = asyncio.run(orchestrator.list_images())

    if "images" in result:
        images_list = result["images"]
        if images_list:
            headers = ["Image ID", "Tool", "OS", "Version", "Created"]
            rows = [
                [
                    img["image_id"],
                    img["tool"],
                    img["os"],
                    img["version"],
                    img["created_at"],
                ]
                for img in images_list
            ]
            click.echo(tabulate(rows, headers=headers, tablefmt="grid"))
        else:
            click.echo("No images found.")
    else:
        click.echo("Error retrieving images.")


@cli.command()
@click.option("--resource-type", required=True, help="Type of resource")
@click.option("--resource-id", required=True, help="Resource ID")
def cleanup(resource_type, resource_id):
    """Clean up resources."""
    click.confirm(
        f"Are you sure you want to delete {resource_type} {resource_id}?",
        abort=True,
    )

    orchestrator = ContainerOrchestrator()
    result = asyncio.run(
        orchestrator.cleanup(resource_type, resource_id)
    )

    if result.get("success"):
        click.secho("✓ Resource deleted.", fg="green")
    else:
        click.secho("✗ Deletion failed.", fg="red")


@cli.command()
def init_db():
    """Initialize database."""
    click.echo("📦 Initializing database...")

    from scripts.init_db import init_database

    success = init_database()
    if success:
        click.secho("✓ Database initialized successfully.", fg="green")
    else:
        click.secho("✗ Database initialization failed.", fg="red")


def main():
    """Entry point."""
    cli()


if __name__ == "__main__":
    main()
