# derive_fuel_levels (pseudo)

Purpose
- Build `fuel.levels[]` (or `fuel[]`) array from asset accessory fuel sensor metadata + telemetry.
- Support multiple fuel tanks/sensors per asset (array output).
- Prefer raw `avl_io_*` over processed fields when they are correspondences.

Provider field correspondence groups (paired)
- avl_io_89 <-> can_fuel_1 (percent)
- avl_io_84 <-> can_fuel_litres (liters)
- avl_io_390 (OBD OEM fuel liters, divide by 10)
- avl_io_234 (CNG level, percent)
- avl_io_270 <-> ble_lls_level_1 (kvants)
- avl_io_273 <-> ble_lls_level_2 (kvants)
- avl_io_201 <-> lls_level_1 (kvants)
- avl_io_203 <-> lls_level_2 (kvants)
- avl_io_210 <-> lls_level_3 (kvants)
- avl_io_212 <-> lls_level_4 (kvants)

Units and conversion rules
- avl_io_390: liters, divide by 10.
- avl_io_234: percent.
- avl_io_89 / can_fuel_1: percent.
- LLS and BLE LLS fields are in kvants and require a calibration table
  to convert kvants -> liters.
- If a value is in percent and tank capacity is known, convert to liters.
  Otherwise keep percent.

Calibration table requirement (LLS / BLE LLS)
- Calibration tables exist in Navixy; we should store them in our system.
- If accessory/sensor has no stored calibration table, run a sync script
  to fetch and cache it (do not call Navixy on every packet).

High-level algorithm
1) Load asset accessories and identify fuel-related sensors.
2) For each fuel sensor:
   - Get provider_fields from metadata (provider_field array).
   - If missing, fetch from Navixy sensor list by sensor id.
   - Enrich provider_fields with correspondences (raw avl_io preferred).
   - Read first valid value in priority order.
   - Convert units as needed:
     - if kvants -> liters using calibration table
     - if percent -> liters using tank capacity (if available)
     - else keep original unit
   - Add a fuel entry with name/label, value, unit, last_updated_at.
3) Return array (can contain multiple tanks).

Detailed pseudocode

FUNCTION derive_fuel_levels(asset_id, telemetry_packet):
    result = []
    accessories = asset_service.get_accessories(asset_id)

    FOR each accessory IN accessories:
        FOR each sensor_meta IN accessory.sensors:
            IF sensor_meta is not a fuel sensor: CONTINUE

            provider_fields = sensor_meta.provider_field
            IF provider_fields is empty:
                navixy_sensors = navixy_api.get_tracker_sensor_list(tracker_id)
                match = find navixy_sensors by sensor_meta.id
                IF match.input_name exists:
                    provider_fields = [match.input_name]

            provider_fields = prioritize_with_correspondences(provider_fields)

            raw_value, raw_unit = first_valid_fuel_value(provider_fields, telemetry_packet)
            IF raw_value is null: CONTINUE

            IF raw_unit == "kvants":
                calibration = get_or_init_calibration_table(asset_id, sensor_meta.id)
                liters_value = convert_kvants_to_liters(raw_value, calibration)
                value = liters_value
                unit = "liters"
            ELSE IF raw_unit == "%":
                capacity = get_tank_capacity(asset_id, sensor_meta.id)
                IF capacity exists:
                    value = (raw_value / 100) * capacity
                    unit = "liters"
                ELSE:
                    value = raw_value
                    unit = "%"
            ELSE:
                value = raw_value
                unit = raw_unit

            result.append({
                name: accessory.name or sensor_meta.label,
                value: value,
                unit: unit,
                last_updated_at: telemetry_packet.last_updated_at
            })

    RETURN result

Helper: prioritize_with_correspondences(provider_fields)
- For each field:
  - if an avl_io correspondence exists, place avl_io first
  - then place processed field
  - keep order and remove duplicates

Helper: first_valid_fuel_value
- Look up fields in priority order until a non-null, valid value is found
- Return (value, unit) based on field type rules above

Helper: get_or_init_calibration_table
- Check if calibration table exists in local system
- If not, run a sync script that fetches from Navixy and stores it
