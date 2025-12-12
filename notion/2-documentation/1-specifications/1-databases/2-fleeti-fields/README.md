**Status:** 🎯 Structure Created - Content To Be Developed

# Purpose

The Fleeti Fields Database is the complete catalog of all Fleeti telemetry fields (~343+ fields) organized by section. This database serves as the **single source of truth** for Fleeti telemetry field definitions.

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
| **Field Name** | Title | ✅ Yes | Semantic field name (path) - primary identifier | `fuel.level` | Primary key - uniquely identifies each Fleeti field. Used throughout system for references. |
| **Field Path** | Text | ✅ Yes | Full path in telemetry object | `fuel.level` | Must match Field Name. Used in YAML config generation and API responses. Critical for consistency. |
| **Category** | Select | ✅ Yes | Section/category | `fuel`, `location`, `motion`, `status`, `power`, `diagnostics`, `sensors`, `driving_behavior`, `device`, `connectivity`, `io`, `driver`, `other`, `metadata` | Organizes fields by domain. Enables filtering and grouping. Critical for schema organization. |
| **Priority** | Select | ✅ Yes | Implementation priority | `P0`, `P1`, `P2`, `P3`, `T`, `BL`, `?`, `ignored`, `later` | Guides implementation order. P0 fields are critical for MVP. Essential for prioritization and planning. |
| **Field Type** | Select | ✅ Yes | Mapping type | `direct`, `prioritized`, `calculated`, `aggregated`, `transformed`, `io_mapped`, `asset_integrated` | Determines transformation approach. Critical for configuration generation. Affects how mapping rules are structured. |
| **Structure Type** | Select | ✅ Yes | Data structure | `simple_value`, `value_unit_object`, `nested_object`, `array` | Defines field structure in telemetry object. Important for API contracts and frontend consumption. |
| **Data Type** | Select | ✅ Yes | JSON data type | `number`, `string`, `boolean`, `object`, `array`, `null` | Type safety and validation. Required for schema validation and API documentation. |
| **Unit** | Text | ❌ No | Standard unit (if applicable) | `km/h`, `°C`, `l`, `%` | Fleeti standard unit. Important for consistency across providers. Used in API documentation. |
| **Description** | Text | ✅ Yes | What the field represents | `Current fuel level in liters` | Critical for understanding field purpose. Used in API docs and developer reference. |
| **Use Cases** | Text | ❌ No | Where/how field is used | `Asset detail view, fuel consumption reports` | Documents field usage. Helps prioritize and understand business value. |
| **Provider Fields** | Relation | ❌ No | Links to Provider Fields DB (many-to-many via Field Mappings) | (Relation) | Shows which provider fields map to this Fleeti field. Useful for impact analysis. |
| **Field Mappings** | Relation | ❌ No | Links to Field Mappings DB (one-to-many) | (Relation) | Direct access to mapping rules. Critical for configuration generation. |
| **Dependencies** | Relation | ❌ No | Other Fleeti fields this depends on | Links to other Fleeti Fields | Tracks field dependencies. Critical for calculated/transformed fields. Ensures correct evaluation order. |
| **Calculation Formula** | Text | ❌ No | Formula/logic (if calculated) | `derive_from_heading(location.heading)` | Documents calculation logic. Used for function reference mappings. Important for maintainability. |
| **Transformation Rule** | Text | ❌ No | Transformation logic (if transformed) | `(fuel.level_percent / 100) * static.tank_capacity_liters` | Documents transformation logic. Critical for transformed fields. Used in configuration generation. |
| **Status** | Select | ✅ Yes | Field status | `active`, `deprecated`, `planned`, `under_review` | Tracks field lifecycle. Deprecated fields should not be used in new code. Critical for data quality. |
| **Version Added** | Text | ✅ Yes | Version when field was added | `1.0.0` | Version tracking. Enables change history and migration planning. |
| **Last Modified** | Date | ✅ Yes | Last modification date | `2025-01-15` | Tracks recent changes. Enables change notifications and "recently modified" views. |
| **Modified By** | Person | ✅ Yes | Who last modified | (Notion person) | Accountability and audit trail. Enables collaboration and questions. |
| **Change History** | Relation | ❌ No | Links to Change History DB (one-to-many) | (Relation) | Complete audit trail of changes. Important for compliance and troubleshooting. |
| **YAML Config Version** | Text | ❌ No | Last synced YAML version | `1.2.3` | Tracks sync status with generated configuration. Critical for configuration management workflow. |
| **Notes** | Text | ❌ No | Additional notes or context | `Requires Asset Service integration` | Captures important context, limitations, or special requirements. Helps developers understand constraints. |

## Primary Key

**Field Name** serves as the primary key. Must be unique and follow dot-separated naming convention (e.g., `fuel.level`, `location.latitude`).

## Indexes & Performance

- **Index on Field Path**: Fast lookups by field path (must be unique)
- **Index on Category + Priority**: Efficient filtering and sorting
- **Index on Status**: Quick filtering of active fields
- **Index on Field Type**: Fast grouping by transformation type

## Validation Rules

- **Field Name**: Must match Field Path exactly
- **Field Path**: Must follow format `category.field` (lowercase, dot-separated)
- **Priority**: Must be one of: P0, P1, P2, P3, T, BL, ?, ignored, later
- **Field Type**: Must match mapping type in Field Mappings database
- **Dependencies**: Cannot create circular dependencies
- **Status**: Cannot be `active` if no mappings exist (warning, not error)

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

