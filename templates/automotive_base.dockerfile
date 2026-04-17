# Automotive Base Image - Shared Foundation
# Includes common dependencies for all automotive tools

FROM ubuntu:22.04 AS automotive-base

LABEL maintainer="automotive-team@local"
LABEL description="Base image for automotive development tools"

ENV DEBIAN_FRONTEND=noninteractive

# Install common automotive development dependencies
RUN apt-get update && apt-get install -y \
    # Build tools
    build-essential \
    cmake \
    git \
    # Language support
    python3 python3-pip \
    python3-dev \
    # Debugging
    gdb \
    lldb \
    valgrind \
    # Network tools
    curl wget \
    net-tools \
    iputils-ping \
    # Security
    openssl \
    ca-certificates \
    # Utilities
    vim nano \
    htop \
    tmux \
    less \
    # Compression
    tar gzip zip \
    && rm -rf /var/lib/apt/lists/*

# Setup common environment
ENV APP_HOME=/app
ENV LOG_DIR=/var/log/automotive
ENV DATA_DIR=/app/data

RUN mkdir -p ${APP_HOME} ${LOG_DIR} ${DATA_DIR}

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser ${APP_HOME} ${LOG_DIR} ${DATA_DIR}

# Setup Python
RUN python3 -m pip install --no-cache-dir \
    pip --upgrade

# Health check placeholder
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD test -f /tmp/health || exit 1

WORKDIR ${APP_HOME}
USER appuser
