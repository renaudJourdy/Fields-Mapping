# Telemetry System Specification

> Comprehensive specification for creating a provider-agnostic Fleeti Telemetry system from multi-provider raw telemetry data

---

## 📋 Table of Contents

1. [Context & Background](#context--background)
2. [Objectives & Vision](#objectives--vision)
3. [Telemetry Sources](#telemetry-sources)
4. [How Telemetry Will Be Used](#how-telemetry-will-be-used)
5. [Field Types & Transformation Rules](#field-types--transformation-rules)
6. [Storage Strategy](#storage-strategy)
7. [Configuration System](#configuration-system)
8. [Field Documentation & Watchdog](#field-documentation--watchdog)
9. [Prioritization & Scope](#prioritization--scope)
10. [Implementation Considerations](#implementation-considerations)
11. [Success Criteria](#success-criteria)
12. [Frontend Integration Insights](#frontend-integration-insights)
13. [Next Steps](#next-steps)
14. [References](#references)
15. [Document History](#document-history)

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

- **Received all telemetry** from test devices
- **Validated data integrity**: Compared Data Forwarding packets with Navixy API exports
- **Field catalog created**: Aggregated all unique telemetry fields found in `docs/reference/Navixy Field Catalog.csv`
- **Result**: 343 distinct telemetry fields identified from Navixy Data Forwarding

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
- **Fields**: 343 identified fields (see `docs/reference/Navixy Field Catalog.csv`)
- **Protocol**: Teltonika AVL `#D#` packets (forwarded as JSON)

### 3.2 Future Providers

#### 3.2.1 OEM Direct Integration

- **Source**: Vehicle/machine manufacturers
- **Connection**: Direct OEM integration via credentials
- **Format**: Provider-specific telemetry format (TBD)
- **Example**: Manufacturer-provided API or data stream

#### 3.2.2 Other Providers

- **Unknown providers**: System must handle providers not yet identified
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
  - **Map markers**: Location-based display (with optional field-based coloring, e.g., temperature on marker)

**Frontend Structure Reference**: Refer to `docs/reference/Telemetry Status Rules.md` for definitive status compatibility/state logic and extend `docs/working/Telemetry Schema Analysis.md` to mirror the LiveMap mobile contract until the legacy LiveMap mapping doc is migrated from the previous project. The frontend expects a specific structure with:
- `asset_id`, `asset_type`, `asset_subtype`, `name` - Identity fields
- `status` object with `top_status`, `statuses[]` array (families: connectivity, immobilization, engine, movement)
- `location` object with `lat`, `lng`, `heading`, `geofences[]`
- `sensors[]` array - All sensor readings (temperature, humidity, CAN data, etc.)
- `counters` object - Odometer, engine_hours, fuel (if not a sensor)
- `immobilizer` object - State if asset supports immobilization
- `trip` object - Ongoing trip information (nullable)

**Important Frontend Patterns**:
- **Sensors vs Counters**: Fuel can be either a sensor OR a counter, **never both**
- **CAN Data**: CAN readings are treated as sensors with `type` prefixed with `"can_"` (e.g., `"can_rpm"`, `"can_coolant_temperature"`)
- **Multiple Sensors**: Each sensor reading is a separate entry in `sensors[]` array, even if from the same physical accessory
- **Accessory Grouping**: Sensors from same accessory use same `accessory_id` and `label` to allow frontend grouping
- **Value + Unit Structure**: Many fields use `{ "value": number, "unit": "string" }` format

#### 4.1.2 Customer APIs

- **Purpose**: Expose Fleeti telemetry to customers via REST/GraphQL API
- **Requirements**:
  - Standardized Fleeti telemetry format (not provider-specific)
  - Consistent field names and units
  - Historical and real-time access

#### 4.1.3 Data Streaming (Future)

- **Purpose**: Additional channel to transmit Fleeti telemetry
- **Formats**: WebSocket, Server-Sent Events (SSE), or message queue (Kafka/RabbitMQ)
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

#### 5.2.1 Priority Rules

| Fleeti Field | Priority Order | Notes |
|--------------|----------------|-------|
| **Speed** | `can_speed` > `obd_speed` > `speed` (GPS) | CAN most accurate, OBD good, GPS fallback |
| **RPM** | `can_rpm` > `obd_rpm` > `avl_io_85` | CAN most accurate, OBD good, AVL IO fallback |
| **Odometer** | `can_mileage` > `hw_mileage` > `avl_io_105` (GPS) | CAN most accurate, hardware good, GPS fallback |
| **Fuel Level** | `can_fuel_1` > `fuel_level` > `avl_io_86` | CAN most accurate, standard field, AVL IO fallback |

**Rule**: Use highest priority non-null value available in the packet

### 5.3 Calculated Fields

**Description**: Fields **created based on multiple telemetry fields** or **different conditions**

- **Aggregation**: Combine multiple telemetry values
- **Conditions**: Apply logic based on state (e.g., trip status, ignition state)
- **Example**: 
  - Average speed during trip = `sum(speed * time) / total_time`
  - Fuel consumption rate = `fuel_used / distance_traveled`

**Rule**: Calculation defined in configuration, executed during normalization

### 5.4 Transformed Fields (Static + Telemetry)

**Description**: Fields that require **static configuration data** combined with telemetry to produce Fleeti telemetry

#### 5.4.1 Example: Fuel Level Percentage → Liters

**Scenario**:
- Provider sends: `can_fuel_1 = 75` (percentage)
- Static data: `tank_capacity = 120` (liters) - stored per asset
- Fleeti output: `fuel.level_liters = 90` (calculated: `75% * 120L = 90L`)
- Fleeti output: `fuel.level_percent = 75` (preserved)

**Rule**: Transformation defined in configuration, requires static field reference

#### 5.4.2 Frontend Output Considerations

**Important**: Based on the LiveMap requirements captured in `docs/reference/Telemetry Status Rules.md` (and the legacy LiveMap mapping doc to be migrated):

- **Fuel Display**: Fuel can appear as either:
  - **Sensor**: `sensors[]` array entry with `type: "fuel"` or `type: "can_fuel_level_litre"`
  - **Counter**: `counters.fuel` with `{ value, unit }` structure
  - **Rule**: Never both - choose based on how it's tracked (real-time reading vs cumulative counter)

- **CAN Data Display**: CAN readings are sensors with `type` prefixed with `"can_"`:
  - `can_rpm`, `can_coolant_temperature`, `can_speed`, `can_mileage`, etc.
  - Each CAN reading is a separate sensor entry
  - Frontend groups by `accessory_id` if needed

- **Status Computation**: `status.top_status` and `status.statuses[]` are computed fields:
  - Derived from raw telemetry (ignition → engine status, speed → movement status, etc.)
  - Priority order: Connectivity > Immobilization > Engine > Movement
  - Backend computes these from raw telemetry values

#### 5.4.2 Static Field Sources

Static fields can come from:
- **Asset configuration**: Vehicle specifications (tank capacity, engine size, etc.)
- **Customer settings**: Custom thresholds, unit preferences
- **Fleet defaults**: Standard values applied when not overridden

**Rule**: Static fields stored separately, referenced during transformation

### 5.5 Mixed Field Types

**Important**: Fleeti telemetry will be a **mix of device telemetry and calculated fields**. Both are considered "Fleeti telemetry" even though calculated fields are not directly from the device.

---

## 6. Storage Strategy

### 6.1 Multi-Layer Storage Architecture

#### 6.1.1 Layer 1: Raw Storage (Cold Storage)

**Purpose**: Preserve **all raw telemetry** from providers for historical recalculation

- **Storage**: Raw packets stored in cold storage (S3, Azure Blob, or similar)
- **Format**: Original provider format (JSON packets, binary, etc.)
- **Retention**: Long-term (permanent or very long retention)
- **Access**: On-demand for recalculation, debugging, validation

**Rationale**: When a new Fleeti telemetry field is added, we need to recalculate all historical data. Raw storage enables this.

#### 6.1.2 Layer 2: Core Telemetry (Hot Storage)

**Purpose**: Store **essential, frequently-accessed** Fleeti telemetry fields

- **Storage**: Relational database (PostgreSQL) or time-series DB (TimescaleDB)
- **Fields**: ~50 core fields (location, speed, ignition, basic vehicle state)
- **Optimization**: Indexed, query-optimized schema
- **Use case**: 90% of queries (map display, live tracking, basic analytics)

**Fields included**:
- Core location (lat, lng, speed, heading)
- Vehicle state (ignition, engine_rpm, odometer)
- Basic events (crash, towing, SOS)
- Fuel (level, rate) - if available
- Device health (battery, signal)

#### 6.1.3 Layer 3: Extended Telemetry (Warm Storage)

**Purpose**: Store **all other telemetry fields** not in core, but queryable on-demand

- **Storage**: JSONB column in PostgreSQL or separate document store
- **Fields**: All 343+ fields (and future fields) preserved
- **Access**: Queryable for detailed views, asset details, historical analysis
- **Linkage**: Foreign key to core telemetry record

**Use case**: When user clicks "Asset Details" or requests specific field history

### 6.2 Interpretation Layer

**Concept**: Raw records are stored, but we need **some kind of interpretation** (normalization/transformation) for consumption.

- **Raw → Core**: Transform provider fields to Fleeti core schema
- **Raw → Extended**: Store all provider fields in extended storage
- **Transformation**: Apply configuration rules (priority, calculation, static field transformation)

### 6.3 Historical Recalculation

**Scenario**: New Fleeti telemetry field is added (e.g., `fuel_economy_trip`)

**Process**:
1. Define new field calculation rule in configuration
2. Scan raw storage for all historical packets
3. Apply calculation rule to each historical packet
4. Update core/extended storage with new field values
5. Customer now has complete history of new field

**Requirement**: Raw storage must be permanent/very long-term to enable this

---

## 7. Configuration System

### 7.1 Configuration Philosophy

**Critical requirement**: We must **avoid hardcoding** transformation rules. Instead, use **configuration files** (YAML) to define:

- Field mappings
- Priority rules
- Calculation formulas
- Static field transformations

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

### 7.3 Configuration File Structure (YAML)

```yaml
# Default configuration (fleeti_telemetry_default.yaml)
version: "1.0"
provider: "navixy"

mappings:
  # Direct mapping
  location.latitude:
    source: "lat"
    unit: "degrees"
    required: true
  
  # Prioritized field
  vehicle.speed:
    sources:
      - priority: 1
        field: "params.can_speed"
        multiplier: 0.00390625
        unit: "km/h"
      - priority: 2
        field: "params.obd_speed"
        unit: "km/h"
      - priority: 3
        field: "speed"
        unit: "km/h"
    target: "vehicle.speed"
    default_unit: "km/h"
  
  # Calculated field
  driving.fuel_economy_trip:
    calculation: |
      IF trip_active AND distance > 0:
        fuel_consumed / distance * 100
      ELSE:
        null
    depends_on:
      - fuel.fuel_consumed_trip
      - trip.distance
      - trip.status
  
  # Transformed field (static + telemetry)
  fuel.level_liters:
    source: "fuel.level_percent"
    transformation: |
      IF static.tank_capacity_liters IS NOT NULL:
        (fuel.level_percent / 100) * static.tank_capacity_liters
      ELSE:
        null
    depends_on:
      - fuel.level_percent
      - static.tank_capacity_liters
    unit: "L"

# Sentinel values
sentinels:
  - field: "params.mn_code"
    value: -1
    treat_as: null
    meaning: "Unknown MCC/MNC"
  
  - field: "params.avl_io_388"
    value: -1
    treat_as: null
    meaning: "Invalid humidity reading"

# Field groups
field_groups:
  core:
    - location.*
    - vehicle.speed
    - vehicle.ignition
    - events.*
  
  extended:
    - vehicle.*
    - fuel.*
    - sensors.*
  
  out_of_scope:
    - axis_x
    - axis_y
    - axis_z
    - autopilot_status
```

### 7.4 Configuration Runtime

- **Default config**: Loaded at startup, used for all assets unless overridden
- **Customer config**: Loaded on-demand when processing customer's assets
- **Asset config**: Loaded when processing specific asset
- **Merging**: Lower-level configs merge with/override parent configs

---

## 8. Field Documentation & Watchdog

### 8.1 Field Documentation Requirement

**Objective**: Create a **complete catalog** of all possible Fleeti telemetry fields we can produce.

**Current state**: `docs/reference/Navixy Field Catalog.csv` contains 343 fields from Navixy, but we need:

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

### 8.3 Field Catalog Structure

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

Each field should document:
- **Name**: Fleeti field name
- **Type**: direct / prioritized / calculated / transformed
- **Sources**: Provider fields that contribute
- **Unit**: Standard unit in Fleeti
- **Range**: Valid value range
- **Description**: What it represents
- **Use cases**: Where it's displayed/used
- **Priority**: Core / Extended / Optional

---

## 9. Prioritization & Scope

### 9.1 Field Prioritization Strategy

**Approach**: Build the **most exhaustive yet readable** telemetry object possible, then reduce by priority.

#### 9.1.1 Priority Levels

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

#### 9.1.2 Out-of-Scope Fields

Some fields should be **set aside** initially:

- `axis_x`, `axis_y`, `axis_z`: Raw accelerometer data (not needed if we have processed acceleration)
- `autopilot_status`: Not relevant for current use cases
- `potentiometer_*`: Specialized sensor, low priority

**Rule**: Store in extended fields but don't include in core schema or default mappings

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

Based on `docs/reference/Telemetry Status Rules.md` (and the legacy LiveMap contract still to be migrated), the frontend expects a specific structure that differs from raw provider telemetry:

**Key Transformations Needed**:
1. **Sensor Array Creation**: Raw telemetry fields must be organized into `sensors[]` array
   - CAN readings → `{ type: "can_rpm", ... }` sensor entries
   - Temperature/humidity → separate sensor entries with same `accessory_id`
   - Fuel can be sensor OR counter, not both

2. **Status Computation**: Raw telemetry → computed status families
   - `ignition` (on/off) → `status.statuses[]` with `{ family: "engine", code: "running" }`
   - `moving` (0/1) → `status.statuses[]` with `{ family: "movement", code: "in_transit" }`
   - `top_status` → computed from status families with priority rules

3. **Asset Type Mapping**: Provider doesn't have asset types - these come from Fleeti asset service
   - `asset_type`: 10=Vehicle, 20=Equipment, 30=Site, 40=Phone
   - `asset_subtype`: Depends on asset type enum

4. **Trip Computation**: Ongoing trip data must be computed from location/time series
   - Not present in raw telemetry packets
   - Derived from location history, ignition events, movement patterns

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
5. **Map frontend structure** to Fleeti telemetry schema (align with the LiveMap contract documented in `docs/reference/Telemetry Status Rules.md`; import the legacy LiveMap spec when available)

### 13.3 Integration Tasks

1. **Status computation engine**: Transform raw telemetry → status families
2. **Sensor aggregation logic**: Organize raw fields into `sensors[]` array
3. **Trip detection algorithm**: Compute ongoing trips from telemetry
4. **Asset type resolver**: Link telemetry to Fleeti asset metadata

---

## 14. References

### Internal Documents
- `docs/reference/Navixy Field Catalog.csv` - Complete catalog of 343 Navixy fields from Data Forwarding
- `docs/working/Telemetry Schema Analysis.md` - Working analysis of Fleeti telemetry structure
- `docs/reference/Telemetry Status Rules.md` - Canonical status computation logic for LiveMap and API outputs

### Related Specifications
- Legacy documents from the previous project (e.g., `Specifications/Data Model & Mapping.md`, `Specifications/Architecture & Data Flow.md`, validator scripts) remain in the old repository and should be migrated or recreated as needed.

### External References
- Navixy Data Forwarding documentation
- Teltonika AVL protocol specification
- Fleeti One mobile app specifications (LiveMap module)

---

## 15. Document History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-01-XX | Initial specification based on POC and requirements | Product Owner |

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-XX  
**Author**: Product Owner  
**Status**: Draft - Pending Review  
**Related Documents**: See References section above

