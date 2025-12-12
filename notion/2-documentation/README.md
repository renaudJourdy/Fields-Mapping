# 📚 Documentation

This section contains comprehensive technical documentation for the Fleeti Telemetry Mapping project, including specifications, field mappings, reference materials, and requirements. It serves as the complete reference for understanding and implementing the provider-agnostic telemetry transformation system.

## Purpose

The **Documentation** section provides:

- **Specifications**: Complete technical specifications for the telemetry system architecture, transformation rules, and schema definitions
- **Field Mappings**: Field catalogs, mapping rules, and transformation logic for converting provider data to Fleeti format
- **Reference Materials**: Provider field catalogs, enum definitions, and historical documentation for reference
- **Requirements**: Functional and product requirements that drive system design and implementation

**Target Audiences:**
- **Developers**: Technical specifications, field mappings, and implementation details
- **Field Mapping Specialists**: Field catalogs, mapping rules, and transformation logic
- **Architects**: System architecture, storage strategy, and design decisions
- **Product Team**: Requirements, feature specifications, and product needs

---

## Quick Navigation

### Common Workflows

**Adding a New Field:**
1. Review [Fleeti Fields Catalog](./field-mappings/fleeti-fields-catalog.md) to understand field structure
2. Check [Provider Fields Catalog](./field-mappings/provider-fields-catalog.md) for provider field details
3. Create mapping rule in [Mapping Rules](./field-mappings/mapping-rules.md)
4. Update [Schema Specification](./specifications/schema-specification.md) if needed

**Understanding Status Computation:**
1. Start with [Status Rules](./specifications/status-rules.md) for computation logic
2. Review [Telemetry System Specification](./specifications/telemetry-system-specification.md) for context
3. Check [Field Mappings](./field-mappings/README.md) for required fields

**Implementing Provider Integration:**
1. Review [Telemetry System Specification](./specifications/telemetry-system-specification.md) architecture section
2. Study [Provider Fields Catalog](./field-mappings/provider-fields-catalog.md) for provider structure
3. Reference [Provider Catalogs](./reference-materials/provider-catalogs.md) for detailed field information
4. Follow [Mapping Rules](./field-mappings/mapping-rules.md) for transformation logic

**Understanding Storage Strategy:**
1. Read [Telemetry System Specification](./specifications/telemetry-system-specification.md) storage section
2. Review [Storage Product Requirements](./requirements/storage-product-requirements.md) (⚠️ Under Review)
3. Check [Architecture Overview](../1-overview-vision/3-architecture-overview.md) for high-level design

---

## Main Sections Overview

### [Specifications](./specifications/README.md) ✅ Validated

Complete technical specifications covering system architecture, field types, transformation rules, status computation, and schema definitions.

**Key Contents:**
- Telemetry system architecture and design
- Field types and transformation rules
- Status computation logic and state machines
- Complete Fleeti telemetry schema structure
- Storage strategy and configuration system

**Audience:** Developers, architects, and technical stakeholders  
**Status:** ✅ Validated

---

### [Field Mappings](./field-mappings/README.md) ✅ Validated

Field catalogs and mapping documentation including Fleeti fields catalog, provider fields catalog, and transformation rules.

**Key Contents:**
- Complete Fleeti telemetry fields catalog (~343+ fields)
- Provider field catalogs (Navixy, Teltonika, future providers)
- Field mapping rules and priority chains
- Transformation logic for calculated and transformed fields
- I/O mapping and configuration-driven mappings

**Audience:** Developers and field mapping specialists  
**Status:** ✅ Validated

---

### [Reference Materials](./reference-materials/README.md) ✅ Validated

Reference documentation including provider catalogs, enum definitions, and legacy documentation.

**Key Contents:**
- Provider field catalogs (Navixy ~340 fields, Teltonika AVL IDs, Flespi)
- Fleeti API enumerations and definitions
- Legacy mapping documents (deprecated, for historical reference only)
- Enum compatibility matrices and reference data

**Audience:** Developers and reference users  
**Status:** ✅ Validated (legacy docs marked as deprecated)

---

### [Requirements](./requirements/README.md) Mixed Status

Functional and product requirements including field mapping requirements and storage product requirements.

**Key Contents:**
- Field mapping requirements and documentation needs
- New field detection watchdog system requirements
- Storage product requirements (three-tier strategy, performance, scalability)
- Historical recalculation capability requirements

**Audience:** Product team, developers, and stakeholders  
**Status:** Mixed (field mapping ✅ Validated, storage ⚠️ Under Review)

---

## Database Overview

The documentation section includes structured databases for managing field mappings and transformation rules. These databases serve as the source of truth for field definitions and mapping configurations.

### Available Databases

**Provider Fields Database**
- Comprehensive catalog of all provider-specific telemetry fields
- Organized by provider (Navixy, Teltonika, OEM, etc.)
- Includes field names, types, descriptions, and observed values
- Used for mapping provider fields to Fleeti canonical fields

**Fleeti Fields Database**
- Complete catalog of all Fleeti telemetry fields
- Organized by section (Asset Metadata, Location, Motion, Power, Fuel, etc.)
- Includes field priorities, types, and transformation requirements
- Serves as the canonical reference for Fleeti telemetry structure

**Mapping Rules Database**
- Field transformation rules and priority chains
- Direct mappings, calculated fields, and transformed fields
- I/O mappings and configuration-driven rules
- Links provider fields to Fleeti fields with transformation logic

**Access:** Databases are accessible through the respective section pages and can be queried, filtered, and updated as needed for field mapping work.

---

## Epic Structure Overview

The documentation is organized around six main functional epics that represent major areas of the telemetry mapping system:

### Epic 1: Ingestion & Provider Integration
**Focus:** Provider parser architecture, data forwarding, validation, and normalization  
**Documentation:** [Telemetry System Specification](./specifications/telemetry-system-specification.md) - Ingestion Layer  
**Related:** [Provider Fields Catalog](./field-mappings/provider-fields-catalog.md), [Provider Catalogs](./reference-materials/provider-catalogs.md)

### Epic 2: Field Mapping & Transformation
**Focus:** Field catalogs, mapping rules, transformation logic, and priority chains  
**Documentation:** [Field Mappings](./field-mappings/README.md), [Mapping Rules](./field-mappings/mapping-rules.md)  
**Related:** [Schema Specification](./specifications/schema-specification.md), [Field Mapping Requirements](./requirements/field-mapping-requirements.md)

### Epic 3: Status Computation
**Focus:** Status family computation, state machines, trigger conditions, and compatibility matrices  
**Documentation:** [Status Rules](./specifications/status-rules.md)  
**Related:** [Telemetry System Specification](./specifications/telemetry-system-specification.md) - Status Computation

### Epic 4: Storage & Data Management
**Focus:** Three-tier storage strategy (hot, warm, cold), data access patterns, and historical recalculation  
**Documentation:** [Storage Product Requirements](./requirements/storage-product-requirements.md) ⚠️, [Telemetry System Specification](./specifications/telemetry-system-specification.md) - Storage Strategy  
**Related:** [Architecture Overview](../1-overview-vision/3-architecture-overview.md)

### Epic 5: Configuration & Management
**Focus:** Configuration hierarchy, YAML configuration, field mapping configuration, and system management  
**Documentation:** [Telemetry System Specification](./specifications/telemetry-system-specification.md) - Configuration System  
**Related:** [Configuration Guide](../3-developer-resources/configuration-guide/README.md)

### Epic 6: API & Consumption
**Focus:** Telemetry API, WebSocket API, data consumption patterns, and frontend integration  
**Documentation:** [Telemetry System Specification](./specifications/telemetry-system-specification.md) - API Layer  
**Related:** [API Documentation](../3-developer-resources/api-documentation/README.md)

**Epic Relationships:** Epics are interconnected—ingestion feeds transformation, which feeds status computation, which feeds storage, all managed through configuration and consumed via APIs. Each epic builds upon the previous ones in the pipeline.

---

## Additional Resources

### Related Sections

- **[Overview & Vision](../1-overview-vision/README.md)**: Project overview, objectives, architecture, and key concepts
- **[Developer Resources](../3-developer-resources/README.md)**: Implementation guides, API documentation, and troubleshooting
- **[Project Management](../4-project-management/README.md)**: Project status, roadmap, and decision records

### Key Reference Documents

- **[Telemetry System Specification](./specifications/telemetry-system-specification.md)**: Complete system specification (start here for architecture)
- **[Schema Specification](./specifications/schema-specification.md)**: Complete field definitions and structure
- **[Status Rules](./specifications/status-rules.md)**: Status computation logic and rules

### Insights & Examples

- **Field Mapping Examples**: See [Mapping Rules](./field-mappings/mapping-rules.md) for transformation examples
- **Provider Integration Patterns**: Review [Provider Fields Catalog](./field-mappings/provider-fields-catalog.md) for provider structures
- **Status Computation Logic**: Study [Status Rules](./specifications/status-rules.md) for computation patterns

---

## Validation Status

All content in this section is based on validated project documentation:

- ✅ **Validated**: Technical specifications from `Wiki/telemetry-system-specification.md`
- ✅ **Validated**: Status rules from `Wiki/telemetry-status-rules.md`
- ✅ **Validated**: Schema specification from `working/fleeti-telemetry-schema-specification.md`
- ✅ **Validated**: Field mapping requirements and documentation needs
- ⚠️ **Under Review**: Storage product requirements (marked clearly in requirements section)

**Note:** Content marked as "Validated" has been reviewed and confirmed against source documentation. Content marked as "Under Review" should be treated as informative and may change based on review.

---

## Getting Started

**New to the project?**
1. Start with [Overview & Vision](../1-overview-vision/README.md) for project context
2. Read [Telemetry System Specification](./specifications/telemetry-system-specification.md) for architecture
3. Review [Field Mappings](./field-mappings/README.md) for field structure
4. Check [Status Rules](./specifications/status-rules.md) for computation logic

**Implementing a feature?**
1. Review relevant epic documentation above
2. Check specifications for technical details
3. Consult field mappings for data structures
4. Reference requirements for product needs

**Mapping provider fields?**
1. Review [Fleeti Fields Catalog](./field-mappings/fleeti-fields-catalog.md)
2. Check [Provider Fields Catalog](./field-mappings/provider-fields-catalog.md)
3. Follow [Mapping Rules](./field-mappings/mapping-rules.md)
4. Update [Schema Specification](./specifications/schema-specification.md) if needed

---

**Last Updated:** 2025-01-XX  
**Section Status:** Active documentation, most content validated ✅
