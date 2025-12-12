**Status:** 🎯 Draft  
**Epic Number:** E3  
**Related Epics:** E2 (depends on transformed Fleeti fields), E6 (top status used for marker display)

---

## 1. Overview

The Status Computation epic computes status families (Connectivity, Transit, Engine, Immobilization) and the top status for each asset based on telemetry data and asset metadata.

### 1.1 Purpose

Compute standardized status families that provide consistent operational state information regardless of provider. The top status determines which status is most critical for display (e.g., marker iconography on the live map).

### 1.2 Scope

**In Scope:**
- Compute Connectivity status (online/offline)
- Compute Transit status (in_transit/parked)
- Compute Engine status (running/standby)
- Compute Immobilization status (immobilized/immobilizing/releasing/free)
- Compute top status (highest-priority status family)
- Status compatibility matrices (which statuses apply to which asset types)
- Status state machines and transition logic

**Out of Scope:**
- Field mapping (Epic 2)
- Storage operations (Epic 4)
- API exposure (Epic 6)

### 1.3 Key Concepts

- **Status Families**: Grouped statuses (Connectivity, Transit, Engine, Immobilization)
- **Top Status**: Highest-priority status family for display
- **Priority Hierarchy**: Connectivity > Immobilization > Engine > Transit
- **Compatibility Matrices**: Which statuses apply to which asset types
- **State Machines**: Status transition logic and trigger conditions

---

## 2. Epic Goals & Success Criteria

### 2.1 Goals

- Compute all status families correctly based on telemetry
- Determine top status for marker display
- Support status compatibility by asset type
- Enable status state transitions with proper timing
- Provide status change timestamps for duration calculations

### 2.2 Success Criteria

- All status families computed correctly for supported asset types
- Top status correctly identifies highest-priority status
- Status transitions occur at correct trigger conditions
- Status change timestamps enable duration calculations
- Compatibility matrices correctly filter statuses by asset type

---

## 3. Features

This epic is composed of the following features, each delivering standalone value:

### Feature List

| Feature ID | Feature Name | Description | Status |
|------------|--------------|-------------|--------|
| F3.1 | Compute Connectivity Status | Compute online/offline status based on last_updated_at | 🎯 Draft |
| F3.2 | Compute Transit Status | Compute in_transit/parked status based on motion and ignition | 🎯 Draft |
| F3.3 | Compute Engine Status | Compute running/standby status based on engine signals | 🎯 Draft |
| F3.4 | Compute Immobilization Status | Compute immobilized/immobilizing/releasing/free status | 🎯 Draft |
| F3.5 | Compute Top Status | Compute highest-priority status family for display | 🎯 Draft |

**Feature Documents:** Each feature is documented in its own markdown file within this epic folder:
- `F3.1-Compute-Connectivity-Status.md`
- `F3.2-Compute-Transit-Status.md`
- `F3.3-Compute-Engine-Status.md`
- `F3.4-Compute-Immobilization-Status.md`
- `F3.5-Compute-Top-Status.md`

---

## 4. Architecture & Design

### 4.1 High-Level Architecture

```
Fleeti Telemetry (from E2)
    ↓
Status Computation Engine
    ├── Connectivity Status (F3.1)
    ├── Transit Status (F3.2)
    ├── Engine Status (F3.3)
    ├── Immobilization Status (F3.4)
    └── Top Status (F3.5)
    ↓
Status Object
    ├── top_status
    └── statuses[]
    ↓
Storage (E4) / API (E6)
```

### 4.2 Key Components

- **Status Computation Engine**: Orchestrates status family computation
- **Connectivity Status Computer**: Computes online/offline
- **Transit Status Computer**: Computes in_transit/parked
- **Engine Status Computer**: Computes running/standby
- **Immobilization Status Computer**: Computes immobilization states
- **Top Status Computer**: Selects highest-priority status family

### 4.3 Data Flow

1. **Receive Telemetry**: Fleeti telemetry from Epic 2
2. **Compute Status Families**: Compute each status family (F3.1-F3.4)
3. **Apply Compatibility**: Filter statuses by asset type compatibility
4. **Compute Top Status**: Select highest-priority status (F3.5)
5. **Output**: Status object with top_status and statuses[]

---

## 5. Cross-Cutting Concerns

This epic must address the following cross-cutting concerns. **Do not duplicate content** - reference the dedicated documentation pages:

### 5.2 Data Quality

**Reference:** [`../../6-data-quality/README.md`](../../6-data-quality/README.md)

Status computation must handle missing or invalid telemetry fields gracefully. See data quality documentation.

### 5.3 Operations

**Reference:** [`../../5-operations/README.md`](../../5-operations/README.md)

Status computation must emit metrics for computation success/failure rates. See monitoring documentation.

### 5.4 Error Handling

**Reference:** [`../../5-operations/error-handling.md`](../../5-operations/error-handling.md)

Status computation failures should use safe defaults (e.g., assume online if connectivity cannot be determined). See error handling documentation.

---

## 6. Dependencies

### 6.1 Prerequisites

- Transformed Fleeti telemetry from Epic 2
- Asset metadata (for compatibility matrices)
- Status rules and compatibility matrices

### 6.2 Dependencies on Other Epics

- **Epic 2**: Requires transformed Fleeti fields (especially `power.ignition`, `motion.is_moving`, `last_updated_at`)

### 6.3 Blocked Epics/Features

- **Epic 6**: Cannot expose status via API without status computation
- **Frontend Markers**: Cannot display markers without top status

---

## 7. Technical Considerations

### 7.1 Performance Requirements

- **Latency:** Status computation < 10ms per packet
- **Throughput:** Handle computation at transformation rate
- **State Tracking:** Efficient state machine implementation

### 7.2 Scalability Considerations

- Status computation is stateless (per packet)
- State transitions tracked per asset
- Compatibility matrices can be cached

### 7.3 Integration Points

- **Fleeti Telemetry**: Input from Epic 2
- **Asset Metadata**: For compatibility matrices
- **Status Rules**: Reference status computation rules

---

## 8. Testing Strategy

### 8.1 Unit Testing

- Status computation for each family
- State machine transitions
- Compatibility matrix filtering
- Top status selection

### 8.2 Integration Testing

- End-to-end status computation with real telemetry
- Multiple status families
- Asset type compatibility

### 8.3 End-to-End Testing

- Full pipeline: Telemetry → Status → Marker Display
- Status transition scenarios
- Edge cases and error handling

---

## 9. References

### 9.1 Related Documentation

- **[Status Rules](./status-rules.md)**: Status computation rules (legacy reference)
- **[🎯 Fleeti Fields Database](../databases/fleeti-fields/README.md)**: Required telemetry fields
- **[📍 WebSocket Contracts](../websocket-contracts/live-map-markers.md)**: Top status usage

### 9.2 External References

- Status rules documentation (to be migrated to feature specs)

---

## 10. Open Questions

1. What are the exact trigger conditions for each status transition?
2. What are the compatibility matrices for each asset type?
3. How should status transitions be timed (immediate vs delayed)?

---

## 11. Change History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2025-01-XX | 1.0 | [Author] | Initial epic specification |

---

**Note:** This epic specification serves as the overview and index. Detailed specifications for each feature are in separate markdown files within this epic folder.

