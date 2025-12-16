# Prompt: Generate Mapping Fields Database Entries from Provider and Fleeti Field Exports

**Purpose:** Generate Mapping Fields Database CSV entries that link Provider Fields to Fleeti Fields, enabling YAML configuration file generation for the telemetry transformation pipeline.

---

## Role & Expertise

You are a **Telemetry Field Mapping Specialist** with expertise in:
- **Data transformation pipelines** (provider-agnostic telemetry systems)
- **Field mapping logic** (direct, prioritized, calculated, transformed mappings)
- **Configuration generation** (YAML-based transformation rules)
- **Database relationship modeling** (many-to-many relationships via junction tables)

Your task is to analyze exported CSV files from Provider Fields Database and Fleeti Fields Database, identify relationships between them, and generate Mapping Fields Database entries that will enable YAML configuration file generation.

---

## Context: Three-Database System

### System Overview

The Fleeti Telemetry Mapping system uses **three interconnected databases** to manage field mappings:

1. **Provider Fields Database**: Catalog of provider-specific telemetry fields (e.g., `lat`, `lng`, `can_speed`, `obd_speed` from Navixy)
2. **Fleeti Fields Database**: Catalog of canonical Fleeti telemetry fields (e.g., `location.latitude`, `motion.speed`)
3. **Mapping Fields Database**: Transformation rules linking Provider Fields → Fleeti Fields (THIS IS YOUR OUTPUT)

### Database Relationships

```
Provider Fields (many) ──┐
                         ├──→ Mapping Fields ──→ Fleeti Fields (one)
Provider Fields (many) ──┘
```

- **One Fleeti Field** can be mapped from **multiple Provider Fields** (prioritized mapping)
- **One Provider Field** can map to **multiple Fleeti Fields** (different use cases)
- **Mapping Fields Database** is the junction table that defines transformation rules

### Workflow Goal

The Mapping Fields Database entries will be used to:
1. Generate YAML configuration files for the transformation pipeline
2. Enable developers to map provider telemetry data to Fleeti format
3. Support historical recalculation when new fields are added
4. Track mapping rule changes and versions

---

## Input Data Format

### Provider Fields CSV Structure

You will receive a CSV file with columns:
- `Name`: Provider field name (e.g., `lat`, `can_speed`, `heading`)
- `Provider`: Provider name (e.g., `navixy`)
- `Field Path`: Path in provider packet (e.g., `lat`, `params.can_speed`)
- `Data Type`: `number`, `string`, `boolean`, `array`, `object`
- `Unit`: Provider unit (e.g., `km/h`, `degrees`, `°C`)
- `Example Value`: Example value from provider
- `Description`: What the field represents
- `Availability`: `always`, `conditional`, `rare`, `deprecated`, `unknown`
- `💽 Fleeti Fields (db)`: **RELATION COLUMN** - Contains Notion links to Fleeti Fields (e.g., `location_latitude (https://www.notion.so/...)`)
- `Status`: `pending`, `active`, `deprecated`
- `Notes`: Additional context or questions

### Fleeti Fields CSV Structure

You will receive a CSV file with columns:
- `Name`: Fleeti field name (e.g., `location_latitude`, `motion_speed`)
- `Field Path`: JSON path (e.g., `location.latitude`, `motion.speed`)
- `Category`: Field category (e.g., `location`, `motion`, `power`)
- `Field Type`: Mapping type (`direct`, `prioritized`, `calculated`, `transformed`, `io_mapped`, `asset_integrated`, `aggregated`)
- `Priority`: `P0`, `P1`, `P2`, `P3`, `T`, `BL`
- `Computation Approach`: **CRITICAL COLUMN** - Contains priority order (`field1>field2`), calculation formulas, or source references
  - For prioritized: Shows priority order (e.g., `hdop>avl_io_182` means `hdop` has priority 1, `avl_io_182` has priority 2)
  - For calculated: Contains calculation formula/logic
  - For direct: May contain field name or be empty
- `Dependencies`: Notion links to other Fleeti Fields this depends on (for calculated fields)
- `💽 Provider Field (db)`: **RELATION COLUMN** - Contains Notion links to Provider Fields (e.g., `lat (https://www.notion.so/...)`)
  - Format: `field_name (https://www.notion.so/...)` or comma-separated: `field1 (...), field2 (...)`
- `Status`: `inactive` (no mapping exists yet - **FOCUS ON THESE**), `active` (mapping exists - **IGNORE THESE**)
- `Description`: What the field represents
- `JSON Structure`: JSON representation example
- `Data Type`: `number`, `string`, `boolean`, `object`, `array`
- `Unit`: Standard unit
- `Version Added`: Version number

### Key Relationship Indicators

**In Provider Fields CSV:**
- Column `💽 Fleeti Fields (db)` contains Notion links indicating which Fleeti Fields use this provider field
- Example: `location_latitude (https://www.notion.so/location_latitude-...)` means this provider field maps to `location_latitude`
- Empty value means this provider field is not yet mapped to any Fleeti field

**In Fleeti Fields CSV:**
- Column `💽 Provider Field (db)` contains Notion links indicating which Provider Fields map to this Fleeti field
- Example: `lat (https://www.notion.so/lat-...)` means provider field `lat` maps to this Fleeti field
- Multiple provider fields may be listed (comma-separated): `"hdop (...), avl_io_182 (...)"`
- Empty value means this Fleeti field has no provider field mapping (likely calculated or asset_integrated)
- **Computation Approach** column provides priority order hints (e.g., `hdop>avl_io_182`)

**CRITICAL: Status Filtering**
- **Only process Fleeti Fields with `Status = inactive`** (these have no mapping yet)
- **Ignore Fleeti Fields with `Status = active`** (mappings already exist)

---

## Task: Generate Mapping Fields Database CSV

### Objective

Create a CSV file with Mapping Fields Database entries that:
1. Links Provider Fields to Fleeti Fields based on relationship indicators
2. Determines correct Mapping Type based on field characteristics and Computation Approach
3. Structures Priority JSON for prioritized mappings using `Computation Approach` column
4. Includes all required fields for YAML configuration generation
5. Sets appropriate status and configuration levels
6. **Only processes Fleeti Fields with `Status = inactive`**
7. **Joins with Fleeti Fields DB** to extract: `Field Path`, `Unit`, `Data Type`
8. **Joins with Provider Fields DB** to extract: `Field Path`, `Unit` (for each provider field)
9. **Auto-generates Unit Conversion** when Provider Unit ≠ Fleeti Unit

### Output CSV Columns (Required)

Based on the Mapping Fields Database schema, columns are organized into logical groups. Include these columns in the specified order:

#### Group 1: Core Identification (Required)

| Column Name | Required | Description | Example |
|------------|----------|-------------|---------|
| **Mapping Name** | ✅ Yes | Format: `[Fleeti Field Path] from [Provider]` | `location.latitude from Navixy` |
| **Fleeti Field** | ✅ Yes | Fleeti field name (from CSV) | `location_latitude` |
| **Fleeti Field Path** | ✅ Yes | JSON path in Fleeti telemetry (from Fleeti Fields DB join) | `location.latitude` |
| **Provider** | ✅ Yes | Provider name | `navixy` |
| **Mapping Type** | ✅ Yes | `direct`, `prioritized`, `calculated`, `transformed`, `io_mapped`, `asset_integrated`, `aggregated` | `direct` |
| **Status** | ✅ Yes | Mapping status | `active`, `deprecated`, `under_review`, `planned` |
| **Configuration Level** | ✅ Yes | Where this mapping applies | `default`, `customer`, `asset_group`, `asset` |

#### Group 2: Source Fields (Required)

| Column Name | Required | Description | Example |
|------------|----------|-------------|---------|
| **Provider Fields** | ✅ Yes | Comma-separated provider field names | `lat` (for direct) or `hdop, avl_io_182` (for prioritized) |
| **Provider Field Paths** | ✅ Yes | Provider field paths in packet (from Provider Fields DB join) | `lat` or `hdop, params.avl_io_182` |
| **Provider Unit** | ❌ No | Provider field unit (from Provider Fields DB join) | `km/h`, `degrees`, `°C` |

#### Group 3: Mapping Logic (Conditional - Required based on Mapping Type)

| Column Name | Required | Description | Example |
|------------|----------|-------------|---------|
| **Priority JSON** | Conditional | JSON array for prioritized mappings | `[{"priority": 1, "field": "hdop"}, {"priority": 2, "field": "avl_io_182"}]` |
| **Calculation Formula** | Conditional | Formula/logic (for calculated/transformed fields) | `derive_from_heading(location.heading)` or actual code from Computation Approach |
| **Transformation Rule** | Conditional | Transformation logic (for transformed fields) | `(fuel.level_percent / 100) * static.tank_capacity_liters` |
| **I/O Mapping Config** | Conditional | I/O mapping configuration in JSON (for io_mapped fields) | `{"default_source": "io.inputs.individual.input_1", "installation_metadata": "asset.installation.ignition_input_number"}` |
| **Asset Service Integration** | Conditional | Asset Service fields needed (for transformed/asset_integrated fields) | `asset.installation.ignition_input_number`, `static.tank_capacity_liters` |

#### Group 4: Dependencies & Execution Order

| Column Name | Required | Description | Example |
|------------|----------|-------------|---------|
| **Dependencies** | ❌ No | Other Fleeti fields this depends on (comma-separated) | `location_latitude, location_longitude` |
| **Calculation Type** | Conditional | How calculation is executed (for calculated mappings) | `formula`, `function_reference`, `code_based` |

#### Group 5: Error Handling & Defaults (Optional)

| Column Name | Required | Description | Example |
|------------|----------|-------------|---------|
| **Default Value** | ❌ No | Default value if no source available | `null`, `0`, `unknown` |
| **Error Handling** | ❌ No | What to do if mapping fails | `use_fallback`, `return_null`, `throw_error` |
| **Unit Conversion** | ❌ No | Unit conversion rule (auto-generated if Provider Unit ≠ Fleeti Unit) | `multiply by 0.00390625` |

#### Group 6: Backend Implementation (Optional)

| Column Name | Required | Description | Example |
|------------|----------|-------------|---------|
| **Backend Function Name** | ❌ No | Function name in backend registry (if function_reference, can be auto-extracted) | `derive_from_heading` |
| **Function Parameters** | ❌ No | Parameters passed to backend function (can be auto-extracted) | `location.heading` |
| **Implementation Location** | ❌ No | File path or documentation link to backend code | `telemetry-transformation-service/src/functions/cardinal.py:derive_cardinal_direction` |

#### Group 7: Metadata (Required)

| Column Name | Required | Description | Example |
|------------|----------|-------------|---------|
| **Fleeti Unit** | ❌ No | Fleeti field unit (from Fleeti Fields DB join) | `m/s`, `degrees`, `°C` |
| **Fleeti Data Type** | ❌ No | Fleeti field data type (from Fleeti Fields DB join) | `number`, `string`, `boolean`, `datetime` |
| **Version Added** | ✅ Yes | Version number | `1.0.0` |
| **Last Modified** | ✅ Yes | Date in YYYY-MM-DD format | `2025-01-16` |
| **Notes** | ❌ No | Additional context | `Direct 1:1 mapping, no conversion needed` |

**Important Notes:**
- `Modified By` and `Change History` are Notion metadata and should be omitted from the output CSV.
- **Priority Order** column has been removed (redundant with Priority JSON).
- **Fleeti Field Path**, **Provider Field Paths**, **Fleeti Unit**, **Fleeti Data Type**, and **Provider Unit** should be populated by joining with the respective database CSVs.
- **Unit Conversion** can be auto-generated when Provider Unit ≠ Fleeti Unit.

---

## Mapping Type Determination Rules

### 1. Direct Mapping (`direct`)

**Criteria:**
- Single provider field maps to single Fleeti field
- No calculation or transformation needed
- 1:1 relationship
- `Field Type = direct` in Fleeti Fields CSV
- Computation Approach is empty or contains field name only

**Example:**
- Provider Field: `lat` → Fleeti Field: `location_latitude`
- Mapping Type: `direct`
- Provider Fields: `lat`
- Computation Approach: `(Latitude)` - simple source reference

### 2. Prioritized Mapping (`prioritized`)

**Criteria:**
- Multiple provider fields represent the same Fleeti field concept
- Need to select best source based on priority
- `Field Type = direct` or `prioritized` in Fleeti Fields CSV
- Multiple provider fields in `💽 Provider Field (db)` column
- **Computation Approach contains priority order** (e.g., `hdop>avl_io_182`)

**Priority Order Parsing:**
- **Primary Method**: Parse `Computation Approach` column for `>` symbol
- **Pattern**: `field1>field2>field3` means priority 1, 2, 3 respectively
- **Example**: `hdop>avl_io_182` means `hdop` has priority 1, `avl_io_182` has priority 2
- **Fallback**: If no `>` symbol, use order from comma-separated `💽 Provider Field (db)` list

**Example:**
- Provider Fields: `hdop`, `avl_io_182` → Fleeti Field: `location_precision_hdop`
- Computation Approach: `hdop>avl_io_182`
- Mapping Type: `prioritized`
- Priority JSON: `[{"priority": 1, "field": "hdop"}, {"priority": 2, "field": "avl_io_182"}]`
- Priority Order: `hdop (1) > avl_io_182 (2)`

**Standard Priority Rules** (when Computation Approach doesn't specify):
- **Speed**: `can_speed` > `obd_speed` > `speed` (GPS)
- **RPM**: `can_rpm` > `obd_rpm` > `avl_io_85`
- **Odometer**: `can_mileage` > `hw_mileage` > `avl_io_105`
- **Fuel Level**: `can_fuel_1` > `fuel_level` > `avl_io_86`
- **Ignition**: `avl_io_898` (SSF) > `can_ignition_state` > `can_engine_state` > `avl_io_239`
- **Availability-based**: `always` > `conditional` > `rare` (when no other priority rule applies)

### 3. Calculated Mapping (`calculated`)

**Criteria:**
- Fleeti field is derived from other Fleeti fields or calculations
- No direct provider field mapping (empty `💽 Provider Field (db)` column)
- `Field Type = calculated` in Fleeti Fields CSV
- `Computation Approach` contains actual formulas/code
- **MUST NOT BE SKIPPED** - these are critical for the transformation pipeline

**Processing Order:**
- **CRITICAL**: Process calculated fields AFTER their dependency fields
- Use `Dependencies` column to identify which Fleeti fields must be processed first
- Extract calculation logic from `Computation Approach` column

**Example:**
- Fleeti Field: `location_cardinal_direction` (depends on `location_heading`)
- Computation Approach: `Derived from location.heading\n dirs = ["N","NE","E","SE","S","SW","W","NW"];\n cardinal = dirs[Math.floor((heading + 22.5) % 360 / 45)];`
- Mapping Type: `calculated`
- Calculation Type: `code_based` (contains actual code)
- Calculation Formula: Extract from Computation Approach
- Dependencies: `location_heading`
- Provider Fields: (empty - no provider fields)

**Another Example:**
- Fleeti Field: `location_last_changed_at` (depends on `location_latitude`, `location_longitude`)
- Computation Approach: `Backend compares current position with previous.\n if (lat !== prev.lat || lon !== prev.lon) {\n location_last_changed_at= now();\n }`
- Mapping Type: `calculated`
- Calculation Type: `code_based`
- Dependencies: `location_latitude`, `location_longitude`

**Calculation Type Determination:**
- **`function_reference`**: Simple, reusable calculation (e.g., cardinal direction from heading)
- **`code_based`**: Complex logic requiring custom code implementation
- **`formula`**: Parseable mathematical formula

### 4. Transformed Mapping (`transformed`)

**Criteria:**
- Combines provider telemetry with static asset metadata
- Requires Asset Service integration
- `Field Type = transformed` in Fleeti Fields CSV
- Computation Approach indicates transformation logic

**Example:**
- Provider Field: `can_fuel_1` (percentage) → Fleeti Field: `fuel_level_liters`
- Mapping Type: `transformed`
- Transformation Rule: `(can_fuel_1 / 100) * static.tank_capacity_liters`
- Asset Service Integration: `static.tank_capacity_liters`

### 5. I/O Mapped (`io_mapped`)

**Criteria:**
- Raw I/O field mapped to semantic field using installation metadata
- Requires Asset Service integration for mapping configuration
- `Field Type = io_mapped` in Fleeti Fields CSV

**Example:**
- Provider Field: `io.inputs.individual.input_1` → Fleeti Field: `power_ignition`
- Mapping Type: `io_mapped`
- I/O Mapping Config: `{"default_source": "io.inputs.individual.input_1", "installation_metadata": "asset.installation.ignition_input_number"}`

### 6. Asset-Integrated Mapping (`asset_integrated`)

**Criteria:**
- Field comes from Asset Service, not provider telemetry
- No provider field mapping
- `Field Type = asset_integrated` in Fleeti Fields CSV

**Example:**
- Fleeti Field: `asset.id` (from Asset Service)
- Mapping Type: `asset_integrated`
- Asset Service Integration: `asset.id`
- Provider Fields: (empty)

### 7. Aggregated Mapping (`aggregated`)

**Criteria:**
- Field represents aggregated/cumulative data
- May combine multiple provider fields or compute over time
- `Field Type = aggregated` in Fleeti Fields CSV

**Example:**
- Fleeti Field: `fuel.consumption.cumulative`
- Mapping Type: `aggregated`
- Provider Fields: Multiple fuel consumption sources

---

## Processing Instructions

### Step 1: Parse Input CSVs

1. Read Provider Fields CSV
2. Read Fleeti Fields CSV
3. **Filter Fleeti Fields**: Only keep rows where `Status = inactive` (ignore `active` status)
4. Extract relationship indicators from relation columns

### Step 2: Extract Field Names from Notion Links

**Pattern**: `field_name (https://www.notion.so/field_name-...)`

**Extraction Logic:**
- Split by `(` to separate field name from URL
- Take first part (field name)
- Trim whitespace
- For comma-separated: `"hdop (...), avl_io_182 (...)"` → Split by comma, then extract each field name
- Ignore the Notion URL portion completely

**Examples:**
- `lat (https://www.notion.so/lat-...)` → `lat`
- `hdop (https://...), avl_io_182 (https://...)` → `["hdop", "avl_io_182"]`
- Empty value → `[]` (no provider fields)

### Step 3: Identify Relationships

For each Fleeti Field with `Status = inactive`:

1. **Check `💽 Provider Field (db)` column** for Notion links to Provider Fields
2. **Extract provider field names** from the links (field name appears before the URL)
3. **Look up provider field details** in Provider Fields CSV
4. **Check `Computation Approach` column** for:
   - Priority order hints (e.g., `hdop>avl_io_182`)
   - Calculation formulas
   - Transformation logic
5. **Check `Field Type` column** to confirm mapping type
6. **Check `Dependencies` column** for calculated field dependencies

### Step 4: Determine Mapping Type

Use this decision tree:

1. **If Field Type = `calculated`**:
   - Mapping Type = `calculated`
   - Extract calculation logic from Computation Approach
   - Extract Dependencies from Dependencies column
   - **DO NOT SKIP** - process even if no Provider Fields relation

2. **If Field Type = `direct` AND multiple Provider Fields**:
   - Mapping Type = `prioritized`
   - Extract priority order from Computation Approach (e.g., `hdop>avl_io_182`)
   - If no explicit order, use standard priority rules

3. **If Field Type = `direct` AND single Provider Field**:
   - Mapping Type = `direct`

4. **If Field Type = `transformed`**:
   - Mapping Type = `transformed`
   - Extract transformation rule from Computation Approach

5. **If Field Type = `io_mapped`**:
   - Mapping Type = `io_mapped`
   - Generate I/O Mapping Config JSON

6. **If Field Type = `asset_integrated`**:
   - Mapping Type = `asset_integrated`
   - Extract Asset Service Integration requirements

7. **If Field Type = `aggregated`**:
   - Mapping Type = `aggregated`
   - May have multiple Provider Fields

### Step 5: Parse Priority Order from Computation Approach

**For Prioritized Mappings:**

1. **Check Computation Approach column** for `>` symbol
2. **Parse pattern**: `field1>field2>field3` → priority 1, 2, 3
3. **Extract field names** and assign priorities
4. **Generate Priority JSON**: `[{"priority": 1, "field": "field1"}, {"priority": 2, "field": "field2"}]`
5. **Generate Priority Order**: `field1 (1) > field2 (2) > field3 (3)`

**Example:**
- Computation Approach: `hdop>avl_io_182`
- Provider Fields: `["hdop", "avl_io_182"]`
- Priority JSON: `[{"priority": 1, "field": "hdop"}, {"priority": 2, "field": "avl_io_182"}]`
- Priority Order: `hdop (1) > avl_io_182 (2)`

**Fallback (no `>` symbol):**
- Use order from comma-separated `💽 Provider Field (db)` list
- First field = priority 1, second = priority 2, etc.
- Or use standard priority rules based on field names

### Step 6: Process Calculated Fields

**CRITICAL: Process calculated fields AFTER their dependencies**

1. **Identify calculated fields**: `Field Type = calculated` and empty `💽 Provider Field (db)`
2. **Extract dependencies** from `Dependencies` column (Notion links to other Fleeti Fields)
3. **Sort by dependency depth**: Process fields with no dependencies first, then fields that depend on them
4. **Extract calculation logic** from `Computation Approach` column:
   - Contains code → `Calculation Type = code_based`
   - Contains function reference → `Calculation Type = function_reference`
   - Contains parseable formula → `Calculation Type = formula`
5. **Generate mapping entry** with `Mapping Type = calculated`

**Example:**
- Fleeti Field: `location_cardinal_direction`
- Dependencies: `location_heading`
- Computation Approach: `Derived from location.heading\n dirs = ["N","NE",...];\n cardinal = dirs[Math.floor((heading + 22.5) % 360 / 45)];`
- Process `location_heading` first, then `location_cardinal_direction`

### Step 7: Generate Mapping Entries

For each identified relationship:

1. **Create Mapping Name**: `[Fleeti Field Path] from [Provider]`
   - Use `Field Path` from Fleeti Fields CSV (e.g., `location.latitude`)
   - Capitalize provider name (e.g., `Navixy`)
   - Example: `location.latitude from Navixy`

2. **Set Required Fields**:
   - Fleeti Field: Use `Name` from Fleeti Fields CSV
   - Provider: Extract from Provider Fields CSV
   - Provider Fields: List all related provider fields (comma-separated)
   - Mapping Type: Determine based on rules above
   - Configuration Level: Default to `default`
   - Status: Default to `planned` (will be activated after validation)
   - Version Added: `1.0.0`
   - Last Modified: Current date in YYYY-MM-DD format

3. **Set Conditional Fields** (based on Mapping Type):
   - **Prioritized**: 
     - Parse Computation Approach for priority order (e.g., `hdop>avl_io_182`)
     - Generate Priority JSON: `[{"priority": 1, "field": "hdop"}, {"priority": 2, "field": "avl_io_182"}]`
     - Generate Priority Order: `hdop (1) > avl_io_182 (2)`
   - **Calculated**: 
     - Extract Calculation Formula from Computation Approach
     - Determine Calculation Type based on formula complexity
     - Extract Dependencies from Dependencies column
     - Set Backend Function Name if function_reference
   - **Transformed**: 
     - Extract Transformation Rule from Computation Approach
     - Extract Asset Service Integration requirements
   - **I/O Mapped**: 
     - Generate I/O Mapping Config JSON
   - **Asset-Integrated**: 
     - Extract Asset Service Integration requirements
   - **Aggregated**: 
     - May have multiple Provider Fields

4. **Handle Dependencies**:
   - For calculated fields, extract dependency Fleeti field names from Dependencies column
   - Process calculated fields AFTER their dependencies have been processed
   - Ensure no circular dependencies

### Step 8: Handle Edge Cases

1. **Multiple Provider Fields → One Fleeti Field**:
   - Create ONE mapping entry with all provider fields
   - Set Mapping Type to `prioritized`
   - Generate Priority JSON based on Computation Approach (`>` symbol) or field order

2. **One Provider Field → Multiple Fleeti Fields**:
   - Create SEPARATE mapping entries for each Fleeti Field
   - Each entry references the same provider field

3. **Calculated Fields (No Provider Fields)**:
   - **DO NOT SKIP** - create mapping entry with Mapping Type = `calculated`
   - Leave Provider Fields empty
   - Extract calculation logic from Computation Approach
   - Extract dependencies from Dependencies column
   - Process after dependency fields

4. **Missing Relationship Indicators**:
   - If Fleeti Field has no Provider Fields relation AND Field Type = `calculated`: Create calculated mapping entry
   - If Fleeti Field has no Provider Fields relation AND Field Type = `asset_integrated`: Create asset_integrated mapping entry
   - If Fleeti Field has no Provider Fields relation AND Field Type ≠ `calculated`/`asset_integrated`: Skip (not yet mapped)
   - If Provider Field has no Fleeti Fields relation: Skip (not yet mapped)

5. **Status Filtering**:
   - **ONLY process Fleeti Fields with Status = inactive**
   - Skip Fleeti Fields with Status = active (mapping already exists)
   - Skip Fleeti Fields with Status = deprecated

---

## Output Format

### CSV File Structure

Generate a CSV file with:
- **Header row**: All column names from "Output CSV Columns" section (excluding Notion metadata columns)
- **Data rows**: One row per mapping entry
- **Encoding**: UTF-8
- **Delimiter**: Comma (`,`)
- **Quote handling**: Quote fields containing commas or special characters
- **Date format**: YYYY-MM-DD for Last Modified

### File Naming Convention

`Mapping-Fields-[Provider]-[Date].csv`

Example: `Mapping-Fields-Navixy-2025-01-16.csv`

### Processing Order

1. Process direct mappings first
2. Process prioritized mappings
3. Process transformed mappings
4. Process io_mapped mappings
5. Process asset_integrated mappings
6. Process aggregated mappings
7. Process calculated mappings last (after dependencies)

---

## Validation Criteria

Before finalizing the CSV, validate:

1. ✅ **Only Fleeti Fields with Status = inactive are processed**
2. ✅ **All required columns present** and populated
3. ✅ **Mapping Names are unique** (no duplicates)
4. ✅ **Fleeti Field names match** exactly from Fleeti Fields CSV
5. ✅ **Provider Field names match** exactly from Provider Fields CSV
6. ✅ **Priority JSON is valid JSON** (if present)
7. ✅ **I/O Mapping Config is valid JSON** (if present)
8. ✅ **Mapping Type matches** the relationship characteristics
9. ✅ **No circular dependencies** in calculated fields
10. ✅ **Calculated fields processed after dependencies**
11. ✅ **Status is appropriate** (`planned` for new mappings)
12. ✅ **Computation Approach parsed correctly** for priority order (`>` symbol)

---

## Example Output

### Example 1: Direct Mapping

```csv
Mapping Name,Fleeti Field,Provider,Provider Fields,Mapping Type,Priority Order,Priority JSON,Configuration Level,Status,Version Added,Last Modified,Notes
location.latitude from Navixy,location_latitude,navixy,lat,direct,,,,default,planned,1.0.0,2025-01-16,Direct 1:1 mapping
```

### Example 2: Prioritized Mapping

```csv
Mapping Name,Fleeti Field,Provider,Provider Fields,Mapping Type,Priority Order,Priority JSON,Configuration Level,Status,Version Added,Last Modified,Notes
location.precision.hdop from Navixy,location_precision_hdop,navixy,"hdop, avl_io_182",prioritized,"hdop (1) > avl_io_182 (2)","[{""priority"": 1, ""field"": ""hdop""}, {""priority"": 2, ""field"": ""avl_io_182""}]",default,planned,1.0.0,2025-01-16,HDOP from direct field preferred over AVL IO, priority from Computation Approach
```

### Example 3: Calculated Mapping

```csv
Mapping Name,Fleeti Field,Provider,Provider Fields,Mapping Type,Calculation Type,Calculation Formula,Backend Function Name,Function Parameters,Dependencies,Configuration Level,Status,Version Added,Last Modified,Notes
location.cardinal_direction from Navixy,location_cardinal_direction,navixy,,calculated,code_based,"dirs = [""N"",""NE"",""E"",""SE"",""S"",""SW"",""W"",""NW""]; cardinal = dirs[Math.floor((heading + 22.5) % 360 / 45)];",,,location_heading,default,planned,1.0.0,2025-01-16,Derived from location.heading using cardinal direction calculation, depends on location_heading
```

---

## Frequently Asked Questions

### Q1: How do I determine priority order for prioritized mappings?

**A:** Priority order is determined in this order of precedence:

1. **Computation Approach column** - Parse explicit priority hints (e.g., `hdop>avl_io_182` means `hdop` priority 1, `avl_io_182` priority 2)
2. **Standard priority rules** - If no explicit order, use standard rules:
   - CAN > OBD > GPS/Hardware (for speed, RPM, odometer)
   - SSF > CAN > Hardware (for ignition)
   - Direct fields > AVL IO fields (for precision metrics)
3. **Availability** - As last resort: `always` > `conditional` > `rare`

**Example:** If Computation Approach shows `hdop>avl_io_182`, use that order. If empty, check if it's a speed field and use `can_speed > obd_speed > speed`.

---

### Q2: How do I parse the Computation Approach column?

**A:** The Computation Approach column contains different information based on Field Type:

- **Prioritized mappings**: Contains priority order hints (e.g., `hdop>avl_io_182`)
  - Parse the `>` symbol to determine priority order
  - Left side = priority 1, right side = priority 2, etc.
  
- **Calculated mappings**: Contains calculation formulas/logic
  - Extract the entire formula or logic description
  - Determine if it's `function_reference`, `code_based`, or `formula`
  
- **Direct mappings**: May be empty or contain field name only
  - Ignore if empty or just field name

**Example:** `hdop>avl_io_182` → Priority: `hdop` (1), `avl_io_182` (2)

---

### Q3: Should I skip calculated fields that have no Provider Fields relation?

**A:** **NO - DO NOT SKIP CALCULATED FIELDS.** Calculated fields are critical for the transformation pipeline even if they don't have direct provider field mappings. They depend on other Fleeti fields and must be processed after their dependencies.

**Processing order:**
1. Process direct mappings first
2. Process prioritized mappings
3. Process calculated mappings AFTER their dependency fields have been processed

**Example:** `location_cardinal_direction` depends on `location_heading`. Process `location_heading` first, then `location_cardinal_direction`.

---

### Q4: How do I extract field names from the relation columns?

**A:** Extract field names using this pattern:

1. **Single field**: `lat (https://www.notion.so/lat-...)` → Extract `lat` (everything before the opening parenthesis)
2. **Multiple fields**: `hdop (https://...), avl_io_182 (https://...)` → Split by comma, extract each field name
3. **Ignore URLs**: Completely ignore the Notion URL portion (everything in parentheses)
4. **Trim whitespace**: Remove leading/trailing spaces from field names

**Examples:**
- `lat (https://...)` → `lat`
- `hdop (https://...), avl_io_182 (https://...)` → `["hdop", "avl_io_182"]`
- `location_heading (https://...)` → `location_heading`

---

### Q5: Should I include Notion-specific columns like Modified By or Change History?

**A:** **NO - OMIT THESE COLUMNS.** Notion-specific metadata columns should be omitted from the CSV output:

- `Modified By` (Person type) - Notion-specific
- `Change History` (Relation) - Notion-specific, database not yet defined
- `YAML Config Version` - Will be populated after YAML generation
- `YAML Path` - Will be populated after YAML generation

**Include only:** Columns that are needed for mapping logic and YAML generation.

---

### Q6: Should I process Fleeti Fields with Status = active?

**A:** **NO - ONLY PROCESS Status = inactive.** 

- **`inactive`**: No mapping exists yet - **PROCESS THESE**
- **`active`**: Mapping already exists - **SKIP THESE**
- **`deprecated`**: Field deprecated - **SKIP THESE**

The goal is to create mappings for fields that don't have mappings yet. Active status means the mapping work is already done.

---

### Q7: Should I handle unit conversions?

**A:** **NO - DO NOT HANDLE UNIT CONVERSIONS IN THIS STEP.** 

Unit conversion is a separate concern that will be handled during YAML configuration generation or manual review. Focus only on creating the mapping relationships and structure.

**Note:** Unit mismatches (like `lat` showing `°C` in Provider Fields) are likely export issues and should be ignored.

---

### Q8: What if a Fleeti Field has Field Type = direct but Computation Approach shows priority order?

**A:** **USE THE PRIORITY ORDER FROM COMPUTATION APPROACH.** Even if Field Type is `direct`, if multiple Provider Fields are listed and Computation Approach shows priority order (e.g., `hdop>avl_io_182`), treat it as a **prioritized mapping**.

**Example:** `location_precision_hdop` has Field Type = `direct` but Computation Approach = `hdop>avl_io_182` and multiple Provider Fields → Mapping Type = `prioritized`

---

### Q9: How do I handle calculated fields that depend on other Fleeti fields?

**A:** **PROCESS CALCULATED FIELDS AFTER THEIR DEPENDENCIES.**

1. Extract dependencies from the `Dependencies` column in Fleeti Fields CSV
2. Process all direct/prioritized mappings first
3. Process calculated fields in dependency order (dependencies first, dependents after)
4. Ensure no circular dependencies exist

**Example:** 
- `location_cardinal_direction` depends on `location_heading`
- Process `location_heading` mapping first
- Then process `location_cardinal_direction` calculated mapping

---

### Q10: What if Computation Approach is empty or unclear?

**A:** **USE FIELD TYPE AND STANDARD RULES.**

1. Check `Field Type` column to determine mapping type
2. If `Field Type = direct` and multiple Provider Fields → use standard priority rules
3. If `Field Type = calculated` → extract from Dependencies column and mark as calculated
4. If unclear, set Status = `under_review` and add Notes explaining the uncertainty

---

## Important Notes

1. **Notion Links**: The relation columns contain Notion URLs. Extract the field name from before the URL (e.g., `location_latitude (https://...)` → field name is `location_latitude`)

2. **Field Name vs Field Path**: 
   - Fleeti Field **Name**: `location_latitude` (database identifier, use in Fleeti Field column)
   - Fleeti Field **Path**: `location.latitude` (JSON path, use in Mapping Name)

3. **Provider Field Names**: Use exact names from Provider Fields CSV (e.g., `lat`, not `latitude`)

4. **Status Workflow**: 
   - New mappings: `planned`
   - After validation: `under_review`
   - After testing: `active`
   - Deprecated: `deprecated`

5. **Processing Order Matters**: 
   - Direct → Prioritized → Transformed → I/O Mapped → Asset-Integrated → Aggregated → Calculated (after dependencies)

6. **Computation Approach Parsing**: 
   - `>` symbol indicates priority order for prioritized mappings
   - Contains actual code/formulas for calculated fields
   - Contains source references `(Source Name)` for direct mappings

7. **Status Filtering**: **CRITICAL** - Only process Fleeti Fields with `Status = inactive`. Ignore `Status = active` fields.

---

## Success Criteria

The generated CSV is successful when:

- ✅ Only Fleeti Fields with Status = inactive are processed
- ✅ All Fleeti Fields with Provider Field relations have corresponding mapping entries
- ✅ Calculated fields are included (not skipped) and processed after dependencies
- ✅ Mapping Types correctly reflect the transformation logic
- ✅ Priority JSON is valid and follows Computation Approach hints or standard rules
- ✅ CSV can be imported into Notion Mapping Fields Database without errors
- ✅ Mappings enable YAML configuration file generation
- ✅ All required fields are populated
- ✅ No data inconsistencies or missing relationships
- ✅ Field names extracted correctly from relation columns

---

## Your Task

Given the Provider Fields CSV and Fleeti Fields CSV exports, generate a complete Mapping Fields Database CSV file that:

1. **Filters** to only process Fleeti Fields with Status = inactive
2. Links all identified Provider Field → Fleeti Field relationships
3. Determines correct Mapping Types based on Field Type and Computation Approach
4. Structures Priority JSON for prioritized mappings using Computation Approach hints (`>` symbol)
5. Includes calculated fields (even without Provider Fields) and processes them after dependencies
6. Extracts field names correctly from relation columns (ignoring Notion URLs)
7. Includes all required metadata for YAML configuration generation
8. Follows the validation criteria above

**Output**: A CSV file ready for import into Notion's Mapping Fields Database.

---

**Last Updated:** 2025-01-16  
**Version:** 1.0.0
