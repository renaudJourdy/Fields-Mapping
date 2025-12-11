# Telemetry Status Rules

# **Complete Compatibility Matrix Reference**

| Asset Type/Subtype | Connectivity | Transit | Engine | Immobilization |
| --- | --- | --- | --- | --- |
| Site.Undefined | yes | no | no | no |
| Site.Coldroom | yes | no | no | no |
| Phone | yes | yes | no | no |
| Equipment.Undefined | yes | yes | no | yes |
| Equipment.FuelTank | yes | no | no | no |
| Equipment.ElectricGenerator | yes | no | yes | yes |
| Vehicle.Undefined | yes | yes | no | yes |
| Vehicle.Car | yes | yes | no | yes |
| Vehicle.Boat | yes | yes | no | yes |
| Vehicle.Truck | yes | yes | no | yes |
| Vehicle.Heavy | yes | yes | no | yes |
| Vehicle.Agricultural | yes | yes | yes | yes |
| Vehicle.Minivan | yes | yes | no | yes |
| Vehicle.Van | yes | yes | no | yes |
| Vehicle.Pickup | yes | yes | no | yes |
| Vehicle.Minibus | yes | yes | no | yes |
| Vehicle.Motorbike | yes | yes | no | yes |
| Vehicle.Machine | yes | yes | yes | yes |
| Vehicle.Genset | yes | yes | no | no |
| Vehicle.Scooter | yes | yes | no | yes |
| Vehicle.ColdRoom | yes | yes | no | yes |
| Vehicle.Bus | yes | yes | no | yes |
| Vehicle.Tricycle | yes | yes | no | yes |
| Vehicle.JetSki | yes | yes | no | yes |
| Vehicle.Buggy | yes | yes | no | yes |
| Vehicle.HandlingCart | yes | yes | no | yes |

This matrix defines which status families apply to each asset type/subtype. Backend must check compatibility before evaluating each status family.

---

# **1. Connectivity Status - Trigger Conditions**

**How to determine online vs offline:**

**For Vehicles, Equipment, and Phones:**

- online: `last_update_at` < 24 hours from current time
- offline: `last_update_at` ≥ 24 hours from current time

**For Sites (General/Undefined subtype):**

- online: `last_update_at` < 24 hours from current time
- offline: `last_update_at` ≥ 24 hours from current time

**For Cold Room Sites (subtype):**

- online: `last_update_at` < 1 hour from current time
- offline: `last_update_at` ≥ 1 hour from current time

**Telemetry fields required:**

- `last_update_at` - ISO8601 UTC timestamp at root level of Fleeti telemetry object, derived from msg_time telemetry field
- Source field: `msg_time` from white-label platform telemetry payload
- `last_update_at` represents the last telemetry message timestamp, not GPS location timestamp

**Note:** Connectivity is based on the root-level `last_update_at` timestamp (derived from msg_time), not GPS location updates. The `msg_time` field from the provider is mapped to the root-level last_update_at in the Fleeti telemetry object.

---

# **2. Immobilization Status - Trigger Conditions**

**How to determine `immobilized`, `free`, `immobilizing`, `releasing`:**

**Prerequisites:**

- Asset must have asset_type ∈ {Vehicle (10), Equipment (20)}
- Asset must have immobilizer accessory installed
- Asset capabilities/metadata must indicate `immobilizer_capable` = true
- Installation metadata must specify which digital output is wired to the immobilizer (e.g., `immobilizer.output_number` = 1)

**Status determination:**

- **immobilized**:
    - Immobilizer accessory present (`immobilizer_capable` = true)
    - Installation metadata specifies immobilizer output number (e.g., output 1)
    - Digital output state = locked (value = 1)
    - Map from telemetry: Check the specified output number, e.g., `io.outputs[1]` = 1 OR `io.outputs.immobilizer` = 1 (when mapped based on installation metadata)
- **free**:
    - Immobilizer accessory present (`immobilizer_capable` = true)
    - Installation metadata specifies immobilizer output number
    - Digital output state = unlocked (value = 0)
    - Map from telemetry: Check the specified output number, e.g., `io.outputs[1]` = 0 OR `io.outputs.immobilizer` = 0
- **immobilizing**:
    - Immobilizer accessory present
    - Immobilization command sent via REST API and backend returns success response
    - Backend immediately sets status to `immobilizing`
    - State persists until:
        - Device confirms immobilization (output changes to 1) → transitions to `immobilized`
        - Command timeout expires → transitions to error state or remains in current state
    - This is managed by backend command tracking, not directly from telemetry
- **releasing**:
    - Immobilizer accessory present
    - Release/unlock command sent via REST API and backend returns success response
    - Backend immediately sets status to `releasing`
- State persists until:
    - Device confirms release (output changes to 0) → transitions to `free`
    - Command timeout expires → error state or remains in current state
- This is managed by backend command tracking, not directly from telemetry

**Required telemetry fields:**

- `io.outputs[N]` (integer: 0/1) - Digital output states, where N is the output number specified in installation metadata
- OR `io.outputs.immobilizer` (if backend maps based on installation metadata)

**Required asset metadata/configuration:**

- `immobilizer_capable` (boolean) - Indicates immobilizer accessory is installed
- `immobilizer.output_number` (integer) - Specifies which digital output is wired to immobilizer (e.g., 1, 2, etc.)
- This metadata is part of asset installation/configuration, not telemetry stream

**Important:** Backend must use the installation metadata to determine which output number corresponds to the immobilizer before interpreting output states. The output number is not universal—it varies per installation.

---

# **3. Engine Status - Trigger Conditions**

**How to determine running vs standby:**

**Prerequisites:**

- Asset must be Engine Status compatible:
    - Equipment (all subtypes): Yes
    - Vehicles: Only specific subtypes support engine status (compatibility matrix)
    - Sites: No (removed from engine status)
    - Phones: No

**Compatibility matrix (required):**

| Asset Type | Subtype | Engine Status Supported | Notes |
| --- | --- | --- | --- |
| Vehicle | Custom | Conditional | Specific vehicle subtypes only (matrix above) |
| Equipment | All | Yes | All equipment subtypes support engine status |
| Site | All | No | Sites do not have engine status |
| Phone/Tablet | All | No | Phones do not have engine status |

**Status determination for compatible assets:**

- **running**:
    - Asset is engine status compatible
    - Ignition state = ON
    - Map from telemetry:
        - Check installation metadata to determine which digital input is wired to ignition (e.g., ignition.input_number = 1)
        - Read the specified input: `io.inputs[1]` = 1 OR `io.inputs.ignition` = 1
        - Fallback: If installation metadata is missing, use input 1 as default (`io.inputs[1]`)
        - OR use CAN ignition data if available: `can_ignition_state` = true
        - OR use hardware/virtual ignition: `vehicle.ignition.hardware` = true OR `vehicle.ignition.virtual` = true
- **standby**:
    - Asset is engine status compatible
    - Ignition state = OFF
    - Map from telemetry:
        - Check installation metadata for ignition input number (e.g., input 1)
        - Read the specified input: `io.inputs[1]` = 0 OR `io.inputs.ignitio`n = 0
        - Fallback: If installation metadata is missing, use input 1 as default
        - OR use CAN ignition: `can_ignition_state` = false
        - OR use hardware/virtual ignition: All ignition sources = false

**Required telemetry fields:**

- `io.inputs[N]` (integer: 0/1) - Digital input states, where N is the input number specified in installation metadata (fallback to input 1 if metadata missing)
- OR `io.inputs.ignition` (if backend maps based on installation metadata)
- OR `can_ignition_state` (boolean) - CAN bus ignition state (preferred if available)
- OR `vehicle.ignition.hardware` (boolean) - Hardware ignition state
- OR `vehicle.ignition.virtual` (boolean) - Virtual/computed ignition state

**Required asset metadata/configuration:**

- `engine_status_capable` (boolean) - Indicates asset supports engine status (based on compatibility matrix)
- `ignition.input_number` (integer, optional) - Specifies which digital input is wired to ignition (default: input 1 if not specified)

**Note:** If ignition data is unavailable or asset is not engine-status-compatible, Engine family status is omitted from `statuses[]`.

---

# 4. Transit Status - Trigger Conditions

### Compatibility Matrix

Transit Status is supported for:

- `Phone` (all subtypes)
- `Equipment.Undefined` (subtype)
- All Vehicle subtypes (except those explicitly excluded)

Transit Status is not supported for:

- `Site.Undefined`
- `Site.Coldroom`
- `Equipment.FuelTank`
- `Equipment.ElectricGenerator`

### Approach: State Machine with Ignition Triggers

Transit Status uses a state machine. Ignition state changes trigger immediate transitions; movement/speed conditions require duration checks.

### State Transitions

### Immediate Transitions (Ignition-Based)

- Ignition OFF → ON: Status → `in_transit` (immediate)
- Ignition ON → OFF: Status → `parked` (immediate)

### Duration-Based Transitions

- IN_TRANSIT → PARKED: (`movement_status = false` OR `speed = 0 km/h`) for 3 minutes → `parked`
- PARKED → IN_TRANSIT: (`movement_status = true` OR `speed > 0.5 km/h`) → `in_transit` (immediate)

### Initial State (No Previous Status)

- If `ignition_state = true` → `in_transit`
- If `movement_status = true` OR `speed > 0.5 km/h` → `in_transit`
- If (`movement_status = false` AND `speed = 0`) for 3 minutes → `parked`
- Default → `in_transit` (conservative)

### Required Telemetry Fields

| Field | Type | Source | Notes |
| --- | --- | --- | --- |
| `ignition_state` | boolean | `io.inputs[ignition.input_number]` OR `can_ignition_state` | Only reliable when `true`; triggers immediate transitions |
| `movement_status` | boolean | Provider movement detection | Used for duration-based transitions |
| `speed` | number (km/h) | GPS speed OR CAN speed | Threshold: `> 0.5 km/h` for movement |

### Thresholds

- Speed threshold: `0.5 km/h` (filters GPS drift)
- Parked detection duration: `3 minutes` (180 seconds)

### Summary Table

| Current Status | Condition | Duration Required | New Status | Notes |
| --- | --- | --- | --- | --- |
| Any | Ignition OFF → ON | Immediate | `in_transit` | Ignition trigger |
| Any | Ignition ON → OFF | Immediate | `parked` | Ignition trigger |
| `in_transit` | `movement = false` OR `speed = 0` | 3 minutes | `parked` | Duration-based |
| `parked` | `movement = true` OR `speed > 0.5 km/h` | Immediate | `in_transit` | Movement detected |
| Initial | `ignition = true` | Immediate | `in_transit` | Initial state |
| Initial | `movement = true` OR `speed > 0.5 km/h` | Immediate | `in_transit` | Initial state |
| Initial | `movement = false` AND `speed = 0` | 3 minutes | `parked` | Initial state |

```bash
┌─────────────┐
│   PARKED    │
└──────┬──────┘
       │
       │ Condition: movement = true OR speed > 0.5 km/h
       │ (immediate)
       │
       ▼
┌─────────────┐
│  IN_TRANSIT │
└──────┬──────┘
       │
       │ Condition: (movement = false OR speed = 0) for 3 minutes
       │
       │
┌──────┴──────┐
│   PARKED    │
└─────────────┘

Additional immediate transitions:
- Ignition OFF → ON: → IN_TRANSIT (immediate)
- Ignition ON → OFF: → PARKED (immediate)
```

### Important Notes

1. Ignition state: Only use when `true` (ignition ON). `false` or `null` = unavailable; do not use as a negative signal.
2. State persistence: Backend must track current Transit Status to apply transition rules.
3. Missing data: If `movement_status` and `speed` are unavailable, maintain current status (no transition).
4. Future improvements: This logic is simplified for initial implementation. It may be refined based on production telemetry analysis, including subsequent record patterns, threshold tuning, or asset-type-specific rules.

### Edge Cases

- Missing data: Maintain current status if `movement_status` and `speed` unavailable
- Conflicting signals: If `movement_status = false` but `speed > 0.5 km/h`, prioritize speed (movement detected)
- Initial state: Use initial state logic if no previous status exists

If movement status data is completely missing: Transit Status family is omitted from `statuses[]` (do not set default value)