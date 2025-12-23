# Sensor Environment Calculation Functions

This directory contains implementation code for calculated Fleeti fields that require complex logic.

## Files

### `derive_sensors_environment.js`

Implementation for the `sensors.environment[]` calculated field.

**Function**: `derive_sensors_environment(asset_id, telemetry_packet)`

**Purpose**: Builds the `sensors.environment[]` array by matching provider fields to sensors based on `asset.accessories[].sensors[]` metadata. Applies prioritized mapping, unit conversions, and groups related measurements from the same sensor.

**Key Features**:
- Provider field correspondence matrix for mapping processed Navixy fields to raw `avl_io` equivalents
- Automatic enrichment of provider fields with correspondences
- Prioritized mapping (raw `avl_io` fields first, then processed Navixy fields)
- Unit conversions (divide by 10 for temperature and humidity raw values, except `avl_io_202` and `avl_io_204`)
- Validation of raw values (error codes, range checks)
- Navixy API integration for sensor configuration lookup
- Groups related measurements (temperature, humidity, battery, frequency) from same sensor

**Updating the Correspondence Matrix**:

To add new field correspondences, edit the `PROVIDER_FIELD_CORRESPONDENCE` constant at the top of the file:

```javascript
const PROVIDER_FIELD_CORRESPONDENCE = {
  'new_processed_field': ['avl_io_XXX'],
  'avl_io_XXX': ['new_processed_field'],
  // ... existing mappings
};
```

**Unit Conversion Rules**:
- **Temperature**: Divide by 10 for raw `avl_io` (except `avl_io_202` and `avl_io_204` which don't need division)
- **Humidity**: Divide by 10 for raw `avl_io` (multiplier 0.1 per Teltonika spec - Property IDs 86, 104, 106, 108)
- **Battery**: No division needed (already in percent)
- **Frequency**: Divide by 10 for raw `avl_io` (or use multiplier/divider from Navixy API)

**Error Codes**:
- Temperature: `-128` = sensor error
- Humidity: `65535` = sensor not found, `65534` = failed parsing, `65533` = abnormal state (firmware 03.28.00+)
- Battery: `-128` = sensor error

**Validation Ranges**:
- Temperature: `-120` to `120` (raw values)
- Humidity: `0` to `1000` (raw values, becomes 0-100% after division)
- Battery: `0` to `100` (percent)
- Frequency: `>= 0`

**Navixy API Reference**:
- Endpoint: `GET https://api.navixy.com/v2/fsm/tracker/sensor/list`
- Returns sensor configuration including `input_name` which maps to provider field names

**Related Documentation**:
- Fleeti Fields: `sensors.environment[]`
- Teltonika AVL Parameters: `docs/rag/reference/teltonika-fmb140-avl-parameters.csv`
- Fleeti Telemetry Schema: `scripts/input/fleeti-telemetry-schema-specification.md`

