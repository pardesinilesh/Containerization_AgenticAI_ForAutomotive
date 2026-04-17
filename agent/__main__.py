"""
Main entry point for agent orchestrator.
"""
import asyncio
import sys
from agent.cli import cli


def main():
    """Entry point."""
    try:
        cli()
    except KeyboardInterrupt:
        print("\nShutdown requested...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
