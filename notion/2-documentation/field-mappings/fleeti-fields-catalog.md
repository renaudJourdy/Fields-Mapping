# Fleeti Fields Catalog

**Status:** ✅ Validated  
**Source:** `working/fleeti-telemetry-schema-specification.md`

Complete catalog of all Fleeti telemetry fields organized by section.

---

## Overview

The Fleeti Fields Catalog provides a comprehensive reference of all possible Fleeti telemetry fields that can exist within the Fleeti system. This catalog is organized into logical sections for easy navigation and understanding.

**Note:** For complete field definitions, provider mappings, and detailed field tables, refer to the [Schema Specification](../specifications/schema-specification.md).

---

## Field Organization

Fleeti telemetry fields are organized into the following sections:

### Core Sections (P0-P1 Priority)

1. **Asset Metadata** - Static asset information (id, name, type, accessories, installation config)
2. **Telemetry Context** - Computed status families, geofences, trip information
3. **Location** - GPS/GNSS positioning data
4. **Motion** - Speed and movement status
5. **Power** - Ignition state and battery information
6. **Fuel** - Fuel levels and consumption
7. **Counters** - Odometer and engine hours
8. **Driving Behavior** - Daily aggregated metrics and eco-driving scores

### Extended Sections (P1-P2 Priority)

9. **Sensors** - Environmental, magnet, inertial, and custom sensors
10. **Diagnostics** - CAN bus data, engine stats, body sensors, health warnings
11. **Connectivity** - Network and communication status

### Internal Sections (BL/T Priority)

12. **I/O** - Raw digital and analog input/output states
13. **Driver** - Driver identification and events
14. **Device** - Tracking device status and configuration
15. **Other** - Device-side events and raw CAN data
16. **Packet Metadata** - Provider packet metadata

---

## Field Priority Levels

Fields are assigned priority levels that determine implementation order and visibility:

- **P0 (Core)**: Essential fields for basic functionality - Location, speed, ignition, status
- **P1 (Must-Have)**: Important fields for fleet management - Fuel, driving behavior, sensors
- **P2 (Nice-to-Have)**: Valuable fields for detailed analysis - Diagnostics, extended sensors
- **P3 (Not-Have)**: Specialized or rarely used fields
- **T (Troubleshooting)**: Available for super admin users only
- **BL (Business Logic)**: Used internally for computation, not exposed to customers

---

## Field Categories

### Core Fields (~50 fields)

Essential telemetry fields required for basic fleet management:

- **Location**: `location.latitude`, `location.longitude`, `location.heading`
- **Motion**: `motion.speed`, `motion.is_moving`
- **Status**: `status.top_status`, `status.statuses[]`
- **Power**: `power.ignition` (BL), `power.ev.*` (for EVs)
- **Asset**: `asset.id`, `asset.name`, `asset.type`, `asset.subtype`

### Extended Fields (~200+ fields)

All telemetry fields for complete data access:

- **Fuel**: `fuel.levels[]`, `fuel.consumption.*`
- **Sensors**: `sensors.environment[]`, `sensors.magnet[]`, `sensors.inertial[]`
- **Diagnostics**: `diagnostics.engine.*`, `diagnostics.body.*`, `diagnostics.health.*`
- **Driving Behavior**: `driving_behavior.daily_summary.*`
- **Counters**: `counters.odometer`, `counters.engine_hours`

### Internal Fields (BL/T)

Fields used internally or for troubleshooting:

- **I/O**: `io.inputs.*`, `io.outputs.*`, `io.analog.*` (BL)
- **Device**: `device.battery.*`, `device.power.*` (T)
- **Provider**: `provider.time.*`, `provider.event.*` (T/BL)

---

## Field Types

Fleeti telemetry fields are categorized by how they are derived:

1. **Direct Mapping**: 1:1 mapping from provider field (e.g., `lat` → `location.latitude`)
2. **Prioritized**: Best source selected from multiple provider fields (e.g., `motion.speed` from CAN/OBD/GPS)
3. **Calculated**: Derived from multiple fields or conditions (e.g., `location.cardinal_direction` from heading)
4. **Transformed**: Combined with static asset metadata (e.g., `fuel.level_liters` from percentage + tank capacity)
5. **I/O Mapped**: Raw I/O mapped to semantic fields via installation metadata (e.g., `power.ignition` from input + metadata)

---

## Complete Field Reference

For complete field definitions including:

- Field paths and types
- Priority levels
- Provider field mappings
- Source logic (direct, prioritized, calculated, transformed)
- Units and descriptions
- Use cases

Refer to the [Schema Specification](../specifications/schema-specification.md).

---

## Related Documentation

- **[Schema Specification](../specifications/schema-specification.md)**: Complete field definitions and provider mappings
- **[Provider Fields Catalog](./provider-fields-catalog.md)**: Provider field overview
- **[Mapping Rules](./mapping-rules.md)**: Field transformation rules
- **[Telemetry System Specification](../specifications/telemetry-system-specification.md)**: Complete system specification

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-XX  
**Status**: ✅ Validated  
**Source**: `working/fleeti-telemetry-schema-specification.md`






