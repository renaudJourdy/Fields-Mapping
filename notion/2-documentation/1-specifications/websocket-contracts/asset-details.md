# Asset Details WebSocket Contract

**Status:** 🎯 To Be Created  
**Priority:** 🔴 HIGH (Blocking Frontend Development)  
**Stream:** `live.asset.details`

---

## Overview

This WebSocket stream provides real-time asset details updates for the asset details panel. It delivers comprehensive telemetry data, status information, and sensor readings needed for displaying detailed asset information in real-time.

---

## Stream Information

- **Stream Name:** `live.asset.details`
- **Version:** `v1`
- **Purpose:** Real-time asset details updates for asset details panel
- **Frontend Use:** Asset details panel display with live telemetry, sensors, KPIs, and status information

---

## Authentication

- **Method:** Bearer token (same as app API authentication)
- **Channel:** Single WebSocket connection per app session
- **Rejection:** Connection rejected if token invalid/expired

---

## Subscription

**Client → Server:**
```json
{
  "action": "subscribe",
  "stream": "live.asset.details",
  "version": "v1",
  "asset_id": "uuid"
}
```

**Server → Client (Response):**
```json
{
  "type": "subscribed",
  "subscription_id": "sub_asset_details",
  "stream": "live.asset.details.v1",
  "asset_id": "uuid",
  "at": "2025-01-21T12:00:00Z"
}
```

---

## Message Types

### Snapshot

Initial full state sent after subscription.

[Full message format to be defined based on Fleeti Fields Database]

### Delta

Incremental updates after snapshot.

[Full message format to be defined based on Fleeti Fields Database]

### Update

Client changes asset selection.

[Full message format to be defined based on Fleeti Fields Database]

### Error & Resync

Error handling and resync requests.

[Full message format to be defined]

---

## Field References

This stream includes Fleeti fields from the [🎯 Fleeti Fields Database](./databases/fleeti-fields/README.md):
- `asset.id`, `asset.name`, `asset.type`, `asset.make`, `asset.model`
- `status.top_status` (computed)
- `status.statuses[]` (computed)
- `location.latitude`, `location.longitude`, `location.heading`, `location.address`
- `motion.speed`, `motion.is_moving`
- `power.ignition`, `power.battery_voltage`
- `fuel.level`, `fuel.consumption`
- `sensors.*` (temperature, door status, etc.)
- `counters.*` (odometer, engine hours, etc.)
- [Additional fields to be defined based on frontend needs]

---

## Related Documentation

- **[🔗 Epic 6 - API & Consumption](../E6-API-Consumption/README.md)**: Usage and implementation needs
- **[🎯 Fleeti Fields Database](./databases/fleeti-fields/README.md)**: Field definitions
- **[Mobile App Specs](../../../docs/rag/SPECIFICATIONS_FAQ.md)**: Frontend requirements

---

**Last Updated:** 2025-01-XX  
**Status:** 🎯 To Be Created

