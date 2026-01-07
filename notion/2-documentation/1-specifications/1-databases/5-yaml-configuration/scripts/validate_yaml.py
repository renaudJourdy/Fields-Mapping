#!/usr/bin/env python3
"""Quick validation script for generated YAML."""

import yaml
from pathlib import Path
import csv

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR.parent / "output"
EXPORT_DIR = SCRIPT_DIR.parent.parent / "3-mapping-fields" / "export"

# Find most recent YAML file
yaml_files = list(OUTPUT_DIR.glob("*.yaml"))
if not yaml_files:
    print("No YAML files found")
    exit(1)

yaml_file = max(yaml_files, key=lambda p: p.stat().st_mtime)
print(f"Validating: {yaml_file}")

with open(yaml_file, 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

print("=== YAML SUMMARY ===")
print(f"Version: {data['version']}")
print(f"Provider: {data['provider']}")
print(f"Total mappings: {len(data['mappings'])}")
print("YAML parsed successfully.")
print("")

# Cross-check: ensure every Mapping Fields CSV row is represented in YAML
csv_files = list(EXPORT_DIR.glob("Mapping Fields (db) *.csv"))
if not csv_files:
    print("\nWarning: No Mapping Fields CSV files found for cross-check.")
else:
    csv_file = max(csv_files, key=lambda p: p.stat().st_mtime)
    print("=== CSV/YAML KEY CHECK ===")
    print(f"Cross-checking against CSV: {csv_file}")

    def extract_field_name(raw: str) -> str:
        """Extract field name from Notion link format: 'field_name (https://...)'."""
        if not raw:
            return ""
        return raw.split('(')[0].strip()

    def is_valid_field_path(path: str) -> bool:
        if not path:
            return False
        if ',' in path or ' ' in path:
            return False
        # Allow root-level fields (e.g., last_updated_at) and array paths (e.g., geofences[])
        if '.' not in path:
            return path.endswith('[]') or path.replace('_', '').isalnum()
        return True

    with open(csv_file, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        expected = []
        invalid_paths = []

        for row in reader:
            # Prefer Fleeti Field column when present (matches YAML keys)
            raw = row.get('Fleeti Field', '').strip()
            if not raw:
                raw = row.get('Name', '').strip()
            name = extract_field_name(raw)
            if name:
                expected.append(name)

            field_path = (row.get('Fleeti Field Path') or '').strip()
            if field_path and not is_valid_field_path(field_path):
                invalid_paths.append((name or raw, field_path))

    yaml_keys = set(data.get('mappings', {}).keys())
    expected_set = set(expected)

    missing_in_yaml = sorted(expected_set - yaml_keys)
    extra_in_yaml = sorted(yaml_keys - expected_set)

    if missing_in_yaml:
        print(f"Missing in YAML ({len(missing_in_yaml)}): {missing_in_yaml}")
    if extra_in_yaml:
        print(f"Extra in YAML ({len(extra_in_yaml)}): {extra_in_yaml}")
    if not missing_in_yaml and not extra_in_yaml:
        print("CSV/YAML key sets match.")
    print("")

    if invalid_paths:
        print("=== FIELD PATH CHECK ===")
        print(f"Invalid Fleeti Field Path ({len(invalid_paths)}): {invalid_paths}")
        print("")

# Dependency order check (YAML order must respect parameters.fleeti dependencies)
order = list(data.get('mappings', {}).keys())
index = {name: i for i, name in enumerate(order)}
violations = []

for name, mapping in data.get('mappings', {}).items():
    deps = []
    params = mapping.get('parameters', {})
    fleeti = params.get('fleeti') if isinstance(params, dict) else None
    if isinstance(fleeti, list):
        deps.extend([d for d in fleeti if isinstance(d, str)])
    for source in mapping.get('sources', []) or []:
        params = source.get('parameters', {}) if isinstance(source, dict) else {}
        fleeti = params.get('fleeti') if isinstance(params, dict) else None
        if isinstance(fleeti, list):
            deps.extend([d for d in fleeti if isinstance(d, str)])

    for dep in deps:
        if dep in index and index[dep] > index[name]:
            violations.append((name, dep))

print("=== DEPENDENCY ORDER CHECK ===")
if violations:
    print(f"Dependency order violations ({len(violations)}): {violations}")
else:
    print("Dependency order check: OK")
print("")

print("=== VALIDATION COMPLETE ===")

