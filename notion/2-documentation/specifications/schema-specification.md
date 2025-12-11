# Schema Specification

**Status:** ✅ Validated  
**Source:** `working/fleeti-telemetry-schema-specification.md`

Complete Fleeti telemetry schema specification with all field definitions, types, priorities, and provider mappings.

---

## Purpose

This document provides a **comprehensive reference** of all possible Fleeti telemetry fields, organized into a provider-agnostic structure. It serves as a foundation for understanding the complete scope of telemetry data that can exist within the Fleeti system.

**Key Objectives:**

1. **Big Picture of Fleeti Fields**: Complete overview of all Fleeti telemetry fields that can potentially exist
2. **Grouped by Section**: Organizes all Fleeti fields into logical sections for easy navigation
3. **Priority Assignment**: Assigns implementation priorities (P0-P3, T, BL, ?) to guide development phases
4. **Provider Field Grouping**: Maps all available Navixy provider fields into their corresponding Fleeti fields

**Note:** This document represents the *maximal possible telemetry object* - not all fields will be implemented immediately, and the actual telemetry structure used in production may be a subset based on priorities and requirements.

---

## Priority System

Fields in this document are assigned priority levels (P0, P1, P2, P3, T, BL, ?) that indicate their importance, implementation order, and visibility:

### Implementation Priorities (P0-P3)

- **P0 (Core Fields)**: Essential telemetry fields required for basic fleet management functionality. Must be implemented first. Displayed to customers and exposed through customer-facing APIs.
- **P1 (Must-Have)**: Important fields that significantly enhance functionality. Implemented after P0. Displayed to customers and exposed through APIs.
- **P2 (Nice-to-Have)**: Valuable fields that provide additional insights. Implemented as resources allow. May be displayed to customers or exposed through APIs.
- **P3 (Not-Have)**: Fields documented but not currently prioritized. May be implemented in future phases. Typically not displayed to customers.

### Special Priorities (T, BL, ?)

- **T (Troubleshooting)**: Available via API for super admin users, not displayed to customers. Used for troubleshooting and diagnostic purposes.
- **BL (Business Logic)**: Used internally for computation, not exposed to customers. Examples: raw I/O states, ignition state for status computation.
- **? (Unknown)**: Priority/usage to be determined. Requires further investigation.

---

## Schema Structure

### Root-Level Fields

The telemetry object includes a root-level `last_updated_at` field that indicates when Fleeti backend last received any telemetry packet from this asset.

```json
{
  "last_updated_at": "number",
  "asset": { ... },
  "status": { ... },
  "location": { ... },
  // ... rest of telemetry fields ...
  "provider": { ... }
}
```

**Key Timestamp Fields:**
- **`last_updated_at`** (root level): Packet freshness indicator. Updates on every packet received. Format: Unix Epoch milliseconds (number).
- **`provider.time.fleeti_time`**: Authoritative Fleeti backend reception timestamp. Set when packet is received via Data Forwarding.
- **`last_changed_at`** (field-level): Value change tracking. Only updates when field value actually changes. Computed by comparing current value with previous telemetry packet.

---

## Schema Sections

The complete Fleeti telemetry schema is organized into the following sections:

### 1. Asset Metadata

**Purpose:** Static asset information that does not change per telemetry packet.

**Includes:**
- Asset identity (id, name, type, subtype)
- Group information
- Customer reference
- Accessories configuration
- Installation metadata (ignition input, immobilizer output, initial counters)
- Asset properties (vehicle, equipment, phone, site specifications)

**Key Fields:**
- `asset.id` (P0) - Primary asset identifier
- `asset.type` (P0) - Type enum (vehicle, equipment, site, phone)
- `asset.subtype` (P0) - Subtype enum
- `asset.accessories[]` (P1) - Accessory configurations
- `asset.installation.*` (BL) - Installation metadata for I/O mapping

### 2. Telemetry Context

**Purpose:** Computed/derived fields that change per telemetry packet.

**Includes:**
- Status families (connectivity, transit, engine, immobilization)
- Top status (highest-priority status family)
- Geofence context
- Ongoing trip information
- Nearby assets

**Key Fields:**
- `status.top_status` (P0) - Highest-priority status family
- `status.statuses[]` (P0) - Array of compatible status families
- `geofences[]` (P1) - Current geofences asset is inside
- `trip` (P1) - Ongoing trip information

### 3. Location

**Purpose:** GPS/GNSS positioning data and location precision metrics.

**Key Fields:**
- `location.latitude` (P0) - Latitude in decimal degrees
- `location.longitude` (P0) - Longitude in decimal degrees
- `location.heading` (P0) - Heading in degrees (0-359)
- `location.cardinal_direction` (P1) - Derived from heading (N, NE, E, SE, S, SW, W, NW)
- `location.last_changed_at` (P1) - Timestamp when location/heading changed significantly
- `location.precision.*` (T) - GPS precision metrics (HDOP, PDOP, satellites, fix quality)

### 4. Connectivity

**Purpose:** Network and communication status information.

**Key Fields:**
- `connectivity.signal_level` (P1) - GSM signal strength (0-31, 99=unknown)
- `connectivity.operator` (T) - Active GSM operator code
- `connectivity.cell.*` (T) - GSM cell information (ID, LAC)
- `connectivity.sim.iccid[]` (T) - SIM card ICCID

### 5. Motion

**Purpose:** Dynamic movement data including speed and motion status.

**Key Fields:**
- `motion.speed` (P0) - Speed (best source: CAN > OBD > GPS)
- `motion.is_moving.value` (P1) - Movement status (0/1)
- `motion.is_moving.last_changed_at` (P1) - Timestamp when movement status changed
- `motion.accelerometer.*` (P3) - Raw accelerometer data (x, y, z)

### 6. Power

**Purpose:** Power source status, canonical ignition state, and battery health.

**Key Fields:**
- `power.ignition` (BL) - Ignition state (used for status computation)
- `power.ignition_last_changed_at` (BL) - Timestamp when ignition changed
- `power.low_voltage_battery.*` (P2) - Vehicle low-voltage battery (12V, 24V, etc.)
- `power.ev.traction_battery.*` (P1) - EV/hybrid traction battery
- `power.ev.charging.*` (P1) - EV charging status

### 7. Fuel

**Purpose:** Fuel system data including levels and consumption.

**Key Fields:**
- `fuel.levels[]` (P1) - Fuel level readings (percentage or liters)
- `fuel.consumption.cumulative` (P1) - Total fuel consumed (liters)
- `fuel.consumption.rate` (P2) - Fuel consumption rate (l/h)
- `fuel.energy.*` (P2) - Fuel type and CNG status

### 8. Counters

**Purpose:** Accumulated counters for odometer and engine hours.

**Key Fields:**
- `counters.odometer` (P1) - Total vehicle mileage (km)
- `counters.engine_hours` (P1) - Total engine work time (hours)

### 9. Driving Behavior

**Purpose:** Daily aggregated driving metrics and eco-driving scores.

**Key Fields:**
- `driving_behavior.daily_summary.driving_duration` (P1) - Cumulative time when vehicle was moving
- `driving_behavior.daily_summary.idling_duration` (P1) - Cumulative idling time
- `driving_behavior.daily_summary.event_counts.*` (P1-P2) - Harsh driving event counts
- `driving_behavior.daily_summary.eco_score.value` (P1) - Eco-driving score

### 10. Sensors

**Purpose:** External and internal sensor readings (temperature, humidity, battery, etc.).

**Key Fields:**
- `sensors.environment[]` (P1) - Environmental sensors (temperature, humidity, battery, frequency)
- `sensors.magnet[]` (P1) - Magnetic field sensors
- `sensors.inertial[]` (P1) - Inertial sensors (pitch, roll)
- `sensors.custom[]` (P2) - Custom sensor values

**Note:** Sensor identity metadata (`id`, `label`, `position`) is derived from `asset.accessories[].sensors[]` (Section 1).

### 11. Diagnostics

**Purpose:** Detailed asset diagnostics, including CAN bus data, engine stats, and body sensors.

**Key Sections:**
- `diagnostics.agricultural.*` (P1-P2) - Agricultural machinery diagnostics
- `diagnostics.axles.weights[]` (P2) - Axle weight measurements
- `diagnostics.body.*` (P2-P3) - Body sensors (belts, doors, lights, occupancy, safety, climate)
- `diagnostics.brakes.*` (P2-P3) - Brake system diagnostics
- `diagnostics.drivetrain.*` (P2-P3) - Drivetrain diagnostics
- `diagnostics.engine.*` (P2) - Engine diagnostics (RPM, temperature, load, etc.)
- `diagnostics.fluids.*` (P1-P2) - Fluid levels (AdBlue, oil pressure)
- `diagnostics.health.*` (P1) - Health warnings (low fuel, low oil, DTC count, MIL status)
- `diagnostics.security.*` (P2) - Security system state flags
- `diagnostics.systems.*` (P2) - System diagnostics (steering, trailer, control, utility)

### 12. I/O (Inputs/Outputs)

**Purpose:** Digital and analog input/output states.

**Key Fields:**
- `io.inputs.individual.input_1` through `input_4` (BL) - Digital input states
- `io.outputs.individual.output_1` through `output_3` (BL) - Digital output states
- `io.analog.input_1`, `input_2` (BL) - Analog input voltage readings

**Note:** I/O fields represent raw device states. These are **not displayed to end customers** but are available to **Fleeti super admin users** for troubleshooting. I/O values are used elsewhere to compute semantic fields based on installation metadata.

### 13. Driver

**Purpose:** Driver identification and related events.

**Key Fields:**
- `driver.id.value` (P1) - Fleeti driver ID from catalog (lookup from hardware key)
- `driver.id.last_changed_at` (P1) - Timestamp when driver changed
- `driver.name` (P1) - Driver name from catalog
- `driver.hardware_key.value` (BL) - Hardware key identifier (iButton or RFID)
- `driver.privacy_mode.*` (P1) - Private mode state

### 14. Device

**Purpose:** Tracking device status, configuration, and security.

**Key Fields:**
- `device.battery.*` (T) - Device internal battery (current, level, voltage)
- `device.power.*` (T) - External power supply status
- `device.bluetooth.status` (P3) - Bluetooth connection status
- `device.firmware.version` (T) - Device firmware version
- `device.identification.*` (T) - Device module identifiers

### 15. Other

**Purpose:** Device-side events, geofence data, impulse counters, and raw CAN data.

**Note:** Events and geofence data will be handled separately from telemetry in the Fleeti system.

### 16. Packet Metadata

**Purpose:** Metadata about the telemetry packet itself.

**Key Fields:**
- `provider.event` (BL/T) - Event type
- `provider.event_code` (BL/T) - Event code
- `provider.time.device_time` (BL/T) - Device timestamp
- `provider.time.provider_time` (T) - Provider server timestamp
- `provider.time.fleeti_time` (T) - Fleeti backend reception timestamp

---

## Field Mapping Patterns

### Direct Mapping

Provider field → Fleeti field (1:1) with optional unit conversion.

**Example:** `lat` → `location.latitude`

### Prioritized Fields

Multiple provider fields represent the same Fleeti concept. Select best source based on priority.

**Example:** Speed priority: `can_speed` > `obd_speed` > `speed` (GPS)

### Calculated Fields

Fields created from multiple telemetry fields or conditions.

**Examples:**
- `location.cardinal_direction` = Derived from `location.heading`
- `status.top_status` = Highest-priority status family
- `driver.id.value` = Lookup `hardware_key.value` in driver catalog

### Transformed Fields

Fields that combine static configuration data with telemetry.

**Example:** `fuel.level_liters` = `fuel.level_percent` * `static.tank_capacity_liters`

### I/O Mapped Fields

Raw I/O fields mapped to semantic fields based on installation metadata.

**Example:** `io.inputs.individual.input_1` + `asset.installation.ignition_input_number = 1` → `power.ignition`

---

## Provider Field Mappings

All Navixy provider fields are mapped to Fleeti telemetry fields. The complete mapping is documented in the source document with:

- Provider field name (e.g., `can_speed`, `avl_io_85`)
- Fleeti field path (e.g., `motion.speed`, `diagnostics.engine.rpm`)
- Priority level
- Source logic (direct, prioritized, calculated, transformed)
- Description and units

**Reference:** See source document for complete provider field mapping tables.

---

## Related Documentation

- **[Telemetry System Specification](./telemetry-system-specification.md)**: Complete system specification
- **[Status Rules](./status-rules.md)**: Status computation rules
- **[Field Mappings](../field-mappings/README.md)**: Field catalogs and mapping rules
- **[Overview & Vision](../../overview-vision/README.md)**: Project overview and architecture

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-XX  
**Status**: ✅ Validated  
**Source**: `working/fleeti-telemetry-schema-specification.md`

**Note:** For complete field definitions, provider mappings, and detailed field tables, refer to the source document: `working/fleeti-telemetry-schema-specification.md`






