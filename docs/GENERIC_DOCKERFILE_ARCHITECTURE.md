# Generic Dockerfile Template Architecture

## Overview

This platform uses a **configuration-driven, generic Dockerfile architecture** instead of maintaining separate Dockerfiles for each tool. This approach significantly reduces code duplication, improves maintainability, and makes it trivial to add new tools.

## Architecture Pattern

```
Tool Configuration (YAML) → Generic Template (Jinja2) → Generated Dockerfile
```

## How It Works

### 1. Tool Configuration (`config/tools/`)

Each tool has a YAML configuration file that defines all its requirements:

```yaml
# config/tools/mynewtools.yaml
name: mynewtools
display_name: "My New Tool"
vendor: vendorname
description: "Tool description"

supported_os:
  - windows
  - linux

docker:
  base_images:
    windows: "mcr.microsoft.com/windows/servercore:ltsc2022"
    linux: "ubuntu:22.04"
  
  ports:
    - 5432
    - 8080
  
  volumes:
    - /app/mynewtools/data
    - /app/mynewtools/config

resources:
  cpu:
    request: "1000m"
    limit: "2000m"
  memory:
    request: "2Gi"
    limit: "4Gi"

features:
  feature1: true
  feature2: true

environment_variables:
  TOOL_HOME: "/app/mynewtools"
  TOOL_PORT: "5432"

dependencies:
  windows:
    - git
    - visualstudio2022community
  linux:
    - build-essential
    - git
    - python3-dev

python_dependencies:
  - pydantic
  - fastapi
  - uvicorn

health_check:
  enabled: true
  interval: "30s"
  timeout: "10s"
  retries: 3
```

### 2. Generic Templates (`builders/templates/`)

Two reusable Jinja2 templates handle all tools:

- **`generic_linux.dockerfile.j2`** - Ubuntu 22.04 base
- **`generic_windows.dockerfile.j2`** - Windows Server 2022 base

These templates use the tool configuration dynamically:

```dockerfile
# Template snippet (generic_linux.dockerfile.j2)
FROM {{ tool_config.docker.base_images.linux }}

LABEL tool="{{ tool_config.name }}" \
      vendor="{{ tool_config.vendor }}" \
      version="{{ version }}"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
{% for dep in tool_config.dependencies.linux %}
    {{ dep }} \
{% endfor %}
    && rm -rf /var/lib/apt/lists/*

# ... more template logic
```

### 3. Docker File Generator

The `DockerfileGenerator` class orchestrates the process:

```python
# builders/dockerfile_generator.py
class DockerfileGenerator:
    def generate(tool, os, version):
        # 1. Load YAML config
        tool_config = self._load_tool_config(tool)
        
        # 2. Select appropriate generic template
        template_name = "generic_windows.dockerfile.j2" if os == "windows" else "generic_linux.dockerfile.j2"
        
        # 3. Render template with config
        return template.render(
            tool=tool,
            tool_config=tool_config,
            version=version
        )
```

## Adding a New Tool

To add a new automotive tool, follow these 3 simple steps:

### Step 1: Create Tool Configuration

Create `config/tools/newtool.yaml`:

```yaml
name: newtool
display_name: "New Tool (Vendor)"
vendor: vendor
description: "Tool description"
# ... rest of configuration
```

### Step 2: Build the Container

```bash
python -m agent.cli build --tool newtool --os linux
python -m agent.cli build --tool newtool --os windows
```

### Step 3: Deploy

```bash
python scripts/deploy.py --tool newtool --env production
```

## Advantages

✅ **DRY Principle** - No code duplication across tools
✅ **Consistency** - All tools use the same build process
✅ **Extensibility** - Add new tools with just a YAML file
✅ **Maintainability** - Single place to update template logic
✅ **Configurability** - Tool-specific settings in YAML, not hardcoded

## Current Tools

- **Trace32 (Lauterbach)** - Professional debugging tool
- **CANoe (Vector)** - CAN network analysis tool

Both tools use the same generic templates and are configured via YAML.

## Template Variables

The generic templates have access to:

- `tool` - Tool name (string)
- `tool_config` - Full tool configuration (dict)
- `version` - Tool version (string)
- `plan` - Optional build plan from LLM (dict)

## Customization

If a tool needs special handling:

1. **Option A**: Add conditional logic to generic template using Jinja2 `{% if %}`
2. **Option B**: Add tool-specific environment variables to YAML
3. **Option C**: Extend `DockerfileGenerator` class with custom methods

## File Structure

```
builders/
├── templates/
│   ├── generic_linux.dockerfile.j2      # Generic Linux template
│   ├── generic_windows.dockerfile.j2    # Generic Windows template
│   └── __init__.py
├── dockerfile_generator.py              # Template renderer
└── ...

config/
├── tools/
│   ├── trace32.yaml                     # Trace32 configuration
│   ├── canoe.yaml                       # CANoe configuration
│   ├── generic_tool.yaml                # Template for new tools
│   └── ...
└── ...
```

## Next Steps

1. Review existing tool configs (`config/tools/*.yaml`)
2. Study generic template structure (`builders/templates/generic_*.dockerfile.j2`)
3. Add new tool by creating tool config YAML
4. Test with `python -m agent.cli build --tool <newtool> --os linux`

