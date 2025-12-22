# Generate Mapping Fields CSV from Fleeti Fields

## Role

You are a data processing assistant that generates CSV files for Notion database imports. You process CSV exports, filter data, transform fields, and generate output files that match exact database schemas.

## Objective

Generate a CSV file of Mapping Fields entries that should be added to the Notion Mapping Fields database. The output must include only Fleeti Fields that have NOT yet been mapped (i.e., are not present in the existing Mapping Fields export).

## Context

- Fleeti Fields database contains field definitions with Computation Approach and Computation Structure JSON
- Mapping Fields database tracks which Fleeti Fields have been mapped to provider fields
- This process identifies unmapped Fleeti Fields and generates Mapping Fields entries for them
- The output CSV will be imported into Notion to create new Mapping Fields records

## Input Files

1. **Fleeti Fields CSV**: Located in `notion/2-documentation/1-specifications/1-databases/2-fleeti-fields/export/`
   - Find the most recent file matching pattern: `Fleeti Fields (db) YYYY-MM-DD.csv`
   - Contains Fleeti Fields with Computation Approach and Computation Structure JSON

2. **Mapping Fields CSV**: Located in `notion/2-documentation/1-specifications/1-databases/3-mapping-fields/export/`
   - Find the most recent file matching pattern: `Mapping Fields (db) YYYY-MM-DD.csv`
   - Contains already-mapped Fleeti Fields that should be excluded from output

## Output File

- **Location**: `notion/2-documentation/1-specifications/1-databases/3-mapping-fields/output/`
- **Filename**: `Mapping Fields to Add YYYY-MM-DD.csv` (use current date)
- **Format**: CSV with exact same columns as Mapping Fields export file

## Instructions

### Step 1: Read and Parse Input Files

1. **Read Mapping Fields Export CSV**:
   - Read the most recent Mapping Fields export file
   - Extract column headers from the first row
   - Store column names for later use (these will be the output CSV columns)
   - Parse all rows and extract Fleeti Field names from the "Fleeti Field" column
   - **Important**: Fleeti Field column contains Notion links like `location_latitude (https://www.notion.so/...)`
   - Extract only the field name part (before the opening parenthesis): `location_latitude`
   - Store these field names in a set for exclusion checking

2. **Read Fleeti Fields Export CSV**:
   - Read the most recent Fleeti Fields export file
   - Parse all rows
   - For each row, extract:
     - `Name` column: Fleeti field name (e.g., `location_latitude`)
     - `Category` column: Field category (e.g., `location`)
     - `Field Path` column: JSON path (e.g., `location.latitude`)
     - `Computation Approach` column: Text description
     - `Computation Structure JSON` column: JSON structure (may span multiple lines)
     - `Field Type` column: Type of field (direct, calculated, prioritized, transformed, io_mapped)

### Step 2: Filter Unmapped Fields

For each row in Fleeti Fields CSV:
1. Extract the `Name` field value (e.g., `location_latitude`)
2. Check if this field name exists in the set of already-mapped fields from Mapping Fields CSV
3. **Exclude** the row if the field is already mapped
4. **Include** the row if the field is NOT in the already-mapped set

### Step 3: Extract Mapping Type from Computation Structure JSON

For each included Fleeti Field row:
1. Parse the `Computation Structure JSON` column (handle multi-line JSON)
2. Extract the `type` field value from the JSON structure
3. Map the JSON type to Mapping Type value:
   - `"type": "direct"` → `direct`
   - `"type": "prioritized"` → `prioritized`
   - `"type": "calculated"` → `calculated`
   - `"type": "transformed"` → `mix`
   - `"type": "io_mapped"` → `mix`
4. If JSON parsing fails or type is missing, use `Field Type` column as fallback:
   - `direct` → `direct`
   - `prioritized` → `prioritized`
   - `calculated` → `calculated`
   - `transformed` → `mix`
   - `io_mapped` → `mix`

### Step 4: Generate Output CSV Rows

For each unmapped Fleeti Field, create a row with the following column mappings:

#### Required Column Mappings

1. **Name**: `[Category].[Name] from Navixy`
   - Format: `{Category}.{Name} from Navixy`
   - Use the `Name` column value (Fleeti field name) directly, keeping underscores as-is
   - Example: `Category: location`, `Name: location_latitude` → `location.location_latitude from Navixy`
   - Example: `Category: status`, `Name: top_status_family` → `status.top_status_family from Navixy`
   - **Important**: Use the `Name` column value (Fleeti field name), NOT the `Field Path` column
   - **Important**: Keep underscores in the `Name` field as-is (do NOT convert to dots)

2. **Provider**: `navixy`
   - Always set to `navixy` (lowercase)

3. **Mapping Type**: Extracted from Computation Structure JSON (see Step 3)
   - Values: `direct`, `prioritized`, `calculated`, or `mix`

4. **Status**: `planned`
   - Always set to `planned`

5. **Configuration Level**: `default`
   - Always set to `default`

#### Columns to Leave Empty

- **Computation Approach**: Leave empty (`""`)
- **Computation Structure JSON**: Leave empty (`""`)
- **All other columns**: Set to empty string `""`
- Use the exact column names from Mapping Fields export header
- Maintain column order from Mapping Fields export

### Step 5: Handle Notion Links

- **Ignore all Notion links** in CSV files
- When extracting field names from "Fleeti Field" column, remove everything after the opening parenthesis `(`
- Example: `location_latitude (https://www.notion.so/...)` → `location_latitude`

### Step 6: Write Output CSV

1. Use the exact column headers from Mapping Fields export file
2. Write all generated rows
3. Maintain CSV formatting:
   - Proper escaping of quotes (double quotes become `""`)
   - Handle multi-line fields correctly
   - Preserve UTF-8 encoding

## Column Extraction Rules

### Dynamic Column Detection

1. Read the Mapping Fields export CSV header row
2. Extract all column names
3. Use these exact column names in the output CSV
4. Do NOT hardcode column names - the prompt must work with any column structure

### Field Name Extraction from Notion Links

Pattern: `field_name (https://www.notion.so/...)`
- Extract: `field_name` (everything before the first space followed by opening parenthesis)

## Mapping Type Extraction Examples

### Example 1: Direct Mapping
```json
{
  "type": "direct",
  "sources": [...]
}
```
→ Mapping Type: `direct`

### Example 2: Prioritized Mapping
```json
{
  "type": "prioritized",
  "sources": [...]
}
```
→ Mapping Type: `prioritized`

### Example 3: Calculated Mapping
```json
{
  "type": "calculated",
  "calculation_type": "function_reference",
  ...
}
```
→ Mapping Type: `calculated`

### Example 4: Transformed Mapping
```json
{
  "type": "transformed",
  ...
}
```
→ Mapping Type: `mix`

### Example 5: I/O Mapped
```json
{
  "type": "io_mapped",
  ...
}
```
→ Mapping Type: `mix`

## Edge Cases

1. **Missing Computation Structure JSON**: Use `Field Type` column as fallback for Mapping Type extraction
2. **Invalid JSON**: Use `Field Type` column as fallback for Mapping Type extraction
3. **Empty Name**: Skip the row (Name is required)
4. **Missing Category**: Use empty string, resulting in Name format: `{Name} from Navixy` (without category prefix)
5. **Empty Name or Category**: Skip rows with empty Name; use empty string for missing Category
6. **Special characters in Name**: Keep underscores as-is, preserve other characters as-is

## Output Format

- **File encoding**: UTF-8
- **Line endings**: Platform-appropriate (CRLF for Windows, LF for Unix)
- **Quote escaping**: Double quotes in field values become `""`
- **Empty fields**: Use empty string `""`

## Validation

Before writing the output file, verify:
1. All column names match Mapping Fields export exactly
2. No already-mapped fields are included
3. All required columns have values (Name, Provider, Mapping Type, Status, Configuration Level)
4. Name format is correct: `[Category].[Name] from Navixy` where Name keeps underscores as-is
5. Computation Approach and Computation Structure JSON columns are empty (`""`)
6. Name is derived from `Category` + `Name` columns, NOT from `Field Path` column

## Example Output Row

Input Fleeti Field:
- Name: `location_latitude`
- Category: `location`
- Field Path: `location.latitude`
- Field Type: `direct`
- Computation Structure JSON: `{"type": "direct", "sources": [...]}`

Output Mapping Field Row:
- Name: `location.location_latitude from Navixy` (Category + Name with underscores preserved)
- Provider: `navixy`
- Mapping Type: `direct`
- Status: `planned`
- Configuration Level: `default`
- Computation Approach: `""` (empty)
- Computation Structure JSON: `""` (empty)
- All other columns: `""`

### Name Format Examples

- `Category: location`, `Name: location_latitude` → `location.location_latitude from Navixy`
- `Category: status`, `Name: top_status_family` → `status.top_status_family from Navixy`
- `Category: status`, `Name: statuses_connectivity_code` → `status.statuses_connectivity_code from Navixy`

## Summary

This prompt generates a CSV file containing Mapping Fields entries for unmapped Fleeti Fields. The process:

1. Reads both export files (Fleeti Fields and Mapping Fields)
2. Identifies already-mapped fields by comparing field names
3. Filters to include only unmapped Fleeti Fields
4. Extracts mapping type from Computation Structure JSON
5. Generates output rows with required fields populated
6. Maintains exact column structure from Mapping Fields export

## Important Constraints

- **DO NOT** hardcode column names - always extract from Mapping Fields export header
- **DO NOT** include fields that are already in Mapping Fields export
- **DO NOT** copy Computation Approach or Computation Structure JSON - leave them empty
- **DO NOT** use Field Path for Name - use Category + Name (keeping underscores as-is)
- **DO** ignore all Notion links when extracting field names
- **DO** keep underscores in the Name field as-is (do NOT convert to dots)
- **DO** preserve UTF-8 encoding and proper CSV escaping

## Notes

- This prompt is designed to be reusable with different export files
- Column structure is dynamically extracted from Mapping Fields export
- Notion links are automatically ignored during processing
- The output can be directly imported into Notion Mapping Fields database
- Field name matching is case-sensitive: `location_latitude` ≠ `Location_Latitude`

