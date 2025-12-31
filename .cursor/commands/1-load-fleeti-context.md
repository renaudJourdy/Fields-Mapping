# Load Fleeti Telemetry Mapping Context

Load comprehensive project context for the Fleeti Telemetry Mapping system. This command automatically reads all relevant documentation, database exports, and configuration files to provide full context for new chat sessions.

**When to use**: Invoke this command at the start of a new chat session to automatically load all project context without manually attaching files.

## Instructions

1. **Read Overview & Vision Documents**: Read all markdown files in the `notion/1-overview-vision/` directory:
   - `README.md` - Overview of the section
   - `1-project-overview.md` - Project overview, current state, problem statement, goals
   - `2-objectives-goals.md` - Primary objectives, key requirements, success criteria
   - `3-architecture-overview.md` - System architecture, data flow, components, storage strategy
   - `4-key-concepts.md` - Terminology and fundamental concepts

2. **Read Database Export CSVs**: Read all CSV files in the following export directories:
   - **Provider Fields**: All CSV files in `notion/2-documentation/1-specifications/1-databases/1-provider-fields/export/`
     - Contains provider-specific telemetry fields (e.g., Navixy fields like `avl_io_*`, `can_*`, `obd_*`)
     - Files use date-based naming (e.g., `Provider Field (db) 12-23-25.csv`)
   - **Fleeti Fields**: All CSV files in `notion/2-documentation/1-specifications/1-databases/2-fleeti-fields/export/`
     - Contains unified Fleeti telemetry fields with computation approaches
     - Files use date-based naming (e.g., `Fleeti Fields (db) 12-23-25.csv`)
   - **Mapping Fields**: All CSV files in `notion/2-documentation/1-specifications/1-databases/3-mapping-fields/export/`
     - Contains mappings between provider fields and Fleeti fields
     - Files use date-based naming (e.g., `Mapping Fields (db) 12-23-25.csv`)

3. **Read YAML Configuration Files**: Read all YAML files in the YAML configuration directories:
   - **Reference Files**: All YAML files in `notion/2-documentation/1-specifications/1-databases/5-yaml-configuration/`
     - Includes `yaml-mapping-reference.yaml` - Authoritative specification for YAML structure and optimization rules
   - **Generated Mappings**: All YAML files in `notion/2-documentation/1-specifications/1-databases/5-yaml-configuration/output/`
     - Includes generated mapping files (e.g., `navixy-mapping-YYYY-MM-DD.yaml`)
     - Files use date-based naming

4. **File Reading Strategy**:
   - Use batch reads for efficiency (read multiple files in parallel when possible)
   - For large CSV files, summarize key information rather than including full content
   - Note the date-based naming pattern: files are named with export dates, so read all files in each directory

5. **Provide Structured Context Summary**: After reading all files, provide a comprehensive summary organized as follows:

## Context Summary Format

After reading all files, provide a structured summary with the following sections:

### Project Overview
- High-level summary of the Fleeti Telemetry Mapping project
- Current state and architecture
- Primary objectives and vision
- Key stakeholders and use cases

### Key Concepts
- Provider-agnostic vs. provider-specific terminology
- Fleeti Telemetry Format structure
- Field types (direct, prioritized, calculated, transformed, I/O mapped)
- Priority levels (P0-P3, T, BL, ?)
- Status families (Connectivity, Transit, Engine, Immobilization)
- Configuration hierarchy (default → customer → asset group → asset)

### Database Structure
- **Provider Fields Database**: Summary of provider-specific fields (e.g., ~340 Navixy fields)
  - Field naming patterns (avl_io_*, can_*, obd_*, etc.)
  - Availability levels (always, conditional, rare)
  - Data types and units
- **Fleeti Fields Database**: Summary of unified Fleeti telemetry fields
  - Field categories (location, metadata, status, power, io, motion, sensors)
  - Computation approaches (direct, prioritized, calculated)
  - Dependencies between fields
  - Computation Structure JSON format
- **Mapping Fields Database**: Summary of provider-to-Fleeti mappings
  - Mapping types (direct, prioritized, calculated)
  - Configuration levels (default, customer, asset group, asset)
  - Links to YAML configurations

### YAML Configuration
- **Reference Specification**: Summary of YAML mapping structure
  - Optimization rules (8 key rules for minimizing redundancy)
  - Mapping types (direct, prioritized, calculated, transformed, io_mapped)
  - Examples for each mapping type
- **Generated Mappings**: Summary of actual field mappings
  - Number of fields mapped
  - Examples of different mapping patterns
  - Provider-specific configurations

### Ready State
- Confirm that all context has been loaded
- Indicate readiness to answer questions about:
  - Project architecture and design decisions
  - Field mappings and transformations
  - Computation approaches and dependencies
  - YAML configuration structure
  - Database relationships and structure

## Important Notes

- **Date-based File Naming**: All export files use date-based naming (e.g., `Provider Field (db) 12-23-25.csv`). The command should read all files in the specified directories, not specific filenames.
- **CSV File Size**: CSV files may be large (300+ rows). Summarize key information rather than including full content.
- **Directory Patterns**: Use directory-based patterns rather than specific filenames to ensure the command works with any date-based exports.
- **Batch Reading**: Read files in parallel when possible for efficiency.
- **Context Completeness**: Ensure all three database types (Provider Fields, Fleeti Fields, Mapping Fields) are covered in the summary.

## Expected Output

After executing this command, the AI should:

1. ✅ Have read all Overview & Vision documentation
2. ✅ Have read all database export CSV files
3. ✅ Have read all YAML configuration files
4. ✅ Provide a structured summary as specified above
5. ✅ Confirm readiness to answer questions about the Fleeti Telemetry Mapping project

The summary should be comprehensive enough that the user can immediately start asking questions without needing to provide additional context.

