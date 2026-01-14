#!/usr/bin/env python3
"""
Extract Provider Fields from YAML Configuration to JSON

This script extracts all Navixy provider fields referenced in the latest YAML configuration
file and generates a JSON file with only the required API columns for data recovery.
"""

import json
import re
import yaml
from pathlib import Path
from datetime import datetime
from typing import Set, Dict, Any, List


# Known states.* fields that should use states.* prefix instead of inputs.*
STATES_FIELDS = {
    'moving', 'battery_level', 'battery_voltage', 'board_voltage',
    'can_abs_state', 'can_adblue_level', 'can_battery_level',
    'can_engine_hours', 'can_engine_load', 'can_engine_temp',
    'can_fuel_rate', 'can_ignition_state', 'can_mileage', 'can_rpm',
    'can_speed', 'can_throttle', 'cornering', 'external_power_state',
    'fuel_level', 'hw_mileage', 'obd_rpm', 'obd_speed', 'obd_throttle',
    'raw_mileage', 'speed', 'towing'
}

# Root level fields (don't need inputs.* or states.* prefix)
ROOT_LEVEL_FIELDS = {
    'lat', 'lng', 'alt', 'heading', 'satellites', 'hdop', 'pdop',
    'speed', 'msg_time', 'gps_fix_type', 'event_id',
    'precision', 'mn_roaming', 'mn_code', 'mn_csq', 'mn_type'
}

# Core columns to always include
CORE_COLUMNS = {
    'gps_fix_type', 'event_id'
}

# Fields to exclude from API columns (cause errors or not available)
EXCLUDED_FIELDS = {
    'ibutton',  # Not available in recovery API, causes errors
    'msg_time'  # Not available in recovery API, causes errors
}


def find_latest_yaml_file(output_dir: Path) -> Path:
    """Find the most recent YAML file matching navixy-mapping-*.yaml pattern."""
    yaml_files = list(output_dir.glob('navixy-mapping-*.yaml'))
    if not yaml_files:
        raise FileNotFoundError(f"No YAML files found in {output_dir}")
    
    # Sort by filename (date-based) descending
    yaml_files.sort(key=lambda p: p.name, reverse=True)
    return yaml_files[0]


def extract_date_from_filename(filename: str) -> str:
    """Extract date from filename like navixy-mapping-2026-01-08.yaml."""
    match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if match:
        return match.group(1)
    return datetime.now().strftime('%Y-%m-%d')


def map_path_to_api_column(field_name: str, path: str) -> str:
    """
    Map YAML path to API column format.
    
    Examples:
    - path: lat -> "lat"
    - path: params.avl_io_69 -> "inputs.avl_io_69"
    - path: params.moving -> "states.moving"
    """
    # Root level fields
    if not path.startswith('params.'):
        if field_name in ROOT_LEVEL_FIELDS:
            return field_name
        # If it's a known root field, return as-is
        return field_name
    
    # Extract field name from params.* path
    if path.startswith('params.'):
        param_field = path.replace('params.', '')
        
        # Check if it's a states.* field
        if param_field in STATES_FIELDS:
            return f"states.{param_field}"
        
        # Default to inputs.*
        return f"inputs.{param_field}"
    
    return field_name


def infer_api_column_from_field_name(field_name: str) -> str:
    """
    Infer API column format from field name when no path is available.
    
    Examples:
    - avl_io_202 -> inputs.avl_io_202
    - can_speed -> inputs.can_speed
    - ble_temp_sensor_1 -> inputs.ble_temp_sensor_1
    - moving -> states.moving (if in STATES_FIELDS)
    """
    # Check if it's a states field
    if field_name in STATES_FIELDS:
        return f"states.{field_name}"
    
    # Check if it's a root level field
    if field_name in ROOT_LEVEL_FIELDS:
        return field_name
    
    # Default to inputs.*
    return f"inputs.{field_name}"


def extract_fields_from_sources(sources: List[Dict[str, Any]], columns: Set[str], needs_discrete_inputs: List[bool], needs_discrete_outputs: List[bool]) -> None:
    """Extract provider fields from sources array."""
    for source in sources:
        # Extract from field/path entries
        if 'field' in source and 'path' in source:
            field_name = source['field']
            path = source['path']
            api_column = map_path_to_api_column(field_name, path)
            columns.add(api_column)
        
        # Extract from parameters.provider.navixy
        if 'parameters' in source:
            params = source['parameters']
            if 'provider' in params and 'navixy' in params['provider']:
                navixy_value = params['provider']['navixy']
                
                # Special case: inputs/outputs bitmasks
                if navixy_value == 'inputs':
                    needs_discrete_inputs.append(True)
                elif navixy_value == 'outputs':
                    needs_discrete_outputs.append(True)
                # If it's a list of field names
                elif isinstance(navixy_value, list):
                    for field_name in navixy_value:
                        api_column = infer_api_column_from_field_name(field_name)
                        columns.add(api_column)
                # If it's a single field name string
                elif isinstance(navixy_value, str):
                    api_column = infer_api_column_from_field_name(navixy_value)
                    columns.add(api_column)


def extract_fields_from_provider_array(provider_array: List[str], columns: Set[str]) -> None:
    """Extract fields from parameters.provider.navixy[] arrays."""
    for field_name in provider_array:
        api_column = infer_api_column_from_field_name(field_name)
        columns.add(api_column)


def extract_provider_fields(yaml_data: Dict[str, Any]) -> Set[str]:
    """Extract all provider fields from YAML configuration."""
    columns: Set[str] = set()
    needs_discrete_inputs = []
    needs_discrete_outputs = []
    
    # Add core columns
    columns.update(CORE_COLUMNS)
    
    mappings = yaml_data.get('mappings', {})
    
    for fleeti_field, mapping in mappings.items():
        # Extract from sources
        if 'sources' in mapping:
            extract_fields_from_sources(
                mapping['sources'],
                columns,
                needs_discrete_inputs,
                needs_discrete_outputs
            )
        
        # Extract from parameters.provider.navixy arrays
        if 'parameters' in mapping:
            params = mapping['parameters']
            if 'provider' in params and 'navixy' in params['provider']:
                navixy_value = params['provider']['navixy']
                if isinstance(navixy_value, list):
                    extract_fields_from_provider_array(navixy_value, columns)
                elif isinstance(navixy_value, str) and navixy_value not in ['inputs', 'outputs']:
                    api_column = infer_api_column_from_field_name(navixy_value)
                    columns.add(api_column)
    
    # Add discrete_inputs/discrete_outputs if needed
    if any(needs_discrete_inputs):
        columns.add('discrete_inputs')
    if any(needs_discrete_outputs):
        columns.add('discrete_outputs')
    
    # Remove excluded fields (cause API errors or not available)
    columns = columns - EXCLUDED_FIELDS
    
    return columns


def generate_json_output(columns: Set[str], yaml_date: str, yaml_version: str = None) -> Dict[str, Any]:
    """Generate JSON structure matching cURL_reference.json format."""
    sorted_columns = sorted(columns)
    
    json_output = {
        "hash": "{{navixy_hash}}",
        "tracker_id": "3312229",
        "from": "2025-11-26T00:00:00Z",
        "to": "2025-11-26T23:59:59Z",
        "columns": sorted_columns
    }
    
    # Add YAML configuration version for version-based validation
    if yaml_version:
        json_output["yaml_config_version"] = yaml_version
    
    return json_output


def main():
    """Main execution function."""
    # Define paths
    script_dir = Path(__file__).parent
    output_dir = script_dir.parent.parent / 'output'
    output_subdir = script_dir / 'output'
    
    # Create output subdirectory if it doesn't exist
    output_subdir.mkdir(exist_ok=True)
    
    # Find latest YAML file
    print(f"Looking for YAML files in: {output_dir}")
    yaml_file = find_latest_yaml_file(output_dir)
    print(f"Found latest YAML file: {yaml_file.name}")
    
    # Extract date from filename
    yaml_date = extract_date_from_filename(yaml_file.name)
    print(f"Extracted date: {yaml_date}")
    
    # Load YAML file
    print(f"Loading YAML file...")
    with open(yaml_file, 'r', encoding='utf-8') as f:
        yaml_data = yaml.safe_load(f)
    
    # Extract YAML version
    yaml_version = yaml_data.get('version', None)
    if yaml_version:
        print(f"YAML configuration version: {yaml_version}")
    
    # Extract provider fields
    print("Extracting provider fields...")
    columns = extract_provider_fields(yaml_data)
    print(f"Found {len(columns)} unique provider fields")
    
    # Generate JSON output
    json_output = generate_json_output(columns, yaml_date, yaml_version)
    
    # Save to output file
    output_filename = f"navixy-recovery-columns-{yaml_date}.json"
    output_path = output_subdir / output_filename
    
    print(f"Saving JSON to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(json_output, f, indent=2, ensure_ascii=False)
    
    print(f"\nSuccess! Generated {output_filename}")
    print(f"Total columns: {len(json_output['columns'])}")
    print(f"\nFirst 10 columns:")
    for col in json_output['columns'][:10]:
        print(f"  - {col}")
    if len(json_output['columns']) > 10:
        print(f"  ... and {len(json_output['columns']) - 10} more")


if __name__ == '__main__':
    main()
