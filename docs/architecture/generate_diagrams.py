#!/usr/bin/env python3
"""
Generate diagrams from PlantUML files using the PlantUML online renderer.
"""
import os
import sys
from pathlib import Path
import urllib.request
import urllib.error
import zlib
import base64

def encode_plantuml(puml_content):
    """Encode PlantUML content for URL."""
    data = zlib.compress(puml_content.encode('utf-8'), 9)
    return base64.b64encode(data).decode('ascii')


def generate_diagram(puml_file, output_format='png'):
    """Generate a single diagram."""
    
    try:
        # Read PlantUML content
        with open(puml_file, 'r') as f:
            puml_content = f.read()
        
        # Encode
        encoded = encode_plantuml(puml_content)
        
        # Build URL
        base_url = "http://www.plantuml.com/plantuml"
        url = f"{base_url}/{output_format}/{encoded}"
        
        # Output file
        output_file = puml_file.with_suffix(f'.{output_format}')
        
        # Download
        print(f"  📥 Generating {output_format.upper()}: {output_file.name}", end=" ")
        sys.stdout.flush()
        
        urllib.request.urlretrieve(url, output_file)
        
        file_size = os.path.getsize(output_file)
        print(f"✓ ({file_size:,} bytes)")
        
        return True
        
    except urllib.error.URLError as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main entry point."""
    
    print("🎨 PlantUML Diagram Generator (Online Renderer)\n")
    
    puml_dir = Path("/Users/pardesinilesh/Downloads/Containerization/docs/architecture")
    puml_files = sorted(list(puml_dir.glob("*.puml")))
    
    if not puml_files:
        print("❌ No PlantUML files found!")
        return False
    
    print(f"Found {len(puml_files)} PlantUML files\n")
    
    success_count = 0
    
    for puml_file in puml_files:
        print(f"📊 {puml_file.name}")
        
        # Generate PNG
        if generate_diagram(puml_file, 'png'):
            success_count += 1
        
        # Generate SVG
        if generate_diagram(puml_file, 'svg'):
            success_count += 1
    
    if success_count == len(puml_files) * 2:
        print(f"\n✅ All diagrams generated successfully!")
        print(f"\n📁 Files in {puml_dir}:")
        
        for file in sorted(puml_dir.iterdir()):
            if file.suffix in ['.png', '.svg', '.puml']:
                size = os.path.getsize(file)
                print(f"  - {file.name} ({size:,} bytes)")
        
        return True
    else:
        print(f"\n⚠️  Generated {success_count}/{len(puml_files) * 2} diagrams")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
