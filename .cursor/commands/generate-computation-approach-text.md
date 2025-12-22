# Generate Computation Approach Text from Notes

Generate human-readable Computation Approach text from the Notes column in a Fleeti Fields CSV file. The Notes column contains speech-to-text descriptions from the user that describe how each field should be computed.

**AUTHORITATIVE REFERENCE**: This command must generate Computation Approach text that will produce the optimized YAML structure defined in `notion/2-documentation/1-specifications/1-databases/5-yaml-configuration/yaml-mapping-reference.yaml`. All patterns and examples must align with the 8 examples in that reference file.

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

6. **Generate Computation Approach text**: Based on the Field Type and parsed Notes, generate appropriate Computation Approach text following these patterns (aligned with YAML reference examples):

## Pattern Rules (Aligned with YAML Reference)

### 1. Direct Mapping Fields (Example 1)

**YAML Reference**: Example 1 - Single source direct mapping

**Pattern:**
```
"Direct mapping from {provider}: {field} (path: {path}) - {description}"
```

**YAML Structure Generated** (optimized):
```yaml
type: direct
sources:
  - field: provider_field_name
    path: provider_field_path
```

**Optimization Rules Applied**:
- `sources` array with single source (no `priority` needed for single source)
- Omit `type: direct` in source (default for provider fields)
- Omit `provider: navixy` in source (matches top-level provider)
- Omit `source_type: provider` (inferred from field/path)
- Omit `description` in source (use comments instead)

**Extraction from Notes:**
- Provider name: Extract from Notes (navixy, oem-trackunit, teltonika, etc.) - lowercase
- Field name: Extract field identifier (e.g., `avl_io_1`, `lat`, `heading`)
- Path: Infer from field name:
  - Navixy `avl_io_*` → `params.avl_io_*`
  - Navixy common fields (`lat`, `lng`, `alt`, `heading`, `speed`, `hdop`, `pdop`) → root level
  - Other providers: Use field name or infer based on provider patterns
- Description: Use Description column, or extract from Notes if more specific

**Example:**
- Notes: "Direct mapping from Navixy lat"
- Field: `location_latitude`
- Generated: `"Direct mapping from Navixy: lat (path: lat) - Latitude in decimal degrees"`

### 2. Prioritized Mapping Fields - Multiple Direct Sources (Example 2)

**YAML Reference**: Example 2 - Multiple direct sources with priority

**Pattern:**
```
"Prioritized: {provider} {field1} (path: {path1}, priority 1), then {provider} {field2} (path: {path2}, priority 2) - {description}"
```

**YAML Structure Generated** (optimized):
```yaml
type: prioritized
sources:
  - priority: 1
    field: provider_field_name
    path: provider.field.path
  - priority: 2
    field: provider_field_name_2
    path: provider.field.path_2
```

**Optimization Rules Applied**:
- `priority` included for each source (multiple sources)
- Omit `type: direct` in sources (default)
- Omit `provider` in sources (all match top-level)
- Omit `source_type: provider` (inferred)
- Omit `description` in sources

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

### 3. Calculated Mapping Fields (Example 3)

**YAML Reference**: Example 3 - Calculated field using function

**Pattern:**
```
"Calculated: derive from {dependencies} using {function_name} function. {additional_details}

Pseudo code:
{simple_pseudo_code}"
```

**YAML Structure Generated** (optimized):
```yaml
type: calculated
calculation_type: function_reference
function: function_name
parameters:
  fleeti:
    - fleeti_field_name
    - fleeti_field_name_2
```

**Optimization Rules Applied**:
- `calculation_type: function_reference` (all calculated fields use functions)
- `parameters.fleeti` lists all Fleeti field dependencies
- Omit `dependencies` field (redundant with parameters.fleeti)
- Backend infers processing order from parameters.fleeti

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

### 4. Prioritized Mapping - Mixed Source Types (Example 4)

**YAML Reference**: Example 4 - Priority chain with direct provider field + calculated source

**Pattern:**
```
"Prioritized: {provider} {field} (path: {path}, priority 1), then calculated using {function_name} function from {dependencies} (priority 2) - {description}

Pseudo code:
{simple_pseudo_code}"
```

**YAML Structure Generated** (optimized):
```yaml
type: prioritized
sources:
  - priority: 1
    field: provider_field_name
    path: provider.field.path
  - priority: 2
    type: calculated
    calculation_type: function_reference
    function: function_name
    parameters:
      fleeti:
        - fleeti_field_name
```

**Optimization Rules Applied**:
- Omit `type: direct` for direct sources (default)
- Keep `type: calculated` for calculated sources (not default)
- `priority` included for each source (multiple sources)
- Omit `provider` in sources (all match top-level)

**Extraction from Notes:**
- Identify direct provider field (priority 1)
- Identify calculated function and dependencies (priority 2)
- Extract function name and parameters
- Generate pseudo code showing the fallback logic

**Example:**
- Notes: "inputs_individual_input_1 = avl_io_1 (priority 1), then extract bit from inputs bitmask (priority 2)"
- Field: `inputs_individual_input_1`
- Generated: `"Prioritized: Navixy avl_io_1 (path: params.avl_io_1, priority 1), then calculated using extract_bit_from_bitmask function from inputs (priority 2) - Individual input 1 state.

Pseudo code:
if (avl_io_1 exists) {
  return avl_io_1
} else {
  return extract_bit_from_bitmask(inputs, 0)
}"`

### 5. Prioritized Mapping - Different Provider (Example 5)

**YAML Reference**: Example 5 - Priority chain with sources from different providers

**Pattern:**
```
"Prioritized: {provider1} {field1} (path: {path1}, priority 1), then {provider2} {field2} (path: {path2}, priority 2) - {description}"
```

**YAML Structure Generated** (optimized):
```yaml
type: prioritized
sources:
  - priority: 1
    field: top_provider_field_name
    path: top_provider.field.path
  - priority: 2
    provider: different_provider
    field: different_provider_field_name
    path: different_provider.field.path
```

**Optimization Rules Applied**:
- Omit `provider` for priority 1 (matches top-level)
- Include `provider` for priority 2 (different from top-level)
- Omit `type: direct` in sources (default)

**Extraction from Notes:**
- Identify multiple providers mentioned
- Extract provider name for each source
- Extract field and path for each provider
- Note which provider matches top-level (omit in YAML)

**Example:**
- Notes: "Navixy speed (priority 1), then Teltonika speed (priority 2)"
- Field: `location_speed`
- Generated: `"Prioritized: Navixy speed (path: speed, priority 1), then Teltonika speed (path: speed, priority 2) - Vehicle speed"`

### 6. Transformed Mapping Fields (Example 6)

**YAML Reference**: Example 6 - Transformed field combining telemetry with static metadata

**Pattern:**
```
"Transformed: combine {telemetry_field} with {static_field} using transformation: {formula}. {additional_details}

Pseudo code:
{simple_pseudo_code}"
```

**YAML Structure Generated** (optimized):
```yaml
type: transformed
transformation: "(telemetry_field / 100) * static.tank_capacity"
service_fields:
  - asset.properties.vehicle.fuel_tank_capacity.value
```

**Optimization Rules Applied**:
- `transformation` contains formula/expression
- `service_fields` lists asset service field paths
- No `sources` array (transformed uses different structure)

**Extraction from Notes:**
- Telemetry field: Extract from Notes
- Static field: Extract asset metadata reference (e.g., `asset.properties.vehicle.fuel_tank_capacity.value`)
- Transformation rule: Extract formula or calculation logic
- Additional details: Extract any implementation notes
- Pseudo code: Generate simple pseudo code showing how telemetry and static data are combined

**Example:**
- Notes: "fuel.level_percent combined with asset.properties.vehicle.fuel_tank_capacity.value to calculate fuel.level_liters"
- Generated: `"Transformed: combine fuel.level_percent with asset.properties.vehicle.fuel_tank_capacity.value using transformation: (fuel.level_percent / 100) * static.tank_capacity. Calculates fuel level in liters from percentage and tank capacity.

Pseudo code:
tank_capacity = getAssetProperty('fuel_tank_capacity')
fuel_level_liters = (fuel.level_percent / 100) * tank_capacity
return fuel_level_liters"`

### 7. I/O Mapped Fields (Example 7)

**YAML Reference**: Example 7 - I/O mapped field using installation metadata

**Pattern:**
```
"I/O Mapped: map {raw_io_field_pattern} to {semantic_field} using installation metadata: {installation_metadata_field}. Default source: {default_source}. {additional_details}

Pseudo code:
{simple_pseudo_code}"
```

**YAML Structure Generated** (optimized):
```yaml
type: io_mapped
default_source: inputs.individual.input_1
installation_metadata: asset.installation.ignition_input_number
```

**Optimization Rules Applied**:
- `default_source` specifies fallback I/O field
- `installation_metadata` specifies asset installation field path
- No `sources` array (io_mapped uses different structure)

**Extraction from Notes:**
- Raw I/O field pattern: Extract from Notes (e.g., `io.inputs.individual.input_N` where N is variable)
- Semantic field: Target Fleeti field name
- Installation metadata: Extract from Notes (e.g., `asset.installation.ignition_input_number`)
- Default source: Extract fallback if mentioned
- Additional details: Extract bitmask extraction or other mapping logic
- Pseudo code: Generate simple pseudo code showing the I/O mapping logic

**Example:**
- Notes: "io.inputs.individual.input_N mapped to power.ignition using asset.installation.ignition_input_number. Default: input_1"
- Generated: `"I/O Mapped: map io.inputs.individual.input_N to power.ignition using installation metadata: asset.installation.ignition_input_number. Default source: inputs.individual.input_1. Maps raw digital input to semantic ignition state based on installation metadata.

Pseudo code:
ignition_input_number = getInstallationMetadata('ignition_input_number')
if (ignition_input_number) {
  power.ignition = io.inputs.individual.input_{ignition_input_number}
} else {
  power.ignition = io.inputs.individual.input_1  // default fallback
}"`

### 8. Prioritized Mapping - All Calculated Sources (Example 8)

**YAML Reference**: Example 8 - Priority chain where all sources are calculated functions

**Pattern:**
```
"Prioritized: calculated using {function1_name} function from {dependencies1} (priority 1), then calculated using {function2_name} function from {dependencies2} (priority 2) - {description}

Pseudo code:
{simple_pseudo_code}"
```

**YAML Structure Generated** (optimized):
```yaml
type: prioritized
sources:
  - priority: 1
    type: calculated
    calculation_type: function_reference
    function: extract_bit_from_bitmask
    parameters:
      provider:
        navixy: inputs
  - priority: 2
    type: calculated
    calculation_type: function_reference
    function: alternative_function
    parameters:
      fleeti:
        - fleeti_field_name
```

**Optimization Rules Applied**:
- `type: calculated` included for all sources (not default)
- `priority` included for each source (multiple sources)
- `parameters` can use `provider:` or `fleeti:` keys
- Omit `provider` in sources (functions handle provider context)

**Extraction from Notes:**
- Identify multiple calculated functions mentioned
- Extract function names and their parameters
- Determine if parameters are provider-specific or Fleeti fields
- Generate pseudo code showing the fallback chain

**Example:**
- Notes: "inputs_individual_input_1 = extract bit from inputs bitmask (priority 1), then extract bit from din bitmask (priority 2)"
- Field: `inputs_individual_input_1`
- Generated: `"Prioritized: calculated using extract_bit_from_bitmask function from inputs (priority 1), then calculated using extract_bit_from_bitmask function from din (priority 2) - Individual input 1 state.

Pseudo code:
try {
  return extract_bit_from_bitmask(inputs, 0)
} catch {
  return extract_bit_from_bitmask(din, 0)
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
- `inputs`, `outputs` → root level (bitmask fields)

### Other Providers:
- Use field name as path, or infer based on common patterns for that provider

## Quality Requirements

The generated Computation Approach text must:
1. **Be explicit enough** to regenerate the Computation Structure JSON accurately
2. **Include all necessary details**: provider, field, path, priority (if applicable), function (if calculated), transformation (if transformed), installation_metadata (if io_mapped)
3. **Be concise** but complete (not too verbose, but not missing critical information)
4. **Be developer-friendly**: Clear enough for developers to understand implementation
5. **Follow established patterns**: Use the patterns above consistently, aligned with YAML reference examples
6. **Handle edge cases**: If Notes contain unclear or ambiguous information, make reasonable inferences and note them
7. **Optimize dependencies**: Prefer using Fleeti fields that already encapsulate prerequisite checks instead of duplicating those checks
8. **Align with optimized YAML structure**: The generated Computation Structure JSON will be converted to optimized YAML per `yaml-mapping-reference.yaml`. Ensure the text contains all necessary information even though some fields may be omitted in the final YAML (the JSON generation step handles optimization)

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
"Direct mapping from Navixy: lat (path: lat) - Latitude in decimal degrees"
```

**Updated CSV row:**
```csv
location_latitude,location,"Direct mapping from Navixy: lat (path: lat) - Latitude in decimal degrees",,number,,Latitude in decimal degrees,location.latitude,direct,,,,"Direct mapping from Navixy lat",P0,...
```

## Reference Examples

**CRITICAL**: The Computation Approach text generated by this command must align with the optimized YAML structure defined in:

**YAML Mapping Reference** (AUTHORITATIVE - REQUIRED READING):
- `notion/2-documentation/1-specifications/1-databases/5-yaml-configuration/yaml-mapping-reference.yaml`
- **This is the authoritative reference for the optimized YAML structure**
- Contains 8 examples covering all mapping types:
  1. Direct mapping - single source
  2. Prioritized mapping - multiple direct sources
  3. Calculated mapping - function-based
  4. Prioritized mapping - mixed (direct + calculated)
  5. Prioritized mapping - different providers
  6. Transformed mapping - telemetry + static metadata
  7. I/O mapped - installation metadata-based
  8. Prioritized mapping - all calculated sources
- Shows all optimization rules and what fields to omit/include

**Understanding the Flow:**
```
Notes (speech-to-text) 
  → Computation Approach (this command)
    → Computation Structure JSON (generate-computation-structure-json command)
      → Optimized YAML Configuration (generate_yaml_config.py script)
```

**Key Optimization Rules (from YAML Reference):**
1. Top-level `type` field: ALWAYS KEEP (required for backend routing)
2. Source-level `type` field: OMIT when default (direct provider source), KEEP when `calculated`
3. Source-level `provider` field: OMIT when matches top-level provider
4. Source-level `priority` field: OMIT for single-source mappings
5. Source-level `description` field: OMIT (use comments instead)
6. `dependencies` field: OMIT when redundant with `parameters.fleeti`
7. `source_type` field: OMIT (can be inferred from context)

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
- **YAML alignment**: All generated Computation Approach text must align with the 8 examples in `yaml-mapping-reference.yaml` - refer to that file as the authoritative specification
