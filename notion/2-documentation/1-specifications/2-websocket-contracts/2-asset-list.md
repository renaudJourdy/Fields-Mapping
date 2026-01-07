# Disclamer

These WebSocket contract documents are provided for reference and to communicate product requirements. They are not prescriptive implementation specs. Engineering teams are responsible for determining the correct backend mapping, payload structure, and transport behavior based on system constraints and architecture. Any production WebSocket contracts must be validated, documented, and maintained by the responsible engineering owners.

---

# Overview

This WebSocket stream provides real-time updates for the Asset List panel. It delivers asset metadata and key telemetry/status fields required to render list cards, grouping headers, and status states (including temperatures for cold storage assets). The stream is windowed for performance: the client subscribes to the visible list window plus a small buffer, while the server still returns global counts for a seamless UX.

---

# Stream Information

- **Stream Name:** `live.assets.list`
- **Version:** `v1`
- **Purpose:** Real-time asset list updates for list panel views
- **Frontend Use:** Asset list panel display, grouping, search, and selection synchronization

---

# Authentication

- **Method:** Bearer token (same as app API authentication)
- **Channel:** Single WebSocket connection per app session
- **Rejection:** Connection rejected if token invalid/expired

---

# Subscription

**Client -> Server:**

```json
{
  "action": "subscribe",
  "stream": "live.assets.list",
  "version": "v1",
  "params": {
    "grouping_mode": "group",
    "filters": {
      "search": null
    },
    "sort": {
      "field": "name",
      "direction": "asc"
    },
    "window": {
      "offset": 0,
      "limit": 50,
      "buffer": 25
    },
    "rate_limit_hz": 2
  }
}
```

**Grouping Mode:**

- `group`: Grouped by asset group (accordion sections)
- `type`: Grouped by asset type
- `geofence`: Grouped by geofence containment (dynamic, based on live location)
- `status`: Grouped by status families/state

**Filters:**

- `search`: string or null (matches asset metadata, driver, and geofence names)

**Sort:**

- `field`: `name` | `status` | `last_updated_at` (extendable)
- `direction`: `asc` | `desc`

**Sort Semantics:**

- `status` sorts by `status.top_status.code` (backend-defined ordering)

**Windowing:**

- `offset`/`limit`: visible slice of the list
- `buffer`: additional rows before/after the visible slice to keep scroll smooth
- Server MUST send updates only for items within `(offset - buffer)` to `(offset + limit + buffer)`
- Server MUST still include global counts for groups and total assets

**Server -> Client (Response):**

```json
{
  "type": "subscribed",
  "subscription_id": "live.assets.list",
  "stream": "live.assets.list",
  "version": "v1",
  "at": "2025-10-23T14:00:00Z",
  "params_echo": {
    "grouping_mode": "group",
    "filters": {
      "search": null
    },
    "sort": {
      "field": "name",
      "direction": "asc"
    },
    "window": {
      "offset": 0,
      "limit": 50,
      "buffer": 25
    },
    "rate_limit_hz": 2
  }
}
```

**subscription_id Guidance:**

- Treat `subscription_id` as an opaque identifier. Use the value provided by the server for subsequent updates.
- A single connection may support multiple subscriptions in the future; do not assume `subscription_id` equals the stream name.

---

# Message Types

## Snapshot

Initial full state sent after subscription. Contains the list window (plus buffer) for the current grouping, filters, and sort. Also returns global counts to keep the UI stable.

**Structure:**

```json
{
  "type": "snapshot",
  "subscription_id": "live.assets.list",
  "seq": 1,
  "at": "2025-10-23T14:00:01Z",
  "data": {
    "total_assets": 201,
    "grouping_mode": "group",
    "sort": {
      "field": "name",
      "direction": "asc"
    },
    "window": {
      "offset": 0,
      "limit": 50,
      "buffer": 25
    },
    "counts": {
      "groups": [
        { "group_id": 10, "group_name": "ALFA", "count": 6 },
        { "group_id": 11, "group_name": "BRAVO", "count": 4 }
      ]
    },
    "groups": [
      {
        "group_id": 10,
        "group_name": "ALFA",
        "count": 6,
        "assets": [
          {
            "asset_id": 1001,
            "name": "CHAMBRE FROIDE/BRAVO",
            "asset_type": "site",
            "asset_subtype": "cold_storage",
            "last_updated_at": "2025-10-23T13:59:50Z",
            "status": {
              "top_status": {
                "family": "transit",
                "code": "in_transit",
                "last_changed_at": "2025-10-23T13:45:00Z"
              },
              "statuses": {
                "connectivity": {
                  "code": "online",
                  "compatible": true,
                  "last_changed_at": "2025-10-23T12:00:00Z"
                },
                "immobilization": {
                  "code": null,
                  "compatible": false,
                  "last_changed_at": null
                },
                "engine": {
                  "code": null,
                  "compatible": false,
                  "last_changed_at": null
                },
                "transit": {
                  "code": "in_transit",
                  "compatible": true,
                  "last_changed_at": "2025-10-23T13:40:00Z"
                }
              }
            },
            "motion": {
              "speed": { "value": 12, "unit": "km/h" }
            },
            "sensors": {
              "environment": [
                {
                  "id": "sensor_1",
                  "name": "CHAMBRE FROIDE/BRAVO",
                  "temperature": { "value": 1.6, "unit": "C" },
                  "humidity": null,
                  "battery": null,
                  "last_updated_at": "2025-10-23T13:59:50Z"
                }
              ]
            },
            "geofences": [
              { "id": "gf_1", "name": "Warehouse A" }
            ]
          }
        ]
      }
    ]
  }
}
```

## Delta

Incremental updates sent after snapshot. Contains only changed assets and/or group counts that fall within the current window (plus buffer). Deltas are partial and may omit unchanged fields.

**Structure:**

```json
{
  "type": "delta",
  "subscription_id": "live.assets.list",
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
          "transit": { "code": "parked" }
        }
      },
      "motion": {
        "speed": { "value": 0, "unit": "km/h" }
      }
    },
    {
      "kind": "group",
      "group_id": 10,
      "count": 7
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

Client updates grouping, filters, sort, or window. Server responds with a new snapshot for the new window, then deltas.

**Client -> Server:**

```json
{
  "action": "update",
  "subscription_id": "live.assets.list",
  "params": {
    "grouping_mode": "status",
    "filters": {
      "search": "iphone"
    },
    "sort": {
      "field": "status",
      "direction": "desc"
    },
    "window": {
      "offset": 0,
      "limit": 50,
      "buffer": 25
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
  "subscription_id": "live.assets.list",
  "code": "invalid_params",
  "message": "Invalid grouping_mode",
  "at": "2025-10-23T14:02:00Z"
}
```

**Resync Required:**

```json
{
  "type": "resync_required",
  "subscription_id": "live.assets.list",
  "reason": "sequence_gap",
  "last_valid_seq": 100,
  "at": "2025-10-23T14:02:00Z"
}
```

Client should re-subscribe when receiving `resync_required`.

---

# Field References

This stream includes Fleeti telemetry fields grouped by category, using exact field paths from the Fleeti Fields Database.

[Untitled](https://www.notion.so/2dc3e766c90180b9b23ec8c111aa4f81?pvs=21)

### Metadata Category (root level)

- `last_updated_at` (datetime) - Timestamp of when the telemetry record was originally created

### Status Category (grouped under `status` object)

- `status.top_status.family` (string)
- `status.top_status.code` (string)
- `status.top_status.last_changed_at` (datetime)
- `status.statuses.connectivity.code` (string)
- `status.statuses.connectivity.compatible` (boolean)
- `status.statuses.connectivity.last_changed_at` (datetime)
- `status.statuses.immobilization.code` (string, nullable)
- `status.statuses.immobilization.compatible` (boolean)
- `status.statuses.immobilization.last_changed_at` (datetime)
- `status.statuses.engine.code` (string, nullable)
- `status.statuses.engine.compatible` (boolean)
- `status.statuses.engine.last_changed_at` (datetime)
- `status.statuses.transit.code` (string, nullable)
- `status.statuses.transit.compatible` (boolean)
- `status.statuses.transit.last_changed_at` (datetime)

### Motion Category (grouped under `motion` object)

- `motion.speed.value` (number, km/h, nullable)
- Speed unit is provided by backend in `motion.speed.unit` (e.g., `km/h`).

### Geofence Category

- `geofences[]` (array) - Current geofence containment (dynamic, based on live location; used for grouping)

### Sensors Category

- `sensors.environment[]` (array) - Used to display temperature values for cold storage assets
    - Derived via `derive_sensors_environment` (see computation approach): groups temperature/humidity/battery by accessory sensor
    - Prioritized mapping across raw `avl_io_*` and processed fields with correspondence matrix
    - Unit handling: temperature/humidity may be scaled (divide by 10 for raw values except LLS cases)
    - Validation: excludes error codes/out-of-range values (e.g., temperature -128, humidity 65535/65534/65533)

## Asset Metadata Fields (from Asset Service)

- `asset_id` (integer)
- `name` (string)
- `asset_type` (string)
- `asset_subtype` (string)
- `group_id` (integer)
- `group_name` (string)