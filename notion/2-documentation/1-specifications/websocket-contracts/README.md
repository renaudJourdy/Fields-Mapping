**Status:** 🎯 Structure Created - Content To Be Developed

This section contains detailed WebSocket contract specifications for real-time telemetry streaming to frontend applications.

## Purpose

WebSocket contracts define:
- Stream names and versions
- Message formats and structures
- Subscription parameters
- Update patterns (snapshot, delta)
- Error handling and resync procedures

**Note:** WebSocket contracts are **abstract** - they specify which Fleeti fields are included, not how provider fields map to them (mapping is handled in Epic 2).

---

## Available Contracts

### [Live Map Markers](./live-map-markers.md)

WebSocket stream for real-time marker updates on the live map.

**Stream:** `live.map.markers`  
**Purpose:** Display asset markers on map with status-based iconography  
**Key Fields:** `top_status`, `statuses[]`, `position`, `heading`, `assetId`, `assetType`

**Status:** 🎯 To Be Created  
**Priority:** 🔴 HIGH (Blocking Frontend Development)

---

## Contract Structure

Each contract document includes:
- Stream name and version
- Authentication requirements
- Subscription parameters
- Message types (subscribe, snapshot, delta, update, error, resync)
- Message formats and examples
- Field references (Fleeti fields from Fleeti Fields Database)
- Sequencing and idempotency rules
- Rate limiting

---

## Relationship to Fleeti Fields Database

WebSocket contracts reference Fleeti fields from the [Fleeti Fields Database](./databases/fleeti-fields/README.md):
- Contracts specify which Fleeti fields are included in each stream
- Field definitions come from the database
- As new Fleeti fields are added, contracts may be updated

---

## Related Documentation

- **[Epic 6 - API & Consumption](../E6-API-Consumption/README.md)**: Usage and implementation needs
- **[Fleeti Fields Database](./databases/fleeti-fields/README.md)**: Field definitions
- **[Mobile App Specs](../../../docs/rag/SPECIFICATIONS_FAQ.md)**: Frontend requirements reference

---

**Last Updated:** 2025-01-XX  
**Section Status:** 🎯 Structure Created - Content To Be Developed

