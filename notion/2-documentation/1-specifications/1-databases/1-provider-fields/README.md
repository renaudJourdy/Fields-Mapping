**Status:** 🎯 Done

**Comment**: Miss relation with Fleeti Fields and Mapping Rules databases

# Purpose

The Provider Fields Database catalogs all provider-specific telemetry fields from all telemetry providers (Navixy, Teltonika, OEM manufacturers, etc.).

---

# What This Database Contains

- **Provider field names**: Exact field names as received from providers
- **Field types**: Data types (string, number, boolean, etc.)
- **Field descriptions**: What each field represents
- **Observed values**: Example values and value ranges
- **Provider metadata**: Provider-specific field information
- **Field availability**: Which providers expose which fields

---

# Database Structure

## Column Definitions

| Column Name | Type | Required | Description | Example | Why It's Important |
| --- | --- | --- | --- | --- | --- |
| **Field Name** | Title | ✅ Yes | Provider field name (primary identifier) | `can_speed` | Primary key - uniquely identifies each provider field. Used for lookups and references. |
| **Provider** | Select | ✅ Yes | Provider name | `navixy`, `oem-trackunit`, `oem-volvo`, `future-provider` | Essential for multi-provider support. Enables filtering and grouping by provider. Required for mapping rules. |
| **Field Path** | Text | ✅ Yes | Full path in provider packet | `params.can_speed` | Exact location in provider data structure. Critical for parsing and extraction. Must match actual provider packet structure. |
| **Data Type** | Select | ✅ Yes | Provider data type | `number`, `string`, `boolean`, `object`, `array` | Ensures type safety during transformation. Required for validation and unit conversion. |
| **Unit** | Text | ❌ No | Provider unit (if applicable) | `km/h`, `m/s`, `mph` | Enables unit conversion to Fleeti standard units. Important for fields like speed, temperature, fuel level. |
| **Example Value** | Text | ❌ No | Example value from provider | `65.5` | Helps developers understand expected values. Useful for testing and validation. Documents observed value ranges. |
| **Description** | Text | ✅ Yes | What provider field represents | `CAN bus speed reading` | Critical for understanding field purpose. Helps with mapping decisions and troubleshooting. |
| **Availability** | Select | ✅ Yes | Field availability | `always`, `conditional`, `rare`, `deprecated`,`unknown` | Indicates reliability of field. Important for priority rules and fallback strategies. |
| **Fleeti Fields** | Relation | ❌ No | Links to Fleeti Fields DB (many-to-many via Field Mappings) | (Relation) | Shows which Fleeti fields use this provider field. Useful for impact analysis when provider field changes. |
| **Field Mappings** | Relation | ❌ No | Links to Field Mappings DB (one-to-many) | (Relation) | Direct link to mapping rules. Enables quick access to how this field is used in transformations. |
| **Status** | Select | ✅ Yes | Field status | `active`, `deprecated`, `unavailable`,`pending` | Tracks field lifecycle. Deprecated fields should not be used in new mappings. Critical for data quality. |
| **Version Added** | Text | ✅ Yes | Version when field was documented | `1.0.0` | Tracks when field was discovered/added. Useful for versioning and change tracking. |
| **Last Modified** | Date | ✅ Yes | Last modification date | `2025-01-15` | Tracks recent changes. Enables "recently modified" views and change notifications. |
| **Notes** | Text | ❌ No | Additional notes | `Requires CAN bus connection` | Captures important context, limitations, or special requirements. Helps developers understand field constraints. |

## Primary Key

**Field Name** serves as the primary key. Combined with **Provider**, it uniquely identifies each provider field.

## Validation Rules

- **Field Name**: Must be unique per provider
- **Field Path**: Must match actual provider packet structure
- **Data Type**: Must be one of the allowed types
- **Status**: Cannot be `active` if field is deprecated in provider

---

# How to Use

This database is used to:

- Map provider fields to Fleeti fields
- Understand provider field structure
- Identify available fields for mapping
- Track provider field changes

---

# Related Documentation

- **🔀 Mapping Fields Database**: How provider fields map to Fleeti fields
- **Provider Catalogs**: Detailed provider field catalogs

---

# Raw Packet Structure

[Raw Packet Structure](https://www.notion.so/Raw-Packet-Structure-2c73e766c90180a4926df82ebdd8c3a0?pvs=21)

---

# Provider Field Database

[Provider Field (db)](https://www.notion.so/2c73e766c901806d9bacd1bf72f6014d?pvs=21)