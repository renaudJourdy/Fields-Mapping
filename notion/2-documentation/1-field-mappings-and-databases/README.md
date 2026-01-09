**Status:** 🎯 Done

This section defines the four databases that serve as the single source of truth for field definitions and mappings in the Fleeti Telemetry Mapping system.

---

# Purpose

**These databases are the definitive source of truth** for field definitions. They provide:

- **Provider Fields Database**: Complete catalog of provider-specific telemetry fields (~340 Navixy fields)
- **Fleeti Fields Database**: Complete catalog of unified Fleeti telemetry fields
- **Mapping Fields Database**: Transformation rules linking provider fields to Fleeti fields
- **YAML Configuration Database**: Versioned tracking of generated YAML configuration files

Reference documents provide the big picture, but field definitions come from these databases.

---

# Database Structure

[Provider Fields Database](https://www.notion.so/Provider-Fields-Database-2c73e766c90180e79450f8d6500a0613?pvs=21)

Catalog of provider-specific telemetry fields (Navixy, Teltonika, OEM, etc.).

**Key Contents:** Field names, types, paths, availability, units, descriptions

**Purpose:** Source fields for mapping to Fleeti canonical fields

---

[Fleeti Fields Database](https://www.notion.so/Fleeti-Fields-Database-2c73e766c90180ad9750d33b64db1c01?pvs=21)

Complete catalog of unified Fleeti telemetry fields organized by category (Location, Motion, Power, Fuel, Status, etc.).

**Key Contents:** Field names (stable identifiers), field paths, categories, priorities (P0-P3, T, BL), computation approaches, WebSocket/REST API exposure

**Purpose:** Canonical reference for Fleeti telemetry structure. Used by WebSocket contracts and REST API endpoints.

---

[Mapping Fields Database](https://www.notion.so/Mapping-Fields-Database-2c73e766c9018042aa20c03b6963c681?pvs=21)

Transformation rules linking provider fields to Fleeti fields per provider.

**Key Contents:** Mapping types (direct, prioritized, calculated, transformed, io_mapped), computation structure JSON, transformation logic, configuration levels

**Purpose:** Defines how provider data transforms into Fleeti format

---

[YAML Configuration Database](https://www.notion.so/YAML-Configuration-Database-2cc3e766c901808ca93fcade58ca6999?pvs=21)

Versioned tracking of generated YAML configuration files per provider.

**Key Contents:** Generated YAML files, semantic versions, generation metadata, relations to mapping fields

**Purpose:** Version control and deployment tracking of configuration files

---

# Database Relationships

The databases are interconnected through relations:

```
Provider Fields (N) ──many-to-many──> Mapping Fields (N)
                                          │
                                          │ many-to-one
                                          ▼
                                    Fleeti Fields (1)
                                          │
                                          │ self-relation
                                          ▼
                                    Dependencies
                                          │
Mapping Fields (1) ──one-to-many──> YAML Configuration (N)
```

## **Key Relationships**

1. **Provider Fields ↔ Mapping Fields** (N:M): Provider fields can be used in multiple mappings; mappings can use multiple provider fields
2. **Mapping Fields → Fleeti Fields** (N:1): Multiple mappings can target one Fleeti field (e.g., different providers mapping to same field)
3. **Fleeti Fields → Fleeti Fields** (Self-relation): Tracks dependencies between fields for correct evaluation order
4. **Mapping Fields → YAML Configuration** (1:N): One YAML config version contains many mappings; tracks which mappings are in which config version

**Relationship Purpose:** Enables impact analysis, configuration generation, dependency tracking, and version management.

## Workflow

1. **Catalog provider fields** → Provider Fields Database
2. **Define Fleeti fields** → Fleeti Fields Database (with computation approaches)
3. **Create mapping rules** → Mapping Fields Database (links provider → Fleeti with transformation logic)
4. **Generate YAML configs** → YAML Configuration Database (tracks versions and deployment)

---

# Integration with Contracts

Fleeti Fields Database columns **WebSocket Contracts** and **REST API Endpoints** track which fields are exposed in:

- WebSocket streams (`live.map.markers`, `live.assets.list`, `live.asset.details`)
- REST API endpoints (`/api/v1/telemetry/snapshots`, `/api/v1/telemetry/assets/{id}/history`)

See  [WebSocket Contracts](https://www.notion.so/WebSocket-Contracts-2c73e766c90180fab506dba058ba2310?pvs=21) and [API Contracts](https://www.notion.so/API-Contracts-2c73e766c901807faafee6b8a3dd2d30?pvs=21)  for contract specifications.