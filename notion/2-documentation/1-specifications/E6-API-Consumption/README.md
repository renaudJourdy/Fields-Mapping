**Status:** 🎯 Draft  
**Epic Number:** E6  
**Related Epics:** E3 (status computation), E4 (storage), E5 (configuration)

---

## 1. Overview

The API & Consumption epic exposes Fleeti telemetry data via WebSocket streams and REST API endpoints. Enables frontend applications and customers to consume telemetry data.

### 1.1 Purpose

Provide real-time and historical access to Fleeti telemetry data. WebSocket streams enable real-time marker updates for live map, REST APIs enable historical data access and customer integration.

### 1.2 Scope

**In Scope:**
- WebSocket streams for real-time telemetry (live map markers)
- REST API endpoints for historical telemetry
- API authentication and authorization
- Rate limiting and performance optimization
- WebSocket contract specifications (referencing contracts folder)

**Out of Scope:**
- Telemetry transformation (Epic 2)
- Status computation (Epic 3)
- Storage operations (Epic 4)

### 1.3 Key Concepts

- **WebSocket Streams**: Real-time telemetry streaming for frontend
- **REST APIs**: Historical telemetry access via REST endpoints
- **Hot/Warm Storage**: Query appropriate storage tier based on latency requirements
- **API Contracts**: Detailed contract specifications in contracts folder

---

## 2. Epic Goals & Success Criteria

### 2.1 Goals

- Expose real-time telemetry via WebSocket streams
- Expose historical telemetry via REST APIs
- Support live map marker updates
- Support customer API access
- Meet latency requirements (< 100ms for hot, < 500ms for warm)

### 2.2 Success Criteria

- WebSocket streams deliver real-time updates for live map
- REST APIs provide historical telemetry access
- API latency meets requirements
- Authentication and authorization work correctly
- Rate limiting prevents abuse

---

## 3. Features

This epic is composed of the following features, each delivering standalone value:

### Feature List

| Feature ID | Feature Name | Description | Status |
|------------|--------------|-------------|--------|
| F6.1 | WebSocket Stream for Live Map Markers | Real-time marker updates via WebSocket stream | 🎯 Draft |
| F6.2 | REST API for Hot Storage | REST endpoints for core fields from hot storage | 🎯 Draft |
| F6.3 | REST API for Warm Storage | REST endpoints for complete telemetry from warm storage | 🎯 Draft |
| F6.4 | API Authentication & Authorization | Authenticate and authorize API requests | 🎯 Draft |
| F6.5 | Rate Limiting & Performance | Rate limiting and performance optimization | 🎯 Draft |

**Feature Documents:** Each feature is documented in its own markdown file within this epic folder:
- `F6.1-WebSocket-Stream-for-Live-Map-Markers.md`
- `F6.2-REST-API-for-Hot-Storage.md`
- `F6.3-REST-API-for-Warm-Storage.md`
- `F6.4-API-Authentication-Authorization.md`
- `F6.5-Rate-Limiting-Performance.md`

---

## 4. Architecture & Design

### 4.1 High-Level Architecture

```
Storage (E4)
    ├── Hot Storage (< 100ms)
    └── Warm Storage (< 500ms)
    ↓
API Layer (E6)
    ├── WebSocket Streams (F6.1)
    └── REST APIs (F6.2, F6.3)
    ↓
Frontend / Customers
```

### 4.2 Key Components

- **WebSocket Server**: Real-time streaming server
- **REST API Server**: REST endpoint server
- **Authentication Service**: API authentication and authorization
- **Rate Limiter**: Rate limiting and throttling
- **Storage Query Layer**: Query hot/warm storage

### 4.3 Data Flow

1. **WebSocket**: Client subscribes → Stream real-time updates from hot storage
2. **REST Hot**: Client requests → Query hot storage → Return core fields
3. **REST Warm**: Client requests → Query warm storage → Return complete fields

---

## 5. Cross-Cutting Concerns

This epic must address the following cross-cutting concerns. **Do not duplicate content** - reference the dedicated documentation pages:

### 5.1 Security

**Reference:** [`../../7-security/README.md`](../../7-security/README.md)

API authentication and authorization must follow security guidelines. See security documentation.

### 5.3 Operations

**Reference:** [`../../5-operations/README.md`](../../5-operations/README.md)

API operations must emit metrics for performance monitoring. See monitoring documentation.

### 5.4 Error Handling

**Reference:** [`../../5-operations/error-handling.md`](../../5-operations/error-handling.md)

API errors must be handled gracefully. See error handling documentation.

---

## 6. Dependencies

### 6.1 Prerequisites

- Hot storage from Epic 4 (F4.1)
- Warm storage from Epic 4 (F4.2)
- Status computation from Epic 3
- Transformed telemetry from Epic 2

### 6.2 Dependencies on Other Epics

- **Epic 3**: Requires status computation (top_status) for marker display
- **Epic 4**: Requires hot/warm storage for data access

### 6.3 Blocked Epics/Features

- **Frontend Development**: Cannot display markers without WebSocket stream

---

## 7. Technical Considerations

### 7.1 Performance Requirements

- **WebSocket Latency:** < 100ms for marker updates
- **REST Hot Latency:** < 100ms for core fields
- **REST Warm Latency:** < 500ms for complete fields
- **Throughput:** Handle concurrent connections and requests

### 7.2 Scalability Considerations

- WebSocket server must scale horizontally
- REST API server must scale horizontally
- Storage queries must be optimized
- Rate limiting must be efficient

### 7.3 Integration Points

- **Hot Storage**: Query core fields for real-time updates
- **Warm Storage**: Query complete fields for historical access
- **Authentication Service**: Authenticate API requests
- **WebSocket Contracts**: Reference contract specifications

---

## 8. Testing Strategy

### 8.1 Unit Testing

- WebSocket stream logic
- REST API endpoint logic
- Authentication and authorization
- Rate limiting logic

### 8.2 Integration Testing

- End-to-end WebSocket streaming with real data
- End-to-end REST API with real data
- Storage integration
- Authentication integration

### 8.3 End-to-End Testing

- Full pipeline: Storage → API → Frontend
- Load testing with concurrent connections
- Latency testing

---

## 9. References

### 9.1 Related Documentation

- **[📡 WebSocket Contracts](../websocket-contracts/README.md)**: WebSocket contract specifications
- **[🌐 API Contracts](../api-contracts/README.md)**: REST API contract specifications
- **[✅ Epic 3 - Status Computation](../E3-Status-Computation/README.md)**: Top status computation
- **[💾 Epic 4 - Storage](../E4-Storage-Data-Management/README.md)**: Storage architecture

---

## 10. Open Questions

1. What is the exact WebSocket message format?
2. What are the exact REST API endpoints?
3. How should rate limiting be implemented?

---

## 11. Change History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2025-01-XX | 1.0 | [Author] | Initial epic specification |

---

**Note:** This epic specification serves as the overview and index. Detailed specifications for each feature are in separate markdown files within this epic folder.

