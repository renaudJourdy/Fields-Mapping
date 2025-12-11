# 📚 Documentation

This section contains comprehensive technical documentation for the Fleeti Telemetry Mapping project, including specifications, field mappings, reference materials, and requirements.

## Purpose

The **Documentation** section provides:

- **Specifications**: Complete technical specifications for the telemetry system
- **Field Mappings**: Field catalogs and mapping rules
- **Reference Materials**: Provider catalogs, enum definitions, and legacy documentation
- **Requirements**: Functional and product requirements

## Section Contents

### [Specifications](./specifications/README.md)

Complete technical specifications including telemetry system specification, status computation rules, and schema definitions.

> *Technical specifications covering system architecture, field types, transformation rules, status computation, and complete telemetry schema structure.*

**Audience:** Developers and technical stakeholders  
**Status:** ✅ Validated

---

### [Field Mappings](./field-mappings/README.md)

Field catalogs and mapping documentation including Fleeti fields catalog, provider fields catalog, and mapping rules.

> *Field mapping documentation covering Fleeti telemetry fields, provider field catalogs, and transformation rules for converting provider data to Fleeti format.*

**Audience:** Developers and field mapping specialists  
**Status:** ✅ Validated

---

### [Reference Materials](./reference-materials/README.md)

Reference documentation including provider catalogs, enum definitions, and legacy documentation.

> *Reference materials including provider field catalogs (Navixy, Teltonika, Flespi), Fleeti API enumerations, and historical mapping documents.*

**Audience:** Developers and reference users  
**Status:** ✅ Validated (legacy docs marked as deprecated)

---

### [Requirements](./requirements/README.md)

Functional and product requirements including field mapping requirements and storage product requirements.

> *Requirements documentation covering field mapping requirements, field documentation needs, and storage product requirements (⚠️ Under Review).*

**Audience:** Product team, developers, and stakeholders  
**Status:** Mixed (field mapping ✅ Validated, storage ⚠️ Under Review)

## Validation Status

All content in this section is based on validated project documentation:

- ✅ **Validated**: Technical specifications from `Wiki/telemetry-system-specification.md`
- ✅ **Validated**: Status rules from `Wiki/telemetry-status-rules.md`
- ✅ **Validated**: Schema specification from `working/fleeti-telemetry-schema-specification.md`
- ⚠️ **Under Review**: Storage product requirements (marked clearly in requirements section)

## Navigation

- **Getting Started**: Begin with [Specifications](./specifications/README.md) for technical details
- **Field Mapping**: Review [Field Mappings](./field-mappings/README.md) for field catalogs and rules
- **Reference**: Consult [Reference Materials](./reference-materials/README.md) for provider catalogs and enums
- **Requirements**: See [Requirements](./requirements/README.md) for functional and product requirements
