# Telemetry System Specification

**Status:** ✅ Validated  
**Source:** `Wiki/telemetry-system-specification.md`

> Comprehensive specification for creating a provider-agnostic Fleeti Telemetry system from multi-provider raw telemetry data

---

## Table of Contents

1. [Context & Background](#1-context--background)
2. [Objectives & Vision](#2-objectives--vision)
3. [Telemetry Sources](#3-telemetry-sources)
4. [How Telemetry Will Be Used](#4-how-telemetry-will-be-used)
5. [Field Types & Transformation Rules](#5-field-types--transformation-rules)
6. [Storage Strategy](#6-storage-strategy)
7. [Configuration System](#7-configuration-system)
8. [Field Documentation & Watchdog](#8-field-documentation--watchdog)
9. [Prioritization & Scope](#9-prioritization--scope)
10. [Implementation Considerations](#10-implementation-considerations)
11. [Success Criteria](#11-success-criteria)
12. [Frontend Integration Insights](#12-frontend-integration-insights)
13. [Next Steps](#13-next-steps)
14. [References](#14-references)

---

## 1. Context & Background

### 1.1 Current Architecture

Fleeti currently uses **Navixy as a white-labeling platform** for configuring GPS trackers:

1. **Device → Navixy**: GPS devices send telemetry data to Navixy's platform
2. **Navixy Storage**: Navixy receives, parses, and stores all telemetry in their own database
3. **Navixy API**: Navixy exposes telemetry data to Fleeti and customers through their API

### 1.2 Data Forwarding Investigation

We have investigated a **new data ingestion method called "Data Forwarding"**:

- **Real-time forwarding**: As soon as a device sends records to Navixy, Navixy forwards us the **raw parsed telemetry** immediately
- **No API polling required**: Eliminates the need to poll Navixy's API
- **Direct access**: We receive the data stream directly from Navixy's infrastructure

### 1.3 POC Validation Results

We have completed a Proof of Concept (POC) to validate Data Forwarding:

- ✅ **Received all telemetry** from test devices
- ✅ **Validated data integrity**: Compared Data Forwarding packets with Navixy API exports
- ✅ **Field catalog created**: Aggregated all unique telemetry fields found in `docs/reference/navixy-field-catalog.csv`
- ✅ **Result**: ~340 distinct telemetry fields identified from Navixy Data Forwarding

---

## 2. Objectives & Vision

### 2.1 Primary Objective

**Create Fleeti's own telemetry system** based on telemetry received through Navixy (and future providers), making Fleeti **provider-agnostic** and **provider-proof**.

### 2.2 Key Requirements

- **Provider-agnostic**: Design must work with Navixy, OEM manufacturers, and any future telemetry providers
- **Provider-proof**: System must be able to aggregate **any possible fields from any provider** into a unified Fleeti telemetry format
- **Future-proof**: Architecture must support new providers and field types without major refactoring
- **Complete data preservation**: Store all raw telemetry to enable historical recalculation when new Fleeti telemetry fields are added

### 2.3 Vision Statement

> "We need to aggregate any possible fields from any provider into a dedicated Fleeti telemetry. This Fleeti telemetry will be consumed by Fleeti One (web/mobile), exposed via API for customers, and potentially streamed in the future. All raw data must be preserved so we can recalculate historical Fleeti telemetry when new fields are introduced."

---

## 3. Telemetry Sources

### 3.1 Current Provider: Navixy

- **Source**: White-label GPS tracking platform
- **Format**: Raw parsed telemetry packets via Data Forwarding
- **Fields**: ~340 identified fields (see `docs/reference/navixy-field-catalog.csv`)

### 3.2 Future Providers

#### 3.2.1 OEM Direct Integration

- **Source**: Vehicle/machine manufacturers
- **Connection**: Direct OEM integration via credentials
- **Format**: Provider-specific telemetry format (AEMP 2.0)
- **Examples**: TrackUnit, CareTrack, Mecalac, Manitou, Liebher

#### 3.2.2 Other Providers

- **Unknown providers**: System must handle providers not yet identified (Abeeway...)
- **Flexible ingestion**: Architecture must accept any telemetry format
- **Field mapping**: New provider fields must be mappable to Fleeti telemetry

---

## 4. How Telemetry Will Be Used

### 4.1 Consumption Channels

#### 4.1.1 Fleeti One Frontend (Primary)

- **Platform**: Web and mobile applications
- **Use cases**:
  - **Live data**: Real-time telemetry display (current location, speed, status)
  - **Historical data**: Time-series visualization of any telemetry field
  - **Asset details**: Detailed telemetry view when clicking on an asset
  - **Map markers**: Location-based display (with field-based coloring, e.g., top-status)

#### 4.1.2 Customer APIs

- **Purpose**: Expose Fleeti telemetry to customers via REST/GraphQL API
- **Requirements**:
  - Standardized Fleeti telemetry format (not provider-specific)
  - Consistent field names and units
  - Historical and real-time access
  - Alerts & notifications

#### 4.1.3 Data Streaming (Future)

- **Purpose**: Additional channel to transmit Fleeti telemetry
- **Formats**: WebSocket, Server-Sent Events (SSE), or message queue
- **Status**: Not yet implemented, but architecture must support it

### 4.2 Display Requirements

- **Live data**: Current telemetry values displayed in real-time
- **Historical data**: Time-series charts for any field (speed over time, fuel consumption, etc.)
- **Conditional display**: Some fields only visible in asset detail view, not on map
- **Customizable markers**: Map markers can display different fields based on configuration

---

## 5. Field Types & Transformation Rules

### 5.1 Direct Mapping Fields

**Description**: Fields that require **no calculation, aggregation, or transformation**

- **Mapping**: Provider field → Fleeti field (1:1)
- **Example**: `lat` (latitude) from provider → `location.latitude` in Fleeti
- **Unit conversion**: May require unit normalization (e.g., `km/h` → `m/s`)

**Rule**: Direct mapping with optional unit conversion

### 5.2 Prioritized Fields

**Description**: Multiple provider fields represent the same Fleeti telemetry concept. We need to **choose the best source** based on priority.

#### Priority Rules

| Fleeti Field | Priority Order | Notes |
|--------------|----------------|-------|
| **Speed** | `can_speed` > `obd_speed` > `speed` (GPS) | CAN most accurate, OBD good, GPS fallback |
| **RPM** | `can_rpm` > `obd_rpm` > `avl_io_85` | CAN most accurate, OBD good, AVL IO fallback |
| **Odometer** | `can_mileage` > `hw_mileage` > `avl_io_105` (GPS) | CAN most accurate, hardware good, GPS fallback |
| **Fuel Level** | `can_fuel_1` > `fuel_level` > `avl_io_86` | CAN most accurate, standard field, AVL IO fallback |
| **Ignition** | `avl_io_898` (SSF) > `can_ignition_state` > `can_engine_state` > `avl_io_239` | Multiple fallback levels, used for status computation (BL priority) |

**Rule**: Use highest priority non-null value available in the packet

### 5.3 Calculated Fields

**Description**: Fields **created based on multiple telemetry fields** or **different conditions**

- **Aggregation**: Combine multiple telemetry values over time
- **Conditions**: Apply logic based on state (e.g., trip status, ignition state)
- **Derivation**: Transform one field into another (e.g., heading → cardinal direction)
- **Lookup**: Resolve values from external catalogs/services
- **Value Change Tracking**: Compare current vs previous values to detect changes and compute `last_changed_at` timestamps

**Examples**:
- `location.cardinal_direction` = Derived from `location.heading` (0-359° → N, NE, E, SE, S, SW, W, NW)
- `power.ev.charging.active` = `cable_plugged = true` AND `traction_battery.level` is increasing over time
- `status.top_status` = Highest-priority status family (Connectivity > Immobilization > Engine > Transit)
- `driver.id.value` = Lookup `hardware_key.value` in Fleeti driver catalog
- `driving_behavior.daily_summary.driving_duration` = Cumulative time when vehicle was moving (aggregated from motion data)
- `location.last_changed_at` = Timestamp when position/heading changed significantly (threshold filters GPS jitter)
- `power.ignition_last_changed_at` = Timestamp when ignition state changed (computed by comparing current vs previous value)

**Rule**: Calculation defined in configuration, executed during normalization

### 5.4 Transformed Fields (Static + Telemetry)

**Description**: Fields that require **static configuration data** combined with telemetry to produce Fleeti telemetry

#### Example: Fuel Level Percentage → Liters

**Scenario**:
- Provider sends: `can_fuel_1 = 75` (percentage)
- Static data: `tank_capacity = 120` (liters) - stored per asset
- Fleeti output: `fuel.level_liters = 90` (calculated: `75% * 120L = 90L`)
- Fleeti output: `fuel.level_percent = 75` (preserved)

**Rule**: Transformation defined in configuration, requires static field reference

#### Static Field Sources

Static fields can come from:
- **Asset configuration**: Vehicle specifications (tank capacity, engine size, etc.)
- **Installation metadata**: I/O wiring configuration (`asset.installation.ignition_input_number`), sensor positions, accessory mappings
- **Customer settings**: Custom thresholds, unit preferences
- **Fleet defaults**: Standard values applied when not overridden

**Rule**: Static fields stored separately, referenced during transformation

#### I/O to Semantic Field Mapping

**Pattern**: Raw I/O fields are mapped to semantic fields based on installation metadata

- **Raw I/O**: `io.inputs.individual.input_1`, `io.outputs.individual.output_2`, `io.analog.input_1`
- **Metadata**: `asset.installation.ignition_input_number`, `asset.installation.immobilizer_output_number`
- **Semantic**: `power.ignition`, `diagnostics.body.doors.*`, `fuel.levels[]`

**Example**: `io.inputs.individual.input_1` + `asset.installation.ignition_input_number = 1` → `power.ignition`

**Bitmask extraction**: Some I/O fields come as bitmasks (`din`, `outputs`) requiring bit extraction (e.g., `din` bit 0 → `input_1`)

**Rule**: I/O semantic mapping defined in installation metadata, transformation pipeline applies mapping during normalization

### 5.5 Asset Metadata Integration

**Description**: Fields that combine **asset metadata** with **telemetry data** to produce enriched Fleeti telemetry

- **Sensor Identity**: `asset.accessories[].sensors[]` (metadata) + `sensors.environment[].temperature` (telemetry) → Combined sensor object with identity + readings
- **Driver Identification**: `driver.hardware_key.value` (telemetry) → Lookup in Fleeti driver catalog → `driver.id.value`, `driver.name`
- **Geofence Context**: `location.lat`/`lng` (telemetry) + Geofence Service → `geofences[]` array

**Rule**: Asset metadata integration performed during normalization, unknown lookups result in `null` values

### 5.6 Field Priority and Visibility

**Description**: Fields are assigned priorities (P0-P3, T, BL, ?) that determine implementation order and visibility

- **P0-P3**: Implementation priorities (P0 = core, P3 = low priority) - Customer-facing, displayed in UI/APIs
- **T (Troubleshooting)**: Available via API for super admin users, not displayed to customers
- **BL (Business Logic)**: Used internally for computation (e.g., `power.ignition` for status computation), not exposed to customers
- **? (Unknown)**: Priority/usage to be determined

### 5.7 Mixed Field Types

**Important**: Fleeti telemetry will be a **mix of device telemetry and calculated fields**. Both are considered "Fleeti telemetry" even though calculated fields are not directly from the device.

**Example packet mix**:
- Direct mapping: `location.latitude` (from provider)
- Prioritized: `motion.speed` (best source selected)
- Calculated: `location.cardinal_direction` (derived)
- I/O mapped: `power.ignition` (from I/O + installation metadata)
- Asset integrated: `sensors.environment[]` (telemetry + asset metadata)

---

## 6. Storage Strategy

⚠️ **Note**: Storage strategy details are under review. See [Architecture Overview](../../overview-vision/architecture-overview.md) for current information.

The telemetry system must store data in **three tiers** to balance performance, cost, and data preservation:

1. **Fast Access (Hot)** - Core fields for real-time map updates (< 100ms latency)
2. **Complete Data (Warm)** - All fields for detail views and API access (< 500ms latency)
3. **Raw Archive (Cold)** - Original provider packets for historical recalculation (permanent retention)

### 6.1 Storage Tiers

#### Fast Access Storage (Hot)

- **Stored**: ~25-30 core fields (location, speed, ignition, basic vehicle state)
- **Performance**: < 100ms query latency for current asset state
- **Use Cases**: Map display, live tracking, real-time updates
- **Retention**: Last 30 days

#### Complete Data Storage (Warm)

- **Stored**: All Fleeti telemetry fields (core + extended)
- **Performance**: < 500ms load time for asset detail view, < 2 seconds for 1-month historical query
- **Use Cases**: Asset detail views, customer API, historical analysis
- **Retention**: 1-5 years

#### Raw Archive Storage (Cold)

- **Stored**: All raw provider telemetry packets (original format, permanent retention)
- **Performance**: On-demand access (seconds to minutes acceptable for archive restore)
- **Use Cases**: Historical recalculation when new fields are added, troubleshooting, debugging
- **Retention**: Permanent

### 6.2 Historical Recalculation

**Product Need**: When new Fleeti telemetry fields are added, customers must have complete historical data for those fields.

**Capability Required**:
- System must be able to scan all historical raw packets
- System must apply new transformation rules to old data
- System must update Complete Data Storage with newly calculated fields
- Customers see complete historical data for new fields (no gaps)

**Requirement**: Raw archive storage must be permanent/very long-term to enable historical recalculation.

---

## 7. Configuration System

### 7.1 Configuration Philosophy

**Critical requirement**: We must **avoid hardcoding** transformation rules. Instead, use **configuration files** (YAML) to define:

- Field mappings (direct, prioritized, calculated, transformed)
- Priority rules (source selection when multiple provider fields available)
- Calculation formulas (derived fields, aggregations)
- Static field transformations (combining telemetry with asset metadata)
- I/O to semantic field mappings (with default fallbacks)

**Rationale**: When a customer requests a different configuration (e.g., use OBD speed instead of CAN speed), we must handle it gracefully without code changes.

### 7.2 Configuration Hierarchy

Configuration can be associated at multiple levels:

1. **Default/Global**: Base configuration for all assets
2. **Customer-level**: Override default configuration for a specific customer
3. **Asset Group**: Override customer configuration for a group of assets
4. **Single Asset**: Override group configuration for a specific asset

**Example**:
```
Default Config: speed = can_speed > obd_speed > gps_speed
Customer A Config: speed = obd_speed > gps_speed (CAN not available)
Asset Group "Fleet B": speed = gps_speed (OBD unreliable)
Asset "Truck-123": speed = can_speed (highest priority, manually set)
```

**Rule**: Lower-level configurations override higher-level configurations

### 7.3 Configuration Scope & Boundaries

**What's configured here**:
- Provider field → Fleeti field mappings
- Priority rules for field selection
- Calculation formulas
- I/O to semantic field mappings (with default fallbacks)
- Static field transformations (references to asset metadata)

**What's NOT configured here** (stored in Asset Service):
- Installation metadata (`asset.installation.ignition_input_number`, `asset.installation.immobilizer_output_number`)
- Asset specifications (tank capacity, engine size, etc.)
- Accessory configurations (`asset.accessories[]`)

**Integration**: Transformation pipeline accesses Asset Service to retrieve installation metadata and asset specifications when needed for field computation.

### 7.4 Configuration File Structure (YAML Examples)

```yaml
# Direct mapping
mappings:
  location.latitude:
    source: "lat"
    unit: "degrees"
  
  # Prioritized field (multiple sources)
  motion.speed:
    sources:
      - priority: 1
        field: "can_speed"
      - priority: 2
        field: "obd_speed"
      - priority: 3
        field: "speed"
  
  # Calculated field
  location.cardinal_direction:
    calculation: "derive_from_heading(location.heading)"
    depends_on: ["location.heading"]
  
  # Transformed field (static + telemetry)
  fuel.level_liters:
    source: "fuel.level_percent"
    transformation: "(fuel.level_percent / 100) * static.tank_capacity_liters"
    depends_on: ["fuel.level_percent", "static.tank_capacity_liters"]
  
  # I/O to semantic mapping (with default fallback)
  power.ignition:
    io_mapping:
      default_source: "io.inputs.individual.input_1"
      installation_metadata: "asset.installation.ignition_input_number"
      bitmask_extraction: "din"
```

---

## 8. Field Documentation & Watchdog

### 8.1 Field Documentation Requirement

**Objective**: Create a **complete catalog** of all possible Fleeti telemetry fields we can produce.

**Current state**: `docs/reference/navixy-field-catalog.csv` contains 343 fields from Navixy, but we need:

1. **Fleeti Telemetry Fields Catalog**: All possible Fleeti fields (not provider fields)
2. **Mapping documentation**: Which provider fields map to which Fleeti fields
3. **Transformation rules**: How each Fleeti field is calculated/derived
4. **Field metadata**: Units, ranges, descriptions, use cases

### 8.2 New Field Detection Watchdog

**Requirement**: System must detect when a **new field appears** in provider telemetry that we haven't seen before (non-zero value).

**Watchdog functionality**:
- Monitor incoming telemetry packets
- Flag any field with non-zero value that:
  - Is not in our field catalog, OR
  - Is in catalog but has no mapping rule configured
- Alert/notification when new field detected
- Log new field with sample values for analysis

**Purpose**: Ensure we don't miss new telemetry capabilities and can document/incorporate them

---

## 9. Prioritization & Scope

### 9.1 Field Prioritization Strategy

**Approach**: Build the **most exhaustive yet readable** telemetry object possible, then reduce by priority.

#### Priority Levels

1. **Core (P0)**: Essential for basic functionality
   - Location (lat, lng, speed, heading)
   - Vehicle state (ignition, engine_rpm)
   - Critical events (crash, SOS)

2. **High (P1)**: Important for fleet management
   - Fuel metrics
   - Driving behavior (harsh braking, acceleration)
   - Odometer, engine hours

3. **Medium (P2)**: Useful for detailed analysis
   - Sensor data (temperature, humidity)
   - IO states (digital inputs/outputs)
   - Device health metrics

4. **Low (P3)**: Specialized or rarely used
   - Out-of-scope fields (axis_x/y/z)
   - Provider-specific diagnostic fields
   - Future fields not yet prioritized

### 9.2 Readability vs Completeness

**Balance**: 
- **Exhaustive**: Document and store everything (343+ fields)
- **Readable**: Core schema is clean and easy to understand (~50 fields)
- **Flexible**: Extended fields available when needed

**Result**: 
- Core telemetry = Clean, fast, 90% of use cases
- Extended telemetry = Complete, available, 100% of data

---

## 10. Implementation Considerations

### 10.1 Initial Implementation Strategy

**Phase 1: Default Configuration**
- Start with **single default configuration** for all assets
- Map all 343 Navixy fields to Fleeti telemetry
- Implement priority rules, calculations, transformations
- Store raw + core + extended

**Phase 2: Configuration Flexibility**
- Add customer-level configuration override
- Add asset group configuration
- Add asset-level configuration
- Configuration UI/API for management

**Phase 3: Multi-Provider Support**
- Abstract provider-specific parsers
- Add OEM provider integration
- Unified Fleeti telemetry output regardless of source

### 10.2 Key Architectural Decisions Needed

1. **Storage backend**: PostgreSQL vs TimescaleDB vs hybrid?
2. **Real-time processing**: Stream processing (Kafka) vs batch vs event-driven?
3. **API design**: REST vs GraphQL vs both?
4. **Configuration storage**: Database vs file system vs config service?
5. **Recalculation strategy**: Batch job vs on-demand vs incremental?

### 10.3 Open Questions

1. **Static fields storage**: Where are asset specifications (tank capacity, etc.) stored? Asset service? Separate config DB?
2. **Customer configuration management**: Who creates/manages customer-specific configurations? Product team? Customers themselves?
3. **Field versioning**: How to handle field schema changes over time? Migration strategy?
4. **Provider field evolution**: How to handle when provider adds new fields? Auto-detect and flag?
5. **Performance**: Expected telemetry volume? Messages per second per device? Total devices?

---

## 11. Success Criteria

### 11.1 Functional Requirements

- ✅ Receive telemetry from Navixy via Data Forwarding
- ✅ Store all raw telemetry permanently (cold storage)
- ✅ Transform to Fleeti telemetry using configuration
- ✅ Store core telemetry for fast queries
- ✅ Store extended telemetry for complete data
- ✅ Expose Fleeti telemetry via API
- ✅ Display in Fleeti One (live + historical)
- ✅ Detect and flag new provider fields
- ✅ Support customer/asset-level configuration

### 11.2 Non-Functional Requirements

- ✅ Provider-agnostic architecture
- ✅ Configuration-driven (no hardcoding)
- ✅ Scalable to multiple providers
- ✅ Historical recalculation capability
- ✅ Complete field documentation
- ✅ Fast query performance (core fields)
- ✅ Complete data preservation

---

## 12. Frontend Integration Insights

### 12.1 Frontend Structure Requirements

Based on `Wiki/telemetry-status-rules.md`, the frontend expects a specific structure that differs from raw provider telemetry:

**Key Transformations Needed**:
1. **Sensor Array Creation**: Raw telemetry fields must be organized into `sensors[]` array
2. **Status Computation**: Raw telemetry → computed status families
3. **Asset Type Mapping**: Provider doesn't have asset types - these come from Fleeti asset service
4. **Trip Computation**: Ongoing trip data must be computed from location/time series

### 12.2 Transformation Layers

```
Raw Provider Telemetry
    ↓
[Provider Parser] (Navixy, OEM, etc.)
    ↓
Provider-Agnostic Telemetry (343+ fields)
    ↓
[Fleeti Transformation Engine]
    ├── Status Computation
    ├── Sensor Array Creation
    ├── Counter Aggregation
    ├── Trip Detection
    └── Static Field Transformation
    ↓
Fleeti Telemetry (Frontend Structure)
    ├── Core Fields (fast queries)
    └── Extended Fields (all data)
    ↓
[API Layer]
    ↓
Fleeti One Frontend / Customer APIs
```

---

## 13. Next Steps

### 13.1 Immediate Actions

1. **Review this specification** and provide feedback
2. **Answer open questions** (Section 10.3)
3. **Define core field schema** (~50 fields) - aligned with frontend requirements
4. **Create field mapping configuration** (YAML) for all 343 Navixy fields
5. **Design database schema** (raw, core, extended tables)
6. **Prototype transformation pipeline** - must output frontend-compatible structure

### 13.2 Documentation Tasks

1. Create **Fleeti Telemetry Fields Catalog** (separate from provider fields)
2. Document **transformation rules** for calculated fields
3. Create **configuration file template** with all mappings
4. Design **watchdog system** for new field detection
5. **Map frontend structure** to Fleeti telemetry schema

### 13.3 Integration Tasks

1. **Status computation engine**: Transform raw telemetry → status families
2. **Sensor aggregation logic**: Organize raw fields into `sensors[]` array
3. **Trip detection algorithm**: Compute ongoing trips from telemetry
4. **Asset type resolver**: Link telemetry to Fleeti asset metadata

---

## 14. References

### Internal Documents

- `docs/reference/navixy-field-catalog.csv` - Complete catalog of 343 Navixy fields from Data Forwarding
- `working/fleeti-telemetry-schema-specification.md` - Working analysis of Fleeti telemetry structure
- `Wiki/telemetry-status-rules.md` - Canonical status computation logic for LiveMap and API outputs

### External References

- Navixy Data Forwarding documentation
- Teltonika AVL protocol specification
- Fleeti One mobile app specifications (LiveMap module)

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-XX  
**Status**: ✅ Validated  
**Source**: `Wiki/telemetry-system-specification.md`






