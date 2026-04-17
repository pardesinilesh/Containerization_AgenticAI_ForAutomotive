"""
Cleanup utility for removing old images and deployments.
"""
import argparse
import asyncio
from agent.orchestrator import ContainerOrchestrator
from agent.state_manager import StateManager


async def cleanup_old_builds(days: int = 7):
    """
    Remove builds older than specified days.

    Args:
        days: Age threshold in days
    """
    from datetime import datetime, timedelta

    state_manager = StateManager()
    builds = state_manager.get_all_builds()

    cutoff = datetime.utcnow() - timedelta(days=days)

    for build in builds:
        if build.get("created_at"):
            created = datetime.fromisoformat(build["created_at"])
            if created < cutoff and build.get("status") != "deleted":
                print(f"Deleting old build: {build['id']}")
                state_manager.update_build_job(build["id"], status="deleted")


async def cleanup_failed_builds():
    """Remove all failed builds."""
    state_manager = StateManager()
    orchestrator = ContainerOrchestrator()

    builds = state_manager.get_all_builds()

    for build in builds:
        if build.get("status") == "failed":
            print(f"Cleaning up failed build: {build['id']}")
            await orchestrator.cleanup("build", build["id"])


async def cleanup_unused_images():
    """Remove locally unused images."""
    orchestrator = ContainerOrchestrator()
    images = await orchestrator.list_images()

    for image in images.get("images", []):
        print(f"Cleaned image: {image}")


async def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Cleanup utility")
    parser.add_argument(
        "--action",
        choices=["old-builds", "failed-builds", "unused-images"],
        required=True,
    )
    parser.add_argument("--days", type=int, default=7, help="Age threshold")

    args = parser.parse_args()

    if args.action == "old-builds":
        await cleanup_old_builds(args.days)
    elif args.action == "failed-builds":
        await cleanup_failed_builds()
    elif args.action == "unused-images":
        await cleanup_unused_images()


if __name__ == "__main__":
    asyncio.run(main())
