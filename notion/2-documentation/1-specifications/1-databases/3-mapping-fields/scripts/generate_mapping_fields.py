#!/usr/bin/env python3
"""
Generate Mapping Fields Database CSV from Fleeti Fields Database exports.

This script transforms Fleeti Fields Database CSV exports (from Notion) into Mapping Fields
Database entries. It generates mapping rules that link provider fields to Fleeti fields,
determining transformation logic, priorities, and calculation rules.

Input:  input/Fleeti Fields (db) 12-18-25.csv (Notion export format)
Output: Mapping-Fields-Navixy-2025-01-16.csv (provider-specific mapping configuration)

See specifications/MAPPING_FIELDS_GENERATION_SPEC.md for detailed documentation.
"""

import csv
import json
import re
from datetime import date
from pathlib import Path

# Input file - Fleeti Fields CSV is in the input folder
# Script is in: 3-mapping-fields/scripts/
# Fleeti Fields CSV is in: 3-mapping-fields/scripts/input/
FLEETI_FIELDS_CSV = Path(__file__).parent / "input" / "Fleeti Fields (db) 12-18-25.csv"

# Output file - CSV should be generated in the same scripts folder as this script
OUTPUT_CSV = Path(__file__).parent / "Mapping-Fields-Navixy-2025-01-16.csv"

def extract_field_name_from_notion_link(link_text):
    """Extract field name from Notion link format: 'field_name (https://...)' or plain field_name"""
    if not link_text or not link_text.strip():
        return ""
    
    # Check if it's a Notion link format
    if '(' in link_text and 'https://' in link_text:
        # Extract field name before opening parenthesis
        match = re.match(r'^([^(]+)', link_text.strip())
        if match:
            return match.group(1).strip()
    
    # Not a Notion link, return as-is
    return link_text.strip()

def extract_field_names_from_notion_links(link_text):
    """Extract multiple field names from comma-separated Notion links"""
    if not link_text or not link_text.strip():
        return []
    
    # Handle comma-separated multiple fields
    fields = []
    for part in link_text.split(','):
        part = part.strip()
        field_name = extract_field_name_from_notion_link(part)
        if field_name:
            fields.append(field_name)
    
    return fields

def infer_provider_field_path(provider_field_name):
    """Infer provider field path from field name.
    
    Simple fields: use name as path (e.g., 'lat' -> 'lat')
    Complex fields: infer from name (e.g., 'avl_io_69' -> 'params.avl_io_69')
    """
    if not provider_field_name:
        return ''
    
    # Check if it's an AVL IO field
    if provider_field_name.startswith('avl_io_'):
        return f'params.{provider_field_name}'
    
    # Simple fields: use name as path
    return provider_field_name

def get_provider_field_paths(provider_field_names):
    """Get provider field paths by inferring from field names.
    
    Args:
        provider_field_names: List of provider field names
        
    Returns:
        List of provider field paths (e.g., ['lat', 'params.avl_io_69'])
    """
    paths = []
    for name in provider_field_names:
        path = infer_provider_field_path(name)
        paths.append(path)
    return paths

def get_provider_units(provider_field_names):
    """Get provider units - leave empty since we don't have Provider Fields CSV"""
    # Return empty list since we don't have provider field metadata
    return [''] * len(provider_field_names)

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
    """Auto-generate unit conversion rule if units differ.
    
    Currently returns empty string - unit conversion should be manually specified.
    This function is kept for future enhancement.
    
    Args:
        provider_units: List of provider field units
        fleeti_unit: Fleeti field unit
        
    Returns:
        Empty string (unit conversion left for manual specification)
    """
    if not fleeti_unit or not provider_units:
        return ''
    
    # Normalize units for comparison
    fleeti_normalized = normalize_unit(fleeti_unit)
    provider_normalized = normalize_unit(provider_units[0] if provider_units else None)
    
    # Skip if units are equivalent or same
    if not provider_normalized or not fleeti_normalized:
        return ''  # Skip for empty/unknown units
    
    if provider_normalized == fleeti_normalized:
        return ''  # Skip for same/equivalent units
    
    # Units differ - return empty (conversion should be manually specified)
    return ''

def extract_dependencies_from_notion_links(links_text):
    """Extract dependency field names from Dependencies column (with Notion links)"""
    if not links_text or not links_text.strip():
        return []
    
    # Use the new function to extract field names from Notion links
    return extract_field_names_from_notion_links(links_text)

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
    """Parse priority order from Computation Approach column.
    
    Supports '>' syntax to specify priority order (e.g., 'hdop>avl_io_182').
    If no priority specified, uses order from provider fields list.
    
    Args:
        computation_approach: Computation Approach text (may contain priority syntax)
        provider_fields: List of provider field names
        
    Returns:
        List of tuples (priority, field_name) sorted by priority
        Example: [(1, 'hdop'), (2, 'avl_io_182')]
    """
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
    """Extract backend function name for function_reference type.
    
    Infers function name from field name/path using consistent naming convention:
    - Removes category prefixes (location_, motion_, etc.)
    - Adds 'derive_' prefix
    - Example: location_cardinal_direction -> derive_cardinal_direction
    
    Args:
        fleeti_name: Fleeti field name (e.g., 'location_cardinal_direction')
        fleeti_path: Fleeti field path (e.g., 'location.cardinal_direction')
        computation_approach: Computation approach text
        calculation_type: Calculation type ('function_reference' or 'formula')
        
    Returns:
        Backend function name (e.g., 'derive_cardinal_direction')
    """
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

def extract_function_parameters(dependency_names, provider_field_names, computation_approach, calculation_type):
    """Extract structured parameter mapping for function_reference type.
    
    Generates new format with fleeti:/provider: keys:
    - Single param: {"fleeti": "location_heading"} (default)
    - Multiple params: {"fleeti": ["location_latitude", "location_longitude"]}
    - Provider fields: {"provider": "heading"} (when provider field is used)
    
    Uses Field Names (stable identifiers) for Fleeti fields.
    Uses field names for provider fields.
    
    Logic:
    - If computation approach mentions a simple field name (like "heading") that could be
      a provider field, and the dependency is a Fleeti field that might be derived from that
      provider field, use provider.
    - If computation approach mentions a provider field name directly, use provider.
    - Otherwise, default to using Fleeti fields from dependencies.
    """
    if calculation_type != 'function_reference':
        return ''
    
    # Check if computation approach mentions a simple field name that could be a provider field
    use_provider = False
    inferred_provider_field = None
    
    if computation_approach:
        comp_lower = computation_approach.lower()
        
        # Check if computation mentions any explicit provider field names
        if provider_field_names:
            for provider_field in provider_field_names:
                pattern = r'\b' + re.escape(provider_field.lower()) + r'\b'
                if re.search(pattern, comp_lower):
                    use_provider = True
                    inferred_provider_field = provider_field
                    break
        
        # If no explicit provider field but computation mentions a simple field name
        # that matches the last part of a dependency (e.g., "heading" from "location_heading"),
        # infer it might be a provider field
        # BUT: if the simple name is part of a dependency name (e.g., "latitude" in "location_latitude"),
        # it's NOT a provider field - it's referring to the Fleeti field
        if not use_provider and dependency_names:
            # Look for simple field names in computation (single word, no underscores)
            simple_field_pattern = r'\b([a-z]+)\b'
            matches = re.findall(simple_field_pattern, comp_lower)
            for match in matches:
                # Skip common words that are not field names
                if match in ['from', 'use', 'convert', 'into', 'to', 'the', 'a', 'an', 'and', 'or', 'if', 'then', 'else', 'when', 'where']:
                    continue
                
                # Check if this simple name is part of any dependency name
                is_part_of_dependency = False
                for dep in dependency_names:
                    if match in dep.lower() and (dep.lower().endswith('_' + match) or dep.lower() == match):
                        # The simple name is part of a dependency - don't use as provider field
                        is_part_of_dependency = True
                        break
                
                # Only use as provider field if it's NOT part of a dependency
                # and it matches the last part of a dependency (e.g., "heading" from "location_heading")
                if not is_part_of_dependency:
                    for dep in dependency_names:
                        if dep.endswith('_' + match) or dep == match:
                            # This could be a provider field - use it
                            use_provider = True
                            inferred_provider_field = match
                            break
                    if use_provider:
                        break
    
    # If we have provider fields and no dependencies, use provider
    if provider_field_names and not dependency_names:
        use_provider = True
        inferred_provider_field = provider_field_names[0] if provider_field_names else None
    
    if use_provider:
        # Use provider fields
        if inferred_provider_field:
            return json.dumps({"provider": inferred_provider_field})
        elif provider_field_names:
            if len(provider_field_names) == 1:
                return json.dumps({"provider": provider_field_names[0]})
            else:
                return json.dumps({"provider": provider_field_names})
    
    # Default: use Fleeti fields from dependencies
    if not dependency_names:
        return ''
    
    if len(dependency_names) == 1:
        return json.dumps({"fleeti": dependency_names[0]})
    else:
        return json.dumps({"fleeti": dependency_names})


def read_csv_file(file_path):
    """Read CSV file and return list of dictionaries.
    
    Uses utf-8-sig encoding to handle BOM (Byte Order Mark) that may be present
    in Notion CSV exports.
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        List of dictionaries, one per row, with column names as keys
    """
    with open(file_path, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
        reader = csv.DictReader(f)
        rows = list(reader)
        # Debug: print first row keys if empty
        if rows and not rows[0]:
            print(f"Warning: First row is empty. Column names: {reader.fieldnames}")
        return rows

def main():
    """
    Main processing function.
    
    Processing flow:
    1. Read and filter Fleeti Fields CSV (only inactive fields)
    2. For each inactive field, determine mapping type and generate entry
    3. Sort calculated mappings by dependency depth
    4. Write output CSV with exact column order matching export format
    """
    # Read input CSV
    print(f"Reading Fleeti Fields CSV: {FLEETI_FIELDS_CSV}")
    fleeti_fields = read_csv_file(FLEETI_FIELDS_CSV)
    
    # Filter inactive Fleeti Fields (active fields are already mapped)
    inactive_fleeti_fields = [f for f in fleeti_fields if f.get('Status', '').strip().lower() == 'inactive']
    print(f"Found {len(inactive_fleeti_fields)} inactive Fleeti Fields")
    
    # Create Fleeti fields lookup by name for dependency validation
    fleeti_lookup = {ff['Name']: ff for ff in fleeti_fields}
    
    # Generate mapping entries
    mapping_entries = []
    
    # Process in order: direct, prioritized, calculated
    direct_mappings = []
    prioritized_mappings = []
    calculated_mappings = []
    
    # Process each inactive Fleeti field and generate mapping entry
    for fleeti_field in inactive_fleeti_fields:
        # Extract core field information from CSV
        fleeti_name = fleeti_field['Name']  # Stable identifier (e.g., 'location_latitude')
        fleeti_path = fleeti_field['Field Path']  # JSON path (e.g., 'location.latitude')
        field_type = fleeti_field['Field Type']  # 'direct' or 'calculated'
        computation_approach = fleeti_field.get('Computation Approach', '').strip()
        dependencies_text = fleeti_field.get('Dependencies', '').strip()  # May contain Notion links
        provider_field_links = fleeti_field.get('💽 Provider Field (db)', '').strip()  # May contain Notion links
        
        # Extract provider field names from Notion links (e.g., 'lat (https://...)' -> 'lat')
        provider_field_names = extract_field_names_from_notion_links(provider_field_links)
        
        # Provider name is hardcoded to 'navixy' since all input data is for Navixy provider
        provider_name = 'navixy'
        
        # Extract Fleeti field metadata from CSV
        fleeti_unit = fleeti_field.get('Unit', '').strip()
        fleeti_data_type = fleeti_field.get('Data Type', '').strip()
        version_added = fleeti_field.get('Version Added', '1.0.0').strip()  # Read from CSV, not hardcoded
        
        # Determine mapping type based on field type and number of provider fields
        # - Calculated: field_type == 'calculated' OR no provider fields + calculated
        # - Prioritized: 2+ provider fields
        # - Direct: 1 provider field
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
                    dependency_field_names, provider_field_names, computation_approach, calculation_type
                )
                
                # Validate that function_reference has both function name and parameters
                if not backend_function_name:
                    print(f"Warning: Skipping calculated field '{fleeti_name}' - missing Backend Function Name")
                    continue
                if not function_parameters:
                    print(f"Warning: Skipping calculated field '{fleeti_name}' - missing Function Parameters")
                    continue
            
            mapping_entry = {
                'Name': f"{fleeti_path} from {provider_name.capitalize()}",
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
                'Version Added': version_added,
                'Notes': f'Calculated field: {fleeti_field.get("Description", "")}',
                '💽 YAML Configurations (db)': ''  # Empty, manual input
            }
            calculated_mappings.append((fleeti_field, mapping_entry, dependency_names))
        
        elif len(provider_field_names) > 1:
            # Prioritized mapping
            priority_order = parse_priority_order(computation_approach, provider_field_names)
            priority_json = json.dumps([{"priority": p, "field": f} for p, f in priority_order])
            
            # Get provider field paths and units
            provider_field_paths = get_provider_field_paths(provider_field_names)
            provider_units = get_provider_units(provider_field_names)
            unit_conversion = auto_generate_unit_conversion(provider_units, fleeti_unit)
            
            mapping_entry = {
                'Name': f"{fleeti_path} from {provider_name.capitalize()}",
                'Fleeti Field': fleeti_name,
                'Fleeti Field Path': fleeti_path,
                'Provider': provider_name,
                'Mapping Type': 'prioritized',
                'Status': 'planned',
                'Configuration Level': 'default',
                'Provider Fields': ', '.join(provider_field_names),
                'Provider Field Paths': ','.join(provider_field_paths),
                'Provider Unit': ', '.join([u if u else '-' for u in provider_units]) if any(provider_units) else '',
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
                'Version Added': version_added,
                'Notes': f'Prioritized mapping: {fleeti_field.get("Description", "")}',
                '💽 YAML Configurations (db)': ''  # Empty, manual input
            }
            prioritized_mappings.append(mapping_entry)
        
        elif len(provider_field_names) == 1:
            # Direct mapping
            provider_field_name = provider_field_names[0]
            provider_field_paths = get_provider_field_paths([provider_field_name])
            provider_units = get_provider_units([provider_field_name])
            unit_conversion = auto_generate_unit_conversion(provider_units, fleeti_unit)
            
            mapping_entry = {
                'Name': f"{fleeti_path} from {provider_name.capitalize()}",
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
                'Version Added': version_added,
                'Notes': f'Direct mapping: {fleeti_field.get("Description", "")}',
                '💽 YAML Configurations (db)': ''  # Empty, manual input
            }
            direct_mappings.append(mapping_entry)
    
    # Sort calculated mappings by dependencies (dependencies first)
    # This ensures correct evaluation order: dependencies are processed before dependents
    def get_dependency_depth(fleeti_field, all_fleeti_fields, visited=None):
        """Calculate dependency depth for topological sort with cycle detection.
        
        Returns the maximum depth of dependencies for a field. Fields with no dependencies
        have depth 0. Fields that depend on other calculated fields have higher depth.
        
        Handles circular dependencies gracefully by returning 0 when a cycle is detected.
        
        Args:
            fleeti_field: Fleeti field dictionary
            all_fleeti_fields: List of all Fleeti fields for lookup
            visited: Set of visited field names (for cycle detection)
            
        Returns:
            Dependency depth (0 = no dependencies, higher = deeper dependency chain)
        """
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
        # Column order matching export CSV exactly
        fieldnames = [
            'Name',  # Mapping Name
            'Backend Function Name',
            'Calculation Type',
            'Computation Approach',
            'Configuration Level',
            'Default Value',
            'Dependencies',
            'Error Handling',
            'Fleeti Data Type',
            'Fleeti Field',
            'Fleeti Field Path',
            'Fleeti Unit',
            'Function Parameters',
            'I/O Mapping Config',
            'Mapping Type',
            'Notes',
            'Priority JSON',
            'Provider',
            'Provider Field Paths',
            'Provider Fields',
            'Provider Unit',
            'Service Integration',
            'Status',
            'Transformation Rule',
            'Unit Conversion',
            'Version Added',
            '💽 YAML Configurations (db)'
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

