# Updates

- 2025-02-01: Clarified cluster top_status aggregation, subscription_id guidance, and verified Fleeti field paths against the latest export.

---

# Overview

This WebSocket stream provides real-time marker updates for assets displayed on the live map. It delivers position, heading, status, and motion information needed for marker rendering. The stream includes server-side clustering support, where assets are automatically grouped into clusters based on viewport and zoom level.

---

# Stream Information

- **Stream Name:** `live.map.markers`
- **Version:** `v1`
- **Purpose:** Real-time marker updates for live map display with server-side clustering
- **Frontend Use:** Marker rendering with status-based iconography and cluster visualization

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
  "params": {
    "viewport": {
      "bounds": [[-25.0, -20.0], [60.0, 70.0]],
      "zoom": 5
    },
    "filters": {
      "search": null
    },
    "rate_limit_hz": 2
  }
}
```

**Viewport Structure:**

- `bounds`: 2D array defining southwest and northeast corners `[[min_lat, min_lng], [max_lat, max_lng]]`
- `zoom`: Integer zoom level (used by backend for clustering decisions)

**Filters Structure:**

- `search`: String or null - filters assets by metadata (name, group name, etc.)

**Future Filters (not yet available):**

- `group_ids`: array of integers - Restrict to specific asset groups
- `customer_reference`: array of strings - Restrict to specific customer accounts
- `country`: string - Restrict to assets in a specific country
- `focus`: string - Define focus mode (default, fuel, temperature, etc.)
- `top_status`: string - Restrict to assets with specific top-level status

**Server → Client (Response):**

```json
{
  "type": "subscribed",
  "subscription_id": "live.map.markers",
  "stream": "live.map.markers",
  "version": "v1",
  "at": "2025-10-23T14:00:00Z",
  "params_echo": {
    "viewport": {
      "bounds": [[-25.0, -20.0], [60.0, 70.0]],
      "zoom": 5
    },
    "filters": {
      "search": null
    },
    "rate_limit_hz": 2
  },
  "server_caps": {
    "snapshot": true,
    "delta": true,
    "clustering": "server"
  }
}
```

**Server Capabilities:**

- `snapshot: true` - Server sends initial full state snapshot
- `delta: true` - Server sends incremental updates after snapshot
- `clustering: "server"` - Backend handles clustering based on viewport and zoom
- `subscription_id` Guidance
    - Treat subscription_id as an opaque identifier. Use the value provided by the server for subsequent updates.
    - A single connection may support multiple subscriptions in the future; do not assume subscription_id equals the stream name.

---

# Message Types

## Snapshot

Initial full state sent after subscription. Contains all assets and clusters within the subscribed viewport.

**Structure:**

```json
{
  "type": "snapshot",
  "subscription_id": "live.map.markers",
  "seq": 1,
  "at": "2025-10-23T14:00:01Z",
  "data": [
    {
      "kind": "asset",
      "asset_id": 1001,
      "name": "Vehicle 12",
      "asset_type": "vehicle",
      "asset_subtype": "truck",
      "last_updated_at": "2025-10-23T13:59:50Z",
      "location": {
        "latitude": 48.8566,
        "longitude": 2.3522,
        "heading": 270
      },
      "status": {
        "top_status": {
          "family": "transit",
          "code": "in_transit",
          "last_changed_at": "2025-10-23T13:45:00Z"
        },
        "statuses": {
          "connectivity": {
            "code": "online"
          },
          "immobilization": {
            "code": null
          },
          "engine": {
            "code": null
          },
          "transit": {
            "code": "in_transit"
          }
        }
      },
      "motion": {
        "speed": {
          "value": 65
        }
      }
    },
    {
      "kind": "cluster",
      "cluster_id": "c_1",
      "location": {
        "latitude": 48.8600,
        "longitude": 2.3400
      },
      "cluster_count": 17,
      "top_status": {
        "family": "immobilization",
        "code": "immobilized"
      }
    }
  ]
}

```

## Delta

Incremental updates sent after snapshot. Contains only changed assets and cluster updates.

**Structure:**

```json
{
  "type": "delta",
  "subscription_id": "live.map.markers",
  "seq": 42,
  "at": "2025-10-23T14:01:30Z",
  "changes": [
    {
      "kind": "asset",
      "asset_id": 1001,
      "status": {
        "top_status": {
          "code": "parked",
          "last_changed_at": "2025-10-23T14:01:25Z"
        },
        "statuses": {
          "transit": {
            "code": "parked"
          }
        }
      },
      "motion": {
        "speed": {
          "value": 0
        }
      }
    },
    {
      "kind": "cluster",
      "cluster_id": "c_1",
      "cluster_count": 18,
      "top_status": {
        "family": "transit",
        "code": "in_transit"
      }
    },
    {
      "kind": "asset",
      "asset_id": 1002,
      "removed": true
    }
  ]
}

```

## Update

Client sends viewport/filter/zoom changes. Server responds with new snapshot or delta.

**Client → Server:**

```json
{
  "action": "update",
  "subscription_id": "live.map.markers",
  "params": {
    "viewport": {
      "bounds": [[47.0, -18.0], [49.0, -16.0]],
      "zoom": 8
    },
    "filters": {
      "search": "truck"
    },
    "rate_limit_hz": 2
  }
}

```

## Error & Resync

**Error Message:**

```json
{
  "type": "error",
  "subscription_id": "live.map.markers",
  "code": "invalid_viewport",
  "message": "Invalid viewport bounds",
  "at": "2025-10-23T14:02:00Z"
}

```

**Resync Required:**

```json
{
  "type": "resync_required",
  "subscription_id": "live.map.markers",
  "reason": "sequence_gap",
  "last_valid_seq": 100,
  "at": "2025-10-23T14:02:00Z"
}

```

Client should re-subscribe when receiving `resync_required`.

---

# Field References

This stream includes Fleeti telemetry fields grouped by category, using exact field paths from the Fleeti Fields Database. 

[Untitled](https://www.notion.so/2d23e766c901800a8a21f5b1590d9aeb?pvs=21)

---

# Clustering

Clustering is performed server-side based on viewport bounds and zoom level. The backend automatically groups nearby assets into clusters when appropriate.

## Cluster Structure

- `kind`: Always `"cluster"`
- `cluster_id`: Unique cluster identifier (string)
- `location.latitude`: Cluster center latitude (number)
- `location.longitude`: Cluster center longitude (number)
- `cluster_count`: Number of assets in cluster (integer)
- `top_status.family`: Top status family for cluster color display (string: connectivity/immobilization/engine/transit)
- `top_status.code`: Top status code for cluster color display (string: offline/immobilized/running/in_transit/parked/online) - determined by highest priority status among clustered assets

## Clustering Behavior

- Clusters are computed automatically by the backend
- Clustering algorithm and thresholds are implementation details
- Client should render clusters as provided without attempting local re-clustering
- Clusters may appear, merge, split, or disappear as viewport changes
- Cluster `top_status.code` determines the visual color/styling of the cluster marker
- Cluster `top_status` uses the same family priority as individual assets (Connectivity > Immobilization > Engine > Transit), applied across all assets in the cluster.

---

# Filters

Filters scope the real-time data to a meaningful subset of assets based on metadata and status.

## Current Filter Support

### Search Filter

- `filters.search`: String or null
- Filters assets by metadata fields (name, group name, etc.)
- Search is case-insensitive and matches partial strings
- When null, no search filtering is applied

## Future Filter Support (not yet available)

The following filters are planned for future releases:

- `filters.group_ids`: Array of integers - Restrict to specific asset groups
- `filters.customer_reference`: Array of strings - Restrict to specific customer accounts
- `filters.country`: String - Restrict to assets located in a specific country
- `filters.focus`: String - Define focus mode (default, fuel, temperature, ecodriving, etc.)
- `filters.top_status`: String - Restrict to assets with specific top-level statuses

When filters change in the UI, the client must send an `update` action with the new filter set.