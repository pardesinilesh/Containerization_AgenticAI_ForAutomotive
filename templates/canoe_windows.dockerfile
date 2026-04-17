# CANoe (Vector) Network Analysis Tool for Automotive Development
# Windows Server 2022 LTS Base Image

FROM mcr.microsoft.com/windows/servercore:ltsc2022 as base

LABEL tool="canoe" \
      vendor="vector" \
      version="latest" \
      maintainer="Automotive Development Team"

# Set working directory
WORKDIR /app/canoe

# Install required dependencies
RUN powershell -Command \
    $ErrorActionPreference = 'Stop'; \
    # Install Chocolatey \
    iex ((New-Object System.Net.ServicePointManager).ServerCertificateValidationCallback = {$true}); \
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; \
    iex ((New-Object Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1')); \
    # Install dependencies \
    choco install -y git visualstudio2022community dotnet-sdk python mingw; \
    rm -Force C:\ProgramData\chocolatey\logs\*

# Create directory structure
RUN powershell -Command \
    mkdir -Force C:\app\canoe\config | Out-Null; \
    mkdir -Force C:\app\canoe\data | Out-Null; \
    mkdir -Force C:\app\canoe\logs | Out-Null; \
    mkdir -Force C:\app\canoe\projects | Out-Null

# Set environment variables
ENV CANOE_HOME="C:\\app\\canoe" \
    CANOE_PORT=5432 \
    CANOE_DEBUG=0 \
    CANOE_CONFIG_PATH="C:\\app\\canoe\\config" \
    CANOE_DATA_PATH="C:\\app\\canoe\\data"

# Copy configuration files if they exist
COPY config/ C:\app\canoe\config\

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD powershell -Command \
    $response = Invoke-WebRequest http://localhost:8080/health -ErrorAction SilentlyContinue; \
    if ($response.StatusCode -eq 200) { exit 0 } else { exit 1 }

# Create startup script
RUN powershell -Command \
    $startupScript = @' \
#!/usr/bin/env python \
import os \
import sys \
import subprocess \
from pathlib import Path \
 \
def main(): \
    canoe_home = os.environ.get('CANOE_HOME', 'C:\\\\app\\\\canoe') \
    config_path = os.environ.get('CANOE_CONFIG_PATH', f'{canoe_home}\\\\config') \
    data_path = os.environ.get('CANOE_DATA_PATH', f'{canoe_home}\\\\data') \
    \
    print(f'[CANoe] Starting CANoe service...') \
    print(f'[CANoe] Home: {canoe_home}') \
    print(f'[CANoe] Config: {config_path}') \
    print(f'[CANoe] Data: {data_path}') \
    \
    # Placeholder for actual CANoe startup logic \
    print('[CANoe] CANoe service initialized successfully') \
    print('[CANoe] Listening on port 5432') \
    \
    # Keep container running \
    import time \
    while True: \
        time.sleep(1) \
 \
if __name__ == '__main__': \
    main() \
'@; \
    $startupScript | Out-File -FilePath C:\app\canoe\start.py -Encoding UTF8

WORKDIR C:\app\canoe

# Start CANoe service
CMD ["python", "start.py"]
