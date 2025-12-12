# Specifications Structure FAQ

**Purpose:** This FAQ document captures key decisions, principles, and context about the Fleeti Telemetry Mapping specifications structure. It helps maintain consistency across specifications and provides context for future work.

**Last Updated:** 2025-01-XX

---

## Table of Contents

1. [Epic Structure & Organization](#1-epic-structure--organization)
2. [Databases at Specifications Level](#2-databases-at-specifications-level)
3. [WebSocket Contracts & API Documentation](#3-websocket-contracts--api-documentation)
4. [Configuration Management](#4-configuration-management)
5. [Feature Breakdown & Granularity](#5-feature-breakdown--granularity)
6. [Legacy Files & Reference Materials](#6-legacy-files--reference-materials)
7. [Cross-Cutting Concerns](#7-cross-cutting-concerns)
8. [Documentation Focus & Philosophy](#8-documentation-focus--philosophy)
9. [Naming Conventions](#9-naming-conventions)
10. [Status Computation & Top Status](#10-status-computation--top-status)

---

## 1. Epic Structure & Organization

### Q: What are the 6 main epics for the telemetry system?

**A:** The system is organized into 6 functional epics:

1. **E1 - Ingestion & Provider Integration**: Provider parser architecture, data forwarding, validation, normalization
2. **E2 - Field Mapping & Transformation**: Field catalogs, mapping rules, transformation logic, priority chains
3. **E3 - Status Computation**: Status family computation, state machines, trigger conditions, compatibility matrices
4. **E4 - Storage & Data Management**: Three-tier storage strategy (hot, warm, cold), data access patterns, historical recalculation
5. **E5 - Configuration & Management**: Configuration hierarchy, YAML configuration, field mapping configuration, system management
6. **E6 - API & Consumption**: Telemetry API, WebSocket API, data consumption patterns, frontend integration

**Note:** Epic 6 may evolve to focus on usage/implementation needs rather than detailed contract specifications. Detailed WebSocket contracts will be documented as reference pages alongside databases.

---

### Q: Should Storage & Data Management be split into separate epics?

**A:** No, keep them together as **E4 - Storage & Data Management**. They are closely linked - storage operations depend on data management strategies, and data management operations (like historical recalculation) depend on storage architecture. The breakdown of features within the epic will clarify the relationship.

---

### Q: Should Configuration & Management have a dedicated epic?

**A:** Yes, **E5 - Configuration & Management** should be a dedicated epic. Configuration is a critical cross-cutting concern that affects all other epics. Features within this epic can reference other epics and sub-features as needed.

---

## 2. Databases at Specifications Level

### Q: What databases exist at the specifications level?

**A:** Three critical databases are defined at the specifications level (not within epics):

1. **Provider Fields Database**: Catalog of all provider-specific telemetry fields (Navixy, Teltonika, OEM, etc.)
2. **Fleeti Fields Database**: Complete catalog of all Fleeti telemetry fields (~343+ fields)
3. **Mapping Fields Database**: Field transformation rules linking provider fields to Fleeti fields

**Location:** `notion/2-documentation/1-specifications/databases/`

**Structure:**
```
databases/
├── README.md (overview and how databases connect)
├── provider-fields/
│   └── README.md (what this database contains, column structure, purpose)
├── fleeti-fields/
│   └── README.md (what this database contains, column structure, purpose)
└── mapping-fields/
    └── README.md (what this database contains, column structure, purpose)
```

---

### Q: How are these databases connected?

**A:** The databases are interconnected:
- **Provider Fields** → **Mapping Fields** → **Fleeti Fields**
- Mapping Fields database links provider fields to Fleeti fields with transformation rules
- A dedicated page (`databases/README.md`) illustrates how these databases connect to each other

**Purpose:** These databases serve as the **single source of truth** for field definitions and mappings. The schema specification document (`docs/legacy/fleeti-telemetry-schema-specification.md`) provides the big picture and helps prioritize fields, but the databases are the definitive reference.

---

### Q: What is the relationship between the schema specification and the databases?

**A:** The schema specification (`docs/legacy/fleeti-telemetry-schema-specification.md`) is a **reference document** that:
- Provides the big picture of all Fleeti fields grouped by section
- Shows how provider fields map to Fleeti fields (for prioritization)
- Helps identify which section a new Fleeti field belongs to
- Is **NOT definitive** - databases are the single source of truth

**Workflow:**
1. Use schema specification to understand big picture and prioritize fields
2. Create Fleeti fields in the database (may require iteration as ~300+ provider fields are analyzed)
3. Create provider fields in the database as needed
4. Create mapping rules in the mapping database
5. Generate configuration file from databases
6. Developers implement based on configuration file

**Note:** The schema specification will evolve as fields are refined during database creation.

---

## 3. WebSocket Contracts & API Documentation

### Q: Where should WebSocket contracts be documented?

**A:** WebSocket contracts should be **reference pages alongside databases** at the specifications level, not hidden within Epic 6 features.

**Structure:**
```
notion/2-documentation/1-specifications/
├── databases/ (databases)
├── websocket-contracts/ (reference pages)
│   ├── README.md (overview)
│   ├── live-map-markers.md (markers stream contract)
│   └── [other streams].md
└── api-contracts/ (reference pages)
    ├── README.md (overview)
    └── [API endpoints].md
```

**Rationale:** These contracts will be used frequently by developers (possibly more than feature specs). They should be easily accessible and not buried in epic/feature structure.

---

### Q: What should Epic 6 contain if contracts are reference pages?

**A:** Epic 6 should focus on **usage and implementation needs** rather than detailed contract specifications:

- List different WebSocket contracts that need to be implemented
- Explain **why** each contract is needed (e.g., "live markers contract needed to display markers on map")
- Reference the detailed contract pages in `websocket-contracts/`
- Focus on integration patterns and frontend consumption needs

**Example:** Epic 6 might say "We need a `live.map.markers` WebSocket stream to display markers on the map. See `websocket-contracts/live-map-markers.md` for the detailed contract."

---

### Q: Do WebSocket contracts include mapping rules?

**A:** No. WebSocket contracts are **abstract** - they specify:
- Which Fleeti fields are included in the stream
- Message structure and format
- Subscription parameters
- Update patterns (snapshot, delta)

**Mapping rules** are handled at the transformation layer (Epic 2) and are not part of the WebSocket contract. The contract only specifies the Fleeti fields that will be available, not how provider fields map to them.

---

### Q: How do WebSocket contracts relate to the Fleeti Fields Database?

**A:** WebSocket contracts are **derived from** the Fleeti Fields Database:
- Contracts specify which Fleeti fields are included in each stream
- As new Fleeti fields are added to the database, contracts may be updated
- Contracts reference Fleeti field names and structures from the database
- The database is the source of truth for field definitions

**Example:** The `live.map.markers` contract includes `top_status`, `statuses[]`, `position`, `heading` - all defined in the Fleeti Fields Database.

---

## 4. Configuration Management

### Q: What is the configuration management workflow?

**A:** Configuration management follows this workflow:

1. **Update Databases**: Product team updates Fleeti Fields, Provider Fields, or Mapping Fields databases
2. **Generate Configuration File**: System generates YAML configuration file from databases
3. **Track Changes**: System tracks what changed, when, and why
4. **Notify Developers**: Developers are notified of configuration updates
5. **Deploy Configuration**: Developers update their system with new configuration
6. **Version Control**: Configuration files are versioned for rollback capability
7. **Customer-Specific Configs**: Future support for customer-specific configuration files

**Key Requirements:**
- Track status of configuration updates (pending, ready, deployed)
- Generate configuration files from documentation/databases (possibly from Notion)
- Version configuration files for rollback
- Notify developers when updates are ready
- Support rollback to previous versions if issues occur

---

### Q: What goes in the configuration file vs. what doesn't?

**A:** The configuration file contains:
- Field mappings (direct, prioritized, calculated, transformed)
- Priority rules (source selection when multiple provider fields available)
- I/O to semantic field mappings (with default fallbacks)
- Static field transformations (references to asset metadata)

**The configuration file does NOT contain:**
- Calculation logic (implemented in backend code)
- Complex business rules (implemented in backend code)
- Status computation logic (implemented in backend code)

**Principle:** Configuration file defines **what** to map, not **how** to compute complex logic.

---

### Q: What features should Epic 5 (Configuration) include?

**A:** Epic 5 should include features for:

1. **Configuration Generation**: Generate configuration files from databases/documentation
2. **Configuration Versioning**: Track configuration versions and changes
3. **Configuration Deployment**: Deploy configuration updates to development/production
4. **Configuration Rollback**: Rollback to previous configuration versions
5. **Configuration Validation**: Validate configuration files before deployment
6. **Change Tracking**: Track what changed, when, and notify developers
7. **Customer-Specific Configs**: Support for customer-level configuration overrides (future)

**Focus:** The epic should focus on the **workflow** and **process** of managing configurations, not the detailed YAML structure (which is documented elsewhere).

---

## 5. Feature Breakdown & Granularity

### Q: What is the right granularity for features?

**A:** Features should be:
- **Standalone and deliverable**: Each feature provides value independently
- **Testable**: Clear acceptance criteria
- **Not too large**: Not an entire epic
- **Not too small**: Not a single task (e.g., "parse latitude field")

**Good Examples:**
- "Receive provider packets and validate schema" (ingestion + validation)
- "Save validated packets to cold storage" (storage operation)
- "Transform provider fields to Fleeti format" (transformation)
- "Compute connectivity status" (status computation)

**Bad Examples:**
- "Complete ingestion pipeline" (too large - multiple features)
- "Parse latitude field" (too small - implementation detail)

---

### Q: How should features reference cross-cutting concerns?

**A:** Features should **reference** cross-cutting documentation, not duplicate it:

```markdown
## 5. Cross-Cutting Concerns

### 5.1 Security
**Reference:** [`../../7-security/README.md`](../../7-security/README.md)
This feature must authenticate provider requests using API keys as specified in the security documentation.

### 5.2 Error Handling
**Reference:** [`../../5-operations/error-handling.md`](../../5-operations/error-handling.md)
Transient errors must be retried using exponential backoff as specified in the error handling documentation.
```

**Principle:** Document cross-cutting concerns once in dedicated sections, reference them from features.

---

### Q: When does a cross-cutting concern become a feature?

**A:** A cross-cutting concern becomes a feature when it's:
- **Deliverable**: Produces a working capability
- **Testable**: Has clear acceptance criteria
- **Standalone**: Can be implemented independently

**Examples:**
- ✅ **Feature**: "Implement API key authentication for ingestion endpoint"
- ✅ **Feature**: "Implement dead letter queue for failed transformations"
- ❌ **Guideline**: "Follow security best practices" (reference security docs)
- ❌ **Guideline**: "Handle errors gracefully" (reference error handling docs)

---

## 6. Legacy Files & Reference Materials

### Q: What should happen to existing specification files?

**A:** Existing validated specification files should be **moved to `docs/legacy/`**:

- `telemetry-system-specification.md` → `docs/legacy/`
- `status-rules.md` → `docs/legacy/`
- `schema-specification.md` → `docs/legacy/`

**Rationale:**
- These are reference documents, not active specifications
- They won't live in Notion (only specifications will)
- They provide context but shouldn't be mentioned in new specifications
- Use them to extract necessary information for creating features

---

### Q: What is the difference between `docs/legacy/` and `docs/reference/`?

**A:**
- **`docs/legacy/`**: Validated reference documents from previous work (specifications, schema, status rules)
- **`docs/reference/`**: Reference materials that support specifications but aren't specifications themselves

**Rule:** Everything that **won't live in Notion** should go to `docs/legacy/` or `docs/reference/`. Only specifications that will be copy-pasted to Notion should be in `notion/2-documentation/1-specifications/`.

---

### Q: Should we create a `reference/` folder in specifications?

**A:** Only if necessary for understanding. The user is unsure what this folder would contain. Based on the project structure:
- **Databases** are at specifications level (not in reference folder)
- **WebSocket contracts** are at specifications level (not in reference folder)
- **Legacy documents** go to `docs/legacy/`
- **Reference materials** (provider catalogs, enums) are in `notion/2-documentation/3-reference-materials/`

**Recommendation:** Skip creating a `reference/` folder in specifications unless a clear need emerges.

---

## 7. Cross-Cutting Concerns

### Q: Where are cross-cutting concerns documented?

**A:** Cross-cutting concerns are documented in dedicated sections:

- **Security**: `notion/2-documentation/7-security/`
- **Data Quality**: `notion/2-documentation/6-data-quality/`
- **Operations**: `notion/2-documentation/5-operations/`
- **Deployment**: `notion/2-documentation/9-deployment/`

**In Specifications:**
- Epics and features **reference** these sections
- They **note** specific considerations for that epic/feature
- They **do NOT duplicate** the detailed guidelines

---

### Q: What about authentication that's already implemented?

**A:** For already-implemented features (like Navixy authentication):
- **Document that it exists** (brief note)
- **Don't create irrelevant content** since it's already developed
- **Focus on product needs**, not technical implementation details
- **Reference** if needed, but don't over-specify

**Example:** "Provider authentication is already implemented for Navixy Data Forwarding. See security documentation for details."

---

## 8. Documentation Focus & Philosophy

### Q: What is the focus of specifications - product or technical?

**A:** Specifications focus on **product vision**, not technical implementation details:

- **Focus on:** What the product needs, what Fleeti fields to create, how to map provider data
- **Don't focus on:** Technical implementation details (developers will create this)
- **Balance:** Be straight-to-the-point while guiding developers to ensure they consider important aspects

**Principle:** Provide product vision and requirements. Technical implementation is created by developers.

---

### Q: How detailed should specifications be?

**A:** Specifications should be:
- **Comprehensive** for product requirements and business logic
- **Lean** for technical implementation details
- **Clear** about what needs to be built
- **Flexible** about how it's built (within constraints)

**Example:** Specify "Compute connectivity status based on last_updated_at threshold" but don't specify the exact code structure or algorithm implementation.

---

### Q: What about things that will evolve?

**A:** Specifications are **iterative**:
- Start with structure and high-level features
- Fill in details feature by feature
- Refine as understanding improves
- Databases and configuration files will evolve as fields are refined

**Principle:** Create structure first, fill details iteratively. Don't try to get everything perfect on first pass.

---

## 9. Naming Conventions

### Q: What naming convention should be used for epic folders?

**A:** Use `E[N]-[Epic-Name]/` format:

- `E1-Ingestion-Provider-Integration/`
- `E2-Field-Mapping-Transformation/`
- `E3-Status-Computation/`
- etc.

**Rationale:** The "E" prefix ensures folders sort correctly in file systems and Notion, maintaining the right order.

---

### Q: What naming convention should be used for feature files?

**A:** Use `F[N].[M]-[Feature-Name].md` format:

- `F1.1-Receive-Provider-Packets.md`
- `F1.2-Validate-Packet-Schema.md`
- `F2.1-Load-Configuration.md`
- etc.

**Rules:**
- Number sequentially within epic (F1.1, F1.2, F1.3)
- Can start with F[N].0 if needed (e.g., `F2.0-Initial-Setup.md`)
- Use kebab-case for feature names

---

### Q: What about numbered prefixes in documentation folders?

**A:** Numbered prefixes (`1-specifications/`, `2-field-mappings/`, etc.) are used in the documentation structure to ensure correct sorting in Cursor AI and Notion. Epic folders use `E[N]-` prefix for the same reason.

---

## 10. Status Computation & Top Status

### Q: Should top status computation be a separate feature?

**A:** Yes, top status computation should be a **separate feature** in Epic 3 (Status Computation):

- **Feature:** `F3.5-Compute-Top-Status.md` (or similar)
- **Purpose:** Compute the highest-priority status family for marker display
- **Dependencies:** Depends on all other status families being computed first
- **Key Content:** Priority hierarchy, compatibility matrices, asset type considerations

**Rationale:** Top status is critical for frontend marker display and has specific logic (priority rules, compatibility matrices) that warrants its own feature.

---

### Q: How should status families be broken down?

**A:** Each status family should have its own feature (or features if complex):

- `F3.1-Compute-Connectivity-Status.md`
- `F3.2-Compute-Transit-Status.md`
- `F3.3-Compute-Engine-Status.md`
- `F3.4-Compute-Immobilization-Status.md`
- `F3.5-Compute-Top-Status.md`

**Each feature should include:**
- Status family logic and rules
- State machines and transitions
- Trigger conditions
- Required telemetry fields
- Compatibility matrices (if applicable)

---

### Q: What about status compatibility matrices?

**A:** Compatibility matrices define which status families are compatible with which asset types. These should be:
- Documented in status computation features
- Referenced in top status computation feature
- Used to determine which statuses can be computed for each asset type

**Example:** Immobilization status only applies to assets with immobilizer accessories. This compatibility rule should be documented in the immobilization status feature and referenced in top status computation.

---

## Additional Context

### Mobile App Specifications Reference

The mobile app specifications (`c:\Git\Fleeti\Notion & Figma Extraction\projects\mobile-app-live-map\specifications\`) provide context for:
- Frontend needs and requirements
- WebSocket contract examples (see `E3-Markers/F3.1-Rendering-Markers-for-Vehicles.md`)
- Real-time data requirements
- Marker display logic and top status usage

**Use this as reference** to understand what the frontend needs, but remember this is for web app (not mobile), so there may be differences.

---

### Schema Specification Reference

The schema specification (`docs/legacy/fleeti-telemetry-schema-specification.md`) is a **critical reference** that:
- Shows the big picture of all Fleeti fields
- Groups provider fields into Fleeti field sections
- Helps prioritize which fields to implement first
- Provides mapping hints (which provider fields map to which Fleeti fields)

**Important:** This document is **not definitive** - databases are the single source of truth. Use it for understanding and prioritization, but field definitions come from databases.

---

### Data Forwarding Context

Data Forwarding from Navixy:
- ✅ Already tested and validated
- ✅ Authentication already implemented
- ✅ Provides real-time telemetry packets
- ✅ ~340 distinct fields identified from Navixy

**In Specifications:** Document that Data Forwarding exists and is working. Don't over-specify authentication since it's already implemented. Focus on how telemetry flows through the system.

---

## Key Principles Summary

1. **Structure First, Details Later**: Create epic/feature structure, fill details iteratively
2. **Reference, Don't Duplicate**: Cross-cutting concerns documented once, referenced from features
3. **Product Focus**: Focus on what product needs, not technical implementation
4. **Databases as Source of Truth**: Databases define fields, not reference documents
5. **Iterative Refinement**: Specifications evolve as understanding improves
6. **Notion-Compatible**: Structure must work for Notion wiki pages
7. **Standalone Features**: Each feature delivers value independently
8. **Clear Contracts**: WebSocket/API contracts easily accessible, not buried in features

---

**Note:** This FAQ should be updated as decisions are made and understanding evolves. It serves as a living document to maintain consistency across specifications work.

