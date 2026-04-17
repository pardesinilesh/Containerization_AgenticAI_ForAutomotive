# Trace32 (Lauterbach) Debugging Tool for Automotive Development
# Windows Server 2022 - Production Ready

FROM mcr.microsoft.com/windows/servercore:ltsc2022 AS base

LABEL maintainer="automotive-team@local"
LABEL tool="trace32"
LABEL os="windows"
LABEL vendor="lauterbach"

# Install Chocolatey and dependencies
RUN powershell -Command \
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process; \
    [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12; \
    iex ((New-Object System.Net.ServicePointManager).SecurityProtocol = 'Tls12'; (New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install required tools
RUN choco install -y \
    git \
    python \
    visualstudio2022community \
    dotnet-sdk

# Setup working directory
WORKDIR /app/trace32

# Create data and config directories
RUN mkdir data && \
    mkdir config && \
    mkdir logs

# Copy license (should be injected at runtime)
# COPY ./config/ ./config/

# Environment variables
ENV TRACE32_HOME="C:\\app\\trace32"
ENV TRACE32_PORT=2000
ENV TRACE32_DEBUG=0
ENV PATH="${TRACE32_HOME}\bin;${PATH}"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD powershell -Command try { $response = Invoke-WebRequest http://localhost:2000/health -UseBasicParsing; if ($response.StatusCode -eq 200) { exit 0 } else { exit 1 }} catch { exit 1 }

# Expose debugging ports
EXPOSE 2000 2001 2002

# Default startup command
CMD ["powershell", "-Command", "Write-Host 'Trace32 container started'; Get-ChildItem ${Env:TRACE32_HOME}; Start-Sleep -Seconds 3600"]
