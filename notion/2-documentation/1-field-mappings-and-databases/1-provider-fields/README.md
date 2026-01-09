**Status:** 🎯 Done

# Purpose

The Provider Fields Database catalogs all provider-specific telemetry fields from all telemetry providers (Navixy, Teltonika, OEM manufacturers, etc.). This database serves as the source catalog for mapping provider fields to Fleeti canonical fields.

**Key Contents:** Provider field names, types, paths, availability, units, descriptions, example values, and relations to mapping rules.

---

# Database Structure

## Column Definitions

| Column Name | Type | Required | Description | Example | Why It's Important |
| --- | --- | --- | --- | --- | --- |
| **Name** | Title | ✅ Yes | Provider field name (primary identifier) | `can_speed` | Primary key - uniquely identifies each provider field. Combined with Provider forms composite key. |
| **Provider** | Select | ✅ Yes | Provider name | `navixy`, `oem-trackunit` | Essential for multi-provider support. Enables filtering and grouping by provider. |
| **Field Path** | Text | ✅ Yes | Full path in provider packet | `params.can_speed` | Exact location in provider data structure. Critical for parsing and extraction. |
| **Data Type** | Select | ✅ Yes | Provider data type | `number`, `string`, `boolean` | Ensures type safety during transformation. Required for validation and unit conversion. |
| **Unit** | Text | ❌ No | Provider unit (if applicable) | `km/h`, `°C`, `liters` | Enables unit conversion to Fleeti standard units. |
| **Description** | Text | ✅ Yes | What provider field represents | `CAN bus speed reading` | Critical for understanding field purpose and mapping decisions. |
| **Availability** | Select | ✅ Yes | Field availability | `always`, `conditional`, `rare` | Indicates reliability. Important for priority rules and fallback strategies. |
| **Example Value** | Text | ❌ No | Example value from provider | `65.5` | Helps developers understand expected values and value ranges. |
| **Status** | Select | ✅ Yes | Field status | `active`, `deprecated`, `pending` | Tracks field lifecycle. Deprecated fields should not be used in new mappings. |
| **Version Added** | Text | ✅ Yes | Version when field was documented | `1.0.0` | Tracks when field was discovered/added. Useful for versioning. |
| **💽 Fleeti Fields (db)** | Relation | ❌ No | Links to Fleeti Fields DB | (Relation) | Shows which Fleeti fields use this provider field. Useful for impact analysis. |
| **💽 Mapping Fields (db)** | Relation | ❌ No | Links to Mapping Fields DB | (Relation) | Direct link to mapping rules. Enables quick access to transformation usage. |
| **Notes** | Text | ❌ No | Additional context | `Requires CAN bus connection` | Captures important context, limitations, or special requirements. |
| **Last Modified** | Date | ✅ Yes | Last modification date | `2025-01-15` | Tracks recent changes. Enables "recently modified" views. |

## Primary Key

**Name** combined with **Provider** uniquely identifies each provider field.

## Validation Rules

- **Name**: Must be unique per provider
- **Field Path**: Must match actual provider packet structure
- **Data Type**: Must be one of the allowed types
- **Status**: Cannot be `active` if field is deprecated in provider

---

# How to Use

This database is used to:

- Map provider fields to Fleeti fields (via Mapping Fields Database)
- Understand provider field structure and availability
- Identify available fields for mapping
- Track provider field changes and lifecycle

---

# Raw Packet Structure

[Raw Packet Structure](https://www.notion.so/Raw-Packet-Structure-2c73e766c90180a4926df82ebdd8c3a0?pvs=21)

---

# Provider Field Database

[Provider Field (db)](https://www.notion.so/2c73e766c901806d9bacd1bf72f6014d?pvs=21)