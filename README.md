# Fleeti Telemetry Mapping Documentation

This repository centralizes the Fleeti telemetry documentation and mapping specifications. This README provides a comprehensive overview of the entire project structure and how to navigate it.

## 📁 Project Structure

```
.
├── cursor/                          # Cursor IDE configuration and commands
├── docs/                            # Documentation and reference materials
│   ├── brainstorming/              # AI-generated analysis and brainstorming documents
│   ├── legacy/                     # Historical documents kept for reference
│   ├── rag/                        # RAG (Retrieval-Augmented Generation) data for AI context
│   ├── templates/                  # Documentation templates
│   └── TO DO.txt                   # Personal task list
├── notion/                         # Notion wiki structure (local organization before syncing)
│   ├── 1-overview-vision/         # Project overview and vision (finalized)
│   ├── 2-documentation/           # Technical documentation
│   ├── 3-developer-resources/     # Developer guides and resources
│   ├── 4-project-management/      # Project management and tracking
│   ├── 5-technical-pages/         # Developer-contributed technical pages
│   └── README.md                   # Notion wiki homepage
└── README.md                       # This file - project overview
```

---

## 📚 Detailed Folder Descriptions

### `cursor/`

**Purpose:** Cursor IDE configuration and custom commands.

**Contents:**
- Cursor-specific configuration files and custom commands for AI-assisted development workflows

**Status:** Configuration folder, updated as needed

---

### `docs/`

**Purpose:** Documentation, reference materials, and AI context data.

#### `docs/brainstorming/`

**Purpose:** Destination folder for all AI-generated analysis and brainstorming documents.

**Usage:**
- When prompting AI to generate analysis, documentation, or brainstorming content, output files should be saved here
- Subfolders should be organized based on the request/topic

**Current subfolders:**
- `storage-strategy/` - Storage strategy analysis and expert reviews
  - `expert-review-storage-strategy-analysis.md` - Expert review analysis of storage strategy
  - `expert-review-storage-strategy-prompt.md` - Prompt used for expert review
  - `telemetry-storage-product-requirements.md` - Storage product requirements document

**Note:** This folder is for AI-generated content that may inform decisions but is not part of the official documentation.

---

#### `docs/legacy/`

**Purpose:** Historical documents from previous work, kept for reference purposes.

**Important:** These documents are **deprecated** and should NOT be used as reference for current field mappings. They are kept for historical context only.

**Contents:**
- `navixy-provider-fields-import.csv` - Legacy Navixy provider fields import data
- `navixy-to-fleeti-mapping-legacy.csv` - Outdated field mapping (field associations deprecated)

**Note:** These files are preserved for historical reference but should not be used for current mapping work.

---

#### `docs/rag/`

**Purpose:** RAG (Retrieval-Augmented Generation) data used to provide AI with context about the Fleeti system. These files help AI understand the project better but are **NOT part of Notion documentation**.

**Contents:**
- `SPECIFICATIONS_FAQ.md` - Frequently asked questions about specifications for AI context

**Subfolders:**

##### `docs/rag/enums/`

**Purpose:** Fleeti API enumerations for AI context only.

**Contents:**
- `response.json` - 45 enumeration types from Fleeti backend API (numeric values, names, translations, image URLs)
- `README.md` - Comprehensive documentation of enum categories and usage patterns

**Note:** These enums help AI understand Fleeti's data structures but should **never be included in Notion documentation**.

---

#### `docs/templates/`

**Purpose:** Documentation templates for creating consistent documentation structure.

**Contents:**
- `epic-template.md` - Template for creating epic documentation
- `feature-template.md` - Template for creating feature documentation

**Usage:** Use these templates when creating new epic or feature documentation to ensure consistency.

---

#### `docs/TO DO.txt`

**Purpose:** Personal task list to track items that need to be done.

**Current items:**
- Add `last_updated_at`
- Add `last_changed_at`
- Add telemetry field name for debug purposes
- Calibration table disclaimer
- Telemetry unmapped?script?

---

### `notion/`

**Purpose:** Local markdown files that reflect the Notion wiki structure. Used to organize content in one place before syncing to Notion.

**Workflow:** Content is organized locally in this folder structure, then manually synced to Notion wiki.

**Main file:**
- `README.md` - Notion wiki homepage with navigation to all sections

---

#### `notion/1-overview-vision/`

**Status:** ✅ **Finalized (95-100% complete)**

**Purpose:** Project overview, objectives, architecture, and key concepts.

**Important:** This section should **remain untouched** except for:
- Fixing mistakes
- Making huge improvements (if detected)

**Contents:**
- `README.md` - Section overview and navigation
- `1-project-overview.md` - High-level project description covering current state, problem statement, goals, stakeholders, and scope
- `2-objectives-goals.md` - Primary objectives and requirements including provider-agnostic system vision, success criteria, and constraints
- `3-architecture-overview.md` - System architecture and design including data flow, components, storage strategy, and configuration system
- `4-key-concepts.md` - Terminology and fundamental concepts including provider-agnostic vs. provider-specific, Fleeti telemetry format, field types, and configuration hierarchy

---

#### `notion/2-documentation/`

**Status:** ⚠️ **Work in Progress** (some sections finalized)

**Purpose:** Comprehensive technical documentation including databases, contracts, reference materials, and epics/features.

**Main file:**
- `README.md` - Documentation section overview and navigation

**Subfolders:**

##### `notion/2-documentation/1-field-mappings-and-databases/`

**Status:** ✅ **Done**

**Purpose:** Four databases that serve as the single source of truth for field definitions and mappings.

**Main file:**
- `README.md` - Database overview, relationships, and workflow

**Subfolders:**

###### `1-provider-fields/`

**Purpose:** Provider Fields Database - Catalog of provider-specific telemetry fields.

**Contents:**
- `README.md` - Database documentation and structure
- `raw-packet-structure.md` - Documentation of raw packet structure from providers
- `export/` - CSV exports from Notion database
  - `Provider Field (db) 12-23-25.csv` - Latest database export

**Usage:** Reference for understanding provider-specific field structures (Navixy, Teltonika, OEM, etc.)

---

###### `2-fleeti-fields/`

**Purpose:** Fleeti Fields Database - Complete catalog of unified Fleeti telemetry fields.

**Contents:**
- `README.md` - Database documentation, field structure, computation approaches, and YAML generation
- `export/` - CSV exports from Notion database
  - `Fleeti Fields (db) 1-6-26.csv` - Latest database export
- `scripts/` - Python scripts for database operations
  - `generate_fleeti_fields.py` - Script for generating Fleeti fields data
- `workspace/` - Working files and drafts
  - `fleeti-fields-catalog.csv` - Working catalog file
  - `asset-details/` - Asset details related workspace files
    - `Fleeti Fields (db) draft.csv` - Draft version
    - `yaml/navixy-mapping-2025-12-29.yaml` - Historical YAML mapping

**Usage:** Canonical reference for Fleeti telemetry structure. Used by WebSocket contracts and REST API endpoints.

---

###### `3-mapping-fields/`

**Purpose:** Mapping Fields Database - Transformation rules linking provider fields to Fleeti fields.

**Contents:**
- `README.md` - Database documentation, mapping types, and YAML generation connection
- `export/` - CSV exports from Notion database
  - `Mapping Fields (db) 1-8-26.csv` - Latest database export
- `output/` - Generated mapping files
  - `Mapping Fields to Add 2026-01-06.csv` - Latest generated mapping additions
  - `Mapping Fields to Add 2026-01-02.csv` - Previous generated mapping additions
  - `Mapping Fields to Add 2025-12-23.csv` - Historical mapping additions
  - `Mapping Fields to Add 2025-12-22.csv` - Historical mapping additions
- `scripts/` - Python scripts for mapping operations
  - `generate_mapping_fields_csv.py` - Script for generating mapping fields CSV

**Usage:** Defines how provider data transforms into Fleeti format. Used to generate YAML configuration files.

---

###### `4-yaml-configuration/`

**Purpose:** YAML Configuration Database - Versioned tracking of generated YAML configuration files.

**Contents:**
- `README.md` - Database documentation, YAML generation specification, and script documentation
- `yaml-mapping-reference.yaml` - Reference YAML file showing mapping structure and format
- `export/` - CSV exports from Notion database
  - `YAML Configurations (db) 1-9-26.csv` - Latest database export
- `output/` - Generated YAML configuration files
  - `navixy-mapping-2026-01-08.yaml` - Latest generated YAML configuration
  - `navixy-mapping-2026-01-07.yaml` - Previous YAML configuration
  - `navixy-mapping-2026-01-02.yaml` - Historical YAML configuration
  - `navixy-mapping-2025-12-23.yaml` - Historical YAML configuration
  - `navixy-mapping-2025-12-22.yaml` - Historical YAML configuration
- `scripts/` - Python scripts for YAML generation and validation
  - `generate_yaml_from_csv.py` - Script that reads Mapping Fields CSV and generates optimized YAML configuration
  - `validate_yaml.py` - Script that validates generated YAML files for correctness and integrity

**Usage:** Version control and deployment tracking of configuration files. Generated YAML files are used by the transformation pipeline.

---

##### `notion/2-documentation/2-websocket-contracts/`

**Status:** 🎯 **Structure Created - Content To Be Developed**

**Purpose:** WebSocket contract specifications for real-time telemetry streaming to frontend applications.

**Contents:**
- `README.md` - WebSocket contracts overview and structure
- `1-live-map-markers.md` - WebSocket stream contract for `live.map.markers` (real-time marker updates on map)
- `2-asset-list.md` - WebSocket stream contract for `live.assets.list` (real-time asset list updates)
- `3-asset-details.md` - WebSocket stream contract for `live.asset.details` (real-time asset details updates)

**Usage:** Defines stream names, message formats, subscription parameters, update patterns (snapshot/delta), and error handling for frontend integration.

---

##### `notion/2-documentation/3-api-contracts/`

**Status:** ✅ **Done**

**Purpose:** REST API contract specifications for telemetry endpoints.

**Contents:**
- `README.md` - API contracts overview and structure
- `1-telemetry-snapshots.md` - REST API endpoint for `/api/v1/telemetry/snapshots` (latest telemetry snapshot per asset, customer vs admin tiers)
- `2-asset-telemetry-history.md` - REST API endpoint for `/api/v1/telemetry/assets/{asset_id}/history` (time-range history for a single asset, customer vs admin tiers)

**Usage:** Defines endpoint URLs, request/response formats, query parameters, pagination, authentication, and error responses for frontend integration.

---

##### `notion/2-documentation/4-reference-materials/`

**Status:** ✅ **Validated**

**Purpose:** Reference documentation including telemetry full schema, status rules, and provider field catalogs.

**Contents:**
- `README.md` - Reference materials overview
- `1-telemetry-full-schema.md` - Complete reference of all possible Fleeti telemetry fields organized by section
- `2-status-rules.md` - Status computation logic and compatibility matrix for asset types
- `resources/` - Provider field catalogs in CSV format
  - `navixy-field-catalog.csv` - Complete catalog of ~340 Navixy telemetry fields
  - `flespi-teltonika-avl-id-catalog.csv` - Comprehensive Teltonika AVL ID reference from Flespi platform
  - `teltonika-fmb140-avl-parameters.csv` - Device-specific AVL parameter reference for Teltonika FMB140 GPS tracker

**Usage:** Reference materials for understanding telemetry schema, status computation, and provider field structures.

---

##### `notion/2-documentation/5-epics-and-features/`

**Status:** ✅ **Active**

**Purpose:** Structured breakdown of all epics and features for the Fleeti Telemetry Mapping system.

**Contents:**
- `README.md` - Complete epic and feature breakdown with all 7 epics and their features listed
- `reference-helpers/` - Helper files for feature planning
  - `features.md` - Feature breakdown document
  - `provider-priority-configuration.md` - Provider priority configuration documentation
  - `speech-to-text.md` - Speech-to-text notes for feature planning

**Epic Folders:**

Each epic has its own folder with a README and individual feature markdown files:

- `E1-Provider-Ingestion-Data-Forwarding/` - 6 features (F1.1-F1.6)
  - Navixy data forwarding, provider-agnostic architecture, customer management, health monitoring, data recovery, auto-sync
- `E2-Transformation-Pipeline/` - 2 features (F2.1-F2.2)
  - YAML configuration execution, hierarchical configuration support
- `E3-Status-Computation/` - 1 feature (F3.1)
  - Status families computation (Connectivity, Transit, Engine, Immobilization)
- `E4-Storage-Strategy/` - 2 features (F4.1-F4.2)
  - Multi-tier storage implementation, retention policies
- `E5-Troubleshooting-Investigation/` - 2 features (F5.1-F5.2)
  - Mapping investigation tool, audit trail
- `E6-Data-Consumption/` - 9 features (F6.1-F6.9)
  - WebSocket streams (markers, asset list, asset details, geofences), REST APIs (snapshots, history, trips, geofences), advanced filters
- `E7-Provider-Priority-Configuration/` - 1 feature (F7.1)
  - Provider priority rules for multi-gateway assets

**Usage:** Feature specifications and implementation planning. Each feature file can be populated with detailed specifications as development progresses.

---

##### `notion/2-documentation/legacy/`

**Status:** ⚠️ **Legacy - For Reference Only**

**Purpose:** Legacy documentation from previous project structure, kept for reference.

**Contents:**
- `4-requirements/` - Legacy requirements documentation
- `5-operations/` - Legacy operations documentation
- `6-data-quality/` - Legacy data quality documentation
- `7-security/` - Legacy security documentation
- `8-integration/` - Legacy integration documentation
- `9-deployment/` - Legacy deployment documentation
- `10-data-management/` - Legacy data management documentation

**Note:** These folders contain legacy documentation that may be referenced but are not part of the current active documentation structure.

---

#### `notion/3-developer-resources/`

**Status:** ⚠️ **Work in Progress**

**Purpose:** Practical guides and resources for developers implementing the system.

**Contents:**
- `README.md` - Developer resources overview
- `api-documentation/` - API documentation (Telemetry API, Configuration API, WebSocket API)
- `configuration-guide/` - Configuration hierarchy and YAML examples
- `developer-guidelines/` - Contribution guidelines, documentation standards, Notion methodology
- `getting-started/` - Quick start guides, development setup, first contribution guide
- `implementation-guides/` - Field mapping, status computation, storage strategy implementation guides
- `technical-specifications/` - Expert reviews and storage strategy analysis
- `troubleshooting/` - Common issues, debugging guide, FAQ

**Note:** All subfolders and files in this section are **work in progress** and should be treated as **informative** only.

---

#### `notion/4-project-management/`

**Status:** ⚠️ **Work in Progress**

**Purpose:** Project status, roadmap, decisions, and ongoing work tracking.

**Contents:**
- `README.md` - Project management overview
- `current-status/` - Current project status
- `ongoing-work/` - Active work items
- `roadmap/` - Project roadmap
- `decision-records/` - Architecture and design decisions
- `meeting-notes/` - Meeting notes and discussions

**Note:** All subfolders and files in this section are **work in progress** and should be treated as **informative** only.

---

#### `notion/5-technical-pages/`

**Status:** ⚠️ **Work in Progress**

**Purpose:** Space for developers to contribute their own technical pages, notes, and examples.

**Contents:**
- `README.md` - Technical pages overview
- `1-telemetry-database-design.md` - Database design documentation for telemetry storage

**Note:** All subfolders and files in this section are **work in progress** and should be treated as **informative** only.

---

## 🎯 How to Use This Repository

### For AI-Assisted Work

1. **Brainstorming/Analysis:** Save AI-generated documents to `docs/brainstorming/` with appropriate subfolder organization
2. **Reference Data:** Use `docs/rag/` for context:
   - `docs/rag/enums/` - Understand Fleeti enum structures
   - `docs/rag/SPECIFICATIONS_FAQ.md` - Reference for specification questions
3. **Templates:** Use `docs/templates/` when creating new epic or feature documentation
4. **Notion Documentation:** 
   - Work in `notion/` folder structure
   - **Respect finalized sections:** `1-overview-vision/` is finalized, avoid changes unless fixing mistakes
   - **Databases are done:** `2-documentation/1-field-mappings-and-databases/` is complete and validated
   - **Treat WIP sections as informative:** Other sections are work in progress
5. **Scripts:** Python scripts are located in database subfolders for generating and validating data

### For Understanding the Project

1. **Start Here:** Read `notion/README.md` for wiki navigation, then `notion/1-overview-vision/README.md` for project overview
2. **Databases:** Review `notion/2-documentation/1-field-mappings-and-databases/` for field definitions and mappings
3. **Contracts:** Check `notion/2-documentation/2-websocket-contracts/` and `3-api-contracts/` for API specifications
4. **Features:** Review `notion/2-documentation/5-epics-and-features/` for feature breakdown and specifications
5. **Reference Materials:** Consult `notion/2-documentation/4-reference-materials/` for schema and status rules
6. **Legacy Context:** Consult `docs/legacy/` for historical reference (but verify against current specs)
7. **Provider Fields:** Reference `notion/2-documentation/4-reference-materials/resources/` for provider field catalogs

### For Notion Sync Workflow

1. **Local Organization:** Organize content in `notion/` folder structure
2. **Manual Sync:** Copy/paste content from local files to Notion wiki
3. **Finalized Content:** 
   - `1-overview-vision/` is ready for Notion sync
   - `2-documentation/1-field-mappings-and-databases/` is complete
   - `2-documentation/3-api-contracts/` is done
   - `2-documentation/4-reference-materials/` is validated
4. **WIP Content:** Other sections are still being refined before Notion sync

### For Database Workflows

1. **Export from Notion:** Export databases to CSV files in respective `export/` folders
2. **Generate YAML:** Use `4-yaml-configuration/scripts/generate_yaml_from_csv.py` to generate YAML from Mapping Fields CSV
3. **Validate YAML:** Use `4-yaml-configuration/scripts/validate_yaml.py` to validate generated YAML files
4. **Review Output:** Check `output/` folders for generated files

---

## 📝 Important Notes

- **README.md Structure:** This README provides comprehensive project structure documentation
- **Notion README:** `notion/README.md` serves as the wiki homepage with navigation
- **Database Exports:** CSV files in `export/` folders are snapshots from Notion databases
- **Generated Files:** Files in `output/` folders are generated by scripts and should not be manually edited
- **RAG Data:** Files in `docs/rag/` help AI understand the project but are not part of Notion documentation
- **Legacy Docs:** Historical documents kept in `docs/legacy/` and `notion/2-documentation/legacy/` for reference but are deprecated
- **Templates:** Use templates in `docs/templates/` for consistent documentation structure
- **Scripts:** Python scripts are located in database subfolders and are part of the workflow

---

## 🔄 Project Status

**Current Phase:** Active development, documentation organization and feature specification

**Finalized Sections:**
- ✅ `notion/1-overview-vision/` - Project overview and vision
- ✅ `notion/2-documentation/1-field-mappings-and-databases/` - All four databases
- ✅ `notion/2-documentation/3-api-contracts/` - REST API contracts
- ✅ `notion/2-documentation/4-reference-materials/` - Reference materials

**Work in Progress:**
- ⚠️ `notion/2-documentation/2-websocket-contracts/` - Structure created, content to be developed
- ⚠️ `notion/2-documentation/5-epics-and-features/` - Structure created, feature files to be populated
- ⚠️ `notion/3-developer-resources/` - Developer guides
- ⚠️ `notion/4-project-management/` - Project management
- ⚠️ `notion/5-technical-pages/` - Technical pages

---

**Last Updated:** 2026-01-09  
**Project Status:** Active development, documentation organization phase
