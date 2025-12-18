#!/usr/bin/env python3
"""
Generate CSV file from Fleeti Telemetry Schema Specification.

Extracts all Fleeti telemetry fields from the markdown specification
and generates a CSV file suitable for Notion database import.
"""

import re
import csv
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Section to category mapping
SECTION_CATEGORY_MAP = {
    "Root-Level Fields": "metadata",
    "1. Asset Metadata": "metadata",
    "2. Telemetry Context": "status",
    "3. Location": "location",
    "4. Connectivity": "connectivity",
    "5. Motion": "motion",
    "6. Power": "power",
    "7. Fuel": "fuel",
    "8. Counters": "counters",
    "9. Driving Behavior": "driving_behavior",
    "10. Sensors": "sensors",
    "11. Diagnostics": "diagnostics",
    "12. I/O": "io",
    "12. I/O (Inputs/Outputs)": "io",
    "13. Driver": "driver",
    "14. Device": "device",
    "15. Other": "other",
    "16. Packet Metadata": "metadata",
}

def infer_field_type(source_logic: str, description: str) -> str:
    """Infer field type from source/logic column."""
    combined = f"{source_logic.lower()} {description.lower()}"
    
    # Check for computed/calculated
    if "**computed:**" in source_logic.lower() or "computed:" in source_logic.lower() or "derived from" in combined:
        return "calculated"
    
    # Check for asset integration
    if "fleeti" in combined and ("service" in combined or "catalog" in combined):
        return "asset_integrated"
    
    # Check for transformation (static data)
    if "static" in combined or "asset.properties" in combined or "installation" in combined or "tank" in combined:
        return "transformed"
    
    # Check for I/O mapping
    if "i/o" in combined or "input" in combined or "output" in combined or "digital" in combined or "analog" in combined:
        return "io_mapped"
    
    # Check for aggregation
    if "cumulative" in combined or "total" in combined or "count" in combined or "sum" in combined:
        return "aggregated"
    
    # Check for prioritized (multiple sources)
    if "Navixy:" in source_logic:
        sources = source_logic.split("Navixy:")[1].strip()
        if ">" in sources or ("," in sources and len(sources.split(",")) > 2):
            return "prioritized"
        return "direct"
    
    # Check for priority indicators
    if "priority" in combined or "fallback" in combined:
        return "prioritized"
    
    return "direct"

def infer_structure_type(field_path: str, description: str, json_examples: Dict) -> str:
    """Infer structure type from field path and examples."""
    # Check if array
    if "[]" in field_path:
        return "array"
    
    # Check JSON examples
    if field_path in json_examples:
        example = json_examples[field_path]
        if isinstance(example, list):
            return "array"
        if isinstance(example, dict):
            if "last_changed_at" in example or "last_updated_at" in example:
                return "nested_object"
            if "value" in example and "unit" in example:
                return "value_unit_object"
            return "nested_object"
    
    # Check description for structure hints
    desc_lower = description.lower()
    if "last_changed_at" in desc_lower or "last_updated_at" in desc_lower:
        return "nested_object"
    if "value" in desc_lower and "unit" in desc_lower and "{" in description:
        return "value_unit_object"
    
    return "simple_value"

def infer_data_type(field_path: str, json_structure: str, description: str, structure_type: str) -> str:
    """Infer JSON data type."""
    if json_structure:
        try:
            parsed = json.loads(json_structure.replace('"', '"'))
            if isinstance(parsed, list):
                return "array"
            if isinstance(parsed, dict):
                return "object"
            if isinstance(parsed, bool):
                return "boolean"
            if isinstance(parsed, (int, float)):
                return "number"
            if isinstance(parsed, str):
                return "string"
        except:
            pass
    
    # Infer from structure type
    if structure_type == "array":
        return "array"
    if structure_type == "nested_object" or structure_type == "value_unit_object":
        return "object"
    
    # Infer from description
    desc_lower = description.lower()
    if "timestamp" in desc_lower or "epoch" in desc_lower or "milliseconds" in desc_lower:
        return "number"
    if "identifier" in desc_lower or "id" in field_path or "uuid" in desc_lower:
        return "string"
    if "boolean" in desc_lower or "true/false" in desc_lower or "on/off" in desc_lower:
        return "boolean"
    if "number" in desc_lower or "count" in desc_lower or "decimal" in desc_lower or "integer" in desc_lower:
        return "number"
    
    return "string"  # Default

def extract_unit_from_json(json_structure: str) -> str:
    """Extract unit from JSON structure."""
    if not json_structure:
        return ""
    
    # Look for unit in JSON
    unit_match = re.search(r'"unit":\s*"([^"]+)"', json_structure)
    if unit_match:
        return unit_match.group(1)
    
    return ""

def extract_unit_from_description(description: str) -> str:
    """Extract unit from description."""
    # Common units
    unit_patterns = [
        (r'\b(km/h|kmh)\b', 'km/h'),
        (r'\b(m/s|mps)\b', 'm/s'),
        (r'\b(mph)\b', 'mph'),
        (r'°C|degrees? C', '°C'),
        (r'°F|degrees? F', '°F'),
        (r'\b(km)\b', 'km'),
        (r'\b(m|meters?)\b', 'm'),
        (r'\b(l|liters?|litres?)\b', 'l'),
        (r'\b(gal|gallons?)\b', 'gal'),
        (r'\b(%|percent)\b', '%'),
        (r'\b(kwh|kWh)\b', 'kwh'),
        (r'\b(kw|kW)\b', 'kw'),
        (r'\b(h|hours?)\b', 'h'),
        (r'\b(m2|m²|square meters?)\b', 'm2'),
        (r'\b(m3|m³|cubic meters?)\b', 'm3'),
    ]
    
    for pattern, unit in unit_patterns:
        if re.search(pattern, description, re.IGNORECASE):
            return unit
    
    return ""

def generate_json_structure(field_path: str, structure_type: str, data_type: str, unit: str, description: str) -> str:
    """Generate JSON structure example."""
    if structure_type == "simple_value":
        if data_type == "number":
            if "timestamp" in description.lower() or "epoch" in description.lower():
                return "1704067200000"
            return "65.5"
        if data_type == "boolean":
            return "true"
        if data_type == "string":
            if "uuid" in description.lower() or "id" in field_path:
                return '"uuid-1234-5678"'
            return '"example"'
        return "null"
    
    if structure_type == "value_unit_object":
        if unit:
            return f'{{ "value": 65.5, "unit": "{unit}" }}'
        return '{ "value": 65.5, "unit": "km/h" }'
    
    if structure_type == "nested_object":
        if "last_changed_at" in field_path or "last_updated_at" in field_path:
            return '{ "value": true, "last_changed_at": 1704067200000 }'
        if "id" in field_path and "name" in description.lower():
            return '{ "id": "uuid", "name": "example" }'
        return '{ "value": true, "last_changed_at": 1704067200000 }'
    
    if structure_type == "array":
        if unit:
            return f'[{{ "value": 85, "unit": "{unit}" }}]'
        if "id" in field_path:
            return '[{ "id": "uuid", "name": "example" }]'
        return '[{ "value": 85, "unit": "%" }]'
    
    return "null"

def extract_computation_approach(source_logic: str, description: str) -> str:
    """Extract generic computation approach."""
    approach = source_logic
    
    # Remove provider-specific details
    approach = re.sub(r"Navixy:\s*`[^`]+`", "", approach)
    approach = re.sub(r"Navixy:\s*[^,]+(?:,\s*[^,]+)*", "", approach)
    
    # Extract computed/derived logic
    if "**Computed:**" in approach:
        approach = approach.split("**Computed:**")[1].strip()
    elif "Computed:" in approach:
        approach = approach.split("Computed:")[1].strip()
    
    # Remove code backticks but keep text
    approach = re.sub(r"`([^`]+)`", r"\1", approach)
    
    # Clean up
    approach = re.sub(r"\s+", " ", approach)
    approach = approach.strip()
    
    # If still has provider references, try to make generic
    if "Navixy" in approach:
        approach = ""
    
    # If empty or too short, use description if it has computation info
    if not approach or len(approach) < 10:
        if "Derived from" in description:
            return description.split(".")[0] + "." if "." in description else description
        if "Computed" in description:
            return description.split(".")[0] + "." if "." in description else description
        if "**Computed:**" in description:
            return description.split("**Computed:**")[1].strip().split(".")[0] + "."
    
    return approach

def extract_dependencies(source_logic: str, description: str) -> str:
    """Extract field dependencies."""
    dependencies = []
    text = f"{source_logic} {description}"
    
    # Look for field references in backticks
    field_refs = re.findall(r"`([a-z_]+\.[a-z_]+(?:\.[a-z_]+)*)`", text)
    dependencies.extend(field_refs)
    
    # Look for "Derived from" patterns
    derived_from = re.findall(r"Derived from\s+`?([a-z_]+\.[a-z_]+(?:\.[a-z_]+)*)`?", text, re.IGNORECASE)
    dependencies.extend(derived_from)
    
    # Look for "Uses" patterns
    uses_pattern = re.findall(r"Uses\s+`?([a-z_]+\.[a-z_]+(?:\.[a-z_]+)*)`?", text, re.IGNORECASE)
    dependencies.extend(uses_pattern)
    
    # Remove duplicates and empty
    dependencies = list(set([d for d in dependencies if d and len(d) > 3]))
    
    return ", ".join(sorted(dependencies)) if dependencies else ""

def extract_notes(source_logic: str, description: str) -> str:
    """Extract special notes."""
    notes = []
    text = f"{source_logic} {description}"
    
    # Look for note markers
    note_match = re.search(r"\*\*Note:\*\*\s*(.+?)(?:\n|$|\.)", text, re.IGNORECASE | re.DOTALL)
    if note_match:
        note_text = note_match.group(1).strip()
        if len(note_text) < 200:  # Reasonable length
            notes.append(note_text)
    
    important_match = re.search(r"\*\*Important:\*\*\s*(.+?)(?:\n|$|\.)", text, re.IGNORECASE | re.DOTALL)
    if important_match:
        note_text = important_match.group(1).strip()
        if len(note_text) < 200:
            notes.append(f"Important: {note_text}")
    
    if "TBD" in text or "To Be Determined" in text:
        notes.append("TBD - To Be Determined")
    
    if "REQUIRES CLARIFICATION" in text:
        notes.append("REQUIRES CLARIFICATION")
    
    return " | ".join(notes) if notes else ""

def parse_markdown_file(file_path: Path) -> List[Dict]:
    """Parse markdown file and extract all fields."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fields = []
    current_category = "other"
    json_examples = {}
    
    # Extract JSON structure examples first
    json_blocks = re.findall(r'```json\n(.*?)\n```', content, re.DOTALL)
    for json_block in json_blocks:
        try:
            parsed = json.loads(json_block)
            def extract_paths(obj, prefix=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        path = f"{prefix}.{key}" if prefix else key
                        json_examples[path] = value
                        extract_paths(value, path)
                elif isinstance(obj, list) and obj:
                    json_examples[prefix] = obj
                    if isinstance(obj[0], dict):
                        extract_paths(obj[0], prefix)
            extract_paths(parsed)
        except:
            pass
    
    # Split content by sections
    lines = content.split('\n')
    i = 0
    current_category = "other"  # Default category
    
    while i < len(lines):
        line = lines[i]
        
        # Check for section header (H1 or H2)
        section_match = re.match(r'^#+\s+(\d+\.\s+)?(.+)$', line)
        if section_match:
            section_name = section_match.group(2).strip()
            # Map to category - try exact match first, then partial
            category_found = False
            for key, category in SECTION_CATEGORY_MAP.items():
                # Exact match
                if key == section_name:
                    current_category = category
                    category_found = True
                    break
                # Key is contained in section name (e.g., "Location" in "3. Location")
                elif key in section_name:
                    current_category = category
                    category_found = True
                    break
                # Section name starts with key (without number prefix)
                elif "." in key:
                    key_suffix = key.split(".")[-1].strip()
                    if section_name.endswith(key_suffix) or key_suffix in section_name:
                        current_category = category
                        category_found = True
                        break
                else:
                    if section_name.endswith(key) or key in section_name:
                        current_category = category
                        category_found = True
                        break
            # Debug: print section detection
            # print(f"Section: '{section_name}' -> Category: {current_category}")
        
        # Look for "Field Sources & Logic" table
        if "Field Sources & Logic" in line or "Field Sources & Notes" in line:
            # Find the table
            table_start = i
            # Look for table header
            while i < len(lines) and "| Fleeti Field" not in lines[i]:
                i += 1
            
            if i >= len(lines):
                break
            
            # Skip header separator
            i += 1
            if i < len(lines) and re.match(r'^\|[-:\s|]+\|$', lines[i]):
                i += 1
            
            # Parse table rows
            while i < len(lines):
                row_line = lines[i].strip()
                if not row_line.startswith('|') or 'Fleeti Field' in row_line:
                    i += 1
                    continue
                
                # Check if this is the end of the table
                if not row_line or not re.match(r'^\|', row_line):
                    break
                
                # Parse row
                cells = [cell.strip() for cell in row_line.split('|')[1:-1]]
                if len(cells) >= 4:
                    field_path = cells[0].strip('`').strip()
                    priority = cells[1].strip() if len(cells) > 1 else "?"
                    source_logic = cells[2].strip() if len(cells) > 2 else ""
                    description = cells[3].strip() if len(cells) > 3 else ""
                    
                    # Skip if not a valid field
                    if not field_path or field_path == "Fleeti Field" or len(field_path) < 3:
                        i += 1
                        continue
                    
                    # Clean field name (remove array notation for Field Name)
                    field_name = field_path.replace("[]", "")
                    
                    # Infer all properties
                    field_type = infer_field_type(source_logic, description)
                    structure_type = infer_structure_type(field_path, description, json_examples)
                    
                    # Extract unit
                    unit = extract_unit_from_json("")  # Will be refined
                    unit_from_desc = extract_unit_from_description(description)
                    if unit_from_desc:
                        unit = unit_from_desc
                    
                    # Generate JSON structure
                    json_structure = generate_json_structure(field_path, structure_type, "string", unit, description)
                    
                    # Refine unit from JSON structure
                    unit_from_json = extract_unit_from_json(json_structure)
                    if unit_from_json:
                        unit = unit_from_json
                    
                    # Infer data type
                    data_type = infer_data_type(field_path, json_structure, description, structure_type)
                    
                    computation_approach = extract_computation_approach(source_logic, description)
                    dependencies = extract_dependencies(source_logic, description)
                    notes = extract_notes(source_logic, description)
                    
                    # Validate priority
                    if priority not in ["P0", "P1", "P2", "P3", "T", "BL", "?"]:
                        priority = "?"
                    
                    # Infer category from field path if section detection failed
                    inferred_category = current_category
                    if field_path.startswith("location."):
                        inferred_category = "location"
                    elif field_path.startswith("motion."):
                        inferred_category = "motion"
                    elif field_path.startswith("power."):
                        inferred_category = "power"
                    elif field_path.startswith("fuel."):
                        inferred_category = "fuel"
                    elif field_path.startswith("connectivity."):
                        inferred_category = "connectivity"
                    elif field_path.startswith("status."):
                        inferred_category = "status"
                    elif field_path.startswith("sensors."):
                        inferred_category = "sensors"
                    elif field_path.startswith("diagnostics."):
                        inferred_category = "diagnostics"
                    elif field_path.startswith("io.") or field_path.startswith("driver."):
                        inferred_category = "io" if field_path.startswith("io.") else "driver"
                    elif field_path.startswith("device."):
                        inferred_category = "device"
                    elif field_path.startswith("counters."):
                        inferred_category = "counters"
                    elif field_path.startswith("driving_behavior.") or "driving" in field_path:
                        inferred_category = "driving_behavior"
                    elif field_path.startswith("asset.") or field_path == "last_updated_at":
                        inferred_category = "metadata"
                    
                    fields.append({
                        "Field Name": field_name,
                        "Field Path": field_path,
                        "Category": inferred_category,
                        "Priority": priority,
                        "Field Type": field_type,
                        "Structure Type": structure_type,
                        "JSON Structure": json_structure,
                        "Data Type": data_type,
                        "Unit": unit,
                        "Description": description,
                        "Computation Approach": computation_approach,
                        "Status": "active",
                        "Version Added": "1.0.0",
                        "WebSocket Contracts": "",
                        "REST API Endpoints": "",
                        "Dependencies": dependencies,
                        "Notes": notes,
                    })
                
                i += 1
            continue
        
        i += 1
    
    return fields

def main():
    """Main function."""
    # Paths
    script_dir = Path(__file__).parent.resolve()
    project_root = script_dir.parent.parent.parent.parent.parent
    spec_file = project_root / "docs/legacy/fleeti-telemetry-schema-specification.md"
    output_file = script_dir / "fleeti-fields-catalog.csv"
    
    print(f"Reading specification from: {spec_file}")
    print(f"Output will be written to: {output_file}")
    
    # Parse markdown
    fields = parse_markdown_file(spec_file)
    
    print(f"Extracted {len(fields)} fields")
    
    # CSV columns in order
    columns = [
        "Field Name",
        "Field Path",
        "Category",
        "Priority",
        "Field Type",
        "Structure Type",
        "JSON Structure",
        "Data Type",
        "Unit",
        "Description",
        "Computation Approach",
        "Status",
        "Version Added",
        "WebSocket Contracts",
        "REST API Endpoints",
        "Dependencies",
        "Notes",
    ]
    
    # Write CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columns, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        
        for field in fields:
            # Ensure all columns are present
            row = {col: field.get(col, "") for col in columns}
            writer.writerow(row)
    
    print(f"CSV file generated: {output_file}")
    print(f"   Total fields: {len(fields)}")
    
    # Validation summary
    print("\nValidation Summary:")
    print(f"  - Unique field names: {len(set(f['Field Name'] for f in fields))}")
    print(f"  - Categories: {sorted(set(f['Category'] for f in fields))}")
    print(f"  - Priorities: {sorted(set(f['Priority'] for f in fields))}")
    print(f"  - Field Types: {sorted(set(f['Field Type'] for f in fields))}")
    
    # Category distribution
    from collections import Counter
    cat_dist = Counter(f['Category'] for f in fields)
    print(f"\nCategory Distribution:")
    for cat, count in sorted(cat_dist.items()):
        print(f"  - {cat}: {count} fields")

if __name__ == "__main__":
    main()

