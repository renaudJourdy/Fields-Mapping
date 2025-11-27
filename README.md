# Project Documentation Guide

This repository centralizes the Fleeti telemetry documentation. Start here to understand where each artifact lives and how to keep it current for future chats or contributors.

## Folder Layout

```
docs/
├── reference/  # Immutable source-of-truth documents
└── working/    # Living drafts or specs updated as the project evolves
```

### Reference Documents (`docs/reference/`)

- `Telemetry Status Rules.md`  
  Canonical status family matrix and trigger logic for Connectivity, Transit, Engine, and Immobilization. This document is treated as final—consult it when implementing or validating status behavior.

- `Navixy Field Catalog.csv`  
  Export of every telemetry field observed via Navixy Data Forwarding (names, priorities, groupings, units, examples). Use it as the authoritative provider-field inventory before defining new Fleeti mappings.

- `enums/response.json`  
  Snapshot of all enums currently defined across the Fleeti ecosystem (accessories, assets, statuses, etc.) with internationalized labels and supporting metadata. Reference it whenever you need the canonical numeric codes or translations exposed in APIs/UI.

### Working Documents (`docs/working/`)

- `Telemetry System Specification.md`  
  High-level vision and requirements for building a provider-agnostic telemetry pipeline (ingestion, mapping, storage tiers, configuration strategy). Update this when product scope or architectural decisions change.

- `Telemetry Schema Analysis.md`  
  Detailed breakdown of the Fleeti telemetry object: sections, nested structures, and provider field mappings. This file evolves alongside the mapping work—edit it as we refine schema coverage.

## How to Use This README in Future Sessions

When starting a new conversation or onboarding someone, simply point them to this README. Each link above provides the precise location and intent of the supporting document, so there is no need to restate their contents elsewhere.

Keep this file updated whenever a document is added, renamed, or reclassified to ensure future collaborators can immediately navigate the project.***

