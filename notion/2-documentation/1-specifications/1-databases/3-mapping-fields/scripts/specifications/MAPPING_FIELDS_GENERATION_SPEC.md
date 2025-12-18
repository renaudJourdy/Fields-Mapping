# Mapping Fields Generation Specification

**Status:** ✅ Active

## Overview

The `generate_mapping_fields.py` script transforms Fleeti Fields Database CSV exports (from Notion) into Mapping Fields Database entries. This script generates mapping rules that link provider fields to Fleeti fields, determining transformation logic, priorities, and calculation rules.

**Input:** `input/Fleeti Fields (db) 12-18-25.csv` (Notion export format)  
**Output:** `Mapping-Fields-Navixy-2025-01-16.csv` (provider-specific mapping configuration)

---

## Input Format

### CSV Source: Notion Export

The script reads from Notion CSV exports which have:
- **Notion link format** in relation columns: `field_name (https://www.notion.so/...)`
- **Comma-separated lists** with Notion links in relation columns
- **Computation Approach** column containing calculation logic
- **Dependencies** column with Notion links to other Fleeti fields

### Key Columns from Fleeti Fields CSV

| Column | Description | Example |
|--------|-------------|---------|
| `Name` | Fleeti field name (stable identifier) | `location_latitude` |
| `Field Path` | JSON path in Fleeti telemetry object | `location.latitude` |
| `Field Type` | Type of field | `direct`, `calculated` |
| `Computation Approach` | Calculation logic (for calculated fields) | `Derived from location.heading` |
| `Dependencies` | Related Fleeti fields (with Notion links) | `location_heading (https://...)` |
| `💽 Provider Field (db)` | Provider field(s) this maps from (with Notion links) | `lat (https://...)` |
| `Unit` | Fleeti field unit | `degrees`, `meters` |
| `Data Type` | Fleeti field data type | `number`, `string`, `datetime` |
| `Version Added` | Version when field was added | `1.0.0` |
| `Status` | Field status | `inactive` (used for filtering) |
| `Description` | Field description | `Latitude in decimal degrees` |

---

## Processing Pipeline

### 1. CSV Reading & Filtering

```python
read_csv_file() → List[Dict]
```

- Reads CSV with `utf-8-sig` encoding (handles BOM)
- Filters to only `inactive` Fleeti fields (active fields are already mapped)
- Creates lookup dictionary for dependency validation

**Design Choice:** Only process inactive fields to generate new mapping entries.

### 2. Notion Link Extraction

```python
extract_field_name_from_notion_link(link_text) → str
extract_field_names_from_notion_links(link_text) → List[str]
```

- Extracts field names from Notion link format: `field_name (https://...)`
- Handles comma-separated lists of Notion links
- Returns plain field names (no URLs)

**Design Choice:** Extract names only - output uses plain field names for easier manual editing.

### 3. Provider Field Path Inference

```python
infer_provider_field_path(provider_field_name) → str
```

- **Simple fields**: Use name as path (e.g., `lat` → `lat`)
- **AVL IO fields**: Add `params.` prefix (e.g., `avl_io_69` → `params.avl_io_69`)

**Design Choice:** Infer paths from field names since we don't have Provider Fields CSV. This is a general pattern, not hardcoded to match specific exports.

### 4. Mapping Type Determination

The script determines mapping type based on:
- **Field Type** from CSV (`direct` or `calculated`)
- **Number of Provider Fields**:
  - 0 provider fields + `calculated` → Calculated mapping
  - 1 provider field → Direct mapping
  - 2+ provider fields → Prioritized mapping

### 5. Priority Order Parsing

```python
parse_priority_order(computation_approach, provider_fields) → List[Tuple[int, str]]
```

- Parses `>` syntax from Computation Approach (e.g., `hdop>avl_io_182`)
- Matches priority fields with actual provider field names
- Falls back to provider field order if no priority specified

**Example:**
- Input: `hdop>avl_io_182` with provider fields `['hdop', 'avl_io_182']`
- Output: `[(1, 'hdop'), (2, 'avl_io_182')]`

### 6. Calculation Type Determination

```python
determine_calculation_type(computation_approach, fleeti_name) → str | None
```

- Returns `formula` for simple parseable mathematical expressions
- Returns `function_reference` for all other computation approaches (default)
- Returns `None` if computation approach is empty (invalid)

**Design Choice:** Default to `function_reference` for all calculated fields to enable pluggable backend functions.

### 7. Backend Function Name Extraction

```python
extract_backend_function_name(fleeti_name, fleeti_path, computation_approach, calculation_type) → str
```

- Infers function name from field name/path
- Removes category prefixes (`location_`, `motion_`, etc.)
- Adds `derive_` prefix
- **Example**: `location_cardinal_direction` → `derive_cardinal_direction`

**Design Choice:** Use consistent naming convention for backend function registry.

### 8. Function Parameters Generation

```python
extract_function_parameters(dependency_names, provider_field_names, computation_approach, calculation_type) → str
```

This is the most complex logic in the script. It generates the new format with `fleeti:`/`provider:` keys.

#### Logic Flow:

1. **Check for explicit provider field mentions** in computation approach
   - If computation mentions a provider field name directly, use provider

2. **Infer provider field from simple field names**
   - If computation mentions a simple word (e.g., "heading") that:
     - Matches the last part of a dependency (e.g., "location_heading" ends with "_heading")
     - Is NOT part of a dependency name (e.g., "latitude" in "location_latitude" is part of the name)
   - Then infer it as a provider field

3. **Default to Fleeti fields** from dependencies

#### Output Format:

- **Single Fleeti param**: `{"fleeti": "location_heading"}`
- **Multiple Fleeti params**: `{"fleeti": ["location_latitude", "location_longitude"]}`
- **Single provider param**: `{"provider": "heading"}`
- **Multiple provider params**: `{"provider": ["field1", "field2"]}`

**Design Choice:** Use `fleeti:`/`provider:` keys for clarity. Backend resolves Field Names to Field Paths at runtime.

### 9. Dependency Sorting

```python
get_dependency_depth(fleeti_field, all_fleeti_fields, visited) → int
```

- Calculates dependency depth for topological sort
- Ensures dependencies are processed before dependents
- Handles circular dependencies gracefully

**Design Choice:** Sort calculated mappings by dependency depth to ensure correct evaluation order.

### 10. Output Generation

- Matches exact column order from export CSV
- Uses plain field names (no Notion links) in output
- Leaves `💽 YAML Configurations (db)` empty (manual input)

---

## Mapping Type Details

### Direct Mapping

**Requirements:**
- 1 provider field
- Field Type: `direct`

**Generated Fields:**
- `Mapping Type`: `direct`
- `Provider Fields`: Single provider field name
- `Provider Field Paths`: Inferred path
- `Status`: `planned`
- `Configuration Level`: `default`
- `Version Added`: From CSV

### Prioritized Mapping

**Requirements:**
- 2+ provider fields
- Field Type: `direct` (but multiple sources)

**Generated Fields:**
- `Mapping Type`: `prioritized`
- `Provider Fields`: Comma-separated list
- `Provider Field Paths`: Comma-separated paths (no spaces)
- `Priority JSON`: Structured priority array
- `Error Handling`: `use_fallback` (default for prioritized)
- `Status`: `planned`
- `Configuration Level`: `default`
- `Version Added`: From CSV

### Calculated Mapping

**Requirements:**
- Field Type: `calculated`
- Computation Approach present
- Dependencies present (for `function_reference`)

**Generated Fields:**
- `Mapping Type`: `calculated`
- `Calculation Type`: `function_reference` (default) or `formula`
- `Computation Approach`: From CSV
- `Backend Function Name`: Inferred from field name
- `Function Parameters`: Generated with `fleeti:`/`provider:` format
- `Dependencies`: Comma-separated Field Names (not Field Paths)
- `Status`: `planned`
- `Configuration Level`: `default`
- `Version Added`: From CSV

---

## Design Decisions

### 1. No Hardcoded Behavior

- All data comes from Fleeti Fields CSV (except defaults like `Status: planned`)
- Logic is general and pattern-based, not specific to match exports
- `Version Added` is read from CSV, not hardcoded

### 2. Field Names vs. Field Paths

- **Field Names** (stable identifiers) are used in:
  - YAML keys
  - Dependencies
  - Function Parameters
- **Field Paths** are used for:
  - Reference/documentation only
  - Mapping Name generation

**Rationale:** Backend resolves Field Name → Field Path at runtime. This makes configurations resilient to Field Path changes.

### 3. Provider Field Path Inference

- General pattern: `avl_io_*` → `params.avl_io_*`
- Simple fields: use name as path
- No hardcoded mappings to specific fields

### 4. Function Parameters Format

- New format: `{"fleeti": "field_name"}` or `{"provider": "field_name"}`
- Supports both single values and arrays
- Clear distinction between Fleeti and provider field sources

### 5. Notion Link Handling

- **Input**: Extract field names from Notion links
- **Output**: Use plain field names (no links)
- **Exception**: `💽 YAML Configurations (db)` left empty for manual input

---

## Code Structure

### Main Functions

1. **`extract_field_name_from_notion_link()`**: Extracts single field name from Notion link
2. **`extract_field_names_from_notion_links()`**: Extracts multiple field names from comma-separated Notion links
3. **`infer_provider_field_path()`**: Infers provider field path from field name
4. **`parse_priority_order()`**: Parses priority order from computation approach
5. **`determine_calculation_type()`**: Determines if calculation is formula or function_reference
6. **`extract_backend_function_name()`**: Infers backend function name from field name/path
7. **`extract_function_parameters()`**: Generates function parameters with fleeti:/provider: format
8. **`get_dependency_depth()`**: Calculates dependency depth for topological sort

### Main Processing Loop

1. Read and filter Fleeti Fields CSV
2. For each inactive Fleeti field:
   - Extract provider fields from `💽 Provider Field (db)` column
   - Determine mapping type (direct/prioritized/calculated)
   - Generate mapping entry based on type
3. Sort calculated mappings by dependency depth
4. Write output CSV with exact column order

---

## Output Format

### Column Order

Matches export CSV exactly:
1. Name
2. Backend Function Name
3. Calculation Type
4. Computation Approach
5. Configuration Level
6. Default Value
7. Dependencies
8. Error Handling
9. Fleeti Data Type
10. Fleeti Field
11. Fleeti Field Path
12. Fleeti Unit
13. Function Parameters
14. I/O Mapping Config
15. Mapping Type
16. Notes
17. Priority JSON
18. Provider
19. Provider Field Paths
20. Provider Fields
21. Provider Unit
22. Service Integration
23. Status
24. Transformation Rule
25. Unit Conversion
26. Version Added
27. 💽 YAML Configurations (db)

### Example Output

**Direct Mapping:**
```csv
location.latitude from Navixy,,,,default,,,,number,location_latitude,location.latitude,degrees,,,direct,Direct mapping: Latitude in decimal degrees,,navixy,lat,lat,,,planned,,,1.0.0,
```

**Calculated Mapping:**
```csv
location.cardinal_direction from Navixy,derive_cardinal_direction,function_reference,"Derived from location.heading...",default,,location_heading,,string,location_cardinal_direction,location.cardinal_direction,none,"{""provider"": ""heading""}",,calculated,Calculated field: Cardinal direction,,navixy,,,,,planned,,,1.0.0,
```

---

## Error Handling

- Skips calculated fields without Computation Approach
- Skips function_reference fields without Dependencies
- Validates function name and parameters are present
- Handles circular dependencies in topological sort

---

## Future Improvements

1. Support for `transformed` and `io_mapped` mapping types
2. Better provider field path inference (if Provider Fields CSV becomes available)
3. Support for `formula` calculation type (currently defaults to `function_reference`)
4. Unit conversion rule generation (currently left empty)

