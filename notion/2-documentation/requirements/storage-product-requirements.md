# Storage Product Requirements

⚠️ **Status: Under Review**

**This document contains product requirements that have not yet been fully reviewed and validated. Use as reference only. Technical implementation details may change based on review.**

**Source:** `working/telemetry-storage-product-requirements.md`  
**Document Version:** 1.0  
**Date:** 2025-01-XX  
**Status:** Draft - Pending Review  
**Owner:** Product Team

---

## Executive Summary

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

## User Stories & Use Cases

### Real-Time Map Display Use Case

**User Story:**
> As a fleet manager, I want to see all my vehicles on a map with real-time location updates so I can monitor fleet activity as it happens.

**Acceptance Criteria:**
- Map markers update within 100ms of receiving new telemetry
- Map displays hundreds or thousands of assets simultaneously without performance degradation
- Each marker shows current location, status, and basic vehicle information
- Map remains responsive when many assets update at the same time
- Status changes (e.g., vehicle goes offline, engine starts) are reflected immediately

### Asset Detail View Use Case

**User Story:**
> As a fleet manager, I want to click on a map marker to see detailed telemetry information about that vehicle so I can understand its current state and diagnose issues.

**Acceptance Criteria:**
- Detail view loads within 500ms of clicking marker
- Detail view shows all available telemetry fields for that asset
- Fields that aren't available are clearly indicated (not just missing)
- Detail view includes current values, historical trends, and status information
- User can see sensor readings, diagnostics, fuel levels, driving behavior, etc.

### Historical Analysis Use Case

**User Story:**
> As a fleet manager, I want to analyze telemetry trends over time so I can identify patterns, optimize operations, and generate reports.

**Acceptance Criteria:**
- User can query telemetry data for any time range (1 day to several years)
- Queries complete within acceptable time (1 day < 500ms, 1 month < 2 seconds)
- User can request specific fields or all fields
- Data can be visualized as time-series charts (speed over time, fuel consumption, etc.)
- Historical data supports recalculation when new fields are added

### Customer API Integration Use Case

**User Story:**
> As a customer developer, I want to integrate Fleeti telemetry data into my own system via API so I can build custom dashboards and workflows.

**Acceptance Criteria:**
- API provides consistent Fleeti telemetry format (not provider-specific)
- API supports live data queries (current state of assets)
- API supports historical data queries (time-series data)
- API allows field selection (customer chooses which fields to retrieve)
- API responses are fast and reliable
- API documentation is clear and comprehensive

### Troubleshooting Use Case

**User Story:**
> As a Fleeti support engineer, I want to access raw provider data and transformation metadata so I can troubleshoot telemetry issues and understand how data was transformed.

**Acceptance Criteria:**
- Support engineer can access raw provider packets for any telemetry record
- Support engineer can see which transformation rules were applied
- Support engineer can trace Fleeti telemetry back to original provider data
- Support engineer can see which configuration version was used
- Debug access is separate from customer-facing APIs

---

## Functional Requirements

### Real-Time Map Display

#### Map Marker Data Requirements

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

#### Update Performance Requirements

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

### Asset Detail View

#### Data Requirements

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

#### Performance Requirements

**Load Time:**
- Asset detail view must load within **500ms** of user clicking map marker
- Initial load should show core fields immediately
- Extended fields can load progressively if needed (but should be fast)

**Data Completeness:**
- Detail view must show **all available fields** for the asset
- No fields should be missing due to performance optimization
- System must merge core fields and extended fields into single response

### Customer API Access

#### API Capabilities

**Live Data Access:**
- API must provide current telemetry state for any asset
- API must support querying multiple assets simultaneously
- API must return standardized Fleeti telemetry format (not provider-specific)

**Historical Data Access:**
- API must support time-range queries (e.g., "Last 24 hours", "January 2025")
- API must support querying single assets or multiple assets
- API must support flexible time ranges (1 day to multiple years)

**Field Selection:**
- Customers must be able to request **specific fields** (e.g., "Give me only location and speed")
- Customers must be able to request **all fields** (complete telemetry object)
- Customers must be able to request **field subsets** (e.g., "All location and fuel fields")

#### Performance Requirements

**Live Data Queries:**
- API response time: **< 200ms** for current state queries
- API must handle concurrent requests from multiple customers
- API must support rate limiting to prevent abuse

**Historical Data Queries:**
- API response time: **< 500ms** for 1-day range queries
- API response time: **< 2 seconds** for 1-month range queries
- API response time: **< 5 seconds** for 1-year range queries

### Historical Data Access

#### Time Range Support

**Supported Time Ranges:**
- **Short-term:** 1 hour to 1 day (for recent analysis)
- **Medium-term:** 1 day to 1 month (for weekly/monthly reports)
- **Long-term:** 1 month to multiple years (for annual analysis, compliance)

#### Recalculation Capability

**Historical Recalculation Requirement:**
- System must support **recalculating historical data** when new fields are added
- System must preserve raw provider data to enable recalculation
- Recalculation must be able to process large time ranges (months or years)

**Use Case:**
- Product team adds new telemetry field (e.g., "fuel_economy_trip")
- System applies new calculation rule to all historical raw data
- Customers now have complete history of new field, not just future data

---

## Performance Requirements

### Latency Requirements

**Real-Time Map Updates:**
- **Telemetry receipt → Map marker update:** < 100ms
- **Status change → Map marker update:** < 100ms
- **Location change → Map marker update:** < 100ms

**Asset Detail View:**
- **Marker click → Detail view load:** < 500ms
- **Core fields display:** < 200ms
- **Extended fields display:** < 500ms total

**Customer API:**
- **Current state query:** < 200ms (p95)
- **Historical query (1 day):** < 500ms (p95)
- **Historical query (1 month):** < 2 seconds (p95)
- **Historical query (1 year):** < 5 seconds (p95)

### Throughput Requirements

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

### Scalability Requirements

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

---

## Storage Strategy

⚠️ **Note**: Storage strategy details are under review. This section provides product requirements, not technical implementation details.

### Three-Tier Storage

The telemetry system must store data in **three tiers** to balance performance, cost, and data preservation:

1. **Fast Access (Hot)** - Core fields for real-time map updates (< 100ms latency)
2. **Complete Data (Warm)** - All fields for detail views and API access (< 500ms latency)
3. **Raw Archive (Cold)** - Original provider packets for historical recalculation (permanent retention)

### Storage Tier Requirements

#### Fast Access Storage (Hot)

**Product Need**: Real-time map marker updates require instant access to essential telemetry fields.

- **Stored**: ~25-30 core fields (location, speed, ignition, basic vehicle state)
- **Performance**: < 100ms query latency for current asset state
- **Use Cases**: Map display, live tracking, real-time updates
- **Volume**: High-frequency reads and writes
- **Retention**: Last 30 days (optimized for real-time queries)

#### Complete Data Storage (Warm)

**Product Need**: Asset detail views and customer API queries require access to all telemetry fields (300+ fields).

- **Stored**: All Fleeti telemetry fields (core + extended)
- **Performance**: < 500ms load time for asset detail view, < 2 seconds for 1-month historical query
- **Use Cases**: Asset detail views, customer API (100% need extended fields), historical analysis
- **Volume**: On-demand queries, batch historical queries
- **Retention**: 1-5 years (optimized for historical queries)

#### Raw Archive Storage (Cold)

**Product Need**: Historical recalculation requires access to original provider packets.

- **Stored**: All raw provider telemetry packets (original format, permanent retention)
- **Performance**: On-demand access (seconds to minutes acceptable for archive restore)
- **Use Cases**: Historical recalculation when new fields are added, troubleshooting, debugging
- **Volume**: Rarely accessed (batch processing for recalculation only)
- **Retention**: Permanent (required for historical recalculation)

### Data Transformation & Storage Flow

**Ingestion Flow:**

1. Store raw provider packet in Cold Storage (permanent archive)
2. Transform provider fields to Fleeti format (apply configuration rules)
3. Store core fields in Fast Access Storage
4. Store all fields (core + extended) in Complete Data Storage

**Transformation Requirements:**

- Apply priority rules (field selection from multiple sources)
- Apply calculation rules (derive new fields from existing data)
- Preserve all provider fields in extended storage for traceability

### Historical Recalculation

**Product Need**: When new Fleeti telemetry fields are added, customers must have complete historical data for those fields.

**Capability Required:**

- System must be able to scan all historical raw packets
- System must apply new transformation rules to old data
- System must update Complete Data Storage with newly calculated fields
- Customers see complete historical data for new fields (no gaps)

**Requirement**: Raw archive storage must be permanent/very long-term to enable historical recalculation.

---

## Data Retention

- **Fast Access**: Last 30 days (optimized for real-time queries)
- **Complete Data**: 1-5 years (optimized for historical queries)
- **Raw Archive**: Permanent (required for historical recalculation)

**Cost Optimization**: Data older than 5 years may be archived to slower, cheaper storage tiers while remaining accessible for recalculation.

---

## Traceability Requirements

### Data Lineage

**Requirement**: System must maintain link from Fleeti telemetry → Raw provider packet

**Traceability Use Cases:**
- Troubleshoot incorrect telemetry value (trace back to provider field and config)
- Understand how provider data was transformed (which rules were applied)
- Validate transformation rules (compare raw vs. transformed data)

### Debug Information

**Required Debug Data:**

1. **Transformed Telemetry:** Complete Fleeti telemetry object
2. **Transformation Metadata:** Which provider field was used, which configuration version
3. **Raw Provider Data:** Original provider packet (exact format from provider)
4. **Configuration Details:** Which configuration version was active, effective configuration after overrides

---

## Related Documentation

- **[Telemetry System Specification](../specifications/telemetry-system-specification.md)**: Complete system specification
- **[Architecture Overview](../../overview-vision/architecture-overview.md)**: System architecture (includes storage strategy overview)
- **[Field Mapping Requirements](./field-mapping-requirements.md)**: Field mapping requirements

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-XX  
**Status**: ⚠️ Under Review - Not yet validated  
**Source**: `working/telemetry-storage-product-requirements.md`

**Important Disclaimer**: This document contains product requirements that have not yet been fully reviewed and validated. Use as reference only. Technical implementation details may change based on review.






