# Provider Fields Catalog

**Status:** ✅ Validated  
**Source:** `Wiki/telemetry-system-specification.md` Section 3

Overview of provider telemetry fields from Navixy and future providers.

---

## Overview

The Provider Fields Catalog documents telemetry fields available from different providers. Currently, we have comprehensive documentation for Navixy fields, with support for future providers planned.

---

## Current Provider: Navixy

### Navixy Overview

- **Source**: White-label GPS tracking platform
- **Format**: Raw parsed telemetry packets via Data Forwarding
- **Fields Identified**: ~340 distinct telemetry fields
- **Catalog Location**: `docs/reference/navixy-field-catalog.csv`

### Navixy Field Categories

Navixy fields are organized into several categories:

- **Location Fields**: GPS coordinates, heading, altitude, precision metrics
- **CAN Bus Fields**: Vehicle CAN bus data (speed, RPM, fuel, diagnostics)
- **OBD Fields**: OBD-II diagnostic data (speed, RPM, fuel consumption)
- **AVL IO Parameters**: Teltonika AVL protocol parameters (343+ parameters)
- **BLE Fields**: Bluetooth Low Energy sensor data
- **Device Fields**: Gateway/device status and configuration
- **I/O Fields**: Digital and analog inputs/outputs
- **Event Fields**: Device-side events and triggers

### Navixy Field Examples

**Location:**
- `lat`, `lng` - GPS coordinates
- `heading` - Direction of travel (0-359°)
- `alt` - Altitude
- `hdop`, `pdop` - GPS precision metrics
- `satellites` - Number of satellites in fix

**CAN Bus:**
- `can_speed` - CAN bus speed (most accurate)
- `can_rpm` - CAN bus engine RPM
- `can_fuel_1` - CAN bus fuel level (percentage)
- `can_mileage` - CAN bus odometer
- `can_ignition_state` - CAN bus ignition state

**OBD:**
- `obd_speed` - OBD-II speed
- `obd_rpm` - OBD-II engine RPM
- `obd_custom_fuel_litres` - OBD-II fuel level
- `obd_time_since_engine_start` - OBD-II engine runtime

**AVL IO Parameters:**
- `avl_io_1` through `avl_io_1000+` - Teltonika AVL protocol parameters
- Examples: `avl_io_85` (Engine RPM), `avl_io_239` (Ignition), `avl_io_898` (SSF Ignition)

**BLE Sensors:**
- `ble_temp_sensor_1` through `ble_temp_sensor_4` - BLE temperature sensors
- `ble_humidity_1` through `ble_humidity_4` - BLE humidity sensors
- `ble_fuel_level_1`, `ble_fuel_level_2` - BLE fuel level sensors

### Complete Navixy Field Catalog

For the complete catalog of all ~340 Navixy fields, see:
- **CSV File**: `docs/reference/navixy-field-catalog.csv`
- **Schema Specification**: [Schema Specification](../specifications/schema-specification.md) contains provider field mappings

---

## Future Providers

### OEM Direct Integration

**Planned Providers:**
- TrackUnit
- CareTrack
- Mecalac
- Manitou
- Liebher
- Other OEM manufacturers

**Integration Approach:**
- **Connection**: Direct OEM integration via credentials
- **Format**: Provider-specific telemetry format (AEMP 2.0 standard)
- **Field Mapping**: Provider fields will be mapped to Fleeti telemetry format using configuration

**Status**: Planned for future implementation

### Other Providers

**Unknown Providers:**
- System must handle providers not yet identified (e.g., Abeeway)
- Architecture must accept any telemetry format
- New provider fields must be mappable to Fleeti telemetry

**Flexible Ingestion:**
- Provider-agnostic parser architecture
- Configuration-driven field mapping
- Unknown fields preserved in raw archive

---

## Field Mapping Approach

### Provider-Agnostic Design

All provider fields are mapped to unified Fleeti telemetry format:

1. **Provider Parser**: Converts provider-specific format to provider-agnostic structure
2. **Field Mapping**: Provider fields mapped to Fleeti fields using configuration
3. **Transformation**: Priority rules, calculations, and transformations applied
4. **Output**: Consistent Fleeti telemetry format regardless of provider source

### Mapping Types

- **Direct Mapping**: 1:1 field mapping (e.g., `lat` → `location.latitude`)
- **Prioritized Mapping**: Best source selected from multiple provider fields
- **Calculated Mapping**: Derived from multiple provider fields
- **Transformed Mapping**: Combined with static asset metadata

See [Mapping Rules](./mapping-rules.md) for detailed mapping logic.

---

## Field Detection and Watchdog

### New Field Detection

System includes a watchdog to detect new provider fields:

- **Monitoring**: Incoming telemetry packets monitored for unknown fields
- **Detection**: Fields with non-zero values that aren't in catalog are flagged
- **Alerting**: Notifications when new fields detected
- **Logging**: New fields logged with sample values for analysis

**Purpose**: Ensure we don't miss new telemetry capabilities and can document/incorporate them

---

## Related Documentation

- **[Fleeti Fields Catalog](./fleeti-fields-catalog.md)**: Complete Fleeti telemetry fields
- **[Mapping Rules](./mapping-rules.md)**: Field transformation rules
- **[Schema Specification](../specifications/schema-specification.md)**: Complete provider field mappings
- **[Telemetry System Specification](../specifications/telemetry-system-specification.md)**: System specification
- **[Reference Materials](../reference-materials/provider-catalogs.md)**: Detailed provider catalogs

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-XX  
**Status**: ✅ Validated  
**Source**: `Wiki/telemetry-system-specification.md` Section 3






