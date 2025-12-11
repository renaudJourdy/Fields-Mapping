# Mapping Rules

**Status:** ✅ Validated  
**Source:** `Wiki/telemetry-system-specification.md` Sections 5, 7

Field mapping types, priority rules, and transformation logic for converting provider telemetry to Fleeti format.

---

## Overview

Mapping rules define how provider telemetry fields are transformed into Fleeti telemetry format. The transformation system supports multiple mapping types to handle the complexity of aggregating data from different providers.

---

## Field Mapping Types

### 1. Direct Mapping Fields

**Description**: Fields that require **no calculation, aggregation, or transformation**

**Mapping Pattern**: Provider field → Fleeti field (1:1)

**Example**:
- Provider: `lat` (latitude)
- Fleeti: `location.latitude`
- Unit conversion: May require unit normalization (e.g., `km/h` → `m/s`)

**Rule**: Direct mapping with optional unit conversion

**Configuration Example**:
```yaml
mappings:
  location.latitude:
    source: "lat"
    unit: "degrees"
```

---

### 2. Prioritized Fields

**Description**: Multiple provider fields represent the same Fleeti telemetry concept. We need to **choose the best source** based on priority.

**Mapping Pattern**: Select highest priority non-null value from multiple sources

**Priority Rules**:

| Fleeti Field | Priority Order | Notes |
|--------------|----------------|-------|
| **Speed** | `can_speed` > `obd_speed` > `speed` (GPS) | CAN most accurate, OBD good, GPS fallback |
| **RPM** | `can_rpm` > `obd_rpm` > `avl_io_85` | CAN most accurate, OBD good, AVL IO fallback |
| **Odometer** | `can_mileage` > `hw_mileage` > `avl_io_105` (GPS) | CAN most accurate, hardware good, GPS fallback |
| **Fuel Level** | `can_fuel_1` > `fuel_level` > `avl_io_86` | CAN most accurate, standard field, AVL IO fallback |
| **Ignition** | `avl_io_898` (SSF) > `can_ignition_state` > `can_engine_state` > `avl_io_239` | Multiple fallback levels, used for status computation (BL priority) |

**Rule**: Use highest priority non-null value available in the packet

**Configuration Example**:
```yaml
mappings:
  motion.speed:
    sources:
      - priority: 1
        field: "can_speed"
      - priority: 2
        field: "obd_speed"
      - priority: 3
        field: "speed"
```

---

### 3. Calculated Fields

**Description**: Fields **created based on multiple telemetry fields** or **different conditions**

**Calculation Types**:
- **Aggregation**: Combine multiple telemetry values over time
- **Derivation**: Transform one field into another (e.g., heading → cardinal direction)
- **Conditions**: Apply logic based on state (e.g., trip status, ignition state)
- **Lookup**: Resolve values from external catalogs/services
- **Value Change Tracking**: Compare current vs previous values to detect changes

**Examples**:
- `location.cardinal_direction` = Derived from `location.heading` (0-359° → N, NE, E, SE, S, SW, W, NW)
- `power.ev.charging.active` = `cable_plugged = true` AND `traction_battery.level` is increasing over time
- `status.top_status` = Highest-priority status family (Connectivity > Immobilization > Engine > Transit)
- `driver.id.value` = Lookup `hardware_key.value` in Fleeti driver catalog
- `location.last_changed_at` = Timestamp when position/heading changed significantly (threshold filters GPS jitter)

**Rule**: Calculation defined in configuration, executed during normalization

**Configuration Example**:
```yaml
mappings:
  location.cardinal_direction:
    calculation: "derive_from_heading(location.heading)"
    depends_on: ["location.heading"]
```

---

### 4. Transformed Fields (Static + Telemetry)

**Description**: Fields that require **static configuration data** combined with telemetry to produce Fleeti telemetry

**Transformation Pattern**: Telemetry field + Static asset metadata → Fleeti field

**Example: Fuel Level Percentage → Liters**

**Scenario**:
- Provider sends: `can_fuel_1 = 75` (percentage)
- Static data: `tank_capacity = 120` (liters) - stored per asset in Asset Service
- Fleeti output: `fuel.level_liters = 90` (calculated: `75% * 120L = 90L`)
- Fleeti output: `fuel.level_percent = 75` (preserved)

**Static Field Sources**:
- **Asset configuration**: Vehicle specifications (tank capacity, engine size, etc.)
- **Installation metadata**: I/O wiring configuration, sensor positions, accessory mappings
- **Customer settings**: Custom thresholds, unit preferences
- **Fleet defaults**: Standard values applied when not overridden

**Rule**: Transformation defined in configuration, requires static field reference

**Configuration Example**:
```yaml
mappings:
  fuel.level_liters:
    source: "fuel.level_percent"
    transformation: "(fuel.level_percent / 100) * static.tank_capacity_liters"
    depends_on: ["fuel.level_percent", "static.tank_capacity_liters"]
```

---

### 5. I/O to Semantic Field Mapping

**Description**: Raw I/O fields mapped to semantic fields based on installation metadata

**Mapping Pattern**: Raw I/O + Installation Metadata → Semantic Field

**Example**:
- Raw I/O: `io.inputs.individual.input_1`
- Metadata: `asset.installation.ignition_input_number = 1`
- Semantic: `power.ignition`

**Bitmask Extraction**: Some I/O fields come as bitmasks (`din`, `outputs`) requiring bit extraction (e.g., `din` bit 0 → `input_1`)

**Rule**: I/O semantic mapping defined in installation metadata, transformation pipeline applies mapping during normalization

**Configuration Example**:
```yaml
mappings:
  power.ignition:
    io_mapping:
      default_source: "io.inputs.individual.input_1"  # Fallback if installation metadata unavailable
      installation_metadata_field: "asset.installation.ignition_input_number"  # Override from Asset Service
      bitmask_extraction: "din"  # If only bitmask available, extract bit 0
```

---

## Configuration System

### Configuration Philosophy

**Critical requirement**: We must **avoid hardcoding** transformation rules. Instead, use **configuration files** (YAML) to define:

- Field mappings (direct, prioritized, calculated, transformed)
- Priority rules (source selection when multiple provider fields available)
- Calculation formulas (derived fields, aggregations)
- Static field transformations (combining telemetry with asset metadata)
- I/O to semantic field mappings (with default fallbacks)

**Rationale**: When a customer requests a different configuration (e.g., use OBD speed instead of CAN speed), we must handle it gracefully without code changes.

### Configuration Hierarchy

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

### Configuration Scope

**What's configured here**:
- Provider field → Fleeti field mappings
- Priority rules for field selection
- Calculation formulas
- I/O to semantic field mappings (with default fallbacks)
- Static field transformations (references to asset metadata)

**What's NOT configured here** (stored in Asset Service):
- Installation metadata (`asset.installation.ignition_input_number`, etc.)
- Asset specifications (tank capacity, engine size, etc.)
- Accessory configurations (`asset.accessories[]`)

**Integration**: Transformation pipeline accesses Asset Service to retrieve installation metadata and asset specifications when needed for field computation.

---

## Transformation Pipeline

### Transformation Process

1. **Receive**: Provider telemetry packet
2. **Parse**: Convert to provider-agnostic structure
3. **Load Configuration**: Retrieve applicable configuration (hierarchy)
4. **Transform**: Apply field mappings, priority rules, calculations
5. **Compute Status**: Calculate status families
6. **Output**: Fleeti telemetry format

### Transformation Order

1. **Direct Mappings**: Apply 1:1 mappings with unit conversion
2. **Priority Rules**: Select best source for prioritized fields
3. **I/O Mapping**: Map raw I/O to semantic fields using installation metadata
4. **Calculations**: Derive calculated fields from existing data
5. **Transformations**: Apply static field transformations
6. **Status Computation**: Compute status families
7. **Asset Integration**: Combine with asset metadata (sensors, driver, geofences)

---

## Related Documentation

- **[Fleeti Fields Catalog](./fleeti-fields-catalog.md)**: Complete Fleeti telemetry fields
- **[Provider Fields Catalog](./provider-fields-catalog.md)**: Provider field overview
- **[Telemetry System Specification](../specifications/telemetry-system-specification.md)**: Complete system specification
- **[Configuration System](../specifications/telemetry-system-specification.md#7-configuration-system)**: Detailed configuration documentation

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-XX  
**Status**: ✅ Validated  
**Source**: `Wiki/telemetry-system-specification.md` Sections 5, 7






