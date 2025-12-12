**Status:** 🎯 Structure Created - Content To Be Developed

This section defines the three critical databases that serve as the single source of truth for field definitions and mappings in the Fleeti Telemetry Mapping system.

# Purpose

The databases section provides:

- **Provider Fields Database**: Complete catalog of all provider-specific telemetry fields
- **Fleeti Fields Database**: Complete catalog of all Fleeti telemetry fields (~343+ fields)
- **Mapping Fields Database**: Field transformation rules linking provider fields to Fleeti fields

**These databases are the definitive source of truth** for field definitions. Reference documents (like the schema specification) provide the big picture and help with prioritization, but field definitions come from these databases.

---

## Database Structure

### [Provider Fields Database](./provider-fields/README.md)

Catalog of all provider-specific telemetry fields organized by provider (Navixy, Teltonika, OEM, etc.).

**Contents:**
- Provider field names, types, descriptions
- Observed values and formats
- Provider-specific field metadata
- Field availability by provider

**Purpose:** Used to map provider fields to Fleeti canonical fields.

---

### [Fleeti Fields Database](./fleeti-fields/README.md)

Complete catalog of all Fleeti telemetry fields organized by section (Asset Metadata, Location, Motion, Power, Fuel, etc.).

**Contents:**
- Fleeti field names, types, priorities
- Field sections and organization
- Transformation requirements
- Visibility and usage (P0-P3, T, BL)

**Purpose:** Serves as the canonical reference for Fleeti telemetry structure.

---

### [Mapping Fields Database](./mapping-fields/README.md)

Field transformation rules and priority chains linking provider fields to Fleeti fields.

**Contents:**
- Direct mappings (1:1 provider → Fleeti)
- Priority chains (multiple provider fields → one Fleeti field)
- Calculation rules (derived fields)
- I/O mappings (raw I/O → semantic fields)
- Transformation logic

**Purpose:** Links provider fields to Fleeti fields with transformation logic.

---

## Database Relationships

The databases are interconnected:

```
Provider Fields Database
         ↓
Mapping Fields Database (transformation rules)
         ↓
Fleeti Fields Database
```

**Workflow:**
1. Provider fields are cataloged in Provider Fields Database
2. Mapping rules are defined in Mapping Fields Database
3. Fleeti fields are defined in Fleeti Fields Database
4. Configuration files are generated from these databases

---

## Related Documentation

- **[Schema Specification](../../../docs/legacy/fleeti-telemetry-schema-specification.md)**: Big picture reference (not definitive, databases are source of truth)
- **[Field Mappings](../../2-field-mappings/README.md)**: Field catalogs and mapping documentation
- **[Configuration Guide](../../../3-developer-resources/configuration-guide/README.md)**: How configuration files are generated from databases

---

**Last Updated:** 2025-01-XX  
**Section Status:** 🎯 Structure Created - Content To Be Developed

