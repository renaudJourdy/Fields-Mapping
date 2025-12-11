# Provider Catalogs

**Status:** ✅ Validated  
**Source:** `Wiki/telemetry-system-specification.md` Section 3, `docs/reference/` files

Detailed provider field catalogs and reference materials.

---

## Overview

This document provides references to detailed provider field catalogs available in the project repository. These catalogs contain comprehensive field definitions and mappings for different telemetry providers.

---

## Navixy Field Catalog

### Catalog File

**Location**: `docs/reference/navixy-field-catalog.csv`

**Content**: Complete catalog of ~340 distinct telemetry fields identified from Navixy Data Forwarding POC

**Fields Include**:
- Location fields (GPS coordinates, heading, altitude)
- CAN bus fields (speed, RPM, fuel, diagnostics)
- OBD fields (diagnostic data)
- AVL IO parameters (Teltonika AVL protocol parameters)
- BLE sensor fields (Bluetooth Low Energy sensors)
- Device fields (gateway status and configuration)
- I/O fields (digital and analog inputs/outputs)
- Event fields (device-side events)

**Usage**: Reference for understanding all available Navixy telemetry fields and mapping them to Fleeti format

---

## Teltonika AVL ID References

### Catalog Files

**Location**: `docs/reference/teltonika-fmb140-avl-parameters.csv`

**Content**: Teltonika AVL protocol parameter definitions

**Usage**: Reference for understanding Teltonika AVL IO parameter IDs (e.g., `avl_io_85`, `avl_io_239`) used in Navixy telemetry

**Note**: Many Navixy fields use Teltonika AVL parameter IDs, so this catalog helps understand the semantic meaning of AVL IO parameters.

---

## Flespi Catalog

### Catalog File

**Location**: `docs/reference/flespi-teltonika-avl-id-catalog.csv`

**Content**: Flespi catalog mapping Teltonika AVL IDs

**Usage**: Reference for Flespi platform AVL ID mappings

**Note**: Flespi is another telemetry platform that uses Teltonika AVL protocol, so this catalog may be useful for future Flespi integration.

---

## Provider Field Mapping

### Mapping Approach

All provider fields are mapped to Fleeti telemetry format using:

1. **Direct Mapping**: 1:1 field mapping (e.g., `lat` → `location.latitude`)
2. **Prioritized Mapping**: Best source selected from multiple provider fields
3. **Calculated Mapping**: Derived from multiple provider fields
4. **Transformed Mapping**: Combined with static asset metadata

See [Mapping Rules](../field-mappings/mapping-rules.md) for detailed mapping logic.

### Complete Provider Mappings

For complete provider field mappings to Fleeti telemetry fields, see:
- **[Schema Specification](../specifications/schema-specification.md)**: Complete provider field mappings
- **[Provider Fields Catalog](../field-mappings/provider-fields-catalog.md)**: Provider field overview

---

## Future Provider Support

### OEM Direct Integration

**Planned Providers**:
- TrackUnit
- CareTrack
- Mecalac
- Manitou
- Liebher
- Other OEM manufacturers

**Format**: Provider-specific telemetry format (AEMP 2.0 standard)

**Status**: Planned for future implementation

### Other Providers

System architecture supports any provider format through:
- Provider-agnostic parser architecture
- Configuration-driven field mapping
- Unknown fields preserved in raw archive

---

## Related Documentation

- **[Provider Fields Catalog](../field-mappings/provider-fields-catalog.md)**: Provider field overview
- **[Mapping Rules](../field-mappings/mapping-rules.md)**: Field transformation rules
- **[Schema Specification](../specifications/schema-specification.md)**: Complete provider field mappings
- **[Telemetry System Specification](../specifications/telemetry-system-specification.md)**: System specification

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-XX  
**Status**: ✅ Validated  
**Source**: `Wiki/telemetry-system-specification.md` Section 3, `docs/reference/` files






