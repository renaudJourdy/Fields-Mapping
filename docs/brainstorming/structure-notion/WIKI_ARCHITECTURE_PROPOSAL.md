# Notion Wiki Architecture Proposal

**Document Version:** 1.0  
**Date:** 2025-01-XX  
**Status:** Proposal - Pending Approval  
**Owner:** Wiki Architecture Team

---

## Executive Summary

This document proposes a comprehensive wiki architecture for "Fleeti Fields - Telemetry Mapping" that serves as the single source of truth for all project documentation. The architecture supports multiple audiences (stakeholders, developers, product owners), enables collaborative contributions, and provides bidirectional sync with local markdown files.

**Key Features:**
- **Multi-audience support:** Clear entry points for stakeholders, developers, and product owners
- **Comprehensive coverage:** All documentation types (specs, guides, status, technical)
- **Collaborative workspace:** Developer contribution areas with guidelines
- **Bidirectional sync:** MCP-enabled sync with local markdown files
- **Well-organized:** Easy navigation and discovery

---

## Architecture Principles

1. **Single Source of Truth:** All documentation in one organized wiki
2. **Multi-Audience Support:** Accessible to stakeholders and developers
3. **Collaborative:** Developers can contribute their own pages
4. **Comprehensive:** Covers all aspects (specs, guides, status, technical)
5. **Well-Organized:** Easy navigation and discovery
6. **Maintainable:** Clear structure, guidelines, and sync workflow
7. **MCP-Enabled:** Leverages Notion MCP integration in Cursor

---

## Complete Wiki Structure

```
✨ Fleeti Fields - Telemetry Mapping (Root Wiki)
│
├── 📋 Overview & Vision
│   ├── README.md (Section overview and navigation)
│   ├── Project Overview
│   │   └── High-level project description, goals, stakeholders
│   ├── Objectives & Goals
│   │   └── Primary objectives, success criteria, key requirements
│   ├── Architecture Overview
│   │   └── System Overview (existing - move from root)
│   └── Key Concepts
│       └── Core concepts, terminology, mental models
│
├── 📚 Documentation
│   ├── README.md (Section overview and navigation)
│   ├── Specifications
│   │   ├── README.md
│   │   ├── Telemetry System Specification
│   │   │   └── System Overview (existing - move from root)
│   │   ├── Status Rules
│   │   │   └── telemetry-status-rules.md (migrate from Wiki/)
│   │   └── Schema Specification
│   │       └── Telemetry - Full Schema (existing - move from root)
│   ├── Requirements
│   │   ├── README.md
│   │   ├── Storage Product Requirements
│   │   │   └── telemetry-storage-product-requirements.md (migrate from working/)
│   │   └── Field Mapping Requirements
│   │       └── Field mapping requirements and priorities
│   ├── Field Mappings
│   │   ├── README.md
│   │   ├── Fleeti Fields Catalog
│   │   │   └── Complete catalog of all Fleeti telemetry fields
│   │   ├── Provider Fields Catalog
│   │   │   └── Provider-specific field catalogs
│   │   └── Mapping Rules
│   │       └── Field mapping rules and transformation logic
│   └── Reference Materials
│       ├── README.md
│       ├── Provider Catalogs
│       │   ├── Navixy Field Catalog (existing - CSV attachment)
│       │   ├── Teltonika AVL Catalog (existing - CSV attachment)
│       │   └── Teltonika FMB140 Catalog (existing - CSV attachment)
│       ├── Enum Definitions
│       │   ├── response.json (migrate from docs/enums/)
│       │   └── Enum Documentation (migrate from docs/enums/README.md)
│       └── Legacy Documentation
│           └── Historical mapping documents (migrate from docs/legacy/)
│
├── 🛠️ Developer Resources
│   ├── README.md (Section overview and navigation)
│   ├── Getting Started
│   │   ├── README.md
│   │   ├── Quick Start Guide
│   │   ├── Development Setup
│   │   └── First Contribution
│   ├── Implementation Guides
│   │   ├── README.md
│   │   ├── Field Mapping Implementation
│   │   │   └── How to implement field mappings
│   │   ├── Status Computation Implementation
│   │   │   └── How to implement status computation
│   │   └── Storage Strategy Implementation
│   │       └── How to implement storage tiers
│   ├── API Documentation
│   │   ├── README.md
│   │   ├── Telemetry API
│   │   ├── Configuration API
│   │   └── WebSocket API
│   ├── Configuration Guide
│   │   ├── README.md
│   │   ├── YAML Configuration
│   │   ├── Configuration Hierarchy
│   │   └── Configuration Examples
│   ├── Technical Specifications
│   │   ├── README.md
│   │   ├── Storage Strategy Analysis
│   │   │   └── expert-review-storage-strategy-analysis.md (migrate from working/)
│   │   └── Expert Reviews
│   │       └── Technical analysis documents
│   ├── Developer Guidelines
│   │   ├── README.md
│   │   ├── Documentation Standards
│   │   ├── Notion Methodology
│   │   │   └── notion-documentation-methodology.md (migrate from working/)
│   │   └── Contribution Guidelines
│   │       └── How to contribute to the wiki
│   └── Troubleshooting
│       ├── README.md
│       ├── Common Issues
│       ├── Debugging Guide
│       └── FAQ
│
├── 📝 Project Management
│   ├── README.md (Section overview and navigation)
│   ├── Current Status
│   │   └── Project status dashboard, milestones, blockers
│   ├── Ongoing Work
│   │   └── Active work items, in-progress tasks
│   ├── Roadmap
│   │   └── Future plans, upcoming features, timeline
│   ├── Decision Records
│   │   ├── README.md
│   │   └── [Decision-001] Storage Strategy
│   │   └── [Decision-002] Field Mapping Approach
│   │   └── ... (more decision records)
│   └── Meeting Notes
│       └── Meeting notes and action items
│
├── 🔧 Technical Pages (Developer-Contributed)
│   ├── README.md (Contribution guidelines, templates, examples)
│   ├── [Developer Name]/
│   │   ├── README.md (Developer's page overview)
│   │   ├── Implementation Notes/
│   │   │   └── Notes on implementations, learnings, gotchas
│   │   ├── Technical Decisions/
│   │   │   └── Technical decisions and rationale
│   │   └── Code Examples/
│   │       └── Code snippets, examples, patterns
│   └── [Team Name]/
│       └── Team-specific technical pages
│
└── 📖 Guidelines & Standards
    ├── README.md (Section overview and navigation)
    ├── Documentation Standards
    │   └── Format guidelines, writing style, multi-audience considerations
    ├── Wiki Organization Guide
    │   └── Where to add content, naming conventions, structure guidelines
    ├── Contribution Guidelines
    │   └── How to contribute, review process, sync workflow
    └── Sync Workflow
        └── How to sync between Notion and local files
```

---

## Section Details

### 📋 Overview & Vision

**Purpose:** Provide high-level project understanding for all audiences.

**Audience:** Stakeholders, Product Owners, New Team Members, Developers

**Content Types:**
- Project overview and description
- Objectives and goals
- Architecture overview
- Key concepts and terminology

**Entry Points:**
- **Stakeholders:** Project Overview, Objectives & Goals
- **New Team Members:** Start here for project understanding
- **Developers:** Architecture Overview for system understanding

**Organization:**
- Progressive disclosure (overview → objectives → architecture → concepts)
- Visual hierarchy with clear headings
- Links to detailed documentation

---

### 📚 Documentation

**Purpose:** Comprehensive reference documentation for all aspects of the system.

**Audience:** Developers, Product Owners, Technical Stakeholders

**Content Types:**
- Technical specifications
- Product requirements
- Field catalogs and mappings
- Reference materials (catalogs, enums, legacy docs)

**Subsections:**

#### Specifications
- **Telemetry System Specification:** High-level system architecture and design
- **Status Rules:** Canonical status computation logic
- **Schema Specification:** Complete field reference (300+ fields)

#### Requirements
- **Storage Product Requirements:** Product-focused storage requirements
- **Field Mapping Requirements:** Field mapping requirements and priorities

#### Field Mappings
- **Fleeti Fields Catalog:** Complete catalog of all Fleeti telemetry fields
- **Provider Fields Catalog:** Provider-specific field catalogs
- **Mapping Rules:** Field mapping rules and transformation logic

#### Reference Materials
- **Provider Catalogs:** CSV files with provider field catalogs
- **Enum Definitions:** API enumeration definitions and documentation
- **Legacy Documentation:** Historical documents for reference

**Organization:**
- Grouped by type (specs, requirements, mappings, reference)
- Clear navigation between related documents
- Searchable and indexed

---

### 🛠️ Developer Resources

**Purpose:** Practical guides and resources for developers implementing the system.

**Audience:** Developers

**Content Types:**
- Getting started guides
- Implementation guides
- API documentation
- Configuration guides
- Technical specifications
- Developer guidelines
- Troubleshooting guides

**Subsections:**

#### Getting Started
- **Quick Start Guide:** Fast onboarding for new developers
- **Development Setup:** Environment setup, dependencies, tools
- **First Contribution:** How to make your first contribution

#### Implementation Guides
- **Field Mapping Implementation:** Step-by-step guide for implementing field mappings
- **Status Computation Implementation:** How to implement status computation logic
- **Storage Strategy Implementation:** How to implement storage tiers

#### API Documentation
- **Telemetry API:** API endpoints for telemetry data
- **Configuration API:** API endpoints for configuration management
- **WebSocket API:** Real-time WebSocket API documentation

#### Configuration Guide
- **YAML Configuration:** YAML configuration file structure and syntax
- **Configuration Hierarchy:** How configuration hierarchy works
- **Configuration Examples:** Example configurations for common scenarios

#### Technical Specifications
- **Storage Strategy Analysis:** Detailed technical analysis of storage strategy
- **Expert Reviews:** Technical analysis documents and expert reviews

#### Developer Guidelines
- **Documentation Standards:** How to write documentation
- **Notion Methodology:** How to use Notion for field documentation
- **Contribution Guidelines:** How to contribute to the project

#### Troubleshooting
- **Common Issues:** Frequently encountered issues and solutions
- **Debugging Guide:** How to debug telemetry issues
- **FAQ:** Frequently asked questions

**Organization:**
- Progressive learning path (getting started → guides → specs → troubleshooting)
- Clear navigation between related guides
- Code examples and practical tips

---

### 📝 Project Management

**Purpose:** Track project progress, decisions, and ongoing work.

**Audience:** Product Owners, Stakeholders, Team Leads

**Content Types:**
- Project status and milestones
- Ongoing work items
- Roadmap and future plans
- Decision records
- Meeting notes

**Subsections:**

#### Current Status
- Project status dashboard
- Milestones and achievements
- Blockers and risks
- Progress metrics

#### Ongoing Work
- Active work items
- In-progress tasks
- Sprint/iteration planning
- Task assignments

#### Roadmap
- Future plans and features
- Timeline and milestones
- Priority and dependencies
- Resource planning

#### Decision Records
- **Format:** [Decision-XXX] Title
- **Content:** Context, decision, rationale, consequences
- **Examples:**
  - [Decision-001] Storage Strategy
  - [Decision-002] Field Mapping Approach
  - [Decision-003] Configuration System Design

#### Meeting Notes
- Meeting notes and summaries
- Action items and owners
- Decisions made in meetings
- Follow-up items

**Organization:**
- Time-based organization (recent first)
- Decision records indexed by topic
- Clear status indicators

---

### 🔧 Technical Pages (Developer-Contributed)

**Purpose:** Collaborative workspace for developers to document their work and share knowledge.

**Audience:** Developers

**Content Types:**
- Implementation notes
- Technical decisions
- Code examples
- Best practices
- Lessons learned

**Structure:**
```
Technical Pages/
├── README.md
│   └── Contribution guidelines, templates, examples
│
├── [Developer Name]/
│   ├── README.md
│   │   └── Developer's page overview, contact info
│   ├── Implementation Notes/
│   │   └── Notes on implementations, learnings, gotchas
│   ├── Technical Decisions/
│   │   └── Technical decisions and rationale
│   └── Code Examples/
│       └── Code snippets, examples, patterns
│
└── [Team Name]/
    └── Team-specific technical pages
```

**Templates:**

**Implementation Note Template:**
```markdown
# [Feature/Component Name] Implementation Notes

**Author:** [Developer Name]  
**Date:** [Date]  
**Status:** [In Progress / Complete / Deprecated]

## Overview
[Brief overview of what was implemented]

## Implementation Details
[Detailed implementation notes]

## Challenges & Solutions
[Challenges encountered and how they were solved]

## Lessons Learned
[Key learnings and takeaways]

## References
[Links to related documentation, code, etc.]
```

**Technical Decision Template:**
```markdown
# [Decision Title]

**Author:** [Developer Name]  
**Date:** [Date]  
**Status:** [Proposed / Accepted / Rejected]

## Context
[Background and context for the decision]

## Decision
[The decision that was made]

## Rationale
[Why this decision was made]

## Alternatives Considered
[Other options that were considered]

## Consequences
[Expected consequences and trade-offs]

## References
[Links to related documentation, discussions, etc.]
```

**Code Example Template:**
```markdown
# [Example Title]

**Author:** [Developer Name]  
**Date:** [Date]  
**Language:** [Programming Language]

## Description
[What this example demonstrates]

## Code
\`\`\`[language]
[Code snippet]
\`\`\`

## Usage
[How to use this example]

## Notes
[Additional notes or considerations]
```

**Guidelines:**
- Use developer name or team name for folder/page name
- Follow template structure for consistency
- Keep content focused and relevant
- Update README.md with page overview
- Optional peer review process

---

### 📖 Guidelines & Standards

**Purpose:** Maintain documentation quality and consistency across the wiki.

**Audience:** All Contributors

**Content Types:**
- Documentation standards
- Wiki organization guidelines
- Contribution guidelines
- Sync workflow documentation

**Subsections:**

#### Documentation Standards
- Format guidelines (markdown, structure, style)
- Writing style (tone, audience, clarity)
- Multi-audience considerations (stakeholder vs developer content)
- Technical vs stakeholder content guidelines

#### Wiki Organization Guide
- Where to add new content
- How to structure pages
- Naming conventions
- Content categorization
- Navigation best practices

#### Contribution Guidelines
- How developers can add pages
- Where to add technical notes
- Review process
- Quality standards
- Collaboration guidelines

#### Sync Workflow
- How to sync between Notion and local files
- MCP-enabled sync process
- Conflict resolution
- Version control
- Best practices

**Organization:**
- Reference documentation format
- Clear examples and templates
- Quick reference guides

---

## Multi-Audience Navigation

### Stakeholder Navigation Path

**Entry Point:** Overview & Vision → Project Overview

**Recommended Path:**
1. **Overview & Vision → Project Overview** (Understand the project)
2. **Overview & Vision → Objectives & Goals** (Understand goals)
3. **Project Management → Current Status** (Check progress)
4. **Project Management → Roadmap** (See future plans)
5. **Documentation → Requirements** (Understand product requirements)

**Quick Links:**
- Project Status Dashboard
- Roadmap
- Key Decisions
- Product Requirements

---

### Developer Navigation Path

**Entry Point:** Developer Resources → Getting Started

**Recommended Path:**
1. **Developer Resources → Getting Started** (Onboarding)
2. **Documentation → Specifications** (Understand system design)
3. **Developer Resources → Implementation Guides** (Learn how to implement)
4. **Documentation → Field Mappings** (Understand field mappings)
5. **Developer Resources → API Documentation** (Learn API usage)
6. **Developer Resources → Troubleshooting** (Solve problems)

**Quick Links:**
- Getting Started Guide
- Implementation Guides
- API Documentation
- Field Mappings Catalog
- Troubleshooting Guide

---

### Product Owner Navigation Path

**Entry Point:** Overview & Vision → Architecture Overview

**Recommended Path:**
1. **Overview & Vision → Architecture Overview** (Understand architecture)
2. **Documentation → Requirements** (Review requirements)
3. **Documentation → Specifications** (Review specifications)
4. **Project Management → Decision Records** (Review decisions)
5. **Project Management → Roadmap** (Plan future work)

**Quick Links:**
- Architecture Overview
- Requirements
- Decision Records
- Roadmap
- Current Status

---

## Content Migration Plan

### Phase 1: High-Priority Content

**Status Rules:**
- **Source:** `Wiki/telemetry-status-rules.md`
- **Destination:** Documentation → Specifications → Status Rules
- **Action:** Migrate content, maintain formatting

**Storage Product Requirements:**
- **Source:** `working/telemetry-storage-product-requirements.md`
- **Destination:** Documentation → Requirements → Storage Product Requirements
- **Action:** Migrate content, maintain structure

**Storage Strategy Analysis:**
- **Source:** `working/expert-review-storage-strategy-analysis.md`
- **Destination:** Developer Resources → Technical Specifications → Storage Strategy Analysis
- **Action:** Migrate content, maintain technical details

**Notion Methodology:**
- **Source:** `working/notion-documentation-methodology.md`
- **Destination:** Developer Resources → Developer Guidelines → Notion Methodology
- **Action:** Migrate content, maintain methodology details

### Phase 2: Medium-Priority Content

**Enum Definitions:**
- **Source:** `docs/enums/response.json` and `docs/enums/README.md`
- **Destination:** Documentation → Reference Materials → Enum Definitions
- **Action:** Migrate JSON and documentation

**Getting Started Guide:**
- **Source:** Create new
- **Destination:** Developer Resources → Getting Started
- **Action:** Create comprehensive getting started guide

**Implementation Guides:**
- **Source:** Create new
- **Destination:** Developer Resources → Implementation Guides
- **Action:** Create implementation guides based on existing documentation

### Phase 3: Low-Priority Content

**Legacy Documentation:**
- **Source:** `docs/legacy/`
- **Destination:** Documentation → Reference Materials → Legacy Documentation
- **Action:** Migrate for historical reference

**Troubleshooting Guides:**
- **Source:** Create new
- **Destination:** Developer Resources → Troubleshooting
- **Action:** Create troubleshooting guides based on common issues

---

## Local Folder Structure

### Proposed Structure

```
notion-wiki/
├── README.md                    # Sync workflow and structure guide
├── .notion-sync.json           # Sync metadata (last sync, version, etc.)
├── .notion-version.json        # Version history
│
├── fleeti-fields-telemetry-mapping/  # Root wiki page
│   ├── README.md               # Main wiki page content
│   │
│   ├── overview-vision/        # Overview & Vision section
│   │   ├── README.md
│   │   ├── project-overview.md
│   │   ├── objectives-goals.md
│   │   └── architecture-overview.md
│   │
│   ├── documentation/          # Documentation section
│   │   ├── README.md
│   │   ├── specifications/
│   │   │   ├── README.md
│   │   │   ├── telemetry-system-specification.md
│   │   │   ├── status-rules.md
│   │   │   └── schema-specification.md
│   │   ├── requirements/
│   │   │   ├── README.md
│   │   │   ├── storage-product-requirements.md
│   │   │   └── field-mapping-requirements.md
│   │   ├── field-mappings/
│   │   │   ├── README.md
│   │   │   ├── fleeti-fields-catalog.md
│   │   │   ├── provider-fields-catalog.md
│   │   │   └── mapping-rules.md
│   │   └── reference-materials/
│   │       ├── README.md
│   │       ├── provider-catalogs/
│   │       ├── enum-definitions/
│   │       └── legacy-documentation/
│   │
│   ├── developer-resources/    # Developer Resources section
│   │   ├── README.md
│   │   ├── getting-started/
│   │   ├── implementation-guides/
│   │   ├── api-documentation/
│   │   ├── configuration-guide/
│   │   ├── technical-specifications/
│   │   ├── developer-guidelines/
│   │   └── troubleshooting/
│   │
│   ├── project-management/     # Project Management section
│   │   ├── README.md
│   │   ├── current-status.md
│   │   ├── ongoing-work.md
│   │   ├── roadmap.md
│   │   ├── decision-records/
│   │   └── meeting-notes/
│   │
│   ├── technical-pages/       # Developer-Contributed section
│   │   ├── README.md
│   │   └── [developer-name]/
│   │
│   └── guidelines-standards/    # Guidelines section
│       ├── README.md
│       ├── documentation-standards.md
│       ├── wiki-organization-guide.md
│       ├── contribution-guidelines.md
│       └── sync-workflow.md
│
└── .gitignore
```

### Key Principles

- **Mirror Notion Structure:** Local folder structure exactly mirrors Notion wiki structure
- **Each Notion Page → Markdown File:** Each Notion page becomes a markdown file
- **Each Notion Subpage → Subfolder with README.md:** Subpages become subfolders with README.md
- **Maintain Hierarchy:** Preserve page hierarchy in folder structure
- **Support Multiple Content Types:** Support markdown, CSV attachments, JSON files

---

## Sync System Design

### MCP-Enabled Sync

**Pull from Notion (MCP):**
1. Use MCP functions to fetch wiki pages
2. Convert Notion content to markdown
3. Create folder structure matching Notion hierarchy
4. Maintain page relationships

**Push to Notion (MCP):**
1. Read local markdown files
2. Create/update Notion pages via MCP
3. Maintain hierarchy
4. Handle conflicts

### Sync Metadata

**`.notion-sync.json`:**
```json
{
  "last_sync": "2025-01-15T10:30:00Z",
  "sync_direction": "bidirectional",
  "notion_root_page_id": "2b23e766-c901-8058-a86c-cb0d70ea3d33",
  "version": "1.0.0",
  "pages": {
    "overview-vision/project-overview.md": {
      "notion_page_id": "abc123",
      "last_modified_notion": "2025-01-15T09:00:00Z",
      "last_modified_local": "2025-01-15T10:00:00Z",
      "sync_status": "synced"
    }
  }
}
```

**`.notion-version.json`:**
```json
{
  "versions": [
    {
      "version": "1.0.0",
      "date": "2025-01-15T10:30:00Z",
      "changes": ["Initial wiki structure", "Migrated status rules"]
    }
  ]
}
```

### Conflict Resolution

**Conflict Detection:**
- Compare `last_modified_notion` with `last_modified_local`
- Flag conflicts when both modified since last sync

**Resolution Process:**
1. Detect conflict
2. Show both versions
3. Manual merge or choose version
4. Update sync metadata
5. Complete sync

---

## Implementation Checklist

### Phase 1: Structure Setup
- [ ] Create wiki structure in Notion
- [ ] Set up section templates
- [ ] Create guidelines pages
- [ ] Set up developer contribution area

### Phase 2: Content Migration
- [ ] Migrate Status Rules
- [ ] Migrate Storage Product Requirements
- [ ] Migrate Storage Strategy Analysis
- [ ] Migrate Notion Methodology
- [ ] Migrate Enum Definitions
- [ ] Create Getting Started guide
- [ ] Create Implementation Guides

### Phase 3: Sync Setup
- [ ] Design local folder structure
- [ ] Create MCP-enabled sync scripts
- [ ] Test sync workflows
- [ ] Document sync process
- [ ] Set up version control

### Phase 4: Documentation
- [ ] Create wiki organization guide
- [ ] Create contribution guidelines
- [ ] Create sync workflow documentation
- [ ] Train team on wiki usage

---

## Success Criteria

1. **Single Source of Truth:** All documentation accessible in one place
2. **Multi-Audience Support:** Clear entry points for all audiences
3. **Easy Navigation:** Users can find content quickly
4. **Collaborative:** Developers can contribute easily
5. **Synced:** Local files stay in sync with Notion
6. **Maintainable:** Clear structure and guidelines ensure quality

---

**End of Wiki Architecture Proposal**

