#!/usr/bin/env python3
"""
Generate Mapping Fields CSV from Fleeti Fields

This script reads Fleeti Fields and Mapping Fields exports, identifies unmapped
Fleeti Fields, and generates a CSV file ready for import into Notion.
"""

import csv
import json
import re
from pathlib import Path
from datetime import date
from typing import Set, Dict, List, Any


def extract_field_name_from_notion_link(field_value: str) -> str:
    """Extract field name from Notion link format: 'field_name (https://...)'"""
    if not field_value:
        return ""
    # Extract everything before the opening parenthesis
    match = re.match(r'^([^(]+)', field_value.strip())
    if match:
        return match.group(1).strip()
    return field_value.strip()


def parse_json_field(json_str: str) -> Dict[str, Any]:
    """Parse JSON field that may span multiple lines."""
    if not json_str or not json_str.strip():
        return {}
    try:
        # Handle escaped quotes in CSV format
        cleaned = json_str.replace('""', '"')
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {}


def extract_mapping_type(computation_json: str, field_type: str) -> str:
    """Extract mapping type from Computation Structure JSON or fallback to Field Type."""
    json_data = parse_json_field(computation_json)
    
    # Try to extract from JSON first
    if json_data and "type" in json_data:
        json_type = json_data["type"]
        type_mapping = {
            "direct": "direct",
            "prioritized": "prioritized",
            "calculated": "calculated",
            "transformed": "mix",
            "io_mapped": "mix"
        }
        if json_type in type_mapping:
            return type_mapping[json_type]
    
    # Fallback to Field Type column
    if field_type:
        type_mapping = {
            "direct": "direct",
            "prioritized": "prioritized",
            "calculated": "calculated",
            "transformed": "mix",
            "io_mapped": "mix"
        }
        return type_mapping.get(field_type.lower(), "calculated")
    
    return "calculated"  # Default fallback


def read_mapping_fields_export(file_path: Path) -> tuple[List[str], Set[str]]:
    """Read Mapping Fields export and extract column headers and already-mapped field names."""
    columns = []
    mapped_fields = set()
    
    with open(file_path, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
        reader = csv.DictReader(f)
        columns = [col.lstrip('\ufeff') for col in (reader.fieldnames or [])]
        
        # Find the "Fleeti Field" column index
        fleeti_field_col = None
        for col in columns:
            if col.lower() == "fleeti field":
                fleeti_field_col = col
                break
        
        if not fleeti_field_col:
            raise ValueError("Could not find 'Fleeti Field' column in Mapping Fields export")
        
        # Extract field names
        for row in reader:
            field_value = row.get(fleeti_field_col, "")
            if field_value:
                field_name = extract_field_name_from_notion_link(field_value)
                if field_name:
                    mapped_fields.add(field_name)
    
    return columns, mapped_fields


def read_fleeti_fields_export(file_path: Path) -> List[Dict[str, str]]:
    """Read Fleeti Fields export and return all rows."""
    rows = []
    with open(file_path, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
        reader = csv.DictReader(f)
        for row in reader:
            # Normalize column names (remove BOM if present)
            normalized_row = {}
            for key, value in row.items():
                normalized_key = key.lstrip('\ufeff')
                normalized_row[normalized_key] = value
            rows.append(normalized_row)
    return rows


def generate_output_rows(
    fleeti_rows: List[Dict[str, str]],
    mapped_fields: Set[str]
) -> List[Dict[str, str]]:
    """Generate output rows for unmapped Fleeti Fields."""
    output_rows = []
    skipped_mapped = 0
    skipped_empty = 0
    
    for row in fleeti_rows:
        field_name = row.get("Name", "").strip()
        if not field_name:
            skipped_empty += 1
            continue
        
        # Skip if already mapped
        if field_name in mapped_fields:
            skipped_mapped += 1
            continue
        
        # Extract required fields
        category = row.get("Category", "").strip()
        computation_json = row.get("Computation Structure JSON", "").strip()
        field_type = row.get("Field Type", "").strip()
        
        # Extract mapping type (needed for output, but don't copy JSON)
        mapping_type = extract_mapping_type(computation_json, field_type)
        
        # Generate Name: [Category].[Name] from Navixy
        # Keep underscores in Name as-is, don't convert to dots
        if category:
            output_name = f"{category}.{field_name} from Navixy"
        else:
            # If no category, just use Name
            output_name = f"{field_name} from Navixy"
        
        # Create output row (will be populated with all columns later)
        output_row = {
            "Name": output_name,
            "Provider": "navixy",
            "Mapping Type": mapping_type,
            "Status": "planned",
            "Configuration Level": "default",
            "Computation Approach": "",  # Leave empty
            "Computation Structure JSON": ""  # Leave empty
        }
        
        output_rows.append(output_row)
    
    if skipped_mapped > 0 or skipped_empty > 0:
        print(f"  Skipped {skipped_mapped} already-mapped fields, {skipped_empty} rows with empty Name")
    return output_rows


def write_output_csv(
    output_path: Path,
    columns: List[str],
    output_rows: List[Dict[str, str]]
):
    """Write output CSV with all columns from Mapping Fields export."""
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        
        for row_data in output_rows:
            # Create a row with all columns, filling in known values and empty strings for others
            output_row = {}
            for col in columns:
                if col in row_data:
                    output_row[col] = row_data[col]
                else:
                    output_row[col] = ""
            writer.writerow(output_row)


def main():
    """Main execution function."""
    # Define paths relative to script location
    script_dir = Path(__file__).parent.resolve()
    # Script is at: notion/2-documentation/1-specifications/1-databases/3-mapping-fields/scripts/
    # Build paths relative to script location
    base_dir = script_dir.parent  # 3-mapping-fields/
    
    fleeti_fields_dir = base_dir.parent / "2-fleeti-fields" / "export"
    mapping_fields_export_dir = base_dir / "export"
    output_dir = base_dir / "output"
    
    # Find most recent files
    fleeti_files = list(fleeti_fields_dir.glob("Fleeti Fields (db) *.csv"))
    mapping_files = list(mapping_fields_export_dir.glob("Mapping Fields (db) *.csv"))
    
    if not fleeti_files:
        raise FileNotFoundError(f"No Fleeti Fields export found in {fleeti_fields_dir}")
    if not mapping_files:
        raise FileNotFoundError(f"No Mapping Fields export found in {mapping_fields_export_dir}")
    
    # Get most recent files (by filename date)
    fleeti_file = max(fleeti_files, key=lambda p: p.name)
    mapping_file = max(mapping_files, key=lambda p: p.name)
    
    print(f"Reading Mapping Fields export: {mapping_file.name}")
    columns, mapped_fields = read_mapping_fields_export(mapping_file)
    print(f"Found {len(mapped_fields)} already-mapped fields")
    print(f"Found {len(columns)} columns in Mapping Fields export")
    
    print(f"\nReading Fleeti Fields export: {fleeti_file.name}")
    fleeti_rows = read_fleeti_fields_export(fleeti_file)
    print(f"Found {len(fleeti_rows)} Fleeti Fields")
    
    print(f"\nGenerating output rows...")
    output_rows = generate_output_rows(fleeti_rows, mapped_fields)
    print(f"Generated {len(output_rows)} unmapped Mapping Fields entries")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate output filename with current date
    today = date.today()
    output_filename = f"Mapping Fields to Add {today.strftime('%Y-%m-%d')}.csv"
    output_path = output_dir / output_filename
    
    print(f"\nWriting output to: {output_path}")
    write_output_csv(output_path, columns, output_rows)
    
    print(f"\nSuccessfully generated {len(output_rows)} Mapping Fields entries")
    print(f"  Output file: {output_path}")


if __name__ == "__main__":
    main()

