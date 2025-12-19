#!/usr/bin/env python3
"""
Generate Fleeti Fields Database CSV from Markdown Specification.

This script parses the fleeti-telemetry-schema-specification.md file and generates
a CSV file matching the export format. It extracts all fields from JSON structures
across all sections and matches them with table metadata.

Input:  input/fleeti-telemetry-schema-specification.md
Output: Fleeti-Fields-YYYY-MM-DD.csv

See specifications/FLEETI_FIELDS_GENERATION_SPEC.md for detailed documentation.
"""

import re
import csv
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# Input file
INPUT_MARKDOWN = Path(__file__).parent / "input" / "fleeti-telemetry-schema-specification.md"

# Output file
OUTPUT_CSV = Path(__file__).parent / "Fleeti-Fields-2025-01-18.csv"

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
    "12. I/O (Inputs/Outputs)": "io",
    "13. Driver": "driver",
    "14. Device": "device",
    "15. Other": "other",
    "16. Packet Metadata": "metadata",
}

def parse_sections(markdown_content: str) -> List[Dict[str, Any]]:
    """Parse markdown file and extract all sections with JSON and tables.
    
    This function processes the markdown file line-by-line to identify:
    1. Section headers (e.g., "# 1. Asset Metadata")
    2. JSON code blocks (between ```json and ```)
    3. Field Sources & Logic tables (markdown tables)
    
    The markdown structure follows this pattern for each section:
    - Section header: # N. Section Name
    - Purpose paragraph: **Purpose:** ...
    - JSON Structure: ```json ... ```
    - Field Sources & Logic table: | Fleeti Field | Priority | ...
    
    Args:
        markdown_content: Full markdown file content
        
    Returns:
        List of section dictionaries, each containing:
        - section_title: Section title (e.g., "1. Asset Metadata")
        - section_number: Section number
        - json_structure: JSON structure string
        - table_rows: List of table row dictionaries
    """
    sections = []
    
    # Regex pattern to match section headers
    # Matches: "# 1. Section Name" or "# Root-Level Fields"
    # Group 1: Section number (if numbered)
    # Group 2: Section name (if numbered)
    # Only matches numbered sections (1-16) or "Root-Level Fields" to skip other headers
    section_pattern = r'^# (?:(\d+)\. (.+)|Root-Level Fields)$'
    
    # Split markdown into lines for line-by-line processing
    lines = markdown_content.split('\n')
    
    # State tracking variables for parsing
    current_section = None      # Current section being processed
    current_json = None         # Accumulated JSON structure string
    in_json_block = False       # Whether we're inside a JSON code block
    json_lines = []             # Lines of current JSON block
    current_table = None        # Accumulated table rows
    in_table = False            # Whether we're inside a table
    table_header_found = False  # Whether we've found the table header row
    
    # Process each line sequentially
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check for section header - this starts a new section
        section_match = re.match(section_pattern, line)
        if section_match:
            # Save previous section if exists (before starting new one)
            if current_section:
                sections.append({
                    'section_title': current_section['title'],
                    'section_number': current_section['number'],
                    'json_structure': current_json,  # May be None if no JSON block found
                    'table_rows': current_table or []  # Empty list if no table found
                })
            
            # Start new section - extract section number and title
            if section_match.group(1):  # Numbered section (e.g., "1. Asset Metadata")
                section_number = section_match.group(1)
                section_title = f"{section_number}. {section_match.group(2)}"
            else:  # Root-Level Fields (special case)
                section_number = "0"
                section_title = "Root-Level Fields"
            
            # Initialize new section state
            current_section = {'title': section_title, 'number': section_number}
            current_json = None
            json_lines = []
            in_json_block = False
            current_table = []
            in_table = False
            table_header_found = False
        
        # Check for JSON code block start (```json)
        elif line.strip().startswith('```json'):
            in_json_block = True
            json_lines = []  # Start accumulating JSON lines
        elif in_json_block:
            # We're inside a JSON code block
            if line.strip().startswith('```'):
                # End of JSON block (closing ```)
                json_content = '\n'.join(json_lines)
                try:
                    # Try to parse to validate JSON syntax
                    # This helps catch malformed JSON early
                    json.loads(json_content)
                    current_json = json_content
                except:
                    # Even if JSON is invalid (e.g., has type descriptions),
                    # keep it as string - we'll handle parsing later
                    current_json = json_content
                in_json_block = False
            else:
                # Accumulate JSON content line
                json_lines.append(line)
        
        # Check for table start - look for header row with "Fleeti Field" and "Priority"
        # Markdown tables have format: | Column1 | Column2 | Column3 |
        elif re.match(r'^\|.*Fleeti Field.*\|', line) and 'Priority' in line:
            # Found table header row - start parsing table
            in_table = True
            table_header_found = True
            # Parse header to get column indices (not used, but good for debugging)
            header_parts = [p.strip() for p in line.split('|')[1:-1]]  # Split by |, remove first/last empty
            current_table = []  # Initialize table rows list
        elif in_table and table_header_found:
            # We're inside a table - process data rows
            # Check for table separator row (| --- | --- |)
            if re.match(r'^\|[\s\-:]+\|', line):
                pass  # Skip separator row (markdown table formatting)
            elif line.strip().startswith('|') and not line.strip().startswith('|---'):
                # This is a data row - parse it
                # Split by | and remove first/last empty strings
                parts = [p.strip() for p in line.split('|')[1:-1]]
                if len(parts) >= 4:  # Ensure we have at least 4 columns
                    # Extract field path (remove markdown backticks if present)
                    # Example: `location.latitude` -> location.latitude
                    field_path = parts[0].strip('`').strip()
                    # Extract priority (P0, P1, P2, P3, T, BL, ?)
                    priority = parts[1].strip() if len(parts) > 1 else ''
                    # Extract source/logic (e.g., "Navixy: `lat`" or "**Computed:** ...")
                    source_logic = parts[2].strip() if len(parts) > 2 else ''
                    # Extract description
                    description = parts[3].strip() if len(parts) > 3 else ''
                    
                    # Store parsed row data
                    current_table.append({
                        'field_path': field_path,
                        'priority': priority,
                        'source_logic': source_logic,
                        'description': description
                    })
            elif not line.strip().startswith('|'):
                # Line doesn't start with | - we've left the table
                in_table = False
        
        i += 1
    
    # Save last section (after loop ends, we need to save the final section)
    if current_section:
        sections.append({
            'section_title': current_section['title'],
            'section_number': current_section['number'],
            'json_structure': current_json,
            'table_rows': current_table or []
        })
    
    return sections

def extract_fields_from_json(json_structure: str, base_path: str = '') -> Dict[str, Any]:
    """Recursively extract all field paths from JSON structure.
    
    The JSON structure may contain type descriptions (e.g., "decimal degrees (-90 to 90)")
    instead of actual values. This function extracts field paths regardless.
    
    Args:
        json_structure: JSON structure as string
        base_path: Base path prefix (for nested objects)
        
    Returns:
        Dictionary mapping field paths to their JSON structure examples
    """
    fields = {}
    
    if not json_structure:
        return fields
    
    # Try to parse JSON - the markdown may contain valid JSON or type descriptions
    # Type descriptions look like: "decimal degrees (-90 to 90)" instead of actual values
    try:
        data = json.loads(json_structure)
    except:
        # JSON parsing failed - likely due to type descriptions instead of values
        # Strategy: Replace type descriptions with placeholder values and retry
        
        cleaned_json = json_structure
        # Replace common type description patterns with valid JSON values
        # These patterns match the markdown specification format
        cleaned_json = re.sub(r'"decimal degrees[^"]*"', '0.0', cleaned_json)  # "decimal degrees (-90 to 90)" -> 0.0
        cleaned_json = re.sub(r'"meters[^"]*"', '0', cleaned_json)            # "meters above sea level" -> 0
        cleaned_json = re.sub(r'"degrees[^"]*"', '0', cleaned_json)            # "degrees (0-359, 0=North)" -> 0
        cleaned_json = re.sub(r'"string[^"]*"', '""', cleaned_json)           # "string (N, NE, E...)" -> ""
        cleaned_json = re.sub(r'"number"', '0', cleaned_json)                  # "number" -> 0
        cleaned_json = re.sub(r'"integer[^"]*"', '0', cleaned_json)           # "integer (0-32)" -> 0
        cleaned_json = re.sub(r'"boolean"', 'true', cleaned_json)             # "boolean" -> true
        cleaned_json = re.sub(r'"uuid"', '""', cleaned_json)                  # "uuid" -> ""
        cleaned_json = re.sub(r'\{ \.\.\. \}', '{}', cleaned_json)            # Handle { ... } placeholders
        cleaned_json = re.sub(r'//.*', '', cleaned_json)                       # Remove JavaScript-style comments
        
        try:
            # Try parsing again with cleaned JSON
            data = json.loads(cleaned_json)
        except:
            # Still failed - use fallback text parsing
            # This handles edge cases where JSON structure is too complex or malformed
            return extract_structure_from_text(json_structure, base_path)
    
    def traverse(obj: Any, path: str = ''):
        """Recursively traverse JSON object to extract all field paths.
        
        This function walks through the JSON structure and extracts every field path,
        handling nested objects, arrays, and special structures like value-unit objects.
        
        Field path examples:
        - Simple: "location.latitude"
        - Nested: "location.precision.hdop"
        - Array container: "status.statuses[]"
        - Array item property: "status.statuses[].family"
        - Value-unit object: "motion.speed" (with {value, unit} structure)
        """
        if isinstance(obj, dict):
            # Process dictionary - iterate over all key-value pairs
            for key, value in obj.items():
                # Build current field path (e.g., "location.latitude" or just "latitude" for root)
                current_path = f"{path}.{key}" if path else key
                
                if isinstance(value, dict):
                    # Value is a nested object - check for special structures
                    # Check if it's a value-unit object (e.g., {value: 45.2, unit: "km"})
                    if 'value' in value and 'unit' in value:
                        # This is a value-unit object - store it as-is
                        fields[current_path] = value
                    # Check if it has timestamp fields (e.g., {value: true, last_changed_at: 123456})
                    elif 'last_changed_at' in value or 'last_updated_at' in value:
                        # This is a nested object with timestamp - store it as-is
                        fields[current_path] = value
                    else:
                        # Regular nested object - store parent path first, then recurse
                        # This ensures parent containers are also available for matching
                        # Example: status.statuses (object container) is stored, not just status.statuses.connectivity
                        fields[current_path] = value
                        # Then recurse to extract nested fields
                        traverse(value, current_path)
                elif isinstance(value, list):
                    # Value is an array
                    # First, add the array container path (e.g., "status.statuses[]")
                    array_path = f"{current_path}[]"
                    fields[array_path] = value
                    
                    # If array contains objects, extract properties from first item
                    # This handles patterns like: statuses: [{family: "connectivity", code: "online"}, ...]
                    if len(value) > 0 and isinstance(value[0], dict):
                        # Traverse first array item to extract property paths
                        for item_key, item_value in value[0].items():
                            # Build path for array item property (e.g., "status.statuses[].family")
                            item_path = f"{current_path}[].{item_key}"
                            
                            if isinstance(item_value, dict):
                                # Property is itself an object - check for special structures
                                if 'value' in item_value and 'unit' in item_value:
                                    fields[item_path] = item_value
                                elif 'last_changed_at' in item_value or 'last_updated_at' in item_value:
                                    fields[item_path] = item_value
                                else:
                                    # Nested object in array item - recurse
                                    traverse(item_value, item_path)
                            else:
                                # Simple property value in array item
                                fields[item_path] = item_value
                else:
                    # Simple value (string, number, boolean, null)
                    fields[current_path] = value
        
        elif isinstance(obj, list) and len(obj) > 0:
            # Handle root-level array (rare case)
            array_path = "[]"
            fields[array_path] = obj
            if isinstance(obj[0], dict):
                # Recurse into first array item
                traverse(obj[0], "")
    
    # Start traversal from root
    traverse(data, base_path)
    return fields

def extract_structure_from_text(json_text: str, base_path: str = '') -> Dict[str, Any]:
    """Extract field structure from JSON-like text with type descriptions.
    
    This is a fallback when JSON parsing fails due to type descriptions.
    It extracts field paths by parsing the JSON structure syntax, handling
    nested objects correctly by matching braces.
    
    Args:
        json_text: JSON-like text with type descriptions
        base_path: Base path prefix
        
    Returns:
        Dictionary mapping field paths to placeholder values
    """
    fields = {}
    
    def find_matching_brace(text: str, start_pos: int) -> int:
        """Find the matching closing brace for an opening brace at start_pos."""
        depth = 0
        i = start_pos
        while i < len(text):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    return i
            i += 1
        return -1
    
    def find_matching_bracket(text: str, start_pos: int) -> int:
        """Find the matching closing bracket for an opening bracket at start_pos."""
        depth = 0
        i = start_pos
        while i < len(text):
            if text[i] == '[':
                depth += 1
            elif text[i] == ']':
                depth -= 1
                if depth == 0:
                    return i
            i += 1
        return -1
    
    def extract_nested(path: str, text: str, depth: int = 0):
        """Recursively extract nested structures, handling nested braces correctly."""
        if depth > 20:  # Prevent infinite recursion
            return
        
        # Pattern to find key-value pairs: "key": ...
        key_pattern = r'"([^"]+)":\s*'
        
        i = 0
        while i < len(text):
            # Find next key
            match = re.search(key_pattern, text[i:])
            if not match:
                break
            
            key_start = i + match.start()
            key_end = i + match.end()
            key = match.group(1)
            current_path = f"{path}.{key}" if path else key
            
            # Skip whitespace after colon
            value_start = key_end
            while value_start < len(text) and text[value_start] in ' \t\n':
                value_start += 1
            
            if value_start >= len(text):
                break
            
            # Determine value type
            if text[value_start] == '"':
                # String value - find closing quote
                quote_end = value_start + 1
                while quote_end < len(text):
                    if text[quote_end] == '"' and text[quote_end - 1] != '\\':
                        break
                    quote_end += 1
                if quote_end < len(text):
                    value = text[value_start + 1:quote_end]
                    fields[current_path] = value
                    i = quote_end + 1
                else:
                    i = value_start + 1
            elif text[value_start] == '{':
                # Object value - find matching brace
                brace_end = find_matching_brace(text, value_start)
                if brace_end > value_start:
                    obj_text = text[value_start + 1:brace_end]
                    fields[current_path] = {}  # Placeholder
                    extract_nested(current_path, obj_text, depth + 1)
                    i = brace_end + 1
                else:
                    i = value_start + 1
            elif text[value_start] == '[':
                # Array value - find matching bracket
                bracket_end = find_matching_bracket(text, value_start)
                if bracket_end > value_start:
                    array_text = text[value_start + 1:bracket_end]
                    array_path = f"{current_path}[]"
                    fields[array_path] = []  # Placeholder
                    # Try to extract array item structure
                    if '{' in array_text:
                        extract_nested(current_path, array_text, depth + 1)
                    i = bracket_end + 1
                else:
                    i = value_start + 1
            else:
                # Simple value (number, boolean, null) - find next comma or brace
                value_end = value_start
                while value_end < len(text) and text[value_end] not in ',}':
                    value_end += 1
                value = text[value_start:value_end].strip()
                fields[current_path] = value
                i = value_end
    
    # Remove outer braces and extract
    cleaned = json_text.strip()
    if cleaned.startswith('{') and cleaned.endswith('}'):
        cleaned = cleaned[1:-1]
    
    extract_nested(base_path, cleaned)
    return fields

def generate_field_name(field_path: str) -> str:
    """Convert field path to stable field name identifier.
    
    Field names are stable identifiers used throughout the system. They don't change
    even if field paths are reorganized. This function converts hierarchical paths
    to flat snake_case identifiers.
    
    Examples:
        location.latitude -> location_latitude
        status.statuses[].family -> status_statuses_family
        location.precision.hdop -> location_precision_hdop
    
    Args:
        field_path: Field path (e.g., 'location.latitude' or 'status.statuses[].family')
        
    Returns:
        Field name in snake_case (e.g., 'location_latitude' or 'status_statuses_family')
    """
    # Remove array notation - [] becomes empty, []. becomes _
    # Example: "status.statuses[].family" -> "status.statuses_family"
    clean_path = field_path.replace('[]', '').replace('[].', '_')
    # Convert dots to underscores to create flat identifier
    # Example: "location.latitude" -> "location_latitude"
    field_name = clean_path.replace('.', '_')
    return field_name

def infer_field_type(source_logic: str, description: str) -> str:
    """Determine field type from source/logic column.
    
    Field type determines how the field is mapped/transformed:
    - direct: 1:1 mapping from provider field
    - prioritized: Multiple provider fields with priority order
    - calculated: Computed from other fields
    - asset_integrated: From Fleeti asset service/catalog
    - transformed: Combined with static asset data
    - io_mapped: Mapped from I/O inputs/outputs
    - aggregated: Cumulative/total values
    
    Args:
        source_logic: Source/Logic text from table (e.g., "Navixy: `lat`" or "**Computed:** ...")
        description: Field description
        
    Returns:
        Field type: 'direct', 'calculated', 'asset_integrated', 'transformed', 'io_mapped', 'aggregated', 'prioritized'
    """
    # Combine source/logic and description for pattern matching
    combined = f"{source_logic.lower()} {description.lower()}"
    
    # Check for computed/calculated fields
    # Pattern: "**Computed:** ..." or "Derived from ..."
    if "**computed:**" in source_logic.lower() or "computed:" in source_logic.lower() or "derived from" in combined:
        return "calculated"
    
    # Check for asset integration (from Fleeti services)
    # Pattern: "Fleeti Asset service" or "Fleeti catalog"
    if "fleeti" in combined and ("service" in combined or "catalog" in combined or "asset service" in combined):
        return "asset_integrated"
    
    # Check for transformation (combines telemetry with static data)
    # Pattern: "static", "asset.properties", "installation", "tank"
    if "static" in combined or "asset.properties" in combined or "installation" in combined or "tank" in combined:
        return "transformed"
    
    # Check for I/O mapping (digital/analog inputs/outputs)
    # Pattern: "I/O", "input", "output", "digital", "analog"
    if "i/o" in combined or "input" in combined or "output" in combined or "digital" in combined or "analog" in combined:
        return "io_mapped"
    
    # Check for aggregation (cumulative values)
    # Pattern: "cumulative", "total", "count", "sum"
    if "cumulative" in combined or "total" in combined or "count" in combined or "sum" in combined:
        return "aggregated"
    
    # Check for prioritized mapping (multiple provider sources)
    if "Navixy:" in source_logic:
        # Extract sources after "Navixy:"
        sources = source_logic.split("Navixy:")[1].strip()
        # Check if multiple sources (comma-separated) or priority indicator (>)
        if ">" in sources or ("," in sources and len([s for s in sources.split(",") if s.strip()]) > 1):
            return "prioritized"
        # Single source = direct mapping
        return "direct"
    
    # Check for explicit priority indicators
    if "priority" in combined or "fallback" in combined:
        return "prioritized"
    
    # Default: direct mapping (single provider field)
    return "direct"

def infer_structure_type(field_path: str, json_value: Any, description: str) -> str:
    """Determine structure type from JSON value and field path.
    
    Args:
        field_path: Field path (e.g., 'location.latitude' or 'motion.speed')
        json_value: JSON value from structure
        description: Field description
        
    Returns:
        Structure type: 'simple_value', 'value_unit_object', 'nested_object', 'array'
    """
    # Check if this is an array container
    if field_path.endswith("[]"):
        return "array"
    
    # Check if this is an array item property
    if "[].]" in field_path or re.search(r'\[\]\.\w+', field_path):
        # Property of array item
        if isinstance(json_value, dict):
            if "last_changed_at" in json_value or "last_updated_at" in json_value:
                return "nested_object"
            if "value" in json_value and "unit" in json_value:
                return "value_unit_object"
            return "nested_object"
        elif isinstance(json_value, list):
            return "array"
        else:
            return "simple_value"
    
    # Check JSON value type
    if isinstance(json_value, list):
        return "array"
    if isinstance(json_value, dict):
        if "last_changed_at" in json_value or "last_updated_at" in json_value:
            return "nested_object"
        if "value" in json_value and "unit" in json_value:
            return "value_unit_object"
        return "nested_object"
    
    # Check description for hints
    desc_lower = description.lower()
    if "last_changed_at" in desc_lower or "last_updated_at" in desc_lower:
        return "nested_object"
    if "value" in desc_lower and "unit" in desc_lower and "{" in description:
        return "value_unit_object"
    
    return "simple_value"

def infer_data_type(field_path: str, json_value: Any, structure_type: str, description: str = '') -> str:
    """Infer JSON data type from value and structure.
    
    Args:
        field_path: Field path
        json_value: JSON value from structure
        structure_type: Inferred structure type
        description: Field description (for fallback inference)
        
    Returns:
        Data type: 'number', 'string', 'boolean', 'object', 'array', 'null'
    """
    # For array item properties, check the actual property value
    if "[].]" in field_path or re.search(r'\[\]\.\w+', field_path):
        # This is a property of an array item
        if isinstance(json_value, list):
            return "array"
        if isinstance(json_value, dict):
            return "object"
        if isinstance(json_value, bool):
            return "boolean"
        if isinstance(json_value, (int, float)):
            return "number"
        if isinstance(json_value, str):
            # Check if it's a type description
            if "number" in json_value.lower() or "integer" in json_value.lower() or "decimal" in json_value.lower():
                return "number"
            if "boolean" in json_value.lower():
                return "boolean"
            return "string"
        # Try to infer from description
        if "number" in description.lower() or "integer" in description.lower() or "decimal" in description.lower():
            return "number"
        if "boolean" in description.lower():
            return "boolean"
        return "string"
    
    # Check structure type
    if structure_type == "array":
        return "array"
    if structure_type in ["nested_object", "value_unit_object"]:
        return "object"
    
    # Check actual JSON value
    if isinstance(json_value, list):
        return "array"
    if isinstance(json_value, dict):
        return "object"
    if isinstance(json_value, bool):
        return "boolean"
    if isinstance(json_value, (int, float)):
        return "number"
    if isinstance(json_value, str):
        # Check if it's a type description
        if "number" in json_value.lower() or "integer" in json_value.lower() or "decimal" in json_value.lower():
            return "number"
        if "boolean" in json_value.lower():
            return "boolean"
        if "uuid" in json_value.lower():
            return "string"
        return "string"
    
    # Fallback: infer from description or field path
    desc_lower = description.lower()
    if "number" in desc_lower or "integer" in desc_lower or "decimal" in desc_lower or "timestamp" in desc_lower:
        return "number"
    if "boolean" in desc_lower or "true" in desc_lower or "false" in desc_lower:
        return "boolean"
    if "array" in desc_lower or "list" in desc_lower:
        return "array"
    
    # Default to string if we can't determine
    return "string"

def extract_unit_from_json(json_value: Any, description: str) -> str:
    """Extract unit from JSON value or description.
    
    Args:
        json_value: JSON value from structure
        description: Field description
        
    Returns:
        Unit string (e.g., 'km/h', 'degrees', 'meters') or empty string
    """
    # Check if JSON value is a value-unit object
    if isinstance(json_value, dict) and "unit" in json_value:
        return json_value["unit"]
    
    # Try to extract from description
    # Look for patterns like "km/h", "degrees", "meters", etc.
    unit_patterns = [
        r'\(([^)]+)\)',  # Units in parentheses
        r'(\w+/\w+)',   # Compound units like km/h
        r'(\w+)',       # Simple units
    ]
    
    for pattern in unit_patterns:
        matches = re.findall(pattern, description)
        for match in matches:
            if match.lower() in ['km/h', 'm/s', 'l/100km', 'kwh/100km', 'm2', '°c', '°f']:
                return match
            if match.lower() in ['degrees', 'meters', 'km', 'm', 'l', 'h', 's', 'kw', 'kwh', 'none']:
                return match
    
    return ""

def extract_computation_approach(source_logic: str) -> str:
    """Extract computation approach from source/logic if computed.
    
    Args:
        source_logic: Source/Logic text from table
        
    Returns:
        Computation approach string or empty string
    """
    if "**computed:**" in source_logic.lower() or "computed:" in source_logic.lower():
        # Extract text after "Computed:"
        match = re.search(r'[Cc]omputed:\s*(.+)', source_logic, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    if "derived from" in source_logic.lower():
        return source_logic.strip()
    
    return ""

def extract_dependencies(source_logic: str, description: str) -> str:
    """Extract dependencies from source/logic or description.
    
    Args:
        source_logic: Source/Logic text from table
        description: Field description
        
    Returns:
        Comma-separated list of dependency field names or empty string
    """
    dependencies = []
    
    # Look for field references in backticks or field paths
    # Pattern: `field.path` or field.path
    field_pattern = r'`?([a-z_]+\.[a-z_\.]+)`?'
    
    for text in [source_logic, description]:
        matches = re.findall(field_pattern, text)
        for match in matches:
            # Convert field path to field name
            field_name = generate_field_name(match)
            if field_name not in dependencies:
                dependencies.append(field_name)
    
    return ", ".join(dependencies) if dependencies else ""

def extract_provider_fields(source_logic: str) -> str:
    """Extract provider field references from source/logic.
    
    Args:
        source_logic: Source/Logic text from table
        
    Returns:
        Comma-separated list of provider field names or empty string
    """
    provider_fields = []
    
    # Look for Navixy: field references
    if "Navixy:" in source_logic:
        navixy_part = source_logic.split("Navixy:")[1].strip()
        # Extract field names in backticks
        field_pattern = r'`([a-z_0-9]+)`'
        matches = re.findall(field_pattern, navixy_part)
        provider_fields.extend(matches)
    
    return ", ".join(provider_fields) if provider_fields else ""

def format_json_structure(json_value: Any) -> str:
    """Format JSON value as string for CSV.
    
    Args:
        json_value: JSON value
        
    Returns:
        Formatted JSON string (triple-quoted for CSV)
    """
    if json_value is None:
        return ""
    
    # Format as JSON string with proper escaping
    json_str = json.dumps(json_value, ensure_ascii=False)
    # Wrap in triple quotes for CSV (escape quotes properly)
    return f'"""{json_str}"""'

def find_closest_json_field(table_path: str, json_fields: Dict[str, Any]) -> Optional[str]:
    """Find closest matching JSON field path for a table field path.
    
    This function handles cases where table paths don't exactly match JSON paths,
    such as when table uses array notation `[]` but JSON has an object structure.
    
    Matching strategies (in order):
    1. Exact match
    2. Remove array notation `[]` and try match (e.g., `status.statuses[]` → `status.statuses`)
    3. Remove array item property notation `[].` and try match (e.g., `status.statuses[].code` → `status.statuses.code`)
    4. Partial match (table path is prefix of JSON path)
    5. Normalized match (remove all array notation and compare)
    
    Args:
        table_path: Field path from table (e.g., "status.statuses[]")
        json_fields: Dictionary of JSON field paths to values
        
    Returns:
        Closest matching JSON field path, or None if no match found
    """
    # Strategy 1: Exact match
    if table_path in json_fields:
        return table_path
    
    # Strategy 2: Remove array notation `[]` from end
    # Example: "status.statuses[]" → "status.statuses"
    path_without_array = table_path.rstrip('[]')
    if path_without_array in json_fields:
        return path_without_array
    
    # Strategy 3: Remove array item property notation `[].`
    # Example: "status.statuses[].code" → "status.statuses.code"
    path_without_array_prop = re.sub(r'\[\]\.', '.', table_path)
    if path_without_array_prop in json_fields:
        return path_without_array_prop
    
    # Strategy 4: Partial match - check if table path (normalized) is a prefix of any JSON path
    # Example: "status.statuses" matches "status.statuses.connectivity"
    clean_table_path = path_without_array.rstrip('.')
    for json_path in json_fields.keys():
        # Check if normalized table path is a prefix of JSON path
        if json_path.startswith(clean_table_path + '.') or json_path == clean_table_path:
            return json_path
    
    # Strategy 5: Normalized match - remove all array notation from both and compare
    # Example: "status.statuses[]" matches "status.statuses" (object)
    clean_table = re.sub(r'\[\]', '', table_path).rstrip('.')
    for json_path in json_fields.keys():
        clean_json = re.sub(r'\[\]', '', json_path).rstrip('.')
        if clean_table == clean_json:
            return json_path
    
    # Strategy 6: Try matching parent path if table path has array notation
    # Example: "status.statuses[].last_changed_at" might match "status.statuses" (parent object)
    if '[]' in table_path:
        # Extract parent path before array notation
        parent_match = re.match(r'^(.+?)\[', table_path)
        if parent_match:
            parent_path = parent_match.group(1)
            if parent_path in json_fields:
                return parent_path
    
    # Strategy 7: Try matching by removing parent prefix from table path
    # Example: Table has "status.statuses[]" but JSON might have "statuses" (missing status prefix)
    # This handles cases where JSON extraction didn't preserve full path
    # NOTE: We return the JSON field path (statuses) not the table path (status.statuses)
    # because the JSON fields dict only contains what was extracted from JSON
    if '.' in table_path:
        # Try removing first segment (e.g., "status.statuses[]" → "statuses[]")
        parts = table_path.split('.', 1)
        if len(parts) > 1:
            remaining_path = parts[1]
            # Remove array notation and try match
            remaining_clean = remaining_path.rstrip('[]')
            if remaining_clean in json_fields:
                # Found match - return the JSON field path (what exists in json_fields)
                return remaining_clean
    
    # No match found
    return None

def match_fields_with_table(json_fields: Dict[str, Any], table_rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Match JSON fields with table rows by field path.
    
    **IMPORTANT: JSON-first approach**
    - Field Path and Field Name ALWAYS come from JSON structure (source of truth)
    - Table provides only metadata: Priority, Source/Logic, Description
    
    This function performs a two-way matching:
    1. For each JSON field, find matching table row (if exists) - use JSON field_path
    2. For each table row, try to find matching JSON field (fuzzy matching) - use JSON field_path if found
    
    This ensures:
    - All JSON fields are included (even if not in table) - uses JSON field_path
    - All table rows are included (even if computed, not in JSON) - tries to match JSON first
    - Field paths always reflect JSON structure, not table notation
    
    Args:
        json_fields: Dictionary of field paths to JSON values (from JSON structure)
        table_rows: List of table row dictionaries (from Field Sources & Logic table)
        
    Returns:
        List of matched field dictionaries ready for CSV generation
        Each dict contains:
        - field_path: Always from JSON structure (source of truth)
        - json_value: JSON value from structure
        - priority: From table (if matched)
        - source_logic: From table (if matched)
        - description: From table (if matched)
        - matched: Boolean indicating if table metadata was found
    """
    matched_fields = []
    
    # Create lookup dictionary for fast table row lookup by field path
    # Key: field_path from table (e.g., "location.latitude" or "status.statuses[]")
    # Value: table row dict with priority, source_logic, description
    table_lookup = {row['field_path']: row for row in table_rows}
    
    # Track which table rows have been matched to avoid duplicates
    matched_table_paths = set()
    
    # Step 1: Process all JSON fields (JSON-first approach)
    # For each field found in JSON structure, try to find matching table row
    for json_field_path, json_value in json_fields.items():
        # Try exact match first
        table_row = table_lookup.get(json_field_path)
        
        if table_row:
            # Found exact matching table row - use JSON field_path with table metadata
            matched_fields.append({
                'field_path': json_field_path,  # Always use JSON path (source of truth)
                'json_value': json_value,
                'priority': table_row['priority'],
                'source_logic': table_row['source_logic'],
                'description': table_row['description'],
                'matched': True  # Flag indicating we have table metadata
            })
            matched_table_paths.add(table_row['field_path'])
        else:
            # No exact match - try fuzzy matching (table might use different notation)
            # Example: JSON has "status.statuses" (object) but table has "status.statuses[]" (array)
            closest_table_path = None
            for table_path in table_lookup.keys():
                # Try to match by comparing normalized paths
                json_normalized = json_field_path.replace('[]', '').replace('[].', '.')
                table_normalized = table_path.replace('[]', '').replace('[].', '.')
                if json_normalized == table_normalized:
                    closest_table_path = table_path
                    break
            
            if closest_table_path:
                # Found fuzzy match - use JSON field_path with table metadata
                table_row = table_lookup[closest_table_path]
                matched_fields.append({
                    'field_path': json_field_path,  # Always use JSON path (source of truth)
                    'json_value': json_value,
                    'priority': table_row['priority'],
                    'source_logic': table_row['source_logic'],
                    'description': table_row['description'],
                    'matched': True
                })
                matched_table_paths.add(closest_table_path)
            else:
                # JSON field exists but no table row match - generate with defaults
                # This can happen if JSON structure has fields not documented in table
                matched_fields.append({
                    'field_path': json_field_path,  # Always use JSON path
                    'json_value': json_value,
                    'priority': '',
                    'source_logic': '',
                    'description': '',
                    'matched': False  # Flag indicating no table metadata
                })
    
    # Step 2: Process table rows that weren't matched to JSON fields
    # These are typically computed fields that don't appear in JSON structure
    # Example: location.cardinal_direction (computed from location.heading)
    # BUT: Try to find closest JSON field first using fuzzy matching
    # IMPORTANT: Always prioritize JSON field paths over table paths
    for table_row in table_rows:
        table_path = table_row['field_path']
        
        # Skip if already matched
        if table_path in matched_table_paths:
            continue
        
        # Try to find closest JSON field using fuzzy matching
        # This handles cases like: table has "status.statuses[]" but JSON has "status.statuses" (object)
        closest_json_path = find_closest_json_field(table_path, json_fields)
        
        if closest_json_path:
            # Found matching JSON field - use JSON field_path with table metadata
            # IMPORTANT: If table path is more complete (e.g., "status.statuses[]" vs "statuses"),
            # prefer the table path (without array notation) as it reflects the actual JSON structure
            # This handles cases where JSON extraction didn't preserve full path
            # The table path "status.statuses[]" better reflects the JSON structure than "statuses"
            if '.' in table_path and '.' not in closest_json_path:
                # Table path is more complete - use it (without array notation) as it reflects JSON structure
                preferred_path = table_path.rstrip('[]')
            else:
                # Use JSON path as-is (it's already complete)
                preferred_path = closest_json_path
            
            json_value = json_fields[closest_json_path]  # Use JSON path to get value from json_fields dict
            matched_fields.append({
                'field_path': preferred_path,  # Use preferred path (table if more complete, else JSON)
                'json_value': json_value,
                'priority': table_row['priority'],
                'source_logic': table_row['source_logic'],
                'description': table_row['description'],
                'matched': True
            })
            matched_table_paths.add(table_path)
        else:
            # No JSON field found - this is a computed field not in JSON structure
            # This should be rare - most fields should be in JSON
            # Use table field_path as fallback, but this indicates a potential issue:
            # either the field is truly computed (not in JSON) or JSON structure is incomplete
            matched_fields.append({
                'field_path': table_path,  # Use table path as fallback (computed field without JSON)
                'json_value': None,  # No JSON value (computed field)
                'priority': table_row['priority'],
                'source_logic': table_row['source_logic'],
                'description': table_row['description'],
                'matched': True  # We have table metadata
            })
    
    return matched_fields

def generate_csv_row(field_data: Dict[str, Any], category: str) -> Dict[str, str]:
    """Generate CSV row from JSON field data.
    
    **JSON-only approach**: This function generates CSV rows directly from JSON structure.
    Field paths and names come ONLY from JSON. Metadata columns (Priority, Source/Logic,
    Description) are left empty and can be filled manually later.
    
    Args:
        field_data: Field dictionary containing:
            - field_path: Field path from JSON (e.g., "location.latitude")
            - json_value: JSON value from structure
        category: Section category (e.g., "location", "motion")
        
    Returns:
        Dictionary with CSV column names as keys, ready for CSV writing
    """
    # Extract field data (JSON-only, no table metadata)
    field_path = field_data['field_path']
    json_value = field_data.get('json_value')
    
    # Generate stable field name identifier from field path
    # Example: "location.latitude" -> "location_latitude"
    field_name = generate_field_name(field_path)
    
    # Infer field properties from JSON structure only
    # Structure Type: JSON structure (simple_value, value_unit_object, etc.)
    structure_type = infer_structure_type(field_path, json_value, '')
    # Data Type: JSON data type (number, string, boolean, etc.)
    data_type = infer_data_type(field_path, json_value, structure_type, '')
    # Unit: Extract from JSON value only (no description available)
    unit = extract_unit_from_json(json_value, '') if json_value else ""
    # JSON Structure: Formatted JSON value for CSV
    json_structure = format_json_structure(json_value) if json_value else ""
    
    # Field Type: Infer from JSON structure only (default to 'direct' for fields in JSON)
    # Since fields are in JSON structure, they're typically direct mappings
    field_type = 'direct'
    
    # Metadata columns are empty (to be filled manually later)
    computation_approach = ''
    dependencies = ''
    description = ''
    priority = ''
    provider_fields = ''
    
    # Generate CSV row dictionary matching export format
    # Column order matches the export CSV exactly
    return {
        'Name': field_name,
        'Category': category,
        'Computation Approach': computation_approach,  # Empty - JSON-only
        'Data Type': data_type,
        'Dependencies': dependencies,  # Empty - JSON-only
        'Description': description,  # Empty - JSON-only
        'Field Path': field_path,  # Always from JSON structure
        'Field Type': field_type,
        'JSON Structure': json_structure,
        'Mapping Fields (db)': '',  # Empty - requires manual input (Notion relation)
        'Notes': '',  # Empty - for manual notes
        'Priority': priority,  # Empty - JSON-only
        'REST API Endpoints': '',  # Empty - requires manual input
        'Status': 'inactive',  # Default for newly generated fields
        'Structure Type': structure_type,
        'Unit': unit,
        'Version Added': '1.0.0',  # Default version
        'WebSocket Contracts': '',  # Empty - requires manual input
        '💽 Provider Field (db)': provider_fields  # Empty - JSON-only
    }

def main():
    """Main processing function.
    
    **JSON-only approach**: Generates Fleeti Fields CSV directly from JSON structures
    in the markdown specification. Field paths and names come ONLY from JSON.
    No table matching or fallback mechanisms.
    
    Orchestrates the entire pipeline:
    1. Read markdown specification file
    2. Parse sections (extract JSON structures)
    3. For each section:
       - Extract fields from JSON structure recursively
       - Generate CSV rows directly from JSON fields
    4. Write CSV file with all field entries
    
    Metadata columns (Priority, Source/Logic, Description) are left empty
    and can be filled manually later in Notion.
    
    The output CSV matches the export format exactly and can be imported
    into Notion or used for further processing.
    """
    print(f"Reading markdown file: {INPUT_MARKDOWN}")
    
    # Step 1: Read markdown specification file
    # UTF-8 encoding handles all Unicode characters (emojis, special chars, etc.)
    with open(INPUT_MARKDOWN, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Step 2: Parse markdown to extract sections
    # Each section contains: JSON structure and Field Sources & Logic table
    print("Parsing sections...")
    sections = parse_sections(markdown_content)
    print(f"Found {len(sections)} sections")
    
    # Step 3: Process each section to generate CSV rows
    all_csv_rows = []
    
    for section in sections:
        section_title = section['section_title']
        section_number = section['section_number']
        json_structure = section['json_structure']  # May be None
        table_rows = section['table_rows']  # May be empty list
        
        # Skip sections without JSON structure
        # JSON is the only source of truth for field definitions
        if not json_structure:
            continue
        
        print(f"\nProcessing section: {section_title}")
        
        # Get category for this section (maps to Notion database category)
        category = SECTION_CATEGORY_MAP.get(section_title, "other")
        
        # Step 3: Extract all field paths from JSON structure and generate CSV rows
        # JSON-only approach: Generate fields directly from JSON structure
        # No table matching - field paths and names come ONLY from JSON
        if json_structure:
            # Recursively extract all field paths from JSON
            json_fields = extract_fields_from_json(json_structure)
            print(f"  Extracted {len(json_fields)} fields from JSON")
            
            # Generate CSV rows directly from JSON fields
            for field_path, json_value in json_fields.items():
                # Create field data dictionary with only JSON information
                field_data = {
                    'field_path': field_path,
                    'json_value': json_value
                }
                csv_row = generate_csv_row(field_data, category)
                all_csv_rows.append(csv_row)
            
            print(f"  Generated {len(json_fields)} field entries from JSON")
    
    # Step 4: Write CSV file
    if all_csv_rows:
        # Column order must match export CSV exactly
        # This ensures compatibility with Notion import and other tools
        fieldnames = [
            'Name',
            'Category',
            'Computation Approach',
            'Data Type',
            'Dependencies',
            'Description',
            'Field Path',
            'Field Type',
            'JSON Structure',
            'Mapping Fields (db)',
            'Notes',
            'Priority',
            'REST API Endpoints',
            'Status',
            'Structure Type',
            'Unit',
            'Version Added',
            'WebSocket Contracts',
            '💽 Provider Field (db)'
        ]
        
        print(f"\nWriting {len(all_csv_rows)} rows to CSV...")
        # UTF-8 encoding with newline='' for proper CSV formatting
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()  # Write column headers
            writer.writerows(all_csv_rows)  # Write all data rows
        
        print(f"Output CSV written to: {OUTPUT_CSV}")
    else:
        print("\nNo field entries generated!")

if __name__ == '__main__':
    main()
