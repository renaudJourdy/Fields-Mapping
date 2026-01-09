**Status:** 🎯 Done

# Purpose

The Fleeti Fields Database is the complete catalog of all **Fleeti canonical telemetry fields** organized by category. This database serves as the **single source of truth** for Fleeti telemetry field definitions.

**Important Distinction:**

- **Provider Fields**: Provider-specific telemetry fields from Navixy, Teltonika, OEM, etc. Documented in the [Provider Fields Database](https://www.notion.so/Provider-Fields-Database-2c73e766c90180e79450f8d6500a0613?pvs=21).
- **Fleeti Fields**: Canonical semantic telemetry fields representing the unified Fleeti telemetry model. Multiple provider fields may map to a single Fleeti field (e.g., `can_speed`, `obd_speed`, `speed` all map to `motion.speed`).

**Key Contents:** Field names (stable identifiers), field paths, categories, computation approaches (pseudo-code), computation structure JSON (machine-readable for YAML generation), WebSocket/REST API exposure, dependencies, and relations to mapping rules.

**Note:** Computation Approach contains pseudo-code (not formulas). Full detailed pseudo-code for complex functions is in Notion database raw content (not CSV). Very complex functions have dedicated `.pseudo.md` files.

---

# Database Structure

## Column Definitions

Columns are listed in the same order as they appear in the CSV export:

| Column Name | Type | Required | Description | Example | Why It's Important |
| --- | --- | --- | --- | --- | --- |
| **Name** | Title | ✅ Yes | Stable field identifier (primary key) | `location_latitude` | Stable identifier that doesn't change even if field is reorganized. |
| **Category** | Select | ✅ Yes | Field category/section | `location`, `motion`, `power`, `fuel`, `status` | Organizes fields by domain. |
| **Complex Cumputation** | Select | ❌ No | Indicates if computation is complex | `Yes`, `No` | Flags complex computation logic. Note: Column name typo ("Cumputation"). |
| **Computation Approach** | Text | ❌ No | Pseudo-code description (generic, not provider-specific) | `Derived from heading using cardinal direction calculation` | Human-readable pseudo-code. Full details in Notion raw content (not CSV). Provider-specific rules in Mapping Fields Database. |
| **Computation Structure JSON** | Text | ❌ No | Machine-readable JSON for YAML generation | `{"type": "prioritized", "sources": [...]}` | Used by `generate_yaml_from_csv.py` to generate YAML structure. Contains type, sources, priorities, functions, parameters. |
| **Data Type** | Select | ✅ Yes | JSON data type | `number`, `string`, `boolean`, `object`, `array` | Type safety and validation. |
| **Dependencies** | Relation | ❌ No | Other Fleeti fields this depends on | (Relation) | Tracks dependencies for correct evaluation order. |
| **Description** | Text | ✅ Yes | What the field represents | `Current fuel level in liters` | Field purpose. Used in API docs. |
| **Field Path** | Text | ✅ Yes | Current path in telemetry JSON | `location.latitude` | **Can change** if field is reorganized. Used in YAML generation and API responses. |
| **Field Type** | Select | ✅ Yes | Mapping type | `direct`, `prioritized`, `calculated`, `transformed`, `io_mapped`, `mix` | Determines transformation approach. |
| **💽 Mapping Fields (db)** | Relation | ❌ No | Links to Mapping Fields DB | (Relation) | Direct access to mapping rules. |
| **Notes** | Text | ❌ No | Additional context | `Requires Asset Service integration` | Important context or limitations. |
| **💽 Provider Field (db)** | Relation | ❌ No | Links to Provider Fields DB | (Relation) | Shows which provider fields map to this field. |
| **Provider Field Path** | Text | ❌ No | Provider field path reference | `params.can_speed` | Reference for documentation. |
| **Provider Field Unit** | Text | ❌ No | Provider field unit reference | `km/h`, `m/s` | Reference for unit conversion. |
| **REST API Endpoints** | Multi-select | ❌ No | REST API endpoints that expose this field | `/telemetry (CUSTOMER)`, `/telemetry (FLEETI)` | Tracks API exposure. |
| **Status** | Select | ✅ Yes | Field status | `active`, `deprecated`, `planned`, `inactive`, `under_review` | Field lifecycle. |
| **Unit** | Text | ❌ No | Standard unit (if applicable) | `km/h`, `°C`, `liters`, `%` | Fleeti standard unit. |
| **Version Added** | Text | ✅ Yes | Version when field was added | `1.0.0` | Version tracking. |
| **WebSocket Contracts** | Multi-select | ❌ No | WebSocket streams that include this field | `live.map.markers`, `live.assets.list`, `live.asset.details` | Tracks WebSocket exposure. |

## Primary Key

**Name** serves as the primary key. Must be unique and follow dot-separated naming convention (e.g., `location_latitude`, `fuel_consumption_cumulative`).

**Important:** Field Name is a **stable identifier** that doesn't change even if field is reorganized. Field Path can be updated independently.

**Example:** `location_latitude` (stable) → `location.latitude` (can change to `position.latitude`)

## Validation Rules

- **Name**: Must be unique and follow naming convention
- **Field Path**: Must follow format `category.field` (lowercase, dot-separated)
- **Field Type**: Must match mapping type in Mapping Fields database
- **Dependencies**: Cannot create circular dependencies
- **Status**: Cannot be `active` if no mappings exist (warning, not error)

---

## Computation Documentation

Computation logic is documented at three levels:

1. **Computation Approach** (CSV): High-level pseudo-code description
2. **Notion Database Raw Content**: Full detailed pseudo-code (not in CSV export)
3. **Dedicated Markdown Files** (`.pseudo.md`): Very complex functions (e.g., `derive_fuel_levels.pseudo.md`, `derive_sensors_environment.pseudo.md`)

---

## YAML Configuration Generation

Data from this database is used by YAML generation scripts:

- **Computation Structure JSON** → Generates YAML structure (via `generate_yaml_from_csv.py`)
- **Computation Approach** → Added as YAML comments
- **Field Path** → Added as YAML comments for reference

See [YAML Configuration Database](../4-yaml-configuration/README.md) for details.

## Provider-Specific Logic

**Transformation rules and provider-specific mapping logic are in the [Mapping Fields Database](https://www.notion.so/Mapping-Fields-Database-2c73e766c9018042aa20c03b6963c681?pvs=21), not here.**

This database contains generic field definitions and pseudo-code. Mapping Fields Database contains provider-specific transformation rules, priority chains, and unit conversions per provider.

---

# How to Use

- Define Fleeti telemetry structure
- Generate YAML configurations (via Mapping Fields Database)
- Reference field definitions in WebSocket and API contracts
- Track field dependencies and evaluation order

---

# Integration with Contracts

**WebSocket Contracts** and **REST API Endpoints** columns track field exposure in WebSocket streams and REST API endpoints.

See [WebSocket Contracts](https://www.notion.so/WebSocket-Contracts-2c73e766c90180fab506dba058ba2310?pvs=21) and [API Contracts](https://www.notion.so/API-Contracts-2c73e766c901807faafee6b8a3dd2d30?pvs=21) for specifications.

---

# Fleeti Fields Database

[Fleeti Fields (db)](https://www.notion.so/2c73e766c901801d9ec1dbd299d1e30e?pvs=21)
