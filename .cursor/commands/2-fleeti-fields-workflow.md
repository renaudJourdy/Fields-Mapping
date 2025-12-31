# Fleeti Fields Creation Workflow

This command documents the complete workflow for creating new Fleeti fields from initial design to final YAML configuration. Use this command to understand the workflow context when the user indicates they are at a specific step.

**When to use**: When the user is working on creating new Fleeti fields and indicates which step of the workflow they are currently at. This command provides context about the entire process and what has been completed at each stage.

## Workflow Overview

The goal is to add new Fleeti fields that serve the Fleeti One application and troubleshooting purposes, creating mapping rules in the YAML configuration file. The workflow transforms Fleeti field designs into production-ready YAML configurations through multiple stages of collaboration, refinement, and database integration.

### Reference Document (Not Source of Truth)

**Location**: `notion/2-documentation/1-specifications/1-databases/2-fleeti-fields/workspace/fleeti-telemetry-schema-specification.md`

- This document is a **reference only**, not the single source of truth
- Used to generate a list of potential Fleeti fields based on provider field analysis
- Provides big-picture understanding of the Fleeti Telemetry structure
- There may be differences between this document and what's actually implemented in databases/YAML
- **Single source of truth**: Notion databases and YAML configuration files

## Workflow Steps

### Step 1: Listing & Selection

**Objective**: Create a draft CSV file listing Fleeti fields to be created and mapped.

**Activities**:
- User extracts potential Fleeti fields from the reference specification document
- User selects which provider fields should be mapped to each Fleeti field
- User creates/modifies a CSV file in the workspace (typically in `notion/2-documentation/1-specifications/1-databases/2-fleeti-fields/workspace/`)
- CSV contains: Field names, provider fields to map, initial notes

**Output**: Fleeti Fields Draft CSV file

**When user says "we're at step 1"**: User is selecting fields and provider mappings, needs help organizing the CSV structure.

---

### Step 2: AI Collaboration for Design

**Objective**: Define computation approach text and computation structure JSON for each Fleeti field.

**Activities**:
- User discusses (speech-to-text or chat) the computation approach with AI
- User explains: why specific provider fields are selected, how they should be prioritized, transformation logic
- AI helps create/refine:
  - **Computation Approach** text: Developer-friendly description explaining the mapping logic, field descriptions, business context
  - **Computation Structure JSON**: Structured JSON that will generate the YAML configuration

**Key Guidelines for Computation Approach**:
- **Purpose**: Complementary information for developers, not duplicate of YAML/JSON
- **Balance**: Concise but informative - avoid redundancy with YAML/JSON, but provide necessary context
- **Content**: 
  - Explain business logic and priorities (why certain fields are preferred)
  - Describe provider field meanings (especially for AVL_IO fields with IDs)
  - Note unit conversions, offset handling, validation requirements
  - For calculated fields with functions:
    - **Simple functions**: Include pseudo-code explaining function behavior
    - **Complex functions**: Reference Notion documentation instead of including extensive pseudo-code (see Step 5 for function implementation)
- **Length**: Keep concise - too much text is painful to read, but include relevant context not available elsewhere

**Key Guidelines for Computation Structure JSON**:
- Must generate the exact YAML configuration when processed
- Format should align with YAML generation script requirements
- Contains all necessary structure for prioritized mappings, calculated fields, unit conversions, etc.

**Output**: Computation Approach text + Computation Structure JSON for each field (in draft form, not yet finalized)

**When user says "we're at step 2"**: User is working with AI to refine computation approach text and JSON structure, needs help creating clear, concise descriptions.

---

### Step 3: YAML Draft Generation

**Objective**: Generate an initial draft YAML configuration file from the computation structure JSON.

**Activities**:
- Generate YAML configuration file based on computation structure JSON
- This is a **draft/intermediate** file for review and fixing
- YAML structure should follow:
  - **Reference specification**: `yaml-mapping-reference.yaml` - Rules, optimization guidelines, and examples
  - **Existing implementations**: YAML files in `notion/2-documentation/1-specifications/1-databases/5-yaml-configuration/output/` - Most up-to-date actual implementations showing real-world patterns and conventions
- Used to visualize and validate the mapping structure
- AI should reference existing YAML files to maintain consistency with already-implemented mappings

**Output**: Draft YAML configuration file (e.g., `navixy-mapping-YYYY-MM-DD-draft.yaml`)

**When user says "we're at step 3"**: User wants to generate or review the draft YAML, needs help with YAML structure or mapping rules.

---

### Step 4: YAML Refinement

**Objective**: Refine the draft YAML configuration file until it matches the desired final structure.

**Activities**:
- User and AI review the draft YAML together
- Make adjustments to mapping structure, priorities, field paths
- Ensure YAML follows optimization rules from `yaml-mapping-reference.yaml`
- Reference existing YAML files in output folder for consistency with implemented patterns
- Agree on final YAML structure

**Output**: Refined/finalized YAML configuration file

**When user says "we're at step 4"**: User is refining YAML structure, needs help with optimization, priorities, or mapping rules.

---

### Step 5: Complex Function Implementation

**Objective**: Create implementation files for complex calculated fields that require extensive logic.

**Activities**:
- Identify which Fleeti fields require complex function implementations (too complex for pseudo-code in computation approach)
- Create function implementation files in appropriate workspace subdirectory (e.g., `workspace/asset-details/functions/`, `workspace/asset-list/functions/`)
- Function files should contain:
  - Complete implementation code (JavaScript or appropriate language)
  - Documentation and comments explaining the logic
  - Provider field correspondence matrices if needed
  - Helper functions for validation, unit conversion, etc.
- Reference example: `workspace/asset-list/functions/derive_sensors_environment.js`
- Common complex functions:
  - `derive_sensors_environment` (already implemented - example)
  - `derive_sensors_magnet` (for asset-details)
  - `derive_fuel_levels` (for asset-details)
- Update computation approach text to reference these function implementations in Notion documentation instead of including all pseudo-code

**Output**: Function implementation files ready for Notion documentation

**When user says "we're at step 5"**: User needs to create or refine complex function implementations, needs help with function structure, logic, or following patterns from existing implementations.

---

### Step 6: Computation Structure File Creation

**Objective**: Create markdown file containing both computation approach and computation structure JSON.

**Activities**:
- Once YAML is refined and agreed upon, create markdown file
- File contains:
  - **Computation Approach**: Final text description
  - **Computation Structure JSON**: JSON that will generate the agreed-upon YAML
- File format: Each field has a section with Field Path, Computation Approach (text), and JSON code block
- Example location: `notion/2-documentation/1-specifications/1-databases/2-fleeti-fields/workspace/asset-details/navixy-mapping-YYYY-MM-DD-computation-structure.md`

**Output**: Markdown file with computation approach + computation structure JSON

**When user says "we're at step 6"**: User wants to create or validate the computation structure file, needs help formatting or ensuring JSON matches YAML.

---

### Step 7: Import to Notion - Fleeti Fields

**Objective**: Import computation approach and JSON into Notion Fleeti Fields database.

**Activities**:
- User copies computation approach text → Fleeti Fields CSV
- User copies computation structure JSON → Fleeti Fields CSV
- Import CSV to Notion Fleeti Fields database
- Fill remaining columns in Notion:
  - Set up relationships with Provider Fields database
  - Fill missing columns (priority, category, field path, etc.)
  - Complete all required metadata

**Output**: Updated Notion Fleeti Fields database with new fields

**When user says "we're at step 7"**: User is importing to Notion, may need help understanding which columns to fill or relationships to establish.

---

### Step 8: Export & Generate Mapping Fields

**Objective**: Generate Mapping Fields CSV from exported Fleeti Fields.

**Activities**:
- Export Fleeti Fields database from Notion → `Fleeti Fields (db) YYYY-MM-DD.csv`
- Run script to generate Mapping Fields CSV (typically in `notion/2-documentation/1-specifications/1-databases/3-mapping-fields/scripts/`)
- Script creates mapping field entries for new Fleeti fields

**Output**: Mapping Fields CSV file ready for Notion import

**When user says "we're at step 8"**: User needs to run generation script, may need help with script execution or troubleshooting.

---

### Step 9: Import to Notion - Mapping Fields

**Objective**: Import Mapping Fields CSV and complete relationships.

**Activities**:
- Import Mapping Fields CSV to Notion Mapping Fields database
- Set up relationships:
  - Link each Mapping Field to corresponding Fleeti Field (database relation)
  - Link to Provider Fields database
- Fill remaining columns (configuration level, status, version, etc.)
- Complete all mapping metadata

**Output**: Updated Notion Mapping Fields database with new mappings

**When user says "we're at step 9"**: User is importing mapping fields, may need help with relationships or column completion.

---

### Step 10: Export & Generate Final YAML

**Objective**: Generate final YAML configuration file from exported Mapping Fields.

**Activities**:
- Export Mapping Fields database from Notion → `Mapping Fields (db) YYYY-MM-DD.csv`
- Run YAML generation script (typically `notion/2-documentation/1-specifications/1-databases/5-yaml-configuration/scripts/generate_yaml_from_csv.py`)
- Script reads computation structure JSON from CSV and generates YAML
- Output: Final YAML configuration file (e.g., `navixy-mapping-YYYY-MM-DD.yaml`)

**Output**: Final YAML configuration file ready for validation

**When user says "we're at step 10"**: User is generating final YAML, may need help with script execution or verifying output matches expectations.

---

### Step 11: Validation

**Objective**: Validate the generated YAML configuration file structure.

**Activities**:
- Review the generated YAML configuration file
- Run validation script (typically `notion/2-documentation/1-specifications/1-databases/5-yaml-configuration/scripts/validate_yaml.py`)
- Ensure YAML structure is correct, no syntax errors, follows optimization rules
- Fix any issues if validation fails

**Output**: Validated YAML configuration file ready for deployment

**When user says "we're at step 11"**: User is validating YAML, may need help fixing validation errors or understanding structure issues.

---

## Key Files and Locations

### Workspace Files
- **Draft CSV**: `notion/2-documentation/1-specifications/1-databases/2-fleeti-fields/workspace/`
- **Computation Structure File**: `notion/2-documentation/1-specifications/1-databases/2-fleeti-fields/workspace/asset-details/`
- **Function Implementations**: `notion/2-documentation/1-specifications/1-databases/2-fleeti-fields/workspace/*/functions/` - Complex function implementations (e.g., `derive_sensors_environment.js`)
- **Reference Specification**: `notion/2-documentation/1-specifications/1-databases/2-fleeti-fields/workspace/fleeti-telemetry-schema-specification.md`

### Export Files
- **Fleeti Fields Export**: `notion/2-documentation/1-specifications/1-databases/2-fleeti-fields/export/Fleeti Fields (db) YYYY-MM-DD.csv`
- **Mapping Fields Export**: `notion/2-documentation/1-specifications/1-databases/3-mapping-fields/export/Mapping Fields (db) YYYY-MM-DD.csv`

### YAML Files
- **YAML Reference**: `notion/2-documentation/1-specifications/1-databases/5-yaml-configuration/yaml-mapping-reference.yaml` - Rules, optimization guidelines, and examples
- **Generated YAML (Output Folder)**: `notion/2-documentation/1-specifications/1-databases/5-yaml-configuration/output/navixy-mapping-YYYY-MM-DD.yaml` - Most up-to-date actual implementations showing real-world patterns and conventions (use for consistency when generating new YAML)

### Scripts
- **Generate Mapping Fields CSV**: `notion/2-documentation/1-specifications/1-databases/3-mapping-fields/scripts/generate_mapping_fields_csv.py`
- **Generate YAML from CSV**: `notion/2-documentation/1-specifications/1-databases/5-yaml-configuration/scripts/generate_yaml_from_csv.py`
- **Validate YAML**: `notion/2-documentation/1-specifications/1-databases/5-yaml-configuration/scripts/validate_yaml.py`

## Important Principles

### Computation Approach Guidelines

1. **Complementary, Not Duplicate**: Provide information not already in YAML/JSON
2. **Developer-Friendly**: Explain context, business logic, provider field meanings
3. **Concise**: Balance brevity with necessary context - avoid redundancy but include important details
4. **Function Documentation**: 
   - **Simple functions**: Include pseudo-code explaining function behavior
   - **Complex functions**: Reference Notion documentation where full implementation is documented (see Step 5)
5. **Provider Field Context**: Explain AVL_IO fields and their purposes (not just IDs)

### Computation Structure JSON

1. **YAML Generation**: JSON must generate the exact YAML configuration when processed
2. **Structure Match**: Format should align with YAML generation script requirements
3. **Completeness**: Include all necessary information (priorities, units, function parameters, etc.)

### Workflow Flexibility

- Steps 1-5: Iterative design phase (can loop back to refine)
- Step 6: Documentation preparation (computation structure file creation)
- Steps 7-9: Notion database integration (user handles manually, AI provides guidance)
- Steps 10-11: Automation and validation (scripts generate final output)

## How to Use This Command

### Initial Response (No Step Specified)

**When the command is run without specifying a step number**: The AI should acknowledge understanding and provide a simple list of all workflow steps (section headers) for easy reference. This helps the user see all steps at a glance without reading the entire file.

**Example response format**:
```
I understand the Fleeti Fields Creation Workflow. Here are the workflow steps:

1. Listing & Selection
2. AI Collaboration for Design
3. YAML Draft Generation
4. YAML Refinement
5. Complex Function Implementation
6. Computation Structure File Creation
7. Import to Notion - Fleeti Fields
8. Export & Generate Mapping Fields
9. Import to Notion - Mapping Fields
10. Export & Generate Final YAML
11. Validation

Which step are you working on?
```

### When User Indicates a Specific Step

1. **Understand Context**: Review what has been completed in previous steps
2. **Identify Current Needs**: Understand what the user needs help with at the current step
3. **Provide Guidance**: Offer relevant assistance based on the step:
   - Steps 1-2: Help with field selection, computation approach writing, JSON structure
   - Steps 3-4: Help with YAML generation and refinement
   - Step 5: Help with complex function implementation, following patterns from existing functions
   - Step 6: Help with markdown file formatting and JSON validation
   - Steps 7-9: Provide guidance on Notion database structure (user handles import/export)
   - Steps 10-11: Help with script execution and validation

4. **Remember**: Each step builds on previous steps - don't repeat work that's already been done

## Example Usage

**User**: "I'm at step 2, working on the computation approach for `engine_hours_value`. Can you help refine it?"

**AI Response**: Should understand that:
- Step 1 (listing) is complete - field is selected
- Current focus: Creating computation approach text and JSON
- Need to help create concise, developer-friendly description
- May need to add pseudo-code if functions are involved
- Should avoid duplicating information that will be in YAML

**User**: "We're at step 4, the YAML looks mostly good but I want to adjust priorities."

**AI Response**: Should understand that:
- Steps 1-3 are complete - have computation approach, JSON, and draft YAML
- Current focus: Refining YAML structure
- Need to help adjust priorities, ensure optimization rules are followed
- Final YAML will be used in step 6 to generate computation structure file

**User**: "I'm at step 5, need to create the magnet sensors function."

**AI Response**: Should understand that:
- Steps 1-4 are complete - YAML is finalized
- Current focus: Creating complex function implementation
- Need to help create function following patterns from `derive_sensors_environment.js`
- Function will be documented in Notion and referenced in computation approach

