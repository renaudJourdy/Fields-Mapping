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
                        # Regular nested object - recurse to extract nested fields
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
    It extracts field paths by parsing the JSON structure syntax.
    
    Args:
        json_text: JSON-like text with type descriptions
        base_path: Base path prefix
        
    Returns:
        Dictionary mapping field paths to placeholder values
    """
    fields = {}
    
    # Extract all key-value pairs from JSON structure
    # Pattern: "key": "value" or "key": { ... }
    key_pattern = r'"([^"]+)":\s*(?:"([^"]+)"|(\{[^}]*\})|(\[[^\]]*\]))'
    
    def extract_nested(path: str, text: str, depth: int = 0):
        """Recursively extract nested structures."""
        if depth > 10:  # Prevent infinite recursion
            return
        
        # Find all key-value pairs at current level
        matches = re.finditer(key_pattern, text)
        for match in matches:
            key = match.group(1)
            current_path = f"{path}.{key}" if path else key
            
            # Check if value is an object
            if match.group(3):  # Object
                obj_text = match.group(3)
                fields[current_path] = {}  # Placeholder
                extract_nested(current_path, obj_text, depth + 1)
            elif match.group(4):  # Array
                array_text = match.group(4)
                array_path = f"{current_path}[]"
                fields[array_path] = []  # Placeholder
                # Try to extract array item structure
                if '{' in array_text:
                    extract_nested(current_path, array_text, depth + 1)
            else:
                # Simple value
                fields[current_path] = match.group(2) if match.group(2) else ""
    
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

def match_fields_with_table(json_fields: Dict[str, Any], table_rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Match JSON fields with table rows by field path.
    
    This function performs a two-way matching:
    1. For each JSON field, find matching table row (if exists)
    2. For each table row, ensure it's included (even if no JSON field)
    
    This ensures:
    - All JSON fields are included (even if not in table)
    - All table rows are included (even if computed, not in JSON)
    
    Args:
        json_fields: Dictionary of field paths to JSON values (from JSON structure)
        table_rows: List of table row dictionaries (from Field Sources & Logic table)
        
    Returns:
        List of matched field dictionaries ready for CSV generation
    """
    matched_fields = []
    
    # Create lookup dictionary for fast table row lookup by field path
    # Key: field_path (e.g., "location.latitude")
    # Value: table row dict with priority, source_logic, description
    table_lookup = {row['field_path']: row for row in table_rows}
    
    # Step 1: Process all JSON fields
    # For each field found in JSON structure, try to find matching table row
    for field_path, json_value in json_fields.items():
        table_row = table_lookup.get(field_path)
        
        if table_row:
            # Found matching table row - use table metadata
            matched_fields.append({
                'field_path': field_path,
                'json_value': json_value,
                'priority': table_row['priority'],
                'source_logic': table_row['source_logic'],
                'description': table_row['description'],
                'matched': True  # Flag indicating we have table metadata
            })
        else:
            # JSON field exists but no table row - generate with defaults
            # This can happen if JSON structure has fields not documented in table
            matched_fields.append({
                'field_path': field_path,
                'json_value': json_value,
                'priority': '',
                'source_logic': '',
                'description': '',
                'matched': False  # Flag indicating no table metadata
            })
    
    # Step 2: Process table rows without JSON fields
    # These are typically computed fields that don't appear in JSON structure
    # Example: location.cardinal_direction (computed from location.heading)
    json_paths = set(json_fields.keys())
    for table_row in table_rows:
        if table_row['field_path'] not in json_paths:
            # Table row exists but no JSON field - include it anyway
            # This ensures computed/derived fields are included in output
            matched_fields.append({
                'field_path': table_row['field_path'],
                'json_value': None,  # No JSON value (computed field)
                'priority': table_row['priority'],
                'source_logic': table_row['source_logic'],
                'description': table_row['description'],
                'matched': True  # We have table metadata
            })
    
    return matched_fields

def generate_csv_row(field_data: Dict[str, Any], category: str) -> Dict[str, str]:
    """Generate CSV row from matched field data.
    
    This function takes matched field data and generates a complete CSV row
    with all required columns. It infers missing metadata and uses defaults
    where appropriate.
    
    Args:
        field_data: Matched field dictionary containing:
            - field_path: Field path (e.g., "location.latitude")
            - json_value: JSON value from structure (may be None)
            - priority: Priority from table (P0, P1, etc.)
            - source_logic: Source/Logic text from table
            - description: Description from table
        category: Section category (e.g., "location", "motion")
        
    Returns:
        Dictionary with CSV column names as keys, ready for CSV writing
    """
    # Extract field data
    field_path = field_data['field_path']
    json_value = field_data.get('json_value')
    priority = field_data.get('priority', '')
    source_logic = field_data.get('source_logic', '')
    description = field_data.get('description', '')
    
    # Generate stable field name identifier from field path
    # Example: "location.latitude" -> "location_latitude"
    field_name = generate_field_name(field_path)
    
    # Infer all metadata from available information
    # Field Type: How the field is mapped (direct, calculated, etc.)
    field_type = infer_field_type(source_logic, description)
    # Structure Type: JSON structure (simple_value, value_unit_object, etc.)
    structure_type = infer_structure_type(field_path, json_value, description)
    # Data Type: JSON data type (number, string, boolean, etc.)
    data_type = infer_data_type(field_path, json_value, structure_type, description)
    # Unit: Extract from JSON value or description
    unit = extract_unit_from_json(json_value, description) if json_value else ""
    # Computation Approach: Extract if calculated
    computation_approach = extract_computation_approach(source_logic)
    # Dependencies: Other Fleeti fields this depends on
    dependencies = extract_dependencies(source_logic, description)
    # Provider Fields: Provider field references (e.g., "lat", "lng")
    provider_fields = extract_provider_fields(source_logic)
    # JSON Structure: Formatted JSON value for CSV
    json_structure = format_json_structure(json_value) if json_value else ""
    
    # Generate CSV row dictionary matching export format
    # Column order matches the export CSV exactly
    return {
        'Name': field_name,
        'Category': category,
        'Computation Approach': computation_approach,
        'Data Type': data_type,
        'Dependencies': dependencies,
        'Description': description,
        'Field Path': field_path,
        'Field Type': field_type,
        'JSON Structure': json_structure,
        'Mapping Fields (db)': '',  # Empty - requires manual input (Notion relation)
        'Notes': '',  # Empty - for manual notes
        'Priority': priority,
        'REST API Endpoints': '',  # Empty - requires manual input
        'Status': 'inactive',  # Default for newly generated fields
        'Structure Type': structure_type,
        'Unit': unit,
        'Version Added': '1.0.0',  # Default version
        'WebSocket Contracts': '',  # Empty - requires manual input
        '💽 Provider Field (db)': provider_fields  # Extracted provider field references
    }

def main():
    """Main processing function.
    
    Orchestrates the entire pipeline:
    1. Read markdown specification file
    2. Parse sections (extract JSON structures and tables)
    3. For each section:
       - Extract fields from JSON structure
       - Match with table rows
       - Generate CSV rows
    4. Write CSV file with all field entries
    
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
        
        # Skip sections without any content (no JSON, no table)
        # This handles edge cases like "Priority System" section
        if not json_structure and not table_rows:
            continue
        
        print(f"\nProcessing section: {section_title}")
        
        # Get category for this section (maps to Notion database category)
        category = SECTION_CATEGORY_MAP.get(section_title, "other")
        
        # Step 3a: Extract all field paths from JSON structure
        json_fields = {}
        if json_structure:
            # Recursively extract all field paths from JSON
            json_fields = extract_fields_from_json(json_structure)
            print(f"  Extracted {len(json_fields)} fields from JSON")
        
        print(f"  Found {len(table_rows)} table rows")
        
        # Step 3b: Match JSON fields with table rows
        # This creates a unified view of all fields (from JSON and table)
        matched_fields = match_fields_with_table(json_fields, table_rows)
        print(f"  Generated {len(matched_fields)} field entries")
        
        # Step 3c: Generate CSV rows for each matched field
        for field_data in matched_fields:
            csv_row = generate_csv_row(field_data, category)
            all_csv_rows.append(csv_row)
    
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
