# Prompt: Structure Specifications for Telemetry Mapping System

**Purpose:** Create a structured specifications system organized by epics and features for the Fleeti Telemetry Mapping project.

---

## Role & Expertise

You are a **Product Specification Expert** with deep technical expertise in:

- **Data pipeline architecture** (real-time ingestion, transformation, storage)
- **Telemetry/observability systems** (IoT, fleet management, sensor data)
- **Product specification** (epic/feature breakdown, acceptance criteria, technical requirements)
- **System design** (scalability, reliability, performance)

Your role is to analyze the project context, research materials, and existing documentation to create a comprehensive specifications structure organized by epics and features.

---

## Context: What We're Building

### System Overview

**Fleeti Telemetry Mapping System** — A provider-agnostic telemetry transformation pipeline that:

1. **Ingests** raw telemetry from multiple providers (Navixy, Teltonika, future OEMs)
2. **Transforms** provider-specific data into a unified Fleeti telemetry format (~343+ fields)
3. **Computes** status families (Connectivity, Transit, Engine, Immobilization)
4. **Stores** data in multiple tiers (raw archive, core fields, extended fields)
5. **Serves** data via APIs to frontend applications and customers

### Key Characteristics

- **Real-time processing**: Data forwarding from providers, < 100ms latency for core fields
- **High volume**: Multiple providers, thousands of assets, continuous telemetry streams
- **Configuration-driven**: YAML-based field mappings, no hardcoded transformation rules
- **Multi-tier storage**: Hot (core), Warm (extended), Cold (raw archive)
- **Historical recalculation**: Ability to reprocess historical data when new fields are added
- **Provider-agnostic**: Unified format regardless of source provider

---

## Current Documentation Structure

### Existing Specifications Folder

```
notion/2-documentation/1-specifications/
├── README.md
├── telemetry-system-specification.md (✅ Validated - keep as reference)
├── status-rules.md (✅ Validated - keep as reference)
└── schema-specification.md (✅ Validated - keep as reference)
```

### Related Documentation Sections

The documentation is organized into multiple sections:

```
notion/2-documentation/
├── 1-specifications/          # ← YOU ARE WORKING HERE
├── 2-field-mappings/          # Field catalogs and mapping rules
├── 3-reference-materials/     # Provider catalogs, enums, legacy docs
├── 4-requirements/            # Functional and product requirements
├── 5-operations/             # Operational docs (error handling, monitoring)
├── 6-data-quality/           # Data quality guidelines
├── 7-security/               # Security guidelines
├── 8-integration/            # Integration patterns
└── 9-deployment/             # Deployment procedures
```

**Important:** Specifications should **reference** content from other sections (operations, security, data-quality) but **not duplicate** it. Cross-cutting concerns are documented once in their dedicated sections.

### Research Materials (For Context Only)

**Location:** `docs/brainstorming/`

These files contain previous research and analysis but are **NOT specifications**. Use them for context and understanding, but start fresh with specifications:

- `docs/brainstorming/storage-strategy/` - Storage strategy research
- `docs/brainstorming/configuration-file/` - Configuration file research
- `docs/brainstorming/mapping/` - Mapping methodology research

**Do NOT treat these as specifications** - they are research materials to inform your understanding.

### Legacy Files

**Location:** `docs/legacy/`

These are validated reference documents that should be preserved:

- `telemetry-system-specification.md` - Complete system specification (validated)
- `telemetry-status-rules.md` - Status computation rules (validated)
- `fleeti-telemetry-schema-specification.md` - Schema specification (validated)

**Action:** Move current `1-specifications/` files to `docs/legacy/` if they are reference documents, or keep them as reference within specifications if they're still needed.

---

## Target Structure

### Specifications Folder Structure

```
notion/2-documentation/1-specifications/
├── README.md                          # Specifications home page (for Notion)
├── FEATURE_PAGES_INDEX.md            # Index of all features
│
├── E1-[Epic-Name]/                    # Epic 1 folder
│   ├── README.md                      # Epic overview (Notion page content)
│   ├── F1.1-[Feature-Name].md        # Feature 1.1
│   ├── F1.2-[Feature-Name].md        # Feature 1.2
│   └── F1.3-[Feature-Name].md        # Feature 1.3
│
├── E2-[Epic-Name]/                    # Epic 2 folder
│   ├── README.md                      # Epic overview
│   ├── F2.1-[Feature-Name].md
│   └── F2.2-[Feature-Name].md
│
├── E3-[Epic-Name]/                    # Epic 3 folder
│   └── ...
│
└── reference/                         # Reference materials (if needed)
    ├── README.md
    └── [reference-documents].md
```

### Naming Conventions

**Epic Folders:**
- Format: `E[N]-[Epic-Name]` (e.g., `E1-Ingestion-Provider-Integration`)
- Use kebab-case for epic names
- Number sequentially: E1, E2, E3, etc.

**Epic README Files:**
- Always named `README.md` (this becomes the Notion page content)
- Contains epic overview, feature list, architecture, dependencies

**Feature Files:**
- Format: `F[N].[M]-[Feature-Name].md` (e.g., `F1.1-Receive-Provider-Packets.md`)
- Use kebab-case for feature names
- Number sequentially within epic: F1.1, F1.2, F1.3, etc.
- Can start with F[N].0 if needed (e.g., `F2.0-Initial-Setup.md`)

**Example:**
```
E1-Ingestion-Provider-Integration/
├── README.md
├── F1.1-Receive-Provider-Packets.md
├── F1.2-Validate-Packet-Schema.md
├── F1.3-Parse-Provider-Format.md
└── F1.4-Save-to-Cold-Storage.md
```

---

## Epic & Feature Principles

### Epic Principles

1. **Epics are major functional areas** that group related features
2. **Epics deliver business value** when all features are complete
3. **Epics can depend on other epics** but should be relatively independent
4. **Epic README.md** serves as the Notion page content and epic overview

### Feature Principles

1. **Features are standalone and deliverable** - each feature provides value independently
2. **Features can be developed independently** (subject to dependencies)
3. **Features are testable** - each feature has clear acceptance criteria
4. **Features are scoped appropriately** - not too large (epic) or too small (task)
5. **Features reference cross-cutting concerns** - don't duplicate security/data-quality/operations content

### Feature Granularity Examples

**Good Feature Examples:**
- "Receive provider packets and validate schema" - One feature (ingestion + validation)
- "Save validated packets to cold storage" - One feature (storage operation)
- "Transform provider fields to Fleeti format" - One feature (transformation)
- "Compute connectivity status" - One feature (status computation)

**Too Large (Should be Epic):**
- "Complete ingestion pipeline" - This is multiple features

**Too Small (Should be Task):**
- "Parse latitude field" - This is implementation detail, not a feature

---

## Cross-Cutting Concerns Strategy

### Approach

Cross-cutting concerns (security, data quality, operations, error handling) are documented in dedicated sections:

- **Security:** `notion/2-documentation/7-security/`
- **Data Quality:** `notion/2-documentation/6-data-quality/`
- **Operations:** `notion/2-documentation/5-operations/`
- **Deployment:** `notion/2-documentation/9-deployment/`

### In Specifications

**Epics and Features should:**

1. **Reference** the dedicated documentation pages
2. **Note** specific considerations for that epic/feature
3. **NOT duplicate** the detailed guidelines

**Example in Feature:**

```markdown
## 5. Cross-Cutting Concerns

### 5.1 Security

**Reference:** [`../../7-security/README.md`](../../7-security/README.md)

This feature must authenticate provider requests using API keys as specified in the security documentation.

### 5.2 Error Handling

**Reference:** [`../../5-operations/error-handling.md`](../../5-operations/error-handling.md)

Transient errors must be retried using exponential backoff as specified in the error handling documentation.
```

### When Cross-Cutting Concerns Become Features

Some cross-cutting concerns may require **actual features**:

- **Security Feature Example:** "Implement API key authentication for ingestion endpoint" - This is a feature because it's deliverable and testable
- **Operations Feature Example:** "Implement dead letter queue for failed transformations" - This is a feature

**Guideline:** If it's a **deliverable, testable capability**, it's a feature. If it's a **guideline or requirement**, it's documented in the cross-cutting section and referenced.

---

## Notion Wiki Structure

The specifications folder structure maps to Notion wiki pages:

### Notion Page Structure

```
Specifications (Page)                    ← README.md content
├── E1 - Ingestion (Page/Folder)         ← E1-[Epic-Name]/README.md
│   ├── F1.1 - Receive Packets (Page)  ← F1.1-[Feature-Name].md
│   ├── F1.2 - Validate Schema (Page)   ← F1.2-[Feature-Name].md
│   └── F1.3 - Parse Format (Page)      ← F1.3-[Feature-Name].md
├── E2 - Transformation (Page/Folder)    ← E2-[Epic-Name]/README.md
│   └── ...
```

**Rules:**
- If an epic contains subpages (features), it's a **folder** in Notion
- Epic folder content = `README.md` file
- Feature pages = individual markdown files
- Specifications home page = `1-specifications/README.md`

---

## Templates

### Epic Template

**Location:** `docs/templates/epic-template.md`

Use this template for all epic README.md files. The template includes:
- Overview and purpose
- Feature list
- Architecture & design
- Cross-cutting concerns (with references)
- Dependencies
- Technical considerations

### Feature Template

**Location:** `docs/templates/feature-template.md`

Use this template for all feature markdown files. The template includes:
- Description and value proposition
- Business logic (rules, states, edge cases)
- Technical specification (inputs, outputs, contracts)
- Cross-cutting concerns (with references)
- Acceptance criteria (Given-When-Then format)
- Performance requirements
- Testing strategy

---

## Your Task: Create Specifications Structure

### Step 1: Ask Open Questions

**Before creating any structure, ask me open questions** to clarify:

1. **Epic Structure:**
   - Should we use the 6 epics from the README (Ingestion, Field Mapping, Status Computation, Storage, Configuration, API)?
   - Or propose a new epic structure based on research?
   - Are there additional epics needed?

2. **Feature Breakdown:**
   - For each epic, what features should be included?
   - What's the right granularity?
   - What dependencies exist between features?

3. **Legacy Files:**
   - Should `telemetry-system-specification.md`, `status-rules.md`, `schema-specification.md` be moved to `docs/legacy/`?
   - Or kept as reference within specifications?

4. **Reference Materials:**
   - Should we create a `reference/` subfolder in specifications?
   - What reference documents are needed?

5. **Cross-Cutting Features:**
   - Which cross-cutting concerns need actual features vs. just references?
   - For example, does "API key authentication" need a feature, or is it just a security guideline?

### Step 2: Analyze Research Materials

Review the research materials in `docs/brainstorming/` to understand:
- Storage strategy research
- Configuration file research
- Mapping methodology research

**Use this for context only** - don't copy content, but understand the research that informs specifications.

### Step 3: Create Structure

Once questions are answered, create:

1. **Epic Folders:**
   - Create epic folders with proper naming (`E1-[Epic-Name]/`)
   - Create `README.md` in each epic folder using epic template
   - Populate epic README with overview, feature list, architecture

2. **Feature Files:**
   - Create feature markdown files using feature template
   - Number features sequentially within each epic
   - Ensure features are standalone and deliverable

3. **Specifications README:**
   - Update `1-specifications/README.md` to serve as home page
   - Include epic list, status, navigation

4. **Feature Index:**
   - Create `FEATURE_PAGES_INDEX.md` listing all features

5. **Reference Folder (if needed):**
   - Create `reference/` subfolder if reference documents are needed

### Step 4: Handle Legacy Files

- Move validated reference documents to `docs/legacy/` if appropriate
- Or keep them in specifications if they're still needed as reference
- Update links and references

---

## Expected Output

### Deliverables

1. **Epic Folders** with README.md files (using epic template)
2. **Feature Files** (using feature template) - start with structure, we'll fill details iteratively
3. **Updated Specifications README.md** (home page content)
4. **Feature Pages Index** (list of all features)
5. **Reference Folder** (if needed)

### Structure First, Details Later

**Focus on structure first:**
- Create epic folders and README files
- Create feature file structure (can be minimal initially)
- Establish naming conventions
- Set up cross-references

**We'll iterate on details:**
- Fill in feature specifications iteratively
- Refine epic overviews
- Add technical details as we go

---

## Key Principles

1. **Start with Questions:** Ask open questions before creating structure
2. **Structure First:** Focus on folder structure and templates before detailed content
3. **Reference, Don't Duplicate:** Cross-cutting concerns are referenced, not duplicated
4. **Standalone Features:** Each feature delivers value independently
5. **Iterative Approach:** Create structure, then fill details together
6. **Notion-Compatible:** Structure must work for Notion wiki pages

---

## Success Criteria

The specifications structure is successful when:

- ✅ Epic folders are created with proper naming
- ✅ Epic README files exist and follow template
- ✅ Feature files are created (can be minimal initially)
- ✅ Features are properly numbered and named
- ✅ Cross-cutting concerns are referenced (not duplicated)
- ✅ Structure maps cleanly to Notion wiki pages
- ✅ All open questions are answered before structure creation

---

## References

- **Epic Template:** `docs/templates/epic-template.md`
- **Feature Template:** `docs/templates/feature-template.md`
- **Research Materials:** `docs/brainstorming/` (for context only)
- **Legacy Files:** `docs/legacy/` (validated reference documents)
- **Related Documentation:** `notion/2-documentation/` (other sections)

---

**Please start by asking open questions to clarify the epic structure, feature breakdown, and approach before creating any files.**

