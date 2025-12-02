# Fleeti Telemetry Mapping Documentation

This repository centralizes the Fleeti telemetry documentation and mapping specifications. Start here to understand where each artifact lives and how to keep it current for future chats or contributors.

## 📁 Folder Layout

```
.
├── docs/
│   ├── enums/          # Fleeti API enumeration definitions
│   ├── legacy/         # Historical/archived mapping documents
│   └── reference/     # Immutable source-of-truth provider catalogs
├── Scripts/           # Validation and analysis tools
├── Wiki/              # Canonical specifications and rules
└── working/           # Work-in-progress documents
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

### Scripts (`Scripts/`) - Validation Tools

**Purpose:** Python scripts and analysis tools for validating mapping completeness and consistency.

- **`validate_navixy_completeness.py`**  
  Validation script to check mapping completeness between Navixy fields and Fleeti schema.

- **`navixy_fields_completeness_check.md`**  
  Results and analysis from completeness validation checks.

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
5. **For historical context:** Consult `docs/legacy/` (but verify against current specs)

Keep this file updated whenever a document is added, renamed, or reclassified to ensure future collaborators can immediately navigate the project.
