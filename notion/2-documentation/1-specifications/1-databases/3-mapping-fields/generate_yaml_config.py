#!/usr/bin/env python3
"""
Generate YAML configuration file from Mapping Fields Database CSV.
Follows the specifications in YAML_GENERATION_SPEC.md
"""

import csv
import json
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# Input file
MAPPING_FIELDS_CSV = Path(__file__).parent / "Mapping-Fields-Navixy-2025-01-16.csv"

# Output file
OUTPUT_YAML = Path(__file__).parent / "navixy-mapping.yaml"


def normalize_unit(unit: str) -> Optional[str]:
    """Normalize unit for comparison (per spec)"""
    if not unit or unit.strip() in ['-', 'none', '']:
        return None
    
    unit_lower = unit.lower().strip()
    
    # Unit equivalence mapping
    equivalence = {
        'm': 'meters', 'meter': 'meters', 'meters': 'meters',
        'km': 'kilometers', 'kilometer': 'kilometers', 'kilometers': 'kilometers',
        'deg': 'degrees', 'degree': 'degrees', 'degrees': 'degrees',
        '°c': 'celsius', 'celsius': 'celsius', 'c': 'celsius',
        '°f': 'fahrenheit', 'fahrenheit': 'fahrenheit', 'f': 'fahrenheit',
        'km/h': 'km/h', 'kmh': 'km/h', 'kph': 'km/h',
        'm/s': 'm/s', 'mps': 'm/s', 'meters_per_second': 'm/s',
        'mph': 'mph', 'miles_per_hour': 'mph',
    }
    
    return equivalence.get(unit_lower, unit_lower)


def should_generate_unit_conversion(provider_unit: str, fleeti_unit: str) -> bool:
    """Determine if unit conversion should be generated (per spec)"""
    if not provider_unit or not fleeti_unit:
        return False
    
    provider_normalized = normalize_unit(provider_unit)
    fleeti_normalized = normalize_unit(fleeti_unit)
    
    # Skip if units are empty/unknown
    if not provider_normalized or not fleeti_normalized:
        return False
    
    # Skip if units are equivalent or same
    if provider_normalized == fleeti_normalized:
        return False
    
    return True


def parse_dependencies(deps_str: str) -> List[str]:
    """Parse dependencies string (comma-separated field names)"""
    if not deps_str or not deps_str.strip():
        return []
    
    # Split by comma and clean up
    deps = [d.strip() for d in deps_str.split(',')]
    return [d for d in deps if d]


def parse_priority_json(priority_json_str: str) -> List[Dict]:
    """Parse Priority JSON string"""
    if not priority_json_str or not priority_json_str.strip():
        return []
    
    try:
        return json.loads(priority_json_str)
    except json.JSONDecodeError:
        return []


def parse_provider_fields(fields_str: str) -> List[str]:
    """Parse comma-separated provider fields"""
    if not fields_str or not fields_str.strip():
        return []
    
    return [f.strip() for f in fields_str.split(',') if f.strip()]


def parse_provider_paths(paths_str: str) -> List[str]:
    """Parse comma-separated provider field paths"""
    if not paths_str or not paths_str.strip():
        return []
    
    return [p.strip() for p in paths_str.split(',') if p.strip()]


def parse_provider_units(units_str: str) -> List[str]:
    """Parse comma-separated provider units"""
    if not units_str or not units_str.strip():
        return []
    
    return [u.strip() for u in units_str.split(',') if u.strip()]


def parse_function_parameters(params_str: str) -> Optional[Dict[str, str]]:
    """Parse Function Parameters (JSON or structured text)"""
    if not params_str or not params_str.strip():
        return None
    
    # Try JSON first
    try:
        return json.loads(params_str)
    except json.JSONDecodeError:
        pass
    
    # Try structured text format: param_name: "fleeti_field_name"
    params = {}
    for line in params_str.split('\n'):
        line = line.strip()
        if ':' in line:
            parts = line.split(':', 1)
            if len(parts) == 2:
                param_name = parts[0].strip()
                field_name = parts[1].strip().strip('"\'')
                if param_name and field_name:
                    params[param_name] = field_name
    
    return params if params else None


def build_dependency_graph(mappings: List[Dict]) -> Tuple[Dict[str, List[str]], Dict[str, Dict]]:
    """Build dependency graph for topological sort"""
    graph = defaultdict(list)
    mapping_dict = {}
    
    for mapping in mappings:
        field_name = mapping['Fleeti Field']
        mapping_dict[field_name] = mapping
        
        if mapping['Mapping Type'] in ['calculated', 'transformed']:
            deps = parse_dependencies(mapping.get('Dependencies', ''))
            graph[field_name] = deps
    
    return graph, mapping_dict


def topological_sort(mappings: List[Dict]) -> List[Dict]:
    """Sort mappings by dependency order"""
    graph, mapping_dict = build_dependency_graph(mappings)
    
    # Build reverse graph for topological sort
    in_degree = defaultdict(int)
    for field_name in graph:
        in_degree[field_name] = len(graph[field_name])
    
    # Add all fields to in_degree
    for mapping in mappings:
        field_name = mapping['Fleeti Field']
        if field_name not in in_degree:
            in_degree[field_name] = 0
    
    # Process in order: direct, prioritized, then calculated/transformed
    sorted_mappings = []
    processed = set()
    
    # First: direct mappings (no dependencies)
    for mapping in mappings:
        if mapping['Mapping Type'] == 'direct':
            sorted_mappings.append(mapping)
            processed.add(mapping['Fleeti Field'])
    
    # Second: prioritized mappings (no dependencies)
    for mapping in mappings:
        if mapping['Mapping Type'] == 'prioritized' and mapping['Fleeti Field'] not in processed:
            sorted_mappings.append(mapping)
            processed.add(mapping['Fleeti Field'])
    
    # Third: calculated/transformed mappings (with dependencies)
    remaining = [m for m in mappings if m['Fleeti Field'] not in processed]
    
    while remaining:
        progress = False
        for mapping in remaining[:]:
            field_name = mapping['Fleeti Field']
            deps = graph.get(field_name, [])
            
            # Check if all dependencies are processed
            if all(dep in processed for dep in deps):
                sorted_mappings.append(mapping)
                processed.add(field_name)
                remaining.remove(mapping)
                progress = True
        
        if not progress:
            # Circular dependency or missing dependency - add remaining
            sorted_mappings.extend(remaining)
            break
    
    return sorted_mappings


def generate_direct_mapping(mapping: Dict) -> Dict:
    """Generate YAML for direct mapping"""
    field_name = mapping['Fleeti Field']
    field_path = mapping['Fleeti Field Path']
    provider_path = mapping['Provider Field Paths'].strip()
    fleeti_unit = mapping.get('Fleeti Unit', '').strip()
    fleeti_data_type = mapping.get('Fleeti Data Type', '').strip()
    
    yaml_entry = {
        'type': 'direct',
        'source': provider_path,
    }
    
    if fleeti_unit:
        yaml_entry['unit'] = fleeti_unit
    
    if fleeti_data_type:
        yaml_entry['data_type'] = fleeti_data_type
    
    # Add optional fields
    if mapping.get('Default Value', '').strip():
        yaml_entry['default'] = mapping['Default Value'].strip()
    
    error_handling = mapping.get('Error Handling', '').strip()
    if error_handling:
        yaml_entry['error_handling'] = error_handling
    else:
        yaml_entry['error_handling'] = 'return_null'  # Default for direct
    
    # Unit conversion (only if units differ)
    provider_unit = mapping.get('Provider Unit', '').strip()
    unit_conversion = mapping.get('Unit Conversion', '').strip()
    
    if unit_conversion:
        yaml_entry['unit_conversion'] = unit_conversion
    elif should_generate_unit_conversion(provider_unit, fleeti_unit):
        # Auto-generate conversion (simplified - would need conversion table)
        pass  # Skip auto-generation per spec (should be manually specified)
    
    # Add Field Path as comment
    yaml_entry['_comment'] = f'# Field Path: {field_path}'
    
    return yaml_entry


def generate_prioritized_mapping(mapping: Dict) -> Dict:
    """Generate YAML for prioritized mapping"""
    field_name = mapping['Fleeti Field']
    field_path = mapping['Fleeti Field Path']
    priority_json = mapping.get('Priority JSON', '').strip()
    fleeti_unit = mapping.get('Fleeti Unit', '').strip()
    fleeti_data_type = mapping.get('Fleeti Data Type', '').strip()
    
    # Parse priority JSON
    priorities = parse_priority_json(priority_json)
    
    # Parse provider fields, paths, and units
    provider_fields = parse_provider_fields(mapping.get('Provider Fields', ''))
    provider_paths = parse_provider_paths(mapping.get('Provider Field Paths', ''))
    provider_units = parse_provider_units(mapping.get('Provider Unit', ''))
    
    # Build sources array
    sources = []
    for priority_entry in priorities:
        field = priority_entry.get('field', '')
        priority = priority_entry.get('priority', 0)
        
        # Find matching path
        path = ''
        if field in provider_fields:
            idx = provider_fields.index(field)
            if idx < len(provider_paths):
                path = provider_paths[idx]
        else:
            # Fallback: use field as path
            path = field
        
        sources.append({
            'priority': priority,
            'field': field,
            'path': path
        })
    
    # Sort by priority
    sources.sort(key=lambda x: x['priority'])
    
    yaml_entry = {
        'type': 'prioritized',
        'sources': sources,
    }
    
    if fleeti_unit:
        yaml_entry['unit'] = fleeti_unit
    
    if fleeti_data_type:
        yaml_entry['data_type'] = fleeti_data_type
    
    # Error handling (default: use_fallback for prioritized)
    error_handling = mapping.get('Error Handling', '').strip()
    if error_handling:
        yaml_entry['error_handling'] = error_handling
    else:
        yaml_entry['error_handling'] = 'use_fallback'
    
    # Add Field Path as comment
    yaml_entry['_comment'] = f'# Field Path: {field_path}'
    
    return yaml_entry


def generate_calculated_mapping(mapping: Dict) -> Dict:
    """Generate YAML for calculated mapping"""
    field_name = mapping['Fleeti Field']
    field_path = mapping['Fleeti Field Path']
    calculation_type = mapping.get('Calculation Type', '').strip()
    computation_approach = mapping.get('Computation Approach', '').strip()
    fleeti_data_type = mapping.get('Fleeti Data Type', '').strip()
    
    yaml_entry = {
        'type': 'calculated',
    }
    
    # All calculated fields use function_reference type
    if not calculation_type:
        calculation_type = 'function_reference'  # Default per spec
    
    yaml_entry['calculation_type'] = calculation_type
    
    if calculation_type == 'function_reference':
        # Function reference type
        backend_function = mapping.get('Backend Function Name', '').strip()
        
        # Auto-extract function name if missing
        if not backend_function:
            # Try to infer from field name
            field_name = mapping['Fleeti Field']
            # Remove category prefix (location_, motion_, etc.)
            field_part = field_name
            for prefix in ['location_', 'motion_', 'fuel_', 'power_', 'status_']:
                if field_part.startswith(prefix):
                    field_part = field_part[len(prefix):]
                    break
            
            # Convert to function name: location_cardinal_direction -> derive_cardinal_direction
            # or geocode_location, etc.
            if 'cardinal' in field_part:
                backend_function = 'derive_cardinal_direction'
            elif 'geocoded' in field_part or 'address' in field_part:
                backend_function = 'geocode_location'
            elif 'last_changed' in field_part:
                backend_function = 'calculate_last_changed_at'
            else:
                # Default: derive_{field_part}
                backend_function = f'derive_{field_part}'
        
        if backend_function:
            yaml_entry['function'] = backend_function
        
        # Function parameters
        function_params = parse_function_parameters(mapping.get('Function Parameters', ''))
        if not function_params:
            # Auto-generate parameters from dependencies if missing
            deps = parse_dependencies(mapping.get('Dependencies', ''))
            if deps:
                function_params = {}
                for dep in deps:
                    # Use last part of field name as parameter name
                    param_name = dep.split('_')[-1]
                    # Handle duplicates
                    if param_name in function_params:
                        param_name = dep.replace('location_', '').replace('_', '_')
                    function_params[param_name] = dep
        
        if function_params:
            yaml_entry['parameters'] = function_params
        
        # Computation approach as comment (not formula field)
        if computation_approach:
            yaml_entry['_computation_approach'] = computation_approach
        
        # Description from notes
        notes = mapping.get('Notes', '').strip()
        if notes:
            yaml_entry['_description'] = notes
        
        # Dependencies
        deps = parse_dependencies(mapping.get('Dependencies', ''))
        if deps:
            yaml_entry['dependencies'] = deps
    
    elif calculation_type == 'formula':
        # Formula type (kept for future use)
        # Dependencies
        deps = parse_dependencies(mapping.get('Dependencies', ''))
        if deps:
            yaml_entry['dependencies'] = deps
    
    if fleeti_data_type:
        yaml_entry['data_type'] = fleeti_data_type
    
    # Error handling (default: return_null for calculated)
    error_handling = mapping.get('Error Handling', '').strip()
    if error_handling:
        yaml_entry['error_handling'] = error_handling
    else:
        yaml_entry['error_handling'] = 'return_null'
    
    # Add Field Path as comment
    yaml_entry['_comment'] = f'# Field Path: {field_path}'
    
    return yaml_entry


def generate_yaml_entry(mapping: Dict) -> Tuple[str, Dict]:
    """Generate YAML entry for a mapping"""
    mapping_type = mapping['Mapping Type']
    field_name = mapping['Fleeti Field']  # Use Field Name as key (stable identifier)
    
    if mapping_type == 'direct':
        yaml_data = generate_direct_mapping(mapping)
    elif mapping_type == 'prioritized':
        yaml_data = generate_prioritized_mapping(mapping)
    elif mapping_type == 'calculated':
        yaml_data = generate_calculated_mapping(mapping)
    elif mapping_type == 'transformed':
        # Transformed mapping (not in CSV yet, but handle for future)
        yaml_data = {
            'type': 'transformed',
            'transformation': mapping.get('Transformation Rule', '').strip(),
            'service_fields': parse_dependencies(mapping.get('Service Integration', '')),
            'data_type': mapping.get('Fleeti Data Type', '').strip(),
            '_comment': f'Field Path: {mapping["Fleeti Field Path"]}'
        }
    elif mapping_type == 'io_mapped':
        # I/O mapped (not in CSV yet, but handle for future)
        io_config = mapping.get('I/O Mapping Config', '').strip()
        try:
            io_dict = json.loads(io_config) if io_config else {}
            yaml_data = {
                'type': 'io_mapped',
                'default_source': io_dict.get('default_source', ''),
                'installation_metadata': io_dict.get('installation_metadata', ''),
                'data_type': mapping.get('Fleeti Data Type', '').strip(),
                '_comment': f'Field Path: {mapping["Fleeti Field Path"]}'
            }
        except json.JSONDecodeError:
            yaml_data = {'type': 'io_mapped', '_comment': f'Field Path: {mapping["Fleeti Field Path"]}'}
    else:
        # Unknown type - skip
        return None, None
    
    return field_name, yaml_data


def format_yaml_with_comments(data: Dict) -> str:
    """Format YAML with comments (handles _comment, _implementation, _description keys)"""
    yaml_str = yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    # Replace comment markers with actual YAML comments
    lines = yaml_str.split('\n')
    formatted_lines = []
    
    for i, line in enumerate(lines):
        # Handle _comment
        if '_comment:' in line:
            comment_value = line.split(':', 1)[1].strip().strip('"\'')
            formatted_lines.append(f'    # Field Path: {comment_value}')
        elif '_implementation:' in line:
            impl_value = line.split(':', 1)[1].strip().strip('"\'')
            formatted_lines.append(f'    # Implementation: {impl_value}')
        elif '_description:' in line:
            desc_value = line.split(':', 1)[1].strip().strip('"\'')
            formatted_lines.append(f'    # Description: {desc_value}')
        elif line.strip().startswith('_'):
            # Skip other underscore-prefixed keys
            continue
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)


def read_csv_file(file_path: Path) -> List[Dict]:
    """Read CSV file and return list of dictionaries"""
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        return list(reader)


def main():
    """Main function to generate YAML configuration"""
    print(f"Reading Mapping Fields CSV: {MAPPING_FIELDS_CSV}")
    mappings = read_csv_file(MAPPING_FIELDS_CSV)
    
    if not mappings:
        print("Error: No mappings found in CSV!")
        return
    
    print(f"Found {len(mappings)} mappings")
    
    # Filter active mappings only (skip deprecated)
    active_mappings = [
        m for m in mappings 
        if m.get('Status', '').strip().lower() in ['active', 'planned', 'under_review']
    ]
    
    print(f"Processing {len(active_mappings)} active mappings")
    
    # Sort by dependency order
    sorted_mappings = topological_sort(active_mappings)
    
    # Generate YAML entries
    yaml_mappings = {}
    for mapping in sorted_mappings:
        field_name, yaml_data = generate_yaml_entry(mapping)
        if field_name and yaml_data:
            yaml_mappings[field_name] = yaml_data
    
    # Build final YAML structure
    provider = mappings[0].get('Provider', 'navixy') if mappings else 'navixy'
    
    yaml_config = {
        'version': '1.0.0',
        'provider': provider,
        'mappings': yaml_mappings
    }
    
    # Write YAML file
    print(f"\nWriting YAML to: {OUTPUT_YAML}")
    
    # Custom YAML formatting with comments
    yaml_output = f"version: \"{yaml_config['version']}\"\n"
    yaml_output += f"provider: \"{yaml_config['provider']}\"\n"
    yaml_output += "mappings:\n"
    
    for field_name, mapping_data in yaml_mappings.items():
        yaml_output += f"  {field_name}:\n"
        
        # Extract comments
        comment = mapping_data.pop('_comment', '')
        computation_approach = mapping_data.pop('_computation_approach', '')
        description = mapping_data.pop('_description', '')
        
        # Write mapping data
        mapping_yaml = yaml.dump(mapping_data, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        # Indent mapping data
        for line in mapping_yaml.split('\n'):
            if line.strip():
                yaml_output += f"    {line}\n"
        
        # Add comments (ensure they're properly formatted as YAML comments)
        if comment:
            # Comment should already be formatted as "# Field Path: ..."
            yaml_output += f"    {comment}\n"
        
        # Add computation approach as comments (multi-line support)
        if computation_approach:
            comp_lines = computation_approach.split('\n')
            for i, comp_line in enumerate(comp_lines):
                comp_line = comp_line.strip()
                if comp_line:
                    if i == 0:
                        yaml_output += f"    # Computation Approach: {comp_line}\n"
                    else:
                        yaml_output += f"    # {comp_line}\n"
        
        if description:
            # Split description into multiple comment lines if needed
            desc_lines = description.split('\n')
            for desc_line in desc_lines:
                if desc_line.strip():
                    yaml_output += f"    # Description: {desc_line.strip()}\n"
        
        yaml_output += "\n"
    
    with open(OUTPUT_YAML, 'w', encoding='utf-8') as f:
        f.write(yaml_output)
    
    print("YAML configuration generated successfully!")
    print(f"   Generated {len(yaml_mappings)} mappings")
    
    # Print summary
    mapping_types = {}
    for mapping in sorted_mappings:
        mtype = mapping['Mapping Type']
        mapping_types[mtype] = mapping_types.get(mtype, 0) + 1
    
    print("\nMapping type summary:")
    for mtype, count in sorted(mapping_types.items()):
        print(f"  - {mtype}: {count}")


if __name__ == '__main__':
    main()

