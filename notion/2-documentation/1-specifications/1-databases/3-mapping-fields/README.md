**Status:** 🎯 In Progress

# Purpose

The Mapping Fields Database contains field transformation rules and priority chains that link provider fields to Fleeti fields.

---

# What This Database Contains

- **Direct mappings**: 1:1 provider field → Fleeti field mappings
- **Priority chains**: Multiple provider fields → one Fleeti field (with priority order)
- **Calculation rules**: Formulas and logic for calculated fields
- **I/O mappings**: Raw I/O fields → semantic fields (with installation metadata)
- **Transformation logic**: Static data transformations (e.g., fuel level % → liters)

---

# Database Structure

## Column Definitions

Columns are organized into logical groups for clarity and YAML generation workflow.

### Group 1: Core Identification (Required)

| Column Name | Type | Required | Description | Example | Why It's Important |
| --- | --- | --- | --- | --- | --- |
| **Mapping Name** | Title | ✅ Yes | Descriptive mapping name (primary identifier) | `motion.speed from Navixy` | Primary key - human-readable identifier. Helps identify mapping purpose at a glance. |
| **Fleeti Field** | Relation | ✅ Yes | Links to Fleeti Fields DB | `motion_speed` | Target field identifier. Required for all mappings. Critical for configuration generation. |
| **Fleeti Field Path** | Text | ✅ Yes | JSON path in Fleeti telemetry object (from Fleeti Fields DB join) | `motion.speed` | Used for reference/documentation only. **NOT used as YAML key** - Field Name is used instead. Backend resolves Field Name → Field Path at runtime. |
| **Provider** | Select | ✅ Yes | Provider name | `navixy`, `oem-trackunit`, `oem-volvo` | Identifies which provider this mapping applies to. Required for multi-provider support. |
| **Mapping Type** | Select | ✅ Yes | Type of mapping | `direct`, `prioritized`, `calculated`, `aggregated`, `transformed`, `io_mapped`, `asset_integrated` | Determines transformation approach. Critical for configuration generation. Each type has different requirements. |
| **Status** | Select | ✅ Yes | Mapping status | `active`, `deprecated`, `under_review`, `planned` | Tracks mapping lifecycle. Deprecated mappings should not be used. Critical for data quality and configuration generation. |
| **Configuration Level** | Select | ✅ Yes | Where this mapping applies | `default`, `customer`, `asset_group`, `asset` | Defines mapping hierarchy. Lower levels override higher levels. Critical for hierarchical configuration support. |

### Group 2: Source Fields (Required)

| Column Name | Type | Required | Description | Example | Why It's Important |
| --- | --- | --- | --- | --- | --- |
| **Provider Fields** | Relation | ✅ Yes | Links to Provider Fields DB (can be multiple) | `can_speed`, `obd_speed`, `speed` | Source field identifiers. Can be single (direct) or multiple (prioritized). Critical for transformation. |
| **Provider Field Paths** | Text | ✅ Yes | Provider field paths in packet (from Provider Fields DB join) | `params.can_speed`, `params.obd_speed`, `speed` | Used to read values from provider packets. Critical for YAML generation. |
| **Provider Unit** | Text | ❌ No | Provider field unit (from Provider Fields DB join) | `km/h`, `degrees`, `°C` | Used to detect unit conversion needs. Can be auto-generated from Provider Fields DB. |

### Group 3: Mapping Logic (Conditional - Required based on Mapping Type)

| Column Name | Type | Required | Description | Example | Why It's Important |
| --- | --- | --- | --- | --- | --- |
| **Priority JSON** | Text | Conditional | Structured priority data in JSON (for prioritized mappings) | `[{"priority": 1, "field": "can_speed"}, {"priority": 2, "field": "obd_speed"}]` | Machine-readable priority order. Used directly in YAML config generation. Required for `prioritized` mappings. |
| **Computation Approach** | Rollup | Conditional | Computation logic rolled up from Fleeti Fields Database relation | See below | **Notion rollup field** that automatically pulls the `Computation Approach` value from the related Fleeti Field entry. Documents computation logic from the Fleeti Fields Database. Used as comments in generated YAML configuration. Required for `calculated` mappings. When exported to CSV, appears as a regular column. |
| **Transformation Rule** | Text | Conditional | Transformation logic (for transformed fields) | `(fuel.level_percent / 100) * static.tank_capacity_liters` | Documents transformation combining telemetry with static data. Required for `transformed` mappings. Used in config generation. |
| **I/O Mapping Config** | Text | Conditional | I/O mapping configuration in JSON (for io_mapped fields) | `{"default_source": "io.inputs.individual.input_1", "installation_metadata": "asset.installation.ignition_input_number"}` | Configuration for I/O to semantic field mapping. Required for `io_mapped` type. Links raw I/O to semantic meaning via installation metadata. |
| **Service Integration** | Text | Conditional | External service fields needed (for transformed/asset_integrated fields) | `asset.installation.ignition_input_number`, `static.tank_capacity_liters`, `geofence.id`, `driver.id` | Documents which external service fields are required. Can reference multiple services: Asset Service (properties, installation), Accessory Service, Geofence Service, Driver Service, etc. Required for `transformed` and `asset_integrated` mappings. Helps identify dependencies. |

### Group 4: Dependencies & Execution Order

| Column Name | Type | Required | Description | Example | Why It's Important |
| --- | --- | --- | --- | --- | --- |
| **Dependencies** | Relation | ❌ No | Other Fleeti fields this depends on | Links to other Fleeti Fields | Tracks field dependencies using **Field Names** (stable identifiers). Critical for calculated/transformed fields. Ensures correct evaluation order. Prevents circular dependencies. Backend resolves Field Names to Field Paths at runtime. |
| **Calculation Type** | Select | Conditional | How calculation is executed (for calculated mappings) | `formula` (parseable), `function_reference` (backend function) | Determines how calculation is implemented. Required for `calculated` mappings. Critical for configuration generation and backend implementation. Use `function_reference` for all function calls (default), `formula` only for simple math expressions. |

### Group 5: Error Handling & Defaults (Optional - System defaults available)

| Column Name | Type | Required | Description | Example | Why It's Important |
| --- | --- | --- | --- | --- | --- |
| **Default Value** | Text | ❌ No | Default value if no source available | `null`, `0`, `unknown` | Fallback value when mapping cannot be applied. System default: `null`. Important for data quality and error handling. |
| **Error Handling** | Text | ❌ No | What to do if mapping fails | `use_fallback`, `return_null`, `throw_error` | Defines error handling strategy. System defaults: `use_fallback` for prioritized, `return_null` for others. Important for data quality and system resilience. |
| **Unit Conversion** | Text | ❌ No | Unit conversion rule (if applicable) | `multiply by 0.00390625` | Converts provider unit to Fleeti standard unit. Can be auto-generated when Provider Unit ≠ Fleeti Unit. Important for fields with different units across providers. |

### Group 6: Backend Implementation (Conditional - Required based on Calculation Type)

| Column Name | Type | Required | Description | Example | Why It's Important |
| --- | --- | --- | --- | --- | --- |
| **Backend Function Name** | Text | Conditional | Function name in backend registry | `derive_cardinal_direction` | **Required** for `function_reference` type. Must exist in backend FUNCTION_REGISTRY. Links to backend implementation. Can be auto-extracted from Computation Approach. Enables function lookup in backend. |
| **Function Parameters** | Text | Conditional | Structured parameter mapping (JSON or structured text) | `{"heading": "location_heading"}` or `heading: location_heading` | **Required** for `function_reference` type. Maps function parameter names to field references. **Default (no prefix)**: Fleeti Field Names (stable identifiers), e.g., `location_heading`. **Provider prefix**: Use `provider:` prefix for direct provider field access, e.g., `provider:lat`. Format: `param_name: "fleeti_field_name"` or `param_name: "provider:field_path"` or JSON. Documents function signature and enables parameter resolution in YAML. Backend resolves: Fleeti fields via Field Name → Field Path lookup; Provider fields directly from provider packet. |

### Group 7: Metadata (Required)

| Column Name | Type | Required | Description | Example | Why It's Important |
| --- | --- | --- | --- | --- | --- |
| **Fleeti Unit** | Text | ❌ No | Fleeti field unit (from Fleeti Fields DB join) | `m/s`, `degrees`, `°C` | Used for unit conversion detection and YAML generation. Can be auto-generated from Fleeti Fields DB. |
| **Fleeti Data Type** | Text | ❌ No | Fleeti field data type (from Fleeti Fields DB join) | `number`, `string`, `boolean`, `datetime` | Used for validation in YAML generation. Can be auto-generated from Fleeti Fields DB. |
| **Version Added** | Text | ✅ Yes | Version when mapping was added | `1.0.0` | Version tracking. Enables change history and migration planning. |
| **Last Modified** | Date | ✅ Yes | Last modification date | `2025-01-15` | Tracks recent changes. Enables change notifications and "recently modified" views. |
| **Modified By** | Person | ✅ Yes | Who last modified | (Notion person) | Accountability and audit trail. Enables collaboration and questions. |
| **Change History** | Relation | ❌ No | Links to Change History DB (one-to-many) | (Relation) | Complete audit trail of changes. Important for compliance and troubleshooting. |
| **YAML Config Version** | Text | ❌ No | Last synced YAML version | `1.2.3` | Tracks sync status with generated configuration. Critical for configuration management workflow. Identifies mappings needing sync. |
| **YAML Path** | Text | ❌ No | Path in YAML config file | `mappings.motion.speed` | Documents where mapping appears in generated YAML. Useful for debugging and navigation. |
| **Notes** | Text | ❌ No | Additional notes | `CAN speed most accurate, use when available` | Captures important context, limitations, or special requirements. Helps developers understand mapping decisions. |
| **Customer Override** | Text | ❌ No | Customer-specific override (if applicable) | `Customer A: obd_speed > gps_speed` | Documents customer-specific mapping variations. Important for multi-tenant support. |

## Primary Key

**Mapping Name** serves as the primary key. Should be descriptive and unique. Format: `[Fleeti Field] from [Provider]` (e.g., `motion.speed from Navixy`).

## Mapping Type Requirements

### Direct Mapping

- **Required**: Mapping Name, Fleeti Field, Fleeti Field Path, Provider, Provider Fields (single), Provider Field Paths, Mapping Type = `direct`, Status, Configuration Level
- **Optional**: Unit Conversion (auto-generated if Provider Unit ≠ Fleeti Unit), Default Value, Error Handling, Fleeti Unit, Fleeti Data Type

### Prioritized Mapping

- **Required**: Mapping Name, Fleeti Field, Fleeti Field Path, Provider, Provider Fields (multiple), Provider Field Paths, Mapping Type = `prioritized`, Priority JSON, Status, Configuration Level
- **Optional**: Unit Conversion (auto-generated if Provider Unit ≠ Fleeti Unit), Default Value, Error Handling, Provider Unit, Fleeti Unit, Fleeti Data Type

### Calculated Mapping

- **Required**: Mapping Name, Fleeti Field, Fleeti Field Path, Provider, Mapping Type = `calculated`, Calculation Type, Computation Approach, Status, Configuration Level
- **If Calculation Type = `function_reference`**:
    - **Required**: Backend Function Name (must exist in FUNCTION_REGISTRY), Function Parameters (structured mapping)
    - **Optional**: Dependencies (should include all field names referenced in Function Parameters)
- **If Calculation Type = `formula`** (kept for future use):
    - **Required**: Computation Approach (parseable mathematical expression)
    - **Optional**: Dependencies (should include all field names referenced in formula)
- **Optional (all types)**: Error Handling, Fleeti Unit, Fleeti Data Type

### Transformed Mapping

- **Required**: Mapping Name, Fleeti Field, Fleeti Field Path, Provider, Mapping Type = `transformed`, Transformation Rule, Service Integration, Status, Configuration Level
- **Optional**: Dependencies, Default Value, Error Handling, Fleeti Unit, Fleeti Data Type

### I/O Mapped

- **Required**: Mapping Name, Fleeti Field, Fleeti Field Path, Provider, Mapping Type = `io_mapped`, I/O Mapping Config, Status, Configuration Level
- **Optional**: Default Value, Error Handling, Fleeti Unit, Fleeti Data Type

### Asset-Integrated Mapping

- **Required**: Mapping Name, Fleeti Field, Fleeti Field Path, Provider, Mapping Type = `asset_integrated`, Service Integration, Status, Configuration Level
- **Optional**: Dependencies, Default Value, Error Handling, Fleeti Unit, Fleeti Data Type

## Indexes & Performance

- **Index on Fleeti Field + Provider**: Fast lookups by target field and provider
- **Index on Mapping Type**: Efficient filtering by mapping type
- **Index on Status**: Quick filtering of active mappings
- **Index on YAML Config Version**: Fast identification of mappings needing sync

## Validation Rules

- **Fleeti Field**: Must reference active Fleeti field
- **Fleeti Field Path**: Must match Field Path from referenced Fleeti field
- **Provider Fields**: Must reference active Provider fields
- **Provider Field Paths**: Must match Field Path from referenced Provider fields
- **Mapping Type**: Must match requirements for selected type
- **Priority JSON**: Required if Mapping Type = `prioritized`, must be valid JSON
- **Computation Approach**: Required if Mapping Type = `calculated` (automatically populated via Notion rollup from Fleeti Fields Database relation)
- **Calculation Type**: Required if Mapping Type = `calculated`
- **Backend Function Name**: Required if Calculation Type = `function_reference` (must exist in backend FUNCTION_REGISTRY)
- **Function Parameters**: Required if Calculation Type = `function_reference`, must be structured mapping (JSON or structured text)
- **Transformation Rule**: Required if Mapping Type = `transformed`
- **I/O Mapping Config**: Required if Mapping Type = `io_mapped`, must be valid JSON
- **Service Integration**: Required if Mapping Type = `transformed` or `asset_integrated`
- **Dependencies**: Cannot create circular dependencies; all field names in Function Parameters must exist in Dependencies
- **Status**: Cannot be `active` if required fields are missing
- **Unit Conversion**: Can be auto-generated when Provider Unit ≠ Fleeti Unit

---

# YAML Generation Connection

## Column → YAML Field Mapping

This table shows how database columns map to YAML configuration fields:

| Database Column | YAML Field | Notes |
| --- | --- | --- |
| **Fleeti Field** (Name) | YAML key (e.g., `location_latitude:`) | **Used as top-level mapping key** (stable identifier) |
| **Fleeti Field Path** | YAML comment `# Field Path: ...` | For reference/documentation only |
| **Mapping Type** | `type: "direct"` / `"prioritized"` / etc. | Direct mapping |
| **Provider Field Paths** | `source: "..."` or `sources: [...]` | Single path or array for prioritized |
| **Priority JSON** | `sources: [{priority, field, path}]` | Parsed into sources array |
| **Calculation Type** | `calculation_type: "function_reference"` / `"formula"` | Determines YAML structure |
| **Backend Function Name** | `function: "function_name"` | Only for `function_reference` |
| **Function Parameters** | `parameters: {param: "field_name"}` | Structured mapping using **Field Names** (not Field Paths) |
| **Computation Approach** | `# Computation Approach: ...` | YAML comment (multi-line support). Populated via Notion rollup from Fleeti Fields Database relation |
| **Transformation Rule** | `transformation: "..."` | For `transformed` type |
| **I/O Mapping Config** | `default_source`, `installation_metadata` | Parsed JSON for `io_mapped` |
| **Service Integration** | `service_fields: [...]` | Array of external service field paths (can reference multiple services: asset, accessory, geofence, driver, etc.) |
| **Dependencies** | `dependencies: [...]` | Array of **Fleeti Field Names** (not Field Paths) |
| **Fleeti Unit** | `unit: "..."` | Used in YAML |
| **Fleeti Data Type** | `data_type: "..."` | Used in YAML |
| **Error Handling** | `error_handling: "..."` | Optional, defaults applied if missing |
| **Unit Conversion** | `unit_conversion: "..."` | Only if units differ |

**Important:** YAML uses **Field Names** (stable identifiers) as keys and in dependencies/parameters. Backend resolves Field Name → Field Path at runtime using a lookup table.

## Function Registry Workflow

1. **Database Entry Creation**
    - Create mapping entry with `Calculation Type = function_reference`
    - Link to Fleeti Field via relation (automatically populates `Computation Approach` via Notion rollup)
    - Populate `Backend Function Name` (must exist in backend FUNCTION_REGISTRY)
    - Populate `Function Parameters` as structured mapping: `{"param_name": "fleeti_field_name"}`
2. **YAML Generation**
    - Generate YAML with `function` and `parameters` fields
    - Add `Computation Approach` as YAML comments (multi-line support)
    - Include dependencies from `Dependencies` column
3. **Backend Validation**
    - Backend loads YAML configuration
    - Validates function exists in FUNCTION_REGISTRY
    - Validates parameter names match function signature
    - Validates Field Names exist in dependencies
4. **Backend Execution**
    - Backend resolves Field Names to Field Paths using lookup table
    - Backend maps function parameters to field values using resolved Field Paths
    - Calls function from registry with mapped parameters
    - Handles errors according to `error_handling` strategy

## Example: Function Reference Workflow

**Database Entry:**

- Fleeti Field: `location_cardinal_direction`
- Fleeti Field Path: `location.cardinal_direction`
- Calculation Type: `function_reference`
- Computation Approach: `Derived from location.heading`
- Backend Function Name: `derive_cardinal_direction`
- Function Parameters: `{"heading": "location_heading"}`
- Dependencies: `location_heading`

**Generated YAML:**

```yaml
location_cardinal_direction:
  type: "calculated"
  calculation_type: "function_reference"
  function: "derive_cardinal_direction"
  parameters:
    heading: "location_heading"  # Field Name, not Field Path
  dependencies:
    - "location_heading"  # Field Name, not Field Path
  data_type: "string"
  # Field Path: location.cardinal_direction (resolved at runtime)
  # Computation Approach: Derived from location.heading

```

**Backend Execution:**

```python
# Backend validates function exists
func = FUNCTION_REGISTRY["derive_cardinal_direction"]

# Backend resolves Field Name to Field Path
field_name = "location_heading"
field_path = resolve_field_path(field_name)  # Returns "location.heading"

# Backend maps parameters
heading_value = get_nested_value(telemetry_data, field_path)

# Backend calls function
result = func(heading=heading_value)  # Returns "NE" for heading=45°
```

---

# How to Use

This database is used to:

- Generate configuration files for the transformation pipeline
- Understand how provider data maps to Fleeti format
- Track mapping rule changes
- Support historical recalculation
- Enable pluggable backend function execution via function registry pattern

---

# Related Documentation

- **📥 Provider Fields Database**: Source provider fields
- **🎯 Fleeti Fields Database**: Target Fleeti fields

---

# Database

[Mapping Fields (db)](https://www.notion.so/2cc3e766c901806b9904e69fec02b085?pvs=21)