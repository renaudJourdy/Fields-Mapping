**Status:** 🎯 Done

# Purpose

The Mapping Fields Database contains field transformation rules that link provider fields to Fleeti fields per provider. This database defines how provider-specific telemetry data transforms into the unified Fleeti format.

**Key Contents:** Mapping rules (direct, prioritized, calculated, transformed, io_mapped), computation structure JSON (machine-readable for YAML generation), provider field references, and configuration levels.

---

# Database Structure

## Column Definitions

Columns are listed in the same order as they appear in the CSV export:

| Column Name | Type | Required | Description | Example | Why It's Important |
| --- | --- | --- | --- | --- | --- |
| **Name** | Title | ✅ Yes | Mapping name (primary key) | `location.latitude from Navixy` | Primary key - descriptive identifier. Format: `[Fleeti Field] from [Provider]`. |
| **Computation Approach** | Text | ❌ No | Pseudo-code description (rolled up from Fleeti Fields DB) | `Direct mapping from Navixy: lat (path: lat)` | Human-readable computation description. Rolled up from related Fleeti Field. Added as YAML comments. |
| **Computation Structure JSON** | Text | ✅ Yes | Machine-readable JSON for YAML generation | `{"type": "direct", "sources": [...]}` | Used by `generate_yaml_from_csv.py` to generate YAML structure. Contains type, sources, priorities, functions, parameters. |
| **Configuration Level** | Select | ✅ Yes | Where mapping applies | `default`, `customer`, `asset_group`, `asset` | Defines mapping hierarchy. Lower levels override higher levels. |
| **Fleeti Field** | Relation | ✅ Yes | Links to Fleeti Fields DB | (Relation) | Target field identifier. Used as YAML key (Field Name, not Field Path). |
| **Fleeti Field Data Type** | Text | ❌ No | Fleeti field data type (from relation) | `number`, `string`, `boolean` | Used for YAML generation and validation. |
| **Fleeti Field Path** | Text | ❌ No | JSON path in telemetry object (from relation) | `location.latitude` | Used for YAML comments only. **NOT used as YAML key** - Field Name is used instead. |
| **Fleeti Field Unit** | Text | ❌ No | Fleeti field unit (from relation) | `degrees`, `km/h`, `liters` | Used for unit conversion detection in YAML generation. |
| **Mapping Type** | Select | ✅ Yes | Type of mapping | `direct`, `prioritized`, `calculated`, `transformed`, `io_mapped`, `mix` | Determines transformation approach. |
| **Notes** | Text | ❌ No | Additional context | `CAN speed most accurate, use when available` | Important context or limitations. |
| **Provider** | Select | ✅ Yes | Provider name | `navixy`, `oem-trackunit` | Identifies which provider this mapping applies to. |
| **Provider Field (db)** | Relation | ❌ No | Links to Provider Fields DB | (Relation) | Reference to provider field. Can be multiple for prioritized mappings. |
| **Provider Field Unit** | Text | ❌ No | Provider field unit (from relation) | `km/h`, `m/s` | Used for unit conversion detection. |
| **Provider Fields** | Relation | ❌ No | Links to Provider Fields DB (can be multiple) | (Relation) | Source field identifiers. Can be single (direct) or multiple (prioritized). |
| **Status** | Select | ✅ Yes | Mapping status | `active`, `deprecated`, `planned`, `inactive` | Tracks mapping lifecycle. Only `active` and `planned` are used in YAML generation. |
| **Version Added** | Text | ✅ Yes | Version when mapping was added | `1.0.0` | Version tracking. |
| **YAML Configurations (db)** | Relation | ❌ No | Links to YAML Configuration DB | (Relation) | Tracks which YAML config versions include this mapping. |

## Primary Key

**Name** serves as the primary key. Format: `[Fleeti Field] from [Provider]` (e.g., `location.latitude from Navixy`).

**Important:** YAML generation uses **Fleeti Field Name** (stable identifier) as the YAML key, not the Mapping Name. The Mapping Name is for human identification only.

## Mapping Type Requirements

**Required for all types:** Name, Fleeti Field, Provider, Mapping Type, Status, Configuration Level, Computation Structure JSON

**Type-specific requirements:**
- **direct**: Single provider field in Computation Structure JSON
- **prioritized**: Multiple sources with priorities in Computation Structure JSON
- **calculated**: Function reference in Computation Structure JSON (`calculation_type: function_reference`)
- **transformed**: Transformation logic in Computation Structure JSON
- **io_mapped**: I/O mapping config in Computation Structure JSON
- **mix**: Mixed source types (e.g., direct + calculated) in Computation Structure JSON

## Validation Rules

- **Name**: Must be unique and follow format `[Fleeti Field] from [Provider]`
- **Fleeti Field**: Must reference active Fleeti field
- **Computation Structure JSON**: Must be valid JSON matching Mapping Type requirements
- **Mapping Type**: Must match structure in Computation Structure JSON
- **Status**: Only `active` and `planned` mappings are used in YAML generation

---

## YAML Configuration Generation

Data from this database is used by YAML generation scripts:

- **Computation Structure JSON** → Generates YAML structure (via `generate_yaml_from_csv.py`)
  - Contains type, sources, priorities, function references, parameters
  - Script parses JSON and applies optimization rules
- **Fleeti Field** (Name) → Used as YAML key (stable Field Name, not Field Path)
- **Computation Approach** → Added as YAML comments (from Fleeti Fields DB rollup)
- **Fleeti Field Path** → Added as YAML comment for reference
- **Fleeti Field Data Type** → Added as `data_type` in YAML
- **Fleeti Field Unit** → Added as `unit` in YAML
- **Provider Field Unit** → Used for unit conversion detection

**Important:** YAML uses **Field Names** (stable identifiers) as keys and in dependencies/parameters. Backend resolves Field Name → Field Path at runtime.

See [YAML Configuration Database](../4-yaml-configuration/README.md) for complete workflow and optimization rules.

---

# How to Use

- Generate YAML configuration files (via YAML generation scripts)
- Define provider-specific transformation rules
- Track mapping rule changes and versions
- Support hierarchical configuration (default, customer, asset_group, asset)

---

# Mapping Fields Database

[Mapping Fields (db)](https://www.notion.so/2cc3e766c901806b9904e69fec02b085?pvs=21)