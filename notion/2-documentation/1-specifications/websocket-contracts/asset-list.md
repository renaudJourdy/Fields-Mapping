# Asset List WebSocket Contract

**Status:** 🎯 To Be Created  
**Priority:** 🔴 HIGH (Blocking Frontend Development)  
**Stream:** `live.assets.list`

---

## Overview

This WebSocket stream provides real-time asset list updates for the asset list panel. It delivers asset metadata, status information, and grouping data needed for displaying and filtering assets in the list view.

---

## Stream Information

- **Stream Name:** `live.assets.list`
- **Version:** `v1`
- **Purpose:** Real-time asset list updates for asset list panel
- **Frontend Use:** Asset list panel display, grouping, search, and selection synchronization

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
  "stream": "live.assets.list",
  "version": "v1",
  "grouping_mode": "group",
  "search_query": "",
  "pagination": {
    "offset": 0,
    "limit": 50
  }
}
```

**Server → Client (Response):**
```json
{
  "type": "subscribed",
  "subscription_id": "sub_asset_list",
  "stream": "live.assets.list.v1",
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

Client updates grouping mode, search query, or pagination.

[Full message format to be defined based on Fleeti Fields Database]

### Error & Resync

Error handling and resync requests.

[Full message format to be defined]

---

## Field References

This stream includes Fleeti fields from the [🎯 Fleeti Fields Database](./databases/fleeti-fields/README.md):
- `asset.id`, `asset.name`, `asset.type`
- `status.top_status` (computed)
- `status.statuses[]` (computed)
- `location.latitude`, `location.longitude`
- `motion.speed`, `motion.is_moving`
- [Additional fields to be defined based on frontend needs]

---

## Related Documentation

- **[🔗 Epic 6 - API & Consumption](../E6-API-Consumption/README.md)**: Usage and implementation needs
- **[🎯 Fleeti Fields Database](./databases/fleeti-fields/README.md)**: Field definitions
- **[Mobile App Specs](../../../docs/rag/SPECIFICATIONS_FAQ.md)**: Frontend requirements

---

**Last Updated:** 2025-01-XX  
**Status:** 🎯 To Be Created

