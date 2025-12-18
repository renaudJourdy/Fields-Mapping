# Overview

The YAML configuration file is generated from the **Mapping Fields Database CSV**, which serves as the single source of data. All necessary information is already included in the CSV via Notion rollups and relations:

1. Reading the Mapping Fields CSV (contains all required data)
2. Processing mappings in dependency order
3. Generating YAML structure based on mapping type

# Field Name vs Field Path

**Critical Design Decision:** YAML configurations use **Field Names** (stable identifiers) instead of **Field Paths** (can change).

- **Stability**: Field Names (`location_latitude`) do not change when Field Paths (`location.latitude` → `position.latitude`) are refactored
- **Resilience**: YAML configurations remain valid even when telemetry object structure changes
- **Maintainability**: Reduces configuration churn and breaking changes

---

# Data Available in Mapping Fields CSV

## Fleeti Fields Data (via Relation/Rollup)

The CSV includes the following columns that are rolled up from the Fleeti Fields Database relation:

- **Fleeti Field** (Name) → **Used as YAML key** (stable identifier, does not change)
- **Fleeti Field Path** → Used for documentation/comments only (can change, resolved at runtime)
- **Fleeti Unit** → Used for unit conversion detection
- **Fleeti Data Type** → Used for validation
- **Computation Approach** → Rolled up from Fleeti Fields relation (for calculated mappings)

**Important:** Field Name (`Fleeti Field`) is the **stable identifier** used in YAML keys, dependencies, and function parameters. 

## Provider Fields Data (via Relation/Rollup)

The CSV includes the following columns that are rolled up from the Provider Fields Database relation:

- **Provider Fields** → Relation to Provider Fields Database entries
- **Provider Field Paths** → Used to read from provider packets (comma-separated if multiple)
- **Provider Unit** → Used for unit conversion detection

---

# YAML Structure

**Important:** YAML uses **Field Name** (stable identifier) as keys, not Field Path. 

```yaml
version: "1.0.0"
provider: "navixy"
mappings:
  location_latitude:
    type: direct
    source: lat
    unit: degrees
    data_type: number
    error_handling: return_null
    # Field Path: location.latitude

  location_longitude:
    type: direct
    source: lng
    unit: degrees
    data_type: number
    error_handling: return_null
    # Field Path: location.longitude

  location_altitude:
    type: direct
    source: alt
    unit: meters
    data_type: number
    error_handling: return_null
    # Field Path: location.altitude

  location_heading:
    type: direct
    source: heading
    unit: degrees
    data_type: number
    error_handling: return_null
    # Field Path: location.heading

  location_precision_fix_quality:
    type: direct
    source: params.avl_io_69
    unit: none
    data_type: number
    error_handling: return_null
    # Field Path: location.precision.fix_quality

  location_precision_satellites:
    type: direct
    source: satellites
    unit: none
    data_type: number
    error_handling: return_null
    # Field Path: location.precision.satellites

  location_precision_hdop:
    type: prioritized
    sources:
    - priority: 1
      field: hdop
      path: hdop
    - priority: 2
      field: avl_io_182
      path: params.avl_io_182
    unit: none
    data_type: number
    error_handling: use_fallback
    # Field Path: location.precision.hdop

  location_precision_pdop:
    type: prioritized
    sources:
    - priority: 1
      field: pdop
      path: pdop
    - priority: 2
      field: avl_io_181
      path: params.avl_io_181
    unit: none
    data_type: number
    error_handling: use_fallback
    # Field Path: location.precision.pdop

  location_cardinal_direction:
    type: calculated
    calculation_type: function_reference
    function: derive_cardinal_direction
    parameters:
      heading: location_heading
    dependencies:
    - location_heading
    data_type: string
    error_handling: return_null
    # Field Path: location.cardinal_direction
    # Computation Approach: Derived from location.heading
    # dirs = ["N","NE","E","SE","S","SW","W","NW"];
    # cardinal = dirs[Math.floor((heading + 22.5) % 360 / 45)];
    # Description: Calculated field: Cardinal direction (N, NE, E, SE, S, SW, W, NW)

  location_geocoded_address:
    type: calculated
    calculation_type: function_reference
    function: derive_geocoded_address
    parameters:
      latitude: location_latitude
      longitude: location_longitude
    dependencies:
    - location_latitude
    - location_longitude
    data_type: string
    error_handling: return_null
    # Field Path: location.geocoded_address
    # Computation Approach: Use external API (Google) to convert latitude and longitude into geocoded address.
    # Description: Calculated field: Single string representation of the location

  location_last_changed_at:
    type: calculated
    calculation_type: function_reference
    function: derive_last_changed_at
    parameters:
      latitude: location_latitude
      longitude: location_longitude
    dependencies:
    - location_latitude
    - location_longitude
    data_type: datetime
    error_handling: return_null
    # Field Path: location.last_changed_at
    # Computation Approach: Backend compares current position with previous.
    # if (lat !== prev.lat || lon !== prev.lon) {
    # location_last_changed_at= now();
    # }
    # Description: Calculated field: Unix Epoch timestamp (milliseconds, number) when location/heading last changed significantly (threshold applied to filter GPS noise). Used for dwell-time calculations and "parked since X" features.
```

---

# Function Registry Pattern

The YAML configuration supports a **Function Registry Pattern** that makes configurations directly pluggable into backend code. This pattern enables:

1. **Direct Function Calls**: Backend can call functions directly from a registry
2. **Parameter Mapping**: Structured mapping of function parameters to Fleeti field names (stable identifiers)
3. **Validation**: Backend can validate function existence and parameter correctness
4. **Implementation Guidance**: YAML comments provide developer guidance without breaking parsing
5. **Stable Configuration**: Uses Field Names instead of Field Paths, making configs resilient to path changes

## Calculation Execution Modes

There are two calculation execution modes, each with different YAML structures:

### 1. Function Reference (`function_reference`) - **Default for All Calculated Fields**

**When to Use:**
- Function exists (or should exist) in backend function registry
- **Default choice** for all calculated fields - use this for function calls
- Can be implemented as a pure function (takes inputs, returns output)
- Reusable across providers or contexts
- All calculated logic should use `function_reference` - functions can handle complex logic internally

**Decision Rule:** Use `function_reference` for all calculated fields that require function calls. Use `formula` only for simple mathematical expressions that can be parsed and evaluated directly.

**YAML Structure:**

```yaml
mappings:
{Fleeti Field Name}:
type:"calculated"
calculation_type:"function_reference"
function:"function_name"  # Must exist in FUNCTION_REGISTRY
formula:"(field1 / field2) * 100"  # Optional: embed formula if available and embeddable
parameters:
param1:"fleeti_field_name_1"
param2:"fleeti_field_name_2"
dependencies:
-"fleeti_field_name_1"
-"fleeti_field_name_2"
data_type:{Fleeti Data Type}
    # Implementation: path/to/implementation.py
    # Description: What the function does
    # Algorithm: Step-by-step algorithm description
    # Field Path: {Fleeti Field Path}
```

**Example 1: Function reference without formula (Fleeti fields)**

```yaml
mappings:
location_cardinal_direction:
type:"calculated"
calculation_type:"function_reference"
function:"derive_cardinal_direction"
parameters:
heading:"location_heading"  # No prefix = Fleeti field
    # Implementation: telemetry-transformation-service/src/functions/cardinal.py
    # Description: Converts heading angle (0-359°) to cardinal direction
    # Algorithm: Add 22.5° offset, divide by 45°, map to 8 directions (N, NE, E, SE, S, SW, W, NW)
    # Field Path: location.cardinal_direction (resolved at runtime)
dependencies:
-"location_heading"
data_type:"string"
```

**Example 2: Function reference with embeddable formula**

```yaml
mappings:
fuel_consumption_rate:
type:"calculated"
calculation_type:"function_reference"
function:"calculate_fuel_consumption_rate"
formula:"(fuel_consumed_trip / trip_distance) * 100"  # Optional: embed formula if available
parameters:
fuel_consumed:"fuel_consumed_trip"
distance:"trip_distance"
    # Implementation: telemetry-transformation-service/src/functions/fuel.py
    # Description: Calculates fuel consumption rate as percentage
    # Algorithm: Divide fuel consumed by trip distance, multiply by 100
    # Field Path: fuel.consumption_rate (resolved at runtime)
dependencies:
-"fuel_consumed_trip"
-"trip_distance"
data_type:"number"
```

**Example 3: Function reference with complex logic (Fleeti fields)**

```yaml
mappings:
location_geocoded_address:
type:"calculated"
calculation_type:"function_reference"
function:"geocode_location"
parameters:
latitude:"location_latitude"  # No prefix = Fleeti field
longitude:"location_longitude"  # No prefix = Fleeti field
    # Implementation: telemetry-transformation-service/src/functions/geocoding.py
    # Description: Converts lat/lng to formatted address using Google Geocoding API
    # Algorithm:
    #   1. Call Google Geocoding API with lat/lng
    #   2. Extract formatted_address from response
    #   3. Cache result for 24 hours (same location)
    #   4. Return formatted address string
    # Field Path: location.geocoded_address (resolved at runtime)
dependencies:
-"location_latitude"
-"location_longitude"
data_type:"string"
```

**Example 4: Function reference with provider fields (future use)**

```yaml
mappings:
raw_data_processor:
type:"calculated"
calculation_type:"function_reference"
function:"process_raw_provider_data"
parameters:
raw_lat:"provider:lat"  # provider: prefix = Provider field path
raw_lng:"provider:lng"  # provider: prefix = Provider field path
raw_heading:"provider:heading"  # provider: prefix = Provider field path
    # Implementation: telemetry-transformation-service/src/functions/raw_processor.py
    # Description: Processes raw provider data before transformation
    # Note: Parameters with provider: prefix read directly from provider packet
data_type:"string"
```

### 2. Formula (`formula`) - **For Simple Math Only**

**When to Use:** Simple mathematical expressions that can be parsed and evaluated directly without requiring a function call. Use sparingly - prefer `function_reference` for most calculations.

**YAML Structure:**

```yaml
mappings:
{Fleeti Field Name}:
type:"calculated"
calculation_type:"formula"
formula:"(field_name1 / field_name2) * 100"  # Parseable expression using Field Names
dependencies:
-"field_name1"
-"field_name2"
data_type:{Fleeti Data Type}
    # Field Path: {Fleeti Field Path}
```

**Example:**

```yaml
mappings:
fuel_consumption_rate:
type:"calculated"
calculation_type:"formula"
formula:"(fuel_consumed_trip / trip_distance) * 100"
dependencies:
-"fuel_consumed_trip"
-"trip_distance"
data_type:"number"
    # Field Path: fuel.consumption_rate (resolved at runtime)
```

**Note:** For most calculations, prefer `function_reference` even if a formula exists. The `formula` type should only be used for very simple expressions that don’t warrant a function call. If a formula can be embedded, include it as an optional `formula` parameter in `function_reference` instead.

## Parameter Mapping Format

For `function_reference` type, parameters must be structured as a mapping from function parameter names to field references. The source of each parameter is indicated using a prefix format:

**Default (no prefix)**: Fleeti field name (stable identifier)
```yaml
parameters:
  latitude: location_latitude  # No prefix = Fleeti field
  longitude: location_longitude
```

**Provider prefix**: Provider field path (for direct provider field access)
```yaml
parameters:
  raw_lat: provider:lat  # provider: prefix = Provider field path
  raw_lng: provider:lng
```

**Mixed sources** (both Fleeti and Provider fields):
```yaml
parameters:
  latitude: location_latitude  # Fleeti field
  raw_heading: provider:heading  # Provider field
```

**Rules:**
- Parameter names must match function signature
- **Fleeti field names** (no prefix) must exist in dependencies
- **Provider field paths** (with `provider:` prefix) reference provider packet fields directly
- All function parameters must be mapped
- Fleeti field names use underscore notation (e.g., `location_heading`)
- Backend resolves:
  - **Fleeti fields**: Field Name → Field Path using lookup table, then reads from transformed telemetry object
  - **Provider fields**: Extracts provider field path (e.g., `lat` from `provider:lat`) and reads directly from provider packet

## Implementation Guidance Comments

YAML comments (lines starting with `#`) can be used to provide implementation guidance without affecting YAML parsing:

```yaml
# Implementation: path/to/file.py
# Description: What the function does
# Algorithm: Step-by-step algorithm description
# Error Handling: How errors should be handled
```

These comments are:
- **Ignored by YAML parser** (safe to include)
- **Visible to developers** (helpful for implementation)
- **Not validated** (informational only)

---

# Mapping Type Processing

### 1. Direct Mapping

**Required Columns:**
- `Fleeti Field` (Name - stable identifier)
- `Fleeti Field Path` (for reference/documentation)
- `Provider Field Paths` (single)
- `Fleeti Unit`
- `Fleeti Data Type`

**YAML Generation:**

```yaml
mappings:
{Fleeti Field Name}:
type:"direct"
source:{Provider Field Paths}
unit:{Fleeti Unit}
data_type:{Fleeti Data Type}
    # Field Path: {Fleeti Field Path}
```

**Optional Columns (if provided):**
- `Unit Conversion` → Add `unit_conversion` key (only if units differ and conversion needed)
- `Default Value` → Add `default` key (optional, typically `null`)
- `Error Handling` → Add `error_handling` key (optional, defaults to `"return_null"` for direct mappings)

**Example:**

```yaml
mappings:
location_latitude:
type:"direct"
source:"lat"
unit:"degrees"
data_type:"number"
default:null
    # Field Path: location.latitude
```

**Note:** `unit_conversion` should only be included if Provider Unit ≠ Fleeti Unit and both are non-empty. See Auto-Generation Rules section for details.

---

### 2. Prioritized Mapping

**Required Columns:**
- `Fleeti Field` (Name - stable identifier)
- `Fleeti Field Path` (for reference/documentation)
- `Provider Fields` (comma-separated)
- `Provider Field Paths` (comma-separated)
- `Priority JSON`
- `Fleeti Unit`
- `Fleeti Data Type`

**YAML Generation:**

1. Parse `Priority JSON` to get priority order
2. For each provider field in priority order:
    - Use `Provider Field Paths` from CSV (already includes paths for all provider fields)
    - Add to `sources` array with priority

```yaml
mappings:
{Fleeti Field Name}:
type:"prioritized"
sources:
-priority:{priority}
field:{Provider Field Name}
path:{Provider Field Path}
      # ... more sources in priority order
unit:{Fleeti Unit}
data_type:{Fleeti Data Type}
error_handling:{Error Handling or"use_fallback"}
    # Field Path: {Fleeti Field Path}
```

**Auto-Generation Rules:**
- `error_handling`: Default to `"use_fallback"` if not specified
- `Unit Conversion`: Auto-generate only if `Provider Unit` ≠ `Fleeti Unit` AND both are valid (see Unit Conversion rules)

**Example:**

```yaml
mappings:
location_precision_hdop:
type:"prioritized"
sources:
-priority:1
field:"hdop"
path:"hdop"
-priority:2
field:"avl_io_182"
path:"params.avl_io_182"
unit:"none"
data_type:"number"
error_handling:"use_fallback"
    # Field Path: location.precision.hdop (resolved at runtime)
```

---

### 3. Calculated Mapping

**Required Columns:**
- `Fleeti Field` (Name - stable identifier)
- `Fleeti Field Path` (for reference/documentation)
- `Calculation Type` (determines YAML structure)
- `Computation Approach` (automatically populated via Notion rollup from Fleeti Fields Database relation)
- `Fleeti Data Type`

**YAML Generation varies by Calculation Type:**

### If `calculation_type = "function_reference"`:

**Required Additional Columns:**
- `Backend Function Name` → Maps to `function` field
- `Function Parameters` → Maps to `parameters` field (structured mapping using Field Names)

**Optional Additional Columns:**
- `Computation Approach` → Maps to `# Computation Approach:` comment (multi-line support)

**YAML Generation:**

```yaml
mappings:
{Fleeti Field Name}:
type:"calculated"
calculation_type:"function_reference"
function:{Backend Function Name}  # Must exist in FUNCTION_REGISTRY
parameters:
{param1}:"{fleeti_field_name_1}"
{param2}:"{fleeti_field_name_2}"
dependencies:
-"{fleeti_field_name_1}"
-"{fleeti_field_name_2}"
data_type:{Fleeti Data Type}
    # Field Path: {Fleeti Field Path}
    # Computation Approach: {Computation Approach from Fleeti Fields CSV}
```

**Example 1: Function reference with computation approach**

```yaml
mappings:
location_cardinal_direction:
type:"calculated"
calculation_type:"function_reference"
function:"derive_cardinal_direction"
parameters:
heading:"location_heading"
dependencies:
-"location_heading"
data_type:"string"
    # Field Path: location.cardinal_direction (resolved at runtime)
    # Computation Approach: Derived from location.heading
    #   dirs = ["N","NE","E","SE","S","SW","W","NW"];
    #   cardinal = dirs[Math.floor((heading + 22.5) % 360 / 45)];
```

**Example 2: Function reference with multi-line computation approach**

```yaml
mappings:
location_geocoded_address:
type:"calculated"
calculation_type:"function_reference"
function:"geocode_location"
parameters:
latitude:"location_latitude"
longitude:"location_longitude"
dependencies:
-"location_latitude"
-"location_longitude"
data_type:"string"
    # Field Path: location.geocoded_address (resolved at runtime)
    # Computation Approach: Use external API (Google) to convert latitude and longitude into geocoded address.
```

### If `calculation_type = "formula"` (kept for future use):

**Required Additional Columns:**
- `Computation Approach` → Parseable mathematical expression (using Field Names)

**YAML Generation:**

```yaml
mappings:
{Fleeti Field Name}:
type:"calculated"
calculation_type:"formula"
formula:{Computation Approach}  # Parseable expression using Field Names
dependencies:
-{Dependency Field Name 1}
-{Dependency Field Name 2}
data_type:{Fleeti Data Type}
    # Field Path: {Fleeti Field Path}
```

**Note:** The `formula` type is kept for future use. Currently, all calculated fields use `function_reference` type with computation approach stored as comments.

---

### 4. Transformed Mapping

**Required Columns:**
- `Fleeti Field` (Name - stable identifier)
- `Fleeti Field Path` (for reference/documentation)
- `Transformation Rule` (may reference Field Names)
- `Service Integration` (can reference multiple services)
- `Fleeti Data Type`

**YAML Generation:**

```yaml
mappings:
{Fleeti Field Name}:
type:"transformed"
transformation:{Transformation Rule}  # May reference Field Names
service_fields:
-{Service Field 1}  # Can be from Asset, Accessory, Geofence, Driver, etc.
-{Service Field 2}
data_type:{Fleeti Data Type}
    # Field Path: {Fleeti Field Path}
```

**Example:**

```yaml
mappings:
fuel_level_liters:
type:"transformed"
transformation:"(fuel_level_percent / 100) * static.tank_capacity_liters"
service_fields:
-"static.tank_capacity_liters"  # Asset Service field
dependencies:
-"fuel_level_percent"
data_type:"number"
    # Field Path: fuel.level_liters (resolved at runtime)

mappings:
geofence_name:
type:"transformed"
transformation:"geofence.name"  # References Geofence Service field
service_fields:
-"geofence.id"  # Geofence Service field
-"geofence.name"  # Geofence Service field
dependencies:
-"location_latitude"
-"location_longitude"
data_type:"string"
    # Field Path: geofence.name (resolved at runtime)
```

---

### 5. I/O Mapped

**Required Columns:**
- `Fleeti Field` (Name - stable identifier)
- `Fleeti Field Path` (for reference/documentation)
- `I/O Mapping Config` (JSON)

**YAML Generation:**

1. Parse `I/O Mapping Config` JSON
2. Extract `default_source` and `installation_metadata`

```yaml
mappings:
{Fleeti Field Name}:
type:"io_mapped"
default_source:{default_source from JSON}
installation_metadata:{installation_metadata from JSON}
data_type:{Fleeti Data Type}
    # Field Path: {Fleeti Field Path}
```

**Example:**

```yaml
mappings:
power_ignition:
type:"io_mapped"
default_source:"io.inputs.individual.input_1"
installation_metadata:"asset.installation.ignition_input_number"
data_type:"boolean"
    # Field Path: power.ignition (resolved at runtime)
```

---

### 6. Asset-Integrated Mapping

**Required Columns:**
- `Fleeti Field` (Name - stable identifier)
- `Fleeti Field Path` (for reference/documentation)
- `Service Integration` (can reference multiple services)
- `Fleeti Data Type`

**YAML Generation:**

```yaml
mappings:
{Fleeti Field Name}:
type:"asset_integrated"
service_fields:
-{Service Field 1}  # Can be from Asset, Accessory, Geofence, Driver, etc.
-{Service Field 2}
data_type:{Fleeti Data Type}
    # Field Path: {Fleeti Field Path}
```

**Example:**

```yaml
mappings:
asset_installation_ignition_input_number:
type:"asset_integrated"
service_fields:
-"asset.installation.ignition_input_number"  # Asset Service field
data_type:"number"
    # Field Path: asset.installation.ignition_input_number (resolved at runtime)

mappings:
accessory_sensor_type:
type:"asset_integrated"
service_fields:
-"accessory.id"  # Accessory Service field
-"accessory.sensor.type"  # Accessory Service field
data_type:"string"
    # Field Path: accessory.sensor.type (resolved at runtime)
```

---

# Backend Integration

## Function Registry Structure

The backend should maintain a function registry that maps function names to implementations:

```python
# telemetry-transformation-service/src/functions/registry.py

FUNCTION_REGISTRY = {
    "derive_cardinal_direction": {
        "function": derive_cardinal_direction,
        "signature": {
            "heading": {"type": "float", "required": True}
        },
        "returns": "str",
        "description": "Converts heading angle (0-359°) to cardinal direction"
    },
    "geocode_location": {
        "function": geocode_location,
        "signature": {
            "latitude": {"type": "float", "required": True},
            "longitude": {"type": "float", "required": True}
        },
        "returns": "str",
        "description": "Converts lat/lng to formatted address using Google Geocoding API"
    }
}
```

## Field Name → Field Path Resolution

**Important:** YAML uses **Field Names** (stable identifiers) as keys and in dependencies/parameters. Backend must resolve Field Names to Field Paths at runtime.

**Backend Lookup Table:**

The backend maintains a lookup table mapping Field Names to Field Paths. This table is updated when Field Paths change, but YAML configurations remain stable.

```python
# Field Name → Field Path lookup table (updated when paths change)
FIELD_NAME_TO_PATH = {
    "location_latitude": "location.latitude",
    "location_longitude": "location.longitude",
    "location_heading": "location.heading",
    "location_cardinal_direction": "location.cardinal_direction",
    "motion_speed": "motion.speed",
    "fuel_consumption_rate": "fuel.consumption_rate",
    # ... updated when Field Paths change
}

def resolve_field_path(field_name):
    """Resolve Field Name to Field Path"""
    return FIELD_NAME_TO_PATH.get(field_name, field_name)
```

## YAML Loader and Validation

The backend YAML loader should:

1. **Load YAML Configuration** (uses Field Names as keys)
2. **Resolve Field Names to Field Paths** (using lookup table)
3. **Validate Function References**
    - Check if `function` exists in `FUNCTION_REGISTRY`
    - Validate parameter names match function signature
    - Validate parameter Field Names exist in dependencies
4. **Resolve Parameter Mapping**
    - Map function parameter names to actual field values
    - Resolve Field Names to Field Paths
    - Extract values from telemetry object using Field Paths
5. **Execute Functions**
    - Call function with mapped parameters
    - Handle errors according to `error_handling` strategy

**Example YAML Loader:**

```python
def load_mapping_config(yaml_path):
    """Load and validate YAML mapping configuration"""
    import yaml

    config = yaml.safe_load(open(yaml_path))

    for field_name, mapping in config["mappings"].items():
        # Resolve Field Name to Field Path for reference
        field_path = resolve_field_path(field_name)

        if mapping["type"] == "calculated":
            if mapping["calculation_type"] == "function_reference":
                # Validate function exists
                func_name = mapping["function"]
                if func_name not in FUNCTION_REGISTRY:
                    raise ValueError(
                        f"Function '{func_name}' not found in registry for field '{field_name}' (path:{field_path})"
                    )

                # Validate parameters match function signature
                func_info = FUNCTION_REGISTRY[func_name]
                func_signature = func_info["signature"]

                for param_name in mapping["parameters"]:
                    if param_name not in func_signature:
                        raise ValueError(
                            f"Parameter '{param_name}' not in function '{func_name}' signature"
                        )

                # Validate all required parameters are provided
                for param_name, param_info in func_signature.items():
                    if param_info.get("required", True) and param_name not in mapping["parameters"]:
                        raise ValueError(
                            f"Required parameter '{param_name}' missing for function '{func_name}'"
                        )

                # Validate Fleeti field names exist in dependencies (provider: fields don't need dependencies)
                for param_name, field_ref in mapping["parameters"].items():
                    if not field_ref.startswith("provider:"):
                        # Only Fleeti fields need to be in dependencies
                        if field_ref not in mapping.get("dependencies", []):
                            raise ValueError(
                                f"Field name '{field_ref}' not in dependencies for parameter '{param_name}'"
                            )

    return config

def execute_calculated_field(mapping, telemetry_data, provider_packet=None):
    """Execute calculated field using function registry"""
    if mapping["calculation_type"] == "function_reference":
        func_name = mapping["function"]
        func_info = FUNCTION_REGISTRY[func_name]
        func = func_info["function"]

        # Map parameters: function_param -> field_value
        params = {}
        for param_name, field_ref in mapping["parameters"].items():
            # Check if parameter references provider field (provider: prefix)
            if field_ref.startswith("provider:"):
                # Extract provider field path (e.g., "lat" from "provider:lat")
                provider_field_path = field_ref[9:]  # Remove "provider:" prefix
                # Read directly from provider packet
                if provider_packet:
                    params[param_name] = get_nested_value(provider_packet, provider_field_path)
                else:
                    params[param_name] = None
            else:
                # Fleeti field: resolve Field Name to Field Path
                field_path = resolve_field_path(field_ref)
                # Extract value from transformed telemetry using Field Path
                params[param_name] = get_nested_value(telemetry_data, field_path)

        # Call function
        try:
            return func(**params)
        except Exception as e:
            # Handle error according to error_handling strategy
            error_handling = mapping.get("error_handling", "return_null")
            if error_handling == "return_null":
                return None
            elif error_handling == "throw_error":
                raise
            else:
                return None

    elif mapping["calculation_type"] == "formula":
        # Parse and evaluate formula
        return evaluate_formula(mapping["formula"], telemetry_data, mapping["dependencies"])
```

## Parameter Mapping Resolution

The backend must resolve parameter mappings by checking the source prefix:

1. **Check Parameter Source**: 
   - If parameter value starts with `provider:` → Extract provider field path and read from provider packet
   - If no prefix → Treat as Fleeti field name, resolve to Field Path, read from transformed telemetry object
2. **Extracting Field Values**: Use field paths to extract values from appropriate source (provider packet or telemetry object)
3. **Type Conversion**: Convert values to match function signature types
4. **Null Handling**: Handle missing/null values according to error handling strategy

**Example:**

```python
def get_nested_value(obj, path):
    """Extract nested value from object using dot notation path"""
    keys = path.split(".")
    value = obj
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        elif isinstance(value, list) and key.isdigit():
            value = value[int(key)] if int(key) < len(value) else None
        else:
            return None
        if value is None:
            return None
    return value

# Example usage with prefix resolution:
telemetry = {
    "location": {
        "heading": 45.0
    }
}

provider_packet = {
    "lat": 40.7128,
    "lng": -74.0060,
    "heading": 90.0
}

# Fleeti field (no prefix): heading -> location.heading
heading_value = get_nested_value(telemetry, "location.heading")  # Returns 45.0

# Provider field (with prefix): provider:heading -> heading
raw_heading = get_nested_value(provider_packet, "heading")  # Returns 90.0
```

## Error Handling

The backend should handle errors according to the `error_handling` field:

- **`return_null`**: Return `None` if function fails or parameters are missing
- **`throw_error`**: Raise exception if function fails
- **`use_fallback`**: Try next priority source (for prioritized mappings only)

---

# Processing Order

1. **Load Data:**
    - Read Mapping Fields CSV (contains all required data via Notion rollups/relations)
    - All Fleeti Fields and Provider Fields data is already included in the CSV columns
2. **Build Dependency Graph:**
    - For each mapping, extract dependencies from CSV `Dependencies` column
    - Build directed graph
    - Detect circular dependencies (error)
3. **Topological Sort:**
    - Process mappings in dependency order
    - Direct mappings first (no dependencies)
    - Then prioritized mappings
    - Then calculated/transformed mappings (after dependencies)
4. **Generate YAML:**
    - For each mapping in sorted order:
        - Read data directly from CSV columns (no joins needed)
        - Generate YAML entry based on mapping type
        - Apply auto-generation rules
5. **Validate:**
    - Check all required fields present in CSV
    - Validate JSON structures (Priority JSON, I/O Mapping Config, etc.)
    - Validate unit conversions
    - Check for missing dependencies

---

# Auto-Generation Rules

## Unit Conversion

**Rule:** Generate unit conversion only when `Provider Unit` ≠ `Fleeti Unit` AND both units are valid and non-empty.

**Skip Conditions (do NOT generate unit_conversion):**
1. **Empty or Unknown Units:** Skip if Provider Unit is empty, `"-"`, `"none"`, or `null`
2. **Equivalent Units:** Skip if units are equivalent (see Unit Equivalence Table below)
3. **Same Units:** Skip if Provider Unit exactly equals Fleeti Unit (case-insensitive)
4. **No Conversion Needed:** Skip if `Unit Conversion` column is explicitly empty and units match

**Unit Equivalence Table:**

| Unit Variants | Equivalent To |
| --- | --- |
| `m`, `meter`, `meters` | `meters` |
| `km`, `kilometer`, `kilometers` | `kilometers` |
| `deg`, `degree`, `degrees` | `degrees` |
| `°C`, `celsius`, `C` | `celsius` |
| `°F`, `fahrenheit`, `F` | `fahrenheit` |
| `km/h`, `kmh`, `kph` | `km/h` |
| `m/s`, `mps`, `meters_per_second` | `m/s` |
| `mph`, `miles_per_hour` | `mph` |
| `none`, `-`, `""` (empty) | No unit (skip conversion) |

**Detection Logic:**
1. Normalize both Provider Unit and Fleeti Unit (trim, lowercase, remove special chars)
2. Check equivalence table for matches
3. If equivalent → **Skip unit_conversion**
4. If different and both valid → Generate conversion rule
5. If Provider Unit is empty/unknown → **Skip unit_conversion**

**Conversion Rule Format:**

Use actionable conversion formulas, not descriptive text:

**Good Examples:**

```yaml
unit_conversion:"multiply by 0.277778"  # km/h → m/s
unit_conversion:"multiply by 3.6"      # m/s → km/h
unit_conversion:"divide by 1000"       # meters → kilometers
unit_conversion:"(value - 32) * 5/9"   # °F → °C
```

**Bad Examples (avoid):**

```yaml
unit_conversion:"Convert from degrees to degrees"  # Same unit
unit_conversion:"Convert from m to meters"         # Equivalent units
unit_conversion:"Convert from - to none"           # Empty unit
```

**Generation Examples:**

| Provider Unit | Fleeti Unit | Action | Result |
| --- | --- | --- | --- |
| `km/h` | `m/s` | Generate | `unit_conversion: "multiply by 0.277778"` |
| `degrees` | `degrees` | Skip | (no unit_conversion key) |
| `m` | `meters` | Skip | (equivalent units) |
| `-` | `none` | Skip | (empty/unknown units) |
| `km/h` | `km/h` | Skip | (same unit) |
| `°C` | `celsius` | Skip | (equivalent units) |

## Error Handling

**Rule:** Apply default error handling based on mapping type.

**Defaults:**
- `prioritized`: `"use_fallback"` (try next priority)
- `direct`: `"return_null"` (return null if source missing)
- `calculated`: `"return_null"` (return null if calculation fails)
- `transformed`: `"return_null"` (return null if transformation fails)

**Override:** If `Error Handling` column is specified, use that value.

## Default Values

**Rule:** Apply default value if source unavailable.

**Default:** `null` (unless `Default Value` column specifies otherwise)

---

# Validation Rules

## Required Field Validation

- **Fleeti Field Path**: Must be present in CSV (already validated via Notion relation)
- **Provider Field Paths**: Must be present in CSV (already validated via Notion relation)
- **Priority JSON**: Must be valid JSON (for prioritized mappings)
- **I/O Mapping Config**: Must be valid JSON (for io_mapped mappings)
- **Dependencies**: All dependencies must reference valid Fleeti Field Names (validated via Notion relation)

## Type Validation

- **Data Types**: Must match between Provider and Fleeti (or conversion specified) - data already in CSV
- **Structure Types**: Nested objects must match JSON Structure - validated via Notion relation

## Unit Conversion Validation

- **Empty Units**: If Provider Unit is empty, `"-"`, `"none"`, or `null`, `unit_conversion` must NOT be generated
- **Equivalent Units**: If units are equivalent (see Unit Equivalence Table), `unit_conversion` must NOT be generated
- **Same Units**: If Provider Unit exactly equals Fleeti Unit, `unit_conversion` must NOT be generated
- **Format**: `unit_conversion` must use actionable formulas (e.g., `"multiply by 0.277778"`), not descriptive text (e.g., `"Convert from X to Y"`)

## Dependency Validation

- **Circular Dependencies**: Must not exist (error)
- **Missing Dependencies**: All dependencies must be defined before dependent field

---

# Example: Complete YAML Generation

**Complete Example:** See [`scripts/navixy-mapping.yaml`](scripts/navixy-mapping.yaml) for a full example of generated YAML configuration.

## Input: Mapping Fields CSV Row

```
Mapping Name,Fleeti Field,Fleeti Field Path,Provider,Mapping Type,Status,Configuration Level,Provider Fields,Provider Field Paths,Provider Unit,Priority JSON,Computation Approach,Transformation Rule,I/O Mapping Config,Service Integration,Dependencies,Calculation Type,Default Value,Error Handling,Unit Conversion,Backend Function Name,Function Parameters,Fleeti Unit,Fleeti Data Type,Version Added,Last Modified,Notes
location.precision.hdop from Navixy,location_precision_hdop,location.precision.hdop,navixy,prioritized,planned,default,"hdop, avl_io_182","hdop, params.avl_io_182","none, none","[{""priority"": 1, ""field"": ""hdop""}, {""priority"": 2, ""field"": ""avl_io_182""}]",,,,,,,,,use_fallback,,,none,number,1.0.0,2025-01-16,Prioritized mapping: Horizontal Dilution of Precision
```

## Generated YAML

```yaml
mappings:
location_precision_hdop:
type:"prioritized"
sources:
-priority:1
field:"hdop"
path:"hdop"
-priority:2
field:"avl_io_182"
path:"params.avl_io_182"
unit:"none"
data_type:"number"
error_handling:"use_fallback"
    # Field Path: location.precision.hdop (resolved at runtime)
```

**Note:** No `unit_conversion` is included because Provider Units (`none, none`) match Fleeti Unit (`none`), so conversion is skipped per Auto-Generation Rules.

---

# Implementation Notes

## CSV Data Structure

The Mapping Fields CSV contains all necessary columns with data already rolled up from relations:

1. **Fleeti Fields Data:**
    - Available directly in CSV columns: `Fleeti Field`, `Fleeti Field Path`, `Fleeti Unit`, `Fleeti Data Type`
    - No lookup needed - data is already in each row
2. **Provider Fields Data:**
    - Available directly in CSV columns: `Provider Fields`, `Provider Field Paths`, `Provider Unit`
    - For comma-separated values, split and process each field path
    - No lookup needed - data is already in each row

**Note:** All data comes from the CSV file. No database joins or lookups are required during generation.

## Performance Considerations

- Read CSV into memory (single file)
- Process mappings in batches by mapping type
- Cache unit conversion lookups

## Error Handling

- **Missing CSV Data**: Log warning, skip mapping or use defaults if required columns are empty
- **Invalid JSON**: Log error, skip mapping (Priority JSON, I/O Mapping Config, Function Parameters)
- **Circular Dependencies**: Log error, fail generation
- **Missing Dependencies**: Log warning, process anyway (may fail at runtime)

---

# Related Documentation

- [**Mapping Fields Database README**](../3-mapping-fields/README.md): Database schema and column definitions (single source for YAML generation)
- [**Example Generated YAML**](scripts/navixy-mapping.yaml): Complete example of generated YAML configuration file
- [**Fleeti Fields Database**](../2-fleeti-fields/README.md): Reference source that populates Mapping Fields Database via Notion relations/rollups
- [**Provider Fields Database**](../1-provider-fields/README.md): Reference source that populates Mapping Fields Database via Notion relations/rollups

**Note:** Fleeti Fields and Provider Fields databases are reference sources used to populate the Mapping Fields Database. They are not directly accessed during YAML generation - all required data is already present in the Mapping Fields CSV via Notion rollups/relations.

---

**Last Updated:** 2025-01-16

**Status:** ✅ Specification