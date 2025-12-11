# Product Requirements: Telemetry Storage & Data Access

**Document Version:** 1.0  
**Date:** 2025-01-XX  
**Status:** Draft - Pending Review  
**Owner:** Product Team

---

## 1. Executive Summary

### Overview

Fleeti's telemetry system must ingest, store, and serve telemetry data from multiple providers (Navixy, OEM manufacturers, future providers) to support real-time map displays, asset detail views, customer API access, and historical analysis. The system must scale from **20,000 assets today to 100,000+ assets over 5 years**, handling **10 million messages per day today, growing to 50 million messages per day**.

### Key Product Capabilities

1. **Real-Time Map Display** - Users see live map markers that update smoothly as vehicles move, with minimal delay
2. **Asset Detail Views** - Users can view complete telemetry information when clicking on map markers
3. **Customer API Access** - Customers can programmatically access live and historical telemetry data
4. **Historical Analysis** - Users can query and visualize telemetry trends over days, weeks, or months
5. **Troubleshooting Tools** - Internal team can debug issues by accessing raw provider data and transformation history

### Critical Success Factors

- **Performance:** Map markers must update within 100ms of telemetry receipt
- **Completeness:** All telemetry data must be preserved (raw + transformed) for historical recalculation
- **Scalability:** System must handle 5x growth (20K → 100K assets) without major refactoring
- **Flexibility:** Customers must be able to access any telemetry field via API
- **Traceability:** System must maintain links from Fleeti data back to original provider data for debugging and recalculation

### Current State & Growth Projections

| Metric | Current (Year 1) | Projected (Year 5) |
|--------|------------------|-------------------|
| **Assets** | 20,000 | 100,000 |
| **Messages per asset/day** | 500 | 500 |
| **Total messages/day** | 10,000,000 | 50,000,000 |
| **Messages per second** | ~116 | ~579 |

---

## 2. User Stories & Use Cases

### 2.1 Real-Time Map Display Use Case

**User Story:**
> As a fleet manager, I want to see all my vehicles on a map with real-time location updates so I can monitor fleet activity as it happens.

**Acceptance Criteria:**
- Map markers update within 100ms of receiving new telemetry
- Map displays hundreds or thousands of assets simultaneously without performance degradation
- Each marker shows current location, status, and basic vehicle information
- Map remains responsive when many assets update at the same time
- Status changes (e.g., vehicle goes offline, engine starts) are reflected immediately

**User Experience:**
- User opens map view in Fleeti One application
- Map loads current locations for all assets in their fleet
- Markers update smoothly as vehicles move
- User can see at a glance which vehicles are moving, parked, offline, or have issues
- No noticeable delay between vehicle movement and map marker update

### 2.2 Asset Detail View Use Case

**User Story:**
> As a fleet manager, I want to click on a map marker to see detailed telemetry information about that vehicle so I can understand its current state and diagnose issues.

**Acceptance Criteria:**
- Detail view loads within 500ms of clicking marker
- Detail view shows all available telemetry fields for that asset
- Fields that aren't available are clearly indicated (not just missing)
- Detail view includes current values, historical trends, and status information
- User can see sensor readings, diagnostics, fuel levels, driving behavior, etc.

**User Experience:**
- User clicks on a map marker for "Truck-123"
- Detail panel opens showing complete telemetry information
- User can see location, speed, fuel level, engine status, sensor readings, etc.
- Some fields may show "Not available" if the asset doesn't have that sensor/equipment
- User can scroll through all available telemetry fields

### 2.3 Historical Analysis Use Case

**User Story:**
> As a fleet manager, I want to analyze telemetry trends over time so I can identify patterns, optimize operations, and generate reports.

**Acceptance Criteria:**
- User can query telemetry data for any time range (1 day to several years)
- Queries complete within acceptable time (1 day < 500ms, 1 month < 2 seconds)
- User can request specific fields or all fields
- Data can be visualized as time-series charts (speed over time, fuel consumption, etc.)
- Historical data supports recalculation when new fields are added

**User Experience:**
- User selects a vehicle and time range (e.g., "Last 7 days")
- User selects fields to analyze (e.g., speed, fuel consumption, engine hours)
- System returns time-series data for visualization
- User can export data for external analysis
- Charts load smoothly and display all requested data points

### 2.4 Customer API Integration Use Case

**User Story:**
> As a customer developer, I want to integrate Fleeti telemetry data into my own system via API so I can build custom dashboards and workflows.

**Acceptance Criteria:**
- API provides consistent Fleeti telemetry format (not provider-specific)
- API supports live data queries (current state of assets)
- API supports historical data queries (time-series data)
- API allows field selection (customer chooses which fields to retrieve)
- API responses are fast and reliable
- API documentation is clear and comprehensive

**User Experience:**
- Developer calls API endpoint to get current telemetry for an asset
- API returns standardized Fleeti telemetry format
- Developer can specify which fields they need (e.g., only location and speed)
- Developer can query historical data for time-series analysis
- API responses are predictable and well-documented

### 2.5 Troubleshooting Use Case

**User Story:**
> As a Fleeti support engineer, I want to access raw provider data and transformation metadata so I can troubleshoot telemetry issues and understand how data was transformed.

**Acceptance Criteria:**
- Support engineer can access raw provider packets for any telemetry record
- Support engineer can see which transformation rules were applied
- Support engineer can trace Fleeti telemetry back to original provider data
- Support engineer can see which configuration version was used
- Debug access is separate from customer-facing APIs

**User Experience:**
- Support engineer investigates a telemetry issue (e.g., "Speed shows incorrect value")
- Engineer accesses debug view for the telemetry record
- Engineer can see:
  - The transformed Fleeti telemetry value
  - Which provider field was used (e.g., "can_speed", "obd_speed", or "gps_speed")
  - The original raw provider packet
  - Which configuration version was applied
- Engineer can identify the root cause and resolve the issue

---

## 3. Functional Requirements

### 3.1 Real-Time Map Display

#### 3.1.1 Map Marker Data Requirements

**Required Fields for Map Markers:**

The following telemetry fields must be available **immediately** (within 100ms) for map marker display:

1. **Location:**
   - Latitude and longitude (required for marker position)
   - Heading (for direction indicator)

2. **Status:**
   - Top status code (determines marker color/icon)
   - Status family (connectivity, transit, engine, immobilization)

3. **Motion:**
   - Speed (for display on marker or tooltip)
   - Movement status (moving or stationary)

4. **Basic Vehicle Info:**
   - Asset name (for marker label)
   - Last update timestamp (for "last seen" display)

**Optional Fields (Nice-to-Have):**
- Fuel level (for fuel gauge indicator)
- Connectivity signal strength (for connection quality indicator)

#### 3.1.2 Update Performance Requirements

**Latency Requirements:**
- **Map marker updates:** Must appear on map within **100ms** of telemetry packet being received
- **Status changes:** Status changes (e.g., offline → online) must be reflected within **100ms**
- **Location updates:** Location changes must appear within **100ms** (GPS jitter filtering may delay minor movements)

**Update Frequency:**
- System must support updates for **all assets simultaneously**
- No throttling or batching that causes noticeable delays
- Updates should feel **real-time** to the user (no lag or stuttering)

**Scalability Requirements:**
- System must support **hundreds or thousands** of assets updating simultaneously
- Performance must not degrade as number of assets increases
- Map display must remain smooth with 1,000+ active assets

#### 3.1.3 Data Availability Requirements

**Current State:**
- System must maintain **current telemetry state** for every asset
- Current state must be queryable **instantly** (no database delay)
- System must handle assets that haven't updated recently (show last known state)

**Data Freshness:**
- System must indicate when telemetry data was last received
- System must handle offline assets gracefully (show "last seen X minutes ago")

### 3.2 Asset Detail View

#### 3.2.1 Data Requirements

**Required Fields for Asset Detail View:**

Asset detail view must display **all available telemetry fields** organized by category:

1. **Core Information:**
   - Location (lat, lng, heading, altitude)
   - Motion (speed, movement status)
   - Status (top status, all status families)

2. **Vehicle Information:**
   - Power (ignition state, battery level)
   - Fuel (level, consumption rate)
   - Counters (odometer, engine hours)

3. **Extended Information (If Available):**
   - Sensors (temperature, humidity, custom sensors)
   - Diagnostics (engine details, CAN data, vehicle health)
   - Driving behavior (harsh events, eco score)
   - Driver information
   - Connectivity details

**Field Availability:**
- Fields that aren't available for an asset must be clearly indicated (e.g., "Not available" or omitted)
- System must not show placeholder or null values without explanation
- User should understand why a field isn't available (no sensor, not configured, etc.)

#### 3.2.2 Performance Requirements

**Load Time:**
- Asset detail view must load within **500ms** of user clicking map marker
- Initial load should show core fields immediately
- Extended fields can load progressively if needed (but should be fast)

**Data Completeness:**
- Detail view must show **all available fields** for the asset
- No fields should be missing due to performance optimization
- System must merge core fields and extended fields into single response

#### 3.2.3 User Experience Requirements

**Progressive Loading:**
- Core fields (location, status, speed) should appear first
- Extended fields can load after core fields (but within 500ms total)
- Loading indicators should show progress if extended fields take time

**Field Organization:**
- Fields should be organized by category (Location, Motion, Power, Fuel, Sensors, etc.)
- Related fields should be grouped together
- User should be able to easily find specific fields

### 3.3 Customer API Access

#### 3.3.1 API Capabilities

**Live Data Access:**
- API must provide current telemetry state for any asset
- API must support querying multiple assets simultaneously
- API must return standardized Fleeti telemetry format (not provider-specific)

**Historical Data Access:**
- API must support time-range queries (e.g., "Last 24 hours", "January 2025")
- API must support querying single assets or multiple assets
- API must support flexible time ranges (1 day to multiple years)

**Batch Queries:**
- API must support querying multiple assets in single request
- API must support querying multiple time ranges
- API must support pagination for large result sets

#### 3.3.2 Field Selection

**Flexibility Requirements:**
- Customers must be able to request **specific fields** (e.g., "Give me only location and speed")
- Customers must be able to request **all fields** (complete telemetry object)
- Customers must be able to request **field subsets** (e.g., "All location and fuel fields")

**Field Selection Behavior:**
- If customer requests specific fields, API returns only those fields (reduces response size)
- If customer requests all fields, API returns complete telemetry object
- If customer requests fields that aren't available, API returns `null` or omits field

#### 3.3.3 Response Formats

**Required Formats:**
- **JSON** (primary format for programmatic access)
- Consistent field names and data types
- Standardized units (e.g., speed always in km/h, fuel in liters or percent)

**Optional Formats (Future):**
- CSV export for bulk data analysis
- GraphQL for flexible field selection (consider for Phase 2)

#### 3.3.4 Performance Requirements

**Live Data Queries:**
- API response time: **< 200ms** for current state queries
- API must handle concurrent requests from multiple customers
- API must support rate limiting to prevent abuse

**Historical Data Queries:**
- API response time: **< 500ms** for 1-day range queries
- API response time: **< 2 seconds** for 1-month range queries
- API response time: **< 5 seconds** for 1-year range queries

**Scalability:**
- API must support **100 requests per second per customer** (or defined rate limit)
- API must handle multiple customers querying simultaneously
- API performance must not degrade under load

### 3.4 Historical Data Access

#### 3.4.1 Time Range Support

**Supported Time Ranges:**
- **Short-term:** 1 hour to 1 day (for recent analysis)
- **Medium-term:** 1 day to 1 month (for weekly/monthly reports)
- **Long-term:** 1 month to multiple years (for annual analysis, compliance)

**Query Patterns:**
- Users typically query during business hours (5:00 - 19:00 CET)
- Query frequency: ~5 queries per hour (per customer or total - needs clarification)
- Time ranges vary: Some queries for 1 day, others for 1 month or longer

#### 3.4.2 Data Completeness

**All Fields Available:**
- Historical queries must return **all telemetry fields** available for the time period
- No fields should be excluded from historical queries
- Historical data must match what was available at the time (don't recalculate retroactively)

**Field Selection:**
- Users can request specific fields for historical queries (reduce response size)
- Users can request all fields for historical queries (complete data)

#### 3.4.3 Recalculation Capability

**Historical Recalculation Requirement:**
- System must support **recalculating historical data** when new fields are added
- System must preserve raw provider data to enable recalculation
- Recalculation must be able to process large time ranges (months or years)

**Use Case:**
- Product team adds new telemetry field (e.g., "fuel_economy_trip")
- System applies new calculation rule to all historical raw data
- Customers now have complete history of new field, not just future data

#### 3.4.4 Performance Requirements

**Query Performance:**
- **1-day range:** < 500ms response time
- **1-month range:** < 2 seconds response time
- **1-year range:** < 5 seconds response time
- **Multi-year range:** < 10 seconds response time (acceptable for bulk export)

**Data Aggregation (Future):**
- System should support aggregation queries (averages, sums, etc.) for reporting
- Aggregation queries should complete within acceptable time (TBD based on use cases)

### 3.5 Troubleshooting & Debug Access

#### 3.5.1 Debug Information Requirements

**Required Debug Data:**

1. **Transformed Telemetry:**
   - Complete Fleeti telemetry object (same as customer API)
   - All fields with current values

2. **Transformation Metadata:**
   - Which provider field was used for each Fleeti field (e.g., "speed came from can_speed")
   - Which configuration version was applied
   - When the transformation was performed

3. **Raw Provider Data:**
   - Original provider packet (exact format from provider)
   - Provider packet identifier
   - When the packet was received

4. **Configuration Details:**
   - Which configuration version was active at the time
   - Configuration hierarchy (default → customer → asset group → asset)
   - Effective configuration after all overrides

#### 3.5.2 Traceability Requirements

**Data Lineage:**
- System must maintain link from Fleeti telemetry → Raw provider packet
- System must maintain link from Fleeti telemetry → Configuration version used
- System must enable "drilling down" from transformed data to raw data

**Traceability Use Cases:**
- Troubleshoot incorrect telemetry value (trace back to provider field and config)
- Understand how provider data was transformed (which rules were applied)
- Validate transformation rules (compare raw vs. transformed data)

#### 3.5.3 Access Control

**Security Requirements:**
- Debug access must be **separate from customer-facing APIs**
- Debug access requires **super admin permissions**
- All debug access must be **audit logged** (who accessed what, when)
- Debug access should be **rate limited** to prevent abuse

**Access Patterns:**
- Debug access is infrequent (only when troubleshooting)
- Debug access may need to query historical data with metadata
- Debug access should be fast enough for efficient troubleshooting (< 1 second)

---

## 4. Performance Requirements

### 4.1 Latency Requirements

**Real-Time Map Updates:**
- **Telemetry receipt → Map marker update:** < 100ms
- **Status change → Map marker update:** < 100ms
- **Location change → Map marker update:** < 100ms (GPS jitter filtering may add small delay for minor movements)

**Asset Detail View:**
- **Marker click → Detail view load:** < 500ms
- **Core fields display:** < 200ms
- **Extended fields display:** < 500ms total

**Customer API:**
- **Current state query:** < 200ms (p95)
- **Historical query (1 day):** < 500ms (p95)
- **Historical query (1 month):** < 2 seconds (p95)
- **Historical query (1 year):** < 5 seconds (p95)

**Troubleshooting/Debug:**
- **Debug data access:** < 1 second
- **Raw data retrieval:** < 2 seconds (may require archive restore for old data)

### 4.2 Throughput Requirements

**Ingestion Throughput:**

| Timeframe | Assets | Messages/Second | Daily Messages |
|-----------|--------|-----------------|----------------|
| **Current (Year 1)** | 20,000 | ~116 | 10,000,000 |
| **Peak (Year 1)** | 20,000 | ~350 | (peak may be 2-3x average) |
| **Projected (Year 5)** | 100,000 | ~579 | 50,000,000 |
| **Peak (Year 5)** | 100,000 | ~1,700 | (peak may be 2-3x average) |

**System must handle:**
- Sustained ingestion at average rates
- Peak ingestion at 2-3x average rates
- No data loss during peak periods
- Graceful degradation (queue if needed, but don't drop data)

**Query Throughput:**

**WebSocket Connections:**
- Support **1,000 concurrent WebSocket connections**
- Each connection receives updates for subscribed assets
- Updates must be delivered promptly (within 100ms of telemetry receipt)

**API Requests:**
- Support **100 requests per second per customer** (or defined rate limit)
- Support multiple customers querying simultaneously
- Support batch queries (multiple assets, time ranges)

**Historical Queries:**
- Support **5 queries per hour** during business hours (per customer or total - needs clarification)
- Queries may span days, weeks, or months
- System must handle concurrent historical queries

### 4.3 Scalability Requirements

**Growth Projections:**

| Metric | Year 1 | Year 3 | Year 5 |
|--------|--------|--------|--------|
| **Assets** | 20,000 | ~50,000 | 100,000 |
| **Daily Messages** | 10M | 25M | 50M |
| **Messages/Second** | ~116 | ~290 | ~579 |
| **Peak Messages/Second** | ~350 | ~870 | ~1,700 |

**Scalability Requirements:**
- System must scale from **20,000 to 100,000 assets** (5x growth) without major refactoring
- Performance must not degrade as number of assets increases
- System must support horizontal scaling (add more capacity as needed)
- Storage must scale to handle 5x data volume

**Performance at Scale:**
- Map updates must remain fast (< 100ms) with 1,000+ active assets
- API queries must remain fast (< 200ms) regardless of total asset count
- Historical queries must remain acceptable (< 5 seconds) regardless of data volume

---

## 5. Data Requirements

### 5.1 Core Fields (Essential for Map Display)

**Core fields** are telemetry fields that are **essential for basic functionality** and must be available **immediately** for map markers and real-time updates.

**Core Field Categories:**

1. **Location:**
   - Latitude and longitude (required)
   - Heading (for direction indicator)
   - Altitude (optional, nice-to-have)

2. **Status:**
   - Top status (determines marker color/icon)
   - Status families (connectivity, transit, engine, immobilization)

3. **Motion:**
   - Speed (for display)
   - Movement status (moving/stationary)

4. **Basic Vehicle State:**
   - Ignition state (for status computation)
   - Last update timestamp (for "last seen" display)

5. **Connectivity:**
   - Signal strength (for connection quality indicator)

**Total Core Fields: ~25-30 fields**

**Performance Requirement:**
- Core fields must be queryable **instantly** (no database delay)
- Core fields must support **real-time updates** (< 100ms latency)
- Core fields must be **cached** for fast access

### 5.2 Extended Fields (Complete Telemetry)

**Extended fields** include **all other telemetry fields** beyond core fields. These are needed for asset detail views and customer API access.

**Extended Field Categories:**

1. **Sensors:**
   - Temperature sensors
   - Humidity sensors
   - Custom sensors
   - Environmental sensors

2. **Diagnostics:**
   - Engine diagnostics
   - CAN bus data
   - Vehicle health indicators
   - Body sensors (doors, lights, belts)

3. **Driving Behavior:**
   - Harsh acceleration/braking/cornering
   - Eco driving scores
   - Daily summaries

4. **Fuel & Energy:**
   - Fuel levels (multiple tanks)
   - Fuel consumption
   - EV battery levels
   - Charging status

5. **Advanced Features:**
   - Driver information
   - Geofences
   - Trip information
   - Nearby assets

**Total Extended Fields: 300+ fields**

**Performance Requirement:**
- Extended fields must be **queryable on-demand** (not cached, but fast)
- Extended fields must be available for asset detail views (< 500ms load time)
- Extended fields must be available for customer API access

### 5.3 Data Volume Estimates

**Current State (Year 1):**
- **Assets:** 20,000
- **Messages per asset per day:** 500
- **Total daily messages:** 10,000,000
- **Messages per second:** ~116 (average), ~350 (peak)

**Projected State (Year 5):**
- **Assets:** 100,000
- **Messages per asset per day:** 500
- **Total daily messages:** 50,000,000
- **Messages per second:** ~579 (average), ~1,700 (peak)

**Storage Estimates:**

**Raw Telemetry Packets (Uncompressed):**
- Average packet size: ~7.5 KB
- Daily storage: 10M × 7.5 KB = **75 GB/day** (Year 1)
- Daily storage: 50M × 7.5 KB = **375 GB/day** (Year 5)
- Monthly storage: **2.25 TB/month** (Year 1) → **11.25 TB/month** (Year 5)
- Annual storage: **27 TB/year** (Year 1) → **135 TB/year** (Year 5)

**Note:** Storage can be reduced by 70% with compression (recommended).

### 5.4 Data Retention Requirements

**Active Data (Frequently Accessed):**
- **Last 30 days:** Must be accessible instantly (fast queries)
- **Last 90 days:** Must be accessible quickly (< 2 seconds)
- **Last 1 year:** Must be accessible within acceptable time (< 5 seconds)

**Archived Data (Rarely Accessed):**
- **Older than 5 years:** Can be archived to slower, cheaper storage
- Archived data must still be accessible (may require restore time)
- Archived data must support recalculation when new fields are added

**Permanent Storage:**
- **Raw provider packets:** Must be stored permanently (for historical recalculation)
- Raw data is rarely accessed (only for recalculation or debugging)
- Raw data can be stored in cheapest storage tier after 5 years

**Data Lifecycle:**
- Recent data (0-30 days): Fast access, frequent queries
- Medium-term data (30-365 days): Moderate access, occasional queries
- Long-term data (1-5 years): Infrequent access, archive candidates
- Historical data (>5 years): Rarely accessed, cheapest storage tier

---

## 6. Storage Strategy (High-Level)

### 6.1 Storage Tier Concept

The telemetry system uses **three storage tiers** to balance performance, cost, and data preservation:

#### Tier 1: Fast Access Storage (Hot)

**Purpose:** Store frequently-accessed telemetry fields for real-time updates and common queries.

**Use Cases:**
- Real-time map marker updates
- Current asset state queries
- Recent historical queries (last 30 days)

**Performance Requirements:**
- Query latency: < 100ms for current state
- Update latency: < 100ms for new telemetry
- Must support high-frequency read and write operations

**Data Stored:**
- Core telemetry fields (~25-30 fields)
- Current state for all assets
- Recent historical data (last 30 days)

**Characteristics:**
- Fast read/write performance
- Higher cost per GB
- Optimized for frequent access

#### Tier 2: Complete Data Storage (Warm)

**Purpose:** Store all telemetry fields (core + extended) for detailed views and historical analysis.

**Use Cases:**
- Asset detail views (all fields)
- Customer API queries (all fields or field selection)
- Historical queries (30 days to 5 years)

**Performance Requirements:**
- Query latency: < 500ms for asset detail view
- Query latency: < 2 seconds for 1-month historical query
- Must support flexible field selection

**Data Stored:**
- All telemetry fields (core + extended, 300+ fields)
- Historical data (30 days to 5 years)
- Transformation metadata (for traceability)

**Characteristics:**
- Good read performance (slower than hot, faster than cold)
- Moderate cost per GB
- Optimized for on-demand queries

#### Tier 3: Permanent Archive Storage (Cold)

**Purpose:** Preserve all raw provider data for historical recalculation and long-term storage.

**Use Cases:**
- Historical recalculation (applying new transformation rules to old data)
- Troubleshooting (accessing original provider packets)
- Long-term data retention (compliance, analysis)

**Performance Requirements:**
- Access latency: Can be slower (seconds to minutes for archive restore)
- Must support batch processing for recalculation
- Rarely accessed (only for recalculation or debugging)

**Data Stored:**
- Raw provider telemetry packets (original format)
- Permanent retention (never deleted)

**Characteristics:**
- Slow access (archive restore required for old data)
- Very low cost per GB
- Optimized for cost, not speed

### 6.2 Data Flow Between Tiers

**Ingestion Flow:**
1. Provider sends raw telemetry packet
2. System stores raw packet in **Cold Storage** (permanent archive)
3. System transforms packet to Fleeti format
4. System stores core fields in **Fast Access Storage**
5. System stores all fields (core + extended) in **Complete Data Storage**

**Query Flow:**
1. **Map marker query:** Reads from Fast Access Storage (core fields only, instant)
2. **Asset detail query:** Reads from Complete Data Storage (all fields, < 500ms)
3. **Historical query:** Reads from Complete Data Storage (all fields, time-range query)
4. **Recalculation query:** Reads from Cold Storage (raw packets, batch processing)

### 6.3 Data Lifecycle

**Data Aging:**
- **0-30 days:** In Fast Access Storage (hot)
- **30-365 days:** In Complete Data Storage (warm)
- **1-5 years:** In Complete Data Storage, may optimize for cost
- **>5 years:** Move to Cold Storage archive

**Note:** Raw provider packets are always stored in Cold Storage from day one.

### 6.4 Cost Considerations

**Storage Cost Strategy:**
- **Fast Access:** Higher cost, but necessary for performance
- **Complete Data:** Moderate cost, balances performance and completeness
- **Cold Archive:** Very low cost, preserves data for recalculation

**Cost Optimization:**
- Move older data to cheaper storage tiers automatically
- Compress raw packets to reduce storage by 70%
- Archive data older than 5 years to cheapest storage
- Monitor storage growth and optimize based on access patterns

**Budget Constraints:**
- Target storage costs within reasonable budget (exact budget TBD)
- Optimize for cost while meeting performance requirements
- Consider data compression and lifecycle policies to reduce costs

---

## 7. API Requirements

### 7.1 API Capabilities

#### 7.1.1 Live Data Access

**Required Capabilities:**
- Get current telemetry state for a single asset
- Get current telemetry state for multiple assets (batch query)
- Get current telemetry state for all assets in a fleet/customer

**Response Requirements:**
- Returns standardized Fleeti telemetry format
- Includes all available fields (core + extended)
- Returns most recent telemetry for each asset
- Indicates when data was last updated

**Performance:**
- Response time: < 200ms for single asset
- Response time: < 500ms for multiple assets (up to 100 assets)
- Response time: < 2 seconds for all assets (large fleets)

#### 7.1.2 Historical Data Access

**Required Capabilities:**
- Query telemetry for a single asset over a time range
- Query telemetry for multiple assets over a time range
- Query telemetry for all assets in a fleet over a time range
- Support flexible time ranges (1 hour to multiple years)

**Time Range Support:**
- **Short-term:** 1 hour to 1 day
- **Medium-term:** 1 day to 1 month
- **Long-term:** 1 month to multiple years

**Response Requirements:**
- Returns time-series data (array of telemetry records)
- Each record includes timestamp and requested fields
- Records sorted chronologically
- Supports pagination for large result sets

**Performance:**
- 1-day range: < 500ms
- 1-month range: < 2 seconds
- 1-year range: < 5 seconds
- Multi-year range: < 10 seconds (acceptable for bulk export)

#### 7.1.3 Field Selection

**Required Capabilities:**
- Customer can request specific fields (e.g., "Give me only location and speed")
- Customer can request all fields (complete telemetry object)
- Customer can request field groups (e.g., "All location fields", "All fuel fields")

**Field Selection Syntax:**
- Simple: `?fields=location,speed,status`
- Nested: `?fields=location.lat,location.lng,speed,status.top_status`
- All fields: `?fields=*`

**Behavior:**
- If field is requested but not available → Returns `null` or omits field
- If no fields specified → Returns core fields only (default)
- Field selection applies to both live and historical queries

### 7.2 Query Patterns

#### 7.2.1 Common Query Patterns

**Pattern 1: Current State**
- **Use Case:** Get latest telemetry for an asset
- **Query:** Single asset, no time range
- **Fields:** All fields or specific fields
- **Frequency:** Very high (WebSocket updates, map markers)

**Pattern 2: Time-Series (Single Asset)**
- **Use Case:** Chart speed over time for a vehicle
- **Query:** Single asset, time range (e.g., "Last 24 hours")
- **Fields:** Specific fields (e.g., speed, timestamp)
- **Frequency:** Medium (5 queries/hour during business hours)

**Pattern 3: Time-Series (Multiple Assets)**
- **Use Case:** Compare fuel consumption across fleet
- **Query:** Multiple assets, time range
- **Fields:** Specific fields (e.g., fuel consumption, timestamp)
- **Frequency:** Low (occasional analysis)

**Pattern 4: Asset Detail**
- **Use Case:** Show all telemetry for an asset
- **Query:** Single asset, current state
- **Fields:** All fields
- **Frequency:** Medium (user clicks on map marker)

#### 7.2.2 Filtering & Pagination

**Filtering Requirements:**
- Filter by asset type (vehicles, equipment, sites, phones)
- Filter by asset group
- Filter by customer
- Filter by status (online, offline, in-transit, etc.)
- Filter by time range

**Pagination Requirements:**
- Support pagination for large result sets
- Default page size: 100 records
- Allow customer to specify page size (up to 1,000 records)
- Provide pagination tokens/links for next/previous pages

### 7.3 Response Formats

#### 7.3.1 Primary Format: JSON

**JSON Structure:**
- Standardized Fleeti telemetry format
- Consistent field names and data types
- Standardized units (speed in km/h, fuel in liters, etc.)
- Nested objects for related fields (location, status, etc.)

**Example Response:**
```json
{
  "asset_id": "uuid",
  "timestamp": 1234567890000,
  "location": {
    "latitude": 5.3561,
    "longitude": -4.0083,
    "heading": 180
  },
  "status": {
    "top_status": {
      "family": "transit",
      "code": "in_transit"
    }
  },
  "motion": {
    "speed": { "value": 50.5, "unit": "km/h" }
  }
}
```

#### 7.3.2 Error Handling

**Error Response Format:**
- Standardized error format
- HTTP status codes (400, 404, 500, etc.)
- Error messages in JSON format
- Error codes for programmatic handling

**Common Errors:**
- Asset not found
- Invalid time range
- Invalid field selection
- Rate limit exceeded
- Server error

### 7.4 API Performance Expectations

**Live Data Queries:**
- Single asset: < 200ms
- Multiple assets (10 assets): < 300ms
- Multiple assets (100 assets): < 500ms
- All assets (large fleet): < 2 seconds

**Historical Queries:**
- 1-day range: < 500ms
- 1-week range: < 1 second
- 1-month range: < 2 seconds
- 1-year range: < 5 seconds

**Field Selection Impact:**
- Core fields only: Fastest (< 200ms)
- Core + some extended fields: Moderate (< 500ms)
- All fields: Slower but acceptable (< 1 second)

---

## 8. Non-Functional Requirements

### 8.1 Scalability

**Growth Support:**
- System must scale from **20,000 assets to 100,000+ assets** (5x growth)
- Performance must not degrade as asset count increases
- System must support horizontal scaling (add capacity as needed)

**Scalability Targets:**
- **Year 1:** 20,000 assets, 10M messages/day, 116 msg/sec
- **Year 5:** 100,000 assets, 50M messages/day, 579 msg/sec
- System must handle **peak loads** (2-3x average message rate)

**Scalability Strategy:**
- Design for horizontal scaling from day one
- No single point of failure
- Ability to add capacity incrementally
- Performance monitoring to identify scaling needs early

### 8.2 Reliability

**Uptime Requirements:**
- System availability: **99.9% uptime** (less than 8.76 hours downtime per year)
- Planned maintenance should be minimal and scheduled
- Unplanned downtime should be rare and quickly resolved

**Data Integrity:**
- No data loss during normal operations
- No data loss during peak load periods
- Data must be consistent (no corruption or partial writes)

**Error Handling:**
- System must handle provider outages gracefully
- System must handle database issues gracefully
- System must provide clear error messages to users
- System must log errors for troubleshooting

**Backup & Recovery:**
- Regular automated backups of critical data
- Ability to restore data from backups
- Disaster recovery plan (RTO and RPO TBD)

### 8.3 Security

**Access Control:**
- Customer API access requires authentication (API keys, OAuth, etc.)
- Customers can only access their own assets
- Debug/troubleshooting access requires super admin permissions
- All access must be audit logged

**Data Privacy:**
- Telemetry data must be encrypted in transit (TLS)
- Telemetry data must be encrypted at rest
- Customer data must be isolated (multi-tenancy)

**API Security:**
- Rate limiting to prevent abuse
- Input validation to prevent injection attacks
- API keys/tokens for authentication
- CORS configuration for web clients

**Audit Logging:**
- Log all API access (who, what, when)
- Log all configuration changes
- Log all debug/troubleshooting access
- Logs must be retained for compliance (retention period TBD)

### 8.4 Maintainability

**Field Addition:**
- System must support **adding new telemetry fields** without major refactoring
- New fields can be added via configuration (no code changes)
- Historical recalculation must work for new fields

**Transformation Rule Updates:**
- System must support **updating transformation rules** via configuration
- Configuration changes should take effect without service restart
- System must support **configuration versioning** and rollback

**Provider Addition:**
- System must support **adding new providers** without major refactoring
- New providers can be added via configuration and mapping rules
- System must remain provider-agnostic

**Monitoring & Observability:**
- System must provide metrics (latency, throughput, error rates)
- System must provide logs for troubleshooting
- System must alert on performance degradation or errors
- System must provide dashboards for operational visibility

---

## 9. Success Criteria

### 9.1 Functional Success Criteria

✅ **Map Display:**
- Map markers update within 100ms of telemetry receipt
- Map supports 1,000+ assets simultaneously without lag
- Status changes are reflected immediately on map

✅ **Asset Detail View:**
- Detail view loads within 500ms
- All available telemetry fields are displayed
- Fields are clearly organized and easy to find

✅ **Customer API:**
- API responses are fast (< 200ms for live data)
- API supports field selection
- API supports historical queries
- API documentation is clear and complete

✅ **Historical Data:**
- Historical queries complete within acceptable time
- All historical data is accessible
- Historical recalculation works for new fields

✅ **Troubleshooting:**
- Support team can access raw provider data
- Support team can trace transformations
- Debug access is secure and audit logged

### 9.2 Performance Success Criteria

✅ **Latency:**
- Map updates: < 100ms
- Asset detail view: < 500ms
- API queries: < 200ms (live), < 2 seconds (1-month historical)

✅ **Throughput:**
- System handles 10M messages/day (Year 1)
- System handles 50M messages/day (Year 5)
- System handles peak loads (2-3x average)

✅ **Scalability:**
- System scales from 20K to 100K assets without major refactoring
- Performance does not degrade as asset count increases

### 9.3 Data Success Criteria

✅ **Completeness:**
- All telemetry data is preserved (raw + transformed)
- No data loss during ingestion or storage
- Historical data remains accessible

✅ **Traceability:**
- Every transformed record links to raw provider data
- Transformation metadata is preserved
- Configuration versions are tracked

---

## 10. Open Questions & Decisions Needed

### 10.1 Product Decisions

1. **Historical Query Frequency:**
   - Question: Is "5 queries/hour" per customer or total across all customers?
   - Impact: Affects capacity planning for historical query performance
   - **Action:** Clarify with product team

2. **Data Retention Policy:**
   - Question: Exact retention periods for different data tiers?
   - Current: Archive after 5 years confirmed
   - **Decision Needed:** Retention periods for fast access (30 days? 90 days?) and complete data storage (1 year? 5 years?)

3. **Field Selection Default:**
   - Question: What should API return if no fields specified?
   - **Decision Needed:** Core fields only (faster) or all fields (more complete)?

4. **API Rate Limits:**
   - Question: What rate limits should be enforced per customer?
   - Current estimate: 100 requests/second per customer
   - **Decision Needed:** Confirm rate limits and define tiered limits if needed

### 10.2 Technical Decisions (For Development Team)

1. **Database Technology:**
   - Product requirement: Fast queries for core fields, flexible queries for extended fields
   - **Decision for developers:** Choose database technology that meets these requirements

2. **Caching Strategy:**
   - Product requirement: Map markers must update within 100ms
   - **Decision for developers:** Implement caching strategy to meet latency requirement

3. **API Design Pattern:**
   - Product requirement: Support field selection, historical queries, batch queries
   - **Decision for developers:** Choose REST, GraphQL, or hybrid approach

### 10.3 Future Considerations

1. **Data Streaming (Future):**
   - Product requirement: Support real-time streaming (WebSocket, SSE, message queue)
   - **Status:** Not in MVP scope, but architecture must support it
   - **Action:** Design architecture to accommodate future streaming requirements

2. **Advanced Analytics:**
   - Product requirement: Support aggregation queries (averages, sums, etc.)
   - **Status:** Not in MVP scope, but consider for Phase 2
   - **Action:** Design storage to support future aggregation capabilities

---

## 11. Prioritization & Phases

### Phase 1: MVP (Minimum Viable Product)

**Core Capabilities:**
- Real-time map display with core fields
- Asset detail view with all available fields
- Basic customer API (live data, simple historical queries)
- Single default configuration (no customer/asset overrides)

**Performance Targets:**
- Map updates: < 100ms
- Asset detail: < 500ms
- API queries: < 200ms (live), < 2 seconds (historical)

**Storage:**
- Fast access storage (core fields)
- Complete data storage (all fields)
- Raw storage archive

### Phase 2: Enhanced API & Configuration

**Additional Capabilities:**
- Advanced customer API (field selection, batch queries)
- Configuration hierarchy (default → customer → asset group → asset)
- Configuration versioning and rollback
- Improved historical query performance

### Phase 3: Advanced Features

**Additional Capabilities:**
- Data streaming (WebSocket, SSE)
- Advanced analytics (aggregation queries)
- Multi-provider support (beyond Navixy)
- Cost optimization (advanced lifecycle policies)

---

## 12. Dependencies & Assumptions

### Dependencies

1. **Asset Service:**
   - Asset metadata (type, name, group, customer) must be available
   - Asset service must provide asset information for telemetry records

2. **Configuration Service:**
   - Transformation configuration must be accessible
   - Configuration changes must be communicated to telemetry system

3. **Geofence Service:**
   - Geofence data must be available for geofence context computation
   - Geofence service must support spatial queries

4. **Driver Service:**
   - Driver catalog must be available for driver identification
   - Driver service must support hardware key lookups

### Assumptions

1. **Provider Data Format:**
   - Provider data format remains relatively stable
   - New provider fields can be added via configuration

2. **Asset Growth:**
   - Growth is predictable (20K → 100K over 5 years)
   - Message frequency remains consistent (~500 messages/asset/day)

3. **Customer Usage:**
   - Customer API usage is reasonable (not excessive abuse)
   - Rate limiting prevents abuse scenarios

4. **Network Connectivity:**
   - Assets have reasonable network connectivity
   - Provider data forwarding is reliable

---

## Appendix A: Glossary

**Core Fields:** Essential telemetry fields needed for map display and real-time updates (~25-30 fields)

**Extended Fields:** All other telemetry fields beyond core fields (300+ fields)

**Fast Access Storage (Hot):** Storage tier for frequently-accessed core fields (optimized for speed)

**Complete Data Storage (Warm):** Storage tier for all telemetry fields (core + extended)

**Cold Archive Storage (Cold):** Storage tier for raw provider packets (optimized for cost, permanent retention)

**Transformation Metadata:** Information about how provider data was transformed into Fleeti format (which fields used, config version, etc.)

**Raw Provider Data:** Original telemetry packets from providers (before transformation)

**Fleeti Telemetry:** Standardized telemetry format used throughout Fleeti (provider-agnostic)

---

## Document History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-01-XX | Initial product requirements document | Product Team |

---

**Document Status:** Draft - Pending Review  
**Next Steps:**
1. Review with product team and stakeholders
2. Resolve open questions (Section 10)
3. Finalize prioritization and phases
4. Hand off to development team for technical design

