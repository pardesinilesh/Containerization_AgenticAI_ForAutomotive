#!/usr/bin/env python3
"""
Generate PlantUML diagrams using Kroki.io service
With SSL certificate verification workaround for macOS systems
"""
import urllib.request
import urllib.error
import ssl
import base64
import zlib
from pathlib import Path
import json
import time

# Create SSL context that doesn't verify certificates (workaround for macOS certifi issues)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


def encode_diagram(puml_content):
    """Encode PlantUML diagram for Kroki.io service."""
    compressed = zlib.compress(puml_content.encode('utf-8'))
    encoded = base64.b64encode(compressed).decode('utf-8')
    return encoded


def generate_with_kroki(puml_file, output_format='png'):
    """Generate diagram using Kroki.io service."""
    
    # Read PlantUML file
    with open(puml_file, 'r') as f:
        content = f.read()
    
    # Encode diagram
    encoded = encode_diagram(content)
    
    # Kroki.io endpoint
    url = f"https://kroki.io/plantuml/{output_format}"
    
    try:
        # Send request with SSL context
        data = encoded.encode('utf-8')
        req = urllib.request.Request(url, data=data)
        req.add_header('Content-Type', 'text/plain')
        
        # Get response with timeout and custom SSL context
        with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
            image_data = response.read()
        
        # Save image
        output_file = puml_file.with_suffix(f'.{output_format}')
        with open(output_file, 'wb') as f:
            f.write(image_data)
        
        return True, output_file
        
    except urllib.error.URLError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)


def main():
    """Generate all PlantUML diagrams using Kroki.io."""
    
    arch_dir = Path("/Users/pardesinilesh/Downloads/Containerization/docs/architecture")
    
    # Find all PlantUML files
    puml_files = sorted(arch_dir.glob("*.puml"))
    
    if not puml_files:
        print("❌ No PlantUML files found!")
        return
    
    print(f"📊 Found {len(puml_files)} PlantUML files\n")
    print("🎨 Generating diagrams using Kroki.io...\n")
    
    results = {
        "total_files": len(puml_files),
        "generated": 0,
        "failed": 0,
        "diagrams": {}
    }
    
    # Generate PNG and SVG for each file
    for puml_file in puml_files:
        filename = puml_file.name
        results["diagrams"][filename] = {}
        
        print(f"📄 {filename}")
        
        # PNG
        print(f"  └─ PNG: ", end="", flush=True)
        success, result = generate_with_kroki(puml_file, 'png')
        if success:
            print(f"✅ {result.name}")
            results["generated"] += 1
            results["diagrams"][filename]["png"] = result.name
        else:
            print(f"❌ {result}")
            results["failed"] += 1
        
        # SVG  
        print(f"  └─ SVG: ", end="", flush=True)
        success, result = generate_with_kroki(puml_file, 'svg')
        if success:
            print(f"✅ {result.name}")
            results["generated"] += 1
            results["diagrams"][filename]["svg"] = result.name
        else:
            print(f"❌ {result}")
            results["failed"] += 1
        
        # Small delay between requests
        time.sleep(0.5)
    
    print(f"\n{'='*60}")
    print(f"✅ Generated {results['generated']} files successfully")
    print(f"❌ Failed: {results['failed']}")
    print(f"{'='*60}\n")
    
    # Save results
    results_file = arch_dir / "generation_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # List all files
    print("📁 Generated files in architecture folder:\n")
    image_files = 0
    for item in sorted(arch_dir.glob("*")):
        if item.suffix in ['.png', '.svg']:
            image_files += 1
        size_kb = item.stat().st_size / 1024
        icon = "🖼️ " if item.suffix in ['.png', '.svg'] else "📄"
        print(f"  {icon} {item.name:40} ({size_kb:7.1f} KB)")
    
    print(f"\n📊 Summary:")
    print(f"  • PlantUML files: {len(puml_files)}")
    print(f"  • Generated images: {image_files}")
    print(f"  • Format: PNG + SVG for each diagram")


if __name__ == "__main__":
    main()
