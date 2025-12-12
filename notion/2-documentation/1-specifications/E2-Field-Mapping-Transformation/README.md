**Status:** 🎯 Draft  
**Epic Number:** E2  
**Related Epics:** E1 (depends on provider-agnostic telemetry), E3 (Status Computation depends on transformed fields), E5 (Configuration provides mapping rules)

---

## 1. Overview

The Field Mapping & Transformation epic transforms provider-agnostic telemetry into Fleeti telemetry format by applying field mappings, priority rules, calculations, and transformations defined in configuration files.

### 1.1 Purpose

This epic converts provider telemetry into unified Fleeti telemetry format (~343+ fields) using configuration-driven mapping rules. It enables provider-agnostic telemetry by applying consistent transformation logic regardless of source provider.

### 1.2 Scope

**In Scope:**
- Loading hierarchical configuration (default, customer, asset group, asset)
- Applying direct field mappings (1:1 provider → Fleeti)
- Applying priority rules (select best source from multiple provider fields)
- Computing calculated fields (derived from telemetry)
- Transforming fields (combining telemetry with static asset metadata)
- I/O to semantic field mapping (raw I/O → semantic fields)

**Out of Scope:**
- Status computation (Epic 3)
- Configuration file generation (Epic 5)
- Storage operations (Epic 4)

### 1.3 Key Concepts

- **Configuration-Driven**: No hardcoded transformation rules, all mappings in YAML configuration
- **Hierarchical Configuration**: Default → Customer → Asset Group → Asset (lower levels override)
- **Field Types**: Direct, prioritized, calculated, transformed, I/O mapped
- **Priority Chains**: Select best source when multiple provider fields available
- **Asset Service Integration**: Retrieve installation metadata and asset specifications for transformations

---

## 2. Epic Goals & Success Criteria

### 2.1 Goals

- Transform provider telemetry to Fleeti format using configuration
- Support all field mapping types (direct, prioritized, calculated, transformed, I/O)
- Apply hierarchical configuration overrides
- Integrate with Asset Service for static data
- Enable new field mappings without code changes

### 2.2 Success Criteria

- All provider fields can be mapped to Fleeti fields via configuration
- Priority rules correctly select best source from multiple provider fields
- Calculated fields are computed correctly
- Transformed fields combine telemetry with static data correctly
- I/O fields are mapped to semantic fields based on installation metadata
- Configuration changes take effect without code deployment

---

## 3. Features

This epic is composed of the following features, each delivering standalone value:

### Feature List

| Feature ID | Feature Name | Description | Status |
|------------|--------------|-------------|--------|
| F2.1 | Load Hierarchical Configuration | Load and merge configuration from default, customer, asset group, asset levels | 🎯 Draft |
| F2.2 | Apply Direct Field Mappings | Map provider fields to Fleeti fields (1:1 with optional unit conversion) | 🎯 Draft |
| F2.3 | Apply Priority Rules | Select best source from multiple provider fields based on priority chain | 🎯 Draft |
| F2.4 | Compute Calculated Fields | Derive calculated fields from telemetry (e.g., cardinal direction from heading) | 🎯 Draft |
| F2.5 | Transform Fields with Static Data | Combine telemetry with asset metadata (e.g., fuel % → liters using tank capacity) | 🎯 Draft |
| F2.6 | Map I/O to Semantic Fields | Map raw I/O signals to semantic fields based on installation metadata | 🎯 Draft |

**Feature Documents:** Each feature is documented in its own markdown file within this epic folder:
- `F2.1-Load-Hierarchical-Configuration.md`
- `F2.2-Apply-Direct-Field-Mappings.md`
- `F2.3-Apply-Priority-Rules.md`
- `F2.4-Compute-Calculated-Fields.md`
- `F2.5-Transform-Fields-with-Static-Data.md`
- `F2.6-Map-IO-to-Semantic-Fields.md`

---

## 4. Architecture & Design

### 4.1 High-Level Architecture

```
Provider-Agnostic Telemetry (from E1)
    ↓
Configuration Loader (F2.1)
    ↓
Field Mapping Engine
    ├── Direct Mappings (F2.2)
    ├── Priority Rules (F2.3)
    ├── Calculated Fields (F2.4)
    ├── Transformed Fields (F2.5)
    └── I/O Mappings (F2.6)
    ↓
Fleeti Telemetry Format
    ↓
Status Computation (E3) / Storage (E4)
```

### 4.2 Key Components

- **Configuration Loader**: Load and merge hierarchical configurations
- **Field Mapping Engine**: Apply all mapping types
- **Priority Rules Engine**: Select best source from multiple fields
- **Calculation Engine**: Compute derived fields
- **Asset Service Integration**: Retrieve static data for transformations
- **I/O Mapping Engine**: Map raw I/O to semantic fields

### 4.3 Data Flow

1. **Load Configuration**: Load and merge hierarchical config (F2.1)
2. **Apply Direct Mappings**: Map 1:1 fields (F2.2)
3. **Apply Priority Rules**: Select best source (F2.3)
4. **Compute Calculated Fields**: Derive fields (F2.4)
5. **Transform with Static Data**: Combine with asset metadata (F2.5)
6. **Map I/O Fields**: Convert raw I/O to semantic (F2.6)
7. **Output**: Complete Fleeti telemetry format

---

## 5. Cross-Cutting Concerns

This epic must address the following cross-cutting concerns. **Do not duplicate content** - reference the dedicated documentation pages:

### 5.1 Security

**Reference:** [`../../7-security/README.md`](../../7-security/README.md)

Configuration files must be validated and secured. See security documentation for configuration security requirements.

### 5.2 Data Quality

**Reference:** [`../../6-data-quality/README.md`](../../6-data-quality/README.md)

Transformed fields must meet data quality standards. See data quality documentation for validation requirements.

### 5.3 Operations

**Reference:** [`../../5-operations/README.md`](../../5-operations/README.md)

Transformation pipeline must emit metrics for mapping success/failure rates. See monitoring documentation.

### 5.4 Error Handling

**Reference:** [`../../5-operations/error-handling.md`](../../5-operations/error-handling.md)

Transformation failures must be handled gracefully. Missing fields should use defaults or mark as unavailable. See error handling documentation.

---

## 6. Dependencies

### 6.1 Prerequisites

- Provider-agnostic telemetry from Epic 1
- Configuration files from Epic 5
- Asset Service for static data retrieval
- Mapping Fields Database for mapping rules

### 6.2 Dependencies on Other Epics

- **Epic 1**: Requires provider-agnostic telemetry
- **Epic 5**: Requires configuration files and mapping rules

### 6.3 Blocked Epics/Features

- **Epic 3**: Cannot compute status without transformed Fleeti fields
- **Epic 4**: Cannot store Fleeti telemetry without transformation

---

## 7. Technical Considerations

### 7.1 Performance Requirements

- **Latency:** Transformation < 50ms per packet
- **Throughput:** Handle peak ingestion rate
- **Configuration Loading:** Efficient caching and merging

### 7.2 Scalability Considerations

- Transformation pipeline is stateless and can scale horizontally
- Configuration can be cached per asset/customer
- Asset Service integration can be optimized with caching

### 7.3 Integration Points

- **Asset Service**: Retrieve installation metadata and asset specifications
- **Mapping Fields Database**: Reference mapping rules
- **Configuration Files**: Load hierarchical configurations

---

## 8. Testing Strategy

### 8.1 Unit Testing

- Configuration loading and merging
- Direct mapping application
- Priority rule selection
- Calculated field computation
- I/O mapping logic

### 8.2 Integration Testing

- End-to-end transformation with test packets
- Asset Service integration
- Configuration override scenarios

### 8.3 End-to-End Testing

- Full pipeline: Provider → Ingestion → Transformation → Status
- Configuration change testing
- Multiple provider transformation

---

## 9. References

### 9.1 Related Documentation

- **[Mapping Fields Database](../databases/mapping-fields/README.md)**: Mapping rules
- **[Fleeti Fields Database](../databases/fleeti-fields/README.md)**: Target field definitions
- **[Provider Fields Database](../databases/provider-fields/README.md)**: Source field definitions
- **[Field Mappings](../../2-field-mappings/mapping-rules.md)**: Mapping rules documentation

### 9.2 External References

- Configuration file format (YAML)
- Asset Service API

---

## 10. Open Questions

1. What is the exact YAML configuration format?
2. How are configuration conflicts resolved in hierarchical merging?
3. What is the optimal configuration caching strategy?

---

## 11. Change History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2025-01-XX | 1.0 | [Author] | Initial epic specification |

---

**Note:** This epic specification serves as the overview and index. Detailed specifications for each feature are in separate markdown files within this epic folder.

