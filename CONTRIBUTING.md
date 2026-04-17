# Contributing Guide

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone <your-fork-url>`
3. Create a feature branch: `git checkout -b feature/my-feature`
4. Set up development environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

## Development Setup

### Run Tests
```bash
pytest
pytest -v  # Verbose
pytest --cov=agent --cov=builders  # With coverage
```

### Run Linting
```bash
flake8 agent builders
black agent builders
mypy agent builders
```

### Run Locally
```bash
# Start all services
docker-compose up

# In another terminal, initialize database
python scripts/init_db.py

# Run the API
uvicorn agent.api:app --reload

# Or use CLI
python -m agent.cli build --help
```

## Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for all functions
- Maximum line length: 100 characters

## Adding a New Tool

1. Create tool config: `config/tools/my_tool.yaml`
2. (Optional) Create Dockerfile template: `templates/my_tool_linux.dockerfile`
3. Add test case: `tests/test_my_tool.py`
4. Document in README

Example tool config:
```yaml
name: "my_tool"
supported_os:
  - windows
  - linux
docker:
  ports: []
  volumes: []
resources:
  cpu:
    request: "500m"
    limit: "1000m"
```

## Submitting Changes

1. Commit with clear messages: `git commit -m "feat: add support for new tool"`
2. Push to your fork: `git push origin feature/my-feature`
3. Create a Pull Request with:
   - Description of changes
   - Testing information
   - Any breaking changes
   - Related issues

## Pull Request Checklist

- [ ] Tests pass: `pytest`
- [ ] Code formatted: `black .`
- [ ] Linting passes: `flake8`
- [ ] Type hints added: `mypy`
- [ ] Documentation updated
- [ ] Tests added for new functionality

## Reporting Issues

- Use issue templates when available
- Include:
  - Python version
  - OS
  - Steps to reproduce
  - Expected vs actual behavior
  - Relevant logs/errors

## Project Structure Areas

- `agent/` - Core orchestration engine
- `builders/` - Docker image builders
- `kubernetes/` - K8s manifests
- `config/` - Configuration files
- `tests/` - Test suite
- `docs/` - Documentation

## Questions?

- Check existing issues/discussions
- Review documentation in `docs/`
- Open a discussion for questions

Thank you for contributing!
