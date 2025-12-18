# Fleeti Fields CSV Generation Specification

**Status:** ✅ Implemented

## Purpose

This document specifies how the `generate_fleeti_fields.py` script generates the Fleeti Fields Database CSV from the markdown specification file.

## Input Format

### Source File

**File:** `input/fleeti-telemetry-schema-specification.md`

The markdown file contains:
- **Section headers**: Numbered sections (1-16) plus "Root-Level Fields"
- **JSON Structure blocks**: Code blocks showing the JSON structure for each section
- **Field Sources & Logic tables**: Markdown tables with field metadata

### Section Structure

Each section follows this pattern:

```markdown
# N. Section Name

**Purpose:** Description of the section

## Structure
```json
{
  "field": "type description",
  "nested": {
    "subfield": "type description"
  }
}
```

## Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `field.path` | P0 | Navixy: `field` | Field description |
```

### Table Columns

The "Field Sources & Logic" table contains:
- **Fleeti Field**: Field path (e.g., `location.latitude`)
- **Priority**: Implementation priority (P0, P1, P2, P3, T, BL, ?)
- **Source / Logic**: How the field is obtained (e.g., "Navixy: `lat`" or "**Computed:** ...")
- **Description**: Human-readable description of the field

## Processing Pipeline

### 1. Section Parsing

The script:
1. Finds all section headers using regex: `^# (\d+)\. (.+)$` or `^# Root-Level Fields$`
2. Extracts JSON structure from code blocks between `\`\`\`json` and `\`\`\``
3. Parses markdown tables starting with "Field Sources & Logic" or "Field Sources & Notes"
4. Groups JSON structure and table rows by section

### 2. JSON Field Extraction

For each section's JSON structure:
1. Attempts to parse as valid JSON
2. If parsing fails (due to type descriptions like "decimal degrees (-90 to 90)"), cleans the JSON:
   - Replaces type descriptions with placeholder values
   - Removes comments
   - Retries parsing
3. If still fails, uses fallback text parsing to extract structure
4. Recursively traverses JSON to extract all field paths:
   - Simple fields: `location.latitude`
   - Nested fields: `location.precision.hdop`
   - Array containers: `status.statuses[]`
   - Array item properties: `status.statuses[].family`
   - Value-unit objects: `motion.speed` (with `{value, unit}`)
   - Nested objects with timestamps: `motion.is_moving` (with `{value, last_changed_at}`)

### 3. Table Parsing

For each section's table:
1. Identifies table header row (contains "Fleeti Field" and "Priority")
2. Parses each data row:
   - Extracts field path (removes backticks)
   - Extracts priority
   - Extracts source/logic
   - Extracts description

### 4. Field Matching

The script matches JSON fields with table rows:
1. Creates lookup dictionary: `field_path → table_row`
2. For each JSON field:
   - If table row exists: Use table metadata
   - If no table row: Generate row with defaults
3. For each table row without JSON field:
   - Generate row (field might be computed, not in JSON structure)

### 5. Metadata Inference

For each matched field, the script infers:

#### Field Type
- **direct**: Source contains "Navixy:" with single field
- **prioritized**: Source contains "Navixy:" with multiple fields or priority indicators
- **calculated**: Source contains "**Computed:**" or "Derived from"
- **asset_integrated**: Source contains "Fleeti" service/catalog references
- **transformed**: Source mentions static data, asset.properties, installation
- **io_mapped**: Source mentions I/O, input, output, digital, analog
- **aggregated**: Source mentions cumulative, total, count, sum

#### Structure Type
- **simple_value**: Single value (string, number, boolean)
- **value_unit_object**: Object with `{value, unit}` structure
- **nested_object**: Object with `{value, last_changed_at}` or other nested structure
- **array**: Array container or array item property

#### Data Type
- **number**: JSON value is number/int/float, or description mentions "number"/"integer"/"decimal"
- **string**: JSON value is string, or description mentions "string"
- **boolean**: JSON value is boolean, or description mentions "boolean"
- **array**: Structure type is array
- **object**: Structure type is nested_object or value_unit_object

#### Other Metadata
- **Unit**: Extracted from JSON value (`unit` property) or description
- **Computation Approach**: Extracted from source/logic if computed
- **Dependencies**: Extracted from source/logic/description (field references)
- **Provider Fields**: Extracted from source/logic (Navixy field references)

### 6. CSV Generation

For each matched field, generates CSV row with columns:

| Column | Source |
|-------|--------|
| `Name` | Generated from field path (snake_case) |
| `Category` | Section category mapping |
| `Computation Approach` | Extracted from source/logic if computed |
| `Data Type` | Inferred from JSON/description |
| `Dependencies` | Extracted field references |
| `Description` | From table |
| `Field Path` | From table |
| `Field Type` | Inferred from source/logic |
| `JSON Structure` | Formatted JSON value (triple-quoted) |
| `Mapping Fields (db)` | Empty (manual input) |
| `Notes` | Empty |
| `Priority` | From table |
| `REST API Endpoints` | Empty (manual input) |
| `Status` | Default: `inactive` |
| `Structure Type` | Inferred from JSON |
| `Unit` | Extracted from JSON/description |
| `Version Added` | Default: `1.0.0` |
| `WebSocket Contracts` | Empty (manual input) |
| `💽 Provider Field (db)` | Extracted provider field references |

## Design Decisions

### 1. Field Name Generation

Field names are generated from field paths using snake_case:
- `location.latitude` → `location_latitude`
- `status.statuses[].family` → `status_statuses_family`
- `location.precision.hdop` → `location_precision_hdop`

**Rationale:** Provides stable identifiers that don't change if field paths are reorganized.

### 2. JSON Structure Handling

The script handles JSON structures with type descriptions (e.g., `"decimal degrees (-90 to 90)"`) by:
1. Attempting to parse as-is
2. Cleaning type descriptions to placeholder values
3. Using fallback text parsing if JSON parsing fails

**Rationale:** The markdown uses type descriptions for documentation, not actual JSON values. The script needs to extract structure regardless.

### 3. Table-First Approach

The script prioritizes table rows over JSON fields:
- If a table row exists, it's used (even if JSON field is missing)
- If a JSON field exists without table row, defaults are used
- This ensures all documented fields are included

**Rationale:** The table is the authoritative source for field metadata. JSON structure provides examples but may be incomplete.

### 4. Default Values

Fields without explicit metadata use defaults:
- `Status`: `inactive` (newly generated fields)
- `Version Added`: `1.0.0`
- Empty columns: Left empty for manual input

**Rationale:** Generated CSV is a starting point. Manual review and updates are expected.

### 5. Category Mapping

Sections are mapped to categories:
- Root-Level Fields → `metadata`
- 1. Asset Metadata → `metadata`
- 2. Telemetry Context → `status`
- 3. Location → `location`
- 4. Connectivity → `connectivity`
- 5. Motion → `motion`
- 6. Power → `power`
- 7. Fuel → `fuel`
- 8. Counters → `counters`
- 9. Driving Behavior → `driving_behavior`
- 10. Sensors → `sensors`
- 11. Diagnostics → `diagnostics`
- 12. I/O (Inputs/Outputs) → `io`
- 13. Driver → `driver`
- 14. Device → `device`
- 15. Other → `other`
- 16. Packet Metadata → `metadata`

**Rationale:** Matches Notion database category options.

## Code Structure

### Main Functions

1. **`parse_sections()`**: Extracts sections, JSON structures, and tables from markdown
2. **`extract_fields_from_json()`**: Recursively extracts field paths from JSON
3. **`extract_structure_from_text()`**: Fallback parser for JSON-like text with type descriptions
4. **`generate_field_name()`**: Converts field path to stable identifier
5. **`infer_field_type()`**: Determines field type from source/logic
6. **`infer_structure_type()`**: Determines structure type from JSON value
7. **`infer_data_type()`**: Determines data type from JSON value and description
8. **`extract_unit_from_json()`**: Extracts unit from JSON value or description
9. **`extract_computation_approach()`**: Extracts computation approach from source/logic
10. **`extract_dependencies()`**: Extracts field dependencies from source/logic/description
11. **`extract_provider_fields()`**: Extracts provider field references from source/logic
12. **`format_json_structure()`**: Formats JSON value for CSV (triple-quoted)
13. **`match_fields_with_table()`**: Matches JSON fields with table rows
14. **`generate_csv_row()`**: Generates CSV row dictionary from matched field data
15. **`main()`**: Orchestrates the entire pipeline

### Error Handling

- JSON parsing failures: Falls back to text parsing
- Missing table rows: Uses defaults
- Missing JSON fields: Still generates rows from table
- Unicode encoding: Handled via UTF-8 file encoding

## Output Format

The generated CSV matches the export format exactly:
- Same column order
- Same data format
- Proper handling of nested fields
- Array fields handled correctly
- Value-unit objects handled correctly

## Usage

```bash
python generate_fleeti_fields.py
```

**Input:** `input/fleeti-telemetry-schema-specification.md`
**Output:** `Fleeti-Fields-YYYY-MM-DD.csv`

## Limitations

1. **Type Descriptions**: JSON structures with type descriptions may not parse perfectly. The script uses fallbacks but may miss some nested structures.

2. **Manual Fields**: Some columns require manual input:
   - Mapping Fields (db)
   - Notes
   - REST API Endpoints
   - WebSocket Contracts

3. **Inference Accuracy**: Field type, structure type, and data type inference is based on heuristics. Manual review is recommended.

4. **Dependencies**: Dependency extraction uses regex patterns. Complex dependencies may not be captured.

## Future Improvements

1. **Better JSON Parsing**: Improve handling of type descriptions in JSON structures
2. **Dependency Parsing**: More robust dependency extraction from computation approaches
3. **Unit Extraction**: Better unit inference from descriptions
4. **Validation**: Add validation to ensure generated CSV matches expected format

---

**Last Updated:** 2025-01-18  
**Status:** ✅ Implemented

