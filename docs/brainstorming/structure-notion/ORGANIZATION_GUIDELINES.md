# Wiki Organization Guidelines

**Document Version:** 1.0  
**Date:** 2025-01-XX  
**Status:** Guidelines - Active  
**Owner:** Documentation Team

---

## Purpose

This document provides guidelines for organizing content in the "Fleeti Fields - Telemetry Mapping" Notion wiki. It helps contributors understand where to add content, how to structure pages, and how to maintain consistency across the wiki.

---

## Wiki Structure Overview

The wiki is organized into six main sections:

1. **📋 Overview & Vision** - High-level project understanding
2. **📚 Documentation** - Comprehensive reference documentation
3. **🛠️ Developer Resources** - Practical guides for developers
4. **📝 Project Management** - Project progress and decisions
5. **🔧 Technical Pages** - Developer-contributed content
6. **📖 Guidelines & Standards** - Documentation standards and guidelines

---

## Where to Add Content

### For Stakeholders

**Add content to:**
- **Overview & Vision → Project Overview** - High-level project updates
- **Overview & Vision → Objectives & Goals** - Goal updates, success metrics
- **Project Management → Current Status** - Status updates, milestones
- **Project Management → Roadmap** - Future plans, timeline updates
- **Documentation → Requirements** - Product requirements, feature requests

**Content types:**
- Project status updates
- Business objectives
- Product requirements
- Roadmap items
- Decision summaries

---

### For Developers

**Add content to:**
- **Documentation → Specifications** - Technical specifications, design docs
- **Developer Resources → Implementation Guides** - Step-by-step implementation guides
- **Developer Resources → API Documentation** - API endpoint documentation
- **Developer Resources → Technical Specifications** - Technical analysis, expert reviews
- **Developer Resources → Troubleshooting** - Common issues, debugging guides
- **🔧 Technical Pages → [Your Name]** - Your own technical notes and contributions

**Content types:**
- Implementation guides
- API documentation
- Technical specifications
- Code examples
- Troubleshooting guides
- Technical decisions

---

### For Product Owners

**Add content to:**
- **Overview & Vision → Architecture Overview** - Architecture updates
- **Documentation → Requirements** - Product requirements, feature specs
- **Documentation → Specifications** - System specifications
- **Project Management → Decision Records** - Decision documentation
- **Project Management → Roadmap** - Product roadmap, priorities

**Content types:**
- Product requirements
- Feature specifications
- Decision records
- Roadmap items
- Architecture decisions

---

## Content Categorization

### Specifications

**Location:** Documentation → Specifications

**Content:**
- Technical system specifications
- Design documents
- Architecture documents
- Status computation rules
- Schema specifications

**Examples:**
- Telemetry System Specification
- Status Rules
- Schema Specification

---

### Requirements

**Location:** Documentation → Requirements

**Content:**
- Product requirements
- Feature requirements
- Functional requirements
- Non-functional requirements

**Examples:**
- Storage Product Requirements
- Field Mapping Requirements

---

### Implementation Guides

**Location:** Developer Resources → Implementation Guides

**Content:**
- Step-by-step implementation guides
- How-to guides
- Best practices
- Code examples

**Examples:**
- Field Mapping Implementation
- Status Computation Implementation
- Storage Strategy Implementation

---

### Reference Materials

**Location:** Documentation → Reference Materials

**Content:**
- Provider catalogs (CSV files)
- Enum definitions
- Legacy documentation
- API references

**Examples:**
- Navixy Field Catalog
- Enum Definitions
- Legacy Mapping Documents

---

### Technical Analysis

**Location:** Developer Resources → Technical Specifications

**Content:**
- Expert reviews
- Technical analysis
- Architecture analysis
- Performance analysis

**Examples:**
- Storage Strategy Analysis
- Expert Review Documents

---

### Project Management

**Location:** Project Management

**Content:**
- Project status
- Ongoing work
- Roadmap
- Decision records
- Meeting notes

**Examples:**
- Current Status
- Decision Records
- Roadmap

---

## Page Structure Guidelines

### Standard Page Structure

**Title:** Clear, descriptive title

**Content:**
1. **Overview/Introduction** - Brief overview of the page content
2. **Main Content** - Detailed content organized with headings
3. **Related Links** - Links to related pages
4. **Last Updated** - Date and author of last update

**Example:**
```markdown
# [Page Title]

## Overview
[Brief overview of what this page covers]

## [Main Section 1]
[Content]

## [Main Section 2]
[Content]

## Related Links
- [Related Page 1](link)
- [Related Page 2](link)

**Last Updated:** 2025-01-15 by [Author Name]
```

---

### Specification Page Structure

**Title:** [Component Name] Specification

**Content:**
1. **Purpose** - What this specification defines
2. **Scope** - What's included/excluded
3. **Requirements** - Detailed requirements
4. **Implementation** - Implementation details (if applicable)
5. **References** - Links to related documentation

---

### Implementation Guide Structure

**Title:** How to [Action]

**Content:**
1. **Prerequisites** - What you need before starting
2. **Step-by-Step Guide** - Detailed steps
3. **Code Examples** - Code snippets and examples
4. **Troubleshooting** - Common issues and solutions
5. **Next Steps** - What to do after completing

---

### Decision Record Structure

**Title:** [Decision-XXX] [Decision Title]

**Content:**
1. **Context** - Background and context
2. **Decision** - The decision made
3. **Rationale** - Why this decision was made
4. **Alternatives Considered** - Other options considered
5. **Consequences** - Expected consequences and trade-offs

---

## Naming Conventions

### Page Titles

**Format:** Use clear, descriptive titles

**Examples:**
- ✅ "Telemetry System Specification"
- ✅ "How to Implement Field Mappings"
- ✅ "Storage Strategy Analysis"
- ❌ "Spec"
- ❌ "Field Mapping Stuff"
- ❌ "Storage"

### File Names (for local sync)

**Format:** Use kebab-case

**Examples:**
- ✅ `telemetry-system-specification.md`
- ✅ `field-mapping-implementation.md`
- ✅ `storage-strategy-analysis.md`
- ❌ `Telemetry System Specification.md`
- ❌ `field_mapping_implementation.md`

### Section Names

**Format:** Use descriptive section names with emojis for visual navigation

**Examples:**
- ✅ "📋 Overview & Vision"
- ✅ "🛠️ Developer Resources"
- ✅ "📝 Project Management"

---

## Content Formatting

### Markdown Guidelines

**Headings:**
- Use `#` for page title (H1)
- Use `##` for main sections (H2)
- Use `###` for subsections (H3)
- Use `####` for sub-subsections (H4)

**Lists:**
- Use bullet points (`-`) for unordered lists
- Use numbers (`1.`) for ordered lists
- Use checkboxes (`- [ ]`) for task lists

**Code:**
- Use backticks (`` ` ``) for inline code
- Use code blocks (```) for code snippets
- Specify language for syntax highlighting

**Links:**
- Use `[Link Text](URL)` for external links
- Use `[Page Title](notion://page-id)` for Notion page links
- Use relative paths for local file links

**Tables:**
- Use markdown table syntax
- Include header row
- Align columns appropriately

---

### Writing Style

**Tone:**
- **Stakeholder content:** Clear, non-technical, business-focused
- **Developer content:** Technical, detailed, implementation-focused
- **Mixed content:** Balance technical accuracy with readability

**Clarity:**
- Use clear, concise language
- Avoid jargon when writing for stakeholders
- Define technical terms when first used
- Use examples to illustrate concepts

**Structure:**
- Start with overview/introduction
- Organize content logically
- Use headings to break up content
- Include related links at the end

---

## Multi-Audience Considerations

### Stakeholder Content

**Characteristics:**
- High-level overviews
- Business-focused language
- Clear value propositions
- Visual summaries (tables, diagrams)

**Avoid:**
- Technical implementation details
- Code examples
- Deep technical jargon
- Internal system details

**Examples:**
- Project Overview
- Objectives & Goals
- Product Requirements
- Roadmap

---

### Developer Content

**Characteristics:**
- Technical details
- Implementation guides
- Code examples
- API documentation
- Troubleshooting guides

**Include:**
- Step-by-step instructions
- Code snippets
- Configuration examples
- Common pitfalls
- Best practices

**Examples:**
- Implementation Guides
- API Documentation
- Technical Specifications
- Troubleshooting Guides

---

### Mixed Content

**Characteristics:**
- Balance technical accuracy with readability
- Provide both high-level and detailed views
- Use progressive disclosure (overview → details)

**Structure:**
- Start with stakeholder-friendly overview
- Provide detailed technical sections
- Link to related documentation

**Examples:**
- Architecture Overview
- System Specification
- Storage Strategy

---

## Developer Contribution Guidelines

### Adding Technical Pages

**Location:** 🔧 Technical Pages → [Your Name]

**Structure:**
```
[Your Name]/
├── README.md (Your page overview)
├── Implementation Notes/
├── Technical Decisions/
└── Code Examples/
```

**Process:**
1. Create your folder/page in "Technical Pages"
2. Add README.md with overview
3. Add content following templates
4. Update your README.md with links to new content

**Templates:**
- See "Technical Pages → README.md" for templates
- Use templates for consistency
- Customize as needed for your use case

---

### Adding Implementation Guides

**Location:** Developer Resources → Implementation Guides

**Process:**
1. Check if similar guide exists
2. Create new page or update existing
3. Follow Implementation Guide structure
4. Include code examples
5. Add troubleshooting section
6. Link from Getting Started guide

---

### Adding API Documentation

**Location:** Developer Resources → API Documentation

**Process:**
1. Document endpoint details
2. Include request/response examples
3. Document authentication
4. Include error handling
5. Add code examples

---

## Maintenance Guidelines

### Regular Updates

**Frequency:**
- Update status pages weekly
- Update ongoing work daily
- Update documentation as changes occur
- Review and update quarterly

**Responsibilities:**
- **Project Manager:** Update project status, roadmap
- **Developers:** Update implementation guides, technical docs
- **Product Owner:** Update requirements, decision records
- **All Contributors:** Keep your technical pages updated

---

### Content Review

**Review Process:**
1. Self-review before publishing
2. Peer review for major changes (optional)
3. Update "Last Updated" date
4. Link from related pages

**Quality Checklist:**
- [ ] Clear title and structure
- [ ] Correct spelling and grammar
- [ ] Proper formatting
- [ ] Related links included
- [ ] Last updated date set
- [ ] Appropriate for target audience

---

### Archiving

**When to Archive:**
- Content is superseded by new documentation
- Content is no longer relevant
- Content is moved to legacy documentation

**Archive Process:**
1. Move to "Documentation → Reference Materials → Legacy Documentation"
2. Add note explaining why archived
3. Link from new documentation
4. Update navigation

---

## Navigation Best Practices

### Internal Linking

**Guidelines:**
- Link to related pages within wiki
- Use descriptive link text
- Group related links at end of page
- Update links when pages move

**Examples:**
- "See [Status Rules](link) for status computation logic"
- "For implementation details, see [Field Mapping Implementation](link)"

---

### Cross-References

**Guidelines:**
- Reference related specifications
- Link to requirements from implementations
- Link to guides from specifications
- Create "See Also" sections

---

### Table of Contents

**When to Use:**
- Long pages (10+ sections)
- Complex documentation
- Reference materials

**Format:**
```markdown
## Table of Contents
1. [Section 1](#section-1)
2. [Section 2](#section-2)
3. [Section 3](#section-3)
```

---

## Examples

### Good Page Structure

```markdown
# Field Mapping Implementation Guide

## Overview
This guide explains how to implement field mappings in the Fleeti telemetry system.

## Prerequisites
- Understanding of [Telemetry System Specification](link)
- Access to [Field Mappings Catalog](link)
- Development environment set up

## Step-by-Step Guide

### Step 1: Identify Provider Fields
[Content]

### Step 2: Map to Fleeti Fields
[Content]

### Step 3: Configure Transformation
[Content]

## Code Examples
[Code snippets]

## Troubleshooting
[Common issues and solutions]

## Related Links
- [Telemetry System Specification](link)
- [Field Mappings Catalog](link)
- [Configuration Guide](link)

**Last Updated:** 2025-01-15 by John Doe
```

---

### Good Decision Record

```markdown
# [Decision-001] Storage Strategy

**Date:** 2025-01-15  
**Status:** Accepted  
**Deciders:** Architecture Team

## Context
We need to store telemetry data in a way that balances performance, cost, and data preservation.

## Decision
We will use a three-tier storage architecture:
1. Fast Access (Hot) - Core fields for real-time updates
2. Complete Data (Warm) - All fields for detail views
3. Raw Archive (Cold) - Original provider packets

## Rationale
- Performance: Hot storage enables < 100ms latency for map updates
- Cost: Cold storage reduces long-term storage costs
- Preservation: Raw archive enables historical recalculation

## Alternatives Considered
- Single-tier storage: Rejected due to cost and performance concerns
- Two-tier storage: Rejected due to lack of recalculation capability

## Consequences
- Positive: Fast map updates, cost-effective storage, recalculation capability
- Negative: Increased complexity, multiple storage systems to maintain

## References
- [Storage Strategy Analysis](link)
- [Storage Product Requirements](link)
```

---

## Quick Reference

### Where to Add Content

| Content Type | Location | Audience |
|-------------|----------|----------|
| Project status | Project Management → Current Status | Stakeholders |
| Technical specs | Documentation → Specifications | Developers |
| Implementation guide | Developer Resources → Implementation Guides | Developers |
| API docs | Developer Resources → API Documentation | Developers |
| Product requirements | Documentation → Requirements | Product Owners |
| Decision record | Project Management → Decision Records | All |
| Technical notes | Technical Pages → [Your Name] | Developers |
| Troubleshooting | Developer Resources → Troubleshooting | Developers |

---

## Getting Help

**Questions about:**
- **Wiki organization:** See [Wiki Organization Guide](link)
- **Documentation standards:** See [Documentation Standards](link)
- **Contribution process:** See [Contribution Guidelines](link)
- **Sync workflow:** See [Sync Workflow](link)

**Contact:**
- Documentation Team: [Contact Info]
- Wiki Maintainer: [Contact Info]

---

**Last Updated:** 2025-01-15  
**Version:** 1.0

