#!/usr/bin/env python3
"""
Generate diagrams using Kroki.io service (alternative to PlantUML.com)
"""
import os
import sys
from pathlib import Path
import urllib.request
import urllib.error
import json
import base64

def generate_with_kroki(puml_file, output_format='png'):
    """Generate diagram using Kroki service."""
    
    try:
        # Read PlantUML content
        with open(puml_file, 'r') as f:
            puml_content = f.read()
        
        # Kroki endpoint
        kroki_url = "https://kroki.io/plantuml"
        
        # Build request
        payload = {
            "diagram_source": puml_content,
            "output_format": output_format
        }
        
        json_data = json.dumps(payload).encode('utf-8')
        
        # Create request
        req = urllib.request.Request(
            kroki_url,
            data=json_data,
            headers={'Content-Type': 'application/json'}
        )
        
        # Output file
        output_file = puml_file.with_suffix(f'.{output_format}')
        
        print(f"  📥 Generating {output_format.upper()}: {output_file.name}", end=" ")
        sys.stdout.flush()
        
        # Get response
        with urllib.request.urlopen(req) as response:
            diagram_data = response.read()
        
        # Save
        with open(output_file, 'wb') as f:
            f.write(diagram_data)
        
        file_size = os.path.getsize(output_file)
        print(f"✓ ({file_size:,} bytes)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def generate_with_docker(puml_file):
    """Generate diagrams using Docker."""
    
    try:
        import subprocess
        
        print(f"  📥 Using Docker to generate PNG", end=" ")
        sys.stdout.flush()
        
        subprocess.run(
            ["docker", "run", "--rm", "-v", f"{puml_file.parent}:/data",
             "plantuml/plantuml", "-png", f"/data/{puml_file.name}"],
            check=True,
            capture_output=True
        )
        
        output_file = puml_file.with_suffix('.png')
        file_size = os.path.getsize(output_file)
        print(f"✓ ({file_size:,} bytes)")
        
        print(f"  📥 Using Docker to generate SVG", end=" ")
        sys.stdout.flush()
        
        subprocess.run(
            ["docker", "run", "--rm", "-v", f"{puml_file.parent}:/data",
             "plantuml/plantuml", "-svg", f"/data/{puml_file.name}"],
            check=True,
            capture_output=True
        )
        
        output_file = puml_file.with_suffix('.svg')
        file_size = os.path.getsize(output_file)
        print(f"✓ ({file_size:,} bytes)")
        
        return True
        
    except Exception as e:
        print(f"❌ Docker error: {e}")
        return False


def main():
    """Main entry point."""
    
    print("🎨 PlantUML Diagram Generator (Kroki.io + Docker)\n")
    
    puml_dir = Path("/Users/pardesinilesh/Downloads/Containerization/docs/architecture")
    puml_files = sorted(list(puml_dir.glob("*.puml")))
    
    if not puml_files:
        print("❌ No PlantUML files found!")
        return False
    
    print(f"Found {len(puml_files)} PlantUML files\n")
    
    # Try Docker first
    print("⚡ Attempting Docker method...")
    docker_success = False
    for puml_file in puml_files:
        print(f"📊 {puml_file.name}")
        if generate_with_docker(puml_file):
            docker_success = True
            break
    
    if docker_success:
        print("\n✅ Docker method successful! Generating remaining diagrams...")
        for puml_file in puml_files[1:]:
            print(f"📊 {puml_file.name}")
            generate_with_docker(puml_file)
        return True
    
    # Fall back to Kroki
    print("\n⚡ Falling back to Kroki.io service...")
    success_count = 0
    
    for puml_file in puml_files:
        print(f"📊 {puml_file.name}")
        
        # Generate PNG
        if generate_with_kroki(puml_file, 'png'):
            success_count += 1
        
        # Generate SVG
        if generate_with_kroki(puml_file, 'svg'):
            success_count += 1
    
    if success_count > 0:
        print(f"\n✅ Generated {success_count}/{len(puml_files) * 2} diagrams successfully!")
        print(f"\n📁 Files in {puml_dir}:")
        
        for file in sorted(puml_dir.iterdir()):
            if file.suffix in ['.png', '.svg', '.puml']:
                size = os.path.getsize(file)
                print(f"  - {file.name} ({size:,} bytes)")
        
        return True
    else:
        print(f"\n❌ Failed to generate any diagrams")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
