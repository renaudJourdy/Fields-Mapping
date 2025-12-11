# Specifications

**Status:** ✅ Validated

This section contains complete technical specifications for the Fleeti Telemetry Mapping system.

# Overview

The specifications section provides comprehensive technical documentation covering:

- **Telemetry System Specification**: Complete system architecture, field types, transformation rules, storage strategy, and configuration system
- **Status Rules**: Status computation logic, compatibility matrices, and status family trigger conditions
- **Schema Specification**: Complete Fleeti telemetry schema structure, field definitions, and provider field mappings

# Specification Documents

## [Telemetry System Specification](./telemetry-system-specification.md)

Complete specification for creating a provider-agnostic Fleeti Telemetry system from multi-provider raw telemetry data.

> *Comprehensive specification covering context and background, objectives and vision, telemetry sources, field types and transformation rules, storage strategy, configuration system, and implementation considerations.*

**Audience:** Developers, architects, and technical stakeholders  
**Status:** ✅ Validated  
**Source:** `Wiki/telemetry-system-specification.md`

---

## [Status Rules](./status-rules.md)

Complete status computation rules for Connectivity, Transit, Engine, and Immobilization status families.

> *Status computation rules including compatibility matrices, trigger conditions, state machines, and required telemetry fields for each status family.*

**Audience:** Developers implementing status computation  
**Status:** ✅ Validated  
**Source:** `Wiki/telemetry-status-rules.md`

---

## [Schema Specification](./schema-specification.md)

Complete Fleeti telemetry schema specification with all field definitions, types, priorities, and provider mappings.

> *Comprehensive telemetry schema covering all Fleeti telemetry fields organized by section (Asset Metadata, Location, Motion, Power, Fuel, Diagnostics, etc.), field priorities, and provider field mappings.*

**Audience:** Developers, API designers, and frontend teams  
**Status:** ✅ Validated  
**Source:** `working/fleeti-telemetry-schema-specification.md`

# Related Documentation

- **[Field Mappings](../field-mappings/README.md)**: Field catalogs and mapping rules
- **[Requirements](../requirements/README.md)**: Functional and product requirements
- **[Overview & Vision](../../overview-vision/README.md)**: Project overview and architecture
