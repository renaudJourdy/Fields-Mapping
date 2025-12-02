### Fields where `last_changed_at` is genuinely valuable for customers

#### A. Status / context

| **Fleeti Field** | **Why `last_changed_at` is great for customers** | **Example features** |
|------------------|--------------------------------------------------|----------------------|
| `status.top_status` | Shows since when the *current overall situation* (e.g. in_transit, parked, immobilized) has been true. Helps understand duration of the current “state of the asset”. | “Asset has been in transit since 10:32”; sort fleet by longest time in current state. |
| `status.statuses[].family` (each entry: connectivity, immobilization, engine, transit) | Per-family duration is very useful (how long offline, immobilized, engine running, etc.). More precise than only top status. | “Offline for 2h”; “Immobilized since yesterday 18:10”; SLA/alert conditions like “engine_running > 4h”. |

#### B. Motion / engine / power

| **Fleeti Field** | **Why `last_changed_at` is great for customers** | **Example features** |
|------------------|--------------------------------------------------|----------------------|
| `power.ignition` | Directly answers “since when is ignition ON/OFF?”. Combines well with trips, idling, night-driving alerts. | “Ignition on since 07:05”; detect abnormal long ignition on at night. |
| `diagnostics.engine.running` | More precise “engine actually running” (vs key in ACC). Duration is important for fuel use, wear, and misuse detection. | “Engine running for 45 min while vehicle is stationary”; maintenance reports based on true running time. |
| `motion.is_moving` | Shows when the vehicle last started/stopped moving. Very intuitive for customers (stopped since X). | “Vehicle stopped since 13:22”; highlight assets that haven’t moved all day. |

#### C. Location

| **Fleeti Field** | **Why `last_changed_at` is great for customers** | **Example features** |
|------------------|--------------------------------------------------|----------------------|
| `location` (group-level `location.last_changed_at`) | Tells how long the asset has been at the *current spot* (ignoring GPS jitter). Critical for dwell-time, loading/unloading, unauthorized stops. | “Parked at this location since 09:10”; dwell time KPIs at customer sites; alerts when vehicle stays too long in a risky area. |

#### D. Security / immobilizer

| **Fleeti Field** | **Why `last_changed_at` is great for customers** | **Example features** |
|------------------|--------------------------------------------------|----------------------|
| `diagnostics.security.immobilizer.engine_lock_active` | Directly answers “since when is the vehicle locked?”. Gives confidence that immobilization took effect and for how long it’s been in place. | Show immobilization timeline; audits after theft attempts (“locked since 22:03 last night”). |
| `diagnostics.security.immobilizer.request_lock_engine` | Useful for tracking when the *command* was requested vs when it actually took effect (combined with output state). Great for operations and support. | Show last immobilization / release command times in history; debug failed commands (command requested but state never changed). |

#### E. Driver / privacy

| **Fleeti Field** | **Why `last_changed_at` is great for customers** | **Example features** |
|------------------|--------------------------------------------------|----------------------|
| `driver.id` | Answers “since when is this driver on this vehicle?”. Essential for responsibility, shift changes, and incident investigations. | Timeline of driver-vehicle association; determine which driver was in charge at time of event. |
| `driver.privacy_mode` | Shows how long private mode has been active (vs business). Important for compliance, HR, and explaining gaps in tracking. | “Private mode active since 18:30”; reports that separate private time vs business time with clear start times. |

---

### Short opinion on `last_updated_at` (for context)

- **Root-level `last_updated_at` (single timestamp)** is very useful for:
  - Showing freshness of telemetry (“Last contact: 2 min ago”).
  - Connectivity/health monitoring.
- **Per-field or per-section `last_updated_at`** is much less useful than `last_changed_at` for customers, and usually not worth the extra complexity.