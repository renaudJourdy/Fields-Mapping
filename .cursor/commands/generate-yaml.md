Generate YAML Configuration from Mapping Fields CSV
Overview
Create a Python script that reads the Mapping Fields CSV export and generates an optimized YAML configuration file following the specifications in yaml-mapping-reference.yaml. The script converts Computation Structure JSON to YAML format, applies optimization rules, and adds Computation Approach as comments.

Input
CSV File: Most recent file in notion/2-documentation/1-specifications/1-databases/3-mapping-fields/export/
Columns used: Fleeti Field, Fleeti Field Path, Computation Structure JSON, Computation Approach, Mapping Type, Fleeti Unit, Provider Field Unit, Fleeti Data Type, Error Handling, Provider, Status
Filter: Only process rows where Status = "planned" or Status = "active" (skip other statuses)
Output
YAML File: notion/2-documentation/1-specifications/1-databases/5-yaml-configuration/output/navixy-mapping-YYYY-MM-DD.yaml
Format: Optimized YAML following yaml-mapping-reference.yaml specifications
Structure: version, provider, mappings (dictionary of Fleeti fields)
Key Processing Steps
1. CSV Reading and Parsing
Find most recent CSV file in export folder (pattern: Mapping Fields (db) *.csv)
Read CSV with UTF-8-sig encoding (handle BOM)
Parse multi-line JSON fields correctly
Extract field name from "Fleeti Field" column (remove Notion links if present)
2. JSON to YAML Conversion
Parse Computation Structure JSON column (handle escaped quotes, multi-line)
Convert JSON structure to YAML following optimization rules:
Rule 1: Keep top-level type (always required)
Rule 2: Omit type: direct in sources (default)
Rule 3: Omit provider in sources when matches top-level provider
Rule 4: Omit priority for single-source mappings
Rule 5: Omit description fields (use comments instead)
Rule 6: Omit dependencies when redundant with parameters.fleeti
Rule 7: Omit source_type (inferred from context)
Rule 8: Add unit at both source level (from "Provider Field Unit") and top level (from "Fleeti Unit")
3. Unit Handling
CRITICAL: Units must ALWAYS be included at both source and top level for direct and prioritized mappings, even for unitless fields (use "none").

Source-level units (for direct and prioritized mappings):
- For each source in direct/prioritized mappings:
  - Use "Provider Field Unit" column value if present and not empty
  - If empty, use "Fleeti Unit" as fallback
  - If still empty, empty string, or "none", use unit: none (DO NOT omit - always include unit field)
  - Apply to ALL direct provider sources (not just prioritized mappings)
  - For calculated sources in prioritized mappings: omit unit (calculated sources don't have provider units)

Top-level units (for all mapping types):
- Direct mappings: ALWAYS include unit field
  - Use "Fleeti Unit" column value if present and not empty
  - If empty, empty string, or "none", use unit: none (DO NOT omit)
- Prioritized mappings: ALWAYS include unit field
  - Use "Fleeti Unit" column value if present and not empty
  - If empty, empty string, or "none", use unit: none (DO NOT omit)
- Calculated mappings: Include unit field ONLY if data_type is number
  - Use "Fleeti Unit" column value if present and not empty
  - If empty, empty string, or "none", use unit: none
  - Omit unit field if data_type is string, boolean, or datetime (unitless types)
- Transformed/I/O mapped: Include unit field if data_type is number
  - Use "Fleeti Unit" column value if present and not empty
  - If empty, empty string, or "none", use unit: none
  - Omit unit field if data_type is string, boolean, or datetime

Unit determination logic:
- Normalize empty strings, None, null, "none", "None", "NONE" → use "none"
- For numeric data types: always include unit (even if "none" for unitless fields like ratios, counts, enums)
- For boolean/string/datetime: omit unit at top level (these are inherently unitless)
- Unitless numeric fields (HDOP, PDOP, fix quality codes, satellite counts, boolean 0/1): use unit: none

Examples:
- location_precision_hdop (number, unitless): unit: none at source and top level
- location_precision_satellites (number, count): unit: none or unit: count at source and top level
- speed (number, km/h): unit: km/h at all source levels and top level
- is_moving_value (number, boolean 0/1): unit: none at source and top level
- location_cardinal_direction (string): omit unit at top level (string is unitless)
4. Field Name Extraction
Use "Fleeti Field" column value directly as YAML key
Remove Notion links if present (pattern: field_name (https://...) → field_name)
Example: location_latitude (https://...) → location_latitude:
5. Additional Fields
Add data_type from "Fleeti Data Type" column
Add error_handling from "Error Handling" column (default: return_null if empty)
Add # Field Path: {Fleeti Field Path} comment at the end (after all properties)
Add # Computation Approach: comment followed by multi-line Computation Approach text at the end (after all properties)
6. YAML Structure Generation
Direct mappings: Single source, no priority
Prioritized mappings: Multiple sources with priorities
Calculated mappings: Function reference with parameters
Transformed mappings: Transformation rule with service fields
I/O mapped: Default source with installation metadata
7. Output Formatting
Use PyYAML library for YAML generation
Set default_flow_style=False for block style
Set sort_keys=False to preserve order
Use allow_unicode=True for proper encoding
Add proper indentation (2 spaces)
Format comments with proper YAML comment syntax (#)
Implementation Details
File Structure
notion/2-documentation/1-specifications/1-databases/5-yaml-configuration/
├── scripts/
│   └── generate_yaml_from_csv.py  # New script
└── output/
    └── navixy-mapping-YYYY-MM-DD.yaml  # Generated output


Dependencies
csv (standard library)
json (standard library)
yaml (PyYAML library)
pathlib (standard library)
datetime (standard library)
Error Handling
Handle missing CSV files gracefully
Handle invalid JSON in Computation Structure JSON column
Handle missing required columns
Skip rows with invalid data (log warnings)
Handle empty or null values appropriately
Validation
Verify all required columns exist
Validate JSON structure before conversion
Ensure YAML output is valid (can be parsed back)
Check that optimization rules are applied correctly
CRITICAL: Validate unit inclusion:
- All direct mappings must have unit at source level AND top level
- All prioritized mappings must have unit at each source level AND top level
- All calculated mappings with data_type: number must have unit at top level
- Unit field should never be omitted for numeric fields (use "none" for unitless)
- Verify no missing units in prioritized mappings (common mistake)
Example Output Structure
version: "1.0.0"
provider: "navixy"

mappings:
  location_latitude:
    type: direct
    sources:
      - field: lat
        path: lat
        unit: degrees
    unit: degrees
    data_type: number
    error_handling: return_null
    # Field Path: location.latitude
    # Computation Approach: Direct mapping from Navixy: lat (path: lat) - Latitude in decimal degrees from Navixy

  location_precision_hdop:
    type: prioritized
    sources:
      - priority: 1
        field: hdop
        path: hdop
        unit: none
      - priority: 2
        field: avl_io_182
        path: params.avl_io_182
        unit: none
    unit: none
    data_type: number
    error_handling: use_fallback
    # Field Path: location.precision.hdop
    # Computation Approach: Prioritized: Navixy hdop (path: hdop, priority 1), then Navixy avl_io_182 (path: params.avl_io_182, priority 2) - Horizontal Dilution of Precision

  location_precision_fix_quality:
    type: direct
    sources:
      - field: avl_io_69
        path: params.avl_io_69
        unit: none
    unit: none
    data_type: number
    error_handling: return_null
    # Field Path: location.precision.fix_quality
    # Computation Approach: Direct mapping from Navixy: avl_io_69 (path: params.avl_io_69) - GNSS Status code

  speed:
    type: prioritized
    sources:
      - priority: 1
        field: can_speed
        path: params.can_speed
        unit: km/h
      - priority: 2
        field: obd_speed
        path: params.obd_speed
        unit: km/h
    unit: km/h
    data_type: number
    error_handling: return_null
    # Field Path: motion.speed.value
    # Computation Approach: Prioritized: Navixy can_speed (path: params.can_speed, priority 1), then Navixy obd_speed (path: params.obd_speed, priority 2)

  location_cardinal_direction:
    type: calculated
    calculation_type: function_reference
    function: derive_cardinal_direction
    parameters:
      fleeti:
        - location_heading
    data_type: string
    error_handling: return_null
    # Field Path: location.cardinal_direction
    # Computation Approach: Calculated: derive from location_heading using derive_cardinal_direction function...


Testing Considerations
Test with actual CSV export file
Verify optimization rules are applied correctly
Test with different mapping types (direct, prioritized, calculated, etc.)
Test unit handling:
  - Direct mappings with units (degrees, km/h, etc.)
  - Direct mappings with empty/unitless units (should use unit: none)
  - Prioritized mappings with units at all source levels AND top level
  - Prioritized mappings with mixed units (verify all sources have units)
  - Calculated mappings with number data_type (should have top-level unit)
  - Calculated mappings with string/boolean data_type (should omit top-level unit)
  - Verify speed mapping has top-level unit (common missing case)
  - Verify HDOP/PDOP mappings have unit: none at all levels
Test with missing units, empty fields (should default to unit: none for numeric fields)
Verify multi-line Computation Approach is formatted correctly