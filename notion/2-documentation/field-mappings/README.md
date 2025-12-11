# Field Mappings

**Status:** ✅ Validated

This section contains field mapping documentation including Fleeti fields catalog, provider fields catalog, and mapping rules.

## Overview

The field mappings section provides:

- **Fleeti Fields Catalog**: Complete catalog of all Fleeti telemetry fields
- **Provider Fields Catalog**: Overview of provider fields (Navixy and future providers)
- **Mapping Rules**: Field transformation rules and priority chains

## Field Mapping Documents

### [Fleeti Fields Catalog](./fleeti-fields-catalog.md)

Complete catalog of all Fleeti telemetry fields organized by section.

> *Comprehensive catalog of Fleeti telemetry fields including field organization, priority levels, and reference to complete schema specification.*

**Audience:** Developers, API designers, and frontend teams  
**Status:** ✅ Validated  
**Source:** `working/fleeti-telemetry-schema-specification.md`

---

### [Provider Fields Catalog](./provider-fields-catalog.md)

Overview of provider telemetry fields from Navixy and future providers.

> *Provider fields catalog covering Navixy field catalog (~340 fields), future provider support, and field mapping approach.*

**Audience:** Developers and field mapping specialists  
**Status:** ✅ Validated  
**Source:** `Wiki/telemetry-system-specification.md` Section 3

---

### [Mapping Rules](./mapping-rules.md)

Field mapping types, priority rules, and transformation logic.

> *Field mapping rules covering direct mapping, prioritized fields, calculated fields, transformed fields, I/O mapping, and configuration system overview.*

**Audience:** Developers implementing field transformations  
**Status:** ✅ Validated  
**Source:** `Wiki/telemetry-system-specification.md` Sections 5, 7

## Related Documentation

- **[Specifications](../specifications/README.md)**: Complete technical specifications
- **[Schema Specification](../specifications/schema-specification.md)**: Complete field definitions
- **[Requirements](../requirements/README.md)**: Field mapping requirements
