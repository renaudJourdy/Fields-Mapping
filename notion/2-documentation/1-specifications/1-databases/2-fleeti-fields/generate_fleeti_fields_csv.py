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
from typing import Dict, List, Optional, Tuple, Any

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
    # Check if this is an array container (field[]) - check this first
    if field_path.endswith("[]"):
        return "array"
    
    # Check if this is an array item property (field[].property)
    if re.search(r'\[\]\.\w+', field_path):
        # This is a property of an array item, not an array itself
        # Extract the property path and look it up in JSON examples
        # e.g., asset.accessories[].id -> look for asset.accessories[0].id or similar
        array_path = field_path.split("[].", 1)[0] + "[]"
        property_path = field_path.split("[].", 1)[1]
        
        # If the property itself is an array (e.g., asset.accessories[].sensors[])
        if property_path.endswith("[]"):
            return "array"
        
        # Try to find the array structure and then the property
        if array_path in json_examples:
            array_example = json_examples[array_path]
            if isinstance(array_example, list) and len(array_example) > 0:
                first_item = array_example[0]
                if isinstance(first_item, dict) and property_path in first_item:
                    prop_value = first_item[property_path]
                    if isinstance(prop_value, dict):
                        if "last_changed_at" in prop_value or "last_updated_at" in prop_value:
                            return "nested_object"
                        if "value" in prop_value and "unit" in prop_value:
                            return "value_unit_object"
                        return "nested_object"
                    elif isinstance(prop_value, list):
                        return "array"
                    else:
                        return "simple_value"
        
        # Fallback: infer from description
        desc_lower = description.lower()
        if "last_changed_at" in desc_lower or "last_updated_at" in desc_lower:
            return "nested_object"
        if "value" in desc_lower and "unit" in desc_lower and "{" in description:
            return "value_unit_object"
        return "simple_value"
    
    # Check JSON examples for exact path match
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

def infer_data_type(field_path: str, json_structure: str, description: str, structure_type: str, json_examples: Dict = None) -> str:
    """Infer JSON data type."""
    # First try to get actual value from JSON examples
    if json_examples:
        if field_path in json_examples:
            value = json_examples[field_path]
            if isinstance(value, list):
                return "array"
            if isinstance(value, dict):
                return "object"
            if isinstance(value, bool):
                return "boolean"
            if isinstance(value, (int, float)):
                return "number"
            if isinstance(value, str):
                return "string"
        
        # For array item properties, check the actual property value
        if "[].]" in field_path or re.search(r'\[\]\.\w+', field_path):
            array_path = field_path.split("[].", 1)[0] + "[]"
            property_path = field_path.split("[].", 1)[1]
            
            if array_path in json_examples:
                array_example = json_examples[array_path]
                if isinstance(array_example, list) and len(array_example) > 0:
                    first_item = array_example[0]
                    if isinstance(first_item, dict) and property_path in first_item:
                        prop_value = first_item[property_path]
                        if isinstance(prop_value, list):
                            return "array"
                        if isinstance(prop_value, dict):
                            return "object"
                        if isinstance(prop_value, bool):
                            return "boolean"
                        if isinstance(prop_value, (int, float)):
                            return "number"
                        if isinstance(prop_value, str):
                            return "string"
    
    # Fallback to parsing JSON structure string
    if json_structure:
        try:
            # Handle both single-line and multi-line JSON
            cleaned = json_structure.strip()
            parsed = json.loads(cleaned)
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

def get_json_structure_from_examples(field_path: str, json_examples: Dict) -> Optional[str]:
    """Get JSON structure from extracted examples. Returns single-line JSON for CSV compatibility."""
    # Try exact path match first
    json_key = f"{field_path}_json"
    if json_key in json_examples:
        # Convert multi-line to single-line for CSV
        json_str = json_examples[json_key]
        try:
            parsed = json.loads(json_str)
            return json.dumps(parsed, separators=(',', ':'))  # Single-line, no spaces
        except:
            # If parsing fails, try to clean up the string
            return json_str.replace('\n', ' ').replace('  ', ' ')
    
    # Try direct path match
    if field_path in json_examples:
        value = json_examples[field_path]
        # Always return JSON string, even for simple values
        return json.dumps(value, separators=(',', ':'))  # Single-line
    
    # For array item properties, try to extract from parent array
    if re.search(r'\[\]\.\w+', field_path):
        array_path = field_path.split("[].", 1)[0] + "[]"
        property_path = field_path.split("[].", 1)[1]
        
        if array_path in json_examples:
            array_example = json_examples[array_path]
            if isinstance(array_example, list) and len(array_example) > 0:
                first_item = array_example[0]
                if isinstance(first_item, dict) and property_path in first_item:
                    prop_value = first_item[property_path]
                    # Always return JSON string, even for simple values
                    return json.dumps(prop_value, separators=(',', ':'))  # Single-line
    
    return None

def generate_json_structure(field_path: str, structure_type: str, data_type: str, unit: str, description: str, json_examples: Dict = None) -> str:
    """Generate JSON structure example, preferring extracted examples. Returns single-line JSON for CSV."""
    # Try to get from extracted examples first
    if json_examples:
        extracted = get_json_structure_from_examples(field_path, json_examples)
        if extracted:
            # Already single-line from get_json_structure_from_examples
            return extracted
    
    # Fallback to generation if no example found
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

def discover_all_fields_from_json(root_obj: Any) -> Dict[str, Dict]:
    """
    Discover all field paths from JSON structures, including nested arrays and objects.
    Returns a dictionary mapping field_path -> field_info.
    """
    discovered_fields = {}
    
    def extract_field_paths(obj: Any, prefix: str = "", visited: set = None) -> None:
        """Recursively extract all field paths from JSON structure."""
        if visited is None:
            visited = set()
        
        # Avoid infinite recursion
        obj_id = id(obj)
        if obj_id in visited:
            return
        visited.add(obj_id)
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                # Build field path
                if prefix:
                    field_path = f"{prefix}.{key}"
                else:
                    field_path = key
                
                # Store the field
                if field_path not in discovered_fields:
                    # Infer structure type
                    if isinstance(value, list):
                        structure_type = "array"
                        data_type = "array"
                    elif isinstance(value, dict):
                        if "last_changed_at" in value or "last_updated_at" in value:
                            structure_type = "nested_object"
                        elif "value" in value and "unit" in value:
                            structure_type = "value_unit_object"
                        else:
                            structure_type = "nested_object"
                        data_type = "object"
                    else:
                        structure_type = "simple_value"
                        if isinstance(value, bool):
                            data_type = "boolean"
                        elif isinstance(value, (int, float)):
                            data_type = "number"
                        else:
                            data_type = "string"
                    
                    # Extract unit if present
                    unit = ""
                    if isinstance(value, dict) and "unit" in value:
                        unit = str(value["unit"])
                    
                    # Generate JSON structure - always return JSON string
                    json_structure = json.dumps(value, separators=(',', ':'))
                    
                    discovered_fields[field_path] = {
                        "field_path": field_path,
                        "structure_type": structure_type,
                        "data_type": data_type,
                        "unit": unit,
                        "json_structure": json_structure,
                        "json_value": value,  # Keep original value for nested extraction
                    }
                
                # Recursively process nested structures
                if isinstance(value, (dict, list)):
                    extract_field_paths(value, field_path, visited)
        
        elif isinstance(obj, list) and len(obj) > 0:
            # Handle arrays - extract array container and array item properties
            array_path = f"{prefix}[]" if prefix else "[]"
            
            if array_path not in discovered_fields:
                discovered_fields[array_path] = {
                    "field_path": array_path,
                    "structure_type": "array",
                    "data_type": "array",
                    "unit": "",
                    "json_structure": json.dumps(obj, separators=(',', ':')),
                    "json_value": obj,
                }
            
            # Extract properties from all array items (union of all properties)
            all_properties = set()
            for item in obj:
                if isinstance(item, dict):
                    all_properties.update(item.keys())
            
            # Create field paths for each property found in any array item
            for prop_key in all_properties:
                # Get first non-None value for this property
                prop_value = None
                for item in obj:
                    if isinstance(item, dict) and prop_key in item:
                        prop_value = item[prop_key]
                        break
                
                if prop_value is not None:
                    # Build array item property path (e.g., asset.accessories[].id)
                    item_prop_path = f"{prefix}[].{prop_key}" if prefix else f"[].{prop_key}"
                    
                    if item_prop_path not in discovered_fields:
                        # Infer structure type for property
                        if isinstance(prop_value, list):
                            structure_type = "array"
                            data_type = "array"
                        elif isinstance(prop_value, dict):
                            if "last_changed_at" in prop_value or "last_updated_at" in prop_value:
                                structure_type = "nested_object"
                            elif "value" in prop_value and "unit" in prop_value:
                                structure_type = "value_unit_object"
                            else:
                                structure_type = "nested_object"
                            data_type = "object"
                        else:
                            structure_type = "simple_value"
                            if isinstance(prop_value, bool):
                                data_type = "boolean"
                            elif isinstance(prop_value, (int, float)):
                                data_type = "number"
                            else:
                                data_type = "string"
                        
                        # Extract unit
                        unit = ""
                        if isinstance(prop_value, dict) and "unit" in prop_value:
                            unit = str(prop_value["unit"])
                        
                        # Generate JSON structure - always return JSON string
                        json_structure = json.dumps(prop_value, separators=(',', ':'))
                        
                        discovered_fields[item_prop_path] = {
                            "field_path": item_prop_path,
                            "structure_type": structure_type,
                            "data_type": data_type,
                            "unit": unit,
                            "json_structure": json_structure,
                            "json_value": prop_value,
                        }
                        
                        # Recursively process nested structures in array item properties
                        if isinstance(prop_value, (dict, list)):
                            # For nested arrays in array items, keep the []. notation
                            # e.g., asset.accessories[].sensors[].type
                            if isinstance(prop_value, list):
                                # Nested array - process it
                                extract_field_paths(prop_value, item_prop_path, visited)
                            else:
                                # Nested object - process properties
                                nested_prefix = item_prop_path.replace("[].", ".")
                                extract_field_paths(prop_value, nested_prefix, visited)
    
    # Process the root object directly
    extract_field_paths(root_obj, "", set())
    
    return discovered_fields

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
    
    # Extract JSON structure examples first - comprehensive extraction
    json_blocks = re.findall(r'```json\n(.*?)\n```', content, re.DOTALL)
    all_parsed_json = []  # Store all parsed JSON for field discovery
    
    for json_block in json_blocks:
        try:
            # Try to parse JSON as-is first
            parsed = json.loads(json_block)
            all_parsed_json.append(parsed)
        except:
            # If parsing fails, try to normalize common placeholders
            try:
                normalized = json_block
                # Replace common placeholders that break JSON parsing
                normalized = re.sub(r':\s*"number"', ': 0', normalized)  # "number" -> 0
                normalized = re.sub(r':\s*"boolean"', ': true', normalized)  # "boolean" -> true
                parsed = json.loads(normalized)
                all_parsed_json.append(parsed)
            except:
                # If still fails, skip this block
                continue
        
        def extract_paths(obj, prefix=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    path = f"{prefix}.{key}" if prefix else key
                    json_examples[path] = value
                    # Store JSON string representation
                    try:
                        json_examples[f"{path}_json"] = json.dumps(value, separators=(',', ':'))
                    except:
                        pass
                    extract_paths(value, path)
            elif isinstance(obj, list) and obj:
                # Store array container
                array_path = f"{prefix}[]" if prefix else "[]"
                json_examples[array_path] = obj
                try:
                    json_examples[f"{array_path}_json"] = json.dumps(obj, separators=(',', ':'))
                except:
                    pass
                
                # Extract properties from ALL array items (union of all properties)
                all_properties = set()
                for item in obj:
                    if isinstance(item, dict):
                        all_properties.update(item.keys())
                
                # Create paths for each property found in any array item
                for item_key in all_properties:
                    # Get first non-None value
                    item_value = None
                    for item in obj:
                        if isinstance(item, dict) and item_key in item:
                            item_value = item[item_key]
                            break
                    
                    if item_value is not None:
                        # Create path like asset.accessories[].id
                        item_prop_path = f"{prefix}[].{item_key}" if prefix else f"[].{item_key}"
                        json_examples[item_prop_path] = item_value
                        try:
                            json_examples[f"{item_prop_path}_json"] = json.dumps(item_value, separators=(',', ':'))
                        except:
                            pass
                        
                        # Recursively extract nested structures
                        if isinstance(item_value, dict):
                            extract_paths(item_value, item_prop_path.replace("[].", "."))
                        elif isinstance(item_value, list) and item_value:
                            extract_paths(item_value, item_prop_path)
        
        extract_paths(parsed)
    
    # Discover all fields from JSON structures (process all parsed JSON blocks)
    discovered_fields = {}
    for parsed_json in all_parsed_json:
        # Process JSON directly without "root" prefix
        fields_from_block = discover_all_fields_from_json(parsed_json)
        discovered_fields.update(fields_from_block)
    
    # Dictionary to store table fields (keyed by field_path)
    table_fields = {}
    
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
                    
                    # Clean field name: replace dots with underscores and strip array brackets
                    field_name = field_path.replace("[]", "").replace(".", "_")
                    
                    # Infer all properties
                    field_type = infer_field_type(source_logic, description)
                    structure_type = infer_structure_type(field_path, description, json_examples)
                    
                    # Generate JSON structure first (uses extracted examples)
                    json_structure = generate_json_structure(field_path, structure_type, "string", "", description, json_examples)
                    
                    # Extract unit from JSON structure or description
                    unit = extract_unit_from_json(json_structure)
                    if not unit:
                        unit_from_desc = extract_unit_from_description(description)
                        if unit_from_desc:
                            unit = unit_from_desc
                    
                    # Also try to extract unit from JSON examples directly
                    if not unit and json_examples:
                        if field_path in json_examples:
                            value = json_examples[field_path]
                            if isinstance(value, dict) and "unit" in value:
                                unit = value["unit"]
                        
                        # For array item properties
                        if re.search(r'\[\]\.\w+', field_path):
                            array_path = field_path.split("[].", 1)[0] + "[]"
                            property_path = field_path.split("[].", 1)[1]
                            if array_path in json_examples:
                                array_example = json_examples[array_path]
                                if isinstance(array_example, list) and len(array_example) > 0:
                                    first_item = array_example[0]
                                    if isinstance(first_item, dict) and property_path in first_item:
                                        prop_value = first_item[property_path]
                                        if isinstance(prop_value, dict) and "unit" in prop_value:
                                            unit = prop_value["unit"]
                    
                    # Infer data type (now with json_examples)
                    data_type = infer_data_type(field_path, json_structure, description, structure_type, json_examples)
                    
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
                    
                    # Fix structure type for known fields
                    if field_path == "provider.time.fleeti_time":
                        structure_type = "simple_value"
                        data_type = "number"
                    
                    # Store table field data
                    table_fields[field_path] = {
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
                    }
                
                i += 1
            continue
        
        i += 1
    
    # Merge discovered fields with table fields
    # Start with table fields (they have priority)
    all_fields = {}
    for field_path, field_data in table_fields.items():
        all_fields[field_path] = field_data
    
    # Helper function to check if a path is a container object
    def is_container_object(field_path: str, table_fields: Dict) -> bool:
        """Check if a field path is a container object that shouldn't be a field."""
        # Root-level containers
        root_containers = ["asset", "status", "location", "connectivity", "motion", "power", "fuel", 
                           "counters", "driving_behavior", "sensors", "diagnostics", "io", "driver", 
                           "device", "other", "provider", "geofences", "trip", "nearby_assets"]
        if field_path in root_containers:
            return True
        
        # Check if this path is a container by seeing if it has sub-properties in table_fields
        # If field_path exists in table_fields, it's explicitly defined, so keep it
        if field_path in table_fields:
            return False
        
        # Check if this is an intermediate container (has children in table_fields)
        # Check if any table field is a sub-property of this path
        for table_path in table_fields.keys():
            # For array containers, check if table_path starts with field_path (e.g., asset.accessories[].id starts with asset.accessories[])
            if field_path.endswith("[]"):
                if table_path.startswith(field_path + ".") or table_path == field_path:
                    # This is a container with subfields, skip it
                    return True
            else:
                # For non-array containers, check if table_path starts with field_path + "."
                if table_path.startswith(field_path + ".") or table_path.startswith(field_path + "[]"):
                    # This is a container, skip it
                    return True
        
        # Known intermediate containers that shouldn't be fields
        intermediate_containers = [
            "asset.group", "asset.installation", "asset.properties", "asset.properties.vehicle",
            "asset.properties.vehicle.powertrain", "asset.properties.equipment", "asset.properties.phone",
            "asset.properties.site", "asset.properties.site.address", "asset.properties.site.location",
            "status.top_status", "status.statuses", "trip", "trip.start_location", "trip.current_location",
            "location.precision", "connectivity.cell", "connectivity.sim", "motion.is_moving",
            "motion.accelerometer", "power.low_voltage_battery", "power.ev", "power.ev.traction_battery",
            "power.ev.charging", "power.ev.motor", "power.ev.range", "driving_behavior.daily_summary",
            "driving_behavior.daily_summary.event_counts", "driving_behavior.daily_summary.eco_score",
            "sensors.environment", "sensors.magnet", "sensors.inertial", "sensors.custom",
            "diagnostics.agricultural", "diagnostics.axles", "diagnostics.body", "diagnostics.body.belts",
            "diagnostics.body.doors", "diagnostics.body.lights", "diagnostics.body.indicators",
            "diagnostics.body.occupancy", "diagnostics.body.safety", "diagnostics.body.climate",
            "diagnostics.brakes", "diagnostics.drivetrain", "diagnostics.engine", "diagnostics.engine.running",
            "diagnostics.fluids", "diagnostics.fluids.oil", "diagnostics.health", "diagnostics.security",
            "diagnostics.security.immobilizer", "diagnostics.systems", "diagnostics.systems.steering",
            "diagnostics.systems.trailer", "diagnostics.systems.control", "diagnostics.systems.utility",
            "io.inputs", "io.inputs.individual", "io.outputs", "io.outputs.individual", "io.analog",
            "driver.id", "driver.privacy_mode", "driver.authorization", "driver.hardware_key",
            "device.battery", "device.bluetooth", "device.power", "device.firmware", "device.identification",
            "other.events", "other.events.eco", "other.events.eco.driving", "other.events.harsh_acceleration",
            "other.events.harsh_braking", "other.events.harsh_cornering", "other.geofence",
            "other.geofence.device_zones", "provider.time"
        ]
        if field_path in intermediate_containers:
            return True
        
        return False
    
    # Add discovered fields that aren't in table
    for field_path, discovered_info in discovered_fields.items():
        if field_path not in all_fields:
            # Skip container objects
            if is_container_object(field_path, table_fields):
                continue
            
            # Generate field name
            field_name = field_path.replace("[]", "").replace(".", "_")
            
            # Skip invalid field names (separator rows, etc.)
            if not field_name or field_name.startswith("-") or len(field_name) < 2:
                continue
            
            # Skip sub-properties of value_unit_objects (value, unit) - parent object is the field
            if field_path.endswith(".value") or field_path.endswith(".unit"):
                # Check if parent is a value_unit_object in table fields
                parent_path = ".".join(field_path.split(".")[:-1])
                if parent_path in table_fields:
                    parent_structure = table_fields[parent_path].get("Structure Type", "")
                    if parent_structure == "value_unit_object":
                        continue
            
            # Infer priority from parent field if it exists in table
            priority = "P3"  # Default
            # Check for parent field in table_fields
            parent_paths = []
            path_parts = field_path.split(".")
            for i in range(len(path_parts)):
                parent = ".".join(path_parts[:i+1])
                if parent.endswith("[]"):
                    parent_paths.append(parent)
                else:
                    parent_paths.append(parent)
            
            # Check parent paths in reverse order (most specific first)
            for parent_path in reversed(parent_paths):
                if parent_path in table_fields:
                    parent_priority = table_fields[parent_path].get("Priority", "")
                    if parent_priority and parent_priority != "?":
                        priority = parent_priority
                        break
            
            # Special handling for status subfields
            if field_path.startswith("status.top_status.") or field_path.startswith("status.statuses[]."):
                priority = "P0"  # Inherit P0 from parent
            
            # Infer category from field path
            inferred_category = "other"
            if field_path.startswith("location.") or field_path == "location":
                inferred_category = "location"
            elif field_path.startswith("motion.") or field_path == "motion":
                inferred_category = "motion"
            elif field_path.startswith("power.") or field_path == "power":
                inferred_category = "power"
            elif field_path.startswith("fuel.") or field_path == "fuel":
                inferred_category = "fuel"
            elif field_path.startswith("connectivity.") or field_path == "connectivity":
                inferred_category = "connectivity"
            elif field_path.startswith("status.") or field_path == "status":
                inferred_category = "status"
            elif field_path.startswith("sensors.") or field_path == "sensors":
                inferred_category = "sensors"
            elif field_path.startswith("diagnostics.") or field_path == "diagnostics":
                inferred_category = "diagnostics"
            elif field_path.startswith("io.") or field_path == "io" or field_path.startswith("driver.") or field_path == "driver":
                inferred_category = "io" if field_path.startswith("io.") or field_path == "io" else "driver"
            elif field_path.startswith("device.") or field_path == "device":
                inferred_category = "device"
            elif field_path.startswith("counters.") or field_path == "counters":
                inferred_category = "counters"
            elif field_path.startswith("driving_behavior.") or "driving" in field_path:
                inferred_category = "driving_behavior"
            elif field_path.startswith("asset.") or field_path == "asset" or field_path == "last_updated_at":
                inferred_category = "metadata"
            elif field_path.startswith("geofences") or field_path == "geofences":
                inferred_category = "metadata"  # Fixed: Geofences are part of telemetry context (metadata)
            elif field_path.startswith("trip.") or field_path == "trip":
                inferred_category = "metadata"  # Fixed: Trip is part of telemetry context (metadata)
            elif field_path.startswith("nearby_assets"):
                inferred_category = "metadata"
            elif field_path.startswith("provider.") or field_path == "provider":
                inferred_category = "metadata"
            elif field_path.startswith("other.") or field_path == "other":
                inferred_category = "other"
            
            # Generate description from field path
            description = f"Field discovered from JSON structure: {field_path}"
            if discovered_info["structure_type"] == "value_unit_object":
                description += f" (value-unit object)"
            elif discovered_info["structure_type"] == "nested_object":
                description += f" (nested object)"
            elif discovered_info["structure_type"] == "array":
                description += f" (array)"
            
            # Infer field type from structure
            field_type = "direct"  # Default
            if discovered_info["structure_type"] == "array":
                field_type = "direct"
            elif "computed" in description.lower() or "derived" in description.lower():
                field_type = "calculated"
            
            # Fix structure type for known fields
            structure_type = discovered_info["structure_type"]
            if field_path == "provider.time.fleeti_time":
                structure_type = "simple_value"  # It's a number, not an object
            
            all_fields[field_path] = {
                "Field Name": field_name,
                "Field Path": field_path,
                "Category": inferred_category,
                "Priority": priority,  # Use inherited priority
                "Field Type": field_type,
                "Structure Type": structure_type,
                "JSON Structure": discovered_info["json_structure"],
                "Data Type": discovered_info["data_type"],
                "Unit": discovered_info["unit"],
                "Description": description,
                "Computation Approach": "",
                "Status": "active",
                "Version Added": "1.0.0",
                "WebSocket Contracts": "",
                "REST API Endpoints": "",
                "Dependencies": "",
                "Notes": "Discovered from JSON structure",
            }
    
    # Add missing fields that should exist based on spec
    # Check for fuel.levels[].unit
    if "fuel.levels[].value" in all_fields and "fuel.levels[].unit" not in all_fields:
        # Check if unit exists in JSON examples
        unit_found = False
        if "fuel.levels[]" in json_examples:
            levels_array = json_examples["fuel.levels[]"]
            if isinstance(levels_array, list) and len(levels_array) > 0:
                first_item = levels_array[0]
                if isinstance(first_item, dict) and "unit" in first_item:
                    unit_value = first_item["unit"]
                    unit_found = True
                    all_fields["fuel.levels[].unit"] = {
                        "Field Name": "fuel_levels_unit",
                        "Field Path": "fuel.levels[].unit",
                        "Category": "fuel",
                        "Priority": "P1",  # Same as fuel.levels[].value
                        "Field Type": "direct",
                        "Structure Type": "simple_value",
                        "JSON Structure": json.dumps(unit_value, separators=(',', ':')),
                        "Data Type": "string",
                        "Unit": "",
                        "Description": "Unit for fuel level measurement (% or l)",
                        "Computation Approach": "",
                        "Status": "active",
                        "Version Added": "1.0.0",
                        "WebSocket Contracts": "",
                        "REST API Endpoints": "",
                        "Dependencies": "",
                        "Notes": "Discovered from JSON structure",
                    }
        
        # If not found in json_examples, add it anyway based on spec structure
        if not unit_found:
            all_fields["fuel.levels[].unit"] = {
                "Field Name": "fuel_levels_unit",
                "Field Path": "fuel.levels[].unit",
                "Category": "fuel",
                "Priority": "P1",  # Same as fuel.levels[].value
                "Field Type": "direct",
                "Structure Type": "simple_value",
                "JSON Structure": '"%"',
                "Data Type": "string",
                "Unit": "",
                "Description": "Unit for fuel level measurement (% or l)",
                "Computation Approach": "",
                "Status": "active",
                "Version Added": "1.0.0",
                "WebSocket Contracts": "",
                "REST API Endpoints": "",
                "Dependencies": "",
                "Notes": "Added based on specification structure",
            }
    
    # Fix structure type for provider.time.fleeti_time if it exists in table fields
    if "provider.time.fleeti_time" in all_fields:
        all_fields["provider.time.fleeti_time"]["Structure Type"] = "simple_value"
        all_fields["provider.time.fleeti_time"]["Data Type"] = "number"
    
    # Remove duplicates - prefer entries with [] notation for arrays
    field_names_seen = {}
    deduplicated_fields = {}
    for field_path, field_data in all_fields.items():
        field_name = field_data["Field Name"]
        
        # Check for duplicates (same field name but different paths)
        if field_name in field_names_seen:
            existing_path = field_names_seen[field_name]
            # Prefer the one with [] notation for arrays
            if "[]" in field_path and "[]" not in existing_path:
                # Replace with the one that has []
                del deduplicated_fields[existing_path]
                deduplicated_fields[field_path] = field_data
                field_names_seen[field_name] = field_path
            elif "[]" not in field_path and "[]" in existing_path:
                # Keep the existing one with []
                continue
            else:
                # Both have [] or neither has [], keep the first one
                continue
        else:
            field_names_seen[field_name] = field_path
            deduplicated_fields[field_path] = field_data
    
    # Filter out invalid rows (separator rows, etc.)
    valid_fields = {}
    for field_path, field_data in deduplicated_fields.items():
        field_name = field_data.get("Field Name", "")
        # Skip invalid field names
        if not field_name or field_name.startswith("-") or len(field_name) < 2:
            continue
        # Skip if field path is invalid
        if not field_path or field_path.startswith("-"):
            continue
        valid_fields[field_path] = field_data
    
    # Convert to list
    return list(valid_fields.values())

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

