# Introduction

This document defines the key concepts and terminology used throughout the Fleeti Telemetry Mapping project. Understanding these concepts is essential for working with the telemetry system, whether you're a developer implementing features, a stakeholder reviewing requirements, or a new team member getting oriented.

# Provider Concepts

## Provider-Agnostic vs. Provider-Specific

**Provider-Agnostic**: A design approach where the system works with multiple telemetry providers without being dependent on any single provider's format, API, or platform.

- **Fleeti Telemetry Format**: Unified format regardless of provider source
- **Abstract Interfaces**: Common interfaces for all providers
- **Configuration-Driven**: Provider differences handled through configuration

**Provider-Specific**: Telemetry data in the original format from a specific provider (e.g., Navixy, OEM manufacturer).

- **Raw Provider Data**: Original telemetry packets from provider
- **Provider Fields**: Field names and structures specific to that provider
- **Provider Formats**: Data formats unique to each provider

**Example**:

- **Provider-Specific**: Navixy sends `can_speed`, `obd_speed`, `speed` (GPS)
- **Provider-Agnostic**: Fleeti telemetry has `motion.speed` (best source selected)

## Data Forwarding

**Data Forwarding** is a real-time telemetry ingestion method where the provider forwards raw parsed telemetry packets immediately as they are received from devices.

**Key Characteristics**:

- **Real-time**: Packets forwarded as soon as received
- **No API Polling**: Eliminates need to poll provider API
- **Direct Access**: Receive data stream directly from provider infrastructure
- **Complete Data**: All telemetry fields included in packets

# Fleeti Telemetry Format

## Canonical Format

**Fleeti Telemetry Format** is the unified, provider-agnostic telemetry structure that all provider data is transformed into.

**Key Characteristics**:

- **Consistent Structure**: Same format regardless of provider source
- **Standardized Fields**: Consistent field names and units
- **Complete Data**: All available telemetry represented
- **Extensible**: New fields can be added without breaking changes

**Example Structure**:

```json
{
  "last_updated_at": 1234567890,
  "asset": { "id": "...", "name": "..." },
  "location": { "latitude": 5.3561, "longitude": -4.0083 },
  "motion": { "speed": { "value": 65, "unit": "km/h" } },
  "power": { "ignition": true },
  "status": { "top_status": { "family": "transit", "code": "in_transit" } }
}
```

## Field Types

Fleeti telemetry fields are categorized by how they are derived from provider data:

### 1. Direct Mapping Fields

**Description**: Fields that require **no calculation, aggregation, or transformation**

- **Mapping**: Provider field → Fleeti field (1:1)
- **Example**: `lat` (latitude) from provider → `location.latitude` in Fleeti
- **Unit Conversion**: May require unit normalization (e.g., `km/h` → `m/s`)

**Rule**: Direct mapping with optional unit conversion

### 2. Prioritized Fields

**Description**: Multiple provider fields represent the same Fleeti telemetry concept. We need to **choose the best source** based on priority.

**Priority Rules**:

- **Speed**: `can_speed` > `obd_speed` > `speed` (GPS)
- **RPM**: `can_rpm` > `obd_rpm` > `avl_io_85`
- **Odometer**: `can_mileage` > `hw_mileage` > `avl_io_105` (GPS)
- **Fuel Level**: `can_fuel_1` > `fuel_level` > `avl_io_86`
- **Ignition**: `avl_io_898` (SSF) > `can_ignition_state` > `can_engine_state` > `avl_io_239`

**Rule**: Use highest priority non-null value available in the packet

### 3. Calculated Fields

**Description**: Fields **created based on multiple telemetry fields** or **different conditions**

**Types of Calculations**:

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

**Rule**: Calculation defined in configuration, executed during normalization

### 4. Transformed Fields (Static + Telemetry)

**Description**: Fields that require **static configuration data** combined with telemetry to produce Fleeti telemetry

**Example**: Fuel Level Percentage → Liters

- Provider sends: `can_fuel_1 = 75` (percentage)
- Static data: `tank_capacity = 120` (liters) - stored per asset
- Fleeti output: `fuel.level_liters = 90` (calculated: `75% * 120L = 90L`)

**Rule**: Transformation defined in configuration, requires static field reference

### 5. I/O Mapped Fields

**Description**: Raw I/O fields mapped to semantic fields based on installation metadata

**Pattern**:

- **Raw I/O**: `io.inputs.individual.input_1`, `io.outputs.individual.output_2`
- **Metadata**: `asset.installation.ignition_input_number`, `asset.installation.immobilizer_output_number`
- **Semantic**: `power.ignition`, `diagnostics.body.doors.*`, `fuel.levels[]`

**Example**: `io.inputs.individual.input_1` + `asset.installation.ignition_input_number = 1` → `power.ignition`

**Rule**: I/O semantic mapping defined in installation metadata, transformation pipeline applies mapping during normalization

# Priority Levels

Fields are assigned priority levels (P0-P3, T, BL, ?) that determine implementation order and visibility:

## Implementation Priorities (P0-P3)

- **P0 (Core Fields)**: Essential telemetry fields required for basic fleet management functionality. Must be implemented first. Displayed to customers and exposed through customer-facing APIs.
- **P1 (Must-Have)**: Important fields that significantly enhance functionality. Implemented after P0. Displayed to customers and exposed through APIs.
- **P2 (Nice-to-Have)**: Valuable fields that provide additional insights. Implemented as resources allow. May be displayed to customers or exposed through APIs.
- **P3 (Not-Have)**: Fields documented but not currently prioritized. May be implemented in future phases. Typically not displayed to customers or exposed through standard APIs.

## Special Priorities (T, BL, ?)

- **T (Troubleshooting)**: Available via API for super admin users, not displayed to customers. Used for troubleshooting and diagnostic purposes.
- **BL (Business Logic)**: Used internally for computation (e.g., `power.ignition` for status computation), not exposed to customers.
- **? (Unknown)**: Priority/usage to be determined. Requires further investigation.

# Status Families

Status families are computed states that represent different aspects of asset status. Each family has specific codes and compatibility rules.

## Connectivity Status

**Purpose**: Indicates whether asset is online or offline

**Codes**:

- `online`: Asset has sent telemetry within the last 24 hours (1 hour for Cold Room sites)
- `offline`: Asset has not sent telemetry for 24+ hours (1+ hours for Cold Room sites)

**Compatibility**: All asset types (Vehicles, Equipment, Sites, Phones)

**Source**: `last_updated_at` timestamp (derived from `msg_time`)

## Transit Status

**Purpose**: Indicates whether asset is in transit or parked

**Codes**:

- `in_transit`: Asset is moving or ignition is on
- `parked`: Asset is stationary (no movement for 3 minutes) or ignition is off

**Compatibility**:

- ✅ Phones, Equipment.Undefined, All Vehicle subtypes
- ❌ Sites, Equipment.FuelTank, Equipment.ElectricGenerator

**Source**: Ignition state, movement status, speed

**State Machine**: Uses ignition triggers (immediate) and movement/speed conditions (duration-based)

## Engine Status

**Purpose**: Indicates whether engine is running or in standby

**Codes**:

- `running`: Engine is running (ignition on)
- `standby`: Engine is in standby (ignition off)

**Compatibility**:

- ✅ Equipment (all subtypes), Specific Vehicle subtypes (Agricultural, Machine)
- ❌ Sites, Phones, Most Vehicle subtypes

**Source**: Ignition state (from I/O inputs, CAN signals, or hardware/virtual ignition)

## Immobilization Status

**Purpose**: Indicates immobilizer state (locked/unlocked)

**Codes**:

- `immobilized`: Immobilizer is locked (output active)
- `free`: Immobilizer is unlocked (output inactive)
- `immobilizing`: Immobilization command sent, waiting for confirmation
- `releasing`: Release command sent, waiting for confirmation

**Compatibility**:

- ✅ Vehicles (most subtypes), Equipment (most subtypes)
- ❌ Sites, Phones, Some Equipment subtypes

**Source**: Digital output state (mapped from installation metadata)

**Requirements**: Asset must have immobilizer accessory installed and installation metadata specifying output number

## Top Status

**Purpose**: Highest-priority status family for display

**Priority Order**: Connectivity > Immobilization > Engine > Transit

**Usage**: Displayed in map markers and UI to show most important status

# Configuration Hierarchy

Configuration can be defined at multiple levels, with lower levels overriding higher levels:

## 1. Default/Global Configuration

**Scope**: Base configuration for all assets

**Use Case**: Standard field mappings and transformation rules

**Example**: Default speed priority: `can_speed > obd_speed > gps_speed`

## 2. Customer-Level Configuration

**Scope**: Override default configuration for a specific customer

**Use Case**: Customer-specific requirements (e.g., different speed source priority)

**Example**: Customer A: `obd_speed > gps_speed` (CAN not available)

## 3. Asset Group Configuration

**Scope**: Override customer configuration for a group of assets

**Use Case**: Fleet-specific requirements (e.g., different configuration for truck fleet vs car fleet)

**Example**: Fleet B: `gps_speed` (OBD unreliable for this fleet)

## 4. Single Asset Configuration

**Scope**: Override group configuration for a specific asset

**Use Case**: Individual asset requirements or troubleshooting

**Example**: Truck-123: `can_speed` (highest priority, manually set)

**Rule**: Lower-level configurations override higher-level configurations

# Data Forwarding

**Data Forwarding** is the real-time telemetry ingestion method used with Navixy.

**Key Characteristics**:

- **Real-time**: Packets forwarded immediately as received
- **No Polling**: Eliminates API polling overhead
- **Direct Stream**: Receive data directly from Navixy infrastructure
- **Complete Packets**: All telemetry fields included

# Transformation Pipeline

The **Transformation Pipeline** is the core component that converts provider telemetry into Fleeti format.

**Process**:

1. **Receive**: Provider telemetry packet
2. **Parse**: Convert to provider-agnostic structure
3. **Load Configuration**: Retrieve applicable configuration (hierarchy)
4. **Transform**: Apply field mappings, priority rules, calculations
5. **Compute Status**: Calculate status families
6. **Output**: Fleeti telemetry format

**Key Features**:

- Configuration-driven (no hardcoding)
- Real-time processing
- Extensible calculation framework
- Asset Service integration

# Storage Tiers

The system uses multiple storage tiers optimized for different access patterns:

- **Hot (Fast Access)**: Core fields for real-time queries
- **Warm (Complete Data)**: All fields for detail views and APIs
- **Cold (Raw Archive)**: Original provider packets for historical recalculation