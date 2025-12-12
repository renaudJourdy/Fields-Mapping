**Status:** 🎯 Structure Created - Content To Be Developed

## Purpose

The Fleeti Fields Database is the complete catalog of all Fleeti telemetry fields (~343+ fields) organized by section. This database serves as the **single source of truth** for Fleeti telemetry field definitions.

## What This Database Contains

- **Fleeti field names**: Canonical field names in Fleeti format
- **Field sections**: Organization (Asset Metadata, Location, Motion, Power, Fuel, etc.)
- **Field types**: Data types and structures
- **Field priorities**: Implementation priorities (P0-P3, T, BL, ?)
- **Transformation requirements**: How fields are computed (direct, prioritized, calculated, transformed)
- **Visibility**: Customer-facing vs internal fields

## Database Structure

[Column structure and schema to be defined]

## How to Use

This database is used to:
- Define Fleeti telemetry structure
- Prioritize field implementation
- Generate configuration files
- Reference field definitions in specifications

## Related Documentation

- **[Schema Specification](../../../docs/legacy/fleeti-telemetry-schema-specification.md)**: Big picture reference (not definitive)
- **[🔀 Mapping Fields Database](../mapping-fields/README.md)**: How provider fields map to Fleeti fields
- **[Field Mappings](../../2-field-mappings/fleeti-fields-catalog.md)**: Field catalog documentation

---

**Last Updated:** 2025-01-XX  
**Status:** 🎯 Structure Created - Content To Be Developed

