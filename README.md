# Fleeti Telemetry Mapping Documentation

This repository centralizes the Fleeti telemetry documentation and mapping specifications. Start here to understand where each artifact lives and how to keep it current for future chats or contributors.

## 📁 Folder Layout

```
.
├── notion/                    # Notion-synced content
│   ├── fleeti-fields/              # Fleeti Fields database sync
│   ├── provider-fields/            # Provider Fields database sync
│   ├── field-mappings/             # Field Mappings database sync
│   └── fleeti-fields-telemetry-mapping/  # Wiki skeleton structure
│       ├── overview-vision/        # Project overview and vision
│       ├── documentation/          # Specifications, requirements, mappings
│       ├── developer-resources/    # Developer guides and resources
│       ├── project-management/     # Status, roadmap, decisions
│       ├── technical-pages/        # Developer-contributed pages
│       └── guidelines-standards/   # Documentation standards
├── configs/                 # YAML configuration files
├── scripts/                # Automation and utility scripts
│   ├── notion/                  # Notion sync scripts
│   ├── validation/              # Validation scripts
│   └── ai-custom/               # AI-generated custom scripts
├── docs/
│   ├── enums/              # Fleeti API enumeration definitions
│   ├── legacy/             # Historical/archived mapping documents
│   ├── reference/          # Immutable source-of-truth provider catalogs
│   └── project/            # Project management documents
├── Wiki/                   # Canonical specifications and rules
├── working/                # Work-in-progress documents
└── notion-wiki/           # Wiki architecture documentation
```

---

## 📚 Documentation Structure

### Wiki (`Wiki/`) - Canonical Specifications

**Purpose:** Final, authoritative specifications that define system behavior and structure.

- **`telemetry-status-rules.md`**  
  Canonical status family matrix and trigger logic for Connectivity, Transit, Engine, and Immobilization. This document is treated as final—consult it when implementing or validating status behavior.

- **`telemetry-system-specification.md`**  
  High-level vision and requirements for building a provider-agnostic telemetry pipeline (ingestion, mapping, storage tiers, configuration strategy). Update this when product scope or architectural decisions change.

### Working Documents (`working/`) - Active Development

**Purpose:** Documents currently being developed or refined. Once finalized, these move to `Wiki/` as reference specifications.

- **`fleeti-telemetry-schema-specification.md`**  
  Detailed breakdown of the Fleeti telemetry object: sections, nested structures, and provider field mappings. This file evolves alongside the mapping work—edit it as we refine schema coverage. **Status:** Work-in-progress. Will be moved to `Wiki/` once finalized.

### Reference Documents (`docs/reference/`) - Provider Catalogs

**Purpose:** Immutable source-of-truth catalogs from telematics providers. These are used to map provider-specific fields to Fleeti canonical fields.

- **`navixy-field-catalog.csv`**  
  Complete catalog of all Navixy telemetry fields observed via Data Forwarding POC. Created by running a script to identify every independent Navixy field received from various device configurations. **Use:** Authoritative provider-field inventory before defining new Fleeti mappings.

- **`flespi-teltonika-avl-id-catalog.csv`**  
  Comprehensive Teltonika AVL ID reference scraped from Flespi platform documentation. Flespi provides updated, comprehensive documentation for Teltonika AVL parameters. **Use:** Reference for mapping Navixy AVL IO IDs to provider field names and understanding field semantics.

- **`teltonika-fmb140-avl-parameters.csv`**  
  Device-specific AVL parameter reference for Teltonika FMB140 GPS tracker model, scraped directly from Teltonika documentation. **Use:** Device-specific reference that may include AVL IDs not present in the general Flespi catalog. Use alongside Flespi catalog for complete coverage.

### Legacy Documents (`docs/legacy/`) - Historical Reference

**Purpose:** Outdated mapping documents kept for historical reference. Field associations may be outdated, but descriptions and metadata may still be useful.

- **`navixy-to-fleeti-mapping-legacy.csv`**  
  First attempt at mapping Navixy fields to Fleeti fields. Created manually based on `navixy-field-catalog.csv` to establish initial field associations. **Status:** Outdated. Field associations and mappings should NOT be used as reference—these have been superseded by `fleeti-telemetry-schema-specification.md`. **Use:** Descriptions and other metadata columns may still contain useful information, but field associations are deprecated.

### Enumeration Definitions (`docs/enums/`) - Fleeti API Enums

**Purpose:** Enumeration definitions from the Fleeti backend API, useful for understanding canonical enum structures used throughout the Fleeti system.

- **`response.json`**  
  Snapshot of 45 enumeration types extracted from the Fleeti backend API. Includes numeric values, names, French/English translations, and image URLs. **Use:** Reference for canonical enum codes, translations, and visual assets when implementing features.

- **`README.md`**  
  Comprehensive documentation of all enum categories, usage patterns, and integration guidelines.

### Notion Sync (`notion/`) - Notion-Synced Content

**Purpose:** Markdown files that sync bidirectionally with Notion databases and wiki pages.

**Database Sync Folders:**
- **`notion/README.md`**  
  Overview of Notion sync system, workflow, and usage guidelines.

- **`notion/fleeti-fields/`**  
  Fleeti telemetry field definitions synced with Notion "Fleeti Telemetry Fields" database.

- **`notion/provider-fields/`**  
  Provider-specific field definitions synced with Notion "Provider Telemetry Fields" database.

- **`notion/field-mappings/`**  
  Field mapping rules synced with Notion "Field Mappings" database.

**Wiki Skeleton Structure:**
- **`notion/fleeti-fields-telemetry-mapping/`**  
  Complete wiki skeleton structure mirroring the Notion wiki. Contains empty README.md files in each section for future content sync:
  - `overview-vision/` - Project overview, objectives, architecture
  - `documentation/` - Specifications, requirements, field mappings, reference materials
  - `developer-resources/` - Getting started, implementation guides, API docs, troubleshooting
  - `project-management/` - Current status, ongoing work, roadmap, decision records
  - `technical-pages/` - Developer-contributed technical pages
  - `guidelines-standards/` - Documentation standards, wiki organization, contribution guidelines

### Configuration Files (`configs/`) - YAML Configurations

**Purpose:** YAML configuration files generated from Notion documentation.

- **`configs/README.md`**  
  Guide to YAML configuration files and generation workflow.

- **`configs/*.yaml`**  
  Provider-specific mapping configurations (e.g., `navixy-mapping.yaml`).

### Scripts (`scripts/`) - Automation Tools

**Purpose:** Python and PowerShell scripts for validation, Notion sync, automation, and custom utilities.

- **`scripts/notion/`**  
  Notion sync scripts:
  - `sync_to_notion.py` - Push local changes to Notion
  - `sync_from_notion.py` - Pull Notion changes locally
  - `detect_conflicts.py` - Detect sync conflicts
  - `validate_sync.py` - Validate markdown files
  - `generate_yaml.py` - Generate YAML from Notion content

- **`scripts/validation/`**  
  Validation scripts:
  - `validate_navixy_completeness.py` - Check mapping completeness
  - `navixy_fields_completeness_check.md` - Validation results

- **`scripts/ai-custom/`**  
  AI-generated custom scripts and utilities:
  - `create-notion-skeleton.ps1` - PowerShell script to create Notion wiki skeleton structure
  - Other custom automation scripts

### Project Documents (`docs/project/`) - Project Management

**Purpose:** Project management documents, reorganization guides, and project summaries.

- **`REORGANIZATION_IMPLEMENTATION_GUIDE.md`**  
  Complete guide for implementing project reorganization and Notion sync infrastructure.

- **`PROJECT_REORGANIZATION_SUMMARY.md`**  
  Summary of project reorganization efforts.

- **`TO DO.txt`**  
  Project task list and action items.

### Wiki Architecture (`notion-wiki/`) - Wiki System Documentation

**Purpose:** Documentation about the Notion wiki architecture, organization guidelines, and sync workflows.

- **`WIKI_ARCHITECTURE_PROPOSAL.md`**  
  Proposed hierarchical wiki structure and multi-audience organization.

- **`ANALYSIS_REPORT.md`**  
  Analysis of current Notion wiki structure and recommendations.

- **`ORGANIZATION_GUIDELINES.md`**  
  Guidelines for wiki organization, documentation standards, and contribution.

- **`SYNC_WORKFLOW.md`**  
  MCP-enabled sync workflows for bidirectional synchronization.

- **`scripts/`**  
  Example sync scripts demonstrating MCP integration.

---

## 🔄 Document Lifecycle

1. **Working** (`working/`): Active development and refinement
2. **Wiki** (`Wiki/`): Finalized specifications moved from `working/`
3. **Legacy** (`docs/legacy/`): Superseded documents kept for historical reference

---

## 🎯 How to Use This README

When starting a new conversation or onboarding someone:

1. **For schema work:** Start with `working/fleeti-telemetry-schema-specification.md`
2. **For status logic:** Reference `Wiki/telemetry-status-rules.md`
3. **For provider fields:** Check `docs/reference/navixy-field-catalog.csv`
4. **For enum values:** Use `docs/enums/response.json`
5. **For Notion sync:** See `notion/README.md` and `scripts/notion/README.md`
6. **For historical context:** Consult `docs/legacy/` (but verify against current specs)

### Notion Sync Workflow

For working with Notion-synced documentation:

1. **Local-first workflow:**
   - Edit markdown files in `notion/` directory
   - Validate: `python scripts/notion/validate_sync.py --database all`
   - Check conflicts: `python scripts/notion/detect_conflicts.py --database all`
   - Sync to Notion: `python scripts/notion/sync_to_notion.py --database all`

2. **Notion-first workflow:**
   - Edit in Notion workspace
   - Pull changes: `python scripts/notion/sync_from_notion.py --database all`

3. **YAML generation:**
   - Generate from Notion: `python scripts/notion/generate_yaml.py --provider navixy`

See `docs/project/REORGANIZATION_IMPLEMENTATION_GUIDE.md` for complete setup instructions.

Keep this file updated whenever a document is added, renamed, or reclassified to ensure future collaborators can immediately navigate the project.
