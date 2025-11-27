# Telemetry Schema Analysis

## 📊 Overview

This document provides a comprehensive analysis of the complete Fleeti Telemetry structure based on the catalog of 338 telemetry fields extracted from Navixy Data Forwarding.

**Generated from:** Navixy Field Catalog  
**Total Fields Cataloged:** 338  
**Main Sections:** 16  
**Date:** 2025-01-21

---

## 🎯 Purpose

This analysis defines the **complete structure** of Fleeti Telemetry objects, mapping all identified fields from provider-specific formats (Navixy) into a provider-agnostic Fleeti telemetry model.

- **Scope:** Defines the *Maximal Telemetry Object* available within the Fleeti system.
- **Projections:** Specific views (API, Frontend, WebSocket) will be defined in separate specifications based on this superset.
- **Mapping Logic:** Defines how raw provider fields are transformed, prioritized, or aggregated into Fleeti fields.

---

## 📋 Table of Contents

1. [Asset Metadata](#1-asset-metadata)
2. [Telemetry Context](#2-telemetry-context)
3. [Location](#3-location)
4. [Connectivity](#4-connectivity)
5. [Vehicle](#5-vehicle)
6. [Fuel](#6-fuel)
7. [Counters](#7-counters)
8. [Driving Behavior](#8-driving-behavior)
9. [Sensors](#9-sensors)
10. [I/O (Inputs/Outputs)](#10-io-inputsoutputs)
11. [Driver](#11-driver)
12. [Device](#12-device)
13. [Events](#13-events)
14. [Geofence](#14-geofence)
15. [Other](#15-other)
16. [Packet Metadata](#16-packet-metadata)
17. [Low Priority & Clarification](#17-low-priority--clarification)

---

## 1. Asset Metadata

**Purpose:** Static asset information that does not change per telemetry packet. This includes identity, ownership, groups, accessories, installation configuration, and asset-specific properties.

### Structure
```json
{
  "asset": {
    "id": "uuid",
    "name": "string",
    "type": 10,
    "subtype": 110,
    "group": { "id": "uuid", "name": "string" },
    "customer_ref": "2010-010",
    "immobilizer_capable": true, // used to display the immobilizer icon
    "accessories": [
      {
        "id": "uuid",
        "type_id": 1,
        "type_code": "immobilizer",
        "connection": "wire",
        "label": "Main immobilizer relay",
      },
      {
        "id": "uuid",
        "type_id": 2,
        "type_code": "temperature",
        "connection": "bluetooth",
        "label": "Cold room sensor",
        "sensors": [ // One accessory can contain multiple telemetry values
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
    "installation": { // useful for status management
      "ignition_input_number": 1, 
      "immobilizer_output_number": 2,
      "initial_odometer_km": 154000,
      "initial_engine_hours_h": 4200
    },
    "properties": {
      "vehicle": {
        "serial_number": "string",
        "brand": "string",
        "model": "string",
        "license_plate": "string",
        "vrn": "string",
        "vin": "string",
        "registration_country": "string",
        "powertrain": {
          "primary_energy": "diesel|gasoline|electric|hybrid|cng|lng|hydrogen|other",
          "fuel_tank_capacity_l": 600,
          "battery_capacity_kwh": 120,
          "theoretical_consumption_l_per_100km": 32.5,
          "theoretical_consumption_kwh_per_100km": 24.3
        }
      },
      "equipment": {
        "serial_number": "string",
        "brand": "string",
        "model": "string",
        "rated_power_kw": 180,
        "energy_source": "diesel|electric|hybrid"
      },
      "phone": {
        "platform": "ios|android|unknown",
        "platform_version": "17.2",
        "employee_id": "string", // not yet available
        "employee_name": "string" // not yet available
      },
      "site": {
        "site_type": "cold_room",
        "name": "Abidjan Coldroom West",
        "address": {
          "line1": "Zone industrielle",
          "city": "Abidjan",
          "country": "CI"
        },
        "location": { // used to display static location of a site
          "latitude": 5.3561,
          "longitude": -4.0083
        },
        "surface_m2": 120,
        "capacity_units": 450,
        "temperature_range_c": { "min": -25, "max": 5 } // Can be used for alerting system in the future (TBD)
      }
    }
  }
}
```

| **Note:** This structure represents static asset metadata. From a front-end perspective, not all of these fields will be available or used directly. However, these fields are essential inputs for the transformation pipeline to compute derived telemetry fields.

### Field Sources & Notes

| Fleeti Field | Source | Description |
|--------------|--------|-------------|
| `asset.id` | Fleeti Asset service | Primary asset identifier |
| `asset.name` | Fleeti Asset service | Human-friendly asset label |
| `asset.type` | Fleeti Asset service | Type enum (vehicle, equipment, site, phone) |
| `asset.subtype` | Fleeti Asset service | Subtype enum (car, truck, cold_room, etc.) |
| `asset.group.id` | Asset grouping service | Primary group identifier |
| `asset.group.name` | Asset grouping service | Primary group name |
| `asset.customer_ref` | Customer registry | Reference code identifying the customer/tenant (e.g., `2010-010`) |
| `asset.immobilizer_capable` | Installation metadata | Whether immobilizer wiring exists |
| `asset.accessories[].id` | Accessory registry | Unique accessory identifier |
| `asset.accessories[].type_id` | Accessory registry | Accessory type numeric ID |
| `asset.accessories[].type_code` | Accessory registry | Accessory type code (immobilizer, temperature, fuel_level, etc.) |
| `asset.accessories[].connection` | Installation metadata | Connection type (wire, bluetooth, wifi) |
| `asset.accessories[].label` | Installation metadata | Human-readable accessory label |
| `asset.accessories[].serial_number` | Installation metadata | Accessory serial number |
| `asset.accessories[].sensors[]` | Installation metadata | Array of sensor types/positions this accessory exposes |
| `asset.installation.ignition_input_number` | Installation metadata | Digital input wired to ignition switch |
| `asset.installation.immobilizer_output_number` | Installation metadata | Digital output controlling immobilizer relay |
| `asset.installation.initial_odometer_km` | Installation metadata | Odometer reading at time of installation (offset) |
| `asset.installation.initial_engine_hours_h` | Installation metadata | Engine hours reading at time of installation (offset) |
| `asset.properties.vehicle.serial_number` | Fleeti catalog | OEM/installer serial number |
| `asset.properties.vehicle.brand` | Fleeti catalog | Vehicle manufacturer brand |
| `asset.properties.vehicle.model` | Fleeti catalog | Vehicle model name |
| `asset.properties.vehicle.license_plate` | Fleeti catalog | Registration plate displayed to users |
| `asset.properties.vehicle.vin` | Navixy Field Catalog (`avl_io_132` (Security State Flags)) | Vehicle identification number |
| `asset.properties.vehicle.registration_country` | Fleeti catalog | Registration jurisdiction (ISO country code) |
| `asset.properties.vehicle.powertrain.primary_energy` | Fleeti catalog | Primary energy source (diesel/gasoline/electric/hybrid/CNG/LNG/hydrogen/other) |
| `asset.properties.vehicle.powertrain.fuel_tank_capacity_l` | Fleeti catalog | Nominal fuel tank size in liters |
| `asset.properties.vehicle.powertrain.battery_capacity_kwh` | Fleeti catalog | Battery capacity in kWh (for electric/hybrid vehicles) |
| `asset.properties.vehicle.powertrain.theoretical_consumption_l_per_100km` | Fleeti catalog | Expected fuel consumption baseline (L/100km) |
| `asset.properties.vehicle.powertrain.theoretical_consumption_kwh_per_100km` | Fleeti catalog | Expected energy consumption baseline (kWh/100km) |
| `asset.properties.equipment.serial_number` | Fleeti catalog | Equipment serial number |
| `asset.properties.equipment.brand` | Fleeti catalog | Equipment manufacturer brand |
| `asset.properties.equipment.model` | Fleeti catalog | Equipment model name |
| `asset.properties.equipment.rated_power_kw` | Fleeti catalog | Equipment rated power in kilowatts |
| `asset.properties.equipment.energy_source` | Fleeti catalog | Equipment energy source (diesel/electric/hybrid) |
| `asset.properties.phone.platform` | Fleeti catalog | Mobile platform (ios/android/unknown) |
| `asset.properties.phone.platform_version` | Fleeti catalog | Platform version (e.g., `17.2`) |
| `asset.properties.phone.employee_id` | Fleeti catalog | Associated employee identifier (not yet available) |
| `asset.properties.phone.employee_name` | Fleeti catalog | Associated employee name (not yet available) |
| `asset.properties.site.site_type` | Fleeti catalog | Site family (cold_room/warehouse/yard/other) |
| `asset.properties.site.name` | Fleeti catalog | Site name |
| `asset.properties.site.address.line1` | Fleeti catalog | Address line 1 |
| `asset.properties.site.address.city` | Fleeti catalog | City name |
| `asset.properties.site.address.country` | Fleeti catalog | Country code (ISO) |
| `asset.properties.site.location.latitude` | Fleeti catalog | Site latitude for map display |
| `asset.properties.site.location.longitude` | Fleeti catalog | Site longitude for map display |
| `asset.properties.site.surface_m2` | Fleeti catalog | Site surface area in square meters |
| `asset.properties.site.capacity_units` | Fleeti catalog | Site capacity (units depend on site type) |
| `asset.properties.site.temperature_range_c` | Fleeti catalog | Expected min/max temperature range in Celsius (especially for cold rooms) |

| **Note:** Most asset metadata fields come from Fleeti catalog. The VIN field (`asset.properties.vehicle.vin`) is sourced from Navixy Field Catalog (`avl_io_132` (Security State Flags)).

---

## 2. Telemetry Context

**Purpose:** Computed/derived fields that change per telemetry packet. These are calculated from raw telemetry combined with asset metadata. Includes status families (connectivity, transit, engine, immobilization), current geofence context, and ongoing trip information.

### Structure
```json
{
  "status": {
    "top_status": { 
      "family": "transit", 
      "code": "in_transit", 
      "updated_at": "ISO8601" 
    },
    "statuses": [
      { 
        "family": "connectivity", 
        "code": "online", 
        "compatible": true, 
        "updated_at": "ISO8601" 
      },
      { 
        "family": "immobilization", 
        "code": "free", 
        "compatible": true, 
        "updated_at": "ISO8601" 
      },
      { 
        "family": "engine", 
        "code": "running", 
        "compatible": true, 
        "updated_at": "ISO8601" 
      },
      { 
        "family": "transit", 
        "code": "in_transit", 
        "compatible": true, 
        "updated_at": "ISO8601" 
      }
    ]
  },
  "geofences": [
    { 
      "id": 42, 
      "name": "Warehouse", 
      "type": "polygon", 
      "entered_at": "ISO8601"
    }
  ],
  "trip": {
    "id": "uuid",
    "started_at": "ISO8601",
    "distance": { "value": 45.2, "unit": "string (km)" },
    "duration": { "value": 3600, "unit": "string (s)" },
    "start_location": { "lat": 5.3561, "lng": -4.0083 },
    "current_location": { "lat": 5.4123, "lng": -4.0156 }
  },
  "nearby_assets": [
    { "id": "ble_beacon_id_hex", "name": "Asset Name", "detected_at": "ISO8601" }
  ]
}
```

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `status.top_status` | P0 | **Computed:** Highest-priority status family | Connectivity > Immobilization > Engine > Transit |
| `status.statuses[]` | P0 | **Computed:** Telemetry + Asset Metadata | Array of compatible status families with codes |
| `geofences[]` | P2 | **Computed:** `location.lat`/`lng` (Longitude)+ Geofence Service | Current geofences the asset is inside |
| `trip` | P1 | **Computed:** Ignition + Movement history | Ongoing trip information (nullable) |
| `trip.distance` | P1 | Navixy: `avl_io_199` (Trip Odometer) > GPS calculation | Trip distance (value + unit) |
| `trip.duration` | P1 | Navixy: `obd_time_since_engine_start` (OBD Engine Runtime) > GPS calculation | Trip duration (value + unit) |
| `nearby_assets[].id` | P0 | Navixy: `ble_beacon_id` (BLE Beacon ID) | Detected BLE beacon ID (nearby asset) |
| `nearby_assets[].name` | P1 | Fleeti catalog | Asset name linked to the beacon ID |
| `nearby_assets[].detected_at` | P0 | Navixy: `msg_time` (metadata) | Timestamp of detection |
| `nearby_assets[].detected` | P2 | Navixy: `avl_io_248` (Immobilizer) | Beacon detection flag |

| **Computation Rules:** See Telemetry Status Rules for definitive logic on status transitions, compatibility matrices, and priority ordering.

---

## 3. Location

**Purpose:** GPS/GNSS positioning data and location precision metrics.

### Structure
```json
{
  "location": {
    "latitude": "decimal degrees (-90 to 90)",
    "longitude": "decimal degrees (-180 to 180)",
    "altitude": "meters above sea level",
    "heading": "degrees (0-359, 0=North)",
    "cardinal_direction": "string (N, NE, E, SE, S, SW, W, NW)",
    "satellites": "integer (0-32)",
    "hdop": "decimal (-1 to 20, -1=unknown)",
    "pdop": "decimal",
    "geocoded_address": "string",
    "precision": {
      "hdop": "decimal",
      "pdop": "decimal",
      "satellites": "integer",
      "fix_quality": "integer (0=no fix, 1=fix)"
    }
  }
}
```

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `location.latitude` | P0 | Navixy: `lat` (Latitude) | Latitude in decimal degrees |
| `location.longitude` | P0 | Navixy: `lng` (Longitude) | Longitude in decimal degrees |
| `location.altitude` | P2 | Navixy: `alt` (Altitude) | Altitude in meters |
| `location.heading` | P0 | Navixy: `heading` (Heading) | Heading in degrees (0-359) |
| `location.cardinal_direction` | P1 | **Computed:** Derived from `location.heading` | Cardinal direction (N, NE, E, etc.) |
| `location.satellites` | P2 | Navixy: `satellites` (Satellites) | Number of satellites in fix |
| `location.hdop` | P2 | Navixy: `hdop` (HDOP)> `avl_io_182` (GNSS HDOP) | Horizontal Dilution of Precision |
| `location.pdop` | P2 | Navixy: `pdop` (PDOP)> `avl_io_181` (GNSS PDOP) | Position Dilution of Precision |
| `location.geocoded_address` | P1 | **Computed:** Reverse geocoding (server-side) | Single string representation of the location |
| `location.precision.fix_quality` | P3 | Navixy: `avl_io_69` (GNSS Status) | GNSS fix status (0=no fix, 1=fix) |
| `location.precision.coordinate_format` | P0 | Navixy: `avl_io_232` (CNG Status) | ISO6709 coordinate format |

---

## 4. Connectivity

**Purpose:** Network and communication status information.

### Structure
```json
{
  "connectivity": {
    "signal_level": "integer (0-31, 99=unknown)",
    "operator": "string or integer code",
    "connection_state": "string (online/offline)",
    "registration_state": "integer (0-5)",
    "network_type": "integer (0=Unknown, 2=GPRS, 3=EDGE, etc.)",
    "sim": {
      "imsi": "string",
      "iccid": "string"
    },
    "cell": {
      "id": "integer",
      "lac": "integer (Location Area Code)"
    }
  }
}
```

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `connectivity.signal_level` | P0 | Navixy: `gsm.signal.csq` (GSM Signal CSQ)> `avl_io_21` (GSM Signal) | Signal strength (0-31 scale preferred) |
| `connectivity.operator` | P2 | Navixy: `avl_io_241` (Active GSM Operator) | Active GSM operator code |
| `connectivity.connection_state` | P2 | Navixy: `avl_io_253` (Green driving type) | GSM connection status |
| `connectivity.registration_state` | P3 | Navixy: `avl_io_254` (Green Driving Value) | GSM network registration status |
| `connectivity.network_type` | P3 | Navixy: `avl_io_115` (Engine Temperature) | Cell network type (GPRS/EDGE/UMTS/LTE) |
| `connectivity.sim.imsi` | P2 | Navixy: `avl_io_14` (ICCID2) | SIM card IMSI |
| `connectivity.sim.iccid` | P3 | Navixy: `avl_io_11` (ICCID1) | SIM card ICCID |
| `connectivity.cell.id` | P3 | Navixy: `avl_io_205` (GSM Cell ID) | GSM base station ID |
| `connectivity.cell.lac` | P3 | Navixy: `avl_io_206` (GSM Area Code) | Location Area Code (LAC) |
| `connectivity.data_mode` | P3 | Navixy: `avl_io_80` (Data Mode) | Device data mode (Home/Roaming/Unknown) |

---

## 5. Motion

**Purpose:** Dynamic movement data including speed and motion status.

### Structure
```json
{
  "motion": {
    "speed": { 
      "value": "decimal", 
      "unit": "string (km/h, mph)" 
    },
    "is_moving": "boolean"
  }
}
```

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `motion.speed` | P0 | **Logic:** `can_speed` (CAN Speed)> `obd_speed` (OBD Speed)> `tacho_speed` > `speed` (Speed)> `avl_io_24` (Speed)> `avl_io_37` (Vehicle Speed)> `avl_io_389` (OBD OEM Total Mileage) | Best available speed (value + unit) |
| `motion.is_moving` | P0 | **Logic:** `moving` (Is Moving)> `avl_io_240` (Movement) | Movement status (0=stationary, 1=moving) |

---

## 6. Power

**Purpose:** Power source status, ignition state, and battery health (asset/vehicle battery).

### Structure
```json
{
  "power": {
    "ignition": "boolean",
    "battery": { 
      "level": "%", 
      "voltage": { "value": "decimal", "unit": "string (V)" }
    }
  }
}
```

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `power.ignition` | P0 | **Logic:** `avl_io_239` (Ignition)> (`io.inputs` matched by `asset.installation.ignition_input_number`) > `can_ignition_state` (CAN Ignition) | Ignition status (Hardware line > Mapped Input > Virtual/CAN) |
| `power.battery.level` | P2 | Navixy: `avl_io_104` (BLE Humidity #2)> `can_battery_level` (can) | Vehicle/Asset battery percentage |
| `power.battery.voltage` | P2 | Navixy: `board_voltage` (External Voltage)> `avl_io_10` | Vehicle/Asset battery voltage |

---

## 7. Diagnostics (Vehicle/Machine/Equipment)

**Purpose:** Detailed asset diagnostics, including CAN bus data, engine stats, and body sensors.

### Structure
```json
{
  "diagnostics": {
    "engine": {
      "rpm": { "value": "integer", "unit": "string (rpm)" },
      "coolant_temperature": { "value": "decimal", "unit": "string (°C)" },
      "temperature": { "value": "decimal", "unit": "string (°C)" },
      "load": "%",
      "ready_to_drive": "boolean",
      "webasto_state": "boolean"
    },
    "body": {
      "doors": { 
        "front_left": "boolean", 
        "front_right": "boolean", 
        "rear_left": "boolean", 
        "rear_right": "boolean", 
        "trunk": "boolean", 
        "hood": "boolean" 
      },
      "belts": { 
        "driver": "boolean", 
        "passenger": "boolean", 
        "rear_left": "boolean", 
        "rear_right": "boolean", 
        "rear_middle": "boolean" 
      },
      "lights": { 
        "low_beam": "boolean", 
        "high_beam": "boolean", 
        "parking": "boolean", 
        "fog_front": "boolean", 
        "fog_rear": "boolean",
        "brake": "boolean", 
        "reverse": "boolean", 
        "turn_signal": "boolean"
      }
    },
    "brakes": {
      "parking_brake": "boolean",
      "abs_active": "boolean",
      "pad_wear": "boolean",
      "retarder_manual": "boolean",
      "retarder_automatic": "boolean"
    },
    "fluids": {
      "adblue_level": "%"
    },
    "axles": {
      "weights": [
        { "value": "decimal", "unit": "string (kg)" }
      ],
      "total_weight": { "value": "decimal", "unit": "string (kg)" }
    },
    "health": {
      "mil_status": "boolean",
      "dtc_count": "integer",
      "mil_activated_distance": { "value": "decimal", "unit": "string (km)" },
      "low_tire_pressure_warning": "boolean"
    },
    "identification": {
      "vin": "string"
    },
    "maintenance": {
      "service_distance": { "value": "decimal", "unit": "string (km)" }
    },
    "drivetrain": {
      "front_differential_locked": "boolean",
      "rear_differential_locked": "boolean",
      "central_differential_4hi_locked": "boolean",
      "central_differential_4lo_locked": "boolean",
      "clutch_state": "boolean"
    },
    "trailer": {
      "axle_lift_active": [
        { "value": "boolean" }
      ]
    },
    "steering": {
      "eps_state": "boolean"
    },
    "climate": {
      "air_conditioning": "boolean"
    },
    "occupancy": {
      "front_passenger": "boolean"
    },
    "safety": {
      "airbag_state": "boolean"
    },
    "wheels": {
      "front_left": { "speed": { "value": "decimal", "unit": "string (km/h)" } },
      "front_right": { "speed": { "value": "decimal", "unit": "string (km/h)" } },
      "rear_left": { "speed": { "value": "decimal", "unit": "string (km/h)" } },
      "rear_right": { "speed": { "value": "decimal", "unit": "string (km/h)" } }
    }
  }
}
```

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `diagnostics.engine.rpm` | P0/P2 | **Logic:** `can_rpm` (CAN Engine RPM)> `obd_rpm` (OBD RPM)> `avl_io_85` (Engine RPM)> `avl_io_304` (Vehicles Range On Battery)> `avl_io_36` (Engine RPM) | Engine RPM (value + unit) |
| `diagnostics.engine.coolant_temperature` | P1 | Navixy: `can_engine_temp` (CAN Engine Temp)> `avl_io_124` (Agricultural Machinery Flags) | Engine coolant temperature (value + unit) |
| `diagnostics.engine.temperature` | P1 | Navixy: `avl_io_390` (OBD OEM Fuel Level) | Generic engine temperature (value + unit) |
| `diagnostics.engine.load` | P3 | Navixy: `can_engine_load` (CAN Engine Load) | Engine load percentage |
| `diagnostics.engine.ready_to_drive` | P3 | Navixy: `can_ready_to_drive` (CAN Ready to Drive) | EV/Hybrid ready state |
| `diagnostics.engine.webasto_state` | P3 | Navixy: `can_webasto_state` (CAN Webasto State) | Auxiliary heater status |
| `diagnostics.engine.pto_state` | P3 | Navixy: `can_pto_state` (CAN PTO State) | Power Take-Off (PTO) state |
| `diagnostics.engine.glow_plug_active` | P3 | Navixy: `can_glow_plug_indicator` (CAN Glow Plug Indicator) | Glow plug indicator (diesel engines) |
| `diagnostics.engine.mil_activated_distance` | P3 | Navixy: `obd_mil_activated_distance` (OBD MIL Activated Distance) | Distance when MIL was activated (value + unit) |
| `diagnostics.body.doors.*` | P2/P3 | Navixy: `can_front_left_door` (CAN Front Left Door), `can_front_right_door` (can), `can_rear_left_door` (can), `can_rear_right_door` (can), `can_trunk_state` (can), `can_door_state` (can), `can_hood_state` (CAN Hood State), `can_roof_state` (CAN Roof State), `avl_io_90` (Door Status), `avl_io_657` (SSF Rear Right Door Open), `avl_io_658` (SSF Trunk Door Open) | Door open/close status |
| `diagnostics.body.belts.*` | P1 | Navixy: `can_seat_belt_driver_state` (can), `can_seat_belt_passenger_state` (CAN Passenger Seat Belt State), `can_rear_left_seat_belt_state` (CAN Rear Left Seat Belt State), `can_rear_right_seat_belt_state` (CAN Rear Right Seat Belt State), `can_rear_centre_seat_belt_state` (CAN Rear Centre Seat Belt State) | Seat belt status |
| `diagnostics.body.lights.*` | P3 | Navixy: `can_front_fog_lights` (CAN Front Fog Lights), `can_additional_front_fog_lights` (can), `can_additional_rear_lights` (can), `can_full_beam_headlights` (CAN Full Beam Headlights), `can_light_signal` (CAN Light Signal), `can_lights_failure` (CAN Lights Failure), `can_parking_lights` (CAN Parking Lights), `can_rear_fog_lights` (CAN Rear Fog Lights), `can_dipped_headlights` (CAN Dipped Headlights) | Headlights, fog lights, etc. |
| `diagnostics.brakes.parking_brake` | P3 | Navixy: `can_hand_brake_state` (CAN Hand Brake) | Parking brake status |
| `diagnostics.brakes.abs_active` | P3 | Navixy: `can_abs_state` (CAN ABS State) | Anti-lock braking system active |
| `diagnostics.brakes.pad_wear` | P3 | Navixy: `can_brake_pad_wear` (CAN Brake Pad Wear) | Brake pad wear indicator |
| `diagnostics.brakes.retarder_manual` | P3 | Navixy: `can_manual_retarder` (CAN Manual Retarder) | Manual retarder state |
| `diagnostics.brakes.retarder_automatic` | P3 | Navixy: `can_automatic_retarder` (CAN Automatic Retarder) | Automatic retarder state |
| `diagnostics.fluids.adblue_level` | P2 | Navixy: `can_adblue_level` (CAN AdBlue Level) | AdBlue level percentage |
| `diagnostics.axles.weights` | P3 | Navixy: `can_axle_load_1` (CAN Axle Load 1), `can_axle_load_2` (CAN Axle Load 2), `can_axle_load_3` (CAN Axle Load 3), `can_axle_load_4` (CAN Axle Load 4), `can_axle_load_5` (CAN Axle Load 5) | Axle weights (value + unit) |
| `diagnostics.axles.total_weight` | P3 | Navixy: *(No direct source - computed from axle weights)* | Total vehicle weight (value + unit) |
| `diagnostics.health.mil_status` | P2 | Navixy: `obd_mil_status` (OBD MIL Status)> `avl_io_43` (Distance Traveled MIL On) | Malfunction Indicator Lamp |
| `diagnostics.health.dtc_count` | P0 | Navixy: `obd_dtc_number` (OBD DTC Count)> `avl_io_30` (Number of DTC) | Diagnostic Trouble Codes count |
| `diagnostics.health.mil_activated_distance` | P3 | Navixy: `obd_mil_activated_distance` (OBD MIL Activated Distance) | Distance when MIL activated (value + unit) |
| `diagnostics.health.low_tire_pressure_warning` | P1 | Navixy: `can_low_tire_pressure` (can) | Low tire pressure warning indicator |
| `diagnostics.identification.vin` | P0 | Navixy: `avl_io_132` (Security State Flags) | VIN (from CAN/OBD) |
| `diagnostics.maintenance.service_distance` | P2 | Navixy: *(No direct source - computed from odometer)* | Service distance (value + unit) |
| `diagnostics.drivetrain.front_differential_locked` | P3 | Navixy: `can_front_diff_locked` (CAN Front Diff Locked) | Front differential lock state |
| `diagnostics.drivetrain.rear_differential_locked` | P3 | Navixy: `can_rear_diff_locked` (CAN Rear Diff Locked) | Rear differential lock state |
| `diagnostics.drivetrain.central_differential_4hi_locked` | P3 | Navixy: `can_central_diff_4hi_locked` (CAN Central Diff 4HI Locked) | Central diff 4HI lock state |
| `diagnostics.drivetrain.central_differential_4lo_locked` | P3 | Navixy: `can_central_diff_4lo_locked` (CAN Central Diff 4LO Locked) | Central diff 4LO lock state |
| `diagnostics.drivetrain.clutch_state` | P3 | Navixy: `can_clutch_state` (CAN Clutch State) | Clutch state |
| `diagnostics.trailer.axle_lift_active[]` | P3 | Navixy: `can_trailer_axle_lift_active_1` (CAN Trailer Axle Lift Active 1), `can_trailer_axle_lift_active_2` (CAN Trailer Axle Lift Active 2) | Trailer axle lift states |
| `diagnostics.steering.eps_state` | P3 | Navixy: `can_eps_state` (EPS State) | Electric Power Steering state |
| `diagnostics.climate.air_conditioning` | P3 | Navixy: `can_air_conditioning` (can) | Air conditioning state |
| `diagnostics.occupancy.front_passenger` | P3 | Navixy: `can_front_passenger_presence` (CAN Front Passenger Presence) | Front passenger presence |
| `diagnostics.safety.airbag_state` | P3 | Navixy: `can_airbag_state` (can) | Airbag state |
| `diagnostics.wheels.front_left.speed` | P3 | Navixy: `avl_io_201` (LLS 1 Fuel Level) | Front left wheel speed (value + unit) |
| `diagnostics.wheels.front_right.speed` | P3 | Navixy: `avl_io_202` (LLS 1 Temperature) | Front right wheel speed (value + unit) |
| `diagnostics.wheels.rear_left.speed` | P3 | Navixy: `avl_io_203` (LLS 2 Fuel Level) | Rear left wheel speed (value + unit) |
| `diagnostics.wheels.rear_right.speed` | P3 | Navixy: `avl_io_204` (LLS 2 Temperature) | Rear right wheel speed (value + unit) |

---

## 8. Fuel

**Purpose:** Fuel system data including levels, consumption, and temperature.

### Structure
```json
{
  "fuel": {
    "levels": [
      { 
        "id": "string (primary, sensor_1)",
        "type": "string (tank)",
        "value": "decimal",
        "unit": "string (%, L)"
      }
    ],
    "consumption": {
      "rate": { "value": "decimal", "unit": "string (L/h)" },
      "cumulative": { "value": "decimal", "unit": "string (L)" },
      "trip": { "value": "decimal", "unit": "string (L)" },
      "economy": {
        "instant": { "value": "decimal", "unit": "string (L/100km)" },
        "average": { "value": "decimal", "unit": "string (L/100km)" }
      }
    },
    "temperature": {
      "value": "decimal", "unit": "string (°C)"
    }
  }
}
```

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `fuel.levels` | P0 | **Logic:** Aggregated array of distinct fuel levels. Requires deduplication logic to handle overlapping sources (e.g., `can_fuel_1` (can)vs multiple BLE/LLS sensors) vs actual multiple tanks. |
| `fuel.levels[].value` | P0 | **Candidates:** `can_fuel_1` (can), `fuel_level` (Fuel Level), `avl_io_101` (Module ID 8B), `avl_io_306` (BLE Fuel Frequency #1), `avl_io_210` (LLS 3 Fuel Level), `avl_io_212` (LLS 4 Fuel Level), `avl_io_270` (BLE Fuel Level #1), `avl_io_273` (BLE Fuel Level #2), `can_fuel_litres` (can), `obd_custom_fuel_litres` (obd), `lls_level_1` (LLS Level 1), `lls_level_2` (LLS Level 2), `lls_level_3` (LLS Level 3), `lls_level_4` (LLS Level 4), `ble_lls_level_1` (fuel), `ble_lls_level_2` (fuel) | Value of the specific fuel level entry. |
| `fuel.consumption.rate` | P1 | Navixy: `can_fuel_rate` (CAN Fuel Rate)> `avl_io_107` (Fuel Consumed (counted)) (Fuel Consumed (counted)) (Fuel Consumed (counted)) (Fuel Consumed (counted)) (Fuel Consumed (counted)) (Fuel Consumed (counted)) (GPS) | Fuel consumption rate (value + unit) |
| `fuel.consumption.cumulative` | P0 | Navixy: `can_fuel_used` > `avl_io_103` (Fuel Used GPS)> `can_consumption` (can)> `can_consumption_relative` (can) | Total fuel used (value + unit) |
| `fuel.consumption.trip.value` | P1 | Navixy: *(No direct source - computed from trip data)* | Trip fuel consumption (value + unit) |
| `fuel.consumption.economy` | P3 | Navixy: `avl_io_83` (Fuel Consumed), `avl_io_84` (Fuel Level) | Instant/Average/CAN economy (value + unit) |
| `fuel.temperature` | P3 | Navixy: `avl_io_102` (Fuel Temperature) | Fuel temperature (value + unit) |

| **🚧 Investigation Needed (Fuel Deduplication):**  
| We need to clarify which Navixy fields are duplicates of raw device fields (e.g., is `fuel_level` (Fuel Level)just a normalized BLE sensor reading?).  
| **Challenge:** Distinguishing between *redundant data* for the same tank (which should be merged/prioritized into one `fuel.levels` entry) versus *distinct data* for multiple tanks (which should result in multiple entries).  
| **Action:** Review Navixy documentation/data samples to establish a definitive deduplication and identification logic for the `fuel.levels` array.

---

## 9. Counters

**Purpose:** Accumulated counters for odometer and engine hours.

### Structure
```json
{
  "counters": {
    "odometer": { "value": "decimal", "unit": "string (km)" },
    "engine_hours": { "value": "decimal", "unit": "string (h)" }
  }
}
```

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `counters.odometer` | P0 | **Logic:** `can_mileage` (CAN Mileage)> (`can_mileage_relative` (can)+ `initial_odometer_km`) > `tacho_mileage` > `hw_mileage` (Hardware Mileage)> `raw_mileage` (Raw Mileage)> `avl_io_105` (Total Mileage (counted)) (Total Mileage (counted)) (Total Mileage (counted)) (Total Mileage (counted)) (Total Mileage (counted)) (Total Mileage (counted)) (GPS) > `avl_io_16` (Total Odometer)> `avl_io_87` (Total Mileage)> `obd_custom_odometer` (obd) | Best available total odometer (value + unit) |
| `counters.engine_hours` | P0 | **Logic:** `can_engine_hours` (CAN Engine Hours)> (`can_engine_hours_relative` (can)+ `initial_engine_hours_h`) > `avl_io_449` (Ignition On Counter)> `avl_io_42` (Runtime since engine start) | Best available engine hours (value + unit) |
| `counters.trip_count` | P3 | Navixy: `avl_io_907` (SSF Engine Lock Active) | Number of trip events |

---

## 10. Driving Behavior

**Purpose:** Daily aggregated driving metrics and eco-driving scores.

### Structure
```json
{
  "driving_behavior": {
    "throttle_position": { "value": "decimal", "unit": "string (%)" },
    "brake_position": { "value": "decimal", "unit": "string (%)" },
    "brake_active": "boolean",
    "overspeed_threshold": { "value": "decimal", "unit": "string (km/h)" },
    "autopilot": {
      "active": "boolean"
    },
    "eco_score": {
      "daily_value": "integer (0-100)",
      "value": "integer (0-100)",
      "duration": { "value": "decimal", "unit": "string (s)" },
      "green_driving_type": "integer (0-8)",
      "green_driving_value": "integer",
      "event_type": "integer (0-4)"
    },
    "daily_summary": {
      "distance": { "value": "decimal", "unit": "string (km)" },
      "driving_duration": { "value": "decimal", "unit": "string (h)" },
      "idling_duration": { "value": "decimal", "unit": "string (h)" },
      "event_counts": {
        "harsh_acceleration": "integer",
        "harsh_braking": "integer",
        "harsh_cornering": "integer",
        "overspeed": "integer",
        "excessive_idling": "integer"
      }
    }
  }
}
```

| **Note:** Real-time harsh driving events (e.g., instant g-force alerts, crash detection) are handled via a separate Event WebSocket stream and are not included in this telemetry snapshot. This section focuses on daily aggregated metrics used for calculating the Eco-Driving score and providing a daily summary.

| **Note:** Raw accelerometer fields (`axis_x` (Axis X), `axis_y` (Axis Y), `axis_z` (Axis Z), `avl_io_17` (Axis X), `avl_io_18` (Axis Y), `avl_io_19` (Axis Z)) are **ignored** as we prefer calculated events (`driving_behavior.*`) for scoring. See [Section 19: Low Priority & Ignored Fields](#19-low-priority--ignored-fields) for details.

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `driving_behavior.throttle_position` | P1 | Navixy: `can_throttle` (CAN Throttle)> `obd_throttle` (OBD Throttle)> `avl_io_41` (Throttle Position)> `avl_io_391` (Private mode) | Accelerator pedal position (value + unit) |
| `driving_behavior.brake_position` | P1 | Navixy: *(No direct source - computed from brake events)* | Brake pedal position (value + unit) |
| `driving_behavior.brake_active` | P1 | Navixy: `can_footbrake_state` (CAN Footbrake State) | Footbrake active state |
| `driving_behavior.overspeed_threshold` | P3 | Navixy: `avl_io_130` (Harvesting Drum RPM) | Speed threshold for overspeed events (value + unit) |
| `driving_behavior.autopilot.active` | P3 | Navixy: `avl_io_129` (Grain Moisture)> `can_cruise_control` (CAN Cruise Control) | Autopilot/Cruise control active |
| `driving_behavior.eco_score.daily_value` | P1 | Navixy: `avl_io_15` (Eco Score)> **Computed:** Fleeti backend (daily aggregation) | Eco-driving score for the current day (0-100) |
| `driving_behavior.eco_score.value` | P1 | Navixy: `avl_io_106` (BLE Humidity #3) | Eco driving evaluation value (0-100) |
| `driving_behavior.eco_score.duration` | P3 | Navixy: `avl_io_235` (Oil Level) | Duration of eco driving behavior (value + unit) |
| `driving_behavior.eco_score.green_driving_type` | P3 | Navixy: `avl_io_121` (Axle 4 Load) | Type of green driving event (0-8) |
| `driving_behavior.eco_score.green_driving_value` | P3 | Navixy: `avl_io_122` (Axle 5 Load) | Green driving evaluation value |
| `driving_behavior.eco_score.event_type` | P3 | Navixy: `avl_io_108` (BLE Humidity #4) | Eco driving event type (0-4) |
| `driving_behavior.daily_summary.distance` | P1 | **Computed:** Sum of trip distances for today | Total distance driven today (value + unit) |
| `driving_behavior.daily_summary.driving_duration` | P1 | Navixy: `avl_io_916` (SSF Electric Engine State)> **Computed:** Sum of trip durations for today | Total driving time today (value + unit) |
| `driving_behavior.daily_summary.idling_duration` | P1 | **Computed:** Sum of idling durations for today | Total idling time today (value + unit) |
| `driving_behavior.daily_summary.event_counts.*` | P1 | **Computed:** Count of events received today (Navixy: `avl_io_112` (AdBlue Level), `avl_io_114` (Engine Load), `avl_io_119` (Axle 2 Load), `avl_io_208` (Geofence zone 33), `avl_io_120` (Axle 3 Load), `avl_io_908` (SSF Request To Lock Engine), `avl_io_910` (SSF Footbrake Is Active), `avl_io_913` (SSF Engine Cover Open), `avl_io_914` (SSF Charging Wire Plugged), `avl_io_915` (SSF Batttery Charging)) | Daily count of harsh events (accel, brake, turn, overspeed, idle) |

---

## 11. Sensors

**Purpose:** External and internal sensor readings (temperature, humidity, battery, etc.).

### Structure
```json
{
  "sensors": {
    "temperature": [
      {
        "position": "integer",
        "value": "decimal", 
        "unit": "string (°C)",
        "name": "string",
        "type": "string" 
      }
    ],
    "humidity": [ 
      {
        "position": "integer", 
        "value": "decimal", 
        "unit": "string (%)",
        "name": "string"
      }
    ],
    "battery": [ 
      {
        "value": "decimal", 
        "unit": "string (%)",
        "name": "string"
      }
    ],
    "signal": [ 
      {
        "value": "integer", 
        "unit": "string (dBm)",
        "tx_power": { "value": "integer", "unit": "string (dBm)" },
        "name": "string"
      }
    ],
    "magnet": [
      {
        "position": "integer",
        "value": "boolean (open/close)",
        "name": "string"
      }
    ],
    "frequency": [
      {
        "value": "decimal",
        "unit": "string (Hz)",
        "name": "string"
      }
    ],
    "potentiometer": [
      {
        "value": "decimal",
        "unit": "string (%)",
        "name": "string"
      }
    ],
    "inertial": [
      {
        "pitch": { "value": "decimal", "unit": "string (degrees)" },
        "roll": { "value": "decimal", "unit": "string (degrees)" },
        "name": "string"
      }
    ]
  }
}
```

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `sensors.temperature` | P0 | Navixy: `ble_temp_sensor_1` (BLE Temp 1), `ble_temp_sensor_2` (BLE Temp 2), `ble_temp_sensor_3` (BLE Temp 3), `ble_temp_sensor_4` (BLE Temp 4), `lls_temperature_1` (LLS Temperature 1), `lls_temperature_2` (LLS Temperature 2), `avl_io_72` (Dallas Temperature 1), `avl_io_73` (Dallas Temperature 2), `ext_temp_sensor_1` (External Temp 1), `ext_temp_sensor_2` (External Temp 2), `ext_temp_sensor_3` (External Temp 3), `temp_sensor` (Temperature Sensor), `avl_io_25` (BLE Temperature #1), `avl_io_26` (BLE Temperature #2), `avl_io_27` (BLE Temperature #3), `avl_io_28` (BLE Temperature #4) | Aggregated temperature readings (value + unit) |
| `sensors.humidity` | P1 | Navixy: `ble_humidity_1` (BLE Humidity 1), `ble_humidity_2` (BLE Humidity 2), `ble_humidity_3` (other), `ble_humidity_4` (other), `avl_io_86` (BLE Humidity #1), `avl_io_385` (Beacon), `avl_io_388` (Module ID 17B), `humidity_1` (Humidity 1), `humidity_2` (Humidity 2) | Aggregated humidity readings (value + unit) |
| `sensors.battery` | P2 | Navixy: `ble_battery_level_2` (BLE Battery 2), `ble_battery_level_3` (BLE Battery 3), `ble_battery_level_4` (BLE Battery 4), `avl_io_20` (BLE Battery #2), `avl_io_22` (BLE Battery #3), `avl_io_23` (BLE Battery #4), `avl_io_517` (Security State Flags P4) | Sensor battery levels (value + unit) |
| `sensors.signal` | P3 | Navixy: `avl_io_518` (Control State Flags P4) | Sensor signal strength (value + unit) |
| `sensors.signal[].tx_power` | P3 | Navixy: `avl_io_519` (Indicator State Flags P4) | Sensor TX power (value + unit) |
| `sensors.magnet` | P0 | Navixy: `ble_magnet_sensor_1` (other), `ble_magnet_sensor_2` (other), `ble_magnet_sensor_3` (other) | Magnet/Door sensors (0=closed, 1=open) |
| `sensors.frequency[]` | P3 | Navixy: `freq_1` (Frequency 1), `freq_2` (Frequency 2), `ble_frequency_1` (BLE Frequency 1) | Frequency sensor readings (value + unit) |
| `sensors.potentiometer[]` | P3 | Navixy: `avl_io_1086` (CSF Start Stop System Inactive) | Potentiometer sensor values (value + unit) |
| `sensors.inertial[]` | P3 | Navixy: `ble_pitch_1` (other), `ble_pitch_2` (other), `ble_roll_1` (other), `ble_roll_2` (other) | Inertial/orientation sensor readings (pitch, roll) |
| `sensors[].id` | P3 | Navixy: `avl_io_76` (Dallas Temperature ID 1), `avl_io_77` (Dallas Temperature ID 2), `avl_io_78` (iButton) | Sensor unique identifier |

---

## 12. I/O (Inputs/Outputs)

**Purpose:** Digital and analog input/output states.

### Structure
```json
{
  "io": {
    "inputs": {
      "bitmask": "integer (0-65535)",
      "individual": { "input_1": "boolean", ... }
    },
    "outputs": {
      "bitmask": "integer (0-255)",
      "individual": { "output_1": "boolean", ... }
    },
    "analog": {
      "values": ["mV", "mV", ...]
    }
  }
}
```

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `io.inputs.bitmask` | P0 | Navixy: `avl_io_945` (CSF Front Passenger Present) | Digital input status bitmask |
| `io.inputs.individual.*` | P0 | Navixy: `avl_io_1` (Digital Input 1), `avl_io_2` (Digital Input 2), `avl_io_3` (Digital Input 3), `avl_io_4` (Pulse Counter Din1) | Individual input states |
| `io.outputs.bitmask` | P0 | Navixy: `avl_io_940` (CSF Driver's Seatbelt Fastened)> `outputs` (Output Status) | Digital output status bitmask |
| `io.outputs.individual.*` | P0 | Navixy: `avl_io_118` (Axle 1 Load), `avl_io_152` (HV Battery Level), `avl_io_179` (Digital Output 1), `avl_io_180` (Digital Output 2) | Individual output states |
| `io.analog.values` | P0 | Navixy: `avl_io_941` (CSF Front Driver's Seatbelt Fastened), `avl_io_942` (CSF Left Driver's Seatbelt Fastened), `avl_io_943` (CSF Right Driver's Seatbelt Fastened), `avl_io_944` (CSF Centre Driver's Seatbelt Fastened)> `avl_io_6` (Analog Input 2)> `avl_io_9` (Analog Input 1)> `adc` (analog) | Analog input values (Prefer `avl_io` over generic `adc` (analog)) |

---

## 13. Driver

**Purpose:** Driver identification and related events.

### Structure
```json
{
  "driver": {
    "id": "integer",
    "hardware_key": {
      "ibutton": "hex string",
      "rfid": "integer"
    }
  }
}
```

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `driver.id` | P1 | Navixy: `avl_io_110` (Fuel Rate) | Driver ID |
| `driver.hardware_key.ibutton` | P0 | Navixy: `ibutton` (iButton ID) | iButton ID |
| `driver.hardware_key.rfid` | P0 | Navixy: `avl_io_960` (ISF Battery Not Charging Indicator) | RFID ID |
| `driver.ibutton_count` | P3 | Navixy: `avl_io_652` (SSF KeyInIgnitionLock) | Number of iButtons detected |

---

## 14. Device

**Purpose:** Tracking device status, configuration, and security.

### Structure
```json
{
  "device": {
    "battery": {
      "level": "%",
      "voltage": { "value": "decimal", "unit": "string (V)" },
      "current": { "value": "decimal", "unit": "string (mA)" },
      "capacity": { "value": "decimal", "unit": "string (mAh)" },
      "charging_state": "integer (0-3)"
    },
    "power": {
      "voltage": { "value": "decimal", "unit": "string (V)" },
      "connected": "boolean"
    },
    "temperature": { "value": "decimal", "unit": "string (°C)" },
    "firmware": {
      "version": "integer"
    },
    "sleep_mode": "integer (0-4)",
    "bluetooth": {
      "status": "integer (0-255)"
    }
  }
}
```

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `device.battery.level` | P2 | Navixy: `battery_level` (Battery Level)> `avl_io_113` (Battery Level)> `avl_io_947` (CSF Front Differential Locked) | Internal battery % |
| `device.battery.voltage` | P2 | Navixy: `battery_voltage` (Battery Voltage)> `avl_io_67` (Battery Voltage) | Internal battery voltage (value + unit) |
| `device.battery.current` | P2 | Navixy: `battery_current` (Battery Current)> `avl_io_68` (Battery Current) | Internal battery current (value + unit) |
| `device.battery.capacity` | P3 | Navixy: `avl_io_948` (CSF Rear Differential Locked) | Battery capacity (value + unit) |
| `device.battery.charging_state` | P2 | Navixy: `avl_io_131` (Gap Under Harvesting Drum) | Battery charging state (0-3) |
| `device.power.voltage` | P1 | Navixy: `board_voltage` (External Voltage)> `avl_io_66` (External Voltage) | External power voltage (value + unit) |
| `device.power.connected` | P2 | Navixy: `external_power_state` (External Power) | External power status |
| `device.temperature` | P3 | Navixy: `avl_io_89` (Fuel level) | Internal device temperature (value + unit) |
| `device.firmware.version` | P3 | Navixy: `avl_io_100` (Program Number) | Device firmware version identifier |
| `device.sleep_mode` | P3 | Navixy: `avl_io_200` (Sleep Mode) | Device sleep mode status (0-4) |
| `device.bluetooth.status` | P3 | Navixy: `avl_io_263` (BT Status)> `avl_io_237` | Bluetooth status (0-255) |

| **Note:** FOTA (Firmware Over-The-Air) update fields (`avl_io_898` (SSF Ignition), `avl_io_900` (SSF Engine Working), `avl_io_902` (SSF Ready To Drive)) are **ignored** as they are device management fields, not telemetry data. See [Section 19: Low Priority & Ignored Fields](#19-low-priority--ignored-fields) for details.

---

## 15. Events

**Purpose:** Event-specific data (TBD in separate specification).

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `events.towing` | P1 | Navixy: `towing` (Towing)> `avl_io_125` (Towing Detection) | Towing detected |
| `events.trip` | P3 | Navixy: `avl_io_250` (Trip) | Trip status (Navixy logic) |
| `events.idling` | P3 | Navixy: `avl_io_251` (Idling) | Idling status (Navixy logic) |
| `events.crash` | P1 | Navixy: `avl_io_126` (Area of Harvest)> `avl_io_759` (Fuel Type) | Crash/accident detection |
| `events.device_unplugged` | P2 | Navixy: `avl_io_252` (Unplug) | Device unplug event |
| `events.driver.ibutton_connected` | P3 | Navixy: `avl_io_653` (SSF Handbrake Is Active) | iButton connection event |
| `events.driver.ibutton_disconnected` | P3 | Navixy: `avl_io_654` (SSF Front Left Door Open) | iButton disconnection event |
| `events.driver.ibutton_new` | P3 | Navixy: `avl_io_655` (SSF Front Right Door Open) | New iButton detected |
| `events.driver.ibutton_hold` | P3 | Navixy: `avl_io_656` (SSF Rear Left Door Open) | iButton hold event |
| `events.eco_driving` | P3 | Navixy: `avl_io_234` (CNG Level) | Eco driving event counter |
| `events.datalink` | P3 | Navixy: `avl_io_966` (ISF Low Tire Pressure Indicator) | Datalink communication event |
| `events.gnss_jamming` | P2 | Navixy: `avl_io_128` (Grain Mown Volume) | GNSS jamming detection |

---

## 16. Geofence

**Purpose:** Geofence zone information (Device-side).

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `geofence.zone_id` | P3 | Navixy: `avl_io_155` (Geofence zone 01) | Geofence zone ID |
| `geofence.auto_status` | P3 | Navixy: `avl_io_175` (Auto Geofence) | Auto geofence status |

---

## 17. Other

**Purpose:** Miscellaneous fields and raw CAN data.

### Structure
```json
{
  "other": {
    "raw_can": ["...", ...],
    "impulse_counters": ["...", ...],
    "flags": {
      "control_state": "integer (bitmask)",
      "agricultural_state": "integer (bitmask)",
      "utility_state": "integer (bitmask)",
      "cistern_state": "integer (bitmask)"
    }
  }
}
```

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `other.raw_can` | P3 | Navixy: `raw_can_1` (Raw CAN 1), `raw_can_3` (Raw CAN 3), `raw_can_8` (Raw CAN 8), `raw_can_9` (Raw CAN 9), `raw_can_11` (Raw CAN 11), `raw_can_14` (Raw CAN 14), `raw_can_15` (Raw CAN 15), `raw_can_16` (Raw CAN 16), `raw_can_17` (Raw CAN 17) | Raw CAN data dump |
| `other.impulse_counters` | P3 | Navixy: `impulse_counter_1` (Impulse Counter 1), `impulse_counter_2` (Impulse Counter 2) | Pulse counters |
| `other.flags.control_state` | P3 | Navixy: `avl_io_123` (Control State Flags) | Control state flags bitmask |
| `other.flags.agricultural_state` | P3 | Navixy: `avl_io_520` (Agricultural State Flags P4) | Agricultural state flags protocol 4 (bitmask) |
| `other.flags.utility_state` | P3 | Navixy: `avl_io_521` (Utility State Flags P4) | Utility state flags protocol 4 (bitmask) |
| `other.flags.cistern_state` | P3 | Navixy: `avl_io_522` (Cistern State Flags P4) | Cistern state flags protocol 4 (bitmask) |

---

## 18. Packet Metadata

**Purpose:** Metadata about the telemetry packet itself.

### Structure
```json
{
  "last_updated_at": "ISO8601 timestamp",
  "debug": {
    "provider": "navixy",
    "time": {
      "device_time": "ISO8601 timestamp",
      "provider_time": "ISO8601 timestamp",
      "fleeti_time": "ISO8601 timestamp"
    },
    "provider_payload": {
      "navixy": {
        "code": "integer",
        "sub_code": "integer",
        "priority": "integer (0-3)"
      }
    }
  }
}
```

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `last_updated_at` | P0 | Fleeti pipeline | Snapshot timestamp |
| `debug.time.device_time` | P0 | Navixy: `msg_time` (metadata) | Device timestamp |
| `debug.time.provider_time` | P0 | Navixy: `server_time` (metadata) | Provider timestamp |
| `debug.provider_payload.*` | P0 | Navixy: `EVENT` (Event), `avl_io_111` (AdBlue Level) | Raw event codes |
| `debug.provider_payload.navixy.code` | P0 | Navixy: `event_code` (Event Code) | Event type identifier |
| `debug.provider_payload.navixy.sub_code` | P0 | Navixy: `sub_event_code` (Sub Event Code) | Sub-event type identifier |

---

## 19. Low Priority & Clarification

**Purpose:** Fields that require clarification or business logic decisions before final mapping. These fields have uncertain mappings and need user/stakeholder input to determine the correct Fleeti field path.

### Fields Requiring Clarification

| Navixy Field | Priority | Proposed Options | Questions / Notes | Teltonika AVL IO Description |
|--------------|----------|------------------|-------------------|------------------------------|
| `avl_io_127` (Mowing Efficiency) | P3 | `power.immobilizer.active` OR `io.outputs.*` | Redundant with `io.outputs` status? Should this be mapped if it provides different information? | [Not found in Teltonika documentation] |
| `avl_io_238` (User ID) | P3 | `driver.extended_id` OR Ignored | What additional information does this provide over `driver.id`? Is this a different ID system? | [Not found in Teltonika documentation] |
| `avl_io_243` (Green driving event duration) | P3 | `motion.instant_movement` OR Ignored | What is the difference from `motion.is_moving`? Is this a different detection method? | [Not found in Teltonika documentation] |
| `avl_io_303` (Instant Movement) | P3 | `motion.instant_movement_duration` OR Ignored | What does "instant movement duration" mean? Is this related to `avl_io_243` (Green driving event duration)? | [Not found in Teltonika documentation] |
| `avl_io_207` (RFID) | P3 | `diagnostics.engine.load` | Is this different from `can_engine_load` (CAN Engine Load)? Should this also map to `diagnostics.engine.load`? | [Not found in Teltonika documentation] |
| `can_engine_state` (can) | P1 | `power.ignition` OR `diagnostics.engine.state` | Is this the same as ignition or different? What values does it contain? | N/A |
| `avl_io_380` (Digital output 3) | P3 | `driver.authorized` OR `status.authorized_driving` OR Ignored | What is the source of this authorization? Should it be ignored as backend-computed? | [Not found in Teltonika documentation] |
| `status` (Status) | P3 | `device.status_bitmap` OR `debug.device_status` OR Ignored | What specific flags does this bitmap contain? Should we parse individual flags or ignore? Generic device status bitmap; specific flags are preferred. | N/A |
| `avl_io_652` (SSF KeyInIgnitionLock) | P3 | `driver.ibutton_count` OR `device.ibutton_count` | Is this the number of iButtons currently detected? Or is this a counter that increments? | [Not found in Teltonika documentation] |
| `avl_io_935` (CSF Light Signal) | P0 | `sensors.custom[]` OR specific sensor type | What kind of sensor this is? Should we create a generic `sensors.custom[]` array? | [Not found in Teltonika documentation] |
| `avl_io_936` (CSF Air Conditioning) | P0 | `sensors.custom[]` OR specific sensor type | What kind of sensor this is? Should we create a generic `sensors.custom[]` array? | [Not found in Teltonika documentation] |
| `avl_io_331` (BLE 1 Custom #1) | P3 | `sensors.temperature[]` OR Section 19 | Custom IO element for BLE sensor - catalog suggests temperature but field is configurable. Verify actual purpose per installation. | Custom IO element for BLE sensor |
| `avl_io_332` (BLE 2 Custom #1) | P3 | `sensors.temperature[]` OR Section 19 | Custom IO element for BLE sensor - catalog suggests temperature but field is configurable. Verify actual purpose per installation. | Custom IO element for BLE sensor |
| `avl_io_333` (BLE 3 Custom #1) | P3 | `sensors.temperature[]` OR Section 19 | Custom IO element for BLE sensor - catalog suggests temperature but field is configurable. Verify actual purpose per installation. | Custom IO element for BLE sensor |
| `avl_io_463` (BLE 1 Custom #2) | P3 | `fuel.consumption.cumulative` OR Section 19 | Custom IO element for BLE sensor - catalog suggests fuel consumption but field is configurable. Verify actual purpose per installation. | Custom IO element for BLE sensor |
| `avl_io_464` (BLE 1 Custom #3) | P3 | `diagnostics.maintenance.service_distance` OR Section 19 | Custom IO element for BLE sensor - catalog suggests service distance but field is configurable. Verify actual purpose per installation. | Custom IO element for BLE sensor |
| `avl_io_465` (BLE 1 Custom #4) | P3 | `diagnostics.fluids.adblue_level` OR Section 19 | Custom IO element for BLE sensor - catalog suggests AdBlue level but field is configurable. Verify actual purpose per installation. | Custom IO element for BLE sensor |
| `avl_io_466` (BLE 1 Custom #5) | P3 | `diagnostics.brakes.parking_brake` OR Section 19 | Custom IO element for BLE sensor - catalog suggests parking brake but field is configurable. Verify actual purpose per installation. | Custom IO element for BLE sensor |
| `avl_io_467` (BLE 2 Custom #2) | P3 | `fuel.consumption.economy` OR Section 19 | Custom IO element for BLE sensor - catalog suggests fuel economy but field is configurable. Verify actual purpose per installation. | Custom IO element for BLE sensor |
| `avl_io_468` (BLE 2 Custom #3) | P3 | `counters.odometer` OR Section 19 | Custom IO element for BLE sensor - catalog suggests odometer but field is configurable. Verify actual purpose per installation. | Custom IO element for BLE sensor |
| `avl_io_469` (BLE 2 Custom #4) | P3 | `diagnostics.axles.weights` OR Section 19 | Custom IO element for BLE sensor - catalog suggests axle weight but field is configurable. Verify actual purpose per installation. | Custom IO element for BLE sensor |
| `avl_io_470` (BLE 2 Custom #5) | P3 | `diagnostics.axles.weights` OR Section 19 | Custom IO element for BLE sensor - catalog suggests axle weight but field is configurable. Verify actual purpose per installation. | Custom IO element for BLE sensor |
| `avl_io_471` (BLE 3 Custom #2) | P3 | `fuel.consumption.rate` OR Section 19 | Custom IO element for BLE sensor - catalog suggests fuel consumption rate but field is configurable. Verify actual purpose per installation. | Custom IO element for BLE sensor |
| `avl_io_472` (BLE 3 Custom #3) | P3 | `fuel.consumption.trip.value` OR Section 19 | Custom IO element for BLE sensor - catalog suggests trip fuel consumption but field is configurable. Verify actual purpose per installation. | Custom IO element for BLE sensor |
| `avl_io_473` (BLE 3 Custom #4) | P3 | `driving_behavior.brake_position` OR Section 19 | Custom IO element for BLE sensor - catalog suggests brake position but field is configurable. Verify actual purpose per installation. | Custom IO element for BLE sensor |
| `can_low_fuel` (can) | P2 | `diagnostics.health.low_fuel_warning` OR `fuel.levels[].warning` OR `diagnostics.warnings.*` | Should this be a boolean warning flag? Should it be part of fuel section or diagnostics section? | N/A |
| `can_oil_pressure_or_level` (vehicle_health) | P2 | `diagnostics.fluids.oil_pressure` OR `diagnostics.fluids.oil_level` OR Both | Is this pressure or level or both? What unit should be used? | N/A |
| `can_coolant_temp_or_level` (vehicle_health) | P2 | `diagnostics.engine.coolant_temperature` OR `diagnostics.fluids.coolant_level` OR Both | Is this temperature or level or both? What unit should be used for level? | N/A |
| `can_electronics_power_control` (CAN Electronics Power Control) | P2 | `diagnostics.health.electronics_power_control` OR `diagnostics.warnings.*` | What does this warning indicate? Should this be a boolean warning flag? | N/A |
| `can_warning` (CAN Warning) | P2 | `diagnostics.health.general_warning` OR `diagnostics.warnings.*` OR Bitmask | Is this a single boolean or bitmask? What specific warnings does this indicate? | N/A |
| `acceleration` (Acceleration), `braking` (Braking), `cornering` (Cornering), `cornering_rad` (Cornering Radius) | P1 | Events stream OR `driving_behavior.acceleration` etc. | Should this be in telemetry snapshot or events stream only? Used in events stream but can reference when necessary to explain ecoscore. | N/A |
| `avl_io_199` (Trip Odometer) | P1 | `trip.distance` OR `counters.trip_odometer` | Is this a cumulative counter or trip-specific? Should this map to `trip.distance` in Telemetry Context? | [Not found in Teltonika documentation] |
| `obd_time_since_engine_start` (OBD Engine Runtime) | P1 | `trip.duration` OR `counters.trip_engine_hours` | Does this reset every trip or is it cumulative? Should this map to `trip.duration`? | N/A |
| `avl_io_131` (Gap Under Harvesting Drum) | P2 | `device.battery.charging_state` (enum) | What do the values 0-3 represent? Should this be a new field `device.battery.charging_state`? | [Not found in Teltonika documentation] |
| `avl_io_81` (Vehicle Speed) | P3 | `connectivity.cell.id` OR `motion.speed` OR Ignored | CSV maps to `connectivity.cell.id` but name suggests speed. Is this a duplicate of `avl_io_37` (Vehicle Speed) or `speed` (Speed)? Should this be ignored or mapped differently? | [Not found in Teltonika documentation] |
| `avl_io_82` (Accelerator Pedal Position) | P3 | `connectivity.cell.lac` OR `driving_behavior.throttle_position` OR Ignored | CSV maps to `connectivity.cell.lac` but name suggests throttle position. Is this a duplicate of `can_throttle` (CAN Throttle) or `avl_io_41` (Throttle Position)? Should this be ignored or mapped differently? | [Not found in Teltonika documentation] |

---

**Document Version:** 1.2  
**Last Updated:** 2025-01-21  
**Generated From:** Navixy Field Catalog (338 fields)  
**Status:** All 338 fields accounted for (336 mapped, 2 in Section 19 for clarification)
