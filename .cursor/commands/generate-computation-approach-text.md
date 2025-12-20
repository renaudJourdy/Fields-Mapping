# Generate Computation Approach Text from Notes

Generate human-readable Computation Approach text from the Notes column in a Fleeti Fields CSV file. The Notes column contains speech-to-text descriptions from the user that describe how each field should be computed.

## Instructions

1. **Request CSV file**: If no CSV file is provided in the chat, ask the user to provide the Fleeti Fields CSV file path.

2. **Check export folder for existing Computation Approach**: Before generating new text, check the export folder for existing CSV files:
   - **Export folder location**: `notion/2-documentation/1-specifications/1-databases/2-fleeti-fields/export/`
   - **Look for CSV files**: Find the most recent `Fleeti Fields (db) YYYY-MM-DD.csv` file
   - **Read existing Computation Approach**: For each field name, check if Computation Approach text already exists
   - **Preserve existing text**: If Computation Approach already exists and is complete (follows patterns, includes pseudo code for calculated fields), preserve it unless Notes provide new or more accurate information

3. **Read CSV file**: Read the Fleeti Fields CSV file and identify:
   - `Name` column: Field name
   - `Notes` column: Speech-to-text description from user
   - `Computation Approach` column: Target column to update
   - `Field Type` column: Type of field (direct, calculated, prioritized, transformed, io_mapped)
   - `Field Path` column: JSON path in Fleeti telemetry
   - `Description` column: Field description
   - `💽 Provider Field (db)` column: Provider field references (may contain Notion links)

4. **Compare with existing**: For each field:
   - If Computation Approach exists in export folder and is complete → preserve it
   - If Computation Approach is missing or incomplete → generate new one
   - If Notes provide new information that improves existing Computation Approach → update it
   - If field is calculated/transformed/io_mapped and missing pseudo code → add pseudo code

5. **Parse Notes column**: For each row where Notes is not empty and Computation Approach needs generation/update:
   - Extract key information from the speech-to-text Notes
   - Identify provider names (navixy, oem-trackunit, teltonika, etc.)
   - Identify field names and paths
   - Identify calculation functions and dependencies
   - Identify priority chains for prioritized mappings

6. **Generate Computation Approach text**: Based on the Field Type and parsed Notes, generate appropriate Computation Approach text following these patterns:

## Pattern Rules

### 1. Direct Mapping Fields

**Pattern:**
```
"Direct mapping from {provider}: {field} (path: {path}) - {description}"
```

**Extraction from Notes:**
- Provider name: Extract from Notes (navixy, oem-trackunit, teltonika, etc.) - lowercase
- Field name: Extract field identifier (e.g., `avl_io_1`, `lat`, `heading`)
- Path: Infer from field name:
  - Navixy `avl_io_*` → `params.avl_io_*`
  - Navixy common fields (`lat`, `lng`, `alt`, `heading`, `speed`, `hdop`, `pdop`) → root level
  - Other providers: Use field name or infer based on provider patterns
- Description: Use Description column, or extract from Notes if more specific

**Example:**
- Notes: "Direct mapping from Navixy avl_io_1"
- Field: `location_precision_fix_quality`
- Generated: `"Direct mapping from Navixy: avl_io_69 (path: params.avl_io_69) - GNSS Status: 0 - GNSS OFF, 1 – GNSS ON with fix, 2 - GNSS ON without fix, 3 - GNSS sleep, 4 - GNSS ON with fix, invalid data"`

### 2. Prioritized Mapping Fields

**Pattern:**
```
"Prioritized: {provider} {field1} (path: {path1}, priority 1), then {provider} {field2} (path: {path2}, priority 2) - {description}"
```

**Extraction from Notes:**
- Multiple provider fields mentioned with priority indicators
- Keywords: "priority", "then", "fallback", "if not available", "otherwise"
- Extract each source with its priority order
- Provider: Same for all sources unless explicitly different
- Path: Infer for each field following direct mapping rules

**Example:**
- Notes: "hdop priority 1, then avl_io_182 priority 2"
- Field: `location_precision_hdop`
- Generated: `"Prioritized: Navixy hdop (path: hdop, priority 1), then Navixy avl_io_182 (path: params.avl_io_182, priority 2) - Horizontal Dilution of Precision"`

### 3. Calculated Mapping Fields

**Pattern:**
```
"Calculated: derive from {dependencies} using {function_name} function. {additional_details}

Pseudo code:
{simple_pseudo_code}"
```

**Extraction from Notes:**
- Function name: Extract or infer from Notes:
  - `"derive"` or `"derived from"` → `derive_{field_name}` or explicit function name
  - `"extract bit"` → `extract_bit_from_bitmask`
  - `"convert to"` → `convert_to_{target_type}`
  - Explicit function names if mentioned (e.g., `derive_cardinal_direction`, `derive_geocoded_address`)
- Dependencies: Extract Fleeti field names from Notes or Dependencies column
- Additional details: Extract calculation logic, formulas, or implementation notes from Notes
- Pseudo code: Generate simple pseudo code (2-5 lines) that shows the implementation logic clearly

**Dependency Optimization (IMPORTANT):**
- **Prefer Fleeti fields over raw provider fields**: If a Fleeti field already encapsulates prerequisite checks or logic, use that field as a dependency instead of duplicating the checks
- **Avoid duplicate dependency checks**: If a field already checks prerequisites (e.g., `statuses_immobilization_compatible` checks `asset_type` and `asset_accessories`), use that compatible field as a dependency rather than re-checking the same prerequisites
- **Example**: For `statuses_immobilization_code`:
  - ❌ **Bad**: Dependencies include `asset_type`, `asset_accessories` (duplicates checks already done in `statuses_immobilization_compatible`)
  - ✅ **Good**: Dependencies include `statuses_immobilization_compatible` (which already checks `asset_type` and `asset_accessories`)
- **Benefits**: 
  - Cleaner dependency chain
  - No redundant checks
  - Better maintainability (single source of truth)
  - More efficient computation
- **When to optimize**: If Notes mention prerequisites that are already checked by another Fleeti field, replace those prerequisites with the Fleeti field that encapsulates them

**Pseudo Code Guidelines:**
- Keep it simple and readable (2-5 lines maximum)
- Use clear variable names matching the dependencies
- Show the core calculation logic
- Include key conditions or transformations
- Use common programming constructs (if/else, assignments, function calls)

**Example:**
- Notes: "Derived from location.heading. Convert heading (0-359 degrees) to cardinal direction (N, NE, E, SE, S, SW, W, NW) using formula: dirs[Math.floor((heading + 22.5) % 360 / 45)]"
- Field: `location_cardinal_direction`
- Dependencies: `location_heading`
- Generated: `"Calculated: derive from location_heading using derive_cardinal_direction function. Converts heading (0-359 degrees) to cardinal direction (N, NE, E, SE, S, SW, W, NW).

Pseudo code:
dirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
index = Math.floor((heading + 22.5) % 360 / 45)
cardinal_direction = dirs[index]"`

**Example:**
- Notes: "Use external API (Google) to convert latitude and longitude into geocoded address"
- Field: `location_geocoded_address`
- Dependencies: `location_latitude, location_longitude`
- Generated: `"Calculated: derive from location_latitude and location_longitude using derive_geocoded_address function. Uses external API (Google) to convert latitude and longitude coordinates into a geocoded address string.

Pseudo code:
coordinates = { lat: location_latitude, lng: location_longitude }
geocoded_address = callGoogleGeocodingAPI(coordinates)
return geocoded_address"`

**Example:**
- Notes: "Backend compares current position with previous. If latitude or longitude changed (threshold applied to filter GPS noise), set timestamp to now(). Used for dwell-time calculations"
- Field: `location_last_changed_at`
- Dependencies: `location_latitude, location_longitude`
- Generated: `"Calculated: derive from location_latitude and location_longitude using derive_last_changed_at function. Backend compares current position with previous position. If latitude or longitude changed (threshold applied to filter GPS noise), sets timestamp to now(). Used for dwell-time calculations and 'parked since X' features.

Pseudo code:
if (current.lat !== previous.lat || current.lng !== previous.lng) {
  if (distance(current, previous) > threshold) {
    location_last_changed_at = now()
  }
}"`

**Example (Dependency Optimization):**
- Notes: "immobilized if output state = 1, free if = 0. Check asset has immobilizer accessory. Read output state from outputs_individual_output_1, outputs_individual_output_2, or outputs_individual_output_3 based on asset.installation.immobilizer_output_number"
- Field: `statuses_immobilization_code`
- **Optimized Dependencies**: `statuses_immobilization_compatible, asset_installation_immobilizer_output_number, outputs_individual_output_1, outputs_individual_output_2, outputs_individual_output_3`
- **NOT**: `asset_type, asset_accessories, asset_installation_immobilizer_output_number, outputs_individual_output_1, outputs_individual_output_2, outputs_individual_output_3` (duplicates checks already in `statuses_immobilization_compatible`)
- Generated: `"Calculated: derive from statuses_immobilization_compatible, asset_installation_immobilizer_output_number, outputs_individual_output_1, outputs_individual_output_2, and outputs_individual_output_3 using derive_statuses_immobilization_code function. Prerequisites: Check statuses_immobilization_compatible (must be true). If false, return null (immobilization not applicable). Read immobilizer output number from asset.installation.immobilizer_output_number (default to 1 if not specified). Read digital output state from the corresponding individual output field: outputs_individual_output_1 (if output_number = 1), outputs_individual_output_2 (if output_number = 2), or outputs_individual_output_3 (if output_number = 3)...

Pseudo code:
if (!statuses_immobilization_compatible) {
  return null  // Immobilization not applicable
}
output_number = asset_installation_immobilizer_output_number || 1
if (output_number === 1) {
  output_state = outputs_individual_output_1
} else if (output_number === 2) {
  output_state = outputs_individual_output_2
} else if (output_number === 3) {
  output_state = outputs_individual_output_3
}
// ... rest of logic"`

### 4. Transformed Mapping Fields

**Pattern:**
```
"Transformed: combine {telemetry_field} with {static_field} using {transformation_rule}. {additional_details}

Pseudo code:
{simple_pseudo_code}"
```

**Extraction from Notes:**
- Telemetry field: Extract from Notes
- Static field: Extract asset metadata reference (e.g., `asset.properties.vehicle.fuel_tank_capacity.value`)
- Transformation rule: Extract formula or calculation logic
- Additional details: Extract any implementation notes
- Pseudo code: Generate simple pseudo code showing how telemetry and static data are combined

**Example:**
- Notes: "fuel.level_percent combined with asset.properties.vehicle.fuel_tank_capacity.value to calculate fuel.level_liters"
- Generated: `"Transformed: combine fuel.level_percent with asset.properties.vehicle.fuel_tank_capacity.value using formula: (fuel.level_percent / 100) * static.tank_capacity_liters. Calculates fuel level in liters from percentage and tank capacity.

Pseudo code:
tank_capacity = getAssetProperty('fuel_tank_capacity')
fuel_level_liters = (fuel.level_percent / 100) * tank_capacity
return fuel_level_liters"`

### 5. I/O Mapped Fields

**Pattern:**
```
"I/O Mapped: map {raw_io_field} to {semantic_field} using {installation_metadata_field}. Default source: {default_source}. {additional_details}

Pseudo code:
{simple_pseudo_code}"
```

**Extraction from Notes:**
- Raw I/O field: Extract from Notes (e.g., `io.inputs.individual.input_1`)
- Semantic field: Target Fleeti field name
- Installation metadata: Extract from Notes (e.g., `asset.installation.ignition_input_number`)
- Default source: Extract fallback if mentioned
- Additional details: Extract bitmask extraction or other mapping logic
- Pseudo code: Generate simple pseudo code showing the I/O mapping logic

**Example:**
- Notes: "io.inputs.individual.input_1 mapped to power.ignition using asset.installation.ignition_input_number"
- Generated: `"I/O Mapped: map io.inputs.individual.input_1 to power.ignition using asset.installation.ignition_input_number. Default source: io.inputs.individual.input_1. Maps raw digital input to semantic ignition state based on installation metadata.

Pseudo code:
ignition_input_number = getInstallationMetadata('ignition_input_number')
if (ignition_input_number) {
  power.ignition = io.inputs.individual.input_{ignition_input_number}
} else {
  power.ignition = io.inputs.individual.input_1  // default fallback
}"`

## Provider Detection Rules

- Look for provider names: `navixy`, `Navixy`, `oem-trackunit`, `OEM-Trackunit`, `teltonika`, `Teltonika`
- Case-insensitive matching
- If provider field mentioned but provider not explicit, default to `navixy` (most common)
- If multiple providers mentioned, use the one from the primary mapping context

## Path Inference Rules

### Navixy Patterns:
- `avl_io_*` → `params.avl_io_*`
- `lat`, `lng`, `alt`, `heading`, `speed` → root level (e.g., `lat`, `lng`)
- `hdop`, `pdop`, `satellites` → root level
- `din`, `dout` → root level (bitmask fields)

### Other Providers:
- Use field name as path, or infer based on common patterns for that provider

## Quality Requirements

The generated Computation Approach text must:
1. **Be explicit enough** to regenerate the Computation Structure JSON accurately
2. **Include all necessary details**: provider, field, path, priority (if applicable), function (if calculated)
3. **Be concise** but complete (not too verbose, but not missing critical information)
4. **Be developer-friendly**: Clear enough for developers to understand implementation
5. **Follow established patterns**: Use the patterns above consistently
6. **Handle edge cases**: If Notes contain unclear or ambiguous information, make reasonable inferences and note them
7. **Optimize dependencies**: Prefer using Fleeti fields that already encapsulate prerequisite checks instead of duplicating those checks (see Dependency Optimization section above)

## New Pattern Detection

If the Notes contain a pattern that doesn't match any of the above patterns:
1. **Identify the new pattern** clearly
2. **Ask the user** to confirm if a new pattern should be created
3. **Document the pattern** if confirmed
4. **Apply the pattern** to generate the Computation Approach text

## Output

1. **Display generated Computation Approach text in chat**: For each field processed, display the generated Computation Approach text in a code block in the chat. This allows the user to review the generated content before it's saved to the CSV.
2. **Update the CSV file** with generated Computation Approach text in the `Computation Approach` column
3. **Show a summary** of:
   - Number of fields processed
   - Number of fields with existing Computation Approach (preserved)
   - Number of fields updated (new or improved)
   - Number of fields newly generated
   - Fields that couldn't be processed (with reasons)
   - Any new patterns identified (if applicable)
   - List of fields that were preserved from export folder

**Display Format**: For each field, show:
```
Field: {field_name}
Computation Approach:
{generated_computation_approach_text}
```

## Example Workflow

**Input CSV row:**
```csv
location_latitude,location,,,number,,Latitude in decimal degrees,location.latitude,direct,,,,"Direct mapping from Navixy lat",P0,...
```

**Generated Computation Approach:**
```
"Direct mapping from Navixy: lat (path: lat) - Latitude in decimal degrees from Navixy"
```

**Updated CSV row:**
```csv
location_latitude,location,"Direct mapping from Navixy: lat (path: lat) - Latitude in decimal degrees from Navixy",,number,,Latitude in decimal degrees,location.latitude,direct,,,,"Direct mapping from Navixy lat",P0,...
```

## Reference Examples

**Important**: The Computation Approach text generated by this command is used to generate Computation Structure JSON. To understand the complete workflow and see examples of Computation Approach → JSON conversion, refer to:

1. **Example CSV file** (shows Computation Approach and Computation Structure JSON side-by-side):
   - `notion/2-documentation/1-specifications/1-databases/2-fleeti-fields/export/Fleeti Fields (db) 12-19-25.csv`
   - This file contains examples of:
     - Computation Approach text (column 3)
     - Computation Structure JSON (column 4)
     - How they relate to each other

2. **Example JSON output** (shows the final JSON structure):
   - `notion/2-documentation/1-specifications/1-databases/5-yaml-configuration/scripts/navixy-mapping.json`
   - This file shows the JSON format that will be generated from Computation Approach text

3. **Workflow documentation**:
   - `notion/2-documentation/1-specifications/1-databases/WORKFLOW.md`
   - Section "Workflow Steps" explains the complete process from Notes → Computation Approach → JSON → YAML

**Understanding the Flow:**
```
Notes (speech-to-text) 
  → Computation Approach (this command)
    → Computation Structure JSON (build-fleeti-field-json command)
      → YAML Configuration (generate_yaml_config.py script)
```

Review these example files to understand:
- How Computation Approach text should be structured
- What information is needed to generate accurate JSON
- How the text-to-JSON conversion works
- The relationship between all components in the workflow

## Important Notes

- **Check export folder first**: Always check `notion/2-documentation/1-specifications/1-databases/2-fleeti-fields/export/` for existing Computation Approach text before generating new text
- **Preserve existing Computation Approach**: If a field already has Computation Approach text in the export folder, preserve it unless:
  - It's incomplete (missing pseudo code for calculated/transformed/io_mapped fields)
  - Notes provide new or more accurate information
  - The existing text doesn't follow the established patterns
- **Handle Notion links**: Provider Field column may contain Notion links like `lat (https://www.notion.so/...)` - extract just the field name
- **CSV encoding**: Handle CSV properly (UTF-8, escaped quotes, etc.)
- **Validation**: Ensure generated text follows the patterns and is valid for JSON regeneration
- **Pseudo code inclusion**: Always include simple pseudo code (2-5 lines) for calculated, transformed, and I/O mapped fields to help developers understand implementation
- **Export folder priority**: The export folder is the source of truth for existing Computation Approach text - always check there first

