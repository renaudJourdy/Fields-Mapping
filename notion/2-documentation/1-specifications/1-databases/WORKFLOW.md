# Workflow: Sources JSON Structure

**Status:** Active

## Overview

This workflow describes the process for generating YAML configurations using the new **Sources JSON** structure. This replaces the previous Priority JSON approach with a more explicit format that supports:

- **Explicit provider specification** per source
- **Mixed source types** (direct provider, calculated, fleeti reference)
- **Structured parameters** with provider context
- **Clearer priority chains** with complete source definitions

---

## YAML Structure

### Mapping Types

The system supports five types of field transformations:

1. **Direct Mapping**: 1:1 provider field → Fleeti field mapping
2. **Prioritized Mapping**: Multiple provider sources with priority order
3. **Calculated Mapping**: Derived from other fields using functions
4. **Transformed Mapping**: Combines telemetry with static asset metadata
5. **I/O Mapped**: Maps raw I/O signals to semantic fields via installation metadata

### Prioritized Mapping with Sources JSON

```yaml
inputs_individual_input_1:
  type: prioritized
  sources:
    - priority: 1
      type: direct
      source_type: provider
      provider: navixy
      field: avl_io_1
      path: params.avl_io_1
      description: "Digital Input 1 from Navixy"
    - priority: 2
      type: calculated
      calculation_type: function_reference
      function: extract_bit_from_bitmask
      parameters:
        provider:
          navixy: din
      description: "Extract bit 0 from Digital Inputs Bitmask"
    - priority: 3
      type: direct
      source_type: fleeti
      field: io_inputs_individual_input_2
      description: "Fallback to another Fleeti field"
  data_type: boolean
  error_handling: use_fallback
  # Field Path: io.inputs.individual.input_1
```

### Transformed Mapping Example

```yaml
fuel_level_liters:
  type: transformed
  transformation: "(fuel.level_percent / 100) * static.tank_capacity_liters"
  service_fields:
    - asset.properties.vehicle.fuel_tank_capacity.value
  data_type: number
  unit: liters
  error_handling: return_null
  # Field Path: fuel.level.liters
```

### I/O Mapped Example

```yaml
power_ignition:
  type: io_mapped
  default_source: io.inputs.individual.input_1
  installation_metadata: asset.installation.ignition_input_number
  data_type: boolean
  error_handling: use_fallback
  # Field Path: power.ignition
```

### Sources JSON Format

Each source in the `sources` array contains:

- **priority**: Integer (1, 2, 3...)
- **type**: `direct` or `calculated`
- **source_type**: `provider` or `fleeti` (for direct sources)
- **provider**: Provider name (e.g., `navixy`, `oem-trackunit`) - required for provider sources
- **field**: Field name identifier
- **path**: Provider field path (for provider sources)
- **calculation_type**: `function_reference` (for calculated sources)
- **function**: Backend function name (for calculated sources)
- **parameters**: Function parameters with provider context:
  ```json
  {
    "provider": {
      "navixy": "field_name"
    }
  }
  ```
- **description**: Human-readable description

---

## Workflow Steps

### 1. Fleeti Fields Generation & Update

**Location:** `2-fleeti-fields/`

#### Step 1.1: Generate Base CSV
```bash
cd 2-fleeti-fields/scripts
python generate_fleeti_fields.py
```
Output: `Fleeti-Fields-YYYY-MM-DD.csv`

#### Step 1.2: Edit CSV
- Add/remove/modify fields as needed
- Ensure all required columns are present

#### Step 1.3: Add Mapping Requirements in Notes Column
For each field, describe mapping requirements in the **Notes** column:

**Examples:**
- `"Direct mapping from Navixy: avl_io_1"`
- `"Prioritized: Navixy avl_io_1, then extract bit 0 from din bitmask"`
- `"Calculated: derive from location_latitude and location_longitude using geocoding API"`
- `"Mix: Direct Navixy avl_io_1, fallback to calculated extract_bit_from_bitmask with din"`

#### Step 1.4: Generate Computation Approach & Sources JSON
Use AI (Cursor command `build-fleeti-field-json`) to generate:
- **Computation Approach**: Human-readable description
- **Computation Structure JSON**: Sources JSON array matching YAML structure

**Computation Approach Syntax Patterns:**
- Direct: `"Direct mapping from {provider}: {field} ({description})"`
- Prioritized: `"Direct mapping from {provider}: {field}. If only {fallback_field} is available, {function_description}"`
- Calculated: `"Derived from {dependencies} using {function_name}"`
- Mixed: Combine patterns above

#### Step 1.5: Validate
- Check all Computation Approach fields are populated
- Verify Sources JSON is valid JSON
- Ensure Sources JSON matches Computation Approach description

#### Step 1.6: Import to Notion
- Import CSV to Fleeti Fields Database
- Adjust columns that cannot be modified in CSV (relations, rollups, etc.)

#### Step 1.7: Export from Notion
- Export updated database to `export/Fleeti Fields (db) YYYY-MM-DD.csv`

---

### 2. Mapping Fields Generation & Update

**Location:** `3-mapping-fields/`

#### Step 2.1: Identify Existing Mappings
Review `export/Mapping Fields (db) YYYY-MM-DD.csv` to identify:
- Already specified mappings
- Fields that need new mappings

**Focus:** Only create mappings for new Fleeti Fields not yet mapped.

#### Step 2.2: Generate Mapping Fields CSV
```bash
cd 3-mapping-fields/scripts
python generate_mapping_fields.py
```

**Input:** `input/Fleeti Fields (db) YYYY-MM-DD.csv`  
**Output:** `Mapping-Fields-Navixy-YYYY-MM-DD.csv`

**Script modifications required:**
- Read `Computation Structure JSON` from Fleeti Fields CSV
- Generate Mapping Fields entries with:
  - `Mapping Type`: Determine from field type (direct, prioritized, calculated, transformed, io_mapped)
  - `Sources JSON`: Populated from Fleeti Fields `Computation Structure JSON` (for prioritized mappings)
  - `Computation Approach`: From Fleeti Fields (for calculated mappings)
  - `Transformation Rule`: For transformed mappings (combines telemetry with static data)
  - `I/O Mapping Config`: For io_mapped fields (default_source and installation_metadata)
  - `Service Integration`: For transformed/io_mapped fields (references to Asset Service)
  - `Function Parameters`: Extracted from Sources JSON parameters (for calculated mappings)

#### Step 2.3: Verify Results
- Check Sources JSON format matches expected structure
- Verify provider names are correct
- Ensure priority order is logical

#### Step 2.4: Import to Notion
- Import CSV to Mapping Fields Database
- Adjust columns that cannot be modified in CSV

#### Step 2.5: Export from Notion
- Export updated database to `export/Mapping Fields (db) YYYY-MM-DD.csv`

---

### 3. YAML Configuration Generation

**Location:** `5-yaml-configuration/`

#### Step 3.1: Prepare Input
Copy Mapping Fields export to input folder:
```bash
cp 3-mapping-fields/export/Mapping\ Fields\ \(db\)\ YYYY-MM-DD.csv \
   5-yaml-configuration/scripts/input/Mapping\ Fields\ \(db\)\ YYYY-MM-DD.csv
```

#### Step 3.2: Generate YAML
```bash
cd 5-yaml-configuration/scripts
python generate_yaml_config.py
```

**Script modifications required:**
- Read `Sources JSON` column from Mapping Fields CSV (for prioritized mappings)
- Parse Sources JSON array and generate YAML `sources` array
- Handle all mapping types:
  - **Direct**: Generate `type: direct` with `source` field
  - **Prioritized**: Generate `type: prioritized` with `sources` array from Sources JSON
  - **Calculated**: Generate `type: calculated` with `function` and `parameters`
  - **Transformed**: Generate `type: transformed` with `transformation` and `service_fields`
  - **I/O Mapped**: Generate `type: io_mapped` with `default_source` and `installation_metadata`
- Handle all source types in Sources JSON: direct (provider), direct (fleeti), calculated

**Output:** `navixy-mapping.yaml`

#### Step 3.3: Validate YAML
- Check all sources have required fields
- Verify provider names are consistent
- Ensure calculated sources have function and parameters

#### Step 3.4: Update Notion
- Link generated YAML to YAML Configuration Database entry
- Update version if needed

---

## Key Concepts

### Field Transformation Types

**1. Direct Mapping**
- 1:1 provider field → Fleeti field
- Optional unit conversion
- Example: `lat` → `location.latitude`

**2. Prioritized Mapping**
- Multiple provider sources with priority order
- Select best available source
- Example: `can_speed > obd_speed > gps_speed`

**3. Calculated Mapping**
- Derived from other fields using functions
- Types: aggregation, derivation, conditions, lookup, value change tracking
- Example: `location.cardinal_direction` from `location.heading`

**4. Transformed Mapping**
- Combines telemetry with static asset metadata
- Requires Asset Service integration
- Example: `fuel.level_liters = (fuel.level_percent / 100) * tank_capacity`

**5. I/O Mapped**
- Maps raw I/O signals to semantic fields
- Uses installation metadata for mapping
- Example: `io.inputs.individual.input_1` + `ignition_input_number` → `power.ignition`

### Sources JSON Structure

**Direct Provider Source:**
```json
{
  "priority": 1,
  "type": "direct",
  "source_type": "provider",
  "provider": "navixy",
  "field": "avl_io_1",
  "path": "params.avl_io_1",
  "description": "Digital Input 1 from Navixy"
}
```

**Direct Fleeti Source:**
```json
{
  "priority": 3,
  "type": "direct",
  "source_type": "fleeti",
  "field": "io_inputs_individual_input_2",
  "description": "Fallback to another Fleeti field"
}
```

**Calculated Source:**
```json
{
  "priority": 2,
  "type": "calculated",
  "calculation_type": "function_reference",
  "function": "extract_bit_from_bitmask",
  "parameters": {
    "provider": {
      "navixy": "din"
    }
  },
  "description": "Extract bit 0 from Digital Inputs Bitmask"
}
```

**Note**: Transformed and I/O Mapped fields use different YAML structures (not Sources JSON) as they require additional configuration (transformation rules, service fields, installation metadata).

### Computation Approach Syntax

**Pattern Recognition:**
- `"Direct mapping from {provider}: {field}"` → Direct source
- `"If only {field} bitmask is available, extract bit {N}"` → Calculated fallback
- `"Derived from {dependencies} using {function}"` → Calculated source
- Provider names: `navixy`, `oem-trackunit`, `teltonika` (case-insensitive)

**Function Inference:**
- `"extract bit {N}"` → `extract_bit_from_bitmask`
- `"derive {field}"` → `derive_{field_name}`
- Explicit function names if mentioned

### Provider Specification

**In Parameters:**
```json
{
  "provider": {
    "navixy": "field_name"
  }
}
```

**In Direct Sources:**
- Explicit `provider` field in source object
- Inherits from mapping row if not specified

---

## File Locations

### Fleeti Fields
- **Script:** `2-fleeti-fields/scripts/generate_fleeti_fields.py`
- **Input:** `2-fleeti-fields/scripts/input/fleeti-telemetry-schema-specification.md`
- **Output:** `2-fleeti-fields/scripts/Fleeti-Fields-YYYY-MM-DD.csv`
- **Export:** `2-fleeti-fields/export/Fleeti Fields (db) YYYY-MM-DD.csv`

### Mapping Fields
- **Script:** `3-mapping-fields/scripts/generate_mapping_fields.py`
- **Input:** `3-mapping-fields/scripts/input/Fleeti Fields (db) YYYY-MM-DD.csv`
- **Output:** `3-mapping-fields/scripts/Mapping-Fields-Navixy-YYYY-MM-DD.csv`
- **Export:** `3-mapping-fields/export/Mapping Fields (db) YYYY-MM-DD.csv`

### YAML Configuration
- **Script:** `5-yaml-configuration/scripts/generate_yaml_config.py`
- **Input:** `5-yaml-configuration/scripts/input/Mapping Fields (db) YYYY-MM-DD.csv`
- **Output:** `5-yaml-configuration/scripts/navixy-mapping.yaml`

---

## Notes Column Format (Fleeti Fields)

When adding mapping requirements in the Notes column, use these patterns:

**Direct Mapping:**
```
Direct mapping from Navixy: avl_io_1 (Digital Input 1)
```

**Prioritized Mapping:**
```
Prioritized: Navixy avl_io_1 (priority 1), then extract bit 0 from din bitmask (priority 2)
```

**Calculated Mapping:**
```
Calculated: derive from location_latitude and location_longitude using geocoding API
```

**Transformed Mapping:**
```
Transformed: fuel.level_percent combined with asset.properties.vehicle.fuel_tank_capacity.value to calculate fuel.level_liters
```

**I/O Mapped:**
```
I/O Mapped: io.inputs.individual.input_1 mapped to power.ignition using asset.installation.ignition_input_number
```

**Mixed Mapping (Prioritized with multiple source types):**
```
Mix: Direct Navixy avl_io_1 (priority 1), fallback to calculated extract_bit_from_bitmask with din (priority 2), then fleeti field io_inputs_individual_input_2 (priority 3)
```

The AI will parse these patterns and generate:
1. **Computation Approach**: Human-readable description
2. **Computation Structure JSON**: Structured Sources JSON array

---

## Validation Checklist

### Fleeti Fields CSV
- [ ] All fields have Computation Approach populated
- [ ] All fields have valid Computation Structure JSON
- [ ] Sources JSON matches Computation Approach description
- [ ] Provider names are consistent (lowercase)
- [ ] Priority order is logical (1, 2, 3...)

### Mapping Fields CSV
- [ ] Mapping Type correctly determined (direct, prioritized, calculated, transformed, io_mapped)
- [ ] Sources JSON column populated from Fleeti Fields (for prioritized mappings)
- [ ] Computation Approach matches Fleeti Fields (for calculated mappings)
- [ ] Transformation Rule present (for transformed mappings)
- [ ] I/O Mapping Config present (for io_mapped fields)
- [ ] Service Integration fields specified (for transformed/io_mapped)
- [ ] Function Parameters extracted correctly from Sources JSON
- [ ] Provider names match Sources JSON

### YAML Configuration
- [ ] All mapping types correctly generated (direct, prioritized, calculated, transformed, io_mapped)
- [ ] Prioritized mappings have valid Sources JSON structure
- [ ] All sources have required fields
- [ ] Provider names are consistent
- [ ] Calculated sources have function and parameters
- [ ] Transformed mappings have transformation rule and service_fields
- [ ] I/O mapped fields have default_source and installation_metadata
- [ ] Priority order is correct
- [ ] Field paths are valid

