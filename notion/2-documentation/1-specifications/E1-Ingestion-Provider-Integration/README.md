**Status:** 🎯 Draft  
**Epic Number:** E1  
**Related Epics:** E2 (Field Mapping depends on ingestion), E4 (Storage depends on ingestion)

---

# 1. Overview

The Ingestion & Provider Integration epic handles receiving raw telemetry packets from multiple providers (Navixy, Teltonika, future OEMs), parsing provider-specific formats, validating data integrity, and preparing packets for transformation.

### 1.1 Purpose

This epic enables the telemetry system to receive and process telemetry from any provider, making Fleeti provider-agnostic. It establishes the foundation for all downstream processing by ensuring clean, validated, provider-agnostic telemetry data flows into the transformation pipeline.

### 1.2 Scope

**In Scope:**
- Receiving telemetry packets from providers (Data Forwarding, API polling, direct integration)
- Parsing provider-specific formats (Navixy, Teltonika, OEM formats)
- Validating packet schema and data integrity
- Normalizing provider data to provider-agnostic structure
- Saving raw packets to cold storage
- Provider authentication (already implemented for Navixy)

**Out of Scope:**
- Field mapping and transformation (Epic 2)
- Status computation (Epic 3)
- Storage tier management (Epic 4)
- Configuration management (Epic 5)

### 1.3 Key Concepts

- **Provider-Agnostic Interface**: All providers implement a common parsing interface
- **Data Forwarding**: Real-time telemetry forwarding from Navixy (already implemented)
- **Provider Parsers**: Convert provider-specific formats to unified structure
- **Packet Validation**: Schema validation and data integrity checks
- **Cold Storage**: Permanent archive of raw provider packets

---

## 2. Epic Goals & Success Criteria

### 2.1 Goals

- Receive telemetry packets from multiple providers in real-time
- Parse provider-specific formats into provider-agnostic structure
- Validate data integrity and handle malformed packets gracefully
- Archive all raw packets for historical recalculation
- Support new providers without major refactoring

### 2.2 Success Criteria

- System receives and processes telemetry from Navixy Data Forwarding
- Provider parsers successfully convert provider formats to unified structure
- Invalid packets are detected and handled without system failure
- All raw packets are stored in cold storage
- System can be extended to support new providers (Teltonika, OEM) with minimal changes

---

## 3. Features

This epic is composed of the following features, each delivering standalone value:

### Feature List

| Feature ID | Feature Name | Description | Status |
|------------|--------------|-------------|--------|
| F1.1 | Receive Provider Packets | Receive telemetry packets from providers (Data Forwarding, API, direct) | 🎯 Draft |
| F1.2 | Validate Packet Schema | Validate packet structure, required fields, and data types | 🎯 Draft |
| F1.3 | Parse Provider Format | Convert provider-specific format to provider-agnostic structure | 🎯 Draft |
| F1.4 | Save to Cold Storage | Archive raw provider packets to cold storage for historical recalculation | 🎯 Draft |

**Feature Documents:** Each feature is documented in its own markdown file within this epic folder:
- `F1.1-Receive-Provider-Packets.md`
- `F1.2-Validate-Packet-Schema.md`
- `F1.3-Parse-Provider-Format.md`
- `F1.4-Save-to-Cold-Storage.md`

---

## 4. Architecture & Design

### 4.1 High-Level Architecture

```
Provider (Navixy/Teltonika/OEM)
    ↓
Ingestion Layer
    ├── Provider Parser (provider-specific)
    ├── Validation Engine
    └── Normalization Engine
    ↓
Provider-Agnostic Telemetry Structure
    ↓
Cold Storage (raw archive)
    ↓
Transformation Pipeline (Epic 2)
```

### 4.2 Key Components

- **Provider Parsers**: Convert provider-specific formats to unified structure
- **Validation Engine**: Schema validation and data integrity checks
- **Normalization Engine**: Standardize field names and types
- **Data Forwarding Handler**: Process Navixy Data Forwarding packets (already implemented)
- **Cold Storage Writer**: Archive raw packets to permanent storage

### 4.3 Data Flow

1. **Receive**: Provider sends telemetry packet (Data Forwarding, API, direct)
2. **Parse**: Provider parser converts format to provider-agnostic structure
3. **Validate**: Validation engine checks schema and data integrity
4. **Normalize**: Normalize field names and types
5. **Archive**: Save raw packet to cold storage
6. **Forward**: Send provider-agnostic telemetry to transformation pipeline

---

## 5. Cross-Cutting Concerns

This epic must address the following cross-cutting concerns. **Do not duplicate content** - reference the dedicated documentation pages:

### 5.1 Security

**Reference:** [`../../7-security/README.md`](../../7-security/README.md)

Provider authentication is already implemented for Navixy Data Forwarding. New provider integrations must authenticate requests using API keys or OAuth as specified in the security documentation.

### 5.2 Data Quality

**Reference:** [`../../6-data-quality/README.md`](../../6-data-quality/README.md)

Packet validation must follow data quality validation rules. Invalid packets should be logged and sent to dead letter queue for review.

### 5.3 Operations

**Reference:** [`../../5-operations/README.md`](../../5-operations/README.md)

Ingestion layer must emit metrics for packets received, parsed, validated, and failed. See monitoring documentation for required metrics.

### 5.4 Error Handling

**Reference:** [`../../5-operations/error-handling.md`](../../5-operations/error-handling.md)

Transient errors (network timeouts, temporary unavailability) must be retried using exponential backoff. Permanent errors (invalid schema, authentication failures) should be logged and sent to dead letter queue.

---

## 6. Dependencies

### 6.1 Prerequisites

- Provider authentication setup (Navixy already implemented)
- Cold storage infrastructure (Epic 4)
- Provider field catalogs in Provider Fields Database

### 6.2 Dependencies on Other Epics

- **Epic 2 (Field Mapping)**: Depends on provider-agnostic telemetry from this epic
- **Epic 4 (Storage)**: Requires cold storage to be available

### 6.3 Blocked Epics/Features

- **Epic 2**: Cannot transform telemetry without ingestion
- **Epic 3**: Cannot compute status without transformed telemetry (depends on Epic 2)

---

## 7. Technical Considerations

### 7.1 Performance Requirements

- **Latency**: Packet processing < 50ms (to support real-time requirements)
- **Throughput**: Handle peak load of ~1,700 packets/second (Year 5 projection)
- **Scalability**: Horizontal scaling for stateless parser services

### 7.2 Scalability Considerations

- Provider parsers are stateless and can scale horizontally
- Validation engine can be parallelized
- Cold storage writes can be batched for efficiency

### 7.3 Integration Points

- **Navixy Data Forwarding**: Real-time packet forwarding (already implemented)
- **Cold Storage**: Archive raw packets (Epic 4)
- **Transformation Pipeline**: Forward provider-agnostic telemetry (Epic 2)
- **Provider Fields Database**: Reference provider field definitions

---

## 8. Testing Strategy

### 8.1 Unit Testing

- Provider parser unit tests with sample packets
- Validation engine tests with valid/invalid packets
- Normalization engine tests with various provider formats

### 8.2 Integration Testing

- End-to-end ingestion flow with test providers
- Cold storage integration tests
- Error handling and retry logic tests

### 8.3 End-to-End Testing

- Full pipeline test: Provider → Ingestion → Cold Storage → Transformation
- Load testing with high packet volumes
- Provider outage simulation

---

## 9. References

### 9.1 Related Documentation

- **[📥 Provider Fields Database](../databases/provider-fields/README.md)**: Provider field definitions
- **[Field Mappings](../../2-field-mappings/provider-fields-catalog.md)**: Provider field catalogs
- **[Architecture Overview](../../../1-overview-vision/3-architecture-overview.md)**: System architecture

### 9.2 External References

- Navixy Data Forwarding documentation (already implemented)
- Provider-specific documentation (Teltonika, OEM APIs)

---

## 10. Open Questions

1. What is the exact format for Teltonika packets?
2. How will OEM direct integration work (API format, authentication)?
3. What is the optimal batch size for cold storage writes?

---

## 11. Change History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2025-01-XX | 1.0 | [Author] | Initial epic specification |

---

**Note:** This epic specification serves as the overview and index. Detailed specifications for each feature are in separate markdown files within this epic folder.

