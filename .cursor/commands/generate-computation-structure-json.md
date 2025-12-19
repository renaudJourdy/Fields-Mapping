# Generate Computation Structure JSON from Computation Approach

Generate Computation Structure JSON (Sources JSON) from Computation Approach text. This command parses human-readable Computation Approach text and generates the structured JSON format used for YAML configuration generation.

## Instructions

1. **Request input**: Accept either:
   - **CSV file**: Fleeti Fields CSV file path (preferred)
   - **Raw Computation Approach text**: Direct text input in chat
   - If neither provided, ask user which format they prefer

2. **Check export folder for existing JSON**: Before generating new JSON, check the export folder for existing Computation Structure JSON:
   - **Export folder location**: `notion/2-documentation/1-specifications/1-databases/2-fleeti-fields/export/`
   - **Look for CSV files**: Find the most recent `Fleeti Fields (db) XXXXXXXX.csv` file
   - **Read existing JSON**: For each field name, check if Computation Structure JSON already exists
   - **Preserve existing JSON**: If Computation Structure JSON already exists and is valid, preserve it unless Computation Approach text has changed

3. **Read input**:
   - **If CSV**: Read the CSV file and extract:
     - `Name` column: Field name
     - `Computation Approach` column: Source text to parse
     - `Field Type` column: Type of field (direct, calculated, prioritized, transformed, io_mapped)
     - `Dependencies` column: Related Fleeti fields (for calculated fields)
     - `Description` column: Field description
   - **If raw text**: Parse the provided Computation Approach text directly

4. **Compare with existing**: For each field:
   - If Computation Structure JSON exists in export folder and Computation Approach hasn't changed → preserve it
   - If Computation Approach is new or changed → generate new JSON
   - If Computation Approach is missing → skip field (with warning)

5. **Parse Computation Approach text**: For each Computation Approach text, identify the pattern and extract:
   - **Direct mapping**: Provider, field, path, description
   - **Prioritized mapping**: Multiple sources with priorities
   - **Calculated mapping**: Function name, dependencies, parameters
   - **Transformed mapping**: Telemetry field, static field, transformation rule
   - **I/O mapped**: Raw I/O field, semantic field, installation metadata

6. **Generate Computation Structure JSON**: Based on the parsed Computation Approach, generate JSON following these patterns:

## JSON Structure Patterns

### 1. Direct Mapping Fields

**Computation Approach Pattern:**
```
"Direct mapping from {provider}: {field} (path: {path}) - {description}"
```

**Generated JSON:**
```json
[
  {
    "priority": 1,
    "type": "direct",
    "source_type": "provider",
    "provider": "{provider}",
    "field": "{field}",
    "path": "{path}",
    "description": "{description}"
  }
]
```

**Extraction Rules:**
- Extract provider name (lowercase: navixy, oem-trackunit, teltonika, etc.)
- Extract field name from pattern
- Extract path from `(path: {path})` or infer from field name
- Extract description from text after `-` or use Description column
- Priority is always 1 for direct mappings

**Example:**
- Computation Approach: `"Direct mapping from Navixy: lat (path: lat) - Latitude in decimal degrees from Navixy"`
- Generated JSON:
```json
[
  {
    "priority": 1,
    "type": "direct",
    "source_type": "provider",
    "provider": "navixy",
    "field": "lat",
    "path": "lat",
    "description": "Latitude in decimal degrees from Navixy"
  }
]
```

### 2. Prioritized Mapping Fields

**Computation Approach Pattern:**
```
"Prioritized: {provider} {field1} (path: {path1}, priority 1), then {provider} {field2} (path: {path2}, priority 2) - {description}"
```

**Generated JSON:**
```json
[
  {
    "priority": 1,
    "type": "direct",
    "source_type": "provider",
    "provider": "{provider}",
    "field": "{field1}",
    "path": "{path1}",
    "description": "{description1}"
  },
  {
    "priority": 2,
    "type": "direct",
    "source_type": "provider",
    "provider": "{provider}",
    "field": "{field2}",
    "path": "{path2}",
    "description": "{description2}"
  }
]
```

**Extraction Rules:**
- Extract each source with its priority number
- Extract provider (usually same for all sources)
- Extract field name and path for each source
- Generate description for each source (can be same or specific)
- Priority increments: 1, 2, 3, etc.

**Example:**
- Computation Approach: `"Prioritized: Navixy hdop (path: hdop, priority 1), then Navixy avl_io_182 (path: params.avl_io_182, priority 2) - Horizontal Dilution of Precision"`
- Generated JSON:
```json
[
  {
    "priority": 1,
    "type": "direct",
    "source_type": "provider",
    "provider": "navixy",
    "field": "hdop",
    "path": "hdop",
    "description": "Horizontal Dilution of Precision from hdop field"
  },
  {
    "priority": 2,
    "type": "direct",
    "source_type": "provider",
    "provider": "navixy",
    "field": "avl_io_182",
    "path": "params.avl_io_182",
    "description": "Horizontal Dilution of Precision from avl_io_182"
  }
]
```

### 3. Calculated Mapping Fields

**Computation Approach Pattern:**
```
"Calculated: derive from {dependencies} using {function_name} function. {additional_details}

Pseudo code:
{simple_pseudo_code}"
```

**Generated JSON:**
```json
[
  {
    "priority": 1,
    "type": "calculated",
    "calculation_type": "function_reference",
    "function": "{function_name}",
    "parameters": {
      "fleeti": [
        "{dependency1}",
        "{dependency2}"
      ]
    },
    "description": "{description}"
  }
]
```

**Extraction Rules:**
- Extract function name from `using {function_name} function`
- **Function name specificity**: Function names must be field-specific and unique
  - If the function name in Computation Approach is generic (e.g., `derive_last_changed_at`), make it specific based on the target field name
  - Example: For field `top_status_last_changed_at`, use `derive_top_status_last_changed_at` (not generic `derive_last_changed_at`)
  - Function names should follow pattern: `derive_{field_name}` or `derive_{category}_{field_name}`
  - This ensures each field has a unique, identifiable function name
- Extract dependencies from `derive from {dependencies}` or Dependencies column
- Dependencies should be Fleeti field names (e.g., `location_heading`, `location_latitude`)
- Generate description from additional_details or Description column
- Parameters structure: `{"fleeti": ["field1", "field2"]}` for Fleeti field dependencies

**Example:**
- Computation Approach: `"Calculated: derive from location_heading using derive_cardinal_direction function. Converts heading (0-359 degrees) to cardinal direction (N, NE, E, SE, S, SW, W, NW).

Pseudo code:
dirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
index = Math.floor((location_heading + 22.5) % 360 / 45)
cardinal_direction = dirs[index]"`
- Dependencies: `location_heading`
- Generated JSON:
```json
[
  {
    "priority": 1,
    "type": "calculated",
    "calculation_type": "function_reference",
    "function": "derive_cardinal_direction",
    "parameters": {
      "fleeti": [
        "location_heading"
      ]
    },
    "description": "Derived from location.heading"
  }
]
```

**Example with multiple dependencies:**
- Computation Approach: `"Calculated: derive from location_latitude and location_longitude using derive_geocoded_address function. Uses external API (Google) to convert latitude and longitude coordinates into a geocoded address string."`
- Dependencies: `location_latitude, location_longitude`
- Generated JSON:
```json
[
  {
    "priority": 1,
    "type": "calculated",
    "calculation_type": "function_reference",
    "function": "derive_geocoded_address",
    "parameters": {
      "fleeti": [
        "location_latitude",
        "location_longitude"
      ]
    },
    "description": "Use external API (Google) to convert latitude and longitude into geocoded address"
  }
]
```

### 4. Transformed Mapping Fields

**Computation Approach Pattern:**
```
"Transformed: combine {telemetry_field} with {static_field} using {transformation_rule}. {additional_details}

Pseudo code:
{simple_pseudo_code}"
```

**Note**: Transformed fields use a different JSON structure (not Sources JSON array). They require:
- Transformation rule (formula)
- Service fields (references to Asset Service)
- This is handled separately in Mapping Fields Database

**For this command**: Generate a placeholder or note that transformed fields require additional configuration beyond Sources JSON.

### 5. I/O Mapped Fields

**Computation Approach Pattern:**
```
"I/O Mapped: map {raw_io_field} to {semantic_field} using {installation_metadata_field}. Default source: {default_source}. {additional_details}

Pseudo code:
{simple_pseudo_code}"
```

**Note**: I/O mapped fields also use a different structure (not Sources JSON array). They require:
- Default source
- Installation metadata field reference
- This is handled separately in Mapping Fields Database

**For this command**: Generate a placeholder or note that I/O mapped fields require additional configuration beyond Sources JSON.

## Parsing Rules

### Provider Detection
- Look for provider names: `navixy`, `Navixy`, `oem-trackunit`, `OEM-Trackunit`, `teltonika`, `Teltonika`
- Case-insensitive matching
- Convert to lowercase in JSON output
- Default to `navixy` if provider not explicitly mentioned

### Path Extraction
- Extract from `(path: {path})` pattern
- If not found, infer from field name:
  - Navixy `avl_io_*` → `params.avl_io_*`
  - Navixy common fields (`lat`, `lng`, `alt`, `heading`, `speed`) → root level
  - Other providers: Use field name as path

### Function Name Extraction
- Extract from `using {function_name} function` pattern
- **IMPORTANT: Function names must be field-specific and unique**
  - Function names should include the target field name or a clear identifier to avoid ambiguity
  - Generic function names like `derive_last_changed_at` should be avoided
  - Use specific names like `derive_top_status_last_changed_at`, `derive_location_last_changed_at`, etc.
  - Function names should follow the pattern: `derive_{field_name}` or `derive_{category}_{field_name}`
- Common function name patterns:
  - `derive_{field_name}` - e.g., `derive_cardinal_direction`, `derive_geocoded_address`
  - `derive_{category}_{field_name}` - e.g., `derive_top_status_family`, `derive_top_status_code`, `derive_top_status_last_changed_at`
  - `extract_bit_from_bitmask` - Generic bitmask extraction (acceptable as it's a utility function)
  - Custom function names as specified in Computation Approach
- **Validation**: If a function name seems too generic (e.g., `derive_last_changed_at` without field context), check if it should be more specific based on the field name

### Dependencies Extraction
- Extract from `derive from {dependencies}` pattern
- Split by `and`, `,` to get multiple dependencies
- Use Dependencies column from CSV if available
- Dependencies should be Fleeti field names (underscore format: `location_heading`)

### Priority Extraction
- For prioritized mappings: Extract priority numbers from text
- For direct/calculated: Always priority 1
- Priority order: 1, 2, 3, etc. (incrementing)

## JSON Format Requirements

1. **Valid JSON**: Output must be valid JSON (can be string-escaped for CSV)
2. **Array format**: Always output as array `[{...}]` even for single sources
3. **Field names**: Use exact field names from Computation Approach
4. **Provider names**: Lowercase (navixy, oem-trackunit, teltonika)
5. **Consistent structure**: Follow the exact JSON structure patterns above

## Output

1. **If CSV input**: Update the CSV file with generated Computation Structure JSON in the `Computation Structure JSON` column
2. **If raw text input**: Output the JSON directly in chat
3. **Show a summary** of:
   - Number of fields processed
   - Number of fields with existing JSON (preserved)
   - Number of fields updated (new or changed Computation Approach)
   - Number of fields newly generated
   - Fields that couldn't be processed (with reasons)
   - Transformed/I/O mapped fields (noted as requiring separate configuration)

## Example Workflow

**Input (CSV row):**
```csv
location_latitude,location,"Direct mapping from Navixy: lat (path: lat) - Latitude in decimal degrees from Navixy",,number,,Latitude in decimal degrees,location.latitude,direct,...
```

**Generated JSON:**
```json
[
  {
    "priority": 1,
    "type": "direct",
    "source_type": "provider",
    "provider": "navixy",
    "field": "lat",
    "path": "lat",
    "description": "Latitude in decimal degrees from Navixy"
  }
]
```

**Updated CSV row:**
```csv
location_latitude,location,"Direct mapping from Navixy: lat (path: lat) - Latitude in decimal degrees from Navixy","""location_latitude"": [{""priority"": 1, ""type"": ""direct"", ""source_type"": ""provider"", ""provider"": ""navixy"", ""field"": ""lat"", ""path"": ""lat"", ""description"": ""Latitude in decimal degrees from Navixy""}]",number,...
```

## Reference Examples

**Important**: To understand the complete workflow and see examples of Computation Approach → JSON conversion, refer to:

1. **Example CSV file** (shows Computation Approach and Computation Structure JSON side-by-side):
   - `notion/2-documentation/1-specifications/1-databases/2-fleeti-fields/export/Fleeti Fields (db) 12-19-25.csv`
   - This file contains examples of:
     - Computation Approach text (column 3)
     - Computation Structure JSON (column 4)
     - How they relate to each other

2. **Example JSON output** (shows the final JSON structure):
   - `notion/2-documentation/1-specifications/1-databases/5-yaml-configuration/scripts/navixy-mapping.json`
   - This file shows the JSON format that will be used for YAML generation

3. **Workflow documentation**:
   - `notion/2-documentation/1-specifications/1-databases/WORKFLOW.md`
   - Section "Workflow Steps" explains the complete process from Notes → Computation Approach → JSON → YAML

**Understanding the Flow:**
```
Notes (speech-to-text) 
  → Computation Approach (generate-computation-approach-text command)
    → Computation Structure JSON (this command)
      → YAML Configuration (generate_yaml_config.py script)
```

Review these example files to understand:
- How Computation Approach text maps to JSON structure
- What information is needed to generate accurate JSON
- The relationship between all components in the workflow

## Important Notes

- **Check export folder first**: Always check `notion/2-documentation/1-specifications/1-databases/2-fleeti-fields/export/` for existing Computation Structure JSON before generating new JSON
- **Preserve existing JSON**: If Computation Structure JSON already exists in export folder and Computation Approach hasn't changed, preserve it
- **CSV encoding**: When updating CSV, properly escape JSON strings (double quotes become `""`)
- **Validation**: Ensure generated JSON is valid and follows the exact structure patterns
- **Transformed/I/O mapped fields**: These fields require additional configuration beyond Sources JSON - note this in output
- **Field name format**: Use underscore format for Fleeti field names in dependencies (e.g., `location_heading`, not `location.heading`)
- **Provider names**: Always lowercase in JSON output (navixy, oem-trackunit, teltonika)
- **Function name specificity**: Function names must be field-specific and unique. Avoid generic function names like `derive_last_changed_at` - use specific names like `derive_top_status_last_changed_at` that include the target field context. Function names should follow the pattern `derive_{field_name}` or `derive_{category}_{field_name}` to ensure uniqueness and clarity.

