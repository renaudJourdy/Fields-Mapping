#!/usr/bin/env python3
"""
Validation script to ensure all Navixy fields from the reference catalog are documented in the Fleeti telemetry schema specification.

Uses docs/reference/navixy-field-catalog.csv as the authoritative source of truth for Navixy field inventory.
"""

import csv
import re
from collections import defaultdict
from pathlib import Path

def extract_navixy_field_code(field_str):
    """Extract the Navixy field code from a string.
    
    Handles formats like:
    - "avl_io_205 (GSM Cell ID)" -> "avl_io_205"
    - "can_speed" -> "can_speed"
    - "EVENT" -> "EVENT"
    """
    if not field_str or field_str.strip() == "":
        return None
    
    # Remove backticks if present
    field_str = field_str.strip().strip('`')
    
    # If it contains parentheses, extract the part before the first space and (
    if '(' in field_str:
        # Match pattern like "avl_io_205 (GSM Cell ID)"
        match = re.match(r'^([^\s(]+)', field_str)
        if match:
            return match.group(1)
    
    # If it's just a field code, return as-is
    return field_str.strip()

def extract_navixy_fields_from_csv(csv_path):
    """Extract all unique Navixy field codes from the CSV file."""
    navixy_fields = {}
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            navixy_field = row.get('provider_name', '').strip()
            if not navixy_field or navixy_field.lower() == 'computed':
                continue
            
            field_code = extract_navixy_field_code(navixy_field)
            if field_code:
                # Store with metadata
                if field_code not in navixy_fields:
                    navixy_fields[field_code] = {
                        'name': row.get('name', '').strip(),
                        'fleeti_field': row.get('Fleeti Field', '').strip(),
                        'telemetry_type': row.get('type', '').strip(),
                    }
    
    return navixy_fields

def extract_navixy_fields_from_markdown(md_path):
    """Extract all Navixy field references from the markdown document."""
    navixy_fields_found = set()
    
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match Navixy field references in tables
    # Extract the entire "Navixy: ..." section first, then parse all fields from it
    navixy_section_pattern = r'Navixy:\s*([^|]+?)(?:\s*\||$)'
    navixy_sections = re.finditer(navixy_section_pattern, content)
    
    for section_match in navixy_sections:
        navixy_section = section_match.group(1).strip()
        # Extract all backticked fields from this section
        backtick_matches = re.finditer(r'`([^`]+)`', navixy_section)
        for bt_match in backtick_matches:
            field_str = bt_match.group(1).strip()
            field_code = extract_navixy_field_code(field_str)
            if field_code and field_code.lower() != 'computed':
                navixy_fields_found.add(field_code)
        
        # Also extract fields without backticks but with parentheses (e.g., "field_code (Name)")
        paren_matches = re.finditer(r'([a-z_][a-z0-9_.]+)\s*\(', navixy_section)
        for p_match in paren_matches:
            field_code = p_match.group(1).strip()
            if field_code and field_code.lower() != 'computed':
                navixy_fields_found.add(field_code)
    
    # Also look for fields in backticks that might be Navixy fields
    # Pattern: `field_code` where field_code looks like a Navixy field (including dots)
    backtick_pattern = r'`([a-z_][a-z0-9_.]+)`'
    matches = re.finditer(backtick_pattern, content)
    for match in matches:
        field_code = match.group(1)
        # Check if it looks like a Navixy field (starts with avl_io_, can_, obd_, etc.)
        if any(field_code.startswith(prefix) for prefix in ['avl_io_', 'can_', 'obd_', 'ble_', 'gsm.', 'raw_can_', 'freq_', 'impulse_counter_', 'ext_temp_sensor_', 'lls_', 'temp_sensor', 'hw_mileage', 'raw_mileage', 'fuel_level']):
            navixy_fields_found.add(field_code)
        # Also check for special cases
        if field_code in ['acceleration', 'braking', 'cornering', 'cornering_rad', 'towing', 'EVENT', 'event_code', 'sub_event_code', 'msg_time', 'server_time', 'outputs', 'status', 'alt', 'lat', 'lng', 'heading', 'hdop', 'pdop', 'satellites', 'moving', 'speed', 'adc', 'analog', 'ibutton', 'battery_current', 'battery_level', 'battery_voltage', 'board_voltage', 'external_power_state', 'axis_x', 'axis_y', 'axis_z']:
            navixy_fields_found.add(field_code)
    
    return navixy_fields_found

def normalize_field_code(field_code):
    """Normalize field codes for comparison (handle case variations)."""
    # Convert to lowercase for comparison, but preserve original
    return field_code.lower()

def find_missing_fields(csv_fields, md_fields):
    """Find fields in CSV but not in markdown."""
    missing = []
    
    # Normalize markdown fields for comparison
    md_fields_normalized = {normalize_field_code(f) for f in md_fields}
    
    for field_code, metadata in csv_fields.items():
        normalized = normalize_field_code(field_code)
        if normalized not in md_fields_normalized:
            missing.append({
                'field_code': field_code,
                'name': metadata['name'],
                'fleeti_field': metadata['fleeti_field'],
                'telemetry_type': metadata['telemetry_type'],
            })
    
    return missing

def generate_report(csv_fields, md_fields, missing_fields, output_path):
    """Generate a validation report."""
    total_csv = len(csv_fields)
    total_md = len(md_fields)
    missing_count = len(missing_fields)
    coverage = ((total_csv - missing_count) / total_csv * 100) if total_csv > 0 else 0
    
    report = f"""# Navixy Fields Completeness Validation Report

## Summary Statistics

- **Total Navixy fields in CSV:** {total_csv}
- **Total Navixy fields found in markdown:** {total_md}
- **Missing fields:** {missing_count}
- **Coverage:** {coverage:.2f}%

---

## Status

"""
    
    if missing_count == 0:
        report += "✅ **All Navixy fields are documented in the schema document.**\n"
    else:
        report += f"⚠️ **{missing_count} Navixy field(s) are missing from the schema document.**\n"
    
    report += "\n---\n\n"
    
    if missing_count > 0:
        report += "## Missing Navixy Fields\n\n"
        report += "| Navixy Field Code | Navixy Field Name | Fleeti Field | Telemetry Type |\n"
        report += "|-------------------|-------------------|--------------|----------------|\n"
        
        for field in sorted(missing_fields, key=lambda x: x['field_code']):
            report += f"| `{field['field_code']}` | {field['name']} | `{field['fleeti_field']}` | {field['telemetry_type']} |\n"
        
        report += "\n---\n\n"
        report += "## Recommendations\n\n"
        report += "1. Review each missing field to determine if it should be added to the schema document.\n"
        report += "2. Add missing fields to the appropriate section in `working/fleeti-telemetry-schema-specification.md`.\n"
        report += "3. Ensure the field is placed in the semantically correct section.\n"
        report += "4. Include priority, source logic, and description for each field.\n"
    
    # Optional: List fields in markdown but not in CSV (for reference)
    csv_field_codes = {normalize_field_code(f) for f in csv_fields.keys()}
    md_only_fields = []
    for md_field in md_fields:
        normalized = normalize_field_code(md_field)
        if normalized not in csv_field_codes:
            md_only_fields.append(md_field)
    
    if md_only_fields:
        report += "\n---\n\n"
        report += "## Fields in Markdown but Not in CSV (Reference Only)\n\n"
        report += "The following Navixy fields appear in the markdown but are not in the CSV:\n\n"
        for field in sorted(md_only_fields):
            report += f"- `{field}`\n"
        report += "\n*Note: These may be legacy fields, computed fields, or fields from other sources.*\n"
    
    report += f"\n---\n\n**Report Generated:** {Path(__file__).name}\n"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Validation report written to: {output_path}")
    print(f"\nSummary:")
    print(f"  Total CSV fields: {total_csv}")
    print(f"  Total MD fields: {total_md}")
    print(f"  Missing: {missing_count}")
    print(f"  Coverage: {coverage:.2f}%")

if __name__ == '__main__':
    csv_path = Path('docs/reference/navixy-field-catalog.csv')
    md_path = Path('working/fleeti-telemetry-schema-specification.md')
    output_path = Path('Scripts/navixy_fields_completeness_check.md')
    
    print("Extracting Navixy fields from CSV...")
    csv_fields = extract_navixy_fields_from_csv(csv_path)
    print(f"Found {len(csv_fields)} unique Navixy fields in CSV")
    
    print("\nExtracting Navixy fields from markdown...")
    md_fields = extract_navixy_fields_from_markdown(md_path)
    print(f"Found {len(md_fields)} Navixy field references in markdown")
    
    print("\nComparing fields...")
    missing_fields = find_missing_fields(csv_fields, md_fields)
    
    print("\nGenerating report...")
    generate_report(csv_fields, md_fields, missing_fields, output_path)
    
    if missing_fields:
        print(f"\n⚠️  Found {len(missing_fields)} missing fields. See report for details.")
    else:
        print("\n✅ All fields are documented!")

