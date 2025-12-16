**Status:** 🎯 Structure Created - Content To Be Developed

# Purpose

The Fleeti Fields Database is the complete catalog of all **Fleeti canonical telemetry fields** organized by section. This database serves as the **single source of truth** for Fleeti telemetry field definitions.

**Important Distinction:**
- **Provider Fields** (300+ fields): Provider-specific telemetry fields from Navixy, Teltonika, OEM, etc. These are documented in the [Provider Fields Database](../1-provider-fields/README.md).
- **Fleeti Fields**: Canonical semantic telemetry fields that represent the unified Fleeti telemetry model. Multiple provider fields may map to a single Fleeti field (e.g., `can_speed`, `obd_speed`, `speed` all map to `motion.speed`).

The complete list of Fleeti fields is documented in the [Schema Specification](../../../docs/legacy/fleeti-telemetry-schema-specification.md).

# What This Database Contains

- **Fleeti field names**: Canonical field names in Fleeti format
- **Field sections**: Organization (Asset Metadata, Location, Motion, Power, Fuel, etc.)
- **Field types**: Data types and structures
- **Field priorities**: Implementation priorities (P0-P3, T, BL, ?)
- **Transformation requirements**: How fields are computed (direct, prioritized, calculated, transformed)
- **Visibility**: Customer-facing vs internal fields

# Database Structure

## Column Definitions

| Column Name | Type | Required | Description | Example | Why It's Important |
|-------------|------|----------|-------------|---------|-------------------|
| **Field Name** | Title | ✅ Yes | Stable field identifier - primary key | `fuel.consumption.cumulative` | Primary key - stable identifier that uniquely identifies each Fleeti field. This is the canonical reference used throughout the system. **Does not change** even if the field is moved to a different path in the telemetry object. Used for references, relations, and stable identification. |
| **Field Path** | Text | ✅ Yes | Full hierarchical path in telemetry object (section → sub-objects → field) | `fuel.consumption.cumulative` | Current technical path in the telemetry JSON structure. Follows the structure: section (e.g., `fuel`, `location`) → sub-objects (e.g., `consumption`, `precision`) → field (e.g., `cumulative`, `hdop`). **Can change** if field is reorganized (e.g., moved from `fuel.consumption.cumulative` to `fuel.total.consumption`). Used in YAML config generation and API responses. Critical for consistency. |
| **Category** | Select | ✅ Yes | Section/category | `fuel`, `location`, `motion`, `status`, `power`, `diagnostics`, `sensors`, `driving_behavior`, `device`, `connectivity`, `io`, `driver`, `other`, `metadata` | Organizes fields by domain. Enables filtering and grouping. Critical for schema organization. |
| **Priority** | Select | ✅ Yes | Implementation priority | `P0`, `P1`, `P2`, `P3`, `T`, `BL`, `?`, `ignored`, `later` | Guides implementation order. P0 fields are critical for MVP. Essential for prioritization and planning. |
| **Field Type** | Select | ✅ Yes | Mapping type | `direct`, `prioritized`, `calculated`, `aggregated`, `transformed`, `io_mapped`, `asset_integrated` | Determines transformation approach. Critical for configuration generation. Affects how mapping rules are structured. |
| **Structure Type** | Select | ✅ Yes | Data structure | `simple_value`, `value_unit_object`, `nested_object`, `array` | Defines field structure in telemetry object. Important for API contracts and frontend consumption. |
| **JSON Structure** | Text | ✅ Yes | JSON representation example | `{ "value": 65.5, "unit": "km/h" }` | Exact JSON structure of the field in the telemetry object. Shows how value, unit, and timestamps are combined. Critical for API documentation and frontend integration. Examples: `65.5` (simple_value), `{ "value": 65.5, "unit": "km/h" }` (value_unit_object), `{ "value": true, "last_changed_at": 1704067200000 }` (nested_object with timestamp), `[{ "value": 85, "unit": "%" }]` (array of value_unit_objects). |
| **Data Type** | Select | ✅ Yes | JSON data type | `number`, `string`, `boolean`, `object`, `array`, `null` | Type safety and validation. Required for schema validation and API documentation. |
| **Unit** | Text | ❌ No | Standard unit (if applicable) | `km/h`, `°C`, `l`, `%` | Fleeti standard unit. Important for consistency across providers. Used in API documentation. |
| **Description** | Text | ✅ Yes | What the field represents | `Current fuel level in liters` | Critical for understanding field purpose. Used in API docs and developer reference. |
| **WebSocket Contracts** | Multi-select | ❌ No | WebSocket streams that include this field | `live.map.markers`, `live.assets.list`, `live.asset.details` | Tracks which WebSocket contracts expose this field. Enables contract completeness checks and field visibility analysis. Options: `live.map.markers` (Live Map Markers), `live.assets.list` (Asset List), `live.asset.details` (Asset Details). |
| **REST API Endpoints** | Multi-select | ❌ No | REST API endpoints that expose this field | `api.telemetry.hot`, `api.telemetry.warm`, `api.telemetry.historical` | Tracks which REST API endpoints expose this field. Helps determine field availability in different storage tiers and API versions. Options: `api.telemetry.hot` (Hot Storage API - core fields), `api.telemetry.warm` (Warm Storage API - complete fields), `api.telemetry.historical` (Historical API - time-range queries). |
| **Provider Fields** | Relation | ❌ No | Links to Provider Fields DB (many-to-many via Field Mappings) | (Relation) | Shows which provider fields map to this Fleeti field. Useful for impact analysis. |
| **Field Mappings** | Relation | ❌ No | Links to Field Mappings DB (one-to-many) | (Relation) | Direct access to mapping rules. Critical for configuration generation. |
| **Dependencies** | Relation | ❌ No | Other Fleeti fields this depends on | Links to other Fleeti Fields | Tracks field dependencies. Critical for calculated/transformed fields. Ensures correct evaluation order. Prevents circular dependencies. |
| **Computation Approach** | Text | ❌ No | High-level description of how field is computed (generic, not provider-specific) | `Derived from heading using cardinal direction calculation`, `Prioritized from multiple speed sources (CAN > OBD > GPS)`, `Combined with static asset metadata (tank capacity)` | Generic description of computation approach. **Note:** Provider-specific formulas, priority rules, and transformation logic are documented in the [Mapping Fields Database](../3-mapping-fields/README.md), not here. This field provides high-level understanding only. |
| **Status** | Select | ✅ Yes | Field status | `active`, `deprecated`, `planned`, `under_review` | Tracks field lifecycle. Deprecated fields should not be used in new code. Critical for data quality. |
| **Version Added** | Text | ✅ Yes | Version when field was added | `1.0.0` | Version tracking. Enables change history and migration planning. |
| **Change History** | Relation | ❌ No | Links to Change History DB (one-to-many) | (Relation) | Complete audit trail of changes. Important for compliance and troubleshooting. |
| **YAML Config Version** | Text | ❌ No | Last synced YAML version | `1.2.3` | Tracks sync status with generated configuration. Critical for configuration management workflow. |
| **Notes** | Text | ❌ No | Additional notes or context | `Requires Asset Service integration` | Captures important context, limitations, or special requirements. Helps developers understand constraints. |

## Primary Key

**Field Name** serves as the primary key. Must be unique and follow dot-separated naming convention (e.g., `fuel.consumption.cumulative`, `location.latitude`). 

**Important:** Field Name is a **stable identifier** that does not change even if the field is reorganized in the telemetry structure. Field Path can be updated independently to reflect the current technical location in the JSON structure.


## Validation Rules

- **Field Name**: Must be unique and follow dot-separated format (e.g., `fuel.consumption.cumulative`)
- **Field Path**: Must follow format `category.field` (lowercase, dot-separated). Can differ from Field Name if field is reorganized, but typically matches initially.
- **Priority**: Must be one of: P0, P1, P2, P3, T, BL, ?, ignored, later
- **Field Type**: Must match mapping type in Field Mappings database
- **Dependencies**: Cannot create circular dependencies
- **Status**: Cannot be `active` if no mappings exist (warning, not error)

## Important: Provider-Specific Logic

**Calculation formulas, transformation rules, and priority chains are provider-specific** and are documented in the [🔀 Mapping Fields Database](../3-mapping-fields/README.md), not in this database.

**Why?**
- A single Fleeti field (e.g., `motion.speed`) can have multiple provider fields mapping to it (`can_speed`, `obd_speed`, `speed`)
- Each provider may require different formulas, unit conversions, or priority rules
- The Mapping Fields Database contains the actual transformation logic per provider

**This Database Contains:**
- ✅ Semantic field definitions (what the field represents)
- ✅ Field structure and data types
- ✅ High-level computation approach (generic description)
- ✅ Dependencies on other Fleeti fields
- ✅ API/WebSocket exposure

**Mapping Fields Database Contains:**
- ✅ Provider-specific calculation formulas
- ✅ Priority chains (which provider field to use first, second, etc.)
- ✅ Transformation rules combining telemetry with static data
- ✅ Unit conversions per provider
- ✅ Actual implementation logic for configuration generation

## Calculated Fields (Formulas)

**Formula 1: Mapping Status**
```
if(empty(prop("Field Mappings")), "⚠️ Unmapped", "✅ Mapped")
```
Purpose: Visual indicator of mapping completeness. Helps identify fields needing mapping.

**Formula 2: Has Dependencies**
```
if(empty(prop("Dependencies")), "No", "Yes")
```
Purpose: Quick indicator if field has dependencies. Important for calculated/transformed fields.

**Formula 3: Days Since Last Modified**
```
dateBetween(prop("Last Modified"), now(), "days")
```
Purpose: Tracks how recently field was updated. Useful for change tracking.

# How to Use

This database is used to:
- Define Fleeti telemetry structure
- Prioritize field implementation
- Generate configuration files
- Reference field definitions in specifications

# Related Documentation

- **[Schema Specification](../../../docs/legacy/fleeti-telemetry-schema-specification.md)**: Big picture reference (not definitive)
- **[🔀 Mapping Fields Database](../mapping-fields/README.md)**: How provider fields map to Fleeti fields
- **[Field Mappings](../../2-field-mappings/fleeti-fields-catalog.md)**: Field catalog documentation

---

**Last Updated:** 2025-01-XX  
**Status:** 🎯 Structure Created - Content To Be Developed

