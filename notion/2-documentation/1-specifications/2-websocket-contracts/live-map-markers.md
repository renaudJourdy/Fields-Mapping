**Status:** 🎯 To Be Created  
**Priority:** 🔴 HIGH (Blocking Frontend Development)  
**Stream:** `live.map.markers`

---

# Overview

This WebSocket stream provides real-time marker updates for assets displayed on the live map. It delivers `top_status`, position, heading, and status information needed for marker rendering.

---

# Stream Information

- **Stream Name:** `live.map.markers`
- **Version:** `v1`
- **Purpose:** Real-time marker updates for live map display
- **Frontend Use:** Marker rendering with status-based iconography

---

# Authentication

- **Method:** Bearer token (same as app API authentication)
- **Channel:** Single WebSocket connection per app session
- **Rejection:** Connection rejected if token invalid/expired

---

# Subscription

**Client → Server:**
```json
{
  "action": "subscribe",
  "stream": "live.map.markers",
  "version": "v1",
  "viewport": {
    "north": 14.68,
    "south": 14.65,
    "east": -17.05,
    "west": -17.09
  },
  "zoom": 10,
  "rate_limit_hz": 5
}
```

**Server → Client (Response):**
```json
{
  "type": "subscribed",
  "subscription_id": "sub_markers",
  "stream": "live.map.markers.v1",
  "at": "2025-01-21T12:00:00Z"
}
```

---

# Message Types

## Snapshot

Initial full state sent after subscription.

[Full message format to be defined based on Fleeti Fields Database]

## Delta

Incremental updates after snapshot.

[Full message format to be defined based on Fleeti Fields Database]

## Update

Client updates viewport/zoom.

[Full message format to be defined based on Fleeti Fields Database]

## Error & Resync

Error handling and resync requests.

[Full message format to be defined]

---

# Field References

This stream includes Fleeti fields from the [🎯 Fleeti Fields Database](./databases/fleeti-fields/README.md):
- `status.top_status` (computed)
- `status.statuses[]` (computed)
- `location.latitude`, `location.longitude`
- `location.heading`
- `asset.id`, `asset.type`
- [Additional fields to be defined based on frontend needs]

---

# Related Documentation

- **[✅ Epic 3 - Status Computation](../E3-Status-Computation/README.md)**: Top status computation logic
- **[🎯 Fleeti Fields Database](./databases/fleeti-fields/README.md)**: Field definitions
- **[Mobile App Specs](../../../docs/rag/SPECIFICATIONS_FAQ.md)**: Frontend requirements

---

**Last Updated:** 2025-01-XX  
**Status:** 🎯 To Be Created

