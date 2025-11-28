# Telemetry Schema Analysis

## 📊 Overview

This document provides a comprehensive analysis of the complete Fleeti Telemetry structure based on the catalog of 161 telemetry fields extracted from Navixy Data Forwarding.

**Generated from:** Fleeti Field Mapping Expanded CSV  
**Total Fields Cataloged:** 161  
**Fields with Multiple Sources:** 59  
**Date:** 2025-01-28

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
5. [Motion](#5-motion)
6. [Power](#6-power)
7. [Fuel](#7-fuel)
8. [Counters](#8-counters)
9. [Driving Behavior](#9-driving-behavior)
10. [Sensors](#10-sensors)
11. [Diagnostics](#11-diagnostics)
12. [I/O (Inputs/Outputs)](#12-i-o-inputs-outputs)
13. [Driver](#13-driver)
14. [Device](#14-device)
15. [Events](#15-events)
16. [Geofence](#16-geofence)
17. [Other](#17-other)
18. [Packet Metadata](#18-packet-metadata)

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
    // ... (see original document for complete structure)
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
| `asset.properties.vehicle.vin` | Navixy: `avl_io_132` (Security State Flags) | ⚠️ **Needs verification:** VIN mapping from Security State Flags seems incorrect. |

| **Note:** Most asset metadata fields come from Fleeti catalog. ⚠️ **Needs verification:** The VIN field (`asset.properties.vehicle.vin`) is currently mapped from `avl_io_132` (Security State Flags), which appears to be semantically incorrect. Please verify the correct AVL ID for VIN.

---

## 2. Telemetry Context

**Purpose:** Computed/derived fields that change per telemetry packet. These are calculated from raw telemetry combined with asset metadata. Includes status families (connectivity, transit, engine, immobilization), current geofence context, and ongoing trip information.

### Structure
```json
{
  "status": {
    "top_status": { "family": "transit", "code": "in_transit", "updated_at": "ISO8601" },
    "statuses": [
      { "family": "connectivity", "code": "online", "compatible": true, "updated_at": "ISO8601" }
    ]
  },
  "geofences": [...],
  "trip": { "id": "uuid", "started_at": "ISO8601", "distance": { "value": 45.2, "unit": "km" } },
  "nearby_assets": [...]
}
```

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `status.top_status` | P0 | **Computed:** Highest-priority status family | Connectivity > Immobilization > Engine > Transit |
| `status.statuses[]` | P0 | **Computed:** Telemetry + Asset Metadata | Array of compatible status families with codes |
| `geofences[]` | P2 | **Computed:** `location.lat`/`lng` + Geofence Service | Current geofences the asset is inside |
| `trip` | P1 | **Computed:** Ignition + Movement history | Ongoing trip information (nullable) |
| `trip.distance` | P2 | Navixy: `avl_io_199` (Trip Odometer) | Trip Odometer value |
| `trip.duration` | P1 | Navixy: `obd_time_since_engine_start` (OBD Engine Runtime), `avl_io_42` (Runtime since engine start) | Runtime since engine start |

| **Computation Rules:** See Telemetry Status Rules for definitive logic on status transitions, compatibility matrices, and priority ordering.

---

## 3. Location

**Purpose:** GPS/GNSS positioning data and location precision metrics.

### Structure
```json
{
  "location": {
    // Field structure based on mappings below
  }
}
```

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `location.altitude` | P2 | Navixy: `alt` (Altitude) | Altitude |
| `location.hdop` | P2 | Navixy: `avl_io_182` (GNSS HDOP), `hdop` (HDOP) | Coefficient, calculation formula |
| `location.heading` | P2 | Navixy: `heading` (Heading) | Heading |
| `location.latitude` | P2 | Navixy: `lat` (Latitude) | Latitude |
| `location.longitude` | P2 | Navixy: `lng` (Longitude) | Longitude |
| `location.pdop` | P2 | Navixy: `avl_io_181` (GNSS PDOP), `pdop` (PDOP) | Coefficient, calculation formula |
| `location.precision.fix_quality` | P2 | Navixy: `avl_io_69` (GNSS Status) | 0 - GNSS OFF 1 – GNSS ON with fix 2 - GNSS ON without fix 3 - GNSS sleep 4 - GNSS ON with fix, invalid data |
| `location.satellites` | P2 | Navixy: `satellites` (Satellites) | Satellites |

---

## 4. Connectivity

**Purpose:** Network and communication status information.

### Structure
```json
{
  "connectivity": {
    // Field structure based on mappings below
  }
}
```

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `connectivity.cell.id` | P2 | Navixy: `avl_io_205` (GSM Cell ID) | GSM base station ID |
| `connectivity.cell.lac` | P2 | Navixy: `avl_io_206` (GSM Area Code) | Location Area code (LAC), it depends on GSM operator. It provides unique number which assigned to a set of base GSM s... |
| `connectivity.data_mode` | P2 | Navixy: `avl_io_80` (Data Mode) | Used differently across models. Most commonly: GSM/LTE network mode / roaming status. Sometimes appears as �Data Mode... |
| `connectivity.operator` | P2 | Navixy: `avl_io_241` (Active GSM Operator) | Currently used GSM Operator code |
| `connectivity.signal_level` | P2 | Navixy: `avl_io_21` (GSM Signal), `gsm.signal.csq` (GSM Signal CSQ) | Value in range 1-5 Explanation |
| `connectivity.sim.iccid[]` | P2 | Navixy: `avl_io_11` (ICCID1), `avl_io_14` (ICCID2) | Value of SIM ICCID, MSB |

---

## 5. Motion

**Purpose:** Dynamic movement data including speed and motion status.

### Structure
```json
{
  "motion": {
    // Field structure based on mappings below
  }
}
```

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `motion.accelerometer.x` | P2 | Navixy: `avl_io_17` (Axis X), `axis_x` (Axis X) | X axis value |
| `motion.accelerometer.y` | P2 | Navixy: `avl_io_18` (Axis Y), `axis_y` (Axis Y) | Y axis value |
| `motion.accelerometer.z` | P2 | Navixy: `avl_io_19` (Axis Z), `axis_z` (Axis Z) | Z axis value |
| `motion.instant_movement` | P2 | Navixy: `avl_io_303` (Instant Movement) | Logic: 0/1 returns movement value |
| `motion.is_moving` | P2 | Navixy: `avl_io_240` (Movement), `moving` (Is Moving) | 0 – Movement Off 1 – Movement On |
| `motion.speed` | P0 | Navixy: `can_speed` (CAN Speed), `obd_speed` (OBD Speed), `avl_io_24` (Speed), `avl_io_37` (Vehicle Speed), `avl_io_81` (Vehicle Speed), `speed` (Speed) | GNSS Speed |

---

## 6. Power

**Purpose:** Power source status, ignition state, and battery health (asset/vehicle battery).

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `ev.battery.level` | P2 | Navixy: `avl_io_152` (HV Battery Level) | Battery level in percent |
| `ev.charging.active` | P2 | Navixy: `avl_io_915` (SSF Batttery Charging) | 0 - Not charging 1 - Charging |
| `ev.charging.cable_plugged` | P2 | Navixy: `avl_io_914` (SSF Charging Wire Plugged) | 0 - Unplugged 1 - Plugged |
| `ev.motor.active` | P2 | Navixy: `avl_io_916` (SSF Electric Engine State) | 0 - Off 1 - On |
| `ev.range.estimated_distance` | P2 | Navixy: `avl_io_304` (Vehicles Range On Battery) | Vehicle Range on Battery |
| `ev.ready_to_drive` | P2 | Navixy: `avl_io_902` (SSF Ready To Drive) | 0 - No 1 - Yes |
| `power.battery.level` | P0 | Navixy: `can_battery_level` | can |
| `power.ignition` | P0 | Navixy: `can_engine_state`, `can_ignition_state` (CAN Ignition), `avl_io_239` (Ignition) | 0 – Ignition Off 1 – Ignition On |
| `engine.ignition_on` | P2 | Navixy: `avl_io_898` (SSF Ignition) | 0 - No 1 - Yes |
| `engine.running` | P2 | Navixy: `avl_io_900` (SSF Engine Working) | 0 - No 1 - Yes |

---

## 7. Fuel

**Purpose:** Fuel system data including levels, consumption, and temperature.

### Structure
```json
{
  "fuel": {
    // Field structure based on mappings below
  }
}
```

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `fuel.consumption.cumulative` | P0 | Navixy: `can_consumption`, `can_consumption_relative`, `avl_io_103` (Fuel Used GPS), `avl_io_107` (Fuel Consumed (counted)), `avl_io_83` (Fuel Consumed) | Same concept as 102: total engine motor hours. Some models use 102, others 103. |
| `fuel.consumption.rate` | P0 | Navixy: `can_fuel_rate` (CAN Fuel Rate), `avl_io_110` (Fuel Rate) | Fuel rate |
| `fuel.energy.cng_status` | P2 | Navixy: `avl_io_232` (CNG Status) | CNG Status |
| `fuel.levels[].value` | P0 | Navixy: `can_fuel_1`, `can_fuel_litres`, `avl_io_390` (OBD OEM Fuel Level), `obd_custom_fuel_litres`, `avl_io_201` (LLS 1 Fuel Level), `avl_io_203` (LLS 2 Fuel Level), `avl_io_210` (LLS 3 Fuel Level), `avl... | Fuel level measured by LLS sensor via RS232/RS485 |
| `vehicle.energy.fuel_type_code` | P2 | Navixy: `avl_io_759` (Fuel Type) | 0 Not available 1 Gasoline 2 Methanol 3 Ethanol 4 Diesel 5 LPG 6 CNG 7 Propane 8 Electric 9 Bifuel running Gasoline 1... |

---

## 8. Counters

**Purpose:** Accumulated counters for odometer and engine hours.

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `counters.engine_hours` | P0 | Navixy: `can_engine_hours` (CAN Engine Hours), `can_engine_hours_relative`, `avl_io_449` (Ignition On Counter) | Duration in seconds which is counted while Ignition state is On |
| `counters.engine_hours.total` | P2 | Navixy: `avl_io_102` (Engine Worktime) | Total engine work time from CAN (motor hours). |
| `counters.odometer` | P0 | Navixy: `can_mileage` (CAN Mileage), `can_mileage_relative`, `avl_io_389` (OBD OEM Total Mileage), `obd_custom_odometer`, `avl_io_105` (Total Mileage (counted)), `avl_io_16` (Total Odometer), `avl_io_87` (... | Total Vehicle Mileage |

---

## 9. Driving Behavior

**Purpose:** Daily aggregated driving metrics and eco-driving scores.

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `driving_behavior.brake_active` | P0 | Navixy: `can_footbrake_state` (CAN Footbrake State), `avl_io_910` (SSF Footbrake Is Active) | 0 - Footbrake inactive 1 - Footbrake active |
| `driving_behavior.daily_summary.driving_duration` | P0 | Navixy: `Computed` | N/A |
| `driving_behavior.daily_summary.event_counts.*` | P0 | Navixy: `Computed`, `Computed`, `Computed`, `Computed`, `Computed` | N/A |
| `driving_behavior.daily_summary.event_counts.excessive_idling` | P0 | Navixy: `Computed` | N/A |
| `driving_behavior.daily_summary.event_counts.harsh_acceleration` | P0 | Navixy: `Computed` | N/A |
| `driving_behavior.daily_summary.event_counts.harsh_braking` | P0 | Navixy: `Computed` | N/A |
| `driving_behavior.daily_summary.event_counts.harsh_cornering` | P0 | Navixy: `Computed` | N/A |
| `driving_behavior.daily_summary.event_counts.overspeed` | P0 | Navixy: `Computed` | N/A |
| `driving_behavior.eco_score.daily_value` | P0 | Navixy: `Computed` | N/A |
| `driving_behavior.eco_score.event_duration` | P2 | Navixy: `avl_io_243` (Green driving event duration) | Duration of event that did generate Green driving |
| `driving_behavior.eco_score.green_driving_type` | P2 | Navixy: `avl_io_253` (Green driving type) | 1 – harsh acceleration 2 – harsh braking 3 – harsh cornering |
| `driving_behavior.eco_score.green_driving_value` | P2 | Navixy: `avl_io_254` (Green Driving Value) | Depending on green driving type: if harsh acceleration or braking – g*100 (value 123 -> 1.23g). If Green driving sour... |
| `driving_behavior.eco_score.value` | P2 | Navixy: `avl_io_15` (Eco Score) | Average amount of events on some distance |
| `driving_behavior.privacy_mode` | P2 | Navixy: `avl_io_391` (Private mode) | Private mode state: 0 - Private mode off 1 - Private mode on |
| `driving_behavior.throttle_position` | P0 | Navixy: `can_throttle` (CAN Throttle), `obd_throttle` (OBD Throttle), `avl_io_41` (Throttle Position), `avl_io_82` (Accelerator Pedal Position) | Throttle position |

---

## 10. Sensors

**Purpose:** External and internal sensor readings (temperature, humidity, battery, etc.).

### Structure
```json
{
  "sensors": {
    // Field structure based on mappings below
  }
}
```

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `sensors.battery` | P2 | Navixy: `avl_io_20` (BLE Battery #2), `avl_io_22` (BLE Battery #3), `avl_io_23` (BLE Battery #4), `ble_battery_level_2` (BLE Battery 2), `ble_battery_level_3` (BLE Battery 3), `ble_battery_level_4` (BLE Ba... | Battery level of sensor #2 |
| `sensors.custom[]` | P2 | Navixy: `avl_io_331` (BLE 1 Custom #1), `avl_io_332` (BLE 2 Custom #1), `avl_io_333` (BLE 3 Custom #1), `avl_io_463` (BLE 1 Custom #2), `avl_io_464` (BLE 1 Custom #3), `avl_io_465` (BLE 1 Custom #4), `avl_... | Custom IO element for BLE sensor |
| `sensors.frequency[]` | P2 | Navixy: `avl_io_306` (BLE Fuel Frequency #1), `ble_frequency_1` (BLE Frequency 1), `freq_1` (Frequency 1), `freq_2` (Frequency 2) | Frequency value of BLE fuel sensor #1 |
| `sensors.humidity` | P2 | Navixy: `ble_humidity_1` (BLE Humidity 1), `ble_humidity_2` (BLE Humidity 2), `ble_humidity_3`, `ble_humidity_4`, `humidity_1` (Humidity 1), `humidity_2` (Humidity 2) | BLE Humidity 1 |
| `sensors.humidity[]` | P2 | Navixy: `avl_io_104` (BLE Humidity #2), `avl_io_106` (BLE Humidity #3), `avl_io_108` (BLE Humidity #4), `avl_io_86` (BLE Humidity #1) | Humidity From firmware version 03.28.00 and up: 65535 - sensor not found 65534 - failed sensor data parsing 65533 - a... |
| `sensors.inertial[].pitch` | P2 | Navixy: `ble_pitch_1`, `ble_pitch_2` | other |
| `sensors.inertial[].roll` | P2 | Navixy: `ble_roll_1`, `ble_roll_2` | other |
| `sensors.magnet` | P2 | Navixy: `ble_magnet_sensor_1`, `ble_magnet_sensor_2`, `ble_magnet_sensor_3` | other |
| `sensors.temperature` | P2 | Navixy: `avl_io_202` (LLS 1 Temperature), `avl_io_204` (LLS 2 Temperature), `avl_io_25` (BLE Temperature #1), `avl_io_26` (BLE Temperature #2), `avl_io_27` (BLE Temperature #3), `avl_io_28` (BLE Temperatur... | Fuel temperature measured by LLS via RS232/RS485 |
| `sensors[].id` | P2 | Navixy: `avl_io_76` (Dallas Temperature ID 1), `avl_io_77` (Dallas Temperature ID 2) | Dallas sensor ID |

---

## 11. Diagnostics

**Purpose:** Detailed asset diagnostics, including CAN bus data, engine stats, and body sensors.

### Structure
```json
{
  "diagnostics": {
    // Field structure based on mappings below
  }
}
```

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `diagnostics.agricultural.area_harvested` | P2 | Navixy: `avl_io_126` (Area of Harvest) | Area of harvest in square meters |
| `diagnostics.agricultural.grain_moisture` | P2 | Navixy: `avl_io_129` (Grain Moisture) | Grain moisture |
| `diagnostics.agricultural.grain_volume` | P2 | Navixy: `avl_io_128` (Grain Mown Volume) | Mown volume |
| `diagnostics.agricultural.harvest_duration` | P2 | Navixy: `avl_io_125` (Harvest Duration) | Duration of harvesting activity (agricultural CAN signal). |
| `diagnostics.agricultural.harvesting_drum_gap` | P2 | Navixy: `avl_io_131` (Gap Under Harvesting Drum) | Gap under harvesting drum |
| `diagnostics.agricultural.harvesting_drum_rpm` | P2 | Navixy: `avl_io_130` (Harvesting Drum RPM) | Harvesting drum rpm |
| `diagnostics.agricultural.mowing_efficiency` | P2 | Navixy: `avl_io_127` (Mowing Efficiency) | Mowing efficiency |
| `diagnostics.axles.weights` | P0 | Navixy: `can_axle_load_1` (CAN Axle Load 1), `can_axle_load_2` (CAN Axle Load 2), `can_axle_load_3` (CAN Axle Load 3), `can_axle_load_4` (CAN Axle Load 4), `can_axle_load_5` (CAN Axle Load 5), `avl_io_118`... | Axle 1 load |
| `diagnostics.body.belts.*` | P0 | Navixy: `can_rear_centre_seat_belt_state` (CAN Rear Centre Seat Belt State), `can_rear_left_seat_belt_state` (CAN Rear Left Seat Belt State), `can_rear_right_seat_belt_state` (CAN Rear Right Seat Belt Stat... | 0 - Not fastened 1 - Fastened |
| `diagnostics.body.doors.*` | P0 | Navixy: `can_door_state`, `can_front_left_door` (CAN Front Left Door), `can_front_right_door`, `can_hood_state` (CAN Hood State), `can_rear_left_door`, `can_rear_right_door`, `can_roof_state` (CAN Roof Sta... | 0 - Closed 1 - Open |
| `diagnostics.body.lights.*` | P0 | Navixy: `can_additional_front_fog_lights`, `can_additional_rear_lights`, `can_dipped_headlights` (CAN Dipped Headlights), `can_front_fog_lights` (CAN Front Fog Lights), `can_full_beam_headlights` (CAN Full... | 0 - Off 1 - On |
| `diagnostics.brakes.abs_active` | P0 | Navixy: `can_abs_state` (CAN ABS State) | CAN ABS State |
| `diagnostics.brakes.pad_wear` | P0 | Navixy: `can_brake_pad_wear` (CAN Brake Pad Wear) | CAN Brake Pad Wear |
| `diagnostics.brakes.parking_brake` | P0 | Navixy: `can_hand_brake_state` (CAN Hand Brake), `avl_io_653` (SSF Handbrake Is Active) | 0 - Handbrake inactive 1 - Handbrake active |
| `diagnostics.brakes.retarder_automatic` | P0 | Navixy: `can_automatic_retarder` (CAN Automatic Retarder) | CAN Automatic Retarder |
| `diagnostics.brakes.retarder_manual` | P0 | Navixy: `can_manual_retarder` (CAN Manual Retarder) | CAN Manual Retarder |
| `diagnostics.climate.air_conditioning` | P0 | Navixy: `can_air_conditioning`, `avl_io_936` (CSF Air Conditioning) | 0 - Off 1 - On |
| `diagnostics.drivetrain.central_differential_4hi_locked` | P0 | Navixy: `can_central_diff_4hi_locked` (CAN Central Diff 4HI Locked) | CAN Central Diff 4HI Locked |
| `diagnostics.drivetrain.central_differential_4lo_locked` | P0 | Navixy: `can_central_diff_4lo_locked` (CAN Central Diff 4LO Locked) | CAN Central Diff 4LO Locked |
| `diagnostics.drivetrain.clutch_state` | P0 | Navixy: `can_clutch_state` (CAN Clutch State) | CAN Clutch State |
| `diagnostics.drivetrain.cruise_control_active` | P0 | Navixy: `can_cruise_control` (CAN Cruise Control) | CAN Cruise Control |
| `diagnostics.drivetrain.front_differential_locked` | P0 | Navixy: `can_front_diff_locked` (CAN Front Diff Locked), `avl_io_947` (CSF Front Differential Locked) | 0 - Unlocked 1 - Locked |
| `diagnostics.drivetrain.rear_differential_locked` | P0 | Navixy: `can_rear_diff_locked` (CAN Rear Diff Locked), `avl_io_948` (CSF Rear Differential Locked) | 0 - Unlocked 1 - Locked |
| `diagnostics.electrical.battery_not_charging` | P2 | Navixy: `avl_io_960` (ISF Battery Not Charging Indicator) | 0 - Off 1 - On |
| `diagnostics.engine.coolant_temperature` | P0 | Navixy: `can_coolant_temp_or_level` (vehicle_health) | vehicle_health |
| `diagnostics.engine.glow_plug_active` | P0 | Navixy: `can_glow_plug_indicator` (CAN Glow Plug Indicator) | CAN Glow Plug Indicator |
| `diagnostics.engine.load` | P0 | Navixy: `can_engine_load` (CAN Engine Load), `avl_io_114` (Engine Load) | Engine Load |
| `diagnostics.engine.pto_state` | P0 | Navixy: `can_pto_state` (CAN PTO State) | CAN PTO State |
| `diagnostics.engine.ready_to_drive` | P0 | Navixy: `can_ready_to_drive` (CAN Ready to Drive) | CAN Ready to Drive |
| `diagnostics.engine.rpm` | P0 | Navixy: `can_rpm` (CAN Engine RPM), `obd_rpm` (OBD RPM), `avl_io_36` (Engine RPM), `avl_io_85` (Engine RPM) | Engine RPM |
| `diagnostics.engine.start_stop_inactive` | P2 | Navixy: `avl_io_1086` (CSF Start Stop System Inactive) | 0 - No 1 - Yes |
| `diagnostics.engine.temperature` | P0 | Navixy: `can_engine_temp` (CAN Engine Temp), `avl_io_115` (Engine Temperature) | Engine Temperature |
| `diagnostics.engine.webasto_state` | P0 | Navixy: `can_webasto_state` (CAN Webasto State) | CAN Webasto State |
| `diagnostics.fluids.adblue.level_liters` | P2 | Navixy: `avl_io_112` (AdBlue Level) | AdBlue level |
| `diagnostics.fluids.adblue_level` | P0 | Navixy: `can_adblue_level` (CAN AdBlue Level), `avl_io_111` (AdBlue Level) | AdBlue |
| `diagnostics.fluids.oil_level` | P2 | Navixy: `avl_io_235` (Oil Level) | Engine Oil Level Indicator Status |
| `diagnostics.fluids.oil_pressure_or_level` | P0 | Navixy: `can_oil_pressure_or_level` (vehicle_health) | vehicle_health |
| `diagnostics.health.can_warning` | P0 | Navixy: `can_warning` (CAN Warning) | CAN Warning |
| `diagnostics.health.dtc_count` | P1 | Navixy: `obd_dtc_number` (OBD DTC Count), `avl_io_30` (Number of DTC) | Number of DTC |
| `diagnostics.health.electronics_power_control` | P0 | Navixy: `can_electronics_power_control` (CAN Electronics Power Control) | CAN Electronics Power Control |
| `diagnostics.health.low_fuel_warning` | P0 | Navixy: `can_low_fuel` | can |
| `diagnostics.health.low_tire_pressure_warning` | P0 | Navixy: `can_low_tire_pressure`, `avl_io_966` (ISF Low Tire Pressure Indicator) | 0 - Off 1 - On |
| `diagnostics.health.mil_activated_distance` | P1 | Navixy: `obd_mil_activated_distance` (OBD MIL Activated Distance), `avl_io_43` (Distance Traveled MIL On) | Distance ormattin MIL on |
| `diagnostics.health.mil_status` | P1 | Navixy: `obd_mil_status` (OBD MIL Status) | OBD MIL Status |
| `diagnostics.ignition.key_inserted` | P2 | Navixy: `avl_io_652` (SSF KeyInIgnitionLock) | 0 - No key in lock 1 - Key in lock |
| `diagnostics.occupancy.front_passenger` | P0 | Navixy: `can_front_passenger_presence` (CAN Front Passenger Presence), `avl_io_945` (CSF Front Passenger Present) | 0 - Not present 1 - Present |
| `diagnostics.safety.airbag_state` | P0 | Navixy: `can_airbag_state` | can |
| `diagnostics.steering.eps_state` | P0 | Navixy: `can_eps_state` (EPS State) | EPS State |
| `diagnostics.trailer.axle_lift_active[]` | P0 | Navixy: `can_trailer_axle_lift_active_1` (CAN Trailer Axle Lift Active 1), `can_trailer_axle_lift_active_2` (CAN Trailer Axle Lift Active 2) | CAN Trailer Axle Lift Active 1 |

---

## 12. I/O (Inputs/Outputs)

**Purpose:** Digital and analog input/output states.

### Structure
```json
{
  "io": {
    // Field structure based on mappings below
  }
}
```

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `io.analog.values` | P2 | Navixy: `adc` (analog), `avl_io_6` (Analog Input 2), `avl_io_9` (Analog Input 1) | analog |
| `io.inputs.individual.*` | P2 | Navixy: `avl_io_1` (Digital Input 1), `avl_io_2` (Digital Input 2), `avl_io_3` (Digital Input 3), `avl_io_4` (Pulse Counter Din1) | Logic: 0/1 |
| `io.outputs.bitmask` | P2 | Navixy: `outputs` (Output Status) | Output Status |
| `io.outputs.individual.*` | P2 | Navixy: `avl_io_179` (Digital Output 1), `avl_io_180` (Digital Output 2), `avl_io_380` (Digital output 3) | Logic: 0/1 |

---

## 13. Driver

**Purpose:** Driver identification and related events.

### Structure
```json
{
  "driver": {
    // Field structure based on mappings below
  }
}
```

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `driver.authorization.state` | P2 | Navixy: `avl_io_248` (Immobilizer) | 0 – iButton not connected 1 – iButton connected (Immobilizer) 2 – iButton connected (Authorized Driving) |
| `driver.extended_id` | P2 | Navixy: `avl_io_238` (User ID) | MAC address of NMEA receiver device connected via Bluetooth |
| `driver.hardware_key.ibutton` | P2 | Navixy: `avl_io_78` (iButton), `ibutton` (iButton ID) | iButton ID |
| `driver.hardware_key.rfid` | P2 | Navixy: `avl_io_207` (RFID) | RFID ID |

---

## 14. Device

**Purpose:** Tracking device status, configuration, and security.

### Structure
```json
{
  "device": {
    // Field structure based on mappings below
  }
}
```

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `device.battery.current` | P2 | Navixy: `avl_io_68` (Battery Current), `battery_current` (Battery Current) | Current |
| `device.battery.level` | P2 | Navixy: `avl_io_113` (Battery Level), `battery_level` (Battery Level) | Battery capacity level |
| `device.battery.voltage` | P2 | Navixy: `avl_io_67` (Battery Voltage), `battery_voltage` (Battery Voltage) | Voltage |
| `device.bluetooth.status` | P2 | Navixy: `avl_io_263` (BT Status) | 0 - BT is disabled 1 - BT Enabled, not device connected 2 - Device connected, BTv3 Only 3 - Device connected, BLE onl... |
| `device.power.connected` | P2 | Navixy: `external_power_state` (External Power) | External Power |
| `device.power.external_voltage` | P2 | Navixy: `board_voltage` (External Voltage) | External Voltage |
| `device.power.voltage` | P2 | Navixy: `avl_io_66` (External Voltage) | Voltage |
| `device.sleep_mode` | P2 | Navixy: `avl_io_200` (Sleep Mode) | 0 - No Sleep 1 – GPS Sleep 2 – Deep Sleep 3 – Online Sleep 4 - Ultra Sleep |
| `device.status_bitmap` | P2 | Navixy: `status` (Status) | Status |

---

## 15. Events

**Purpose:** Event-specific data (TBD in separate specification).

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `events.device_unplugged` | P2 | Navixy: `avl_io_252` (Unplug) | 0 – battery present 1 – battery unplugged |
| `events.harsh_acceleration.force` | P2 | Navixy: `acceleration` (Acceleration) | Acceleration |
| `events.harsh_braking.force` | P2 | Navixy: `braking` (Braking) | Braking |
| `events.harsh_cornering.force` | P2 | Navixy: `cornering` (Cornering) | Cornering |
| `events.harsh_cornering.radius` | P2 | Navixy: `cornering_rad` (Cornering Radius) | Cornering Radius |
| `events.idling` | P2 | Navixy: `avl_io_251` (Idling) | 0 – moving 1 – idling |
| `events.towing` | P2 | Navixy: `towing` (Towing) | Towing |
| `events.trip` | P2 | Navixy: `avl_io_250` (Trip) | 0 – trip stop 1 – trip start From 01.00.24 fw version available with BT app new values: 2 – Business Status 3 – Priva... |

---

## 16. Geofence

**Purpose:** Geofence zone information (Device-side).

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `geofence.auto_status` | P2 | Navixy: `avl_io_175` (Auto Geofence) | 0 – target left zone 1 – target entered zone |
| `geofence.device_zones[32].inside` | P2 | Navixy: `avl_io_208` (Geofence zone 33) | 0 – target left zone 1 – target entered zone 2 – over speeding end 3 – over speeding start |
| `geofence.zone_id` | P2 | Navixy: `avl_io_155` (Geofence zone 01) | 0 – target left zone 1 – target entered zone 2 – over speeding end 3 – over speeding start |

---

## 17. Other

**Purpose:** Miscellaneous fields and raw CAN data.

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `other.flags.agricultural_state` | P2 | Navixy: `avl_io_124` (Agricultural Machinery Flags), `avl_io_520` (Agricultural State Flags P4) | Agricultural machinery flags |
| `other.flags.cistern_state` | P2 | Navixy: `avl_io_522` (Cistern State Flags P4) | Cistern state flags protocol 4, more information click here Flags |
| `other.flags.control_state` | P2 | Navixy: `avl_io_123` (Control State Flags), `avl_io_518` (Control State Flags P4) | Control state flags |
| `other.flags.indicator_state` | P2 | Navixy: `avl_io_519` (Indicator State Flags P4) | Indicator state flags protocol 4, more information click here Flags |
| `other.flags.security_state` | P2 | Navixy: `avl_io_132` (Security State Flags), `avl_io_517` (Security State Flags P4) | Security state flags |
| `other.flags.utility_state` | P2 | Navixy: `avl_io_521` (Utility State Flags P4) | Utility state flags protocol 4, more information click here Flags |
| `other.impulse_counters` | P2 | Navixy: `impulse_counter_1` (Impulse Counter 1), `impulse_counter_2` (Impulse Counter 2) | Impulse Counter 1 |
| `other.raw_can` | P0 | Navixy: `raw_can_1` (Raw CAN 1), `raw_can_11` (Raw CAN 11), `raw_can_14` (Raw CAN 14), `raw_can_15` (Raw CAN 15), `raw_can_16` (Raw CAN 16), `raw_can_17` (Raw CAN 17), `raw_can_3` (Raw CAN 3), `raw_can_8` ... | Raw CAN 1 |
| `security.immobilizer.engine_lock_active` | P2 | Navixy: `avl_io_907` (SSF Engine Lock Active) | 0 - Inactive 1 - Active |
| `security.immobilizer.request_lock_engine` | P2 | Navixy: `avl_io_908` (SSF Request To Lock Engine) | 0 - Off 1 - On |

---

## 18. Packet Metadata

**Purpose:** Metadata about the telemetry packet itself.

### Field Sources & Logic

| Fleeti Field | Priority | Source / Logic | Description |
|--------------|----------|----------------|-------------|
| `device.firmware.version` | P2 | Navixy: `avl_io_100` (Program Number) | CAN program / profile ID used by LV-CAN/ALL-CAN adapters to decode vehicle signals. |
| `device.identification.module_id_17b` | P2 | Navixy: `avl_io_388` (Module ID 17B) | Module ID 17 Bytes |
| `device.identification.module_id_8b` | P2 | Navixy: `avl_io_101` (Module ID 8B) | Module ID 8 Bytes |
| `provider.event` | P2 | Navixy: `EVENT` (Event) | Event |
| `provider.event_code` | P2 | Navixy: `event_code` (Event Code) | Event Code |
| `provider.event_subcode` | P2 | Navixy: `sub_event_code` (Sub Event Code) | Sub Event Code |
| `provider.time.device_time` | P2 | Navixy: `msg_time` (metadata) | metadata |
| `provider.time.provider_time` | P2 | Navixy: `server_time` (metadata) | metadata |

---

**Document Version:** 2.0  
**Last Updated:** 2025-01-28  
**Generated From:** Fleeti Field Mapping Expanded CSV (161 fields)  
**Status:** All fields from CSV mapped and documented
