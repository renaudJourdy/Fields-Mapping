# Overview

This API returns telemetry history for a single asset over a time range. It mirrors the WebSocket payloads and returns the same Fleeti fields, but across time-series records.

Two visibility tiers are supported:

- Customer (redacted field set)
- Admin/Super Admin (full field set)

---

# Endpoints

## Asset History (Customer Scope)

`GET /api/v1/telemetry/assets/{asset_id}/history`

Returns telemetry history for a single asset, within the requested time range.

### Query Parameters

- `start_at` (ISO8601, required)
- `end_at` (ISO8601, required)
- `page_limit` (int, default 500, max 5000)
- `page_cursor` (string, optional)
- `order` (string, `asc` | `desc`, default `asc`)
- `include` (string, optional; comma-separated field groups, defaults to all customer-visible fields)

### Response (200)

```json
{
  "meta": {
    "asset_id": 1001,
    "start_at": "2025-10-23T00:00:00Z",
    "end_at": "2025-10-23T23:59:59Z",
    "page_limit": 500,
    "page_cursor": null,
    "next_cursor": "eyJ0cyI6IjIwMjUtMTAtMjNUMTI6MDA6MDBaIn0=",
    "order": "asc"
  },
  "data": [
    {
      "at": "2025-10-23T13:59:50Z",
      "last_updated_at": "2025-10-23T13:59:50Z",
      "location": {
        "latitude": 48.8566,
        "longitude": 2.3522,
        "altitude": 18.2,
        "heading": 270,
        "cardinal_direction": "W",
        "last_changed_at": "2025-10-23T13:58:00Z"
      },
      "status": {
        "top_status": {
          "family": "transit",
          "code": "in_transit"
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
        "ignition": {
          "value": true,
          "last_changed_at": "2025-10-23T13:40:00Z"
        },
        "ev": { "remaining_range": { "value": 48, "unit": "km" } }
      },
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
          "unit": "hours",
          "last_updated_at": "2025-10-23T13:59:50Z"
        },
        "odometer": {
          "value": 23054.4,
          "unit": "km",
          "last_updated_at": "2025-10-23T13:59:50Z"
        }
      },
      "trip": {
        "ongoing_trip": {
          "started_at": "2025-10-23T13:40:00Z",
          "mileage": { "value": 23.5, "unit": "km" },
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

## Admin Asset History

`GET /api/v1/admin/telemetry/assets/{asset_id}/history`

Returns telemetry history for a single asset, including admin-only fields.

### Query Parameters

Same as customer endpoint.

### Response (200)

Same shape as the customer response, plus admin-only fields.

```json
{
  "meta": {
    "asset_id": 1001,
    "start_at": "2025-10-23T00:00:00Z",
    "end_at": "2025-10-23T23:59:59Z",
    "page_limit": 500,
    "page_cursor": null,
    "next_cursor": "eyJ0cyI6IjIwMjUtMTAtMjNUMTI6MDA6MDBaIn0=",
    "order": "asc"
  },
  "data": [
    {
      "at": "2025-10-23T13:59:50Z",
      "last_updated_at": "2025-10-23T13:59:50Z",
      "location": {
        "latitude": 48.8566,
        "longitude": 2.3522,
        "altitude": 18.2,
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
          "code": "in_transit"
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
        "ignition": {
          "value": true,
          "last_changed_at": "2025-10-23T13:40:00Z"
        },
        "ev": { "remaining_range": { "value": 48, "unit": "km" } }
      },
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
          "unit": "hours",
          "last_updated_at": "2025-10-23T13:59:50Z"
        },
        "odometer": {
          "value": 23054.4,
          "unit": "km",
          "last_updated_at": "2025-10-23T13:59:50Z"
        }
      },
      "trip": {
        "ongoing_trip": {
          "started_at": "2025-10-23T13:40:00Z",
          "mileage": { "value": 23.5, "unit": "km" },
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

History records use Fleeti field paths from the Fleeti Fields Database, aligned with the WebSocket snapshot payloads.

Customer history is a redacted view of the admin history. Admin-only fields include the I/O inputs/outputs and location precision fields shown above.

---

# Notes

- Cursor pagination is used for efficient time-series traversal.
- `next_cursor` is an opaque bookmark returned by the server; pass it back as `page_cursor` to continue.
- Cursors avoid costly offset scans and preserve stable ordering when many records share the same timestamp.
- Units like `motion.speed.unit` are provided by backend.
- `geocoded_address` is computed on demand
- When new Fleeti fields or mapping fields are added, developers must keep both customer/admin history responses updated to match the latest Fleeti Fields Database.