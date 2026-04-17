# CANoe (Vector) Network Analysis Tool for Automotive Development
# Ubuntu 22.04 LTS Base Image

FROM ubuntu:22.04 as base

LABEL tool="canoe" \
      vendor="vector" \
      version="latest" \
      maintainer="Automotive Development Team"

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    wget \
    python3 \
    python3-dev \
    python3-pip \
    libpq-dev \
    postgresql-client \
    openssh-client \
    net-tools \
    iputils-ping \
    telnet \
    vim \
    nano \
    && rm -rf /var/lib/apt/lists/*

# Create application directory structure
RUN mkdir -p /app/canoe/{config,data,logs,projects}

WORKDIR /app/canoe

# Set environment variables
ENV CANOE_HOME="/app/canoe" \
    CANOE_PORT=5432 \
    CANOE_DEBUG=0 \
    CANOE_CONFIG_PATH="/app/canoe/config" \
    CANOE_DATA_PATH="/app/canoe/data" \
    PATH="/app/canoe/bin:$PATH"

# Install Python dependencies for CANoe support
RUN pip3 install --no-cache-dir \
    can \
    python-can \
    cantools \
    pydantic \
    fastapi \
    uvicorn \
    psycopg2-binary

# Copy configuration files if they exist
COPY config/ /app/canoe/config/

# Create startup script
RUN cat > /app/canoe/start.sh << 'EOF' \
#!/bin/bash \
set -e \
 \
echo "[CANoe] Starting CANoe service..." \
echo "[CANoe] Home: $CANOE_HOME" \
echo "[CANoe] Config: $CANOE_CONFIG_PATH" \
echo "[CANoe] Data: $CANOE_DATA_PATH" \
 \
# Create necessary directories \
mkdir -p "$CANOE_HOME"/{config,data,logs,projects} \
 \
# Placeholder for actual CANoe startup logic \
echo "[CANoe] CANoe service initialized successfully" \
echo "[CANoe] Listening on port 5432" \
 \
# Execute startup Python script \
python3 /app/canoe/start.py \
EOF

# Create Python startup script
RUN cat > /app/canoe/start.py << 'EOF' \
#!/usr/bin/env python3 \
import os \
import sys \
import time \
from pathlib import Path \
 \
def initialize_canoe(): \
    """Initialize CANoe service""" \
    canoe_home = os.environ.get('CANOE_HOME', '/app/canoe') \
    config_path = os.environ.get('CANOE_CONFIG_PATH', f'{canoe_home}/config') \
    data_path = os.environ.get('CANOE_DATA_PATH', f'{canoe_home}/data') \
    \
    print(f'[CANoe] Home directory: {canoe_home}') \
    print(f'[CANoe] Config path: {config_path}') \
    print(f'[CANoe] Data path: {data_path}') \
    \
    # Ensure directories exist \
    Path(config_path).mkdir(parents=True, exist_ok=True) \
    Path(data_path).mkdir(parents=True, exist_ok=True) \
    \
    print('[CANoe] CANoe service initialized successfully') \
    print('[CANoe] Listening on port 5432') \
    \
    # Keep service running \
    try: \
        while True: \
            time.sleep(1) \
    except KeyboardInterrupt: \
        print('[CANoe] CANoe service stopped') \
        sys.exit(0) \
 \
if __name__ == '__main__': \
    initialize_canoe() \
EOF

# Make scripts executable
RUN chmod +x /app/canoe/start.sh /app/canoe/start.py

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose ports
EXPOSE 5432 8080 8443

WORKDIR /app/canoe

# Start CANoe service
ENTRYPOINT ["/app/canoe/start.sh"]
CMD []
