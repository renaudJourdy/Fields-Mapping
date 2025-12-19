# Priority System

Fields in this document are assigned priority levels (P0, P1, P2, P3, T, BL, ?) to indicate their importance, implementation order, and visibility:

## Implementation Priorities (P0-P3)

These priorities indicate the order of implementation and customer-facing importance:

- **P0 (Core Fields)**: Essential telemetry fields required for basic fleet management functionality. These fields form the foundation of the Fleeti telemetry system and must be implemented first. These are typically displayed to customers and exposed through customer-facing APIs.
- **P1 (Must-Have)**: Important fields that significantly enhance functionality but are not strictly required for basic operations. These should be implemented after P0 fields. These are typically displayed to customers and exposed through customer-facing APIs.
- **P2 (Nice-to-Have)**: Valuable fields that provide additional insights or features but are not critical for core functionality. These can be implemented as resources allow. These may be displayed to customers or exposed through APIs based on feature requirements.
- **P3 (Not-Have)**: Fields that are documented but not currently prioritized for implementation. These may be implemented in future phases or based on specific customer requirements. These are typically not displayed to customers or exposed through standard APIs.

## Special Priorities (T, BL, ?)

These priorities indicate special handling requirements beyond implementation order:

- **T (Troubleshooting)**: Fields available for troubleshooting and diagnostic purposes. These fields are **not displayed to end customers** but are **available through APIs for super admin users** to access historical data and troubleshoot issues. Examples include device diagnostic information, connectivity details, location precision metrics, and raw technical data. These fields are essential for support teams and technical troubleshooting but not needed for standard fleet management operations.
- **BL (Business Logic)**: Fields used internally by the Fleeti backend for business logic computation but **not displayed to customers or exposed through customer-facing APIs**. These fields are used to compute other fields, determine status, or perform internal calculations. Examples include raw I/O states used to compute semantic fields, ignition state used for status computation, and intermediate computed values. These fields are essential for system operation but remain internal to the backend.
- **? (Unknown/To Be Determined)**: Fields where the priority or usage is not yet determined and requires further investigation. These fields are documented but their implementation priority, visibility, and usage patterns need to be clarified before implementation.

## Priority Assignment Guidelines

- **Customer-facing fields** (displayed in UI, exposed in customer APIs): Use P0, P1, or P2
- **Internal computation fields** (used to compute other fields, not displayed): Use BL
- **Troubleshooting fields** (super admin access only, diagnostic purposes): Use T
- **Uncertain fields** (needs investigation): Use ?
- **Low priority or future fields**: Use P3

Priority assignments help guide development teams in planning implementation phases, resource allocation, and API/UI visibility decisions.

---

# 🎯 Purpose

This document provides a **comprehensive reference** of all possible Fleeti telemetry fields, organized into a provider-agnostic structure. It serves as a foundation for understanding the complete scope of telemetry data that can exist within the Fleeti system.

**Key Objectives:**

1. **Big Picture of Fleeti Fields**: Provides a complete overview of all Fleeti telemetry fields that can potentially exist, based on available provider capabilities.
2. **Grouped by Section**: Organizes all Fleeti fields into logical sections (Asset Metadata, Location, Power, Fuel, Diagnostics, etc.) for easy navigation and understanding.
3. **Priority Assignment**: Assigns implementation priorities (P0-P3, T, BL, ?) to help identify high-priority fields and guide development phases.
4. **Provider Field Grouping**: Maps all available Navixy provider fields into their corresponding Fleeti fields, showing how provider-specific data is transformed and aggregated into the Fleeti telemetry model.

**Document Usage:**

- **Reference for Specifications**: This document is not used directly by developers as-is, but serves as a reference when creating detailed implementation specifications, API contracts, or frontend schemas.
- **Field Management**: When adding or removing fields, this document serves as the source of truth for understanding:
    - Which Fleeti fields exist
    - How provider fields map to Fleeti fields
    - What priority and visibility each field should have
    - Which section a field belongs to
- **Basis for Implementations**: All provider fields from Navixy are documented here, forming the foundation for creating all Fleeti fields. This ensures completeness and consistency across implementations.

**`Note:** This document represents the *maximal possible telemetry object* - not all fields will be implemented immediately, and the actual telemetry structure used in production may be a subset based on priorities and requirements. Specific views (API, Frontend, WebSocket) will be defined in separate specifications based on this reference.`

---

# Root-Level Fields

The telemetry object includes a root-level `last_updated_at` field that indicates when Fleeti backend last received any telemetry packet from this asset.

## Root Structure

```json
{
  "last_updated_at": "ISO8601",
  "asset": { ... },
  "status": { ... },
  "location": { ... },
  // ... rest of telemetry fields ...
  "provider": { ... }
}
```

## Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
| --- | --- | --- | --- |
| `last_updated_at` | P0 | **Computed:** Set to `provider.time.fleeti_time` when packet is received | ISO8601 timestamp when Fleeti backend last received any telemetry packet from this asset. Indicates telemetry freshness. Used for connectivity status computation and "last contact" displays. Same value as `provider.time.fleeti_time`. |

**Note:** Timestamp fields serve different purposes:

- **`last_updated_at`** (root level): Packet freshness indicator. Updates on every packet received. Set to `provider.time.fleeti_time`.
- **`provider.time.fleeti_time`**: Authoritative Fleeti backend reception timestamp. Set when packet is received via Data Forwarding.
- **`last_changed_at`** (field-level): Value change tracking. Only updates when field value actually changes (old_value ≠ new_value). Computed by comparing current value with previous telemetry packet.

For location, a threshold is applied to filter GPS jitter (only significant position/heading changes trigger updates). For status arrays, `last_changed_at` updates when the `code` changes, not on every packet.

---

# 1. Asset Metadata

**Purpose:** Static asset information that does not change per telemetry packet. This includes identity, ownership, groups, accessories, installation configuration, and asset-specific properties.

## Structure

```json
{
  "asset": {
    "id": "uuid",
    "name": "string",
    "type": 10,
    "subtype": 110,
    "group": { "id": "uuid", "name": "string" },
    "customer_ref": "2010-010",
    "accessories": [
      {
        "id": "uuid",
        "type_id": 1,
        "type_code": "immobilizer",
        "connection": "wire",
        "label": "Main immobilizer relay"
      },
      {
        "id": "uuid",
        "type_id": 2,
        "type_code": "temperature",
        "connection": "bluetooth",
        "label": "Cold room sensor",
        "sensors": [
          { "type": "temperature", "position": 1 },
          { "type": "humidity", "position": 1 }
        ]
      },
      {
        "id": "uuid",
        "type_id": 3,
        "type_code": "fuel_level",
        "connection": "wire",
        "label": "Fuel probe 1",
        "serial_number": "LLS-00933",
        "sensors": [
          { "type": "fuel_level", "position": 1 }
        ]
      }
    ],
    "installation": {
      "ignition_input_number": 1,
      "immobilizer_output_number": 2,
      "initial_odometer": { "value": 154000, "unit": "km" },
      "initial_engine_hours": { "value": 4200, "unit": "h" }
    },
    "properties": {
      "vehicle": {
        "serial_number": "string",
        "brand": "string",
        "model": "string",
        "license_plate": "string",
        "vin": "string",
        "powertrain": {
          "primary_energy": "diesel|gasoline|electric|hybrid|cng|lng|hydrogen|other",
          "fuel_tank_capacity": { "value": 600, "unit": "l" },
          "battery_capacity": { "value": 120, "unit": "kwh" },
          "theoretical_consumption": { "value": 32.5, "unit": "l/100km" },
          "theoretical_consumption_kwh": { "value": 24.3, "unit": "kwh/100km" }
        }
      },
      "equipment": {
        "serial_number": "string",
        "brand": "string",
        "model": "string",
        "rated_power": { "value": 180, "unit": "kw" },
        "energy_source": "diesel|electric|hybrid"
      },
      "phone": {
        "platform": "ios|android|unknown",
        "platform_version": "17.2",
        "employee_id": "string",
        "employee_name": "string"
      },
      "site": {
        "name": "Abidjan Coldroom West",
        "address": {
          "line1": "Zone industrielle",
          "city": "Abidjan",
          "country": "CI"
        },
        "location": {
          "latitude": 5.3561,
          "longitude": -4.0083
        },
        "surface": { "value": 120, "unit": "m2" },
        "capacity_units": 450,
        "temperature_range": { "min": { "value": -25, "unit": "°C" }, "max": { "value": 5, "unit": "°C" } }
      }
    }
  }
}
```

| **Note:** This structure represents static asset metadata. From a front-end perspective, not all of these fields will be available or used directly. However, these fields are essential inputs for the transformation pipeline to compute derived telemetry fields.

## Field Sources & Notes

| Fleeti Field | Priority | Source | Description |
| --- | --- | --- | --- |
| `asset.id` | P0 | Fleeti Asset service | Primary asset identifier |
| `asset.name` | P0 | Fleeti Asset service | Human-friendly asset label |
| `asset.type` | P0 | Fleeti Asset service | Type enum (vehicle, equipment, site, phone) |
| `asset.subtype` | P0 | Fleeti Asset service | Subtype enum (car, truck, cold_room, etc.) |
| `asset.group.id` | P0 | Asset grouping service | Primary group identifier |
| `asset.group.name` | P0 | Asset grouping service | Primary group name |
| `asset.customer_ref` | P0 | Customer registry | Reference code identifying the customer/tenant (e.g., `2010-010`) |
| `asset.accessories[].id` | P1 | Accessory registry | Unique accessory identifier |
| `asset.accessories[].type_id` | P1 | Accessory registry | Accessory type numeric ID |
| `asset.accessories[].type_code` | P1 | Accessory registry | Accessory type code (immobilizer, temperature, fuel_level, etc.) |
| `asset.accessories[].connection` | P3 | Installation metadata | Connection type (wire, bluetooth, wifi) |
| `asset.accessories[].label` | P1 | Installation metadata | Human-readable accessory label |
| `asset.accessories[].serial_number` | P2 | Installation metadata | Accessory serial number |
| `asset.accessories[].sensors[]` | P1 | Installation metadata | Array of sensor types/positions this accessory exposes |
| `asset.installation.ignition_input_number` | BL | Installation metadata | Digital input wired to ignition switch |
| `asset.installation.immobilizer_output_number` | BL | Installation metadata | Digital output controlling immobilizer relay |
| `asset.installation.initial_odometer` | BL | Installation metadata | Odometer reading at time of installation (offset) - `{ value: number, unit: "km" }` |
| `asset.installation.initial_engine_hours` | BL | Installation metadata | Engine hours reading at time of installation (offset) - `{ value: number, unit: "h" }` |
| `asset.properties.vehicle.serial_number` | P2 | Fleeti catalog | OEM/installer serial number |
| `asset.properties.vehicle.brand` | P1 | Fleeti catalog | Vehicle manufacturer brand |
| `asset.properties.vehicle.model` | P1 | Fleeti catalog | Vehicle model name |
| `asset.properties.vehicle.license_plate` | P1 | Fleeti catalog | Registration plate displayed to users |
| `asset.properties.vehicle.vin` | P2 | Fleeti catalog | Vehicle identification number (VIN) - **Metadata only, no Navixy AVL ID available** |
| `asset.properties.vehicle.powertrain.primary_energy` | P2 | Fleeti catalog | Primary energy source (diesel/gasoline/electric/hybrid/CNG/LNG/hydrogen/other) |
| `asset.properties.vehicle.powertrain.fuel_tank_capacity` | P1 | Fleeti catalog | Nominal fuel tank size - `{ value: number, unit: "l" }` |
| `asset.properties.vehicle.powertrain.battery_capacity` | P2 | Fleeti catalog | Battery capacity (for electric/hybrid vehicles) - `{ value: number, unit: "kwh" }` |
| `asset.properties.vehicle.powertrain.theoretical_consumption` | P2 | Fleeti catalog | Expected fuel consumption baseline - `{ value: number, unit: "l/100km" }` |
| `asset.properties.vehicle.powertrain.theoretical_consumption_kwh` | P2 | Fleeti catalog | Expected energy consumption baseline - `{ value: number, unit: "kwh/100km" }` |
| `asset.properties.equipment.serial_number` | P2 | Fleeti catalog | Equipment serial number |
| `asset.properties.equipment.brand` | P1 | Fleeti catalog | Equipment manufacturer brand |
| `asset.properties.equipment.model` | P1 | Fleeti catalog | Equipment model name |
| `asset.properties.equipment.rated_power` | P2 | Fleeti catalog | Equipment rated power - `{ value: number, unit: "kw" }` |
| `asset.properties.equipment.energy_source` | P2 | Fleeti catalog | Equipment energy source (diesel/electric/hybrid) |
| `asset.properties.phone.platform` | P2 | Fleeti catalog | Mobile platform (ios/android/unknown) |
| `asset.properties.phone.platform_version` | P2 | Fleeti catalog | Platform version (e.g., `17.2`) |
| `asset.properties.phone.employee_id` | P1 | Fleeti catalog | Associated employee identifier (not yet available) |
| `asset.properties.phone.employee_name` | P1 | Fleeti catalog | Associated employee name (not yet available) |
| `asset.properties.site.name` | P1 | Fleeti catalog | Site name |
| `asset.properties.site.address.line1` | P2 | Fleeti catalog | Address line 1 |
| `asset.properties.site.address.city` | P2 | Fleeti catalog | City name |
| `asset.properties.site.address.country` | P2 | Fleeti catalog | Country code (ISO) |
| `asset.properties.site.location.latitude` | P0 | Fleeti catalog | Site latitude for map display |
| `asset.properties.site.location.longitude` | P0 | Fleeti catalog | Site longitude for map display |
| `asset.properties.site.surface` | P2 | Fleeti catalog | Site surface area - `{ value: number, unit: "m2" }` |
| `asset.properties.site.capacity_units` | P2 | Fleeti catalog | Site capacity (units depend on site type) |
| `asset.properties.site.temperature_range` | P2 | Fleeti catalog | Expected min/max temperature range (especially for cold rooms) - `{ min: { value: number, unit: "°C" }, max: { value: number, unit: "°C" } }` |

**Note:** Immobilizer capability is derived from the `accessories[]` array. If any accessory has `type_code === "immobilizer"`, the asset is immobilizer-capable. Use `asset.accessories?.some(acc => acc.type_code === "immobilizer") ?? false` to check capability. This ensures a single source of truth and avoids data consistency issues.

| **Note:** Most asset metadata fields come from Fleeti catalog.

---

# 2. Telemetry Context

**Purpose:** Computed/derived fields that change per telemetry packet. These are calculated from raw telemetry combined with asset metadata. Includes status families (connectivity, transit, engine, immobilization), current geofence context, and ongoing trip information.

## Structure

```json
{
  "status": {
    "top_status": {
      "family": "transit",
      "code": "in_transit",
      "last_changed_at": "ISO8601"
    },
    "statuses": {
      "connectivity":{
        "code": "online",
        "compatible": true,
        "last_changed_at": "ISO8601"
      },
      "immobilization":{
        "code": "free",
        "compatible": true,
        "last_changed_at": "ISO8601"
      },
      "engine":{
        "code": "running",
        "compatible": true,
        "last_changed_at": "ISO8601"
      },
      "transit":{
        "code": "in_transit",
        "compatible": true,
        "last_changed_at": "ISO8601"
      }
  },
  "geofences": [
    {
      "geofence_id": 42,
      "geofence_name": "Warehouse"
    },
    {
      "geofence_id": 15,
      "geofence_name": "Service Area"
    }
  ],
  "trip": {
    "id": "uuid",
    "started_at": "ISO8601",
    "distance": { "value": 45.2, "unit": "km" },
    "duration": { "value": 3600, "unit": "s" },
    "start_location": { "lat": 5.3561, "lng": -4.0083 },
    "current_location": { "lat": 5.4123, "lng": -4.0156 }
  },
  "nearby_assets": [
    {
      "id": "ble_beacon_id_hex",
      "name": "Asset Name"
    },
    {
      "id": "asset_uuid_123",
      "name": "Nearby Vehicle"
    }
  ]
}
```

## Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
| --- | --- | --- | --- |
| `status.top_status` | P0 | **Computed:** Highest-priority status family | Connectivity > Immobilization > Engine > Transit |
| `status.top_status.last_changed_at` | P0 | **Computed:** Backend compares current `code` with previous value | ISO8601 timestamp when the top status code last changed. Used to calculate duration of current status state. |
| `status.statuses[]` | P0 | **Computed:** Telemetry + Asset Metadata | Array of compatible status families with codes |
| `status.statuses[].last_changed_at` | P0 | **Computed:** Backend compares current `code` with previous value for each status family | ISO8601 timestamp when this status family's code last changed. Used to calculate duration of current status (e.g., "offline for 2h", "engine running since 10:30"). |
| `geofences[]` | P1 | **Computed:** `location.lat`/`lng` + Geofence Service | Current geofences the asset is inside |
| `trip` | P1 | **Computed:** Ignition + Movement history | Ongoing trip information (nullable) |
| `trip.distance` | P1 | Navixy: `avl_io_199` (Trip Odometer) | Trip Odometer value |
| `trip.duration` | P1 | Navixy: `obd_time_since_engine_start` (OBD Engine Runtime), `avl_io_42` (Runtime since engine start) | Runtime since engine start |
| `nearby_assets[].id` | P2 | Navixy: `avl_io_385` (Beacon), `ble_beacon_id` (BLE Beacon ID) | List of Beacon IDs |

**Note:** All `last_changed_at` fields are computed by the Fleeti backend by comparing current values with previous telemetry packet values. For status fields, `last_changed_at` updates when the `code` changes (not on every packet). For location, a threshold is applied to filter GPS jitter (only significant position/heading changes trigger updates). These timestamps enable duration calculations and timeline features that improve customer experience.

| **Computation Rules:** See `Wiki/telemetry-status-rules.md` for definitive logic on status transitions, compatibility matrices, and priority ordering.

---

# 3. Location

**Purpose:** GPS/GNSS positioning data and location precision metrics.

## Structure

```json
{
  "location": {
    "latitude": "decimal degrees (-90 to 90)",
    "longitude": "decimal degrees (-180 to 180)",
    "altitude": "meters above sea level",
    "heading": "degrees (0-359, 0=North)",
    "cardinal_direction": "string (N, NE, E, SE, S, SW, W, NW)",
    "geocoded_address": "string",
    "last_changed_at": "ISO8601",
    "precision": {
      "hdop": "decimal (-1 to 20, -1=unknown)",
      "pdop": "decimal",
      "fix_quality": "integer (0=no fix, 1=fix)",
      "satellites": "integer (0-32)"
    }
  }
}
```

## Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
| --- | --- | --- | --- |
| `location.latitude` | P0 | Navixy: `lat` (Latitude) | Latitude in decimal degrees |
| `location.longitude` | P0 | Navixy: `lng` (Longitude) | Longitude in decimal degrees |
| `location.altitude` | P2 | Navixy: `alt` (Altitude) | Altitude in meters |
| `location.heading` | P0 | Navixy: `heading` (Heading) | Heading in degrees (0-359) |
| `location.cardinal_direction` | P1 | **Computed:** Derived from `location.heading` | Cardinal direction (N, NE, E, SE, S, SW, W, NW) |
| `location.geocoded_address` | P1 | **Computed:** Reverse geocoding (server-side) | Single string representation of the location |
| `location.last_changed_at` | P1 | **Computed:** Backend compares current position/heading with previous, using threshold to filter GPS jitter | ISO8601 timestamp when location/heading last changed significantly (threshold applied to filter GPS noise). Used for dwell-time calculations and "parked since X" features. |
| `location.precision.fix_quality` | T | Navixy: `avl_io_69` (GNSS Status) | 0 - GNSS OFF 1 – GNSS ON with fix 2 - GNSS ON without fix 3 - GNSS sleep 4 - GNSS ON with fix, invalid data |
| `location.precision.hdop` | T | Navixy: `avl_io_182` (GNSS HDOP), `hdop` (HDOP) | Horizontal Dilution of Precision |
| `location.precision.pdop` | T | Navixy: `avl_io_181` (GNSS PDOP), `pdop` (PDOP) | Position Dilution of Precision |
| `location.precision.satellites` | T | Navixy: `satellites` (Satellites) | Number of satellites in fix |

---

# 4. Connectivity

**Purpose:** Network and communication status information.

## Structure

```json
{
  "connectivity": {
    "signal_level": "integer (0-31, 99=unknown)",
    "operator": "string or integer code",
    "last_updated_at":"ISO",
    "data_mode": "integer (0-255)",
    "cell": {
      "id": "integer (0-65535)",
      "lac": "integer (0-65535)"
    },
    "sim": {
      "iccid": ["string"]
    }
  }
}
```

## Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
| --- | --- | --- | --- |
| `connectivity.cell.id` | T | Navixy: `avl_io_205` (GSM Cell ID) | GSM base station ID |
| `connectivity.cell.lac` | T | Navixy: `avl_io_206` (GSM Area Code) | Location Area Code (LAC). Depends on GSM operator. Provides unique number assigned to a set of base GSM stations. Used for cell tower identification. |
| `connectivity.data_mode` | P3 | Navixy: `avl_io_80` (Data Mode) | Used differently across models. Most commonly: GSM/LTE network mode / roaming status. Sometimes appears as "Data Mode" or network type indicator. Interpretation depends on device model and firmware version. |
| `connectivity.operator` | T | Navixy: `avl_io_241` (Active GSM Operator) | Currently used GSM Operator code |
| `connectivity.signal_level` | P1 | Navixy: `avl_io_21` (GSM Signal), `gsm.signal.csq` (GSM Signal CSQ) | Value in range 1-5 Explanation |
| `connectivity.sim.iccid[]` | T | Navixy: `avl_io_11` (ICCID1), `avl_io_14` (ICCID2) | Value of SIM ICCID, MSB |

---

# 5. Motion

**Purpose:** Dynamic movement data including speed and motion status.

## Structure

```json
{
  "motion": {
    "last_updated_at":"ISO",
    "speed": { "value": "number", "unit": "km/h" },
    "is_moving": {
      "value": "boolean",
      "last_changed_at": "ISO8601"
    },
    "instant_movement": "boolean",
    "accelerometer": {
      "x": "number (mG)",
      "y": "number (mG)",
      "z": "number (mG)"
    }
  }
}
```

## Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
| --- | --- | --- | --- |
| `motion.accelerometer.x` | P3 | Navixy: `avl_io_17` (Axis X), `axis_x` (Axis X) | X axis value |
| `motion.accelerometer.y` | P3 | Navixy: `avl_io_18` (Axis Y), `axis_y` (Axis Y) | Y axis value |
| `motion.accelerometer.z` | P3 | Navixy: `avl_io_19` (Axis Z), `axis_z` (Axis Z) | Z axis value |
| `motion.instant_movement` | P3 | Navixy: `avl_io_303` (Instant Movement) | **REQUIRES CLARIFICATION:** Semantic distinction from `motion.is_moving` unclear. Both are boolean movement indicators. Need to confirm with Navixy/GPS provider: What does "Instant Movement" represent vs. standard Movement detection? |
| `motion.is_moving.value` | P1 | Navixy: `avl_io_240` (Movement), `moving` (Is Moving) | 0 – Movement Off 1 – Movement On |
| `motion.is_moving.last_changed_at` | P1 | **Computed:** Backend compares current `is_moving.value` with previous | ISO8601 timestamp when `motion.is_moving.value` last changed. Used to show "vehicle stopped since X" and calculate dwell times. |
| `motion.speed` | P0 | Navixy: `can_speed` (CAN Speed), `obd_speed` (OBD Speed), `avl_io_24` (Speed), `avl_io_37` (Vehicle Speed), `avl_io_81` (Vehicle Speed), `speed` (Speed) | GNSS Speed |

---

# 6. Power

**Purpose:** Power source status, canonical ignition state, and battery health (asset/vehicle battery). Includes low-voltage electrical system and EV/hybrid traction battery systems.

## Structure

```json
{
  "power": {
    "last_updated_at": "ISO8601"
    "ignition": {"value":"boolean","last_changed_at": "ISO8601"},
    "low_voltage_battery": {
      "level": { "value": "number", "unit": "%" },
      "charging": "boolean"
    },
    "ev": {
      "traction_battery": {
        "level": { "value": "number", "unit": "%" }
      },
      "charging": {
        "active": "boolean",
        "last_changed_at": "ISO8601"
        "cable_plugged": "boolean"
      },
      "motor": {
        "last_changed_at": "ISO8601"
        "active": "boolean"
      },
      "range": {
        "estimated_distance": { "value": "number", "unit": "km" }
      }
    }
  }

```

**Notes:**

- **`power.ignition`**: Ignition state computed from multiple sources (ignition cable, CAN signals, RPM, or AVL combined sources). This is the primary ignition field used by the rest of the Fleeti system for status computation and business logic. Source priority: SSF Ignition (`avl_io_898`) > CAN ignition state > CAN engine state > AVL Ignition (`avl_io_239`).
- **`power.low_voltage_battery.*`**: Represents the vehicle's low-voltage electrical system battery (starter/board battery). Voltage level depends on the vehicle (12V, 24V, 48V, etc.).
- **`power.ev.traction_battery.*`**: Represents the high-voltage traction battery used for propulsion on EVs and hybrids. Only populated when the vehicle exposes these signals.
- **Raw engine diagnostic fields** (`engine.running`) are documented in Section 11 (Diagnostics) as they represent diagnostic signals that differ from ignition state (e.g., engine actually running vs ignition on).

## Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
| --- | --- | --- | --- |
| `power.ignition` | BL | **Logic:** Prefer `avl_io_898` (SSF Ignition); else `can_ignition_state`; else `can_engine_state`; else `avl_io_239` (Ignition). All sources provide equivalent ignition state information. | Ignition state (on/off). Computed from multiple sources (ignition cable, CAN signals, RPM, or AVL combined sources). Used by status computation and business logic. Source priority: SSF Ignition (`avl_io_898`) > CAN ignition state > CAN engine state > AVL Ignition (`avl_io_239`). |
| `power.ignition_last_changed_at` | BL | **Computed:** Backend compares current `ignition` value with previous | ISO8601 timestamp when `power.ignition` last changed. Used to show "ignition on since X", detect abnormal long ignition periods, and improve trip detection. |
| `power.low_voltage_battery.level` | P2 | Navixy: `can_battery_level` | Board/system battery level (%) – 12V, 24V, etc. |
| `power.low_voltage_battery.charging` | P2 | Navixy: `avl_io_915` (SSF Battery Charging) | 0 = not charging, 1 = charging (alternator / DC-DC) |
| `power.ev.traction_battery.level` | P1 | Navixy: `avl_io_152` (HV Battery Level) | HV / drive battery SOC in % |
| `power.ev.charging.cable_plugged` | P1 | Navixy: `avl_io_914` (SSF Charging Wire Plugged) | 0 = unplugged, 1 = plugged. Indicates charging cable is physically connected to the vehicle. |
| `power.ev.charging.active` | P1 | **Computed:** `cable_plugged = true` AND `traction_battery.level` is increasing over time | True when EV is actively charging (cable plugged AND battery level increasing). Note: Logic to be implemented in transformation pipeline based on battery level trend analysis. |
| `power.ev.motor.active` | BL | Navixy: `avl_io_916` (SSF Electric Engine State) | 0 = off, 1 = electric motor active |
| `power.ev.range.estimated_distance` | P1 | Navixy: `avl_io_304` (Vehicles Range On Battery) | Remaining range on battery |

---

# 7. Fuel

**Purpose:** Fuel system data including levels and consumption.

## Structure

```json
{
  "fuel": {
    "levels": [
      { "value": "number", "unit": "%" | "l" ,"last_updated_at": "ISO8601"}
    ],
    "consumption": {
      "last_updated_at": "ISO8601",
      "cumulative": { "value": "number", "unit": "l" },
      "rate": { "value": "number", "unit": "l/h" }
    },
    "energy": {
      "cng_status": "boolean",
      "fuel_type_code": "integer (0-255)"
    }
  }
}
```

## Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
| --- | --- | --- | --- |
| `fuel.consumption.cumulative` | P1 | Navixy: `can_consumption`, `can_consumption_relative`, `avl_io_103` (Fuel Used GPS), `avl_io_107` (Fuel Consumed (counted)), `avl_io_83` (Fuel Consumed) | Total fuel consumed (cumulative). Measured in liters. Sources include CAN consumption, GPS-calculated fuel used, and counted fuel consumed. |
| `fuel.consumption.rate` | P2 | Navixy: `can_fuel_rate` (CAN Fuel Rate), `avl_io_110` (Fuel Rate) | Fuel rate |
| `fuel.energy.cng_status` | P2 | Navixy: `avl_io_232` (CNG Status) | CNG Status |
| `fuel.levels[].value` | P1 | Navixy: `can_fuel_1`, `can_fuel_litres`, `avl_io_390` (OBD OEM Fuel Level), `obd_custom_fuel_litres`, `avl_io_201` (LLS 1 Fuel Level), `avl_io_203` (LLS 2 Fuel Level), `avl_io_210` (LLS 3 Fuel Level), `avl_io_212` (LLS 4 Fuel Level), `avl_io_234` (CNG Level), `avl_io_270` (BLE Fuel Level #1), `avl_io_273` (BLE Fuel Level #2), `avl_io_84` (Fuel Level), `avl_io_89` (Fuel level), `ble_lls_level_1` (fuel), `ble_lls_level_2` (fuel), `fuel_level` (Fuel Level), `lls_level_1` (LLS Level 1), `lls_level_2` (LLS Level 2), `lls_level_3` (LLS Level 3), `lls_level_4` (LLS Level 4) | Fuel level measured by LLS sensor via RS232/RS485 |
| `fuel.energy.fuel_type_code` | P2 | Navixy: `avl_io_759` (Fuel Type) | 0 Not available 1 Gasoline 2 Methanol 3 Ethanol 4 Diesel 5 LPG 6 CNG 7 Propane 8 Electric 9 Bifuel running Gasoline 1... |

---

# 8. Counters

**Purpose:** Accumulated counters for odometer and engine hours.

## Structure

```json
{
  "counters": {
    "odometer": { "value": "number", "unit": "km" },
    "engine_hours": { "value": "number", "unit": "h" }
  }
}
```

## Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
| --- | --- | --- | --- |
| `counters.engine_hours` | P1 | Navixy: `can_engine_hours` (CAN Engine Hours), `can_engine_hours_relative`, `avl_io_449` (Ignition On Counter), `avl_io_102` (Engine Worktime) | Total engine work time. Unit conversion may be required (some sources in seconds, others in hours). |
| `counters.odometer` | P1 | Navixy: `can_mileage` (CAN Mileage), `can_mileage_relative`, `avl_io_389` (OBD OEM Total Mileage), `obd_custom_odometer`, `avl_io_105` (Total Mileage (counted)), `avl_io_16` (Total Odometer), `avl_io_87` (Total Mileage), `hw_mileage` (Hardware Mileage), `raw_mileage` (Raw Mileage) | Total Vehicle Mileage |

---

# 9. Driving Behavior

**Purpose:** Daily aggregated driving metrics and eco-driving scores.

## Structure

```json
{
  "driving_behavior": {
    "brake_active": "boolean",
    "throttle_position": { "value": "number", "unit": "%" },
    "daily_summary": {
      "driving_duration": { "value": "number", "unit": "s" },
      "idling_duration": { "value": "number", "unit": "s" },
      "event_counts": {
        "excessive_idling": "integer",
        "harsh_acceleration": "integer",
        "harsh_braking": "integer",
        "harsh_cornering": "integer",
        "overspeed": "integer"
      },
      "eco_score": {
        "value": "number"
      }
    }
  }
}
```

## Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
| --- | --- | --- | --- |
| `driving_behavior.brake_active` | P3 | Navixy: `can_footbrake_state` (CAN Footbrake State), `avl_io_910` (SSF Footbrake Is Active) | 0 - Footbrake inactive 1 - Footbrake active |
| `driving_behavior.daily_summary.driving_duration` | P1 | Navixy: `Computed` | **Computed:** Cumulative time when the vehicle was actually moving (not just ignition on). Computed by backend based on motion data. Full implementation details will be documented in dedicated pages. |
| `driving_behavior.daily_summary.idling_duration` | P1 | Navixy: `Computed` | **Computed:** Cumulative time when the vehicle was idling (ignition on, not moving). Full implementation details and thresholds will be documented in dedicated pages. |
| `driving_behavior.daily_summary.event_counts.excessive_idling` | P2 | Navixy: `Computed` | **Computed:** Count of excessive idling events. The "excessive" threshold is configurable (for example, idling longer than X minutes). Full implementation details will be documented in dedicated pages. |
| `driving_behavior.daily_summary.event_counts.harsh_acceleration` | P1 | Navixy: `Computed` | **Computed:** Number of harsh acceleration events. Device and/or backend detect harsh accelerations based on thresholds and aggregate the count for the period. Detailed logic will be documented separately. |
| `driving_behavior.daily_summary.event_counts.harsh_braking` | P1 | Navixy: `Computed` | **Computed:** Number of harsh braking events aggregated over the period. Full threshold and detection logic will be documented in dedicated pages. |
| `driving_behavior.daily_summary.event_counts.harsh_cornering` | P1 | Navixy: `Computed` | **Computed:** Number of harsh cornering events aggregated over the period. Full threshold and detection logic will be documented in dedicated pages. |
| `driving_behavior.daily_summary.event_counts.overspeed` | P1 | Navixy: `Computed` | **Computed:** Number of overspeed events. Definition of overspeed (vehicle-specific limits vs. road-speed limits) is being finalized. Implementation details will be documented in dedicated pages. |
| `driving_behavior.daily_summary.eco_score.value` | P1 | Navixy: `avl_io_15` (Eco Score) | Eco-driving score value reported by device firmware (averaged events per distance). |
| `driving_behavior.throttle_position` | P3 | Navixy: `can_throttle` (CAN Throttle), `obd_throttle` (OBD Throttle), `avl_io_41` (Throttle Position), `avl_io_82` (Accelerator Pedal Position) | Throttle position |

---

# 10. Sensors

**Purpose:** External and internal sensor readings (temperature, humidity, battery, etc.).

## Structure

```json
{
  "sensors": {
    "environment": [
      {
        "id": "string",
        "label": "string",
        "position": "integer",
        "temperature": { "value": "number", "unit": "°C" },
        "humidity": { "value": "number", "unit": "%" },
        "battery": { "value": "number", "unit": "%" },
        "frequency": { "value": "number", "unit": "Hz" },
        "last_updated_at": "ISO8601"
      }
    ],
    "magnet": [
      {
        "id": "string",
        "label": "string",
        "position": "integer",
        "state": "state",
        "last_updated_at": "ISO8601",
        "last_changed_at": "ISO8601"
      }
    ],
    "inertial": [
      {
        "id": "string",
        "label": "string",
        "position": "integer",
        "last_updated_at": "ISO8601",
        "pitch": { "value": "number", "unit": "°" },
        "roll": { "value": "number", "unit": "°" }
      }
    ],
    "custom": [
      {
        "id": "string",
        "label": "string",
        "position": "integer",
        "last_updated_at": "ISO8601",
        "values": [
          { "value": "number | string", "unit": "string" }
        ]
      }
    ]
  }
}
```

## Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
| --- | --- | --- | --- |
| `sensors.environment[].id` | P1 | Navixy: `avl_io_76` (Dallas Temperature ID 1), `avl_io_77` (Dallas Temperature ID 2) | Sensor identifier (e.g., Dallas sensor ID). Identity metadata is also derived from `asset.accessories[].sensors[]` (Section 1). |
| `sensors.environment[].temperature` | P1 | Navixy: `avl_io_202` (LLS 1 Temperature), `avl_io_204` (LLS 2 Temperature), `avl_io_25` (BLE Temperature #1), `avl_io_26` (BLE Temperature #2), `avl_io_27` (BLE Temperature #3), `avl_io_28` (BLE Temperature #4), `avl_io_72` (Dallas Temperature 1), `avl_io_73` (Dallas Temperature 2), `ble_temp_sensor_1` (BLE Temp 1), `ble_temp_sensor_2` (BLE Temp 2), `ble_temp_sensor_3` (BLE Temp 3), `ble_temp_sensor_4` (BLE Temp 4), `ext_temp_sensor_1` (External Temp 1), `ext_temp_sensor_2` (External Temp 2), `ext_temp_sensor_3` (External Temp 3), `lls_temperature_1` (LLS Temperature 1), `lls_temperature_2` (LLS Temperature 2), `temp_sensor` (Temperature Sensor) | Temperature readings from LLS, BLE, Dallas, and external sensors. Measured in degrees Celsius. |
| `sensors.environment[].humidity` | P1 | Navixy: `avl_io_86` (BLE Humidity #1), `avl_io_104` (BLE Humidity #2), `avl_io_106` (BLE Humidity #3), `avl_io_108` (BLE Humidity #4), `ble_humidity_1` (BLE Humidity 1), `ble_humidity_2` (BLE Humidity 2), `ble_humidity_3`, `ble_humidity_4`, `humidity_1` (Humidity 1), `humidity_2` (Humidity 2) | Relative humidity readings from environmental sensors (BLE probes, LLS/external humidity sensors, or other accessories). Measured in percent (%). |
| `sensors.environment[].battery` | T | Navixy: `avl_io_20` (BLE Battery #2), `avl_io_22` (BLE Battery #3), `avl_io_23` (BLE Battery #4), `ble_battery_level_2` (BLE Battery 2), `ble_battery_level_3` (BLE Battery 3), `ble_battery_level_4` (BLE Battery 4) | Battery level of BLE environmental sensors. Measured in percentage. |
| `sensors.environment[].frequency` | P3 | Navixy: `avl_io_306` (BLE Fuel Frequency #1), `ble_frequency_1` (BLE Frequency 1), `freq_1` (Frequency 1), `freq_2` (Frequency 2) | Frequency readings from BLE sensors. Measured in Hz. |
| `sensors.magnet[].value` | P1 | Navixy: `ble_magnet_sensor_1` (BLE Magnet Sensor 1), `ble_magnet_sensor_2` (BLE Magnet Sensor 2), `ble_magnet_sensor_3` (BLE Magnet Sensor 3) | Magnetic field sensor readings. Value represents sensor state (typically 0 = no magnetic field detected, 1 = magnetic field detected). Used for door/window position detection or security applications. |
| `sensors.inertial[].pitch` | P1 | Navixy: `ble_pitch_1` (BLE Pitch 1), `ble_pitch_2` (BLE Pitch 2) | Pitch angle from inertial sensors. Measured in degrees. |
| `sensors.inertial[].roll` | P1 | Navixy: `ble_roll_1` (BLE Roll 1), `ble_roll_2` (BLE Roll 2) | Roll angle from inertial sensors. Measured in degrees. |
| `sensors.custom[].values[]` | P2 | Navixy: `avl_io_331` (BLE 1 Custom #1), `avl_io_332` (BLE 2 Custom #1), `avl_io_333` (BLE 3 Custom #1), `avl_io_463` (BLE 1 Custom #2), `avl_io_464` (BLE 1 Custom #3), `avl_io_465` (BLE 1 Custom #4), `avl_io_466` (BLE 1 Custom #5), `avl_io_467` (BLE 2 Custom #2), `avl_io_468` (BLE 2 Custom #3), `avl_io_469` (BLE 2 Custom #4), `avl_io_470` (BLE 2 Custom #5), `avl_io_471` (BLE 3 Custom #2), `avl_io_472` (BLE 3 Custom #3), `avl_io_473` (BLE 3 Custom #4) | Custom IO element values from BLE sensors. Can be numeric or string depending on sensor configuration. |

**Note:** Sensor identity metadata (`id`, `label`, `position`) is derived from `asset.accessories[].sensors[]` (Section 1). Section 10 provides the per-sensor measurement view (telemetry data), not the final frontend structure. Multiple channels from the same physical sensor are grouped within a single sensor object. The structure is generic and works for BLE, LLS, external, Dallas, and other sensor protocols.

> Note: Some accessories expose both temperature and humidity (for example BLE environmental probes), while others expose only humidity (for example humidity-only probes). All of these are represented as sensors.environment[] entries; channels that are not available for a given sensor are simply omitted.
> 

---

# 11. Diagnostics

**Purpose:** Detailed asset diagnostics, including CAN bus data, engine stats, and body sensors.

## Structure

```json
{
  "diagnostics": {
    "agricultural": {
      "last_updated_at": "ISO8601",
      "area_harvested": { "value": "number", "unit": "m2" },
      "grain_moisture": { "value": "number", "unit": "%" },
      "grain_volume": { "value": "number", "unit": "kg" },
      "harvest_duration": { "value": "number", "unit": "s" },
      "harvesting_drum_gap": { "value": "number", "unit": "mm" },
      "harvesting_drum_rpm": { "value": "number", "unit": "rpm" },
      "mowing_efficiency": { "value": "number", "unit": "m2/h" },
      "state_flags": "integer | hex"
    },
    "axles": {
      "weights": [
        {
          "position": "integer",
          "value": "number",
          "unit": "kg",
          "last_updated_at": "ISO8601",
        }
      ]
    },
    "body": {
      "belts": {
        "last_updated_at": "ISO8601",
        "driver": "boolean",
        "passenger": "boolean",
        "rear_left": "boolean",
        "rear_right": "boolean",
        "rear_centre": "boolean"
      },
      "doors": {
        "last_updated_at": "ISO8601",
        "front_left": "boolean",
        "front_right": "boolean",
        "rear_left": "boolean",
        "rear_right": "boolean",
        "trunk": "boolean",
        "hood": "boolean",
        "roof": "boolean",
        "engine_cover": "boolean"
      },
      "lights": {
        "last_updated_at": "ISO8601",
        "dipped_headlights": "boolean",
        "full_beam_headlights": "boolean",
        "front_fog_lights": "boolean",
        "rear_fog_lights": "boolean",
        "parking_lights": "boolean",
        "additional_front_fog_lights": "boolean",
        "additional_rear_lights": "boolean",
        "light_signal": "boolean",
        "lights_failure": "boolean"
      },
      "indicators": {
        "state_flags": "integer | hex",
        "cistern_state_flags": "integer | hex"
      },
      "occupancy": {
        "front_passenger": "boolean"
      },
      "safety": {
        "airbag_state": "boolean"
      },
      "climate": {
        "air_conditioning": "boolean"
      }
    },
    "brakes": {
      "abs_active": "boolean",
      "pad_wear": { "value": "number", "unit": "%" },
      "parking_brake": "boolean",
      "retarder_automatic": "boolean",
      "retarder_manual": "boolean"
    },
    "drivetrain": {
      "last_updated_at": "ISO8601",
      "central_differential_4hi_locked": "boolean",
      "central_differential_4lo_locked": "boolean",
      "clutch_state": "boolean",
      "cruise_control_active": "boolean",
      "front_differential_locked": "boolean",
      "rear_differential_locked": "boolean"
    },
    "engine": {
      "last_updated_at": "ISO8601",
      "running": {
        "value": "boolean",
        "last_changed_at": "ISO8601"
      },
      "coolant_temperature": { "value": "number", "unit": "°C" },
      "glow_plug_active": "boolean",
      "load": { "value": "number", "unit": "%" },
      "pto_state": "boolean",
      "ready_to_drive": "boolean",
      "rpm": { "value": "number", "unit": "rpm" },
      "start_stop_inactive": "boolean",
      "temperature": { "value": "number", "unit": "°C" },
      "webasto_state": "boolean",
      "key_inserted": "boolean"
    },
    "fluids": {
      "last_updated_at": "ISO8601",
      "adblue_level": { "value": "number", "unit": "l | %" },
      "oil": {
        "pressure": { "value": "number", "unit": "kPa | psi" }
      }
    },
    "health": {
      "last_updated_at": "ISO8601",
      "can_warning": "boolean",
      "dtc_count": "integer",
      "electronics_power_control": "boolean",
      "battery_not_charging": "boolean",
      "low_fuel_warning": "boolean",
      "low_oil_warning": "boolean",
      "low_tire_pressure_warning": "boolean",
      "mil_activated_distance": { "value": "number", "unit": "km" },
      "mil_status": "integer"
    },
    "security": {
      "last_updated_at": "ISO8601",
      "state_flags": "integer | hex",
      "immobilizer": {
        "engine_lock_active": "boolean",
        "request_lock_engine": "boolean"
      }
    },
    "systems": {
      "last_updated_at": "ISO8601",
      "steering": {
        "eps_state": "boolean"
      },
      "trailer": {
        "axle_lift_active": "boolean[]"
      },
      "control": {
        "state_flags": "integer | hex"
      },
      "utility": {
        "state_flags": "integer | hex"
      }
    }
  }
}
```

## Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
| --- | --- | --- | --- |
| `diagnostics.agricultural.area_harvested` | P2 | Navixy: `avl_io_126` (Area of Harvest) | Area of harvest in square meters |
| `diagnostics.agricultural.grain_moisture` | P2 | Navixy: `avl_io_129` (Grain Moisture) | Grain moisture |
| `diagnostics.agricultural.grain_volume` | P2 | Navixy: `avl_io_128` (Grain Mown Volume) | Mown volume |
| `diagnostics.agricultural.harvest_duration` | P2 | Navixy: `avl_io_125` (Harvest Duration) | Duration of harvesting activity (agricultural CAN signal). |
| `diagnostics.agricultural.harvesting_drum_gap` | P2 | Navixy: `avl_io_131` (Gap Under Harvesting Drum) | Gap under harvesting drum |
| `diagnostics.agricultural.harvesting_drum_rpm` | P2 | Navixy: `avl_io_130` (Harvesting Drum RPM) | Harvesting drum rpm |
| `diagnostics.agricultural.mowing_efficiency` | P2 | Navixy: `avl_io_127` (Mowing Efficiency) | Mowing efficiency |
| `diagnostics.axles.weights[]` | P2 | Navixy: `can_axle_load_1` (CAN Axle Load 1), `can_axle_load_2` (CAN Axle Load 2), `can_axle_load_3` (CAN Axle Load 3), `can_axle_load_4` (CAN Axle Load 4), `can_axle_load_5` (CAN Axle Load 5), `avl_io_118` (Axle 1 Load), `avl_io_119` (Axle 2 Load), `avl_io_120` (Axle 3 Load), `avl_io_121` (Axle 4 Load), `avl_io_122` (Axle 5 Load) | Axle weight measurements. Each entry includes position (1-5) and weight in kg. Sources include CAN axle load signals and AVL IO parameters. |
| `diagnostics.body.belts.*` | P2 | Navixy: `can_rear_centre_seat_belt_state` (CAN Rear Centre Seat Belt State), `can_rear_left_seat_belt_state` (CAN Rear Left Seat Belt State), `can_rear_right_seat_belt_state` (CAN Rear Right Seat Belt State), `can_seat_belt_driver_state` (CAN Seat Belt Driver State), `can_seat_belt_passenger_state` (CAN Passenger Seat Belt State), `avl_io_940` (CSF Driver's Seatbelt Fastened), `avl_io_941` (CSF Front Driver's Seatbelt Fastened), `avl_io_942` (CSF Left Driver's Seatbelt Fastened), `avl_io_943` (CSF Right Driver's Seatbelt Fastened), `avl_io_944` (CSF Centre Driver's Seatbelt Fastened) | Seatbelt fastening status for driver, passenger, and rear seats (left, right, centre). Values: 0 = not fastened, 1 = fastened. |
| `diagnostics.body.doors.*` | P2 | Navixy: `can_door_state` (CAN Door State), `can_front_left_door` (CAN Front Left Door), `can_front_right_door` (CAN Front Right Door), `can_hood_state` (CAN Hood State), `can_rear_left_door` (CAN Rear Left Door), `can_rear_right_door` (CAN Rear Right Door), `can_roof_state` (CAN Roof State), `can_trunk_state` (CAN Trunk State), `avl_io_90` (Door Status), `avl_io_654` (SSF Front Left Door Open), `avl_io_655` (SSF Front Right Door Open), `avl_io_656` (SSF Rear Left Door Open), `avl_io_657` (SSF Rear Right Door Open), `avl_io_658` (SSF Trunk Door Open), `avl_io_913` (SSF Engine Cover Open) | Door/hatch/cover open/closed status. Includes front doors (left, right), rear doors (left, right), trunk, hood, roof, and engine cover. Values: 0 = closed, 1 = open. |
| `diagnostics.body.lights.*` | P3 | Navixy: `can_additional_front_fog_lights` (CAN Additional Front Fog Lights), `can_additional_rear_lights` (CAN Additional Rear Lights), `can_dipped_headlights` (CAN Dipped Headlights), `can_front_fog_lights` (CAN Front Fog Lights), `can_full_beam_headlights` (CAN Full Beam Headlights), `can_light_signal` (CAN Light Signal), `can_lights_failure` (CAN Lights Failure), `can_parking_lights` (CAN Parking Lights), `can_rear_fog_lights` (CAN Rear Fog Lights), `avl_io_935` (CSF Light Signal) | Vehicle lighting system status. Includes headlights (dipped, full beam), fog lights (front, rear, additional), parking lights, light signal, and lights failure indicator. Values: 0 = off, 1 = on. |
| `diagnostics.brakes.abs_active` | P3 | Navixy: `can_abs_state` (CAN ABS State) | CAN ABS State |
| `diagnostics.brakes.pad_wear` | P2 | Navixy: `can_brake_pad_wear` (CAN Brake Pad Wear) | Brake pad wear level from CAN bus. Measured in percentage (0-100%). Indicates remaining brake pad thickness. Lower values indicate more wear. |
| `diagnostics.brakes.parking_brake` | P3 | Navixy: `can_hand_brake_state` (CAN Hand Brake), `avl_io_653` (SSF Handbrake Is Active) | 0 - Handbrake inactive 1 - Handbrake active |
| `diagnostics.brakes.retarder_automatic` | P2 | Navixy: `can_automatic_retarder` (CAN Automatic Retarder) | CAN Automatic Retarder |
| `diagnostics.brakes.retarder_manual` | P2 | Navixy: `can_manual_retarder` (CAN Manual Retarder) | CAN Manual Retarder |
| `diagnostics.body.climate.air_conditioning` | P2 | Navixy: `can_air_conditioning`, `avl_io_936` (CSF Air Conditioning) | 0 - Off 1 - On |
| `diagnostics.drivetrain.central_differential_4hi_locked` | P3 | Navixy: `can_central_diff_4hi_locked` (CAN Central Diff 4HI Locked) | CAN Central Diff 4HI Locked |
| `diagnostics.drivetrain.central_differential_4lo_locked` | P3 | Navixy: `can_central_diff_4lo_locked` (CAN Central Diff 4LO Locked) | CAN Central Diff 4LO Locked |
| `diagnostics.drivetrain.clutch_state` | P3 | Navixy: `can_clutch_state` (CAN Clutch State) | CAN Clutch State |
| `diagnostics.drivetrain.cruise_control_active` | P2 | Navixy: `can_cruise_control` (CAN Cruise Control) | CAN Cruise Control |
| `diagnostics.drivetrain.front_differential_locked` | P3 | Navixy: `can_front_diff_locked` (CAN Front Diff Locked), `avl_io_947` (CSF Front Differential Locked) | 0 - Unlocked 1 - Locked |
| `diagnostics.drivetrain.rear_differential_locked` | P3 | Navixy: `can_rear_diff_locked` (CAN Rear Diff Locked), `avl_io_948` (CSF Rear Differential Locked) | 0 - Unlocked 1 - Locked |
| `diagnostics.engine.running.value` | BL | Navixy: `avl_io_900` (SSF Engine Working) | Engine actually running (motor state). Note: This is diagnostic data; may differ from `power.ignition` if ignition cable is not connected to motor level. |
| `diagnostics.engine.running.last_changed_at` | BL | **Computed:** Backend compares current `running.value` with previous | ISO8601 timestamp when `diagnostics.engine.running.value` last changed. Used to calculate true engine running duration (vs ignition on), important for fuel consumption and maintenance tracking. |
| `diagnostics.engine.coolant_temperature` | P2 | Navixy: `can_coolant_temp_or_level` (CAN Coolant Temp or Level) | Engine coolant temperature from cooling system. Measured in degrees Celsius (°C). |
| `diagnostics.engine.glow_plug_active` | P2 | Navixy: `can_glow_plug_indicator` (CAN Glow Plug Indicator) | CAN Glow Plug Indicator |
| `diagnostics.engine.load` | P2 | Navixy: `can_engine_load` (CAN Engine Load), `avl_io_114` (Engine Load) | Engine Load |
| `diagnostics.engine.pto_state` | P2 | Navixy: `can_pto_state` (CAN PTO State) | CAN PTO State |
| `diagnostics.engine.ready_to_drive` | P3 | Navixy: `can_ready_to_drive` (CAN Ready to Drive), `avl_io_902` (SSF Ready To Drive) | CAN Ready to Drive. Present on EV/hybrid and some modern ICE vehicles. |
| `diagnostics.engine.rpm` | P2 | Navixy: `can_rpm` (CAN Engine RPM), `obd_rpm` (OBD RPM), `avl_io_36` (Engine RPM), `avl_io_85` (Engine RPM) | Engine RPM |
| `diagnostics.engine.start_stop_inactive` | P3 | Navixy: `avl_io_1086` (CSF Start Stop System Inactive) | 0 - No 1 - Yes |
| `diagnostics.engine.temperature` | P2 | Navixy: `can_engine_temp` (CAN Engine Temp), `avl_io_115` (Engine Temperature) | Engine Temperature |
| `diagnostics.engine.webasto_state` | P2 | Navixy: `can_webasto_state` (CAN Webasto State) | CAN Webasto State |
| `diagnostics.fluids.adblue_level` | P1 | Navixy: `can_adblue_level` (CAN AdBlue Level), `avl_io_111` (AdBlue Level), `avl_io_112` (AdBlue Level) | AdBlue/DEF fluid level. May be reported in liters or percentage depending on source. |
| `diagnostics.fluids.oil.pressure` | P2 | Navixy: `can_oil_pressure_or_level` (CAN Oil Pressure or Level) | Engine oil pressure. Measured in kPa or psi depending on source. |
| `diagnostics.health.low_oil_warning` | P1 | Navixy: `avl_io_235` (Oil Level) | Low engine oil level warning indicator. Values: 0 = normal, 1 = low oil warning. |
| `diagnostics.health.battery_not_charging` | P1 | Navixy: `avl_io_960` (ISF Battery Not Charging Indicator) | Battery not charging warning indicator. Values: 0 = off, 1 = on. Indicates that the low-voltage system battery is not being charged (alternator/DC-DC issue). |
| `diagnostics.health.can_warning` | P1 | Navixy: `can_warning` (CAN Warning) | CAN bus warning indicator. Values: 0 = no warning, 1 = warning present. Indicates general CAN bus communication or system warnings detected by the vehicle's diagnostic system. Read from CAN bus. |
| `diagnostics.health.dtc_count` | P1 | Navixy: `obd_dtc_number` (OBD DTC Count), `avl_io_30` (Number of DTC) | Number of DTC |
| `diagnostics.health.electronics_power_control` | P2/P3 | Navixy: `can_electronics_power_control` (CAN Electronics Power Control) | Electronics power control state from CAN bus. Values: 0 = normal operation, 1 = power control active. Indicates power management system status (e.g., power saving mode, normal operation, reduced power mode). Interpretation depends on vehicle manufacturer and model. |
| `diagnostics.health.low_fuel_warning` | P1 | Navixy: `can_low_fuel` (CAN Low Fuel) | Low fuel warning indicator from CAN bus. Values: 0 = normal, 1 = low fuel warning. |
| `diagnostics.health.low_tire_pressure_warning` | P1 | Navixy: `can_low_tire_pressure`, `avl_io_966` (ISF Low Tire Pressure Indicator) | 0 - Off 1 - On |
| `diagnostics.health.mil_activated_distance` | P1 | Navixy: `obd_mil_activated_distance` (OBD MIL Activated Distance), `avl_io_43` (Distance Traveled MIL On) | Distance traveled with MIL (Malfunction Indicator Lamp) activated. Measured in kilometers (km). Indicates how far the vehicle has traveled since the MIL was triggered. |
| `diagnostics.health.mil_status` | P1 | Navixy: `obd_mil_status` (OBD MIL Status) | Malfunction Indicator Lamp (MIL) status from OBD. Values depend on OBD protocol version. Typically: 0 = MIL off (no faults), 1 = MIL on (fault detected). Related to DTC count (`diagnostics.health.dtc_count`). When MIL is on, diagnostic trouble codes are present and should be checked. |
| `diagnostics.engine.key_inserted` | P3 | Navixy: `avl_io_652` (SSF KeyInIgnitionLock) | 0 - No key in lock 1 - Key in lock |
| `diagnostics.body.occupancy.front_passenger` | P2 | Navixy: `can_front_passenger_presence` (CAN Front Passenger Presence), `avl_io_945` (CSF Front Passenger Present) | 0 - Not present 1 - Present |
| `diagnostics.body.safety.airbag_state` | P2 | Navixy: `can_airbag_state` (CAN Airbag State) | Airbag system state from CAN bus. Values: 0 = airbag system inactive/normal, 1 = airbag system active/warning. Indicates airbag system status and potential safety issues. |
| `diagnostics.systems.steering.eps_state` | P2 | Navixy: `can_eps_state` (EPS State) | Electric Power Steering (EPS) system state. Values: 0 = inactive/normal, 1 = active/warning. Indicates EPS system operational status. When active, the EPS system is engaged and assisting steering. Warning state may indicate system faults or reduced assistance. Read from CAN bus. |
| `diagnostics.systems.trailer.axle_lift_active[]` | P1 | Navixy: `can_trailer_axle_lift_active_1` (CAN Trailer Axle Lift Active 1), `can_trailer_axle_lift_active_2` (CAN Trailer Axle Lift Active 2) | Trailer axle lift active status. Array of boolean values, one per trailer axle. Values: false = axle down (normal position), true = axle lifted. Used for load distribution control and to reduce wear on specific axles when trailer is empty or lightly loaded. Read from CAN bus. |
| `diagnostics.agricultural.state_flags` | P1 | Navixy: `avl_io_124` (Agricultural Machinery Flags), `avl_io_520` (Agricultural State Flags P4) | Agricultural machinery state flags (bitmask). Encodes various agricultural equipment states. Format: integer or hex depending on source. |
| `diagnostics.body.indicators.state_flags` | P1 | Navixy: `avl_io_519` (Indicator State Flags P4) | Vehicle indicator state flags (bitmask, Protocol 4). Encodes various indicator states (e.g. turn indicators, warning lamps). Format: integer or hex. |
| `diagnostics.body.indicators.cistern_state_flags` | P2 | Navixy: `avl_io_522` (Cistern State Flags P4) | Cistern/tank state flags (bitmask, Protocol 4). Encodes cistern-related equipment states. Format: integer or hex. |
| `diagnostics.systems.control.state_flags` | P2 | Navixy: `avl_io_123` (Control State Flags), `avl_io_518` (Control State Flags P4) | Vehicle control system state flags (bitmask). Encodes control system states. Format: integer or hex depending on source. |
| `diagnostics.security.state_flags` | P2 | Navixy: `avl_io_132` (Security State Flags), `avl_io_517` (Security State Flags P4) | Security system state flags (bitmask). Encodes security-related states. Format: integer or hex depending on source. |
| `diagnostics.security.immobilizer.engine_lock_active` | P2 | Navixy: `avl_io_907` (SSF Engine Lock Active) | Engine lock active status. Values: 0 = inactive, 1 = active. Indicates whether the engine is currently locked by the immobilizer system. Used for immobilization status computation. |
| `diagnostics.security.immobilizer.request_lock_engine` | P2 | Navixy: `avl_io_908` (SSF Request To Lock Engine) | Request to lock engine status. Values: 0 = off, 1 = on. Indicates a request/command to lock the engine has been sent. Used for immobilization status computation. |
| `diagnostics.systems.utility.state_flags` | P2 | Navixy: `avl_io_521` (Utility State Flags P4) | Utility vehicle/equipment state flags (bitmask, Protocol 4). Encodes utility equipment states. Format: integer or hex. |

---

# 12. I/O (Inputs/Outputs)

**Purpose:** Digital and analog input/output states.

## Structure

```json
{
  "io": {
    "last_updated_at": "ISO8601",
    "inputs": {
      "individual": {
        "input_1": "boolean",
        "input_2": "boolean",
        "input_3": "boolean",
        "input_4": "boolean"
      }
    },
    "outputs": {
      "individual": {
        "output_1": "boolean",
        "output_2": "boolean",
        "output_3": "boolean"
      }
    },
    "analog": {
      "input_1": { "value": "number", "unit": "V" },
      "input_2": { "value": "number", "unit": "V" }
    }
  }
}
```

**Note:** I/O fields represent raw digital and analog input/output states from the tracking device. These fields are **not displayed to end customers** but are available to **Fleeti super admin users** for troubleshooting and diagnostic purposes.

I/O values are used elsewhere in the Fleeti application to compute semantic fields:

- **Digital inputs** (e.g., `io.inputs.individual.input_1`) are mapped to semantic meanings based on installation metadata (e.g., input_1 = ignition cable, input_2 = door sensor, etc.). These are used to compute canonical states like `power.ignition` and `diagnostics.body.doors.*`.
- **Digital outputs** (e.g., `io.outputs.individual.output_2`) are mapped based on installation metadata (e.g., output_2 = immobilizer relay). These are used for immobilization control and status computation.
- **Analog inputs** (e.g., `io.analog.input_1`) are similarly mapped based on installation metadata and may be used to compute fuel levels, temperature readings, or other sensor values.

**Important:** In the Fleeti telemetry schema, I/O fields are **interpretable as-is** (raw device values). The semantic mapping (which input/output represents what function) is defined in `asset.installation.*` metadata (Section 1) and is used by the transformation pipeline to compute canonical fields. The I/O section provides the raw, uninterpreted device states for troubleshooting and debugging.

## Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
| --- | --- | --- | --- |
| `io.inputs.individual.input_1` | BL | Navixy: `avl_io_1` (Digital Input 1), `din` (Digital Inputs Bitmask, bit 0) | Digital input 1 state. Values: 0 = low/inactive, 1 = high/active. Semantic meaning (e.g., ignition, door sensor) is defined in `asset.installation.*` metadata. Used to compute canonical fields like `power.ignition`. If only bitmask is available, transformation pipeline extracts bit 0. |
| `io.inputs.individual.input_2` | BL | Navixy: `avl_io_2` (Digital Input 2), `din` (Digital Inputs Bitmask, bit 1) | Digital input 2 state. Values: 0 = low/inactive, 1 = high/active. Semantic meaning defined in installation metadata. If only bitmask is available, transformation pipeline extracts bit 1. |
| `io.inputs.individual.input_3` | BL | Navixy: `avl_io_3` (Digital Input 3), `din` (Digital Inputs Bitmask, bit 2) | Digital input 3 state. Values: 0 = low/inactive, 1 = high/active. Semantic meaning defined in installation metadata. If only bitmask is available, transformation pipeline extracts bit 2. |
| `io.inputs.individual.input_4` | BL | Navixy: `avl_io_4` (Pulse Counter Din1), `din` (Digital Inputs Bitmask, bit 3) | Digital input 4 state (also functions as pulse counter). Values: 0 = low/inactive, 1 = high/active. Pulse count resets when records are saved. Semantic meaning defined in installation metadata. If only bitmask is available, transformation pipeline extracts bit 3. |
| `io.outputs.individual.output_1` | BL | Navixy: `avl_io_179` (Digital Output 1), `outputs` (Output Status Bitmask, bit 0) | Digital output 1 state. Values: 0 = inactive, 1 = active. Semantic meaning (e.g., immobilizer relay) is defined in `asset.installation.*` metadata. Used for immobilization control and status computation. If only bitmask is available, transformation pipeline extracts bit 0. |
| `io.outputs.individual.output_2` | BL | Navixy: `avl_io_180` (Digital Output 2), `outputs` (Output Status Bitmask, bit 1) | Digital output 2 state. Values: 0 = inactive, 1 = active. Semantic meaning defined in installation metadata. If only bitmask is available, transformation pipeline extracts bit 1. |
| `io.outputs.individual.output_3` | BL | Navixy: `avl_io_380` (Digital Output 3), `outputs` (Output Status Bitmask, bit 2) | Digital output 3 state. Values: 0 = inactive, 1 = active. Semantic meaning defined in installation metadata. If only bitmask is available, transformation pipeline extracts bit 2. |
| `io.analog.input_1` | BL | Navixy: `avl_io_9` (Analog Input 1), `adc` (analog) | Analog input 1 voltage reading. Measured in volts (V). Prefer `avl_io_9` over generic `adc` when available. Semantic meaning (e.g., fuel level sensor, temperature probe) is defined in installation metadata. Used to compute canonical sensor/fluid fields. |
| `io.analog.input_2` | BL | Navixy: `avl_io_6` (Analog Input 2), `adc` (analog) | Analog input 2 voltage reading. Measured in volts (V). Prefer `avl_io_6` over generic `adc` when available. Semantic meaning defined in installation metadata. Used to compute canonical sensor/fluid fields. |

---

# 13. Driver

**Purpose:** Driver identification and related events.

## Structure

```json
{
  "driver": {
    "id": {
      "value": "string | null",
      "last_changed_at": "ISO8601"
    },
    "name": "string | null",
    "privacy_mode": {
      "value": "boolean",
      "last_changed_at": "ISO8601"
    },
    "authorization": {
      "state": "integer (0-2)"
    },
    "hardware_key": {
      "value": "string",
      "extended_id": "string | null"
    }
  }
}
```

**Note:** Driver identification works as follows:

- **Hardware key detection**: The tracking device detects a hardware key (iButton or RFID) and reports it as `hardware_key.value` (hex string). The backend determines the key type (iButton vs RFID) based on the device model and signal characteristics.
- **Driver lookup**: The backend looks up the hardware key in the Fleeti driver catalog to find the associated driver. If found, `id` and `name` are populated. If not found (new/unknown key), `id` and `name` are `null`.
- **Unknown drivers**: When a new hardware key is detected that isn't in the catalog, `driver.id.value` and `driver.name` will be `null`. Fleet managers can then create a new driver object in the Fleeti catalog and associate it with the hardware key.
- **Extended ID**: `hardware_key.extended_id`. The usefulness of this field for driver identification is still being evaluated (TBD).
- **Authorization state**: `authorization.state` indicates iButton connection status in the context of immobilizer authorization (0 = no key, 1 = key connected but immobilizer active, 2 = key connected and authorized for driving).

## Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
| --- | --- | --- | --- |
| `driver.id.value` | P1 | **Computed:** Lookup `hardware_key.value` in Fleeti driver catalog | Fleeti driver ID from catalog. `null` if hardware key is not found in catalog (unknown driver). |
| `driver.id.last_changed_at` | P1 | **Computed:** Backend compares current `id.value` with previous | ISO8601 timestamp when `driver.id.value` last changed. Used to show driver-vehicle association timeline and determine which driver was responsible at time of events. |
| `driver.name` | P1 | **Computed:** Lookup `hardware_key.value` in Fleeti driver catalog | Driver name from catalog. `null` if hardware key is not found in catalog (unknown driver). |
| `driver.privacy_mode.value` | P1 | Navixy: `avl_io_391` (Private mode) | Private mode state. Values: 0 = Private mode off, 1 = Private mode on. Driver setting that indicates whether the driver has activated private/work mode. |
| `driver.privacy_mode.last_changed_at` | P1 | **Computed:** Backend compares current `privacy_mode.value` with previous | ISO8601 timestamp when `driver.privacy_mode.value` last changed. Used to show "private mode active since X" and separate private vs business time in reports. |
| `driver.authorization.state` | T | Navixy: `avl_io_248` (Immobilizer) | iButton connection status in immobilizer context. Values: 0 = iButton not connected, 1 = iButton connected (Immobilizer active), 2 = iButton connected (Authorized Driving). Note: Field name is "Immobilizer" but represents iButton authorization state. |
| `driver.hardware_key.value` | BL | Navixy: `avl_io_78` (iButton), `avl_io_207` (RFID), `ibutton` (iButton ID) | Hardware key identifier as hex string. Can be iButton or RFID code. Backend determines key type based on device model and signal characteristics. Used to lookup driver in Fleeti catalog. |
| `driver.hardware_key.extended_id` | BL/P3 | Navixy: `avl_io_238` (User ID) | MAC address of NMEA receiver device connected via Bluetooth. Usefulness for driver identification is still being evaluated (TBD). May be `null` if not available. |

---

# 14. Device

**Purpose:** Tracking device status, configuration, and security.

## Structure

```json
{
  "device": {
    "last_updated_at": "ISO8601",
    "battery": {
      "current": { "value": "number", "unit": "A" },
      "level": { "value": "number", "unit": "%" },
      "voltage": { "value": "number", "unit": "V" }
    },
    "bluetooth": {
      "status": "integer (0-4)"
    },
    "power": {
      "board_voltage": { "value": "number", "unit": "V" },
      "connected": "boolean",
      "external_voltage": { "value": "number", "unit": "V" }
    },
    "sleep_mode": "integer (0-4)",
    "status_bitmap": "integer",
    "firmware": {
      "version": "integer"
    },
    "identification": {
      "module_id_17b": "string",
      "module_id_8b": "string"
    }
  }
}
```

## Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
| --- | --- | --- | --- |
| `device.battery.current` | T | Navixy: `avl_io_68` (Battery Current), `battery_current` (Battery Current) | Device internal battery current. Measured in amperes (A). |
| `device.battery.level` | T | Navixy: `avl_io_113` (Battery Level), `battery_level` (Battery Level) | Device internal battery capacity level. Measured in percentage (0-100%). |
| `device.battery.voltage` | T | Navixy: `avl_io_67` (Battery Voltage), `battery_voltage` (Battery Voltage) | Device internal battery voltage. Measured in volts (V). |
| `device.bluetooth.status` | P3 | Navixy: `avl_io_263` (BT Status) | Bluetooth connection status. Values: 0 = BT disabled, 1 = BT enabled (no device connected), 2 = Device connected (BTv3 only), 3 = Device connected (BLE only), 4 = Device connected (BLE + BT). |
| `device.power.board_voltage` | T | Navixy: `board_voltage` (External Voltage) | External power supply voltage from board voltage reading. Measured in volts (V). |
| `device.power.connected` | T | Navixy: `external_power_state` (External Power) | External power supply connection status. Values: false = not connected, true = connected. |
| `device.power.external_voltage` | T | Navixy: `avl_io_66` (External Voltage) | External power supply voltage from AVL IO parameter. Measured in volts (V). Note: May represent the same measurement as `board_voltage` but from a different source. |
| `device.sleep_mode` | T | Navixy: `avl_io_200` (Sleep Mode) | Device sleep mode status. Values: 0 = No sleep, 1 = GPS sleep, 2 = Deep sleep, 3 = Online sleep, 4 = Ultra sleep. |
| `device.status_bitmap` | T | Navixy: `status` (Status) | Device status bitmap. Contains device status flags and state information encoded as integer bits. Specific bit meanings depend on device model and firmware version. |
| `device.firmware.version` | T | Navixy: `avl_io_100` (Program Number) | Device firmware version identifier. Also represents CAN program/profile ID used by LV-CAN/ALL-CAN adapters to decode vehicle signals. |
| `device.identification.module_id_17b` | T | Navixy: `avl_io_388` (Module ID 17B) | Device module identifier (17 bytes, hex string). Unique device hardware identifier. |
| `device.identification.module_id_8b` | T | Navixy: `avl_io_101` (Module ID 8B) | Device module identifier (8 bytes, hex string). Unique device hardware identifier. |

---

# 15. Other

**Purpose:** Device-side events, geofence data, impulse counters, and raw CAN data. These fields are not part of the core telemetry schema but are included for completeness. Events and geofence data will be handled separately from telemetry in the Fleeti system.

## Structure

```json
{
  "other": {
    "events": {
      "device_unplugged": "boolean",
      "eco": {
        "driving": {
          "daily_value": "number",
          "event_duration": { "value": "number", "unit": "ms" },
          "green_driving_type": "integer (1-3)",
          "green_driving_value": "number"
        }
      },
      "harsh_acceleration": {
        "force": "number"
      },
      "harsh_braking": {
        "force": "number"
      },
      "harsh_cornering": {
        "force": "number",
        "radius": "number"
      },
      "idling": "boolean",
      "towing": "boolean",
      "trip": "integer (0-9)"
    },
    "geofence": {
      "auto_status": "integer (0-1)",
      "zone_id": "integer (0-3)",
      "device_zones": [
        {
          "inside": "integer (0-3)"
        }
      ]
    },
    "impulse_counters": [
      { "value": "number", "position": "integer" }
    ],
    "raw_can": ["string | number"]
  }
}
```

**Note:** This section consolidates fields that are not part of the core telemetry schema:

- **Events**: Device-side event data (harsh driving, eco events, trip status, etc.). These will be handled separately from telemetry in the Fleeti system.
- **Geofence**: Device-side geofence zone information. Geofence context is computed server-side and appears in Section 2 (Telemetry Context), not here.
- **Impulse counters**: These are **not cumulative counters** like odometer or engine hours (Section 8). They count pulses on digital inputs and **reset when records are saved**. The meaning of each impulse counter depends on what sensor/device is wired to the corresponding digital input (defined in installation metadata). May represent frequency measurements or event counts. **Clarification needed:** Specific purpose TBD based on installation configuration.
- **Raw CAN**: Unprocessed CAN bus messages. Interpretation and mapping to semantic fields will be defined in a future specification.

## Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
| --- | --- | --- | --- |
| `other.events.device_unplugged` | P1 | Navixy: `avl_io_252` (Unplug) | Device battery unplugged event. Values: 0 = battery present, 1 = battery unplugged. |
| `other.events.eco.driving.daily_value` | P1 | Navixy: `Computed` | **Computed:** Daily eco-driving score contribution used for dashboards/reports. Mirrors device-reported eco behavior value when provided. |
| `other.events.eco.driving.event_duration` | BL | Navixy: `avl_io_243` (Green Driving Event Duration) | Duration (ms) of the detected green-driving event that contributed to the eco score. |
| `other.events.eco.driving.green_driving_type` | P0 | Navixy: `avl_io_253` (Green Driving Type) | Encodes which harsh driving dimension triggered the eco event: 1 = harsh acceleration, 2 = harsh braking, 3 = harsh cornering. |
| `other.events.eco.driving.green_driving_value` | P0 | Navixy: `avl_io_254` (Green Driving Value) | Magnitude of the green-driving event (e.g., g-force * 100). Used with `green_driving_type` to qualify the event. |
| `other.events.harsh_acceleration.force` | P0 | Navixy: `acceleration` (Acceleration) | Harsh acceleration force measurement. |
| `other.events.harsh_braking.force` | P0 | Navixy: `braking` (Braking) | Harsh braking force measurement. |
| `other.events.harsh_cornering.force` | P0 | Navixy: `cornering` (Cornering) | Harsh cornering force measurement. |
| `other.events.harsh_cornering.radius` | P0 | Navixy: `cornering_rad` (Cornering Radius) | Cornering radius measurement. |
| `other.events.idling` | P2 | Navixy: `avl_io_251` (Idling) | Idling event status. Values: 0 = moving, 1 = idling. |
| `other.events.towing` | P2 | Navixy: `towing` (Towing) | Towing detection event. |
| `other.events.trip` | P3 | Navixy: `avl_io_250` (Trip) | Trip status. Values: 0 = trip stop, 1 = trip start. From firmware 01.00.24: 2 = Business Status, 3 = Private Status, 4-9 = Custom Statuses. |
| `other.geofence.auto_status` | P3 | Navixy: `avl_io_175` (Auto Geofence) | Auto geofence status. Values: 0 = target left zone, 1 = target entered zone. |
| `other.geofence.device_zones[].inside` | P3 | Navixy: `avl_io_208` (Geofence zone 33), `avl_io_155` (Geofence zone 01) | Device-side geofence zone status. Values: 0 = target left zone, 1 = target entered zone, 2 = over speeding end, 3 = over speeding start. Note: Geofence context is computed server-side and appears in Section 2 (Telemetry Context). |
| `other.geofence.zone_id` | P3 | Navixy: `avl_io_155` (Geofence zone 01) | Device-side geofence zone ID. Values: 0 = target left zone, 1 = target entered zone, 2 = over speeding end, 3 = over speeding start. |
| `other.impulse_counters[]` | P3 | Navixy: `impulse_counter_1` (Impulse Counter 1), `impulse_counter_2` (Impulse Counter 2), `avl_io_4` (Pulse Counter Din1), `avl_io_5` (Pulse Counter Din2) | Impulse/pulse counters from digital inputs. **Not cumulative counters** (unlike odometer/engine_hours). Counts pulses on digital inputs and resets when records are saved. Meaning depends on what sensor/device is wired to the input (defined in installation metadata). May represent frequency measurements or event counts. **Clarification needed:** Specific purpose TBD based on installation configuration. |
| `other.raw_can[]` | ? | Navixy: `raw_can_1` (Raw CAN 1), `raw_can_3` (Raw CAN 3), `raw_can_8` (Raw CAN 8), `raw_can_9` (Raw CAN 9), `raw_can_11` (Raw CAN 11), `raw_can_14` (Raw CAN 14), `raw_can_15` (Raw CAN 15), `raw_can_16` (Raw CAN 16), `raw_can_17` (Raw CAN 17) | Raw CAN bus data. Unprocessed CAN messages. Interpretation and mapping to semantic fields will be defined in a future specification. |

---

# 16. Packet Metadata

**Purpose:** Metadata about the telemetry packet itself.

**Note:** Device identification (`device.identification.*`) and firmware version (`device.firmware.version`) are documented in Section 14 (Device), as they represent current device state rather than packet-specific metadata.

## Structure

```json
{
  "provider": {
    "event": "string",
    "event_code": "integer",
    "event_subcode": "integer",
    "time": {
      "device_time": "ISO8601",
      "provider_time": "ISO8601",
      "fleeti_time": "ISO8601"
    }
  }
}
```

## Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
| --- | --- | --- | --- |
| `provider.event` | BL/T | Navixy: `EVENT` (Event) | Event |
| `provider.event_code` | BL/T | Navixy: `event_code` (Event Code) | Event Code |
| `provider.event_subcode` | BL/T | Navixy: `sub_event_code` (Sub Event Code) | Sub Event Code |
| `provider.time.device_time` | BL/T | Navixy: `msg_time` (metadata) | metadata |
| `provider.time.provider_time` | T | Navixy: `server_time` (metadata) | metadata |
| `provider.time.fleeti_time` | T | **Computed:** Set to current server timestamp when packet is received by Fleeti backend | ISO8601 timestamp when Fleeti backend received this telemetry packet via Data Forwarding. This is the authoritative "Fleeti reception time" and is used as the source for root-level `last_updated_at`. |