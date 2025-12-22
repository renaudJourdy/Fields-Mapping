#!/usr/bin/env python3
"""Quick validation script for generated YAML."""

import yaml
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR.parent / "output"

# Find most recent YAML file
yaml_files = list(OUTPUT_DIR.glob("*.yaml"))
if not yaml_files:
    print("No YAML files found")
    exit(1)

yaml_file = max(yaml_files, key=lambda p: p.stat().st_mtime)
print(f"Validating: {yaml_file}")

with open(yaml_file, 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

print(f"Version: {data['version']}")
print(f"Provider: {data['provider']}")
print(f"Total mappings: {len(data['mappings'])}")
print(f"Sample fields: {list(data['mappings'].keys())[:5]}")

# Check a few mappings
for field_name in list(data['mappings'].keys())[:3]:
    mapping = data['mappings'][field_name]
    print(f"\n  {field_name}:")
    print(f"    - type: {mapping.get('type')}")
    print(f"    - has unit: {'unit' in mapping}")
    print(f"    - has data_type: {'data_type' in mapping}")
    print(f"    - has error_handling: {'error_handling' in mapping}")

print("\nYAML is valid!")

