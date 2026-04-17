# Trace32 (Lauterbach) Debugging Tool for Automotive Development
# Ubuntu 22.04 - Production Ready

FROM ubuntu:22.04 AS base

LABEL maintainer="automotive-team@local"
LABEL tool="trace32"
LABEL os="linux"
LABEL vendor="lauterbach"

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    wget \
    python3 \
    python3-pip \
    libssl-dev \
    libreadline-dev \
    zlib1g-dev \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Setup working directory
WORKDIR /app/trace32

# Create data and config directories
RUN mkdir -p data config logs && \
    chmod 755 data config logs

# Environment variables
ENV TRACE32_HOME="/app/trace32"
ENV TRACE32_PORT=2000
ENV TRACE32_DEBUG=0
ENV PATH="${TRACE32_HOME}/bin:${PATH}"

# Install Python dependencies
RUN python3 -m pip install --no-cache-dir \
    flask==3.0.0 \
    gunicorn==21.2.0 \
    requests==2.31.0

# Create namespace for isolation
RUN useradd -m -u 1000 trace32user

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:2000/health || exit 1

# Expose debugging ports
EXPOSE 2000 2001 2002

# Default startup command
CMD ["/bin/bash", "-c", "echo 'Trace32 container started' && sleep 3600"]
