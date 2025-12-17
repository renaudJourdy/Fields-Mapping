#!/usr/bin/env python3
"""
Generate Mapping Fields Database CSV from Provider Fields and Fleeti Fields exports.
Follows the specifications in docs/prompts/GENERATE_MAPPING_FIELDS_PROMPT.md
"""

import csv
import json
import re
from datetime import date
from pathlib import Path

# Input files
PROVIDER_FIELDS_CSV = Path(__file__).parent.parent / "1-provider-fields" / "export" / "Provider Field (db) 12-16-25.csv"
FLEETI_FIELDS_CSV = Path(__file__).parent.parent / "2-fleeti-fields" / "export" / "Fleeti Fields (db) 12-16-25.csv"

# Output file
OUTPUT_CSV = Path(__file__).parent / "Mapping-Fields-Navixy-2025-01-16.csv"

def extract_field_name_from_notion_link(link_text):
    """Extract field name from Notion link format: 'field_name (https://...)'"""
    if not link_text or not link_text.strip():
        return []
    
    # Handle comma-separated multiple fields
    fields = []
    for part in link_text.split(','):
        part = part.strip()
        # Extract field name before opening parenthesis
        match = re.match(r'^([^(]+)', part)
        if match:
            field_name = match.group(1).strip()
            if field_name:
                fields.append(field_name)
    
    return fields

def get_provider_field_paths(provider_field_names, provider_lookup):
    """Get provider field paths from provider field names"""
    paths = []
    for name in provider_field_names:
        provider_field = provider_lookup.get(name)
        if provider_field:
            path = provider_field.get('Field Path', name)
            paths.append(path)
        else:
            paths.append(name)  # Fallback to name if not found
    return paths

def get_provider_units(provider_field_names, provider_lookup):
    """Get provider units from provider field names"""
    units = []
    for name in provider_field_names:
        provider_field = provider_lookup.get(name)
        if provider_field:
            unit = provider_field.get('Unit', '').strip()
            units.append(unit if unit else '')
        else:
            units.append('')
    return units

def normalize_unit(unit):
    """Normalize unit for comparison (per updated spec)"""
    if not unit or unit in ['-', 'none', '']:
        return None
    unit_lower = unit.lower().strip()
    # Unit equivalence mapping
    equivalence = {
        'm': 'meters', 'meter': 'meters',
        'deg': 'degrees', 'degree': 'degrees',
        'km/h': 'km/h', 'kmh': 'km/h', 'kph': 'km/h',
        'm/s': 'm/s', 'mps': 'm/s',
        '°c': 'celsius', 'celsius': 'celsius', 'c': 'celsius',
        '°f': 'fahrenheit', 'fahrenheit': 'fahrenheit', 'f': 'fahrenheit',
    }
    return equivalence.get(unit_lower, unit_lower)

def auto_generate_unit_conversion(provider_units, fleeti_unit):
    """Auto-generate unit conversion rule if units differ (per updated spec)"""
    if not fleeti_unit or not provider_units:
        return ''
    
    # Normalize units
    fleeti_normalized = normalize_unit(fleeti_unit)
    provider_normalized = normalize_unit(provider_units[0] if provider_units else None)
    
    # Skip if units are equivalent or same (per updated spec)
    if not provider_normalized or not fleeti_normalized:
        return ''  # Skip for empty/unknown units
    
    if provider_normalized == fleeti_normalized:
        return ''  # Skip for same/equivalent units
    
    # Units differ - return empty (conversion should be manually specified)
    # The updated spec says to skip unit_conversion generation
    return ''

def extract_dependencies_from_notion_links(links_text):
    """Extract dependency field names from Dependencies column"""
    if not links_text or not links_text.strip():
        return []
    
    # Extract field names from Notion links
    dependencies = []
    # Pattern: field_name (https://...)
    pattern = r'([a-z_][a-z0-9_]*(?:_[a-z0-9_]*)*)\s*\(https://'
    matches = re.findall(pattern, links_text)
    return matches

def keep_dependencies_as_field_names(dependency_names, fleeti_lookup):
    """Keep dependencies as Field Names (stable identifiers), not convert to Field Paths.
    
    Field Names are stable identifiers used in YAML. Backend resolves Field Name → Field Path
    at runtime using a lookup table. This makes YAML configurations resilient to Field Path changes.
    """
    # Validate that all dependency names exist in lookup, but return names (not paths)
    validated_names = []
    for dep_name in dependency_names:
        dep_field = fleeti_lookup.get(dep_name)
        if dep_field:
            # Field exists - use Field Name (stable identifier)
            validated_names.append(dep_name)
        else:
            # Field not found - still use name (will be caught during validation)
            validated_names.append(dep_name)
    return validated_names

def parse_priority_order(computation_approach, provider_fields):
    """Parse priority order from Computation Approach column"""
    if not computation_approach:
        # Fallback: use order from provider fields list
        return [(i+1, field) for i, field in enumerate(provider_fields)]
    
    # Check for > symbol indicating priority order
    if '>' in computation_approach:
        # Parse pattern: field1>field2>field3
        priority_fields = [f.strip() for f in computation_approach.split('>')]
        # Match with actual provider fields
        priorities = []
        for i, priority_field in enumerate(priority_fields):
            # Find matching provider field (exact match or contains)
            for pf in provider_fields:
                if priority_field == pf or pf.endswith(priority_field) or priority_field in pf:
                    priorities.append((i+1, pf))
                    break
        
        # If we didn't match all, fill in remaining
        if len(priorities) < len(provider_fields):
            matched_fields = {p[1] for p in priorities}
            remaining = [pf for pf in provider_fields if pf not in matched_fields]
            for pf in remaining:
                priorities.append((len(priorities)+1, pf))
        
        return priorities
    
    # Fallback: use order from provider fields list
    return [(i+1, field) for i, field in enumerate(provider_fields)]

def determine_calculation_type(computation_approach, fleeti_name):
    """Determine calculation type from Computation Approach.
    
    Returns 'formula' for simple parseable mathematical expressions.
    Returns 'function_reference' for all other computation approaches.
    Returns None if computation_approach is empty (invalid mapping).
    """
    if not computation_approach or not computation_approach.strip():
        return None  # Cannot determine type without computation approach
    
    computation_lower = computation_approach.lower()
    
    # Check for parseable formulas (simple math expressions)
    # Must be a mathematical expression, not a sentence
    if re.match(r'^[a-zA-Z0-9_\.\s\+\-\*\/\(\)]+$', computation_approach.strip()):
        # Check if it's a simple expression without complex logic
        # Exclude sentences (containing common words like "use", "convert", "from")
        if ('=' not in computation_approach and 
            'if' not in computation_lower and
            'use' not in computation_lower and
            'convert' not in computation_lower and
            'from' not in computation_lower and
            'api' not in computation_lower and
            len(computation_approach.split()) < 10):  # Short expressions only
            return 'formula'
    
    # All other calculated fields use function_reference type
    return 'function_reference'

def extract_backend_function_name(fleeti_name, fleeti_path, computation_approach, calculation_type):
    """Extract backend function name for function_reference type"""
    computation_lower = computation_approach.lower() if computation_approach else ''
    
    # Try to extract from computation approach
    # Example: "Derived from location.heading" -> "derive_cardinal_direction"
    if 'derive' in computation_lower or 'derived' in computation_lower:
        # Convert field name to function name: location_cardinal_direction -> derive_cardinal_direction
        # Remove category prefix if present
        field_part = fleeti_name
        for prefix in ['location_', 'motion_', 'fuel_', 'power_', 'status_']:
            if field_part.startswith(prefix):
                field_part = field_part[len(prefix):]
                break
        
        # Convert to snake_case function name
        function_name = f"derive_{field_part}"
        return function_name
    
    # Try to infer from field path
    # location.cardinal_direction -> derive_cardinal_direction
    if '.' in fleeti_path:
        field_part = fleeti_path.split('.')[-1]
        function_name = f"derive_{field_part}"
        return function_name
    
    # Fallback: use field name with derive prefix
    return f"derive_{fleeti_name}"

def extract_function_parameters(dependency_names, computation_approach, calculation_type):
    """Extract structured parameter mapping for function_reference type.
    
    Uses Field Names (stable identifiers) instead of Field Paths.
    Backend resolves Field Name → Field Path at runtime.
    """
    if calculation_type != 'function_reference' or not dependency_names:
        return ''
    
    # Simple heuristic: if single dependency, use field name as param
    if len(dependency_names) == 1:
        # Extract parameter name from field name (last part after underscore)
        field_name = dependency_names[0]
        param_name = field_name.split('_')[-1]  # Use last part of field name
        params_dict = {param_name: field_name}  # Use Field Name, not Field Path
        return json.dumps(params_dict)
    
    # Multiple dependencies: try to infer parameter names
    # This is a placeholder - would need more sophisticated parsing
    params_dict = {}
    for i, field_name in enumerate(dependency_names):
        param_name = field_name.split('_')[-1]  # Use last part of field name as param name
        # If duplicate, add index
        if param_name in params_dict:
            param_name = f"{param_name}_{i+1}"
        params_dict[param_name] = field_name  # Use Field Name, not Field Path
    
    return json.dumps(params_dict)


def read_csv_file(file_path):
    """Read CSV file and return list of dictionaries"""
    with open(file_path, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
        reader = csv.DictReader(f)
        rows = list(reader)
        # Debug: print first row keys if empty
        if rows and not rows[0]:
            print(f"Warning: First row is empty. Column names: {reader.fieldnames}")
        return rows

def main():
    # Read input CSVs
    print(f"Reading Provider Fields CSV: {PROVIDER_FIELDS_CSV}")
    provider_fields = read_csv_file(PROVIDER_FIELDS_CSV)
    
    print(f"Reading Fleeti Fields CSV: {FLEETI_FIELDS_CSV}")
    fleeti_fields = read_csv_file(FLEETI_FIELDS_CSV)
    
    # Filter inactive Fleeti Fields
    inactive_fleeti_fields = [f for f in fleeti_fields if f.get('Status', '').strip().lower() == 'inactive']
    print(f"Found {len(inactive_fleeti_fields)} inactive Fleeti Fields")
    
    # Create provider fields lookup by name
    provider_lookup = {pf['Name']: pf for pf in provider_fields}
    
    # Create Fleeti fields lookup by name
    fleeti_lookup = {ff['Name']: ff for ff in fleeti_fields}
    
    # Generate mapping entries
    mapping_entries = []
    
    # Process in order: direct, prioritized, calculated
    direct_mappings = []
    prioritized_mappings = []
    calculated_mappings = []
    
    for fleeti_field in inactive_fleeti_fields:
        fleeti_name = fleeti_field['Name']
        fleeti_path = fleeti_field['Field Path']
        field_type = fleeti_field['Field Type']
        computation_approach = fleeti_field.get('Computation Approach', '').strip()
        dependencies_text = fleeti_field.get('Dependencies', '').strip()
        provider_field_links = fleeti_field.get('💽 Provider Field (db)', '').strip()
        
        # Extract provider field names
        provider_field_names = extract_field_name_from_notion_link(provider_field_links)
        
        # Get provider name (should be navixy for all)
        provider_name = 'navixy'
        if provider_field_names:
            # Get provider from first provider field
            first_provider_field = provider_lookup.get(provider_field_names[0])
            if first_provider_field:
                provider_name = first_provider_field.get('Provider', 'navixy')
        
        # Get Fleeti field metadata
        fleeti_unit = fleeti_field.get('Unit', '').strip()
        fleeti_data_type = fleeti_field.get('Data Type', '').strip()
        
        # Determine mapping type
        if field_type == 'calculated' or (not provider_field_names and field_type == 'calculated'):
            # Calculated field
            dependency_names = extract_dependencies_from_notion_links(dependencies_text)
            # Keep dependencies as Field Names (stable identifiers), not convert to Field Paths
            # Backend resolves Field Name → Field Path at runtime
            dependency_field_names = keep_dependencies_as_field_names(dependency_names, fleeti_lookup)
            calculation_type = determine_calculation_type(computation_approach, fleeti_name)
            
            # Skip mapping if no computation approach (invalid calculated field)
            if not calculation_type:
                print(f"Warning: Skipping calculated field '{fleeti_name}' - missing Computation Approach")
                continue
            
            # Extract backend function name and parameters only for function_reference type
            backend_function_name = ''
            function_parameters = ''
            
            if calculation_type == 'function_reference':
                # For function_reference type, both function name and parameters are required
                # Skip if dependencies are missing (cannot generate valid function parameters)
                if not dependency_field_names:
                    print(f"Warning: Skipping calculated field '{fleeti_name}' - missing Dependencies (required for function_reference)")
                    continue
                
                # Extract backend function name and parameters for function_reference
                backend_function_name = extract_backend_function_name(
                    fleeti_name, fleeti_path, computation_approach, calculation_type
                )
                function_parameters = extract_function_parameters(
                    dependency_field_names, computation_approach, calculation_type
                )
                
                # Validate that function_reference has both function name and parameters
                if not backend_function_name:
                    print(f"Warning: Skipping calculated field '{fleeti_name}' - missing Backend Function Name")
                    continue
                if not function_parameters:
                    print(f"Warning: Skipping calculated field '{fleeti_name}' - missing Function Parameters")
                    continue
            
            mapping_entry = {
                'Mapping Name': f"{fleeti_path} from {provider_name.capitalize()}",
                'Fleeti Field': fleeti_name,
                'Fleeti Field Path': fleeti_path,
                'Provider': provider_name,
                'Mapping Type': 'calculated',
                'Status': 'planned',
                'Configuration Level': 'default',
                'Provider Fields': '',  # Empty for calculated
                'Provider Field Paths': '',  # Empty for calculated
                'Provider Unit': '',  # Empty for calculated
                'Priority JSON': '',
                'Computation Approach': computation_approach,
                'Transformation Rule': '',
                'I/O Mapping Config': '',
                'Service Integration': '',
                'Dependencies': ', '.join(dependency_field_names) if dependency_field_names else '',
                'Calculation Type': calculation_type or '',
                'Default Value': '',
                'Error Handling': '',
                'Unit Conversion': '',
                'Backend Function Name': backend_function_name,
                'Function Parameters': function_parameters,
                'Fleeti Unit': fleeti_unit,
                'Fleeti Data Type': fleeti_data_type,
                'Version Added': '1.0.0',
                'Last Modified': '2025-01-16',
                'Notes': f'Calculated field: {fleeti_field.get("Description", "")}'
            }
            calculated_mappings.append((fleeti_field, mapping_entry, dependency_names))
        
        elif len(provider_field_names) > 1:
            # Prioritized mapping
            priority_order = parse_priority_order(computation_approach, provider_field_names)
            priority_json = json.dumps([{"priority": p, "field": f} for p, f in priority_order])
            
            # Get provider field paths and units
            provider_field_paths = get_provider_field_paths(provider_field_names, provider_lookup)
            provider_units = get_provider_units(provider_field_names, provider_lookup)
            unit_conversion = auto_generate_unit_conversion(provider_units, fleeti_unit)
            
            mapping_entry = {
                'Mapping Name': f"{fleeti_path} from {provider_name.capitalize()}",
                'Fleeti Field': fleeti_name,
                'Fleeti Field Path': fleeti_path,
                'Provider': provider_name,
                'Mapping Type': 'prioritized',
                'Status': 'planned',
                'Configuration Level': 'default',
                'Provider Fields': ', '.join(provider_field_names),
                'Provider Field Paths': ', '.join(provider_field_paths),
                'Provider Unit': ', '.join([u if u else 'none' for u in provider_units]),
                'Priority JSON': priority_json,
                'Computation Approach': '',
                'Transformation Rule': '',
                'I/O Mapping Config': '',
                'Service Integration': '',
                'Dependencies': '',
                'Calculation Type': '',
                'Default Value': '',
                'Error Handling': 'use_fallback',  # Default for prioritized mappings
                'Unit Conversion': unit_conversion,
                'Backend Function Name': '',
                'Function Parameters': '',
                'Fleeti Unit': fleeti_unit,
                'Fleeti Data Type': fleeti_data_type,
                'Version Added': '1.0.0',
                'Last Modified': '2025-01-16',
                'Notes': f'Prioritized mapping: {fleeti_field.get("Description", "")}'
            }
            prioritized_mappings.append(mapping_entry)
        
        elif len(provider_field_names) == 1:
            # Direct mapping
            provider_field_name = provider_field_names[0]
            provider_field_paths = get_provider_field_paths([provider_field_name], provider_lookup)
            provider_units = get_provider_units([provider_field_name], provider_lookup)
            unit_conversion = auto_generate_unit_conversion(provider_units, fleeti_unit)
            
            mapping_entry = {
                'Mapping Name': f"{fleeti_path} from {provider_name.capitalize()}",
                'Fleeti Field': fleeti_name,
                'Fleeti Field Path': fleeti_path,
                'Provider': provider_name,
                'Mapping Type': 'direct',
                'Status': 'planned',
                'Configuration Level': 'default',
                'Provider Fields': provider_field_name,
                'Provider Field Paths': provider_field_paths[0] if provider_field_paths else provider_field_name,
                'Provider Unit': provider_units[0] if provider_units else '',
                'Priority JSON': '',
                'Computation Approach': '',
                'Transformation Rule': '',
                'I/O Mapping Config': '',
                'Service Integration': '',
                'Dependencies': '',
                'Calculation Type': '',
                'Default Value': '',
                'Error Handling': '',
                'Unit Conversion': unit_conversion,
                'Backend Function Name': '',
                'Function Parameters': '',
                'Fleeti Unit': fleeti_unit,
                'Fleeti Data Type': fleeti_data_type,
                'Version Added': '1.0.0',
                'Last Modified': '2025-01-16',
                'Notes': f'Direct mapping: {fleeti_field.get("Description", "")}'
            }
            direct_mappings.append(mapping_entry)
    
    # Sort calculated mappings by dependencies (dependencies first)
    def get_dependency_depth(fleeti_field, all_fleeti_fields, visited=None):
        """Calculate dependency depth for topological sort with cycle detection"""
        if visited is None:
            visited = set()
        
        field_name = fleeti_field['Name']
        if field_name in visited:
            # Circular dependency detected, return 0 to break cycle
            return 0
        
        visited.add(field_name)
        dependencies = extract_dependencies_from_notion_links(fleeti_field.get('Dependencies', ''))
        if not dependencies:
            visited.remove(field_name)
            return 0
        
        # Find max depth of dependencies
        max_depth = 0
        for dep_name in dependencies:
            for ff in all_fleeti_fields:
                if ff['Name'] == dep_name:
                    depth = get_dependency_depth(ff, all_fleeti_fields, visited.copy()) + 1
                    max_depth = max(max_depth, depth)
                    break
        
        visited.remove(field_name)
        return max_depth
    
    calculated_mappings.sort(key=lambda x: get_dependency_depth(x[0], inactive_fleeti_fields))
    
    # Combine all mappings in order
    all_mappings = direct_mappings + prioritized_mappings + [me for _, me, _ in calculated_mappings]
    
    print(f"\nGenerated {len(all_mappings)} mapping entries:")
    print(f"  - {len(direct_mappings)} direct mappings")
    print(f"  - {len(prioritized_mappings)} prioritized mappings")
    print(f"  - {len(calculated_mappings)} calculated mappings")
    
    # Write output CSV
    if all_mappings:
        # Reorganized column order matching README structure
        fieldnames = [
            # Group 1: Core Identification
            'Mapping Name', 'Fleeti Field', 'Fleeti Field Path', 'Provider', 'Mapping Type', 'Status', 'Configuration Level',
            # Group 2: Source Fields
            'Provider Fields', 'Provider Field Paths', 'Provider Unit',
            # Group 3: Mapping Logic
            'Priority JSON', 'Computation Approach', 'Transformation Rule', 'I/O Mapping Config', 'Service Integration',
            # Group 4: Dependencies & Execution Order
            'Dependencies', 'Calculation Type',
            # Group 5: Error Handling & Defaults
            'Default Value', 'Error Handling', 'Unit Conversion',
            # Group 6: Backend Implementation
            'Backend Function Name', 'Function Parameters',
            # Group 7: Metadata
            'Fleeti Unit', 'Fleeti Data Type', 'Version Added', 'Last Modified', 'Notes'
        ]
        
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_mappings)
        
        print(f"\nOutput CSV written to: {OUTPUT_CSV}")
    else:
        print("\nNo mapping entries generated!")

if __name__ == '__main__':
    main()

