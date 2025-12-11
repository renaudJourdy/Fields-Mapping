# Fleeti Telemetry Mapping Documentation

This repository centralizes the Fleeti telemetry documentation and mapping specifications. This README explains the current project structure and how to navigate it.

## 📁 Current Project Structure

```
.
├── docs/                    # Documentation and reference materials
│   ├── brainstorming/       # AI-generated analysis and brainstorming documents
│   ├── legacy/             # Historical documents kept for reference
│   ├── rag/                # RAG (Retrieval-Augmented Generation) data for AI context
│   │   ├── enums/          # Fleeti API enumerations (for AI context only)
│   │   └── reference/      # Immutable provider field catalogs
│   └── TO DO.txt           # Personal task list
├── notion/                 # Notion wiki structure (local organization before syncing)
│   ├── 1-overview-vision/  # Finalized overview and vision (95-100% complete)
│   ├── 2-documentation/    # Technical documentation (work in progress)
│   ├── 3-developer-resources/  # Developer guides (work in progress)
│   ├── 4-project-management/   # Project management (work in progress)
│   └── 5-technical-pages/      # Technical pages (work in progress)
└── Scripts/                # Scripts for AI use when needed
```

---

## 📚 Folder Descriptions

### `docs/brainstorming/`

**Purpose:** Destination folder for all AI-generated analysis and brainstorming documents.

**Usage:**
- When prompting AI to generate analysis, documentation, or brainstorming content, output files should be saved here
- Subfolders should be organized based on the request/topic
- Examples: `configuration-file/`, `mapping/`, `storage-strategy/`, `structure-notion/`

**Current subfolders:**
- `configuration-file/` - Configuration file analysis
- `mapping/` - Mapping methodology documents
- `storage-strategy/` - Storage strategy analysis and reviews
- `structure-notion/` - Notion structure organization guidelines

---

### `docs/legacy/`

**Purpose:** Historical documents from previous work, kept for reference purposes.

**Important:** These documents are **deprecated** and should NOT be used as reference for current field mappings. They are kept for historical context only.

**Contents:**
- `telemetry-system-specification.md` - Original system specification
- `telemetry-status-rules.md` - Original status rules document
- `fleeti-telemetry-schema-specification.md` - Original schema specification
- `navixy-to-fleeti-mapping-legacy.csv` - Outdated field mapping (field associations deprecated)

---

### `docs/rag/`

**Purpose:** RAG (Retrieval-Augmented Generation) data used to provide AI with context about the Fleeti system. These files help AI understand the project better but are **NOT part of Notion documentation**.

#### `docs/rag/enums/`

**Purpose:** Fleeti API enumerations for AI context only.

**Contents:**
- `response.json` - 45 enumeration types from Fleeti backend API (numeric values, names, translations, image URLs)
- `README.md` - Comprehensive documentation of enum categories and usage patterns

**Note:** These enums help AI understand Fleeti's data structures but should **never be included in Notion documentation**.

#### `docs/rag/reference/`

**Purpose:** Immutable source-of-truth provider field catalogs used for mapping provider-specific fields to Fleeti canonical fields.

**Contents:**
- `navixy-field-catalog.csv` - Complete catalog of ~340 Navixy telemetry fields observed via Data Forwarding POC
- `flespi-teltonika-avl-id-catalog.csv` - Comprehensive Teltonika AVL ID reference from Flespi platform documentation
- `teltonika-fmb140-avl-parameters.csv` - Device-specific AVL parameter reference for Teltonika FMB140 GPS tracker

**Usage:** Reference these catalogs when mapping provider fields to Fleeti telemetry format.

---

### `docs/TO DO.txt`

**Purpose:** Personal task list to track items that need to be done.

**Current items:**
- Add `last_updated_at`
- Add `last_changed_at`
- Add telemetry field name for debug purposes
- Calibration table disclaimer
- Telemetry unmapped?script?

---

### `notion/`

**Purpose:** Local markdown files that reflect the Notion wiki structure. Used to organize content in one place before pasting to Notion.

**Workflow:** Content is organized locally in this folder structure, then manually synced to Notion wiki.

#### `notion/1-overview-vision/`

**Status:** ✅ **Finalized (95-100% complete)**

**Purpose:** Project overview, objectives, architecture, and key concepts.

**Important:** This section should **remain untouched** except for:
- Fixing mistakes
- Making huge improvements (if detected)

**Contents:**
- `1-project-overview.md` - High-level project description
- `2-objectives-goals.md` - Primary objectives and requirements
- `3-architecture-overview.md` - System architecture and design
- `4-key-concepts.md` - Terminology and fundamental concepts

#### `notion/2-documentation/`

**Status:** ⚠️ **Work in Progress**

**Purpose:** Comprehensive technical documentation including specifications, field mappings, reference materials, and requirements.

**Contents:**
- `specifications/` - Technical specifications (telemetry system, status rules, schema)
- `field-mappings/` - Field catalogs and mapping rules
- `reference-materials/` - Provider catalogs, enum definitions, legacy documentation
- `requirements/` - Functional and product requirements

**Note:** All subfolders and files in this section are **work in progress** and should be treated as **informative** only.

#### `notion/3-developer-resources/`

**Status:** ⚠️ **Work in Progress**

**Purpose:** Practical guides and resources for developers implementing the system.

**Contents:**
- `getting-started/` - Quick start guides and development setup
- `implementation-guides/` - Field mapping, status computation, storage strategy implementation
- `api-documentation/` - Telemetry API, Configuration API, WebSocket API
- `configuration-guide/` - Configuration hierarchy and YAML examples
- `developer-guidelines/` - Contribution guidelines, documentation standards
- `technical-specifications/` - Expert reviews and storage strategy analysis
- `troubleshooting/` - Common issues, debugging guide, FAQ

**Note:** All subfolders and files in this section are **work in progress** and should be treated as **informative** only.

#### `notion/4-project-management/`

**Status:** ⚠️ **Work in Progress**

**Purpose:** Project status, roadmap, decisions, and ongoing work tracking.

**Contents:**
- `current-status/` - Current project status
- `ongoing-work/` - Active work items
- `roadmap/` - Project roadmap
- `decision-records/` - Architecture and design decisions
- `meeting-notes/` - Meeting notes and discussions

**Note:** All subfolders and files in this section are **work in progress** and should be treated as **informative** only.

#### `notion/5-technical-pages/`

**Status:** ⚠️ **Work in Progress**

**Purpose:** Space for developers to contribute their own technical pages, notes, and examples.

**Note:** All subfolders and files in this section are **work in progress** and should be treated as **informative** only.

---

### `Scripts/`

**Purpose:** Scripts folder for AI use when needed.

**Current status:** Empty folder, available for scripts generated by AI when automation or utilities are required.

---

## 🎯 How to Use This Repository

### For AI-Assisted Work

1. **Brainstorming/Analysis:** Save AI-generated documents to `docs/brainstorming/` with appropriate subfolder organization
2. **Reference Data:** Use `docs/rag/` for context:
   - `docs/rag/enums/` - Understand Fleeti enum structures
   - `docs/rag/reference/` - Reference provider field catalogs
3. **Notion Documentation:** 
   - Work in `notion/` folder structure
   - **Respect finalized sections:** `1-overview-vision/` is finalized, avoid changes unless fixing mistakes
   - **Treat WIP sections as informative:** Other sections are work in progress
4. **Scripts:** Use `Scripts/` folder when AI needs to create automation scripts

### For Understanding the Project

1. **Start Here:** Read `notion/1-overview-vision/README.md` for project overview
2. **Technical Specs:** Review `notion/2-documentation/specifications/` for system architecture
3. **Field Mappings:** Check `notion/2-documentation/field-mappings/` for field catalogs
4. **Legacy Context:** Consult `docs/legacy/` for historical reference (but verify against current specs)
5. **Provider Fields:** Reference `docs/rag/reference/` for provider field catalogs

### For Notion Sync Workflow

1. **Local Organization:** Organize content in `notion/` folder structure
2. **Manual Sync:** Copy/paste content from local files to Notion wiki
3. **Finalized Content:** `1-overview-vision/` is ready for Notion sync
4. **WIP Content:** Other sections are still being refined before Notion sync

---

## 📝 Notes

- **README.md is outdated:** The old README described a previous project structure with `configs/`, `scripts/`, `Wiki/`, `working/`, and `notion-wiki/` folders that no longer exist
- **Current structure is simplified:** Focus is on documentation organization and Notion sync preparation
- **RAG data is for AI context:** Files in `docs/rag/` help AI understand the project but are not part of Notion documentation
- **Legacy docs preserved:** Historical documents kept in `docs/legacy/` for reference but are deprecated

---

**Last Updated:** 2025-01-XX  
**Project Status:** Active development, documentation organization phase
