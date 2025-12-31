/**
 * ============================================================================
 * PROVIDER FIELD CORRESPONDENCE MATRIX
 * ============================================================================
 * Maps processed Navixy BLE magnet fields to their raw avl_io equivalents
 * and vice versa. Raw avl_io fields are always preferred over BLE fields.
 * ============================================================================
 */
const PROVIDER_FIELD_CORRESPONDENCE = {
    'ble_magnet_sensor_1': ['avl_io_10808'], 'avl_io_10808': ['ble_magnet_sensor_1'],
    'ble_magnet_sensor_2': ['avl_io_10809'], 'avl_io_10809': ['ble_magnet_sensor_2'],
    'ble_magnet_sensor_3': ['avl_io_10810'], 'avl_io_10810': ['ble_magnet_sensor_3'],
    'ble_magnet_sensor_4': ['avl_io_10811'], 'avl_io_10811': ['ble_magnet_sensor_4']
};

/**
 * ============================================================================
 * FUNCTION: derive_sensors_magnet
 * ============================================================================
 * Builds sensors.magnet[] array by matching provider fields to sensors
 * based on asset.accessories[].sensors[] metadata.
 *
 * Function Reference: derive_sensors_magnet
 * Implementation Location: This file
 * Dependencies: asset.accessories[].sensors[] metadata
 * ============================================================================
 */
// NOTE: This file is intentionally illustrative (not plug-and-play).
// Integrators should wire actual asset/telemetry accessors used in production.
function derive_sensors_magnet(asset_id, telemetry_packet) {
    const sensors_magnet = [];
    const accessories = asset_service.get_accessories(asset_id) || [];
    const asset = asset_service.get_asset ? asset_service.get_asset(asset_id) : null;

    for (const accessory of accessories) {
        if (accessory.sensors && accessory.sensors.length > 0) {
            const sensor_entry = {
                id: accessory.id,
                name: accessory.name,
                label: accessory.label,
                position: null,
                state: null,
                last_updated_at: telemetry_packet.last_updated_at,
                last_changed_at: null
            };

            for (const sensor_meta of accessory.sensors) {
                if (!sensor_meta.type || !sensor_meta.type.toLowerCase().includes('magnet')) {
                    continue;
                }

                if (sensor_meta.position !== undefined && sensor_meta.position !== null) {
                    sensor_entry.position = sensor_meta.position;
                }

                // Get provider fields from metadata
                let provider_fields = sensor_meta.provider_field || [];

                // If empty, fetch from Navixy API
                if (provider_fields.length === 0) {
                    if (asset && asset.tracker_id) {
                        const navixy_sensors = navixy_api.get_tracker_sensor_list({ tracker_id: asset.tracker_id });
                        const matching_sensor = navixy_sensors.find(s => s.id === sensor_meta.id);
                        if (matching_sensor && matching_sensor.input_name) {
                            provider_fields = [matching_sensor.input_name];
                        }
                    }
                }

                provider_fields = prioritize_with_correspondences(provider_fields);

                const state_value = get_magnet_state(provider_fields, telemetry_packet);
                if (state_value !== null) {
                    sensor_entry.state = state_value;

                    const previous_entry = get_current_magnet_entry(asset_id, sensor_meta.id);
                    const previous_state = previous_entry ? previous_entry.state : undefined;

                    if (previous_state === undefined || previous_state === null) {
                        sensor_entry.last_changed_at = telemetry_packet.last_updated_at;
                    } else if (previous_state !== state_value) {
                        sensor_entry.last_changed_at = telemetry_packet.last_updated_at;
                    } else if (previous_entry && previous_entry.last_changed_at) {
                        sensor_entry.last_changed_at = previous_entry.last_changed_at;
                    }
                }
            }

            if (sensor_entry.state !== null) {
                sensors_magnet.push(sensor_entry);
            }
        }
    }

    return sensors_magnet;
}

/**
 * Helper: Prioritize provider fields with correspondence matrix.
 * Always prefers avl_io_* over BLE fields.
 */
function prioritize_with_correspondences(provider_fields) {
    const ordered = [];
    const seen = new Set();

    function add(field) {
        if (!field || seen.has(field)) {
            return;
        }
        ordered.push(field);
        seen.add(field);
    }

    for (const field of provider_fields) {
        const correspondences = PROVIDER_FIELD_CORRESPONDENCE[field] || [];
        const raw = correspondences.find(c => c.startsWith('avl_io_')) || (field.startsWith('avl_io_') ? field : null);

        if (raw) {
            add(raw);
        }
        add(field);

        for (const corr of correspondences) {
            if (!corr.startsWith('avl_io_')) {
                add(corr);
            }
        }
    }

    return ordered;
}

/**
 * Helper: Get magnet state with prioritized mapping.
 * Valid values are 0 or 1 only.
 */
function get_magnet_state(provider_fields, telemetry_packet) {
    for (const field of provider_fields) {
        const value = telemetry_packet[field];
        if (value === 0 || value === 1) {
            return value;
        }
    }

    return null;
}

/**
 * Helper: Fetch previous magnet entry from telemetry packet if present.
 */
function get_current_magnet_entry(asset_id, sensor_id) {
    // TODO: Replace with your actual runtime getter for the current stored telemetry.
    // Example ideas (pick one that matches your backend):
    // const current = telemetry_store.get_current(asset_id);
    // const current = asset_service.get_current_telemetry(asset_id);
    // const current = asset_service.get_asset(asset_id)?.telemetry;
    const current = null;

    const magnets = current && current.sensors && current.sensors.magnet;
    if (Array.isArray(magnets)) {
        return magnets.find(m => m.id === sensor_id) || null;
    }

    return null;
}

// Export for use in backend
module.exports = {
    derive_sensors_magnet,
    prioritize_with_correspondences,
    PROVIDER_FIELD_CORRESPONDENCE
};
