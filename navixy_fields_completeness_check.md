# Navixy Fields Completeness Validation Report

## Summary Statistics

- **Total Navixy fields in CSV:** 338
- **Total Navixy fields found in markdown:** 278
- **Missing fields:** 62
- **Coverage:** 81.66%

---

## Status

⚠️ **62 Navixy field(s) are missing from the schema document.**

---

## Missing Navixy Fields

| Navixy Field Code | Navixy Field Name | Fleeti Field | Telemetry Type |
|-------------------|-------------------|--------------|----------------|
| `avl_io_119` | Axle 2 Load | `diagnostics.axles.weights` | data |
| `avl_io_120` | Axle 3 Load | `diagnostics.axles.weights` | data |
| `avl_io_121` | Axle 4 Load | `diagnostics.axles.weights` | data |
| `avl_io_122` | Axle 5 Load | `diagnostics.axles.weights` | data |
| `avl_io_212` | LLS 4 Fuel Level | `fuel.levels[].value` | data |
| `avl_io_234` | CNG Level | `fuel.levels[].value` | data |
| `avl_io_270` | BLE Fuel Level #1 | `fuel.levels[].value` | data |
| `avl_io_273` | BLE Fuel Level #2 | `fuel.levels[].value` | data |
| `avl_io_385` | Beacon | `nearby_assets[].id` | data |
| `avl_io_466` | BLE 1 Custom #5 | `sensors.custom[]` | data |
| `avl_io_467` | BLE 2 Custom #2 | `sensors.custom[]` | data |
| `avl_io_468` | BLE 2 Custom #3 | `sensors.custom[]` | data |
| `avl_io_469` | BLE 2 Custom #4 | `sensors.custom[]` | data |
| `avl_io_470` | BLE 2 Custom #5 | `sensors.custom[]` | data |
| `avl_io_471` | BLE 3 Custom #2 | `sensors.custom[]` | data |
| `avl_io_472` | BLE 3 Custom #3 | `sensors.custom[]` | data |
| `avl_io_473` | BLE 3 Custom #4 | `sensors.custom[]` | data |
| `avl_io_654` | SSF Front Left Door Open | `diagnostics.body.doors.*` | data |
| `avl_io_655` | SSF Front Right Door Open | `diagnostics.body.doors.*` | data |
| `avl_io_656` | SSF Rear Left Door Open | `diagnostics.body.doors.*` | data |
| `avl_io_657` | SSF Rear Right Door Open | `diagnostics.body.doors.*` | data |
| `avl_io_658` | SSF Trunk Door Open | `diagnostics.body.doors.*` | data |
| `avl_io_72` | Dallas Temperature 1 | `sensors.temperature` | data |
| `avl_io_73` | Dallas Temperature 2 | `sensors.temperature` | data |
| `avl_io_84` | Fuel Level | `fuel.levels[].value` | data |
| `avl_io_89` | Fuel level | `fuel.levels[].value` | data |
| `avl_io_90` | Door Status | `diagnostics.body.doors.*` | data |
| `avl_io_913` | SSF Engine Cover Open | `diagnostics.body.doors.*` | data |
| `avl_io_935` | CSF Light Signal | `diagnostics.body.lights.*` | data |
| `avl_io_940` | CSF Driver's Seatbelt Fastened | `diagnostics.body.belts.*` | data |
| `avl_io_941` | CSF Front Driver's Seatbelt Fastened | `diagnostics.body.belts.*` | data |
| `avl_io_942` | CSF Left Driver's Seatbelt Fastened | `diagnostics.body.belts.*` | data |
| `avl_io_943` | CSF Right Driver's Seatbelt Fastened | `diagnostics.body.belts.*` | data |
| `avl_io_944` | CSF Centre Driver's Seatbelt Fastened | `diagnostics.body.belts.*` | data |
| `ble_beacon_id` | BLE Beacon ID | `nearby_assets[].id` | data |
| `ble_lls_level_1` | fuel | `fuel.levels[].value` | data |
| `ble_lls_level_2` | fuel | `fuel.levels[].value` | data |
| `ble_temp_sensor_1` | BLE Temp 1 | `sensors.temperature` | data |
| `ble_temp_sensor_2` | BLE Temp 2 | `sensors.temperature` | data |
| `ble_temp_sensor_3` | BLE Temp 3 | `sensors.temperature` | data |
| `ble_temp_sensor_4` | BLE Temp 4 | `sensors.temperature` | data |
| `can_light_signal` | CAN Light Signal | `diagnostics.body.lights.*` | data |
| `can_lights_failure` | CAN Lights Failure | `diagnostics.body.lights.*` | data |
| `can_parking_lights` | CAN Parking Lights | `diagnostics.body.lights.*` | data |
| `can_rear_fog_lights` | CAN Rear Fog Lights | `diagnostics.body.lights.*` | data |
| `can_seat_belt_driver_state` | can | `diagnostics.body.belts.*` | data |
| `can_seat_belt_passenger_state` | CAN Passenger Seat Belt State | `diagnostics.body.belts.*` | data |
| `can_trunk_state` | can | `diagnostics.body.doors.*` | data |
| `ext_temp_sensor_1` | External Temp 1 | `sensors.temperature` | data |
| `ext_temp_sensor_2` | External Temp 2 | `sensors.temperature` | data |
| `ext_temp_sensor_3` | External Temp 3 | `sensors.temperature` | data |
| `fuel_level` | Fuel Level | `fuel.levels[].value` | data |
| `hw_mileage` | Hardware Mileage | `counters.odometer` | data |
| `lls_level_1` | LLS Level 1 | `fuel.levels[].value` | data |
| `lls_level_2` | LLS Level 2 | `fuel.levels[].value` | data |
| `lls_level_3` | LLS Level 3 | `fuel.levels[].value` | data |
| `lls_level_4` | LLS Level 4 | `fuel.levels[].value` | data |
| `lls_temperature_1` | LLS Temperature 1 | `sensors.temperature` | data |
| `lls_temperature_2` | LLS Temperature 2 | `sensors.temperature` | data |
| `raw_can_9` | Raw CAN 9 | `other.raw_can` | data |
| `raw_mileage` | Raw Mileage | `counters.odometer` | data |
| `temp_sensor` | Temperature Sensor | `sensors.temperature` | data |

---

## Recommendations

1. Review each missing field to determine if it should be added to the schema document.
2. Add missing fields to the appropriate section in `Telemetry_Schema_Analysis_Updated.md`.
3. Ensure the field is placed in the semantically correct section.
4. Include priority, source logic, and description for each field.

---

## Fields in Markdown but Not in CSV (Reference Only)

The following Navixy fields appear in the markdown but are not in the CSV:

- `ileage`
- `onsumed`

*Note: These may be legacy fields, computed fields, or fields from other sources.*

---

**Report Generated:** validate_navixy_completeness.py
