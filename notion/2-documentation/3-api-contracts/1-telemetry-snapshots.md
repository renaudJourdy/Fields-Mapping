# Overview

This API returns the latest telemetry snapshot per asset. It mirrors the WebSocket snapshot payloads, but is delivered over REST for initial page loads, offline access, and batch retrieval.

Two visibility tiers are supported:

- Customer (redacted field set)
- Admin/Super Admin (full field set)

---

# Endpoints

## Snapshot List (Customer Scope)

`GET /api/v1/telemetry/snapshots`

Returns the latest telemetry snapshot for each asset visible to the customer.

### Query Parameters

- `page_limit` (int, default 50, max 200)
- `page_offset` (int, default 0)
- `sort` (string, default `last_updated_at`)
- `direction` (string, `asc` | `desc`, default `desc`)
- `filters.search` (string, optional; name/driver/geofence search)
- `filters.group_id` (int, optional)
- `filters.status` (string, optional; status family or code)
- `filters.asset_type` (string, optional)
- `filters.geofence_id` (string, optional; dynamic containment)

### Response (200)

```json
{
  "meta": {
    "page_limit": 50,
    "page_offset": 0,
    "total": 201,
    "sort": "last_updated_at",
    "direction": "desc"
  },
  "data": [
    {
      "asset": {
        "id": 1001,
        "name": "AA 772 FP AVA FLEG",
        "type": "vehicle",
        "subtype": "pickup",
        "group_id": 10,
        "group_name": "ALFA"
      },
      "last_updated_at": "2025-10-23T13:59:50Z",
      "location": {
        "latitude": 48.8566,
        "longitude": 2.3522,
        "heading": 270,
        "cardinal_direction": "W",
        "last_changed_at": "2025-10-23T13:58:00Z"
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
      "motion": {
        "speed": { "value": 42, "unit": "km/h" },
        "is_moving": {
          "value": true,
          "last_changed_at": "2025-10-23T13:40:00Z"
        },
        "last_updated_at": "2025-10-23T13:59:50Z"
      },
      "power": {
        "ignition": { "value": true },
        "ev": { "remaining_range": { "value": 48, "unit": "km" } }
      },
      "sensors": {
        "environment": [
          {
            "id": "sensor_1",
            "name": "Frigo_A",
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
            "state": "open",
            "last_updated_at": "2025-10-23T13:59:50Z",
            "last_changed_at": "2025-10-23T13:58:30Z"
          }
        ]
      },
      "driver": {
        "name": "Cheikh Fall",
        "key": "A1B2C3D4",
        "last_updated_at": "2025-10-23T13:58:30Z"
      },
      "diagnostics": {
        "health": {
          "dtc": {
            "count": 6,
            "status": true,
            "codes": ["P0204", "P0089", "P0405", "P0122", "P0183", "P0073"]
          }
        }
      },
      "fuel": {
        "tank_level": {
          "value": 82,
          "unit": "%",
          "last_updated_at": "2025-10-23T13:59:50Z"
        },
        "consumption": {
          "cumulative": {
            "value": 3400.5,
            "unit": "liters",
            "last_updated_at": "2025-10-23T13:59:50Z"
          }
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
          "mileage":{
            "value": 23.5,
            "unit": "km",
          },
          "waypoints": [
            { "latitude": 48.8566, "longitude": 2.3522 },
            { "latitude": 48.8580, "longitude": 2.3500 }
          ]
        }
      },
      "geofences": [
        { "id": "gf_1", "name": "Warehouse A" }
      ]
    }
  ]
}
```

---

## Admin Snapshot List

`GET /api/v1/admin/telemetry/snapshots`

Returns the latest telemetry snapshot for each asset, including admin-only fields.

### Query Parameters

Same as customer endpoint.

### Response (200)

Same shape as the customer response, plus admin-only fields.

```json
{
  "meta": {
    "page_limit": 50,
    "page_offset": 0,
    "total": 201,
    "sort": "last_updated_at",
    "direction": "desc"
  },
  "data": [
    {
      "asset": {
        "id": 1001,
        "name": "AA 772 FP AVA FLEG",
        "type": "vehicle",
        "subtype": "pickup",
        "group_id": 10,
        "group_name": "ALFA"
      },
      "last_updated_at": "2025-10-23T13:59:50Z",
      "location": {
        "latitude": 48.8566,
        "longitude": 2.3522,
        "heading": 270,
        "cardinal_direction": "W",
        "last_changed_at": "2025-10-23T13:58:00Z",
        "precision": {
          "fix_quality": 1,
          "hdop": 0.8,
          "pdop": 1.2,
          "satellites": 12
        }
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
      "motion": {
        "speed": { "value": 42, "unit": "km/h" },
        "is_moving": {
          "value": true,
          "last_changed_at": "2025-10-23T13:40:00Z"
        },
        "last_updated_at": "2025-10-23T13:59:50Z"
      },
      "power": {
        "ignition": { "value": true },
        "ev": { "remaining_range": { "value": 48, "unit": "km" } }
      },
      "sensors": {
        "environment": [
          {
            "id": "sensor_1",
            "name": "Frigo_A",
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
            "state": 1,
            "last_updated_at": "2025-10-23T13:59:50Z",
            "last_changed_at": "2025-10-23T13:58:30Z"
          }
        ]
      },
      "driver": {
        "name": "Cheikh Fall",
        "key": "A1B2C3D4",
        "last_updated_at": "2025-10-23T13:58:30Z"
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
          "unit": "%",
          "last_updated_at": "2025-10-23T13:59:50Z"
        },
        "consumption": {
          "cumulative": {
            "value": 3400.5,
            "unit": "liters",
            "last_updated_at": "2025-10-23T13:59:50Z"
          }
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
          "mileage":{
            "value": 23.5,
            "unit": "km",
          },
          "waypoints": [
            { "latitude": 48.8566, "longitude": 2.3522 },
            { "latitude": 48.8580, "longitude": 2.3500 }
          ]
        }
      },
      "io": {
        "inputs": {
          "individual": {
            "input_1": true,
            "input_2": false,
            "input_3": null,
            "input_4": null
          }
        },
        "outputs": {
          "individual": {
            "output_1": false,
            "output_2": null,
            "output_3": null
          }
        }
      },
      "geofences": [
        { "id": "gf_1", "name": "Warehouse A" }
      ]
    }
  ]
}
```

---

# Field Set

Snapshots use Fleeti field paths from the Fleeti Fields Database. The response payload is aligned with the WebSocket snapshot for:

- `live.assets.list` (list-ready subset)
- `live.asset.details` (full telemetry, admin only)

Customer snapshots are a redacted view of the admin snapshot. Admin-only fields include the I/O inputs/outputs and location precision fields shown above.

---

# Notes

- Pagination is offset-based for simplicity in list views.
- For large fleets, combine pagination with server-side filters.
- Units like `motion.speed.unit` are provided by backend.
- `geocoded_address` is computed on demand
- When new Fleeti fields or mapping fields are added, developers must keep both customer/admin snapshot responses updated to match the latest Fleeti Fields Database.