# Data Lineage & Transformation Metadata

**Status:** 🎯 Draft  
**Priority:** 🟡 MEDIUM (Important for debugging and historical recalculation)  
**Epic Association:** Epic 2 (Transformation), Epic 4 (Storage), Epic 5 (Configuration)

---

## Overview

This document describes transformation metadata tracking, which enables data lineage, debugging, and accurate historical recalculation. Each telemetry record stores metadata about how it was calculated: which configuration was used, which provider fields were selected, and which mapping rules were applied.

---

## Table of Contents

1. [Transformation Metadata](#1-transformation-metadata)
2. [Storage of Metadata](#2-storage-of-metadata)
3. [Use Cases](#3-use-cases)
4. [Historical Recalculation](#4-historical-recalculation)

---

## 1. Transformation Metadata

### 1.1 Purpose

Transformation metadata answers critical questions:
- **Which configuration file/version was used?** (for debugging and recalculation)
- **Which provider fields were selected?** (for prioritized mappings, shows which source was chosen)
- **Which mapping rules were applied?** (for understanding how fields were calculated)
- **What was the transformation path?** (for data lineage and audit)

### 1.2 Metadata Structure

Each transformed telemetry record includes a `_metadata` or `_provenance` object containing:

```json
{
  "transformation": {
    "config_version": "1.2.3",
    "config_hash": "sha256:abc123...",
    "config_levels": ["default", "customer:acme", "asset_group:fleet-a"],
    "applied_at": "2025-01-21T12:00:00Z",
    "transformation_pipeline_version": "2.1.0"
  },
  "field_lineage": {
    "motion.speed": {
      "mapping_type": "prioritized",
      "selected_provider_field": "can_speed",
      "available_provider_fields": ["can_speed", "obd_speed", "speed"],
      "priority_order": ["can_speed", "obd_speed", "speed"],
      "selected_index": 0,
      "value_source": "can_speed",
      "unit_conversion": null
    },
    "fuel.level": {
      "mapping_type": "transformed",
      "base_provider_field": "fuel_level_percent",
      "transformation_rule": "(fuel.level_percent / 100) * static.tank_capacity_liters",
      "static_data_used": {
        "asset.properties.vehicle.powertrain.fuel_tank_capacity.value": 80
      },
      "result": 45.6
    },
    "location.cardinal_direction": {
      "mapping_type": "calculated",
      "calculation_type": "function_reference",
      "backend_function": "derive_from_heading",
      "function_parameters": ["location.heading"],
      "dependencies": ["location.heading"]
    }
  },
  "raw_packet": {
    "packet_id": "navixy-20250121-120000-abc123",
    "provider": "navixy",
    "received_at": "2025-01-21T12:00:00Z",
    "cold_storage_reference": "s3://cold-storage/navixy/2025/01/21/abc123.raw"
  }
}
```

### 1.3 Metadata Fields

| Field | Type | Description | Example | Why It's Important |
|-------|------|-------------|---------|-------------------|
| **config_version** | String | Configuration file version | `1.2.3` | Identifies which configuration was used. Critical for historical recalculation. |
| **config_hash** | String | SHA256 hash of configuration | `sha256:abc123...` | Ensures exact configuration is reproducible. Detects configuration drift. |
| **config_levels** | Array | Hierarchical config levels applied | `["default", "customer:acme"]` | Shows which configuration hierarchy was used. Important for multi-tenant scenarios. |
| **applied_at** | Timestamp | When transformation occurred | `2025-01-21T12:00:00Z` | Timestamp for transformation. Critical for debugging and audit. |
| **field_lineage** | Object | Per-field transformation details | See structure above | **Core metadata** - shows exactly how each field was calculated. |
| **raw_packet** | Object | Reference to original packet | See structure above | Links to cold storage for recalculation. |

### 1.4 Field Lineage Details

For each Fleeti field, the lineage includes:

**For Prioritized Mappings:**
- `mapping_type`: `"prioritized"`
- `selected_provider_field`: Which provider field was actually chosen
- `available_provider_fields`: All provider fields that were checked
- `priority_order`: The priority chain that was evaluated
- `selected_index`: Position in priority chain (0 = highest priority)
- `value_source`: The exact provider field path used

**For Calculated Fields:**
- `mapping_type`: `"calculated"`
- `calculation_type`: `"function_reference"` or `"formula"`
- `backend_function`: Function name (if function_reference)
- `function_parameters`: Parameters passed to function
- `dependencies`: Other Fleeti fields this depends on

**For Transformed Fields:**
- `mapping_type`: `"transformed"`
- `base_provider_field`: Source provider field
- `transformation_rule`: Formula/rule applied
- `static_data_used`: Asset metadata values used
- `result`: Final calculated value

**For Direct Mappings:**
- `mapping_type`: `"direct"`
- `provider_field`: Source provider field
- `unit_conversion`: Unit conversion applied (if any)

---

## 2. Storage of Metadata

### 2.1 Storage Tiers

**Warm Storage:**
- ✅ **Store complete transformation metadata** with each telemetry record
- Enables debugging and field-level lineage queries
- Supports "how was this calculated?" queries

**Hot Storage:**
- ⚠️ **Store minimal metadata** (config_version only) to reduce storage size
- Core fields only, metadata can be retrieved from warm storage if needed

**Cold Storage:**
- ✅ **Store raw packet** with packet metadata (provider, timestamp, packet_id)
- Links to transformation metadata via packet_id

### 2.2 Storage Structure

**Warm Storage Record:**
```json
{
  "asset_id": "uuid",
  "timestamp": 1234567890123,
  "telemetry": { /* complete Fleeti telemetry */ },
  "status": { "top_status": "in_transit", "statuses": [...] },
  "_metadata": {
    "transformation": { /* transformation metadata */ },
    "field_lineage": { /* field-level lineage */ },
    "raw_packet": { /* raw packet reference */ }
  }
}
```

### 2.3 Storage Considerations

**Storage Size:**
- Metadata adds ~1-5KB per record (depending on field count)
- For 1M records/day: ~1-5GB/day additional storage
- Acceptable trade-off for debugging and recalculation capability

**Query Performance:**
- Metadata stored as JSON object (not indexed by default)
- Can be indexed for specific queries (e.g., "find all records using config v1.2.3")
- Field lineage queries may require full record scan (acceptable for debugging)

---

## 3. Use Cases

### 3.1 Debugging

**Scenario:** Customer reports incorrect speed value.

**Query:** "Show me how `motion.speed` was calculated for asset X at timestamp Y"

**Metadata Provides:**
- Which provider field was selected (`can_speed`, `obd_speed`, or `speed`)
- Which configuration version was used
- What the priority chain was
- Why a specific provider field was chosen

### 3.2 Data Quality Investigation

**Scenario:** Unexpected field values in historical data.

**Query:** "Find all records where `fuel.level` used transformation rule X"

**Metadata Provides:**
- Which transformation rules were applied
- Which static data (tank capacity) was used
- Configuration version at time of transformation

### 3.3 Configuration Impact Analysis

**Scenario:** Configuration change deployed, need to understand impact.

**Query:** "Compare field lineage before and after config change"

**Metadata Provides:**
- Exact configuration versions used
- Field-level differences in calculation
- Impact assessment of configuration changes

### 3.4 Compliance & Audit

**Scenario:** Customer asks "How was this data calculated?"

**Metadata Provides:**
- Complete audit trail of transformation
- Configuration versions used
- Provider fields selected
- Transformation rules applied

---

## 4. Historical Recalculation

### 4.1 Recalculation with Metadata

When recalculating historical data:

1. **Load raw packet** from cold storage (via `raw_packet.cold_storage_reference`)
2. **Identify original configuration** (via `transformation.config_version` and `config_hash`)
3. **Apply original configuration** to raw packet
4. **Compare results** with stored metadata to verify accuracy
5. **Apply new configuration** to compute new fields

### 4.2 Recalculation Process

```json
{
  "recalculation_job": {
    "target_fields": ["fuel.consumption.cumulative"],
    "time_range": {
      "start": "2025-01-01T00:00:00Z",
      "end": "2025-01-21T12:00:00Z"
    },
    "process": [
      "1. Load historical records from warm storage",
      "2. Extract raw_packet.cold_storage_reference",
      "3. Load original config (transformation.config_version)",
      "4. Load new config (latest version)",
      "5. Apply both configs to raw packets",
      "6. Compare original vs new calculations",
      "7. Update warm storage with new fields"
    ]
  }
}
```

### 4.3 Configuration Versioning

**Critical Requirement:** Configuration versions must be:
- **Immutable**: Once deployed, config version cannot change
- **Reproducible**: Same config version + same raw packet = same result
- **Stored**: All configuration versions stored permanently for recalculation

**Configuration Storage:**
- Store all configuration versions in configuration storage (Epic 5)
- Link config versions to transformation metadata
- Enable retrieval of exact configuration used for any historical record

---

## 5. Implementation Requirements

### 5.1 Transformation Pipeline (Epic 2)

**Requirement:** Generate transformation metadata during field mapping.

**Tasks:**
- Track which configuration is loaded
- Track which provider fields are selected (for prioritized mappings)
- Track which mapping rules are applied
- Generate field lineage for each Fleeti field
- Include raw packet reference

### 5.2 Storage (Epic 4)

**Requirement:** Store transformation metadata with telemetry records.

**Tasks:**
- Include `_metadata` object in warm storage records
- Store minimal metadata in hot storage (config_version only)
- Link to cold storage via packet_id

### 5.3 Configuration Management (Epic 5)

**Requirement:** Version and store all configuration files.

**Tasks:**
- Generate config hash (SHA256) for each configuration version
- Store all configuration versions permanently
- Enable retrieval of configuration by version/hash

---

## 6. Related Documentation

- **[🔄 Epic 2 - Field Mapping](../1-specifications/E2-Field-Mapping-Transformation/README.md)**: Transformation pipeline
- **[💾 Epic 4 - Storage](../1-specifications/E4-Storage-Data-Management/README.md)**: Storage specifications
- **[⚙️ Epic 5 - Configuration](../1-specifications/E5-Configuration-Management/README.md)**: Configuration management
- **[📜 Change History Database](../1-specifications/1-databases/4-change-history/README.md)**: Configuration change tracking

---

**Last Updated:** 2025-01-XX  
**Status:** 🎯 Draft - Ready for Review

