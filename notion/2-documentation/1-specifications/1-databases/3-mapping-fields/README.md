**Status:** 🎯 Structure Created - Content To Be Developed

# Purpose

The Mapping Fields Database contains field transformation rules and priority chains that link provider fields to Fleeti fields.

# What This Database Contains

- **Direct mappings**: 1:1 provider field → Fleeti field mappings
- **Priority chains**: Multiple provider fields → one Fleeti field (with priority order)
- **Calculation rules**: Formulas and logic for calculated fields
- **I/O mappings**: Raw I/O fields → semantic fields (with installation metadata)
- **Transformation logic**: Static data transformations (e.g., fuel level % → liters)

# Database Structure

## Column Definitions

| Column Name | Type | Required | Description | Example | Why It's Important |
|-------------|------|----------|-------------|---------|-------------------|
| **Mapping Name** | Title | ✅ Yes | Descriptive mapping name (primary identifier) | `motion.speed from Navixy` | Primary key - human-readable identifier. Helps identify mapping purpose at a glance. |
| **Fleeti Field** | Relation | ✅ Yes | Links to Fleeti Fields DB | `motion.speed` | Target field for mapping. Required for all mappings. Critical for configuration generation. |
| **Provider** | Select | ✅ Yes | Provider name | `navixy`, `oem-trackunit`, `oem-volvo` | Identifies which provider this mapping applies to. Required for multi-provider support. |
| **Provider Fields** | Relation | ✅ Yes | Links to Provider Fields DB (can be multiple) | `can_speed`, `obd_speed`, `speed` | Source fields for mapping. Can be single (direct) or multiple (prioritized). Critical for transformation. |
| **Mapping Type** | Select | ✅ Yes | Type of mapping | `direct`, `prioritized`, `calculated`, `aggregated`, `transformed`, `io_mapped`, `asset_integrated` | Determines transformation approach. Critical for configuration generation. Each type has different requirements. |
| **Priority Order** | Text | ❌ No | Human-readable priority order (for prioritized mappings) | `can_speed (1) > obd_speed (2) > speed (3)` | Human-readable format. Useful for documentation but Priority JSON is used for generation. |
| **Priority JSON** | Text | ❌ No | Structured priority data in JSON (for prioritized mappings) | `[{"priority": 1, "field": "can_speed"}, {"priority": 2, "field": "obd_speed"}]` | Machine-readable priority order. Used directly in YAML config generation. Required for prioritized mappings. |
| **Calculation Type** | Select | ❌ No | How calculation is executed (for calculated mappings) | `formula` (parseable), `function_reference` (backend function), `code_based` (complex logic) | Determines how calculation is implemented. Critical for configuration generation and backend implementation. |
| **Calculation Formula** | Text | ❌ No | Formula/logic (for calculated/transformed fields) | `derive_from_heading(location.heading)` or `(fuel.level_percent / 100) * static.tank_capacity_liters` | Documents calculation logic. Used in YAML config for function references and parseable formulas. Critical for calculated fields. |
| **Backend Function Name** | Text | ❌ No | Function name in backend registry (if function_reference) | `derive_from_heading` | Links to backend implementation. Required for function_reference type. Enables function lookup in backend. |
| **Function Parameters** | Text | ❌ No | Parameters passed to backend function | `location.heading` | Documents function signature. Important for function_reference mappings. Helps with implementation. |
| **Implementation Location** | Text | ❌ No | File path or documentation link to backend code | `telemetry-transformation-service/src/functions/cardinal.py:derive_cardinal_direction` | Points to actual code implementation. Critical for code_based and function_reference types. Enables code navigation. |
| **Transformation Rule** | Text | ❌ No | Transformation logic (for transformed fields) | `(fuel.level_percent / 100) * static.tank_capacity_liters` | Documents transformation combining telemetry with static data. Required for transformed mappings. Used in config generation. |
| **Dependencies** | Relation | ❌ No | Other Fleeti fields this depends on | Links to other Fleeti Fields | Tracks field dependencies. Critical for calculated/transformed fields. Ensures correct evaluation order. Prevents circular dependencies. |
| **Unit Conversion** | Text | ❌ No | Unit conversion rule (if applicable) | `multiply by 0.00390625` | Converts provider unit to Fleeti standard unit. Important for fields with different units across providers. |
| **Default Value** | Text | ❌ No | Default value if no source available | `null`, `0`, `unknown` | Fallback value when mapping cannot be applied. Important for data quality and error handling. |
| **Error Handling** | Text | ❌ No | What to do if mapping fails | `use_fallback`, `return_null`, `throw_error` | Defines error handling strategy. Important for data quality and system resilience. |
| **I/O Mapping Config** | Text | ❌ No | I/O mapping configuration in JSON (for io_mapped fields) | `{"default_source": "io.inputs.individual.input_1", "installation_metadata": "asset.installation.ignition_input_number"}` | Configuration for I/O to semantic field mapping. Required for io_mapped type. Links raw I/O to semantic meaning via installation metadata. |
| **Asset Service Integration** | Text | ❌ No | Asset Service fields needed (for transformed/asset_integrated fields) | `asset.installation.ignition_input_number`, `static.tank_capacity_liters` | Documents which asset metadata fields are required. Critical for transformed and asset_integrated mappings. Helps identify dependencies. |
| **Configuration Level** | Select | ✅ Yes | Where this mapping applies | `default`, `customer`, `asset_group`, `asset` | Defines mapping hierarchy. Lower levels override higher levels. Critical for hierarchical configuration support. |
| **Customer Override** | Text | ❌ No | Customer-specific override (if applicable) | `Customer A: obd_speed > gps_speed` | Documents customer-specific mapping variations. Important for multi-tenant support. |
| **Status** | Select | ✅ Yes | Mapping status | `active`, `deprecated`, `under_review`, `planned` | Tracks mapping lifecycle. Deprecated mappings should not be used. Critical for data quality and configuration generation. |
| **Version Added** | Text | ✅ Yes | Version when mapping was added | `1.0.0` | Version tracking. Enables change history and migration planning. |
| **Last Modified** | Date | ✅ Yes | Last modification date | `2025-01-15` | Tracks recent changes. Enables change notifications and "recently modified" views. |
| **Modified By** | Person | ✅ Yes | Who last modified | (Notion person) | Accountability and audit trail. Enables collaboration and questions. |
| **Change History** | Relation | ❌ No | Links to Change History DB (one-to-many) | (Relation) | Complete audit trail of changes. Important for compliance and troubleshooting. |
| **YAML Config Version** | Text | ❌ No | Last synced YAML version | `1.2.3` | Tracks sync status with generated configuration. Critical for configuration management workflow. Identifies mappings needing sync. |
| **YAML Path** | Text | ❌ No | Path in YAML config file | `mappings.motion.speed` | Documents where mapping appears in generated YAML. Useful for debugging and navigation. |
| **Notes** | Text | ❌ No | Additional notes | `CAN speed most accurate, use when available` | Captures important context, limitations, or special requirements. Helps developers understand mapping decisions. |

## Primary Key

**Mapping Name** serves as the primary key. Should be descriptive and unique. Format: `[Fleeti Field] from [Provider]` (e.g., `motion.speed from Navixy`).

## Mapping Type Requirements

### Direct Mapping
- **Required**: Fleeti Field, Provider, Provider Fields (single), Mapping Type = `direct`
- **Optional**: Unit Conversion, Default Value, Error Handling

### Prioritized Mapping
- **Required**: Fleeti Field, Provider, Provider Fields (multiple), Mapping Type = `prioritized`, Priority JSON
- **Optional**: Priority Order (human-readable), Unit Conversion, Default Value, Error Handling

### Calculated Mapping
- **Required**: Fleeti Field, Provider, Mapping Type = `calculated`, Calculation Type, Calculation Formula
- **If function_reference**: Backend Function Name, Function Parameters, Implementation Location
- **If code_based**: Implementation Location
- **Optional**: Dependencies, Error Handling

### Transformed Mapping
- **Required**: Fleeti Field, Provider, Mapping Type = `transformed`, Transformation Rule, Asset Service Integration
- **Optional**: Dependencies, Default Value, Error Handling

### I/O Mapped
- **Required**: Fleeti Field, Provider, Mapping Type = `io_mapped`, I/O Mapping Config
- **Optional**: Default Value, Error Handling

### Asset-Integrated Mapping
- **Required**: Fleeti Field, Provider, Mapping Type = `asset_integrated`, Asset Service Integration
- **Optional**: Dependencies, Default Value, Error Handling

## Indexes & Performance

- **Index on Fleeti Field + Provider**: Fast lookups by target field and provider
- **Index on Mapping Type**: Efficient filtering by mapping type
- **Index on Status**: Quick filtering of active mappings
- **Index on YAML Config Version**: Fast identification of mappings needing sync

## Validation Rules

- **Fleeti Field**: Must reference active Fleeti field
- **Provider Fields**: Must reference active Provider fields
- **Mapping Type**: Must match requirements for selected type
- **Priority JSON**: Required if Mapping Type = `prioritized`, must be valid JSON
- **Calculation Formula**: Required if Mapping Type = `calculated`
- **Backend Function Name**: Required if Calculation Type = `function_reference`
- **Implementation Location**: Required if Calculation Type = `code_based` or `function_reference`
- **Transformation Rule**: Required if Mapping Type = `transformed`
- **I/O Mapping Config**: Required if Mapping Type = `io_mapped`, must be valid JSON
- **Dependencies**: Cannot create circular dependencies
- **Status**: Cannot be `active` if required fields are missing

# How to Use

This database is used to:
- Generate configuration files for the transformation pipeline
- Understand how provider data maps to Fleeti format
- Track mapping rule changes
- Support historical recalculation

# Related Documentation

- **[📥 Provider Fields Database](../provider-fields/README.md)**: Source provider fields
- **[🎯 Fleeti Fields Database](../fleeti-fields/README.md)**: Target Fleeti fields
- **[Mapping Rules](../../2-field-mappings/mapping-rules.md)**: Mapping rules documentation

---

**Last Updated:** 2025-01-XX  
**Status:** 🎯 Structure Created - Content To Be Developed

