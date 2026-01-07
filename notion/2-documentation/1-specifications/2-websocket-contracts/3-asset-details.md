# Overview

This WebSocket stream provides real-time updates for a single asset details panel. It delivers comprehensive telemetry and status fields required to render KPIs, live data, sensors, trip context, and diagnostics.

---

# Stream Information

- **Stream Name:** `live.asset.details`
- **Version:** `v1`
- **Purpose:** Real-time asset details updates for asset details panel
- **Frontend Use:** Asset details panel display with live telemetry, sensors, KPIs, and status information

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
  "stream": "live.asset.details",
  "version": "v1",
  "params": {
    "asset_id": 1001,
    "rate_limit_hz": 2
  }
}
```

**Server -> Client (Response):**

```json
{
  "type": "subscribed",
  "subscription_id": "live.asset.details",
  "stream": "live.asset.details",
  "version": "v1",
  "asset_id": 1001,
  "at": "2025-10-23T14:00:00Z"
}
```

**subscription_id Guidance:**
- Treat `subscription_id` as an opaque identifier. Use the value provided by the server for subsequent updates.
- A single connection may support multiple subscriptions in the future; do not assume `subscription_id` equals the stream name.

---

# Message Types

## Snapshot

Initial full state sent after subscription. Contains all Fleeti fields listed in the export for `live.asset.details`.

**Structure:**

```json
{
  "type": "snapshot",
  "subscription_id": "live.asset.details",
  "seq": 1,
  "at": "2025-10-23T14:00:01Z",
  "data": {
    "asset": {
      "id": 1001,
      "name": "AA 772 FP AVA FLEG",
      "type": "vehicle",
      "subtype": "pickup",
      "group_id": 10,
      "group_name": "ALFA",
      "make": "Isuzu",
      "model": "D-Max",
      "license_plate": "AA 772 FP DK-10"
    },
    "last_updated_at": "2025-10-23T13:59:50Z",
    "location": {
      "latitude": 48.8566,
      "longitude": 2.3522,
      "altitude": 18.2,
      "heading": 270,
      "cardinal_direction": "W",
      "last_changed_at": "2025-10-23T13:58:00Z",
      "geocoded_address": "Route de King Fahd, Dakar, Senegal"
    },
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
    "power": {
      "ignition": {
        "value": true,
        "last_changed_at": "2025-10-23T13:40:00Z"
      },
      "ev": {
        "remaining_range": 48
      }
    },
    "motion": {
      "speed": { "value": 42, "unit": "km/h" },
      "is_moving": {
        "value": true,
        "last_changed_at": "2025-10-23T13:40:00Z"
      },
      "last_updated_at": "2025-10-23T13:59:50Z"
    },
    "geofences": [
      { "id": "gf_1", "name": "Warehouse A" }
    ],
    "sensors": {
      "environment": [
        {
          "id": "sensor_1",
          "name": "Frigo_A",
          "label": "Front Sensor",
          "position": "front",
          "temperature": { "value": 2.4, "unit": "C" },
          "humidity": { "value": 48.3, "unit": "%" },
          "battery": null,
          "last_updated_at": "2025-10-23T13:59:50Z"
        }
      ],
      "magnet": [
        {
          "id": "door_1",
          "label": "Entrance",
          "position": "front",
          "state": 1,
          "last_updated_at": "2025-10-23T13:59:50Z",
          "last_changed_at": "2025-10-23T13:58:30Z"
        }
      ]
    },
    "driver": {
      "driver_name": "Cheikh Fall",
      "driver_key": "A1B2C3D4"
    },
    "diagnostics": {
      "health": {
        "dtc": {
          "count": 5,
          "status": true,
          "codes": ["P0204", "P0089", "P0405", "P0122", "P0183", "P0073"]
        }
      }
    },
    "fuel": {
      "tank_level": {
        "value": 82,
        "unit":"%", // can be liters
        "last_updated_at": "2025-10-23T13:59:50Z"
      },
      "consumption": {
        "cumulative": {
          "value": 3400.5,
          "unit":"liters", // can be liters
          "last_updated_at": "2025-10-23T13:59:50Z"
        },
      }
    },
    "counters": {
      "engine_hours": {
        "value": 18745.7,
        "last_updated_at": "2025-10-23T13:59:50Z"
      },
      "odometer": {
        "value": 23054.4,
        "last_updated_at": "2025-10-23T13:59:50Z"
      }
    },
    "trip": {
      "ongoing_trip": {
        "started_at": "2025-10-23T13:40:00Z",
        "mileage": 23.5,
        "waypoints": [
          { "latitude": 48.8566, "longitude": 2.3522 },
          { "latitude": 48.8580, "longitude": 2.3500 }
        ]
      }
    }
  }
}
```

## Delta

Incremental updates after snapshot. Deltas are partial and may omit unchanged fields.

**Structure:**

```json
{
  "type": "delta",
  "subscription_id": "live.asset.details",
  "seq": 42,
  "at": "2025-10-23T14:01:30Z",
  "changes": [
    {
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
    }
  ]
}
```

## Update

Client changes selected asset. Server responds with a new snapshot for the new asset.

**Client -> Server:**

```json
{
  "action": "update",
  "subscription_id": "live.asset.details",
  "params": {
    "asset_id": 1002,
    "rate_limit_hz": 2
  }
}
```

## Error & Resync

**Error Message:**

```json
{
  "type": "error",
  "subscription_id": "live.asset.details",
  "code": "invalid_params",
  "message": "Invalid asset_id",
  "at": "2025-10-23T14:02:00Z"
}
```

**Resync Required:**

```json
{
  "type": "resync_required",
  "subscription_id": "live.asset.details",
  "reason": "sequence_gap",
  "last_valid_seq": 100,
  "at": "2025-10-23T14:02:00Z"
}
```

Client should re-subscribe when receiving `resync_required`.

---

# Field References

This stream includes Fleeti telemetry fields grouped by category, using exact field paths from the Fleeti Fields Database.
Field paths listed below were verified against the latest Fleeti Fields export (`Fleeti Fields (db) 1-2-26.csv`).

## Telemetry Fields (from Fleeti Telemetry System)

### Location Category (grouped under `location` object)

- `location.latitude`
- `location.longitude`
- `location.altitude`
- `location.heading`
- `location.cardinal_direction`
- `location.last_changed_at`
- `location.geocoded_address` (computed on demand; server-side only, not part of mapping config)

### Metadata Category (root level)

- `last_updated_at`

### Status Category (grouped under `status` object)

- `status.top_status.family`
- `status.top_status.code`
- `status.top_status.last_changed_at`
- `status.statuses.connectivity.code`
- `status.statuses.connectivity.compatible`
- `status.statuses.connectivity.last_changed_at`
- `status.statuses.immobilization.code`
- `status.statuses.immobilization.compatible`
- `status.statuses.immobilization.last_changed_at`
- `status.statuses.engine.code`
- `status.statuses.engine.compatible`
- `status.statuses.engine.last_changed_at`
- `status.statuses.transit.code`
- `status.statuses.transit.compatible`
- `status.statuses.transit.last_changed_at`

### Power Category (grouped under `power` object)

- `power.ignition.value`
- `power.ignition.last_changed_at`
- `power.ev.remaining_range`

### Motion Category (grouped under `motion` object)

- `motion.speed.value` (unit provided by backend in `motion.speed.unit`)
- `motion.last_updated_at`
- `motion.is_moving.value`
- `motion.is_moving.last_changed_at`

### Geofence Category

- `geofences[]` (current geofence containment)

### Sensors Category

- `sensors.environment[]`
- `sensors.magnet`

### Driver Category

- `driver.driver_name`
- `driver.driver_key`

### Diagnostics Category

- `diagnostics.health.dtc.count`
- `diagnostics.health.dtc.status`
- `diagnostics.health.dtc.codes[]`

### Fuel Category

- `fuel.tank_level.value` (unit conditional)
- `fuel.tank_level.last_updated_at`
- `fuel.consumption.cumulative`

### Counters Category

- `counters.engine_hours.value`
- `counters.engine_hours.last_updated_at`
- `counters.odometer.value`
- `counters.odometer.last_updated_at`

### Trip Category

- `trip.ongoing_trip.started_at`
- `trip.ongoing_trip.mileage`
- `trip.ongoing_trip.waypoints`

## Asset Metadata Fields (from Asset Service)

- `asset.id`
- `asset.name`
- `asset.type`
- `asset.subtype`
- `asset.group_id`
- `asset.group_name`
- `asset.make`
- `asset.model`
- `asset.registration`

---

# UI Notes (from Figma)

- Header shows asset identity, type/subtype, group, and quick actions (immobilize, overflow).
- KPIs: transit time, idle time, mileage.
- Tabs: Live data vs Trip history.
- Sections: current driver (with call action), status list, location (geofence + coordinates + geocoded address + last change), temperatures, external door state, counters, and trip visualization.

---

# Related Documentation

- **[Fleeti Fields Database](../1-databases/2-fleeti-fields/README.md)**: Field definitions
- **[Mobile App Specs](../../../docs/rag/SPECIFICATIONS_FAQ.md)**: Frontend requirements

---

**Last Updated:** 2025-02-01
**Status:** Specification Draft
