# derive_sensors_environment (pseudo)

Purpose
- Build `sensors.environment[]` from asset accessory sensor metadata + current telemetry.
- Group temperature, humidity, and battery readings that belong to the same physical sensor/accessory.
- Enrich provider field names with raw `avl_io_*` equivalents using a correspondence matrix.

Key inputs
- `asset.accessories[].sensors[]` metadata (type, provider_field, id, label/name, position).
- Telemetry packet with provider fields (raw and processed).
- Navixy API for sensor config when provider_field is missing.

Correspondence matrix (examples)
- Temperature (LLS): lls_temperature_1 <-> avl_io_202; lls_temperature_2 <-> avl_io_204
- Temperature (external): ext_temp_sensor_1..4 <-> avl_io_72..75
- Temperature (BLE): ble_temp_sensor_1..4 <-> avl_io_25..28
- Humidity (BLE): ble_humidity_1..4 <-> avl_io_86/104/106/108
- Battery (BLE): ble_battery_level_1..4 <-> avl_io_29/20/22/23
- Some generic humidity fields have no verified correspondence

Unit and validation rules
- Temperature (raw avl_io): valid range -120..120, exclude -128 (sensor error)
  - Divide by 10 for raw avl_io values, except avl_io_202 and avl_io_204 (already scaled)
- Temperature (processed fields): accept non-null
- Humidity (raw avl_io): valid 0..1000, exclude 65535/65534/65533; divide by 10
- Humidity (processed fields): valid 0..100
- Battery (raw or processed): valid 0..100, exclude -128

High-level algorithm
1) Load asset accessories: `asset.accessories[]`.
2) For each accessory, iterate `accessory.sensors[]` entries.
3) For each sensor_meta of type temperature/humidity/battery:
   - Build provider_fields list from metadata.
   - If empty, call Navixy API `tracker/sensor/list` and match by sensor id.
   - Enrich provider_fields using correspondence matrix (include both processed and avl_io names).
   - Read the first valid value by type using the validation/unit rules.
4) Create one environment entry per accessory, and fill temperature/humidity/battery if present.
5) Only add the entry if at least one of temperature/humidity/battery is present.

Detailed pseudocode

FUNCTION derive_sensors_environment(asset_id, telemetry_packet):
    result = []
    accessories = asset_service.get_accessories(asset_id)

    FOR each accessory IN accessories:
        IF accessory.sensors is empty: CONTINUE

        entry = {
            id, name, label, position (optional),
            temperature: null, humidity: null, battery: null,
            last_updated_at: telemetry_packet.last_updated_at
        }

        FOR each sensor_meta IN accessory.sensors:
            IF sensor_meta.type not in [temperature, humidity, battery]: CONTINUE

            provider_fields = sensor_meta.provider_field
            IF provider_fields is empty:
                navixy_sensors = navixy_api.get_tracker_sensor_list(tracker_id)
                match = find navixy_sensors by sensor_meta.id
                IF match.input_name exists:
                    provider_fields = [match.input_name]

            provider_fields = enrich_with_correspondences(provider_fields)

            IF sensor_meta.type == temperature:
                entry.temperature = first valid temperature from provider_fields
            IF sensor_meta.type == humidity:
                entry.humidity = first valid humidity from provider_fields
            IF sensor_meta.type == battery:
                entry.battery = first valid battery from provider_fields

        IF entry has any measurement:
            result.append(entry)

    RETURN result

Helper: enrich_with_correspondences(provider_fields)
- Add each field plus any mapped correspondences from the matrix
- Preserve order, avoid duplicates

Helper: first valid temperature
- If field is avl_io:
  - reject -128 and values outside -120..120
  - divide by 10 except avl_io_202/avl_io_204
- If field is processed:
  - accept non-null

Helper: first valid humidity
- If field is avl_io:
  - reject 65535/65534/65533
  - accept 0..1000, divide by 10
- If field is processed:
  - accept 0..100

Helper: first valid battery
- Accept 0..100, reject -128
