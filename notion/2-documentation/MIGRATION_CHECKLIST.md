# Documentation Restructure Migration Checklist

**Status:** 📋 Planning  
**Purpose:** Step-by-step checklist for migrating from reference-oriented to developer-oriented documentation structure

---

## Pre-Migration Preparation

### Review & Approval
- [ ] Review `DEVELOPER_DOCUMENTATION_RESTRUCTURE_PROPOSAL.md`
- [ ] Get team feedback and approval
- [ ] Identify priority pages (which to migrate first)
- [ ] Set timeline and milestones

### Content Audit
- [ ] Audit all existing documentation files
- [ ] Identify "how to" content vs. reference content
- [ ] Identify content gaps (missing "how to" guidance)
- [ ] List all cross-references that need updating

---

## Phase 1: Create New Structure

### Main Documentation Pages
- [ ] Create `documentation/README.md` (new overview)
- [ ] Create `documentation/fleeti-fields.md`
- [ ] Create `documentation/provider-fields.md`
- [ ] Create `documentation/configuration-files.md`
- [ ] Create `documentation/mapping-rules.md` (transform existing)
- [ ] Create `documentation/status-computation.md`
- [ ] Create `documentation/storage-strategy.md`

### Reference Materials Subfolder
- [ ] Create `documentation/reference/` directory
- [ ] Create `documentation/reference/README.md`
- [ ] Create `documentation/reference/specifications.md`
- [ ] Create `documentation/reference/provider-catalogs.md`
- [ ] Create `documentation/reference/enum-definitions.md`
- [ ] Create `documentation/reference/legacy-documentation.md`

---

## Phase 2: Content Migration

### fleeti-fields.md
- [ ] Extract field structure guidance from `specifications/schema-specification.md`
- [ ] Extract "how to add fields" from `field-mappings/fleeti-fields-catalog.md`
- [ ] Extract priority guidance from `specifications/schema-specification.md`
- [ ] Add step-by-step "adding new field" workflow
- [ ] Add field validation rules
- [ ] Add practical examples
- [ ] Link to `reference/specifications.md` for complete schema

### provider-fields.md
- [ ] Extract provider overview from `field-mappings/provider-fields-catalog.md`
- [ ] Extract "how to add provider" guidance
- [ ] Extract provider-specific considerations from `reference-materials/provider-catalogs.md`
- [ ] Add step-by-step "adding new provider" workflow
- [ ] Add field availability matrix
- [ ] Add practical examples
- [ ] Link to `reference/provider-catalogs.md` for complete catalogs

### configuration-files.md
- [ ] Extract configuration structure from `specifications/telemetry-system-specification.md`
- [ ] Extract YAML examples from `field-mappings/mapping-rules.md`
- [ ] Add step-by-step "creating configuration" workflow
- [ ] Add configuration hierarchy explanation
- [ ] Add testing and validation guidance
- [ ] Add version control best practices
- [ ] Add practical examples
- [ ] Link to `reference/specifications.md` for complete spec

### mapping-rules.md (Transform Existing)
- [ ] Transform `field-mappings/mapping-rules.md` to "how to" format
- [ ] Add step-by-step workflows for each mapping type
- [ ] Add practical examples and patterns
- [ ] Add best practices and anti-patterns
- [ ] Add troubleshooting guidance
- [ ] Link to `reference/specifications.md` for complete rules

### status-computation.md
- [ ] Extract status families overview from `specifications/status-rules.md`
- [ ] Extract implementation guidance
- [ ] Add step-by-step "implementing status" workflow
- [ ] Add compatibility matrix explanation
- [ ] Add trigger conditions guide
- [ ] Add state machine explanation
- [ ] Add practical examples
- [ ] Link to `reference/specifications.md` for complete rules

### storage-strategy.md
- [ ] Extract storage tiers from `specifications/telemetry-system-specification.md`
- [ ] Extract data flow explanation
- [ ] Extract core vs extended guidance
- [ ] Add step-by-step "understanding storage" guide
- [ ] Add query patterns
- [ ] Add performance considerations
- [ ] Add practical examples
- [ ] Link to `reference/specifications.md` for complete spec
- [ ] Link to `requirements/storage-product-requirements.md` (when validated)

### Reference Materials
- [ ] Create `reference/specifications.md` with links to all specs
- [ ] Move `field-mappings/provider-fields-catalog.md` → `reference/provider-catalogs.md`
- [ ] Move `reference-materials/enum-definitions.md` → `reference/enum-definitions.md`
- [ ] Move `reference-materials/legacy-documentation.md` → `reference/legacy-documentation.md`
- [ ] Consolidate specification summaries in `reference/specifications.md`

---

## Phase 3: Update Links

### Internal Documentation Links
- [ ] Update `documentation/README.md` links
- [ ] Update all main page cross-references
- [ ] Update reference material links
- [ ] Update specification links

### External Links
- [ ] Update `overview-vision/` section links
- [ ] Update project management links
- [ ] Update any developer resources links
- [ ] Update root page navigation

### Link Verification
- [ ] Verify all internal links work
- [ ] Verify all external links work
- [ ] Check for broken references
- [ ] Update any Notion page links if applicable

---

## Phase 4: Deprecation & Cleanup

### Deprecation Notices
- [ ] Add deprecation notice to `specifications/README.md`
- [ ] Add deprecation notice to `field-mappings/README.md`
- [ ] Add deprecation notice to `reference-materials/README.md`
- [ ] Add migration guide pointing to new structure

### Archive Old Structure (After Migration Verified)
- [ ] Verify all content migrated
- [ ] Verify all links updated
- [ ] Get final approval to remove old structure
- [ ] Archive or remove old folders
- [ ] Update any scripts or automation

---

## Phase 5: Validation & Testing

### Content Review
- [ ] Review all new pages for clarity
- [ ] Verify all examples work
- [ ] Check for consistency across pages
- [ ] Verify tone and style consistency

### Developer Testing
- [ ] Have developers test finding information
- [ ] Gather feedback on new structure
- [ ] Identify any missing content
- [ ] Identify any confusing sections

### Documentation Quality
- [ ] Verify all pages follow same pattern
- [ ] Check for broken links
- [ ] Verify reference materials accessible
- [ ] Ensure navigation is clear

---

## Post-Migration

### Continuous Improvement
- [ ] Monitor usage patterns
- [ ] Gather ongoing feedback
- [ ] Update based on developer needs
- [ ] Add new guides as needed

### Maintenance
- [ ] Keep reference materials updated
- [ ] Keep main pages current
- [ ] Update examples as system evolves
- [ ] Maintain link integrity

---

## Notes

- **Priority Order:** Consider migrating highest-impact pages first (mapping-rules, configuration-files)
- **Parallel Work:** Some pages can be created in parallel
- **Incremental:** Can migrate incrementally, don't need to do all at once
- **Feedback Loop:** Get developer feedback early and often

---

**Status:** Ready to begin when approved

