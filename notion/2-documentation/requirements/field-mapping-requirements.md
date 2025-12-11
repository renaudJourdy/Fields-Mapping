# Field Mapping Requirements

**Status:** ✅ Validated  
**Source:** `Wiki/telemetry-system-specification.md` Section 8

Field mapping requirements including field documentation and new field detection.

---

## Overview

This document defines requirements for field documentation and new field detection in the telemetry system. These requirements ensure complete field coverage and the ability to detect and incorporate new telemetry capabilities.

---

## Field Documentation Requirement

### Objective

Create a **complete catalog** of all possible Fleeti telemetry fields we can produce.

### Current State

`docs/reference/navixy-field-catalog.csv` contains 343 fields from Navixy, but we need:

1. **Fleeti Telemetry Fields Catalog**: All possible Fleeti fields (not provider fields)
2. **Mapping documentation**: Which provider fields map to which Fleeti fields
3. **Transformation rules**: How each Fleeti field is calculated/derived
4. **Field metadata**: Units, ranges, descriptions, use cases

### Required Documentation

Each field should document:

- **Name**: Fleeti field name
- **Type**: direct / prioritized / calculated / transformed
- **Sources**: Provider fields that contribute
- **Unit**: Standard unit in Fleeti
- **Range**: Valid value range
- **Description**: What it represents
- **Use cases**: Where it's displayed/used
- **Priority**: Core / Extended / Optional

### Field Catalog Structure

```
Fleeti Telemetry Fields Catalog
├── Core Fields (~50)
│   ├── location.*
│   ├── vehicle.*
│   └── events.*
├── Extended Fields (~200+)
│   ├── fuel.*
│   ├── driving.*
│   ├── sensors.*
│   └── ...
└── Calculated Fields
    ├── aggregations.*
    ├── derived.*
    └── transformed.*
```

---

## New Field Detection Watchdog

### Requirement

System must detect when a **new field appears** in provider telemetry that we haven't seen before (non-zero value).

### Watchdog Functionality

**Monitoring**:
- Monitor incoming telemetry packets
- Track all fields present in packets
- Compare against known field catalog

**Detection**:
- Flag any field with non-zero value that:
  - Is not in our field catalog, OR
  - Is in catalog but has no mapping rule configured

**Alerting**:
- Alert/notification when new field detected
- Log new field with sample values for analysis
- Include field name, value, and context (asset, provider, timestamp)

**Purpose**: Ensure we don't miss new telemetry capabilities and can document/incorporate them

### Watchdog Implementation Requirements

1. **Real-time Monitoring**: Check fields as packets are received
2. **Catalog Comparison**: Compare against complete field catalog
3. **Mapping Rule Check**: Verify mapping rules exist for cataloged fields
4. **Alert System**: Notify appropriate teams when new fields detected
5. **Logging**: Store new field samples for analysis
6. **Analysis Tools**: Provide tools to review and categorize new fields

---

## Field Mapping Requirements

### Complete Field Coverage

**Requirement**: All provider fields must be mappable to Fleeti telemetry format.

**Approach**:
- Document all provider fields in catalog
- Define mapping rules for each field
- Support unknown fields through flexible architecture
- Preserve all fields in raw archive

### Mapping Rule Documentation

**Requirement**: All field mappings must be documented with:

- Provider field name
- Fleeti field path
- Mapping type (direct, prioritized, calculated, transformed)
- Priority rules (if applicable)
- Calculation logic (if applicable)
- Dependencies (if applicable)

### Configuration-Driven Mappings

**Requirement**: All field mappings must be defined in configuration files (YAML), not hardcoded.

**Rationale**: 
- Customer-specific requirements without code changes
- Faster adaptation to new fields and providers
- Easier testing and validation
- Reduced deployment risk

---

## Field Priority Requirements

### Priority Assignment

**Requirement**: All fields must be assigned priority levels (P0-P3, T, BL, ?) that determine:

- Implementation order
- Customer visibility
- API exposure
- UI display

### Priority Guidelines

- **Customer-facing fields** (displayed in UI, exposed in customer APIs): Use P0, P1, or P2
- **Internal computation fields** (used to compute other fields, not displayed): Use BL
- **Troubleshooting fields** (super admin access only, diagnostic purposes): Use T
- **Uncertain fields** (needs investigation): Use ?
- **Low priority or future fields**: Use P3

---

## Related Documentation

- **[Fleeti Fields Catalog](../field-mappings/fleeti-fields-catalog.md)**: Complete Fleeti telemetry fields
- **[Schema Specification](../specifications/schema-specification.md)**: Complete field definitions
- **[Mapping Rules](../field-mappings/mapping-rules.md)**: Field transformation rules
- **[Telemetry System Specification](../specifications/telemetry-system-specification.md)**: Complete system specification

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-XX  
**Status**: ✅ Validated  
**Source**: `Wiki/telemetry-system-specification.md` Section 8






