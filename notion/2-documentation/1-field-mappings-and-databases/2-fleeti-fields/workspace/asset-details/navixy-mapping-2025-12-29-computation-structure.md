# Computation Structure JSON for navixy-mapping-2025-12-29.yaml

This document contains the computation structure JSON for all fields in the YAML mapping file. These JSON structures are designed to generate the exact same YAML configuration when used with the generation script.

## engine_hours_value

**Field Path:** `counters.engine_hours.value`

**Computation Approach:** Prioritized mapping from multiple Navixy provider fields. CAN Engine Hours (can_engine_hours) is preferred when available as it provides absolute engine hours directly. Engine Worktime (avl_io_102) is a relative counter that starts from zero and requires addition of asset.installation.initial_engine_hours offset. Priorities 3 and 4 use add_installation_offset_engine_hours function to handle relative counters (avl_io_103, can_engine_hours_relative). Ignition On Counter (avl_io_449) is the last priority fallback. Unit conversion: Sources report in different units (seconds, minutes, hours) - backend applies conversion to hours as needed.

Pseudo code for add_installation_offset_engine_hours:
```
relative_value = get_provider_field_value(provider_field_name)
initial_offset = asset_service.get_installation_metadata('initial_engine_hours') || 0
// Convert relative value to hours if needed (based on source unit)
absolute_hours = convert_to_hours(relative_value) + initial_offset
return absolute_hours
```

```json
{
  "type": "prioritized",
  "sources": [
    {
      "priority": 1,
      "field": "avl_io_102",
      "path": "params.avl_io_102",
      "unit": "minutes"
    },
    {
      "priority": 2,
      "field": "can_engine_hours",
      "path": "params.can_engine_hours",
      "unit": "hours"
    },
    {
      "priority": 3,
      "type": "calculated",
      "calculation_type": "function_reference",
      "function": "add_installation_offset_engine_hours",
      "parameters": {
        "provider": {
          "navixy": "avl_io_103"
        }
      },
      "unit": "minutes"
    },
    {
      "priority": 4,
      "type": "calculated",
      "calculation_type": "function_reference",
      "function": "add_installation_offset_engine_hours",
      "parameters": {
        "provider": {
          "navixy": "can_engine_hours_relative"
        }
      },
      "unit": "hours"
    },
    {
      "priority": 5,
      "field": "avl_io_449",
      "path": "params.avl_io_449",
      "unit": "seconds"
    }
  ]
}
```

## engine_hours_last_updated_at

**Field Path:** `counters.engine_hours.last_updated_at`

**Computation Approach:** Calculated: derive from engine_hours_value and last_updated_at using derive_engine_hours_last_updated_at function. Tracks data freshness (when value was last received), not when the value changed.

Pseudo code:
```
if (engine_hours_value !== null && engine_hours_value !== undefined) {
  engine_hours_last_updated_at = last_updated_at  // Use timestamp from telemetry packet
} else {
  engine_hours_last_updated_at = previous_engine_hours_last_updated_at  // Keep unchanged if no value received
}
```

```json
{
  "type": "calculated",
  "calculation_type": "function_reference",
  "function": "derive_engine_hours_last_updated_at",
  "parameters": {
    "fleeti": [
      "engine_hours_value",
      "last_updated_at"
    ]
  }
}
```

## odometer_value

**Field Path:** `counters.odometer.value`

**Computation Approach:** Prioritized mapping from multiple Navixy provider fields. CAN Mileage (can_mileage) is preferred when available as it provides absolute odometer directly. Priorities 5 and 6 use add_installation_offset_odometer function to handle relative counters (avl_io_105, can_mileage_relative) which require addition of asset.installation.initial_odometer offset. Unit conversion: Sources reporting in meters (priorities 1, 3, 5, 7) are converted to kilometers (divide by 1000). This field stores raw counter values; installation offset is applied separately if needed.

Pseudo code for add_installation_offset_odometer:
```
relative_value = get_provider_field_value(provider_field_name)
initial_offset = asset_service.get_installation_metadata('initial_odometer') || 0
// Convert relative value to km if needed (based on source unit)
absolute_km = convert_to_km(relative_value) + initial_offset
return absolute_km
```

```json
{
  "type": "prioritized",
  "sources": [
    {
      "priority": 1,
      "field": "avl_io_87",
      "path": "params.avl_io_87",
      "unit": "meters"
    },
    {
      "priority": 2,
      "field": "can_mileage",
      "path": "params.can_mileage",
      "unit": "km"
    },
    {
      "priority": 3,
      "field": "avl_io_389",
      "path": "params.avl_io_389",
      "unit": "meters"
    },
    {
      "priority": 4,
      "field": "obd_custom_odometer",
      "path": "params.obd_custom_odometer",
      "unit": "km"
    },
    {
      "priority": 5,
      "type": "calculated",
      "calculation_type": "function_reference",
      "function": "add_installation_offset_odometer",
      "parameters": {
        "provider": {
          "navixy": "avl_io_105"
        }
      },
      "unit": "meters"
    },
    {
      "priority": 6,
      "type": "calculated",
      "calculation_type": "function_reference",
      "function": "add_installation_offset_odometer",
      "parameters": {
        "provider": {
          "navixy": "can_mileage_relative"
        }
      },
      "unit": "km"
    },
    {
      "priority": 7,
      "field": "avl_io_16",
      "path": "params.avl_io_16",
      "unit": "meters"
    },
    {
      "priority": 8,
      "field": "hw_mileage",
      "path": "params.hw_mileage",
      "unit": "km"
    }
  ]
}
```

## odometer_last_updated_at

**Field Path:** `counters.odometer.last_updated_at`

**Computation Approach:** Calculated: derive from odometer_value and last_updated_at using derive_odometer_last_updated_at function. Tracks data freshness (when value was last received), not when the value changed.

Pseudo code:
```
if (odometer_value !== null && odometer_value !== undefined) {
  odometer_last_updated_at = last_updated_at  // Use timestamp from telemetry packet
} else {
  odometer_last_updated_at = previous_odometer_last_updated_at  // Keep unchanged if no value received
}
```

```json
{
  "type": "calculated",
  "calculation_type": "function_reference",
  "function": "derive_odometer_last_updated_at",
  "parameters": {
    "fleeti": [
      "odometer_value",
      "last_updated_at"
    ]
  }
}
```

## magnet

**Field Path:** `sensors.magnet[]`

**Computation Approach:** Calculated: derive from asset.accessories[].sensors[] metadata and telemetry provider fields using derive_sensors_magnet function. Builds `sensors.magnet[]` with one entry per physical magnet sensor (e.g., multiple doors on a single asset). Matches provider fields to sensors via asset metadata, applies prioritized mapping with validation, and enriches fields with correspondences. Prioritize raw `avl_io_*` values over BLE `ble_magnet_sensor_*` values (use BLE only when raw is empty). If `provider_field` metadata is missing, fetch sensor configuration via Navixy API and map by sensor ID. Returns array of sensor objects (id, label, position, state, last_updated_at, last_changed_at). State values: 0 = no magnetic field detected, 1 = magnetic field detected. Store numeric state (0/1); UI localizes labels (e.g., Open/Closed vs Ouvert/Fermé).

**Implementation Reference:** See Notion documentation for complete function implementation details. Function location: `notion/2-documentation/1-specifications/1-databases/2-fleeti-fields/workspace/asset-details/functions/derive_sensors_magnet.js`

```json
{
  "type": "calculated",
  "calculation_type": "function_reference",
  "function": "derive_sensors_magnet",
  "parameters": {
    "fleeti": [],
    "provider": {
      "navixy": [
        "ble_magnet_sensor_1",
        "avl_io_10808",
        "ble_magnet_sensor_2",
        "avl_io_10809",
        "ble_magnet_sensor_3",
        "avl_io_10810",
        "ble_magnet_sensor_4",
        "avl_io_10811"
      ]
    }
  }
}
```

## driver_name

**Field Path:** `driver.driver_name`

**Computation Approach:** Calculated: derive from driver_key using derive_driver_name function. Looks up hardware key in Fleeti driver catalog with state preservation logic. The hardware key comes from Navixy provider fields (see driver_key field for source priority). Backend determines key type (iButton vs RFID) based on device model and signal characteristics.

Pseudo code:
```
if (driver_key === null || driver_key === undefined || driver_key === "") {
  driver_name = previous_driver_name  // Keep last known state, do not update
} else if (driver_key !== previous_driver_key) {
  // New driver_key received, lookup in catalog
  driver = driver_catalog.lookup(driver_key)
  if (driver !== null) {
    driver_name = driver.name  // Update with name from catalog
  } else {
    driver_name = null  // Unknown driver, hardware_key will still be displayed
  }
} else {
  driver_name = previous_driver_name  // driver_key unchanged, keep current state
}
```

```json
{
  "type": "calculated",
  "calculation_type": "function_reference",
  "function": "derive_driver_name",
  "parameters": {
    "fleeti": [
      "driver_key"
    ]
  }
}
```

## driver_key

**Field Path:** `driver.driver_key`

**Computation Approach:** Prioritized driver key from Navixy AVL I/O (iButton preferred), with `ibutton` as fallback and RFID last. Hardware key is a hex string (iButton or RFID). Backend infers key type from device model/signal. Used to resolve `driver_name` via Fleeti driver catalog.

```json
{
  "type": "prioritized",
  "sources": [
    {
      "priority": 1,
      "field": "avl_io_78",
      "path": "params.avl_io_78",
      "unit": "none"
    },
    {
      "priority": 2,
      "field": "ibutton",
      "path": "ibutton",
      "unit": "none"
    },
    {
      "priority": 3,
      "field": "avl_io_207",
      "path": "params.avl_io_207",
      "unit": "none"
    }
  ]
}
```

## dtc_count

**Field Path:** `diagnostics.health.dtc.count`

**Computation Approach:** Prioritized mapping from Navixy provider fields. Number of DTC (avl_io_30) is priority 1, OBD DTC Count (obd_dtc_number) is priority 2. Integer value representing the number of Diagnostic Trouble Codes (DTCs) present.

```json
{
  "type": "prioritized",
  "sources": [
    {
      "priority": 1,
      "field": "avl_io_30",
      "path": "params.avl_io_30",
      "unit": "none"
    },
    {
      "priority": 2,
      "field": "obd_dtc_number",
      "path": "params.obd_dtc_number",
      "unit": "none"
    }
  ]
}
```

## dtc_status

**Field Path:** `diagnostics.health.dtc.status`

**Computation Approach:** Prioritized mapping from Navixy provider fields. CAN MIL Status (avl_io_519) is priority 1, OBD MIL Status (obd_mil_status) is priority 2. Malfunction Indicator Lamp (MIL) status read from CAN. Values: 0 = MIL off (no faults), 1 = MIL on (fault detected). Boolean value.

```json
{
  "type": "prioritized",
  "sources": [
    {
      "priority": 1,
      "field": "avl_io_519",
      "path": "params.avl_io_519",
      "unit": "none"
    },
    {
      "priority": 2,
      "field": "obd_mil_status",
      "path": "params.obd_mil_status",
      "unit": "none"
    }
  ]
}
```

## dtc_codes

**Field Path:** `diagnostics.health.dtc.codes[]`

**Computation Approach:** Calculated: derive from provider fields avl_io_281 and avl_io_282 using derive_dtc_codes_combined function. Both fields are complementary sources that need to be combined into a single array.

Pseudo code:
```
dtc_codes_1 = telemetry_packet.params.avl_io_281  // CAN DTC Array
dtc_codes_2 = telemetry_packet.params.avl_io_282  // CAN DTC Array (complementary)
dtc_codes = []
if (dtc_codes_1 !== null && Array.isArray(dtc_codes_1)) {
  dtc_codes = dtc_codes.concat(dtc_codes_1)
}
if (dtc_codes_2 !== null && Array.isArray(dtc_codes_2)) {
  dtc_codes = dtc_codes.concat(dtc_codes_2)
}
return dtc_codes  // Combined array of DTC codes
```

```json
{
  "type": "calculated",
  "calculation_type": "function_reference",
  "function": "derive_dtc_codes_combined",
  "parameters": {
    "provider": {
      "navixy": [
        "avl_io_281",
        "avl_io_282"
      ]
    }
  }
}
```

## remaining_range

**Field Path:** `power.ev.remaining_range`

**Computation Approach:** Direct mapping from Navixy: avl_io_304 (path: params.avl_io_304). Remaining range on battery for EV/hybrid vehicles, measured in kilometers. Only populated when the vehicle exposes this signal (EV/hybrid vehicles). Unit conversion: Provider field reports in meters, converted to kilometers.

```json
{
  "type": "direct",
  "sources": [
    {
      "field": "avl_io_304",
      "path": "params.avl_io_304",
      "unit": "meters"
    }
  ]
}
```

## fuel_tank_level_value

**Field Path:** `fuel.tank_level.value`

**Computation Approach:** Calculated: derive from asset.accessories[].sensors[] metadata and telemetry provider fields using derive_fuel_levels function. Returns an array to support multiple tanks/sensors per asset. Provider fields are grouped by correspondences (raw `avl_io_*` preferred over processed names); values are normalized by unit rules: `avl_io_390` divide by 10 (liters), `avl_io_234` percent, CAN/OBD sources in liters or percent, and LLS/BLE LLS in kvants. Kvants require a calibration table (stored locally; if missing, initialize by fetching from Navixy and caching). Percent values are converted to liters when tank capacity is known; otherwise kept as percent. Applies validation and selects the first valid value per sensor.

**Implementation Reference:** See Notion documentation for complete function implementation details. Function location: `notion/2-documentation/1-specifications/1-databases/2-fleeti-fields/workspace/asset-details/functions/derive_fuel_levels.js`

```json
{
  "type": "calculated",
  "calculation_type": "function_reference",
  "function": "derive_fuel_levels",
  "parameters": {
    "fleeti": [],
    "provider": {
      "navixy": [
        "avl_io_89",
        "can_fuel_1",
        "avl_io_84",
        "can_fuel_litres",
        "avl_io_390",
        "obd_custom_fuel_litres",
        "avl_io_234",
        "avl_io_270",
        "ble_lls_level_1",
        "avl_io_273",
        "ble_lls_level_2",
        "avl_io_201",
        "lls_level_1",
        "avl_io_203",
        "lls_level_2",
        "avl_io_210",
        "lls_level_3",
        "avl_io_212",
        "lls_level_4"
      ]
    }
  }
}
```

## fuel_tank_level_last_updated_at

**Field Path:** `fuel.tank_level.last_updated_at`

**Computation Approach:** Calculated: derive from fuel_tank_level_value and last_updated_at using derive_fuel_tank_level_last_updated_at function. Tracks data freshness (when value was last received), not when the value changed.

Pseudo code:
```
if (fuel_tank_level_value !== null && fuel_tank_level_value !== undefined) {
  fuel_tank_level_last_updated_at = last_updated_at  // Use timestamp from telemetry packet
} else {
  fuel_tank_level_last_updated_at = previous_fuel_tank_level_last_updated_at  // Keep unchanged if no value received
}
```

```json
{
  "type": "calculated",
  "calculation_type": "function_reference",
  "function": "derive_fuel_tank_level_last_updated_at",
  "parameters": {
    "fleeti": [
      "fuel_tank_level_value",
      "last_updated_at"
    ]
  }
}
```

## fuel_consumption_cumulative

**Field Path:** `fuel.consumption.cumulative`

**Computation Approach:** Prioritized mapping from multiple Navixy provider fields. Fuel Consumed (avl_io_83) is preferred but requires unit conversion from deciliters to liters using divide_by_10 function. CAN Consumption (can_consumption) is the same source as avl_io_83, already in liters. Total fuel consumed (cumulative value), measured in liters.

Pseudo code for divide_by_10:
```
value = get_provider_field_value('avl_io_83')
return value / 10  // Convert deciliters to liters
```

```json
{
  "type": "prioritized",
  "sources": [
    {
      "priority": 1,
      "type": "calculated",
      "calculation_type": "function_reference",
      "function": "divide_by_10",
      "parameters": {
        "provider": {
          "navixy": "avl_io_83"
        }
      }
    },
    {
      "priority": 2,
      "field": "can_consumption",
      "path": "params.can_consumption",
      "unit": "liters"
    },
    {
      "priority": 3,
      "field": "avl_io_107",
      "path": "params.avl_io_107",
      "unit": "liters"
    },
    {
      "priority": 4,
      "field": "can_consumption_relative",
      "path": "params.can_consumption_relative",
      "unit": "liters"
    }
  ]
}
```

## ongoing_trip_started_at

**Field Path:** `trip.ongoing_trip.started_at`

**Computation Approach:** Calculated: derive from statuses_transit_code and last_updated_at using derive_ongoing_trip_started_at function. Part of ongoing trip information computed from Fleeti status fields (no provider fields used). Trip starts when transit status transitions from parked to in_transit. Uses Fleeti's own logic based on transit status family changes.

Pseudo code:
```
previous_transit_code = getPreviousTransitStatus()
if (previous_transit_code === "parked" && statuses_transit_code === "in_transit") {
  // Trip started: transition from parked to in_transit
  ongoing_trip_started_at = last_updated_at  // Set to current timestamp
} else if (statuses_transit_code === "in_transit") {
  // Trip ongoing, keep existing start time
  ongoing_trip_started_at = previous_ongoing_trip_started_at  // Keep unchanged
} else {
  // Not in transit, no trip ongoing
  ongoing_trip_started_at = null
}
```

```json
{
  "type": "calculated",
  "calculation_type": "function_reference",
  "function": "derive_ongoing_trip_started_at",
  "parameters": {
    "fleeti": [
      "statuses_transit_code",
      "last_updated_at"
    ]
  }
}
```

## ongoing_trip_mileage

**Field Path:** `trip.ongoing_trip.mileage`

**Computation Approach:** Calculated: derive from ongoing_trip_started_at and odometer_value using derive_ongoing_trip_mileage function. Calculates distance traveled during the ongoing trip (from trip start to current position), measured in kilometers. Updates as trip progresses.

Pseudo code:
```
if (ongoing_trip_started_at === null) {
  return null  // No trip ongoing
}
trip_start_odometer = getOdometerAtTime(ongoing_trip_started_at)
if (trip_start_odometer !== null && odometer_value !== null) {
  ongoing_trip_mileage = odometer_value - trip_start_odometer  // Use odometer difference
} else {
  ongoing_trip_mileage=null;
}
```

```json
{
  "type": "calculated",
  "calculation_type": "function_reference",
  "function": "derive_ongoing_trip_mileage",
  "parameters": {
    "fleeti": [
      "ongoing_trip_started_at",
      "odometer_value"
    ]
  }
}
```

## ongoing_trip_waypoints

**Field Path:** `trip.ongoing_trip.waypoints`

**Computation Approach:** Calculated: derive from ongoing_trip_started_at, location_latitude, and location_longitude using derive_ongoing_trip_waypoints function. Array of latitude/longitude coordinates representing the trip path for map display. Backend accumulates waypoints from trip start to current time.

Pseudo code:
```
if (ongoing_trip_started_at === null) {
  return []  // No trip ongoing, return empty array
}
// Backend accumulates waypoints from trip start
waypoints = getAccumulatedWaypoints(asset_id, ongoing_trip_started_at)
// Add current location if it's different from last waypoint (with threshold to filter GPS noise)
current_waypoint = { latitude: location_latitude, longitude: location_longitude }
last_waypoint = waypoints[waypoints.length - 1]
if (last_waypoint === undefined || calculateDistance(current_waypoint, last_waypoint) > threshold) {
  waypoints.push(current_waypoint)  // Add current location to waypoints
}
return waypoints
```

```json
{
  "type": "calculated",
  "calculation_type": "function_reference",
  "function": "derive_ongoing_trip_waypoints",
  "parameters": {
    "fleeti": [
      "ongoing_trip_started_at",
      "location_latitude",
      "location_longitude"
    ]
  }
}
```