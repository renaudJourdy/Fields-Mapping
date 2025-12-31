/**
 * ============================================================================
 * PROVIDER FIELD CORRESPONDENCE MATRIX
 * ============================================================================
 * Maps processed Navixy field names to their raw avl_io equivalents and vice versa
 * Used to automatically enrich provider_field arrays with both formats
 * 
 * NOTE: Temperature and humidity fields require division by 10 for raw avl_io values
 * (except avl_io_202 and avl_io_204 for temperature which don't need division).
 * Battery fields are already in correct units (percent).
 * ============================================================================
 */
const PROVIDER_FIELD_CORRESPONDENCE = {
    // Temperature fields - LLS (no division needed)
    'lls_temperature_1': ['avl_io_202'], 'avl_io_202': ['lls_temperature_1'],
    'lls_temperature_2': ['avl_io_204'], 'avl_io_204': ['lls_temperature_2'],

    // Temperature fields - External (divide by 10 for raw avl_io)
    'ext_temp_sensor_1': ['avl_io_72'], 'avl_io_72': ['ext_temp_sensor_1'],
    'ext_temp_sensor_2': ['avl_io_73'], 'avl_io_73': ['ext_temp_sensor_2'],
    'ext_temp_sensor_3': ['avl_io_74'], 'avl_io_74': ['ext_temp_sensor_3'],
    'ext_temp_sensor_4': ['avl_io_75'], 'avl_io_75': ['ext_temp_sensor_4'],

    // Temperature fields - BLE (divide by 10 for raw avl_io)
    'ble_temp_sensor_1': ['avl_io_25'], 'avl_io_25': ['ble_temp_sensor_1'],
    'ble_temp_sensor_2': ['avl_io_26'], 'avl_io_26': ['ble_temp_sensor_2'],
    'ble_temp_sensor_3': ['avl_io_27'], 'avl_io_27': ['ble_temp_sensor_3'],
    'ble_temp_sensor_4': ['avl_io_28'], 'avl_io_28': ['ble_temp_sensor_4'],

    // Humidity fields - BLE (divide by 10 for raw avl_io - multiplier 0.1 per Teltonika spec)
    // Reference: Teltonika FMB140 AVL Parameters - Property IDs 86, 104, 106, 108
    'ble_humidity_1': ['avl_io_86'], 'avl_io_86': ['ble_humidity_1'],
    'ble_humidity_2': ['avl_io_104'], 'avl_io_104': ['ble_humidity_2'],
    'ble_humidity_3': ['avl_io_106'], 'avl_io_106': ['ble_humidity_3'],
    'ble_humidity_4': ['avl_io_108'], 'avl_io_108': ['ble_humidity_4'],

    // Humidity fields - Generic
    'humidity_1': [], 'humidity_2': [],  // May have correspondence, needs verification

    // Battery fields - BLE (already in percent, no division needed)
    // Reference: Teltonika FMB140 AVL Parameters - Property IDs 29, 20, 22, 23
    'ble_battery_level_1': ['avl_io_29'], 'avl_io_29': ['ble_battery_level_1'],
    'ble_battery_level_2': ['avl_io_20'], 'avl_io_20': ['ble_battery_level_2'],
    'ble_battery_level_3': ['avl_io_22'], 'avl_io_22': ['ble_battery_level_3'],
    'ble_battery_level_4': ['avl_io_23'], 'avl_io_23': ['ble_battery_level_4']
};

/**
 * ============================================================================
 * FUNCTION: derive_sensors_environment
 * ============================================================================
 * Builds sensors.environment[] array by matching provider fields to sensors
 * based on asset.accessories[].sensors[] metadata.
 * 
 * Function Reference: derive_sensors_environment
 * Implementation Location: This file
 * Dependencies: asset.accessories[].sensors[] metadata
 * ============================================================================
 */
function derive_sensors_environment(asset_id, telemetry_packet) {
    const sensors_environment = [];
    const accessories = asset_service.get_accessories(asset_id);

    for (const accessory of accessories) {
        if (accessory.sensors && accessory.sensors.length > 0) {
            const sensor_entry = {
                id: accessory.id,
                name: accessory.name,
                label: accessory.label,
                position: null,
                temperature: null,
                humidity: null,
                battery: null,
                last_updated_at: telemetry_packet.last_updated_at
            };

            for (const sensor_meta of accessory.sensors) {
                if (['temperature', 'humidity', 'battery'].includes(sensor_meta.type)) {

                    if (sensor_meta.position !== undefined && sensor_meta.position !== null) {
                        sensor_entry.position = sensor_meta.position;
                    }

                    // Get provider fields from metadata
                    let provider_fields = sensor_meta.provider_field || [];

                    // If empty, fetch from Navixy API
                    if (provider_fields.length === 0) {
                        const navixy_sensors = navixy_api.get_tracker_sensor_list({ tracker_id: asset.tracker_id });

                        // Match by sensor ID only (not name - names can be duplicated, input_name cannot)
                        const matching_sensor = navixy_sensors.find(s => s.id === sensor_meta.id);

                        if (matching_sensor && matching_sensor.input_name) {
                            provider_fields = [matching_sensor.input_name];
                            provider_fields = enrich_with_correspondences(provider_fields);
                        }
                    } else {
                        // Enrich existing fields with correspondences
                        provider_fields = enrich_with_correspondences(provider_fields);
                    }

                    // Process sensor value based on type
                    if (sensor_meta.type === 'temperature') {
                        sensor_entry.temperature = get_temperature_value(provider_fields, telemetry_packet);
                    } else if (sensor_meta.type === 'humidity') {
                        sensor_entry.humidity = get_humidity_value(provider_fields, telemetry_packet);
                    } else if (sensor_meta.type === 'battery') {
                        sensor_entry.battery = get_battery_value(provider_fields, telemetry_packet);
                    }
                }
            }

            // Add entry if has at least one measurement
            if (sensor_entry.temperature || sensor_entry.humidity || sensor_entry.battery) {
                sensors_environment.push(sensor_entry);
            }
        }
    }

    return sensors_environment;
}

/**
 * Helper: Enrich provider fields with correspondences from matrix
 */
function enrich_with_correspondences(provider_fields) {
    const enriched = [];
    const seen = new Set();

    for (const field of provider_fields) {
        if (!seen.has(field)) {
            enriched.push(field);
            seen.add(field);
        }

        const correspondences = PROVIDER_FIELD_CORRESPONDENCE[field];
        if (correspondences && correspondences.length > 0) {
            for (const corr of correspondences) {
                if (!seen.has(corr)) {
                    enriched.push(corr);
                    seen.add(corr);
                }
            }
        }
    }

    return enriched;
}

/**
 * Helper: Get temperature value with prioritized mapping
 */
function get_temperature_value(provider_fields, telemetry_packet) {
    for (const field of provider_fields) {
        const value = telemetry_packet[field];

        if (field.startsWith('avl_io_')) {
            // Validate raw value: -120 to 120, exclude -128 (error)
            if (value !== null && value !== undefined && value !== -128 && value >= -120 && value <= 120) {
                // Divide by 10 except avl_io_202 and avl_io_204
                if (field === 'avl_io_202' || field === 'avl_io_204') {
                    return { value: value, unit: '°C' };
                } else {
                    return { value: value / 10, unit: '°C' };
                }
            }
        } else {
            // Processed Navixy field (ext_temp_sensor_X, ble_temp_sensor_X, etc.)
            if (value !== null && value !== undefined) {
                return { value: value, unit: '°C' };
            }
        }
    }

    return null;
}

/**
 * Helper: Get humidity value with prioritized mapping
 */
function get_humidity_value(provider_fields, telemetry_packet) {
    for (const field of provider_fields) {
        const value = telemetry_packet[field];

        if (field.startsWith('avl_io_')) {
            // Validate: 0-1000, exclude error codes 65535, 65534, 65533
            if (value !== null && value !== undefined && ![65535, 65534, 65533].includes(value) && value >= 0 && value <= 1000) {
                return { value: value / 10, unit: '%' };  // Divide by 10 (multiplier 0.1)
            }
        } else {
            // Processed Navixy field (ble_humidity_X, humidity_X)
            if (value !== null && value !== undefined && value >= 0 && value <= 100) {
                return { value: value, unit: '%' };
            }
        }
    }

    return null;
}

/**
 * Helper: Get battery value (already in percent, no division)
 */
function get_battery_value(provider_fields, telemetry_packet) {
    for (const field of provider_fields) {
        const value = telemetry_packet[field];

        // Both raw and processed are already in percent
        if (value !== null && value !== undefined && value !== -128 && value >= 0 && value <= 100) {
            return { value: value, unit: '%' };
        }
    }

    return null;
}

// Export for use in backend
module.exports = {
    derive_sensors_environment,
    enrich_with_correspondences,
    PROVIDER_FIELD_CORRESPONDENCE
};
