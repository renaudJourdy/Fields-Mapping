# Purpose

Backend implementation specifications for the data recovery system, extracted from the [F1.5-Data-Recovery-System](https://www.notion.so/F1-5-Data-Recovery-System-2e73e766c901807983bcd99b7cb6e0ad?pvs=21)  feature documentation.

This section provides developers with:

- Navixy Raw Data Read API integration specifications
- Provider field extraction automation script documentation
- Version-based validation implementation requirements
- Complete API call specifications with all required provider fields

---

# Contents

## Scripts and Tools

### Provider Field Extraction Script

[extract_provider_fields.py](https://www.notion.so/extract_provider_fields-py-2e83e766c9018067b1b0fcd1e5036968?pvs=21)

**Purpose:** Automatically extracts provider fields from the latest YAML configuration file and generates a JSON payload for Navixy API calls.

**Key Features:**

- Extracts provider fields from YAML configuration sources
- Maps YAML field paths to API-compatible column names
- Includes version-based validation (`yaml_config_version` field)
- Generates ready-to-use JSON payload for API calls
- Excludes problematic fields (`ibutton`, `msg_time`)

**Usage:** See script documentation and feature specification for detailed usage instructions.

---

## API Integration

### Navixy Raw Data Read API

**Endpoint:** `https://api.{region}.navixy.com/dwh/v1/tracker/raw_data/read`

**Regions:**

- EU: `api.eu.navixy.com`
- US: `api.us.navixy.com`
- RU: `api.navixy.com`

**Request Format:** JSON POST request with `hash`, `tracker_id`, `from`, `to`, and `columns` array

**Response Format:** CSV with column headers in first row

---

## Version-Based Validation

The JSON payload includes a `yaml_config_version` field that enables efficient version-based checking:

- **Check Version Before Extraction**: Compare stored JSON's `yaml_config_version` with current YAML's `version` field
- **Skip Extraction if Versions Match**: If versions match, reuse existing `columns` array (no need to re-extract fields)
- **Re-extract Only When Version Changes**: Only execute field extraction when YAML version has changed
- **Store Version with Payload**: Include `yaml_config_version` in stored JSON/cache for quick comparison

---

## Implementation Requirements

### Backend Implementation

1. **YAML Configuration Loading**: Load the latest YAML configuration file from backend storage
2. **Version Extraction**: Extract the `version` field from YAML configuration
3. **Version Comparison**: Compare stored JSON version with current YAML version
4. **Field Extraction**: Execute field extraction only when versions differ
5. **Payload Generation**: Generate API request payload with `columns` array and `yaml_config_version`

### Key Extraction Rules

- Extract fields from `sources[]` entries in YAML mappings
- Extract fields from `parameters.provider.navixy[]` arrays
- Map YAML paths to API column format:
    - `params.avl_io_*` → `inputs.avl_io_*`
    - `params.*` → `inputs.*` or `states.*` based on field name
    - Root-level fields (e.g., `lat`, `lng`) remain as-is
- Always include core columns: `lat`, `lng`, `alt`, `speed`, `heading`, `satellites`, `hdop`, `pdop`, `gps_fix_type`, `event_id`
- Exclude fields: `ibutton`, `msg_time` (cause API errors or automatically included)

# Example

## Output JSON

```json
{
  "hash": "{{navixy_hash}}",
  "tracker_id": "3312229",
  "from": "2025-11-26T00:00:00Z",
  "to": "2025-11-26T23:59:59Z",
  "columns": [
    "alt",
    "discrete_inputs",
    "discrete_outputs",
    "event_id",
    "gps_fix_type",
    "hdop",
    "heading",
    "inputs.avl_io_1",
    "inputs.avl_io_102",
    "inputs.avl_io_103",
    "inputs.avl_io_104",
    "inputs.avl_io_105",
    "inputs.avl_io_106",
    "inputs.avl_io_107",
    "inputs.avl_io_108",
    "inputs.avl_io_10808",
    "inputs.avl_io_10809",
    "inputs.avl_io_10810",
    "inputs.avl_io_10811",
    "inputs.avl_io_16",
    "inputs.avl_io_179",
    "inputs.avl_io_180",
    "inputs.avl_io_181",
    "inputs.avl_io_182",
    "inputs.avl_io_2",
    "inputs.avl_io_20",
    "inputs.avl_io_201",
    "inputs.avl_io_202",
    "inputs.avl_io_203",
    "inputs.avl_io_204",
    "inputs.avl_io_207",
    "inputs.avl_io_210",
    "inputs.avl_io_212",
    "inputs.avl_io_22",
    "inputs.avl_io_23",
    "inputs.avl_io_234",
    "inputs.avl_io_239",
    "inputs.avl_io_24",
    "inputs.avl_io_240",
    "inputs.avl_io_25",
    "inputs.avl_io_26",
    "inputs.avl_io_27",
    "inputs.avl_io_270",
    "inputs.avl_io_273",
    "inputs.avl_io_28",
    "inputs.avl_io_281",
    "inputs.avl_io_282",
    "inputs.avl_io_29",
    "inputs.avl_io_3",
    "inputs.avl_io_30",
    "inputs.avl_io_304",
    "inputs.avl_io_37",
    "inputs.avl_io_380",
    "inputs.avl_io_389",
    "inputs.avl_io_390",
    "inputs.avl_io_4",
    "inputs.avl_io_449",
    "inputs.avl_io_519",
    "inputs.avl_io_69",
    "inputs.avl_io_72",
    "inputs.avl_io_73",
    "inputs.avl_io_74",
    "inputs.avl_io_75",
    "inputs.avl_io_78",
    "inputs.avl_io_81",
    "inputs.avl_io_83",
    "inputs.avl_io_84",
    "inputs.avl_io_86",
    "inputs.avl_io_87",
    "inputs.avl_io_89",
    "inputs.ble_battery_level_1",
    "inputs.ble_battery_level_2",
    "inputs.ble_battery_level_3",
    "inputs.ble_battery_level_4",
    "inputs.ble_humidity_1",
    "inputs.ble_humidity_2",
    "inputs.ble_humidity_3",
    "inputs.ble_humidity_4",
    "inputs.ble_lls_level_1",
    "inputs.ble_lls_level_2",
    "inputs.ble_magnet_sensor_1",
    "inputs.ble_magnet_sensor_2",
    "inputs.ble_magnet_sensor_3",
    "inputs.ble_magnet_sensor_4",
    "inputs.ble_temp_sensor_1",
    "inputs.ble_temp_sensor_2",
    "inputs.ble_temp_sensor_3",
    "inputs.ble_temp_sensor_4",
    "inputs.can_consumption",
    "inputs.can_consumption_relative",
    "inputs.can_engine_hours_relative",
    "inputs.can_fuel_1",
    "inputs.can_fuel_litres",
    "inputs.can_mileage_relative",
    "inputs.ext_temp_sensor_1",
    "inputs.ext_temp_sensor_2",
    "inputs.ext_temp_sensor_3",
    "inputs.ext_temp_sensor_4",
    "inputs.humidity_1",
    "inputs.humidity_2",
    "inputs.lls_level_1",
    "inputs.lls_level_2",
    "inputs.lls_level_3",
    "inputs.lls_level_4",
    "inputs.lls_temperature_1",
    "inputs.lls_temperature_2",
    "inputs.obd_custom_fuel_litres",
    "inputs.obd_custom_odometer",
    "inputs.obd_dtc_number",
    "inputs.obd_mil_status",
    "inputs.temp_sensor",
    "lat",
    "lng",
    "pdop",
    "satellites",
    "speed",
    "states.can_engine_hours",
    "states.can_mileage",
    "states.can_speed",
    "states.hw_mileage",
    "states.moving",
    "states.obd_speed"
  ],
  "yaml_config_version": "1.0.6"
}
```

## Expected cURL

```json
curl --location 'https://api.eu.navixy.com/dwh/v1/tracker/raw_data/read' \
  --header 'accept: text/csv' \
  --header 'Content-Type: application/json' \
  --data '{
    "hash": "{{navixy_hash}}",
    "tracker_id": "{{tracker_id}}",
    "from": "{{from_date}}",
    "to": "{{to_date}}",
    "columns": [
      "alt",
      "discrete_inputs",
      "discrete_outputs",
      "event_id",
      "gps_fix_type",
      "hdop",
      "heading",
      "inputs.avl_io_1",
      "inputs.avl_io_102",
      "inputs.avl_io_103",
      "inputs.avl_io_104",
      "inputs.avl_io_105",
      "inputs.avl_io_106",
      "inputs.avl_io_107",
      "inputs.avl_io_108",
      "inputs.avl_io_10808",
      "inputs.avl_io_10809",
      "inputs.avl_io_10810",
      "inputs.avl_io_10811",
      "inputs.avl_io_16",
      "inputs.avl_io_179",
      "inputs.avl_io_180",
      "inputs.avl_io_181",
      "inputs.avl_io_182",
      "inputs.avl_io_2",
      "inputs.avl_io_20",
      "inputs.avl_io_201",
      "inputs.avl_io_202",
      "inputs.avl_io_203",
      "inputs.avl_io_204",
      "inputs.avl_io_207",
      "inputs.avl_io_210",
      "inputs.avl_io_212",
      "inputs.avl_io_22",
      "inputs.avl_io_23",
      "inputs.avl_io_234",
      "inputs.avl_io_239",
      "inputs.avl_io_24",
      "inputs.avl_io_240",
      "inputs.avl_io_25",
      "inputs.avl_io_26",
      "inputs.avl_io_27",
      "inputs.avl_io_270",
      "inputs.avl_io_273",
      "inputs.avl_io_28",
      "inputs.avl_io_281",
      "inputs.avl_io_282",
      "inputs.avl_io_29",
      "inputs.avl_io_3",
      "inputs.avl_io_30",
      "inputs.avl_io_304",
      "inputs.avl_io_37",
      "inputs.avl_io_380",
      "inputs.avl_io_389",
      "inputs.avl_io_390",
      "inputs.avl_io_4",
      "inputs.avl_io_449",
      "inputs.avl_io_519",
      "inputs.avl_io_69",
      "inputs.avl_io_72",
      "inputs.avl_io_73",
      "inputs.avl_io_74",
      "inputs.avl_io_75",
      "inputs.avl_io_78",
      "inputs.avl_io_81",
      "inputs.avl_io_83",
      "inputs.avl_io_84",
      "inputs.avl_io_86",
      "inputs.avl_io_87",
      "inputs.avl_io_89",
      "inputs.ble_battery_level_1",
      "inputs.ble_battery_level_2",
      "inputs.ble_battery_level_3",
      "inputs.ble_battery_level_4",
      "inputs.ble_humidity_1",
      "inputs.ble_humidity_2",
      "inputs.ble_humidity_3",
      "inputs.ble_humidity_4",
      "inputs.ble_lls_level_1",
      "inputs.ble_lls_level_2",
      "inputs.ble_magnet_sensor_1",
      "inputs.ble_magnet_sensor_2",
      "inputs.ble_magnet_sensor_3",
      "inputs.ble_magnet_sensor_4",
      "inputs.ble_temp_sensor_1",
      "inputs.ble_temp_sensor_2",
      "inputs.ble_temp_sensor_3",
      "inputs.ble_temp_sensor_4",
      "inputs.can_consumption",
      "inputs.can_consumption_relative",
      "inputs.can_engine_hours_relative",
      "inputs.can_fuel_1",
      "inputs.can_fuel_litres",
      "inputs.can_mileage_relative",
      "inputs.ext_temp_sensor_1",
      "inputs.ext_temp_sensor_2",
      "inputs.ext_temp_sensor_3",
      "inputs.ext_temp_sensor_4",
      "inputs.humidity_1",
      "inputs.humidity_2",
      "inputs.lls_level_1",
      "inputs.lls_level_2",
      "inputs.lls_level_3",
      "inputs.lls_level_4",
      "inputs.lls_temperature_1",
      "inputs.lls_temperature_2",
      "inputs.obd_custom_fuel_litres",
      "inputs.obd_custom_odometer",
      "inputs.obd_dtc_number",
      "inputs.obd_mil_status",
      "inputs.temp_sensor",
      "lat",
      "lng",
      "pdop",
      "satellites",
      "speed",
      "states.can_engine_hours",
      "states.can_mileage",
      "states.can_speed",
      "states.hw_mileage",
      "states.moving",
      "states.obd_speed"
    ]
  }'
```

## Expected Output (CSV)

[raw-data-3312229.csv](attachment:f472e11d-4e0c-4794-9f5e-3fe27165f965:raw-data-3312229.csv)