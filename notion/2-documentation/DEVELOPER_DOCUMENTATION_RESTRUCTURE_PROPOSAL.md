# Developer-Focused Documentation Restructure Proposal

**Status:** 🎯 Proposal  
**Date:** 2025-01-XX  
**Purpose:** Transform reference-oriented documentation into action-oriented developer guides

---

## Executive Summary

The current documentation structure is **reference-oriented** (organized by document type: specs, requirements, mappings, reference). This proposal restructures it to be **developer-oriented** (organized by developer workflows: how to work with fields, how to create mappings, how to implement status, etc.).

**Key Principle:** Follow the same clear, focused pattern as the `overview-vision/` section - direct markdown files with actionable content.

---

## Current Structure Analysis

### Current Organization (Reference-Oriented)

```
documentation/
├── specifications/          # Reference specs (telemetry-system-spec, status-rules, schema)
├── field-mappings/         # Field catalogs (Fleeti fields, provider fields, mapping rules)
├── reference-materials/    # Reference docs (provider catalogs, enums, legacy)
└── requirements/          # Requirements docs (field mapping, storage)
```

### Problems with Current Structure

1. **Reference-First:** Organized by document type, not by developer need
2. **Hard to Discover:** Developers must know what document type contains what they need
3. **No Workflow Guidance:** Missing step-by-step "how to" instructions
4. **Specification-Heavy:** Specs are primary, guidance is secondary
5. **Nested Folders:** Unnecessary nesting for end-user content

### What Developers Actually Need

1. **Field Management:** How to add fields, map fields, define priorities
2. **Configuration:** How to create/update YAML configs, test configurations
3. **Mapping Rules:** How to implement direct, prioritized, calculated, transformed mappings
4. **Status Computation:** How to implement status families, compatibility rules
5. **Storage Strategy:** How data flows, what goes where, how to query
6. **Implementation Guides:** Step-by-step workflows, examples, troubleshooting

---

## Proposed Structure (Developer-Oriented)

### New Organization

```
documentation/
├── README.md                          # Section overview and navigation guide
│
├── fleeti-fields.md                  # How to work with Fleeti fields
├── provider-fields.md                 # How to work with provider fields
├── configuration-files.md             # How to create and manage YAML configs
├── mapping-rules.md                  # How to implement mapping rules
├── status-computation.md              # How to implement status computation
├── storage-strategy.md                # How to understand and work with storage
│
└── reference/                         # Reference materials (secondary access)
    ├── README.md                      # Reference materials overview
    ├── specifications.md              # Link to complete specifications
    ├── provider-catalogs.md           # Complete provider field catalogs
    ├── enum-definitions.md            # Enum definitions
    └── legacy-documentation.md        # Legacy docs (deprecated)
```

### Key Changes

1. **Action-Oriented Pages:** Main pages focus on "how to" rather than "what is"
2. **Direct Markdown Files:** Following `overview-vision/` pattern (no nested folders for end pages)
3. **Reference Materials Subfolder:** Still accessible but not primary organization
4. **Developer Workflows:** Organized by what developers need to do

---

## Detailed Page Structure

### 1. `README.md` - Documentation Overview

**Purpose:** Navigation hub and entry point for all documentation

**Content:**
- Section overview and purpose
- Quick navigation guide
- Developer workflow paths
- Links to all main pages
- Links to reference materials

**Audience:** All developers

---

### 2. `fleeti-fields.md` - How to Work with Fleeti Fields

**Purpose:** Practical guide for working with Fleeti telemetry fields

**Content:**
- **Field Structure:** How fields are organized (sections, nesting)
- **Adding New Fields:** Step-by-step process for adding a new Fleeti field
- **Field Priorities:** Understanding P0-P3, T, BL priorities and when to use them
- **Field Categories:** Core vs extended, customer-facing vs internal
- **Field Validation:** Validation rules and constraints
- **Examples:** Real examples of field definitions
- **Reference:** Link to complete schema specification

**Migration Source:**
- `field-mappings/fleeti-fields-catalog.md` → Extract "how to" content
- `specifications/schema-specification.md` → Extract field structure guidance
- `requirements/field-mapping-requirements.md` → Extract field documentation requirements

**Audience:** Developers adding or modifying Fleeti fields

---

### 3. `provider-fields.md` - How to Work with Provider Fields

**Purpose:** Practical guide for working with provider telemetry fields

**Content:**
- **Provider Overview:** Supported providers (Navixy, Teltonika, Flespi, etc.)
- **Adding Provider Support:** Step-by-step process for adding a new provider
- **Provider Field Types:** Understanding provider field formats and types
- **Field Availability:** Which fields are available from which providers
- **Provider-Specific Considerations:** Special handling for different providers
- **Examples:** Real examples of provider field mappings
- **Reference:** Link to complete provider catalogs

**Migration Source:**
- `field-mappings/provider-fields-catalog.md` → Extract "how to" content
- `reference-materials/provider-catalogs.md` → Extract provider-specific guidance

**Audience:** Developers working with provider integrations

---

### 4. `configuration-files.md` - How to Create and Manage YAML Configs

**Purpose:** Practical guide for creating and managing configuration files

**Content:**
- **Configuration Structure:** YAML file structure and organization
- **Creating Configurations:** Step-by-step process for creating a new config
- **Configuration Hierarchy:** Default → Customer → Asset hierarchy
- **Defining Mappings:** How to define different mapping types in YAML
- **Testing Configurations:** How to test and validate configurations
- **Version Control:** Best practices for managing config versions
- **Examples:** Real YAML configuration examples
- **Reference:** Link to complete configuration specification

**Migration Source:**
- `specifications/telemetry-system-specification.md` → Extract configuration system content
- `field-mappings/mapping-rules.md` → Extract configuration examples

**Audience:** Developers creating or updating configurations

---

### 5. `mapping-rules.md` - How to Implement Mapping Rules

**Purpose:** Practical guide for implementing field mapping rules

**Content:**
- **Mapping Types Overview:** Direct, prioritized, calculated, transformed, I/O
- **Direct Mappings:** How to implement 1:1 field mappings
- **Prioritized Mappings:** How to implement priority-based field selection
- **Calculated Fields:** How to implement computed fields
- **Transformed Fields:** How to implement field transformations
- **I/O Mappings:** How to handle input/output state mappings
- **Examples and Patterns:** Real-world mapping examples
- **Best Practices:** Common patterns and anti-patterns
- **Reference:** Link to complete mapping rules specification

**Migration Source:**
- `field-mappings/mapping-rules.md` → Transform to "how to" format
- `specifications/telemetry-system-specification.md` → Extract transformation logic

**Audience:** Developers implementing field transformations

---

### 6. `status-computation.md` - How to Implement Status Computation

**Purpose:** Practical guide for implementing status computation

**Content:**
- **Status Families Overview:** Connectivity, Transit, Engine, Immobilization
- **Status Compatibility:** Understanding compatibility matrices
- **Trigger Conditions:** How status changes are triggered
- **Implementation Guide:** Step-by-step implementation process
- **State Machines:** How status state machines work
- **Required Fields:** Which telemetry fields are needed for each status
- **Examples:** Real status computation examples
- **Reference:** Link to complete status rules specification

**Migration Source:**
- `specifications/status-rules.md` → Transform to "how to" format
- `specifications/telemetry-system-specification.md` → Extract status computation logic

**Audience:** Developers implementing status computation

---

### 7. `storage-strategy.md` - How to Understand and Work with Storage

**Purpose:** Practical guide for understanding storage strategy

**Content:**
- **Storage Tiers Overview:** Hot, warm, cold storage tiers
- **What Goes Where:** Core vs extended data placement
- **Data Flow:** How data flows through storage tiers
- **Query Patterns:** How to query different storage tiers
- **Performance Considerations:** Performance implications and optimizations
- **Historical Recalculation:** How historical data recalculation works
- **Examples:** Real storage usage examples
- **Reference:** Link to complete storage specification

**Migration Source:**
- `specifications/telemetry-system-specification.md` → Extract storage strategy content
- `requirements/storage-product-requirements.md` → Extract storage requirements (when validated)

**Audience:** Developers working with storage or data access

---

### 8. `reference/` - Reference Materials (Secondary Access)

**Purpose:** Complete reference materials for when you need full specifications

**Structure:**
```
reference/
├── README.md                      # Reference materials overview
├── specifications.md              # Complete technical specifications
├── provider-catalogs.md           # Complete provider field catalogs
├── enum-definitions.md            # Enum definitions
└── legacy-documentation.md        # Legacy docs (deprecated)
```

**Content Strategy:**
- **specifications.md:** Links to and summaries of all specification documents
- **provider-catalogs.md:** Complete provider field catalogs (moved from `field-mappings/`)
- **enum-definitions.md:** Enum definitions (moved from `reference-materials/`)
- **legacy-documentation.md:** Legacy docs marked as deprecated

**Migration Source:**
- `specifications/` → Consolidate into `specifications.md` with links
- `field-mappings/provider-fields-catalog.md` → Move to `provider-catalogs.md`
- `reference-materials/enum-definitions.md` → Move to `enum-definitions.md`
- `reference-materials/legacy-documentation.md` → Move to `legacy-documentation.md`

**Audience:** Developers needing complete reference documentation

---

## Content Strategy

### Balancing Guidance vs. Reference

**Main Pages (Action-Oriented):**
- **Focus:** "How to" instructions, step-by-step workflows, practical examples
- **Style:** Clear, actionable, with real examples
- **Length:** Focused and scannable (not exhaustive)
- **Links:** Link to reference materials when full specs are needed

**Reference Materials (Complete Specs):**
- **Focus:** Complete specifications, exhaustive catalogs, detailed definitions
- **Style:** Comprehensive reference format
- **Length:** Can be long and detailed
- **Usage:** Consulted when you need complete information

### Content Transformation Approach

**From Reference to Guidance:**

1. **Extract "How To" Content:**
   - Identify actionable steps
   - Extract practical examples
   - Focus on workflows

2. **Reorganize by Workflow:**
   - Group by what developers need to do
   - Not by document type
   - Logical flow from basic to advanced

3. **Add Implementation Guidance:**
   - Step-by-step instructions
   - Common patterns
   - Troubleshooting tips
   - Best practices

4. **Link to Reference:**
   - Link to complete specs when needed
   - Don't duplicate exhaustive content
   - Keep main pages focused

---

## Migration Plan

### Phase 1: Create New Structure

1. **Create new main pages:**
   - `README.md` (new overview)
   - `fleeti-fields.md` (new)
   - `provider-fields.md` (new)
   - `configuration-files.md` (new)
   - `mapping-rules.md` (transform existing)
   - `status-computation.md` (new)
   - `storage-strategy.md` (new)

2. **Create reference subfolder:**
   - `reference/README.md`
   - `reference/specifications.md`
   - `reference/provider-catalogs.md`
   - `reference/enum-definitions.md`
   - `reference/legacy-documentation.md`

### Phase 2: Migrate Content

1. **Transform existing content:**
   - Extract "how to" content from existing docs
   - Reorganize by workflow
   - Add implementation guidance
   - Create reference links

2. **Move reference materials:**
   - Move complete catalogs to `reference/`
   - Consolidate specifications
   - Preserve legacy docs

### Phase 3: Update Links

1. **Update internal links:**
   - Update all cross-references
   - Update navigation
   - Update README files

2. **Update external links:**
   - Update links from other sections
   - Update overview-vision links
   - Update project management links

### Phase 4: Deprecate Old Structure

1. **Mark old folders as deprecated:**
   - Add deprecation notices
   - Add migration guides
   - Keep for reference during transition

2. **Remove after migration complete:**
   - Remove old folders once migration verified
   - Archive if needed

---

## Benefits of New Structure

### For Developers

1. **Easier Discovery:** Find what you need by workflow, not document type
2. **Action-Oriented:** Clear "how to" instructions, not just "what is"
3. **Practical Examples:** Real examples and patterns
4. **Focused Content:** Scannable, focused pages
5. **Reference Access:** Still have access to complete specs when needed

### For Documentation Maintenance

1. **Clear Organization:** Logical structure based on developer needs
2. **Easy Updates:** Update guidance without touching reference materials
3. **Consistent Pattern:** Follows `overview-vision/` pattern
4. **Scalable:** Easy to add new guides as needed

### For Project

1. **Better Onboarding:** New developers can follow clear workflows
2. **Reduced Support:** Clear documentation reduces questions
3. **Faster Implementation:** Actionable guidance speeds up development
4. **Better Quality:** Clear patterns lead to consistent implementations

---

## Implementation Recommendations

### Immediate Actions

1. **Review and Refine:** Review this proposal with team
2. **Prioritize Pages:** Decide which pages to create first
3. **Create Templates:** Create page templates for consistency
4. **Start Migration:** Begin with highest-priority pages

### Success Criteria

1. **Developer Feedback:** Developers can find what they need quickly
2. **Usage Patterns:** Main pages are accessed more than reference
3. **Content Quality:** Actionable guidance, not just reference
4. **Maintainability:** Easy to update and maintain

---

## Questions for Review

1. **Page Structure:** Are these the right main pages? Any missing?
2. **Content Balance:** Right balance between guidance and reference?
3. **Migration Approach:** Is the migration plan feasible?
4. **Timeline:** What's the priority and timeline for migration?
5. **Feedback:** What feedback do developers have on current structure?

---

## Next Steps

1. **Review Proposal:** Team review and feedback
2. **Refine Structure:** Adjust based on feedback
3. **Create Templates:** Page templates for consistency
4. **Start Implementation:** Begin with highest-priority pages
5. **Iterate:** Continuous improvement based on usage

---

**Status:** Ready for review and feedback

