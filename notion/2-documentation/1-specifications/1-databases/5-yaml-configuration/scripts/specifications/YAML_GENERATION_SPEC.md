# YAML Configuration Generation Specification

**Status:** ✅ Active

## Overview

The `generate_yaml_config.py` script transforms Mapping Fields Database CSV exports (from Notion) into executable YAML configuration files for the telemetry transformation pipeline.

**Input:** `input/Mapping Fields (db) 12-18-25 copy.csv` (Notion export format)  
**Output:** `navixy-mapping.yaml` (provider-specific mapping configuration)

---

## Input Format

### CSV Source: Notion Export

The script reads from Notion CSV exports which have:
- **Different column order** than script-generated CSVs
- **Notion link format** in relation columns: `field_name (https://www.notion.so/...)`
- **JSON strings** in structured columns (e.g., Function Parameters)

### Key Columns

| Column | Description | Example |
|--------|-------------|---------|
| `Fleeti Field` | Field name (may include Notion link) | `location_latitude (https://...)` |
| `Function Parameters` | JSON parameter mapping | `{"fleeti": "location_heading"}` |
| `Dependencies` | Comma-separated (may include Notion links) | `location_latitude (https://...), location_longitude` |

---

## Processing Pipeline

### 1. CSV Reading & Normalization

```python
read_csv_file() → List[Dict]
```

- Reads CSV with `utf-8-sig` encoding (handles BOM)
- Normalizes column names (Notion exports have different names)
- Preserves all columns for compatibility

**Design Choice:** Normalize rather than require exact column names to handle Notion export variations.

### 2. Notion Link Extraction

```python
extract_field_name_from_notion_link(link_text) → str
```

**Pattern:** `field_name (https://www.notion.so/...)` → `field_name`

**Regex:** `^([^(]+)` - extracts text before first parenthesis

**Why:** Notion exports include full URLs in relation columns. We only need the field name for processing.

### 3. Function Parameter Parsing

```python
parse_function_parameters(params_str) → Dict[str, Any]
```

**Two Input Formats Supported:**

#### Format A: New Format (Direct)
```json
{"provider": "heading"}
{"fleeti": "location_heading"}
{"fleeti": ["location_latitude", "location_longitude"]}
```

#### Format B: Legacy Format (With Prefix)
```json
{"raw_lat": "provider:lat"}
{"heading": "location_heading"}
```

**Processing Logic:**

1. **Try JSON parsing** - Standard `json.loads()`
2. **Detect format** - Check if keys are `fleeti`/`provider` (new) or arbitrary names (legacy)
3. **Handle duplicate keys** - JSON doesn't support duplicates, so parse raw string with regex:
   ```python
   # Pattern: "fleeti": "value" (finds all occurrences)
   r'"fleeti"\s*:\s*"([^"]+)"'
   ```
4. **Convert to output structure:**
   - Single value → `{"fleeti": "location_heading"}`
   - Multiple values → `{"fleeti": ["location_latitude", "location_longitude"]}`

**Design Choices:**
- **Support duplicate keys:** Notion exports may have `{"fleeti": "val1", "fleeti": "val2"}` (invalid JSON). Regex parsing handles this.
- **Simple output structure:** Use `fleeti:` and `provider:` as top-level keys for clarity.
- **Backward compatible:** Legacy format with `provider:` prefix in values still works.

### 4. Dependency Parsing

```python
parse_dependencies(deps_str) → List[str]
```

**Input:** `"location_latitude (https://...), location_longitude"`  
**Output:** `["location_latitude", "location_longitude"]`

Extracts field names from Notion links and splits by comma.

### 5. Topological Sort

```python
topological_sort(mappings) → List[Dict]
```

**Order:**
1. Direct mappings (no dependencies)
2. Prioritized mappings (no dependencies)
3. Calculated/Transformed (with dependencies, sorted by dependency graph)

**Why:** Ensures dependencies are available before calculated fields are processed.

### 6. YAML Generation

**Mapping Types:**

#### Direct Mapping
```yaml
location_latitude:
  type: direct
  source: lat
  data_type: number
  unit: degrees
```

#### Prioritized Mapping
```yaml
location_precision_hdop:
  type: prioritized
  sources:
    - priority: 1
      field: hdop
      path: hdop
```

#### Calculated Mapping
```yaml
location_cardinal_direction:
  type: calculated
  calculation_type: function_reference
  function: derive_cardinal_direction
  parameters:
    provider: heading  # or fleeti: location_heading
  dependencies:
    - location_heading
```

---

## Parameter Format Specification

### CSV Format

**Single Parameter:**
```json
{"provider": "heading"}
{"fleeti": "location_heading"}
```

**Multiple Parameters (Array Format - Recommended):**
```json
{"fleeti": ["location_latitude", "location_longitude"]}
```

**Multiple Parameters (Duplicate Keys - Supported but not recommended):**
```json
{"fleeti": "location_latitude", "fleeti": "location_longitude"}
```
*Note: JSON parsers only keep last value, so script uses regex to find all occurrences.*

### YAML Output Format

**Single Parameter:**
```yaml
parameters:
  fleeti: location_heading
  # or
  provider: heading
```

**Multiple Parameters:**
```yaml
parameters:
  fleeti:
    - location_latitude
    - location_longitude
```

**Mixed Sources:**
```yaml
parameters:
  fleeti:
    - location_latitude
  provider: heading
```

### Source Identification

- **`fleeti:`** = Fleeti field (transformed/calculated data)
- **`provider:`** = Provider field (raw provider data)

**Default:** If no prefix, assume Fleeti field.

---

## Key Design Decisions

### 1. Why `fleeti:` and `provider:` as Keys?

**Problem:** Original format used parameter names (`heading: location_heading`) which didn't indicate data source.

**Solution:** Use `fleeti:` and `provider:` as keys to clearly indicate where parameters come from.

**Benefit:** Developers immediately see if function uses transformed (Fleeti) or raw (provider) data.

### 2. Why Support Duplicate Keys?

**Problem:** Notion exports may generate invalid JSON with duplicate keys.

**Solution:** Parse raw string with regex to find all occurrences before JSON parsing.

**Trade-off:** More complex parsing, but handles real-world Notion export quirks.

### 3. Why Notion Link Extraction?

**Problem:** Notion exports include full URLs in relation columns.

**Solution:** Extract field name before first parenthesis using regex.

**Benefit:** Works with both Notion exports and plain field names.

### 4. Why Topological Sort?

**Problem:** Calculated fields depend on other fields being processed first.

**Solution:** Sort mappings by dependency order (direct → prioritized → calculated).

**Benefit:** Ensures correct evaluation order, prevents dependency errors.

---

## Code Structure

```
generate_yaml_config.py
├── Input/Output
│   ├── read_csv_file() - Handles Notion export format
│   └── main() - Orchestrates generation
├── Parsing
│   ├── extract_field_name_from_notion_link() - Notion link extraction
│   ├── parse_function_parameters() - Parameter format conversion
│   ├── parse_dependencies() - Dependency list parsing
│   └── parse_priority_json() - Priority chain parsing
├── Processing
│   ├── topological_sort() - Dependency ordering
│   └── build_dependency_graph() - Graph construction
└── Generation
    ├── generate_direct_mapping() - Direct field mapping
    ├── generate_prioritized_mapping() - Priority chain mapping
    ├── generate_calculated_mapping() - Calculated field mapping
    └── generate_yaml_entry() - Entry point dispatcher
```

---

## Usage

```bash
cd notion/2-documentation/1-specifications/1-databases/5-yaml-configuration/scripts
python generate_yaml_config.py
```

**Prerequisites:**
- CSV file in `input/` folder
- Python 3.7+ with `pyyaml` installed

---

## Related Documentation

- **Mapping Fields Database:** `../../3-mapping-fields/README.md`
- **Fleeti Fields Database:** `../../2-fleeti-fields/README.md`
- **Provider Fields Database:** `../../1-provider-fields/README.md`

