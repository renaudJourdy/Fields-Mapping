# derive_sensors_magnet (pseudo)

Purpose
- Build `sensors.magnet[]` from asset accessory sensor metadata + current telemetry.
- Prefer raw `avl_io_*` values over BLE `ble_magnet_sensor_*` values.
- Use Navixy sensor config API if metadata has no provider fields.

Correspondence matrix (priority raw over BLE)
- ble_magnet_sensor_1 <-> avl_io_10808
- ble_magnet_sensor_2 <-> avl_io_10809
- ble_magnet_sensor_3 <-> avl_io_10810
- ble_magnet_sensor_4 <-> avl_io_10811

Valid values
- State is boolean: 0 or 1 only. Ignore all other values.
- UI/localization: store numeric state (0/1). Display labels are localized in the UI
  (e.g., Open/Closed vs Ouvert/Ferme).

High-level algorithm
1) Load asset accessories: `asset.accessories[]`.
2) For each accessory, examine `accessory.sensors[]` entries that are magnet sensors.
3) For each magnet sensor:
   - Determine provider_fields list from metadata.
   - If empty, call Navixy API to fetch tracker sensor list and match by sensor id.
   - Enrich the provider_fields using the correspondence matrix.
   - Build a priority list that always tries `avl_io_*` first, then BLE names.
   - Read the first valid state (0 or 1) from the telemetry packet.
   - If a valid state is found, create a sensor object with:
     - id, name/label, position (if available)
     - state (0/1)
     - last_updated_at = telemetry packet last_updated_at
     - last_changed_at =
         - last_updated_at if no previous stored value exists
         - last_updated_at if previous stored value != current state
         - previous last_changed_at if state unchanged
4) Return array of sensor objects. Only include sensors with a valid state.

Detailed pseudocode

FUNCTION derive_sensors_magnet(asset_id, telemetry_packet):
    result = []
    accessories = asset_service.get_accessories(asset_id)

    FOR each accessory IN accessories:
        IF accessory.sensors is empty: CONTINUE

        FOR each sensor_meta IN accessory.sensors:
            IF sensor_meta.type is not magnet: CONTINUE

            provider_fields = sensor_meta.provider_field
            IF provider_fields is empty:
                navixy_sensors = navixy_api.get_tracker_sensor_list(tracker_id)
                match = find navixy_sensors by sensor_meta.id
                IF match.input_name exists:
                    provider_fields = [match.input_name]

            provider_fields = prioritize_with_correspondences(provider_fields)

            state = first value in telemetry_packet[provider_fields] that is 0 or 1
            IF state is null: CONTINUE

            previous = get_current_stored_magnet_entry(asset_id, sensor_meta.id)

            last_changed_at =
                IF previous is null: telemetry_packet.last_updated_at
                ELSE IF previous.state != state: telemetry_packet.last_updated_at
                ELSE previous.last_changed_at

            result.append({
                id: accessory.id,
                name: accessory.name,
                label: accessory.label,
                position: sensor_meta.position (if present),
                state: state,
                last_updated_at: telemetry_packet.last_updated_at,
                last_changed_at: last_changed_at
            })

    RETURN result

Helper: prioritize_with_correspondences(provider_fields)
- For each field in provider_fields:
  - If it has an avl_io correspondence, put avl_io first
  - Then put the BLE field
  - Ensure unique order, no duplicates

Helper: get_current_stored_magnet_entry(asset_id, sensor_id)
- Read current stored telemetry for the asset (implementation depends on backend)
- Return the existing magnet entry for this sensor id, or null
