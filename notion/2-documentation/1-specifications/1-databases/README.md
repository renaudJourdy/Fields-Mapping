**Status:** 🎯 In Progress

This section defines the three critical databases that serve as the single source of truth for field definitions and mappings in the Fleeti Telemetry Mapping system.

---

# Purpose

The databases section provides:

- **Provider Fields Database**: Complete catalog of all provider-specific telemetry fields
- **Fleeti Fields Database**: Complete catalog of all Fleeti telemetry fields (~343+ fields)
- **Mapping Fields Database**: Field transformation rules linking provider fields to Fleeti fields
- **Change History Database** (Optional): Audit trail of all changes to fields and mappings
- **YAML Configuration Database**: Versioned tracking of generated YAML configuration files

**These databases are the definitive source of truth** for field definitions. Reference documents (like the schema specification) provide the big picture and help with prioritization, but field definitions come from these databases.

---

# Database Structure

[Provider Fields Database](https://www.notion.so/Provider-Fields-Database-2c73e766c90180e79450f8d6500a0613?pvs=21)

Catalog of all provider-specific telemetry fields organized by provider (Navixy, Teltonika, OEM, etc.).

**Contents:**

- Provider field names, types, descriptions
- Observed values and formats
- Provider-specific field metadata
- Field availability by provider

**Purpose:** Used to map provider fields to Fleeti canonical fields.

---

[Fleeti Fields Database](https://www.notion.so/Fleeti-Fields-Database-2c73e766c90180ad9750d33b64db1c01?pvs=21)

Complete catalog of all Fleeti telemetry fields organized by section (Asset Metadata, Location, Motion, Power, Fuel, etc.).

**Contents:**

- Fleeti field names, types, priorities
- Field sections and organization
- Transformation requirements
- Visibility and usage (P0-P3, T, BL)

**Purpose:** Serves as the canonical reference for Fleeti telemetry structure.

---

[Mapping Fields Database](https://www.notion.so/Mapping-Fields-Database-2c73e766c9018042aa20c03b6963c681?pvs=21)

Field transformation rules and priority chains linking provider fields to Fleeti fields.

**Contents:**

- Direct mappings (1:1 provider → Fleeti)
- Priority chains (multiple provider fields → one Fleeti field)
- Calculation rules (derived fields)
- I/O mappings (raw I/O → semantic fields)
- Transformation logic

**Purpose:** Links provider fields to Fleeti fields with transformation logic.

---

[[📝 Change History Database](https://www.notion.so/4-change-history/README.md) (Optional)](https://www.notion.so/Change-History-Database-Optional-2c73e766c901809988fcf94d86a67f67?pvs=21)

Complete audit trail of all changes to fields and mappings for versioning and compliance.

**Contents:**

- Change records for all field and mapping modifications
- Change metadata (who, when, why)
- Version tracking
- YAML sync status

**Purpose:** Maintains audit trail and enables change tracking, rollback planning, and compliance.

---

[⚙️ YAML Configuration Database](https://www.notion.so/YAML-Configuration-Database-2cc3e766c901808ca93fcade58ca6999?pvs=21)

Versioned tracking of generated YAML configuration files per provider.

**Contents:**

- Generated YAML configuration files
- Version tracking per provider
- Generation metadata (date, status)
- Relations to mapping fields used in generation

**Purpose:** Version control and tracking of generated configuration files. Enables configuration management, rollback, and audit trail of deployed configurations.

---

# Database Relationships

The databases are interconnected through relations:

```
┌─────────────────────────────┐
│  Provider Fields Database   │
│                             │
│  - Field Name (PK)          │
│  - Provider                 │
│  - Field Path               │
│  - Data Type                │
│  - Status                   │
└──────────┬──────────────────┘
           │
           │ many-to-many
           │ (via Field Mappings)
           │
           ▼
┌─────────────────────────────┐
│  Mapping Fields Database    │
│                             │
│  - Mapping Name (PK)        │
│  - Fleeti Field (FK)        │
│  - Provider Fields (FK)     │
│  - Mapping Type             │
│  - Priority JSON            │
│  - Calculation Formula      │
│  - Status                   │
└──────────┬──────────────────┘
           │
           │ many-to-one       │ one-to-many
           │                   │
           ▼                   ▼
┌─────────────────────────┐ ┌─────────────────────────────┐
│  Fleeti Fields Database │ │ YAML Configuration Database │
│                         │ │                             │
│  - Field Name (PK)      │ │ - Config Name (PK)          │
│  - Field Path           │ │ - Provider                  │
│  - Category             │ │ - Version                   │
│  - Priority             │ │ - YAML Content              │
│  - Field Type           │ │ - Generation Date           │
│  - Status               │ │ - Status                    │
└─────────────────────────┘ └─────────────────────────────┘
```

## Relationship Details

### Relationship 1: Provider Fields ↔ Mapping Fields

**Type:** Many-to-Many (via Relation field)

**From Database:** Provider Fields

**To Database:** Mapping Fields

**Via Field:** `Provider Fields` (Relation field in Mapping Fields)

**Cardinality:** N:M (one provider field can be used in many mappings, one mapping can use many provider fields)

**Required:** Yes (mapping must reference at least one provider field)

**Cascade Rules:** If provider field is deleted, mappings referencing it should be marked deprecated

**Purpose:** Links provider fields to mapping rules. Enables:

- Finding all mappings that use a specific provider field
- Identifying which provider fields are used for a mapping
- Impact analysis when provider fields change

### Relationship 2: Mapping Fields → Fleeti Fields

**Type:** Many-to-One

**From Database:** Mapping Fields

**To Database:** Fleeti Fields

**Via Field:** `Fleeti Field` (Relation field in Mapping Fields)

**Cardinality:** N:1 (many mappings can target one Fleeti field)

**Required:** Yes (mapping must reference a Fleeti field)

**Cascade Rules:** If Fleeti field is deleted, mappings referencing it should be marked deprecated

**Purpose:** Links mapping rules to target Fleeti fields. Enables:

- Finding all mappings for a specific Fleeti field
- Generating configuration for a specific field
- Understanding how a field is computed

### Relationship 3: Fleeti Fields → Fleeti Fields (Self-Relation)

**Type:** Many-to-Many (Self-Relation)

**Via Field:** `Dependencies` (Relation field in Fleeti Fields)

**Cardinality:** N:M (one field can depend on many fields, one field can be depended upon by many fields)

**Required:** No (only for calculated/transformed fields)

**Cascade Rules:** Prevents circular dependencies

**Purpose:** Tracks field dependencies. Critical for:

- Ensuring correct evaluation order
- Identifying fields that need to be computed first
- Preventing circular dependencies

### Relationship 4: Change History (Optional)

**Type:** One-to-Many

**From Database:** Change History

**To Database:** Provider Fields, Fleeti Fields, Mapping Fields

**Via Field:** `Entity` (Relation field in Change History)

**Cardinality:** 1:N (one change record per entity modification)

**Required:** No (optional but recommended)

**Purpose:** Complete audit trail of all changes to fields and mappings.

### Relationship 5: Mapping Fields → YAML Configuration

**Type:** One-to-Many

**From Database:** Mapping Fields

**To Database:** YAML Configuration

**Via Field:** `YAML Config` (Relation field in Mapping Fields)

**Cardinality:** 1:N (one YAML config contains many mappings, one mapping belongs to one YAML config version)

**Required:** No (optional, but recommended for tracking)

**Purpose:** Links mapping rules to generated configuration versions. Enables:

- Finding which YAML config version contains a specific mapping
- Identifying all mappings included in a configuration version
- Tracking configuration generation and versioning
- Impact analysis when mappings change (which configs need regeneration)

## Workflow

1. **Provider fields are cataloged** in Provider Fields Database
    - Fields are discovered from provider packets
    - Field properties are documented (type, unit, availability)
2. **Fleeti fields are defined** in Fleeti Fields Database
    - Fields are organized by category
    - Priorities are assigned (P0-P3)
    - Field types are specified (direct, calculated, etc.)
3. **Mapping rules are created** in Mapping Fields Database
    - Links provider fields to Fleeti fields
    - Defines transformation logic
    - Specifies priority orders, formulas, etc.
4. **YAML configurations are generated and tracked** in YAML Configuration Database
    - Configurations are generated from mapping rules
    - Versions are tracked and managed per provider
    - Changes trigger new configuration versions
    - Configuration files are versioned and audited

---

# Related Documentation

- **Schema Specification**: Big picture reference (not definitive, databases are source of truth)
- **Field Mappings**: Field catalogs and mapping documentation
- **Configuration Guide**: How configuration files are generated from databases