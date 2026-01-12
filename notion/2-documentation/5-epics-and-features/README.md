# Epic 1 - Provider Ingestion & Data Forwarding

## F1.1 - Navixy Data Forwarding Integration

- Connect to Navixy Data Forwarding endpoint
- Authenticate and establish connection per customer
- Receive raw telemetry packets
- Validate packet format
- Parse packet data
- Store raw packets in cold storage
- Forward parsed data to transformation pipeline

## F1.2 - Provider-Agnostic Architecture

**Architectural Requirement**

- Design architecture to support multiple providers with different technologies
- Support different ingestion methods (data forwarding, API polling, webhooks)
- Implement provider abstraction layer
- Each provider can have its own configuration file and mapping
- Adding new provider should not affect existing providers
- Ensure provider isolation and independence

**Note:** Architecture readiness, not implementing multiple providers yet

## F1.3 - Customer Management for Data Forwarding

- Manually add single customer to data forwarding
- Manually remove single customer from data forwarding
- Bulk add multiple customers to data forwarding
- Bulk remove multiple customers from data forwarding
- Suspend data forwarding per customer
- Resume data forwarding per customer
- Create documentation - How to connect to Navixy for specific customer

## F1.4 - Data Forwarding Health Monitoring

- Monitor connection status per customer
- Detect when data forwarding stops (partial failure)
- Detect when data forwarding stops (total failure)
- Alert system for partial failures
- Alert system for total failures
- Track connection health metrics

## F1.5 - Data Recovery System

- Detect gap in received data
- Manual recovery trigger for lost packets via Navixy API
- Fetch missing data from Navixy API
- Rebuild raw packet logs from API data
- Ingest rebuilt packets through normal workflow
- Handle recovery workflow decision (rebuild raw packet logs or direct API to database)
- Validate recovered data integrity

## F1.6 - Auto-sync with Customer System

- Automatic data forwarding setup when new customer added in Fleeti Admin
- Synchronization with customer-based system
- Remove data forwarding when customer removed
- Handle customer status changes (active/suspended)

---

# Epic 2 - Transformation Pipeline

## F2.1 - YAML Configuration Execution

- Load provider-specific YAML mapping files
- Execute YAML configuration for raw packets
- Process direct field mappings
- Process prioritized field mappings (priority-based selection)
- Process calculated field mappings (formula-based computation)
- Process transformed field mappings (combine with static metadata)
- Process I/O mapped fields (map raw I/O signals to semantic fields)
- Transform raw packets to Fleeti format
- Validate transformed data structure

## F2.2 - Hierarchical Configuration Support

**Architecture**

- Design architecture to support customer-level configuration overrides
- Design architecture to support asset group-level configuration overrides
- Design architecture to support single asset-level configuration overrides
- Implement configuration hierarchy resolution (asset > group > customer > provider)
- Default to provider-level configuration
- Enable future overrides at customer/group/asset levels

---

# Epic 3 - Status Computation

## F3.1 - Status Families Computation

- Compute Connectivity status family (online/offline)
- Compute Transit status family (in_transit/parked)
- Compute Engine status family (running/standby)
- Compute Immobilization status family (free/immobilized/immobilizing/releasing)
- Compute top_status using priority hierarchy (Connectivity > Immobilization > Engine > Movement > Online)
- Backend-driven status consistency (no frontend computation)
- Required for - Mobile app marker rendering, WebSocket streams

---

# Epic 4 - Storage Strategy

## F4.1 - Multi-Tier Storage Implementation

- Implement hot storage for live map markers (< 100ms latency requirement)
- Implement warm storage for asset list/details (< 500ms latency requirement)
- Implement cold storage for raw packets and historical data
- Store transformed Fleeti telemetry in appropriate tier based on access pattern
- Implement storage tier selection logic
- Optimize hot storage for real-time queries
- Optimize warm storage for list/details queries

## F4.2 - Storage Retention Policy

- Implement 1 month retention in hot/warm storage
- Automatically move older data to cold storage
- Implement data migration process (hot/warm → cold)
- Schedule automatic data movement
- **Investigation Required:** Cost/performance analysis (1 month vs 1 year in hot/warm)

**Investigation Items:**

- Cost comparison - 1 month vs 1 year in hot/warm storage
- Performance metrics - Cold storage query latency for 1 month of history
- Hot vs Warm - Performance and cost differences (should we only have hot storage?)

---

# Epic 5 - Troubleshooting & Investigation

## F5.1 - Mapping Investigation Tool

- Rebuild mapping logic for specific time period
- Show which provider fields were selected (e.g., CAN speed vs OBD speed)
- Display calculation parameters for calculated fields
- Investigate mapping decisions based on raw records
- Investigate mapping decisions based on configuration files
- Visualize field selection process
- Export investigation results

## F5.2 - Mapping Audit Trail

**Optional**

- Store mapping decisions in cold storage for 1 year
- Record plaintext correspondence - value, source field, calculation parameters
- Enable audit trail querying
- Implement audit trail retention policy

---

# Epic 6 - Data Consumption

## F6.1 - WebSocket Stream - `live.map.markers`

- Implement WebSocket subscription handler for `live.map.markers`
- Handle viewport-based filtering
- Generate marker snapshots (initial state)
- Generate marker deltas (incremental updates)
- Implement clustering logic (server-side)
- Handle subscription acknowledgements
- Implement error handling and reconnection
- Implement security/authentication
- Support real-time position updates
- Support real-time heading updates
- Support real-time status updates

## F6.2 - WebSocket Stream - `live.assets.list`

- Implement WebSocket subscription handler for `live.assets.list`
- Support grouping modes (group/type/geofence)
- Generate asset list snapshots
- Generate asset list deltas
- Support pagination (window-based)
- Support search filtering
- Handle real-time status updates
- Handle real-time metric updates

## F6.3 - WebSocket Stream - `live.asset.details`

- Implement WebSocket subscription handler for `live.asset.details`
- Support asset-specific subscription (by asset_id)
- Generate asset details snapshots
- Generate asset details deltas
- Support real-time telemetry updates (status, location, sensors, counters, KPIs)
- Support immobilizer state updates
- Support ongoing trip visualization
- Handle subscription switching (change asset)

## F6.4 - WebSocket Stream - `live.map.geofences`

- Implement WebSocket subscription handler for `live.map.geofences`
- Handle viewport-based geofence filtering
- Generate geofence snapshots
- Generate geofence deltas
- Implement geofence clustering logic
- Support real-time geofence updates
- Handle geofence geometry rendering

## F6.5 - REST API - Telemetry Snapshots

- Implement `/api/v1/telemetry/snapshots` endpoint (customer scope)
- Implement `/api/v1/admin/telemetry/snapshots` endpoint (admin scope)
- Query hot/warm storage for snapshots
- Aggregate with Asset Service data
- Enforce customer vs Admin visibility (troubleshoot fields hidden from customers)
- Support filtering and pagination
- Optimize query performance

## F6.6 - REST API - Asset Telemetry History

- Implement `/api/v1/telemetry/assets/{asset_id}/history` endpoint (customer scope)
- Implement `/api/v1/admin/telemetry/assets/{asset_id}/history` endpoint (admin scope)
- Query historical telemetry (up to 1 month)
- Combine hot/warm/cold storage queries
- Enforce customer vs Admin visibility
- Support time range filtering (start_at, end_at)
- Support pagination
- Optimize cross-tier query performance

## F6.7 - REST API - Trip History

- Implement trip history overview endpoint
- Implement trip history details endpoint
- Query historical trip data (up to 1 month)
- Combine hot/warm/cold storage queries
- Support trip filtering and pagination
- Aggregate trip waypoints and metrics

## F6.8 - REST API - Geofences

- Implement `/api/v1/geofences` endpoint (list)
- Implement `/api/v1/geofences/{geofence_id}` endpoint (details)
- Support pagination (offset, limit)
- Support search (name, keywords)
- Support sorting (name_asc, name_desc, type)
- Return geofence geometry and metadata
- Support view-only access (no CRUD operations)

## F6.9 - Advanced WebSocket Filters

- Implement advanced filtering - group_ids
- Implement advanced filtering - customer_reference
- Implement advanced filtering - country
- Implement advanced filtering - focus mode
- Implement advanced filtering - top_status
- Enhance viewport and filter capabilities
- Support filter combinations

---

# Epic 7 - Provider Priority Configuration

## F7.1 - Provider Priority Rules

- Implement field-level provider selection for multi-gateway assets
- Support hierarchical configuration (default/customer/group/asset)
- Implement same-provider selection strategy (most recent)
- Apply provider priority rules to all WebSocket streams
- Apply provider priority rules to all REST APIs
- Handle provider priority resolution logic
- Support provider priority configuration management
