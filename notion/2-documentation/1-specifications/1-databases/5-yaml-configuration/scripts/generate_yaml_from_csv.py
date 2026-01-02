#!/usr/bin/env python3
"""
Generate YAML Configuration from Mapping Fields CSV

Reads the most recent CSV file from the export folder and generates
an optimized YAML configuration file following the specifications in
yaml-mapping-reference.yaml.
"""

import csv
import json
import re
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import OrderedDict


# Paths
SCRIPT_DIR = Path(__file__).parent
EXPORT_DIR = SCRIPT_DIR.parent.parent / "3-mapping-fields" / "export"
OUTPUT_DIR = SCRIPT_DIR.parent / "output"

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def find_most_recent_csv() -> Optional[Path]:
    """Find the most recent CSV file matching the pattern."""
    pattern = "Mapping Fields (db) *.csv"
    csv_files = list(EXPORT_DIR.glob("Mapping Fields (db) *.csv"))
    
    if not csv_files:
        return None
    
    # Return the most recently modified file
    return max(csv_files, key=lambda p: p.stat().st_mtime)


def extract_field_name(notion_link: str) -> str:
    """Extract field name from Notion link format: 'field_name (https://...)'"""
    if not notion_link or not notion_link.strip():
        return ""
    
    # Remove Notion link if present
    match = re.match(r'^([^(]+)', notion_link.strip())
    if match:
        return match.group(1).strip()
    
    return notion_link.strip()


def parse_json_field(json_str: str) -> Optional[Dict]:
    """Parse JSON field from CSV, handling escaped quotes and multi-line."""
    if not json_str or not json_str.strip():
        return None
    
    # Remove leading/trailing whitespace
    json_str = json_str.strip()
    
    try:
        # JSON is stored with escaped quotes in CSV ("" for ")
        # Try parsing directly first (Python csv module should handle this)
        return json.loads(json_str)
    except json.JSONDecodeError:
        # If that fails, try unescaping quotes manually
        try:
            # Replace CSV-escaped double quotes ("" -> ")
            cleaned = json_str.replace('""', '"')
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse JSON: {e}")
            print(f"JSON string (first 200 chars): {json_str[:200]}")
            # Try one more time with unescaping newlines
            try:
                cleaned = json_str.replace('""', '"').replace('\\n', '\n')
                return json.loads(cleaned)
            except json.JSONDecodeError:
                return None


def normalize_unit(unit: str, default_to_none: bool = False) -> Optional[str]:
    """
    Normalize unit value.
    
    Args:
        unit: Unit string to normalize
        default_to_none: If True, return "none" for empty/unitless units instead of None
    
    Returns:
        Normalized unit string, or "none" if default_to_none=True and unit is empty/unitless,
        or None if default_to_none=False and unit is empty/unitless
    """
    if not unit or not unit.strip():
        return "none" if default_to_none else None
    
    unit_lower = unit.strip().lower()
    if unit_lower in ['none', '-', '']:
        return "none" if default_to_none else None
    
    return unit_lower


def apply_optimization_rules(
    computation_json: Dict,
    top_level_provider: str,
    provider_field_unit: str,
    fleeti_unit: str,
    data_type: str = ""
) -> Dict:
    """
    Apply optimization rules to convert JSON to optimized YAML structure.
    
    Optimization Rules:
    1. Keep top-level type (always required)
    2. Omit type: direct in sources (default)
    3. Omit provider in sources when matches top-level provider
    4. Omit priority for single-source mappings
    5. Omit description fields (use comments instead)
    6. Omit dependencies when redundant with parameters.fleeti
    7. Omit source_type (inferred from context)
    8. Add unit at both source level and top level
    """
    optimized = {}
    
    # Rule 1: Keep top-level type
    optimized['type'] = computation_json.get('type', 'direct')
    
    mapping_type = optimized['type']
    
    # Handle different mapping types
    if mapping_type in ['direct', 'prioritized']:
        sources = computation_json.get('sources', [])
        optimized_sources = []
        
        # Parse provider_field_unit - could be a single value or comma-separated
        provider_field_units = []
        if provider_field_unit:
            provider_field_units = [u.strip() for u in provider_field_unit.split(',')]
        
        # If we have fewer units than sources, pad with empty strings
        while len(provider_field_units) < len(sources):
            provider_field_units.append('')
        
        for idx, source in enumerate(sources):
            optimized_source = {}
            
            # Rule 4: Omit priority for single-source mappings
            if len(sources) > 1 and 'priority' in source:
                optimized_source['priority'] = source['priority']
            
            # Rule 2: Omit type: direct in sources (default)
            if source.get('type') != 'direct' and 'type' in source:
                optimized_source['type'] = source['type']
            
            # Rule 3: Omit provider in sources when matches top-level provider
            source_provider = source.get('provider', top_level_provider)
            if source_provider != top_level_provider:
                optimized_source['provider'] = source_provider
            
            # Add field and path (required for direct sources)
            if 'field' in source:
                optimized_source['field'] = source['field']
            if 'path' in source:
                optimized_source['path'] = source['path']
            
            # Rule 8: Add unit at source level
            # CRITICAL: Always include unit for direct provider sources (use "none" if unitless)
            # Priority: 1) from CSV column, 2) from JSON source, 3) use fleeti_unit as fallback, 4) use "none"
            if source.get('type') == 'calculated':
                # Handle calculated sources in prioritized mappings
                if 'calculation_type' in source:
                    optimized_source['calculation_type'] = source['calculation_type']
                if 'function' in source:
                    optimized_source['function'] = source['function']
                if 'parameters' in source:
                    optimized_source['parameters'] = source['parameters']
                # Calculated sources don't need unit (function output is in Fleeti unit)
            else:
                # Direct provider sources: ALWAYS include unit (use "none" if unitless)
                source_unit = None
                if idx < len(provider_field_units) and provider_field_units[idx]:
                    source_unit = normalize_unit(provider_field_units[idx], default_to_none=True)
                elif 'unit' in source:
                    source_unit = normalize_unit(source['unit'], default_to_none=True)
                elif fleeti_unit:
                    source_unit = normalize_unit(fleeti_unit, default_to_none=True)
                else:
                    source_unit = "none"
                
                optimized_source['unit'] = source_unit
            
            optimized_sources.append(optimized_source)
        
        optimized['sources'] = optimized_sources
        
        # Rule 8: Add unit at top level (from Fleeti Unit)
        # CRITICAL: ALWAYS include unit for direct/prioritized mappings (regardless of data_type)
        # Use "none" for unitless fields, but always include the unit field
        # Fallback: If fleeti_unit is empty, use first provider field unit
        if not fleeti_unit and provider_field_unit:
            provider_field_units_list = [u.strip() for u in provider_field_unit.split(',')]
            if provider_field_units_list and provider_field_units_list[0]:
                fleeti_unit = provider_field_units_list[0]
        top_unit = normalize_unit(fleeti_unit, default_to_none=True) if fleeti_unit else "none"
        optimized['unit'] = top_unit
    
    elif mapping_type == 'calculated':
        # Keep calculation_type and function
        if 'calculation_type' in computation_json:
            optimized['calculation_type'] = computation_json['calculation_type']
        if 'function' in computation_json:
            optimized['function'] = computation_json['function']
        
        # Keep parameters
        if 'parameters' in computation_json:
            optimized['parameters'] = computation_json['parameters']
        
        # Rule 6: Omit dependencies when redundant with parameters.fleeti
        # (dependencies field is not included in optimized output)
        
        # Rule 8: Add unit at top level for all calculated mappings
        top_unit = normalize_unit(fleeti_unit, default_to_none=True) if fleeti_unit else "none"
        optimized['unit'] = top_unit
    
    elif mapping_type == 'transformed':
        # Keep transformation and service_fields
        if 'transformation' in computation_json:
            optimized['transformation'] = computation_json['transformation']
        if 'service_fields' in computation_json:
            optimized['service_fields'] = computation_json['service_fields']
        
        # Rule 8: Add unit at top level for all transformed mappings
        top_unit = normalize_unit(fleeti_unit, default_to_none=True) if fleeti_unit else "none"
        optimized['unit'] = top_unit
    
    elif mapping_type == 'io_mapped':
        # Keep default_source and installation_metadata
        if 'default_source' in computation_json:
            optimized['default_source'] = computation_json['default_source']
        if 'installation_metadata' in computation_json:
            optimized['installation_metadata'] = computation_json['installation_metadata']
        
        # Rule 8: Add unit at top level for all io_mapped mappings
        top_unit = normalize_unit(fleeti_unit, default_to_none=True) if fleeti_unit else "none"
        optimized['unit'] = top_unit
    
    return optimized


def format_yaml_with_comments(yaml_dict: Dict, field_path: str, computation_approach: str) -> str:
    """
    Generate YAML string with comments for Field Path and Computation Approach.
    
    Since PyYAML doesn't support comments natively, we'll add them as separate
    dictionary entries and format manually, or use a workaround.
    
    Actually, we'll use PyYAML to generate the YAML and then inject comments.
    """
    # Generate base YAML
    yaml_str = yaml.dump(
        yaml_dict,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        indent=2,
        width=1000  # Prevent line wrapping
    )
    
    # Add comments before the mapping entry
    # Find the first key in the mapping (field name) and add comments before it
    lines = yaml_str.split('\n')
    
    # Find the indentation level of the first field
    indent_level = 0
    for line in lines:
        if line.strip() and not line.strip().startswith('#'):
            indent_level = len(line) - len(line.lstrip())
            break
    
    # Build the commented version
    # Since we're working with a nested structure, we need to find where to insert comments
    # For simplicity, we'll prepend comments to the entire field definition
    comment_lines = []
    if field_path:
        comment_lines.append(f"    # Field Path: {field_path}")
    if computation_approach:
        # Multi-line computation approach - split and comment each line
        for line in computation_approach.strip().split('\n'):
            comment_lines.append(f"    # {line}")
    
    # This is tricky - we need to insert comments before each field's content
    # A better approach: add comments as strings in a special way, or post-process
    # For now, we'll use a simpler approach and add comments at the field level
    
    return yaml_str


def extract_fleeti_dependencies(computation_json: Dict) -> List[str]:
    """Extract Fleeti field dependencies from parameters.fleeti."""
    deps = set()

    def add_from_params(params: Optional[Dict]) -> None:
        if not params:
            return
        fleeti = params.get('fleeti')
        if isinstance(fleeti, list):
            for name in fleeti:
                if name:
                    deps.add(name)

    # Top-level parameters
    add_from_params(computation_json.get('parameters'))

    # Source-level parameters (for prioritized mappings with calculated sources)
    for source in computation_json.get('sources', []):
        if source.get('type') == 'calculated' or 'parameters' in source:
            add_from_params(source.get('parameters'))

    return sorted(deps)


def process_csv_row(row: Dict, provider: str) -> Optional[tuple]:
    """Process a single CSV row and return (field_name, yaml_entry_dict, comments, deps)."""
    # Filter by status
    status = row.get('Status', '').strip().lower()
    if status not in ['planned', 'active']:
        return None
    
    # Extract field name
    fleeti_field = row.get('Fleeti Field', '').strip()
    if not fleeti_field:
        return None
    
    field_name = extract_field_name(fleeti_field)
    if not field_name:
        return None
    
    # Get computation structure JSON
    computation_json_str = row.get('Computation Structure JSON', '').strip()
    if not computation_json_str:
        print(f"Warning: No Computation Structure JSON for field {field_name}, skipping")
        return None
    
    computation_json = parse_json_field(computation_json_str)
    if not computation_json:
        print(f"Warning: Failed to parse Computation Structure JSON for field {field_name}, skipping")
        return None
    
    # Get units
    # Get Fleeti Unit - fallback to Fleeti Field Unit if empty (CSV column mismatch fix)
    fleeti_unit = row.get('Fleeti Unit', '').strip()
    if not fleeti_unit:
        # Fallback: Use Fleeti Field Unit if Fleeti Unit is empty
        fleeti_unit = row.get('Fleeti Field Unit', '').strip()
    provider_field_unit = row.get('Provider Field Unit', '').strip()
    
    # Get data type (needed for unit handling rules)
    data_type = row.get('Fleeti Field Data Type', '').strip()
    
    # Apply optimization rules
    optimized = apply_optimization_rules(
        computation_json,
        provider,
        provider_field_unit,
        fleeti_unit,
        data_type
    )
    
    # Add additional fields
    if data_type:
        optimized['data_type'] = data_type
    
    error_handling = row.get('Error Handling', '').strip()
    if error_handling:
        optimized['error_handling'] = error_handling
    else:
        optimized['error_handling'] = 'return_null'
    
    # Get field path and computation approach for comments
    field_path = row.get('Fleeti Field Path', '').strip()
    computation_approach = row.get('Computation Approach', '').strip()

    deps = extract_fleeti_dependencies(computation_json)

    return (field_name, optimized, field_path, computation_approach, deps)


def order_mappings_by_dependencies(entries: List[Dict]) -> List[str]:
    """Topologically sort mappings by parameters.fleeti dependencies."""
    name_to_entry = {e['name']: e for e in entries}
    order_index = {e['name']: e['order'] for e in entries}

    deps_map = {}
    reverse_deps = {}
    in_degree = {}

    for name, entry in name_to_entry.items():
        deps = [d for d in entry['deps'] if d in name_to_entry and d != name]
        deps_map[name] = deps
        in_degree[name] = len(deps)
        for dep in deps:
            reverse_deps.setdefault(dep, []).append(name)

    available = [name for name, deg in in_degree.items() if deg == 0]
    available.sort(key=lambda n: order_index[n])

    ordered = []
    while available:
        name = available.pop(0)
        ordered.append(name)
        for dependent in reverse_deps.get(name, []):
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                insert_at = 0
                while insert_at < len(available) and order_index[available[insert_at]] <= order_index[dependent]:
                    insert_at += 1
                available.insert(insert_at, dependent)

    if len(ordered) != len(entries):
        # Cycle or missing dependency; fall back to original CSV order
        print("Warning: Dependency ordering incomplete (cycle detected). Falling back to CSV order.")
        return [e['name'] for e in sorted(entries, key=lambda e: e['order'])]

    return ordered


def generate_yaml_config(csv_path: Path) -> Path:
    """Generate YAML configuration from CSV file."""
    print(f"Reading CSV file: {csv_path}")
    
    # Read CSV with UTF-8-sig encoding (handles BOM)
    with open(csv_path, 'r', encoding='utf-8-sig', newline='') as f:
        # Use csv.DictReader to handle multi-line fields
        reader = csv.DictReader(f)
        rows = list(reader)
    
    if not rows:
        raise ValueError("CSV file is empty or has no data rows")
    
    # Determine provider from first row (assuming all rows have same provider)
    provider = rows[0].get('Provider', 'navixy').strip().lower()
    if not provider:
        provider = 'navixy'
    
    # Process rows
    mappings = OrderedDict()
    comments_dict = {}  # Store comments separately
    entries = []
    
    for row in rows:
        result = process_csv_row(row, provider)
        if result:
            field_name, yaml_entry, field_path, computation_approach, deps = result
            entries.append({
                'name': field_name,
                'yaml_entry': yaml_entry,
                'field_path': field_path,
                'computation_approach': computation_approach,
                'deps': deps,
                'order': len(entries)
            })

    ordered_names = order_mappings_by_dependencies(entries)
    entries_by_name = {e['name']: e for e in entries}
    for name in ordered_names:
        entry = entries_by_name[name]
        mappings[name] = entry['yaml_entry']
        comments_dict[name] = {
            'field_path': entry['field_path'],
            'computation_approach': entry['computation_approach']
        }
    
    # Build final YAML structure
    yaml_config = OrderedDict([
        ('version', '1.0.0'),
        ('provider', provider),
        ('mappings', mappings)
    ])
    
    # Generate output filename with date
    today = datetime.now().strftime('%Y-%m-%d')
    output_filename = f"{provider}-mapping-{today}.yaml"
    output_path = OUTPUT_DIR / output_filename
    
    # Generate YAML string with comments
    # Since PyYAML doesn't support comments well, we'll generate the YAML
    # and then manually add comments by post-processing
    yaml_lines = []
    yaml_lines.append('version: "1.0.0"')
    yaml_lines.append(f'provider: "{provider}"')
    yaml_lines.append('')
    yaml_lines.append('mappings:')
    
    # Process each mapping with comments
    for field_name, yaml_entry in mappings.items():
        # Add field name
        yaml_lines.append(f'  {field_name}:')
        
        # Generate YAML for the entry (without the field name)
        entry_yaml = yaml.dump(
            yaml_entry,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
            indent=2,
            width=1000
        )
        
        # Indent all lines by 4 spaces (2 for mappings level + 2 for field level)
        for line in entry_yaml.split('\n'):
            if line.strip():  # Skip empty lines
                yaml_lines.append('    ' + line)
        
        # Add comments at the end (after all properties)
        comments = comments_dict.get(field_name, {})
        if comments.get('field_path'):
            yaml_lines.append(f'    # Field Path: {comments["field_path"]}')
        
        if comments.get('computation_approach'):
            comp_lines = comments['computation_approach'].split('\n')
            for i, line in enumerate(comp_lines):
                if i == 0:
                    yaml_lines.append(f'    # Computation Approach: {line}')
                else:
                    yaml_lines.append(f'    # {line}')
        
        yaml_lines.append('')  # Empty line between fields
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(yaml_lines))
    
    print(f"Generated YAML file: {output_path}")
    print(f"Processed {len(mappings)} mappings")
    
    return output_path


def main():
    """Main entry point."""
    # Find most recent CSV file
    csv_path = find_most_recent_csv()
    if not csv_path:
        raise FileNotFoundError(
            f"No CSV file found matching pattern 'Mapping Fields (db) *.csv' in {EXPORT_DIR}"
        )
    
    print(f"Using CSV file: {csv_path}")
    
    # Generate YAML
    output_path = generate_yaml_config(csv_path)
    print(f"\nSuccess! Generated YAML configuration at: {output_path}")


if __name__ == '__main__':
    main()

