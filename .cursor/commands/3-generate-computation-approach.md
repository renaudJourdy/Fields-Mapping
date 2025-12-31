# Generate Computation Approach

Generate computation approach text for Fleeti telemetry fields based on notes from CSV files or direct chat input. This command learns from existing computation approaches in the Fleeti Fields export CSV and generates new computation approaches that will produce valid Computation Structure JSON.

**When to use**: Use this command when you have notes about how a Fleeti field should be computed and need to generate the formal computation approach text that will be used to generate the Computation Structure JSON.

## Usage

### Batch Mode (CSV File)
```
/generate-computation-approach <csv-file-path>
```
Processes a CSV file containing field names and notes, generates computation approaches for all fields, and outputs a markdown file.

### Single Field Mode (Direct Input)
```
/generate-computation-approach --field <field-name> --notes <notes-text>
```
Processes a single field with notes provided directly, outputs computation approach in chat as a code snippet.

### Interactive Mode
```
/generate-computation-approach
```
Prompts for field name and notes interactively, outputs computation approach in chat.

## Instructions

### Step 1: Load Context and Understand Patterns

1. **Read Fleeti Fields Export CSV**: Read the latest Fleeti Fields export CSV from `notion/2-documentation/1-specifications/1-databases/2-fleeti-fields/export/`
   - Files use date-based naming (e.g., `Fleeti Fields (db) 12-23-25.csv`)
   - Read all CSV files in the directory to find the most recent export

2. **Analyze Existing Computation Approaches**: Study the "Computation Approach" and "Computation Structure JSON" columns to understand:
   - **Direct Mapping Pattern**: "Direct mapping from Navixy: <field> (path: <path>) - <description>"
   - **Prioritized Mapping Pattern**: "Prioritized: Navixy <field1> (path: <path1>, priority 1), then Navixy <field2> (path: <path2>, priority 2) - <description>"
   - **Calculated Pattern**: "Calculated: derive from <dependencies> using <function> function. <detailed logic>"
   - **Transformed Pattern**: "Transformed: combines telemetry with static asset metadata. <formula/transformation>"
   - **I/O Mapped Pattern**: "I/O Mapped: Maps raw I/O signals to semantic fields via installation metadata. <mapping logic>"

3. **Understand JSON Structure Relationship**: 
   - Direct mappings produce `{"type": "direct", "sources": [...]}`
   - Prioritized mappings produce `{"type": "prioritized", "sources": [{"priority": 1, ...}, ...]}`
   - Calculated mappings produce `{"type": "calculated", "calculation_type": "function_reference", "function": "...", "parameters": {...}}`
   - Transformed mappings produce `{"type": "transformed", "transformation": "...", "service_fields": [...]}`
   - I/O mapped produce `{"type": "io_mapped", "default_source": "...", "installation_metadata": "..."}`

4. **Reference Examples**: Look at fields like:
   - `location_latitude` (direct mapping)
   - `speed` (prioritized with 6 sources)
   - `location_cardinal_direction` (calculated)
   - `sensors.environment[]` (calculated with complex function)
   - `inputs_individual_input_1` (prioritized with calculated + direct fallback)

### Step 2: Process Input

#### CSV Mode
1. **Detect CSV Structure**: Flexibly detect columns:
   - Field name columns: "Name", "Field Name", "Field", "Fleeti Field"
   - Notes columns: "Notes", "Note", "Computation Notes", "Description"
   - Category columns: "Category" (optional, for grouping in output)
   - Field path columns: "Field Path", "Path" (optional, if provided)

2. **Parse CSV**: Extract field names and notes from each row
   - Skip empty rows
   - Handle missing notes gracefully (will ask questions later)

3. **Process Each Row**: For each field in the CSV:
   - Extract field name and notes
   - Proceed to Step 3 for computation approach generation

#### Direct Text Mode
1. **Extract Parameters**: 
   - Field name from `--field` argument
   - Notes from `--notes` argument or interactive prompt

2. **Process Single Field**: Proceed to Step 3 for computation approach generation

### Step 3: Generate Computation Approach

For each field, analyze the notes and generate computation approach text:

1. **Determine Mapping Type**:
   - Look for keywords: "direct", "prioritized", "calculated", "transformed", "io_mapped", "I/O mapped"
   - If unclear, ask: "Is this a direct mapping (1:1 provider field), prioritized mapping (multiple sources with priority), calculated field (derived from other fields), transformed field (combines telemetry with asset metadata), or I/O mapped field (maps raw I/O to semantic fields)?"

2. **Identify Provider Fields**:
   - Extract provider field names mentioned in notes (e.g., `can_speed`, `avl_io_239`, `obd_speed`)
   - If multiple fields mentioned, determine if they need priority ordering
   - If no provider fields mentioned but mapping type suggests direct/prioritized, ask: "Which provider field(s) should be used for this mapping?"

3. **Determine Priority Order** (for prioritized mappings):
   - Look for explicit priority indicators: "first", "then", "priority 1", "preferred", "fallback"
   - If multiple fields but no clear priority, ask: "What is the priority order for these provider fields? Which should be tried first, second, etc.?"

4. **Identify Dependencies** (for calculated fields):
   - Look for references to other Fleeti fields (e.g., "from location_heading", "using speed and ignition_value")
   - If calculated but dependencies unclear, ask: "Which other Fleeti fields does this field depend on?"

5. **Identify Function** (for calculated fields):
   - Look for function names: "derive_*", "extract_*", etc.
   - Check if function follows existing patterns (e.g., "derive_cardinal_direction", "derive_geofences")
   - If function unclear, ask: "What function should be used? Is there an existing function (like derive_cardinal_direction) or do we need a new one? What should it be called?"

6. **Identify Unit Conversion Needs**:
   - Look for unit mentions: "km/h", "degrees", "meters", "liters", "%"
   - If units differ between provider and Fleeti field, note unit conversion requirement
   - If units unclear, ask: "What units are the provider fields in, and what unit should the Fleeti field use?"

7. **Identify Asset Metadata Requirements** (for transformed/I/O mapped):
   - Look for references to "asset.installation.*", "asset.properties.*", "asset.accessories[]"
   - If transformed but metadata unclear, ask: "What asset metadata fields are required for this transformation?"

8. **Generate Computation Approach Text**:
   - Follow established patterns from existing fields
   - Use consistent formatting and terminology
   - Include pseudo code for complex calculations when appropriate
   - Reference similar fields when applicable (e.g., "Follow same pattern as sensors.environment[]")

### Step 4: Ask Clarifying Questions

When notes are insufficient or ambiguous, ask contextual questions:

- **Mapping Type Unclear**: "Based on the notes, I cannot determine the mapping type. Is this a direct mapping, prioritized mapping, calculated field, transformed field, or I/O mapped field?"

- **Priority Order Ambiguous**: "Multiple provider fields are mentioned but the priority order is unclear. What is the priority order? (e.g., can_speed > obd_speed > speed)"

- **Provider Fields Not Specified**: "For a [direct/prioritized] mapping, which provider field(s) should be used? Please specify the field name(s) and their paths."

- **Dependencies Missing**: "This appears to be a calculated field, but the dependencies are not clear. Which other Fleeti fields does this field depend on?"

- **Function Unclear**: "What function should be used for this calculation? Is there an existing function or do we need a new one? What should it be called?"

- **Unit Conversion Needed**: "The notes mention different units. What units are the provider fields in, and what unit should the Fleeti field use? Should unit conversion be applied?"

- **Asset Metadata Unclear**: "This appears to require asset metadata, but which specific fields? (e.g., asset.installation.initial_engine_hours, asset.properties.vehicle.fuel_tank_capacity)"

- **Complex Logic Unclear**: "The computation logic seems complex. Can you provide more details about how the calculation should work? Should I reference a similar field as an example?"

### Step 5: Output Results

#### Batch Mode (CSV Input)
1. **Create Markdown File**: 
   - Location: `notion/2-documentation/1-specifications/1-databases/2-fleeti-fields/scripts/output/`
   - Filename: `computation-approach-YYYY-MM-DD.md` or `computation-approach-<descriptive-name>.md` (if provided)
   - If file exists, append or create new with timestamp

2. **Format Markdown File**:
```markdown
# Computation Approach for Fleeti Fields

Generated: YYYY-MM-DD HH:MM:SS

## <Category>

### <field_name>
**Field Path:** `<field.path>`

**Computation Approach:**
<generated computation approach text>

**Source:** <notes source if available in CSV>

**Original Notes:**
<original notes from input>

---
```

3. **Group by Category**: If category information is available, group fields by category in the output

#### Single Field Mode (Direct Input)
1. **Display in Chat**: Show computation approach in a code snippet:
```markdown
### <field_name>
**Field Path:** `<field.path>`

**Computation Approach:**
<generated computation approach text>
```

2. **Ready for Copy-Paste**: Format should be ready for direct copy-paste into the Fleeti Fields database

## Pattern Recognition Examples

### Direct Mapping
**Pattern**: "Direct mapping from Navixy: <field> (path: <path>) - <description>"
**Example**: `location_latitude` → "Direct mapping from Navixy: lat (path: lat) - Latitude in decimal degrees from Navixy"

### Prioritized Mapping
**Pattern**: "Prioritized: Navixy <field1> (path: <path1>, priority 1), then Navixy <field2> (path: <path2>, priority 2) - <description>"
**Example**: `speed` → "Prioritized: Navixy can_speed (path: params.can_speed, priority 1), then Navixy obd_speed (path: params.obd_speed, priority 2), then Navixy avl_io_24 (path: params.avl_io_24, priority 3), then Navixy speed (path: speed, priority 4), then Navixy avl_io_37 (path: params.avl_io_37, priority 5), then Navixy avl_io_81 (path: params.avl_io_81, priority 6) - Speed in km/h. GNSS Speed is the fallback."

### Calculated
**Pattern**: "Calculated: derive from <dependencies> using <function> function. <detailed logic>"
**Example**: `location_cardinal_direction` → "Calculated: derive from location_heading using derive_cardinal_direction function. Converts heading (0-359 degrees) to cardinal direction (N, NE, E, SE, S, SW, W, NW)."

### Complex Calculated (with pseudo code)
**Pattern**: Includes detailed pseudo code for complex logic
**Example**: `sensors.environment[]` → Includes detailed backend processing, unit conversion rules, and validation rules

### Prioritized with Calculated Fallback
**Pattern**: "Prioritized: calculated using <function> (priority 1), then Navixy <field> (priority 2)"
**Example**: `inputs_individual_input_1` → "Prioritized: calculated using extract_bit_from_bitmask function from inputs (priority 1), then Navixy avl_io_1 (path: params.avl_io_1, priority 2)"

## Important Notes

- **Learn from Existing Fields**: Always reference existing computation approaches in the Fleeti Fields export to maintain consistency
- **JSON Structure**: The computation approach text must be detailed enough to generate valid Computation Structure JSON
- **Ask Questions Proactively**: When in doubt, ask clarifying questions rather than making assumptions
- **Reference Similar Fields**: When notes mention "follow same pattern as X", look up that field and adapt its pattern
- **Unit Conversion**: Always specify units for both provider fields and Fleeti fields when unit conversion is needed
- **Dependencies**: Clearly list all Fleeti field dependencies for calculated fields
- **Function Names**: Use consistent function naming patterns (derive_*, extract_*, etc.)

## Expected Output

After executing this command, you should have:

1. ✅ Loaded and analyzed the Fleeti Fields export CSV to understand patterns
2. ✅ Processed input (CSV or direct text)
3. ✅ Generated computation approach text following established patterns
4. ✅ Asked clarifying questions when notes were insufficient
5. ✅ Output results in appropriate format (markdown file for batch, code snippet for single)

The generated computation approach should be ready for use in the Fleeti Fields database and should produce valid Computation Structure JSON when processed by the YAML generation script.

