# Expert Review: Telemetry Storage Strategy & Data Consumption Architecture

**Author:** Senior Data Storage Architect & API Design Specialist  
**Date:** 2025-01-XX  
**Review Scope:** Section 6 (Storage Strategy) of Fleeti Telemetry System Specification

---

## 1. Executive Summary

### AWS-Specific Context

**⚠️ IMPORTANT:** This analysis assumes **AWS as the cloud provider** (non-negotiable). All recommendations are tailored for AWS-native services:

- **Raw Storage:** AWS S3 with lifecycle policies (Standard → Intelligent-Tiering → Glacier)
- **Database:** RDS PostgreSQL with TimescaleDB extension (or self-managed on EC2)
- **Caching:** ElastiCache Redis
- **Ingestion:** Kinesis Data Streams or SQS
- **API:** API Gateway (REST + WebSocket)
- **Compute:** ECS/EKS or Lambda

### High-Level Assessment

The proposed three-layer storage architecture (raw/cold, core/hot, extended/warm) is **fundamentally sound** but requires significant refinement in several critical areas. The core concept aligns with industry best practices for telemetry systems, but implementation details need clarification to avoid performance bottlenecks and operational complexity.

**AWS-Specific Considerations:**
- TimescaleDB availability on RDS needs verification (fallback to EC2 if not supported)
- S3 lifecycle policies are critical for cost optimization
- ElastiCache Redis provides managed caching layer
- API Gateway supports both REST and WebSocket APIs
- Kinesis Data Streams handles high-volume ingestion efficiently

**🔴 CRITICAL FINDING FROM VOLUME ANALYSIS:**
- **100% of API queries require extended fields** - JSONB performance optimization is **NOT optional**
- **40% of WebSocket queries require extended fields** - Cannot optimize for core-only
- This means database sizing, indexing, and caching strategies must prioritize JSONB query performance from day one
- Start with **db.r5.xlarge or larger** instance sizes to handle JSONB queries efficiently

### Key Recommendations at a Glance

1. **✅ Keep three-layer architecture** - Valid approach, but refine boundaries and merge strategy
2. **⚠️ Use TimescaleDB on AWS** - RDS PostgreSQL with TimescaleDB extension (verify support) or self-managed on EC2
3. **✅ Single database with JSONB for extended** - Avoids cross-database joins, simplifies queries (works well on RDS)
4. **🔴 CRITICAL: Store transformation metadata with every record** - Essential for traceability and historical recalculation
5. **⚠️ Define exact core field set now** - "~50 fields" is too vague for implementation
6. **✅ WebSocket should use optimized payload structure** - Not raw telemetry objects (use API Gateway WebSocket API)
7. **🔴 CRITICAL: Address mapping metadata storage** - Current spec is silent on this critical requirement
8. **✅ AWS S3 for raw storage** - Use lifecycle policies for cost optimization (Standard → Glacier)
9. **✅ ElastiCache Redis for caching** - Managed caching layer for WebSocket performance
10. **✅ Kinesis Data Streams for ingestion** - High-volume streaming ingestion (or SQS for lower volume)

### Critical Gaps or Concerns

1. **Missing Transformation Metadata Storage** - The spec mentions historical mapping consultation but doesn't specify how transformation metadata (which provider field was used, config version, etc.) is stored. This is **critical** for traceability.

2. **Unclear Merge Strategy** - No defined approach for merging hot and warm storage in API responses, which could lead to inconsistent query performance.

3. **Vague Core Field Definition** - "~50 fields" is too imprecise. Need explicit field list for database schema design.

4. **Raw Storage Linkage Undefined** - How raw storage records link to transformed telemetry for recalculation is not specified.

5. **Configuration Versioning Gap** - Configuration versioning is mentioned but storage/querying mechanism is undefined.

6. **WebSocket Optimization Unspecified** - Frontend requires optimized payloads, but spec doesn't detail structure.

---

## 2. Detailed Analysis

### 2.1 Storage Architecture Review

#### Is the Three-Layer Architecture Appropriate?

**✅ YES, with refinements.**

The three-layer approach is appropriate for your use cases:

- **Raw (Cold)**: Essential for historical recalculation - ✅ Correct
- **Core (Hot)**: Fast access for 90% of queries - ✅ Correct approach
- **Extended (Warm)**: Complete data preservation - ✅ Correct approach

**However**, the boundaries between layers need clearer definition, and the merge strategy needs specification.

#### Should Core and Extended Be in the Same Database?

**✅ YES - Use single PostgreSQL/TimescaleDB with JSONB column for extended.**

**Recommendation:** Store core fields as relational columns in a TimescaleDB hypertable, with extended fields in a JSONB column on the same row.

**Rationale:**

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **Same DB (PostgreSQL + JSONB)** | ✅ Single query for merged data<br>✅ ACID transactions<br>✅ Foreign key integrity<br>✅ Simplified schema | ⚠️ JSONB query performance for complex queries<br>⚠️ Index limitations on nested JSONB | **RECOMMENDED** |
| **Separate Databases** | ✅ Can optimize each independently<br>✅ Scale independently | ❌ Complex cross-DB joins<br>❌ No ACID guarantees across DBs<br>❌ Two query sources to merge<br>❌ Operational complexity | **NOT RECOMMENDED** |

**Trade-off Analysis:**

The single-database approach wins because:
1. **API responses often need both** - Customer API will frequently query core + extended fields
2. **Simpler queries** - Single SELECT with JSONB access vs. two queries + merge
3. **Consistency** - ACID transactions ensure data consistency
4. **JSONB is mature** - PostgreSQL JSONB performance is excellent for your use case (read-heavy, occasional deep queries)

**Exception:** Only consider separate databases if:
- Extended storage grows to **tens of TB** and needs different scaling strategy
- You have **strict compliance requirements** for data segregation
- JSONB query performance becomes a bottleneck (measure first, optimize later)

#### How to Handle Merging Hot and Warm Storage?

**Single Query Strategy (Recommended):**

```sql
SELECT 
    -- Core fields (relational columns)
    telemetry_id,
    asset_id,
    timestamp,
    location_lat,
    location_lng,
    speed_kmh,
    status_top_status_code,
    -- Extended fields (JSONB)
    extended_data->'sensors' as sensors,
    extended_data->'diagnostics' as diagnostics,
    -- Transformation metadata (JSONB)
    transformation_metadata->'config_version' as config_version,
    transformation_metadata->'provider_fields_used' as provider_fields_used
FROM telemetry_core
WHERE asset_id = $1 AND timestamp BETWEEN $2 AND $3;
```

**Performance Optimization:**
- Use **GIN indexes** on frequently-queried JSONB paths (e.g., `extended_data->'sensors'->>'temperature'`)
- Use **partial indexes** for common query patterns
- Consider **materialized views** for complex aggregations

**Field Selection Strategy:**
- If query only needs core fields → SELECT relational columns only (fast)
- If query needs extended fields → Include JSONB access (slightly slower, but acceptable)
- If query needs ALL fields → Full SELECT with JSONB expansion (use for asset detail views)

#### PostgreSQL JSONB vs Separate Document Store

**✅ PostgreSQL JSONB is the right choice.**

**Comparison:**

| Feature | PostgreSQL JSONB | MongoDB/Elasticsearch |
|---------|------------------|----------------------|
| Query Performance (Core + Extended) | ✅ Single query, excellent | ❌ Requires aggregation/join |
| ACID Transactions | ✅ Full support | ⚠️ Limited/eventual consistency |
| Operational Complexity | ✅ Single DB to manage | ❌ Two systems to operate |
| Schema Flexibility | ✅ Flexible (JSONB) + Structured (columns) | ✅ Flexible |
| Cost | ✅ Lower (single infrastructure) | ❌ Higher (two systems) |
| Learning Curve | ✅ Team likely knows PostgreSQL | ⚠️ Additional expertise needed |

**Verdict:** Stick with PostgreSQL JSONB unless you have a compelling reason (e.g., need full-text search across all fields → consider Elasticsearch as an index, not primary storage).

#### How to Link Raw Storage to Transformed Telemetry?

**🔴 CRITICAL GAP - Needs specification.**

**Recommended Approach (AWS-Specific):**

1. **Store raw storage reference in transformed record:**

```sql
CREATE TABLE telemetry_core (
    telemetry_id UUID PRIMARY KEY,
    asset_id UUID NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    
    -- Core fields (relational)
    location_lat DECIMAL(10, 8),
    location_lng DECIMAL(11, 8),
    -- ... other core fields
    
    -- Metadata columns (AWS S3)
    raw_storage_key VARCHAR(500), -- S3 object key (full path)
    raw_storage_bucket VARCHAR(100) DEFAULT 'fleeti-raw-telemetry', -- S3 bucket name
    provider_name VARCHAR(50), -- 'navixy', 'oem_trackunit', etc.
    provider_packet_id VARCHAR(255), -- Provider's packet identifier
    
    -- Extended data (JSONB)
    extended_data JSONB,
    
    -- Transformation metadata (JSONB) - SEE SECTION 2.5
    transformation_metadata JSONB,
    
    -- Indexes
    CONSTRAINT fk_asset FOREIGN KEY (asset_id) REFERENCES assets(id)
);

CREATE INDEX idx_telemetry_timestamp ON telemetry_core (timestamp DESC);
CREATE INDEX idx_telemetry_asset_timestamp ON telemetry_core (asset_id, timestamp DESC);
CREATE INDEX idx_telemetry_raw_storage ON telemetry_core (raw_storage_bucket, raw_storage_key);
-- TimescaleDB hypertable
SELECT create_hypertable('telemetry_core', 'timestamp');
```

2. **AWS S3 Raw Storage Structure:**

```
s3://fleeti-raw-telemetry/
  {provider}/
    {year}/
      {month}/
        {day}/
          {asset_id}/
            {timestamp}-{packet_id}.json
```

**AWS S3 Configuration:**

- **Storage Class:** Standard for recent data (0-30 days), Intelligent-Tiering for 30-90 days, Glacier Instant Retrieval for 90-365 days, Glacier Deep Archive for >365 days
- **Lifecycle Policies:** Automatically transition objects to cheaper storage classes
- **Encryption:** Enable S3 bucket encryption (SSE-S3 or SSE-KMS)
- **Versioning:** Enable versioning for data protection (optional, increases cost)
- **Access Control:** Use IAM policies and bucket policies for access control
- **Cross-Region Replication:** Consider for disaster recovery (optional)

**S3 Lifecycle Policy Example:**

```json
{
  "Rules": [
    {
      "Id": "RawTelemetryLifecycle",
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "INTELLIGENT_TIERING"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER_IR"
        },
        {
          "Days": 365,
          "StorageClass": "DEEP_ARCHIVE"
        }
      ]
    }
  ]
}
```

3. **Recalculation workflow:**

```python
# Pseudocode for historical recalculation (AWS S3)
import boto3

s3_client = boto3.client('s3')

def recalculate_historical_field(new_field_name, calculation_rule, config_version):
    # Query all raw storage keys from telemetry_core
    raw_keys = db.query("""
        SELECT DISTINCT raw_storage_key, raw_storage_bucket, asset_id, timestamp
        FROM telemetry_core
        WHERE timestamp >= :start_date
        ORDER BY timestamp
    """)
    
    for raw_key in raw_keys:
        # Fetch raw packet from AWS S3
        try:
            response = s3_client.get_object(
                Bucket=raw_key.bucket,
                Key=raw_key.key
            )
            raw_packet = json.loads(response['Body'].read())
        except s3_client.exceptions.NoSuchKey:
            # Handle missing object (may be in Glacier, need restore)
            logger.warning(f"Object {raw_key.key} not found, may need Glacier restore")
            continue
        
        # Apply new transformation rule
        new_field_value = apply_transformation(raw_packet, calculation_rule, config_version)
        
        # Update extended_data JSONB column
        db.execute("""
            UPDATE telemetry_core
            SET extended_data = jsonb_set(
                extended_data,
                '{new_field_path}',
                :new_value::jsonb
            ),
            transformation_metadata = jsonb_set(
                transformation_metadata,
                '{fields_used,new_field_name}',
                jsonb_build_object(
                    'provider_field', :provider_field_used,
                    'config_version', :config_version,
                    'calculated_at', :now
                )
            )
            WHERE raw_storage_key = :raw_key
        """, ...)
```

**AWS-Specific Considerations for Recalculation:**

- **Glacier Restore:** If objects are in Glacier, initiate restore job first (takes 1-5 minutes for Instant Retrieval, hours for Deep Archive)
- **S3 Batch Operations:** Use S3 Batch Operations for large-scale recalculation jobs (process millions of objects)
- **Lambda Functions:** Use AWS Lambda for parallel recalculation processing
- **Step Functions:** Use AWS Step Functions to orchestrate complex recalculation workflows
- **Cost Optimization:** Use S3 Select to query JSON objects without downloading full files (if querying specific fields)

**Key Points:**
- **Every transformed record must store** `raw_storage_key` and `raw_storage_bucket`
- Use **consistent naming convention** for raw storage paths
- Consider **partitioning raw storage** by date/provider for efficient scanning
- **Index `raw_storage_key`** for fast lookup during recalculation

#### Specific Technology Recommendation: TimescaleDB on AWS

**✅ Use TimescaleDB (PostgreSQL extension) for core storage on AWS.**

**AWS Deployment Options:**

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| **RDS PostgreSQL + TimescaleDB Extension** | ✅ Managed service<br>✅ Automatic backups<br>✅ High availability | ⚠️ Extension support varies by RDS version<br>⚠️ May need to enable extension manually | **CHECK AVAILABILITY** |
| **Aurora PostgreSQL + TimescaleDB** | ✅ Serverless scaling<br>✅ Multi-AZ by default<br>✅ Better performance | ⚠️ Extension support unclear<br>⚠️ Higher cost | **INVESTIGATE** |
| **Self-Managed on EC2** | ✅ Full control<br>✅ Latest TimescaleDB version<br>✅ All features available | ❌ Operational overhead<br>❌ Need to manage backups/HA | **RECOMMENDED IF RDS NOT SUPPORTED** |
| **AWS Timestream** | ✅ Fully managed<br>✅ Purpose-built for time-series<br>✅ Serverless<br>✅ Automatic scaling | ❌ No JSONB support (can't store extended fields easily)<br>❌ Different query language (SQL-like but different)<br>❌ Migration complexity<br>❌ Would require separate storage for extended fields | **NOT RECOMMENDED** (loses JSONB capability, requires dual storage) |

**Note on AWS Timestream:**
While AWS Timestream is purpose-built for time-series data, it **cannot replace** the PostgreSQL + JSONB approach because:
- Timestream doesn't support JSONB columns for extended fields
- You would need **two storage systems** (Timestream for core + DynamoDB/S3 for extended)
- This adds complexity and breaks the single-query advantage
- **Exception:** Consider Timestream ONLY if you're willing to store extended fields separately and accept dual-query complexity

**Recommended Approach for AWS:**

1. **First Choice: RDS PostgreSQL with TimescaleDB Extension**
   - Check if your RDS PostgreSQL version supports TimescaleDB extension
   - If supported: Use RDS for managed PostgreSQL with TimescaleDB
   - Enable extension: `CREATE EXTENSION IF NOT EXISTS timescaledb;`
   - Benefits: Managed service, automatic backups, Multi-AZ support

2. **Fallback: Self-Managed TimescaleDB on EC2**
   - If RDS doesn't support TimescaleDB extension, deploy on EC2
   - Use EC2 Auto Scaling Groups for high availability
   - Use EBS volumes with snapshots for backups
   - Consider AWS Systems Manager for patching and maintenance

3. **Alternative: Aurora PostgreSQL (Investigate)**
   - Check if Aurora PostgreSQL supports TimescaleDB extension
   - If supported, Aurora provides better performance and scaling
   - Higher cost but better operational characteristics

**Why TimescaleDB over vanilla PostgreSQL:**

1. **Time-series optimization:**
   - Automatic partitioning by time (hypertables)
   - Compression for older data (reduce storage costs)
   - Continuous aggregates (pre-computed aggregations)

2. **Query performance:**
   - Time-based queries are **10-100x faster** than PostgreSQL
   - Efficient time-range queries for historical data
   - Automatic query optimization for time-series patterns

3. **Operational benefits:**
   - Data retention policies (auto-delete old data)
   - Background jobs for maintenance
   - Native support for downsampling

**AWS-Specific Considerations:**
- Use **RDS Multi-AZ** for high availability (if using RDS)
- Use **RDS Read Replicas** for read scaling
- Use **EBS gp3 volumes** for EC2 deployments (better performance/cost)
- Use **CloudWatch** for monitoring database metrics
- Use **AWS Backup** for automated backup management
- Consider **AWS Secrets Manager** for database credentials

**Schema Design Considerations:**

```sql
-- Core telemetry table with TimescaleDB
CREATE TABLE telemetry_core (
    telemetry_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    asset_id UUID NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    
    -- Root-level metadata
    last_updated_at BIGINT NOT NULL, -- Unix epoch milliseconds
    
    -- Location (core)
    location_lat DECIMAL(10, 8),
    location_lng DECIMAL(11, 8),
    location_heading SMALLINT, -- 0-359
    location_altitude INTEGER, -- meters
    
    -- Motion (core)
    motion_speed_kmh DECIMAL(5, 2),
    motion_is_moving BOOLEAN,
    
    -- Status (core) - computed fields
    status_top_status_family VARCHAR(50), -- 'connectivity', 'transit', etc.
    status_top_status_code VARCHAR(50), -- 'online', 'in_transit', etc.
    status_top_status_changed_at BIGINT, -- Unix epoch milliseconds
    
    -- Power (core)
    power_ignition BOOLEAN,
    power_ignition_changed_at BIGINT,
    
    -- Counters (core)
    counters_odometer_km DECIMAL(10, 2),
    counters_engine_hours_h DECIMAL(8, 2),
    
    -- Fuel (core) - if available
    fuel_level_percent SMALLINT, -- 0-100
    fuel_level_liters DECIMAL(6, 2),
    
    -- Connectivity (core)
    connectivity_signal_level SMALLINT, -- 0-31
    
    -- Device health (core)
    device_battery_level SMALLINT, -- 0-100
    
    -- Raw storage linkage
    raw_storage_key VARCHAR(500),
    raw_storage_bucket VARCHAR(100),
    provider_name VARCHAR(50),
    provider_packet_id VARCHAR(255),
    
    -- Extended data (all other fields)
    extended_data JSONB DEFAULT '{}'::jsonb,
    
    -- Transformation metadata (CRITICAL - see Section 2.5)
    transformation_metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Indexes
    CONSTRAINT fk_asset FOREIGN KEY (asset_id) REFERENCES assets(id)
);

-- Create TimescaleDB hypertable
SELECT create_hypertable('telemetry_core', 'timestamp',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- Indexes for common queries
CREATE INDEX idx_telemetry_asset_timestamp ON telemetry_core (asset_id, timestamp DESC);
CREATE INDEX idx_telemetry_status ON telemetry_core (status_top_status_family, status_top_status_code);
CREATE INDEX idx_telemetry_location ON telemetry_core USING GIST (
    ll_to_earth(location_lat, location_lng)
); -- For geospatial queries

-- JSONB indexes for extended data
CREATE INDEX idx_telemetry_extended_sensors ON telemetry_core USING GIN (
    (extended_data->'sensors')
);
CREATE INDEX idx_telemetry_extended_diagnostics ON telemetry_core USING GIN (
    (extended_data->'diagnostics')
);

-- Compression policy (TimescaleDB) - compress data older than 30 days
SELECT add_compression_policy('telemetry_core', INTERVAL '30 days');
```

---

### 2.2 Frontend WebSocket Optimization

#### What Exact Fields Should Be in Core/Hot Storage?

**🔴 CRITICAL: Define exact field list now.**

Based on your schema specification and use cases, here's the **recommended core field set** for WebSocket/map display:

**Core Fields for Hot Storage (Relational Columns):**

```typescript
interface CoreTelemetryFields {
  // Metadata
  telemetry_id: string;
  asset_id: string;
  timestamp: number; // Unix epoch milliseconds
  last_updated_at: number; // Unix epoch milliseconds
  
  // Location (P0)
  location_lat: number;
  location_lng: number;
  location_heading: number; // 0-359
  location_cardinal_direction: string; // Computed: N, NE, E, etc.
  
  // Motion (P0)
  motion_speed_kmh: number;
  motion_is_moving: boolean;
  
  // Status (P0) - Computed
  status_top_status_family: string; // 'connectivity' | 'immobilization' | 'engine' | 'transit'
  status_top_status_code: string; // 'online' | 'offline' | 'in_transit' | 'parked' | etc.
  status_top_status_changed_at: number; // Unix epoch milliseconds
  
  // Status array (simplified for core) - store as JSONB array
  status_statuses: Array<{
    family: string;
    code: string;
    last_changed_at: number;
  }>;
  
  // Power (BL → but needed for status computation, expose computed status)
  // Note: power_ignition itself is BL, but status derived from it is P0
  
  // Connectivity (P1 for WebSocket)
  connectivity_signal_level: number; // 0-31
  
  // Fuel (P1) - if available
  fuel_level_percent: number | null; // 0-100
  fuel_level_liters: number | null;
  
  // Counters (P1)
  counters_odometer_km: number | null;
  counters_engine_hours_h: number | null;
  
  // Device health (P1)
  device_battery_level: number | null; // 0-100
}
```

**Total: ~25-30 core fields** (not 50 - be more selective)

**Fields NOT in core (move to extended):**
- All sensor data (temperature, humidity) → Extended
- All diagnostics (CAN data, engine details) → Extended
- All I/O states → Extended (BL fields)
- Geofences (computed server-side, not stored in telemetry)
- Trip details (computed/aggregated, not raw telemetry)
- Driver information → Separate service/table

#### How to Structure WebSocket Payload?

**✅ Use optimized payload structure, NOT full telemetry objects.**

**Problem with sending full telemetry objects:**
- Too much data (bandwidth waste)
- Includes fields not needed for map/list
- Includes computed fields that frontend doesn't need

**Recommended WebSocket Payload Structure:**

```typescript
// WebSocket message format
interface WebSocketTelemetryUpdate {
  type: 'telemetry_update' | 'status_change' | 'location_update';
  asset_id: string;
  timestamp: number; // Unix epoch milliseconds
  
  // Only changed fields (delta updates)
  delta: {
    location?: {
      lat: number;
      lng: number;
      heading?: number;
    };
    status?: {
      top_status: {
        family: string;
        code: string;
        last_changed_at: number;
      };
    };
    motion?: {
      speed_kmh?: number;
      is_moving?: boolean;
    };
    fuel?: {
      level_percent?: number;
    };
    // ... other changed fields
  };
}

// Full snapshot (sent on connection or request)
interface WebSocketTelemetrySnapshot {
  type: 'telemetry_snapshot';
  assets: Array<{
    asset_id: string;
    asset_name: string; // From asset service
    asset_type: number; // From asset service
    location: {
      lat: number;
      lng: number;
      heading: number;
    };
    status: {
      top_status: {
        family: string;
        code: string;
        last_changed_at: number;
      };
    };
    motion: {
      speed_kmh: number;
      is_moving: boolean;
    };
    fuel?: {
      level_percent: number;
    };
    last_updated_at: number;
  }>;
}
```

**Optimization Strategies:**

1. **Delta Updates Only:**
   - Send only changed fields, not full objects
   - Reduces bandwidth by 70-90%
   - Frontend merges delta into local state

2. **Throttling:**
   - Don't send updates faster than frontend can render (e.g., max 1 update/second per asset)
   - Batch multiple asset updates into single WebSocket message
   - Use debouncing for high-frequency fields (location)

3. **Field Selection:**
   - WebSocket exposes **only core fields**
   - If frontend needs extended fields → use REST API for asset detail view

4. **Compression:**
   - Use WebSocket per-message compression (RFC 7692)
   - Reduces bandwidth by 60-80% for JSON payloads

#### Should WebSocket Allow Field Selection?

**✅ NO - Keep it simple.**

**Recommendation:** WebSocket should **only expose core fields** for map/list display. No field selection parameter.

**Rationale:**
- **Simplicity:** WebSocket protocol should be predictable
- **Performance:** Field selection adds query complexity
- **Use Case Separation:**
  - WebSocket = Real-time map/list updates (core fields only)
  - REST API = Asset detail views, historical queries (all fields, field selection)

**If field selection is needed:**
- Use REST API with `?fields=location,speed,fuel` parameter
- Use GraphQL for complex field selection requirements

#### How to Ensure Fast Map Markers and Tracker List Updates?

**Performance Optimization Checklist:**

1. **Database Query Optimization:**
   ```sql
   -- Optimized query for map markers (all assets in viewport)
   SELECT 
       asset_id,
       location_lat,
       location_lng,
       location_heading,
       status_top_status_code,
       motion_speed_kmh,
       last_updated_at
   FROM telemetry_core
   WHERE 
       timestamp > NOW() - INTERVAL '1 hour' -- Only recent data
       AND location_lat BETWEEN :viewport_south AND :viewport_north
       AND location_lng BETWEEN :viewport_west AND :viewport_east
   ORDER BY timestamp DESC
   -- Use materialized view or cache for frequently-accessed viewports
   ```

2. **Caching Strategy (AWS ElastiCache):**
   - **ElastiCache Redis** for current telemetry state (TTL: 30-60 seconds)
   - WebSocket reads from cache, not database
   - Database updates invalidate cache (use Redis pub/sub for cache invalidation)
   - Reduces database load by 80-90%
   - **ElastiCache Configuration:**
     - Use Redis 7.x (latest stable)
     - Enable cluster mode for high availability (if needed)
     - Use ElastiCache for Redis with Multi-AZ for failover
     - Configure automatic failover
     - Use ElastiCache Replication Groups for read scaling

3. **WebSocket Connection Management:**
   - Use **room/channel pattern** (e.g., Socket.IO rooms)
   - Clients subscribe to specific assets or viewports
   - Server only sends updates for subscribed assets
   - Reduces network traffic

4. **Batch Updates:**
   - Send updates in batches (e.g., every 100ms or 10 assets)
   - Reduces WebSocket message overhead
   - Frontend processes batches efficiently

5. **Indexing:**
   - Index on `(asset_id, timestamp DESC)` for latest-per-asset queries
   - Index on `(location_lat, location_lng)` for geospatial queries
   - Consider PostGIS extension for advanced geospatial queries

---

### 2.3 Customer API Design

#### Should Customer API Expose All Fields or Parameterized Subsets?

**✅ YES - Support field selection via query parameter.**

**Recommendation:** Use REST API with `?fields=` parameter for simple cases, GraphQL for complex selection.

**API Design Options:**

| Approach | Pros | Cons | Use Case |
|----------|------|------|----------|
| **REST with `?fields=`** | ✅ Simple to implement<br>✅ Easy to understand<br>✅ Good for common patterns | ⚠️ Limited flexibility<br>⚠️ Verbose for nested fields | **RECOMMENDED for MVP** |
| **GraphQL** | ✅ Maximum flexibility<br>✅ Single endpoint<br>✅ Type-safe queries | ❌ Higher complexity<br>❌ Learning curve<br>❌ Caching challenges | **Consider for Phase 2** |
| **Multiple Endpoints** | ✅ Clear separation<br>✅ Easy to cache | ❌ Many endpoints to maintain<br>❌ Inconsistent patterns | **NOT RECOMMENDED** |

**Recommended REST API Design:**

```http
# Get current telemetry for asset (core fields only)
GET /api/v1/assets/{asset_id}/telemetry/current
→ Returns core fields only

# Get current telemetry with field selection
GET /api/v1/assets/{asset_id}/telemetry/current?fields=location,speed,status,fuel
→ Returns only specified fields

# Get historical telemetry (all fields, or selected)
GET /api/v1/assets/{asset_id}/telemetry/history?start={timestamp}&end={timestamp}&fields=location,speed,fuel

# Get asset detail view (all fields)
GET /api/v1/assets/{asset_id}/telemetry/current?fields=*
→ Returns core + extended fields (merged)
```

**Field Selection Syntax:**

```
?fields=location,speed,status
?fields=location.lat,location.lng,speed,status.top_status
?fields=*  # All fields (core + extended)
```

**Implementation:**

```python
# Pseudocode for field selection
def get_telemetry(asset_id, fields=None):
    # Query core fields (always fast)
    core_query = """
        SELECT 
            telemetry_id,
            asset_id,
            timestamp,
            location_lat,
            location_lng,
            -- ... other core fields
        FROM telemetry_core
        WHERE asset_id = :asset_id
        ORDER BY timestamp DESC
        LIMIT 1
    """
    
    core_data = db.query(core_query, asset_id=asset_id)
    
    # If fields specified, filter response
    if fields:
        if fields == '*':
            # Include extended_data JSONB
            extended_query = """
                SELECT extended_data
                FROM telemetry_core
                WHERE asset_id = :asset_id
                ORDER BY timestamp DESC
                LIMIT 1
            """
            extended_data = db.query(extended_query, asset_id=asset_id)
            return merge_core_and_extended(core_data, extended_data)
        else:
            # Filter to requested fields
            return filter_fields(core_data, fields)
    else:
        # Default: core fields only
        return core_data
```

#### How to Handle Field Selection Across Hot and Warm Storage?

**Single Query Strategy (Recommended):**

Since we're using single database with JSONB, field selection is straightforward:

```sql
-- Query with field selection
SELECT 
    -- Core fields (always selected if requested)
    CASE WHEN 'location' = ANY(:requested_fields) THEN location_lat ELSE NULL END as lat,
    CASE WHEN 'location' = ANY(:requested_fields) THEN location_lng ELSE NULL END as lng,
    
    -- Extended fields (selectively)
    CASE 
        WHEN 'sensors' = ANY(:requested_fields) 
        THEN extended_data->'sensors' 
        ELSE NULL 
    END as sensors,
    
    CASE 
        WHEN 'diagnostics' = ANY(:requested_fields) 
        THEN extended_data->'diagnostics' 
        ELSE NULL 
    END as diagnostics
    
FROM telemetry_core
WHERE asset_id = :asset_id;
```

**Better Approach: Query First, Filter in Application:**

```python
def get_telemetry_with_fields(asset_id, fields):
    # Always fetch core fields (fast, indexed)
    core_data = db.query("""
        SELECT *
        FROM telemetry_core
        WHERE asset_id = :asset_id
        ORDER BY timestamp DESC
        LIMIT 1
    """, asset_id=asset_id)
    
    # Fetch extended_data only if needed
    if needs_extended_fields(fields):
        extended_data = core_data['extended_data']
    else:
        extended_data = {}
    
    # Merge and filter in application layer
    merged = merge_core_extended(core_data, extended_data)
    filtered = filter_by_fields(merged, fields)
    
    return filtered
```

**Performance Consideration:**
- If query only requests core fields → Don't access JSONB (fastest)
- If query requests extended fields → Access JSONB (slightly slower, but acceptable)
- Use GIN indexes on frequently-accessed JSONB paths

#### Should Historical Queries Always Merge Hot and Warm?

**✅ NO - Make it configurable.**

**Recommendation:** Support three query modes:

1. **Core Only** (default for time-series):
   ```http
   GET /api/v1/assets/{asset_id}/telemetry/history?start={ts}&end={ts}
   → Returns only core fields (fast, efficient for charts)
   ```

2. **Core + Extended** (for detail views):
   ```http
   GET /api/v1/assets/{asset_id}/telemetry/history?start={ts}&end={ts}&fields=*
   → Returns all fields (slower, but complete)
   ```

3. **Selective Fields** (for specific analysis):
   ```http
   GET /api/v1/assets/{asset_id}/telemetry/history?start={ts}&end={ts}&fields=location,speed,fuel
   → Returns only requested fields
   ```

**Query Optimization:**

```sql
-- Core-only query (fast, uses relational indexes)
SELECT 
    timestamp,
    location_lat,
    location_lng,
    motion_speed_kmh
FROM telemetry_core
WHERE asset_id = :asset_id
    AND timestamp BETWEEN :start AND :end
ORDER BY timestamp ASC;

-- Extended fields query (slower, but flexible)
SELECT 
    timestamp,
    location_lat,
    location_lng,
    extended_data->'sensors' as sensors,
    extended_data->'diagnostics' as diagnostics
FROM telemetry_core
WHERE asset_id = :asset_id
    AND timestamp BETWEEN :start AND :end
ORDER BY timestamp ASC;
```

#### Best API Design Pattern: REST vs GraphQL vs Both?

**✅ Start with REST, consider GraphQL later.**

**Phased Approach:**

**Phase 1 (MVP): REST API**
- Simple to implement
- Easy to understand
- Good enough for 80% of use cases
- Supports field selection via `?fields=` parameter

**Phase 2 (If Needed): Add GraphQL**
- If customers need complex nested queries
- If field selection becomes too complex for REST
- If frontend team requests GraphQL for better type safety

**Recommendation:**
- **Start with REST** - Implement field selection, pagination, filtering
- **Monitor usage patterns** - If queries become complex, add GraphQL endpoint
- **Don't over-engineer** - REST can handle most telemetry API needs

**REST API Structure:**

```
GET  /api/v1/assets/{asset_id}/telemetry/current
GET  /api/v1/assets/{asset_id}/telemetry/history
GET  /api/v1/assets/{asset_id}/telemetry/current?fields=location,speed
POST /api/v1/assets/{asset_id}/telemetry/query  # For complex queries
```

---

### 2.4 Internal/Troubleshooting API Design

#### Separate Endpoint vs Debug Parameter?

**✅ Use same API with `?debug=true` parameter + separate endpoint for raw data.**

**Recommended Approach:**

1. **Same API with debug parameter** for transformed telemetry with metadata:
   ```http
   GET /api/v1/assets/{asset_id}/telemetry/current?debug=true
   → Returns normal telemetry + transformation metadata + T-priority fields
   ```

2. **Separate endpoint** for raw provider data:
   ```http
   GET /api/v1/internal/assets/{asset_id}/telemetry/raw/{telemetry_id}
   → Returns raw provider packet from cold storage
   ```

**Rationale:**
- **Debug parameter** is simpler for common troubleshooting (seeing transformation metadata)
- **Separate endpoint** is clearer for raw data access (different access pattern)
- **Security:** Separate endpoint can have stricter access controls

#### What Additional Fields/Metadata Should Debug Mode Expose?

**Debug Mode Payload Structure:**

```json
{
  "telemetry": {
    // Normal telemetry fields (core + extended)
    "location": { "lat": 5.3561, "lng": -4.0083 },
    "status": { "top_status": { "code": "in_transit" } },
    // ... all other fields
  },
  
  "debug": {
    "transformation_metadata": {
      "config_version": "1.2.3",
      "config_applied_at": "2025-01-15T10:30:00Z",
      "provider_fields_used": {
        "motion.speed": {
          "source": "can_speed",
          "priority": 1,
          "raw_value": 50.5,
          "transformed_value": 50.5,
          "unit_conversion": null
        },
        "status.top_status": {
          "computed_from": ["power.ignition", "motion.is_moving"],
          "logic": "transit_status_state_machine",
          "previous_state": "parked",
          "transition_reason": "ignition_on"
        }
      }
    },
    
    "raw_storage_reference": {
      "storage_key": "navixy/2025/01/15/asset-123/1234567890-packet-abc.json",
      "storage_bucket": "fleeti-raw-telemetry",
      "provider_packet_id": "packet-abc",
      "retrieved_at": "2025-01-15T10:30:05Z"
    },
    
    "troubleshooting_fields": {
      // T-priority fields
      "location_precision_hdop": 1.2,
      "location_precision_pdop": 1.8,
      "location_precision_satellites": 12,
      "connectivity_cell_id": 12345,
      "connectivity_cell_lac": 678,
      "device_status_bitmap": 12345
    },
    
    "computation_timing": {
      "transformation_duration_ms": 5,
      "status_computation_duration_ms": 2,
      "total_processing_duration_ms": 7
    }
  }
}
```

#### How to Expose Raw Provider Data?

**Separate Endpoint for Raw Data:**

```http
GET /api/v1/internal/assets/{asset_id}/telemetry/raw/{telemetry_id}
```

**Response:**
```json
{
  "telemetry_id": "uuid",
  "raw_packet": {
    // Original provider JSON packet
    "lat": 5.3561,
    "lng": -4.0083,
    "can_speed": 50.5,
    "avl_io_239": 1,
    // ... all provider fields
  },
  "provider": "navixy",
  "received_at": "2025-01-15T10:30:00Z",
  "storage_location": {
    "bucket": "fleeti-raw-telemetry",
    "key": "navixy/2025/01/15/asset-123/1234567890-packet-abc.json"
  },
  "transformed_telemetry_id": "uuid", // Link back to transformed record
}
```

**Access Control:**
- Requires `super_admin` role
- Audit log all raw data access
- Rate limit to prevent abuse

#### Should Debug Mode Include Transformation Metadata?

**✅ YES - This is critical for troubleshooting.**

**Transformation Metadata Structure:**

Store in `transformation_metadata` JSONB column:

```json
{
  "config_version": "1.2.3",
  "config_applied_at": "2025-01-15T10:30:00Z",
  "config_hierarchy": [
    { "level": "default", "config_id": "default-v1" },
    { "level": "customer", "config_id": "customer-abc-v2" },
    { "level": "asset", "config_id": "asset-123-v1" }
  ],
  "fields_used": {
    "motion.speed": {
      "source": "can_speed",
      "priority": 1,
      "raw_value": 50.5,
      "unit": "km/h",
      "transformation": null,
      "fallback_used": false
    },
    "power.ignition": {
      "source": "avl_io_898",
      "priority": 1,
      "raw_value": 1,
      "transformation": null,
      "fallback_used": false
    },
    "fuel.level_liters": {
      "source": "can_fuel_1",
      "priority": 1,
      "raw_value": 75,
      "unit": "%",
      "transformation": {
        "type": "static_field_calculation",
        "formula": "(raw_value / 100) * static.tank_capacity_liters",
        "static_fields_used": {
          "tank_capacity_liters": 120
        },
        "result": 90
      }
    }
  },
  "computed_fields": {
    "status.top_status": {
      "computed_from": ["power.ignition", "motion.is_moving", "connectivity.online"],
      "logic": "status_computation_engine",
      "result": {
        "family": "transit",
        "code": "in_transit",
        "reason": "ignition_on_and_moving"
      }
    }
  }
}
```

**Storage Strategy:**
- Store in `transformation_metadata` JSONB column
- Index frequently-queried paths (e.g., `config_version`)
- Consider separate table for config versions (see Section 2.5)

---

### 2.5 Historical Mapping Consultation

**🔴 CRITICAL SECTION - This is the biggest gap in the current spec.**

#### How to Store and Expose Mapping/Transformation Metadata?

**Recommended Storage Strategy:**

**Option 1: Store with Each Record (Recommended)**

Store transformation metadata in `transformation_metadata` JSONB column on every telemetry record:

```sql
CREATE TABLE telemetry_core (
    -- ... other columns ...
    transformation_metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Index for config version queries
    CREATE INDEX idx_transformation_config_version ON telemetry_core (
        (transformation_metadata->>'config_version')
    );
);
```

**Pros:**
- ✅ Always available with record
- ✅ No additional queries needed
- ✅ Historical records include their transformation context
- ✅ Simple to query

**Cons:**
- ⚠️ Storage overhead (~500-1000 bytes per record)
- ⚠️ JSONB column grows over time

**Verdict: ✅ RECOMMENDED** - Storage overhead is acceptable for traceability benefits.

**Option 2: Separate Metadata Table (Alternative)**

```sql
CREATE TABLE telemetry_transformation_metadata (
    telemetry_id UUID PRIMARY KEY,
    config_version VARCHAR(50),
    config_applied_at TIMESTAMPTZ,
    fields_used JSONB,
    FOREIGN KEY (telemetry_id) REFERENCES telemetry_core(telemetry_id)
);
```

**Pros:**
- ✅ Cleaner separation
- ✅ Can query metadata independently

**Cons:**
- ❌ Requires JOIN for every query
- ❌ More complex queries
- ❌ Risk of orphaned records

**Verdict: ❌ NOT RECOMMENDED** - Overhead of JOINs outweighs benefits.

#### How to Ensure Traceability?

**Three-Level Traceability:**

1. **Fleeti Telemetry → Provider Raw Data:**
   ```sql
   SELECT 
       t.telemetry_id,
       t.location_lat,
       t.raw_storage_key,
       t.raw_storage_bucket,
       t.provider_name
   FROM telemetry_core t
   WHERE t.telemetry_id = :telemetry_id;
   ```
   - Every record stores `raw_storage_key` and `raw_storage_bucket`
   - Direct link to raw provider packet

2. **Fleeti Telemetry → Transformation Rules:**
   ```sql
   SELECT 
       t.telemetry_id,
       t.transformation_metadata->>'config_version' as config_version,
       t.transformation_metadata->'fields_used' as fields_used
   FROM telemetry_core t
   WHERE t.telemetry_id = :telemetry_id;
   ```
   - `transformation_metadata` stores config version and fields used

3. **Config Version → Actual Configuration:**
   ```sql
   -- Separate table for config versions (immutable)
   CREATE TABLE telemetry_config_versions (
       config_version VARCHAR(50) PRIMARY KEY,
       config_yaml TEXT, -- Full YAML config
       created_at TIMESTAMPTZ,
       created_by VARCHAR(100)
   );
   ```
   - Store all config versions in separate table
   - Immutable (never update, only insert new versions)
   - Enables historical recalculation with exact config

**Complete Traceability Query:**

```sql
-- Get full traceability for a telemetry record
SELECT 
    t.telemetry_id,
    t.asset_id,
    t.timestamp,
    
    -- Transformed Fleeti telemetry
    t.location_lat,
    t.motion_speed_kmh,
    
    -- Transformation metadata
    t.transformation_metadata->>'config_version' as config_version,
    t.transformation_metadata->'fields_used'->'motion.speed' as speed_field_metadata,
    
    -- Raw storage reference
    t.raw_storage_key,
    t.raw_storage_bucket,
    t.provider_name,
    
    -- Config version details
    cv.config_yaml as config_used
    
FROM telemetry_core t
LEFT JOIN telemetry_config_versions cv 
    ON cv.config_version = t.transformation_metadata->>'config_version'
WHERE t.telemetry_id = :telemetry_id;
```

#### Best Way to Query Historical Records with Mapping Metadata?

**API Endpoint for Historical Mapping Consultation:**

```http
GET /api/v1/internal/assets/{asset_id}/telemetry/{telemetry_id}/traceability
```

**Response:**
```json
{
  "telemetry_id": "uuid",
  "timestamp": 1234567890000,
  
  "fleeti_telemetry": {
    "location": { "lat": 5.3561, "lng": -4.0083 },
    "motion": { "speed_kmh": 50.5 },
    "status": { "top_status": { "code": "in_transit" } }
  },
  
  "transformation_metadata": {
    "config_version": "1.2.3",
    "config_applied_at": "2025-01-15T10:30:00Z",
    "fields_used": {
      "motion.speed": {
        "source": "can_speed",
        "priority": 1,
        "raw_value": 50.5,
        "provider_field_path": "params.can_speed"
      },
      "status.top_status": {
        "computed_from": ["power.ignition", "motion.is_moving"],
        "logic": "transit_status_state_machine"
      }
    }
  },
  
  "raw_provider_data": {
    "storage_key": "navixy/2025/01/15/asset-123/1234567890-packet-abc.json",
    "provider": "navixy",
    "raw_packet": {
      // Original provider JSON
    }
  },
  
  "config_used": {
    "version": "1.2.3",
    "yaml": "# Full config YAML...",
    "created_at": "2025-01-10T00:00:00Z"
  }
}
```

**Query Optimization:**
- Index `transformation_metadata->>'config_version'` for fast config version lookups
- Cache config versions in memory (rarely change)
- Use materialized views for common traceability queries

---

### 2.6 Developer Guidance

#### How to Specify Requirements Without Implementation Details?

**Product Specification Structure:**

**✅ DO Specify (Product Requirements):**

1. **Functional Requirements:**
   - What data must be stored (core vs extended fields)
   - What queries must be supported (current state, historical range, etc.)
   - What APIs must be exposed (REST endpoints, WebSocket events)
   - What performance requirements (latency, throughput)

2. **Data Requirements:**
   - Exact core field list (see Section 2.2)
   - Field priorities (P0, P1, P2, T, BL)
   - Data retention policies (how long to keep raw/core/extended)
   - Data access patterns (read-heavy, write-heavy, query patterns)

3. **Performance Requirements:**
   - Latency targets (WebSocket updates < 100ms, API queries < 500ms)
   - Throughput targets (X messages/second ingestion, Y concurrent WebSocket connections)
   - Query patterns (time-range queries, latest-per-asset, geospatial)

4. **Non-Functional Requirements:**
   - Traceability requirements (must link to raw data, config version)
   - Audit requirements (who accessed what, when)
   - Security requirements (access control, data encryption)

**❌ DON'T Specify (Implementation Details):**

1. **Database Choice:**
   - Don't specify "use PostgreSQL" → Specify "relational database with JSONB support"
   - Let architects choose PostgreSQL vs other options

2. **Index Strategy:**
   - Don't specify exact indexes → Specify query performance requirements
   - Let DBAs design indexes based on actual query patterns

3. **Caching Strategy:**
   - Don't specify "use Redis" → Specify "cache current state for fast WebSocket access"
   - Let architects choose caching solution

4. **API Framework:**
   - Don't specify "use Express.js" → Specify API contract (endpoints, request/response formats)
   - Let developers choose framework

**Example Product Specification:**

```markdown
## Core Telemetry Storage Requirements

### Functional Requirements
- Must store latest telemetry state for each asset (for WebSocket updates)
- Must support historical queries with time-range filtering
- Must support field selection in API responses
- Must link to raw provider data for traceability

### Data Requirements
- Core fields: [exact list from Section 2.2]
- Extended fields: All other fields in JSONB column
- Raw storage: Link via raw_storage_key column
- Transformation metadata: Store config version and fields used

### Performance Requirements
- WebSocket updates: < 100ms latency from database to client
- API queries (current state): < 200ms p95 latency
- API queries (historical, 1 day): < 500ms p95 latency
- Ingestion throughput: Support 10,000 messages/second
- Concurrent WebSocket connections: Support 1,000 connections

### Query Patterns
- Latest telemetry per asset (for WebSocket)
- Time-range queries for historical data
- Geospatial queries (assets in viewport)
- Field selection queries (core only, extended only, or both)

### Non-Functional Requirements
- Traceability: Every transformed record must link to raw provider data
- Audit: Log all API access (who, what, when)
- Data retention: Raw data permanent, core/extended configurable
```

#### Performance Requirements to Specify

**Recommended Performance Targets:**

1. **WebSocket Latency:**
   - Database query: < 50ms (p95)
   - Total round-trip (DB → WebSocket → Client): < 100ms (p95)

2. **API Query Latency:**
   - Current state query: < 200ms (p95)
   - Historical query (1 day range): < 500ms (p95)
   - Historical query (1 month range): < 2000ms (p95)

3. **Ingestion Throughput:**
   - Message ingestion: 10,000 messages/second (sustained)
   - Peak ingestion: 50,000 messages/second (burst)

4. **Concurrent Connections:**
   - WebSocket connections: 1,000 concurrent
   - API requests: 100 requests/second per customer

5. **Storage Performance:**
   - Write latency: < 10ms (p95) for core + extended storage
   - Read latency: < 50ms (p95) for core fields
   - Read latency: < 200ms (p95) for core + extended fields

**Query Pattern Requirements:**

```markdown
## Required Query Patterns

1. **Latest Telemetry Per Asset:**
   - Query: Get most recent telemetry for N assets
   - Performance: < 100ms for 100 assets
   - Frequency: High (WebSocket updates)

2. **Time-Range Historical:**
   - Query: Get telemetry for asset in time range
   - Performance: < 500ms for 1 day, < 2000ms for 1 month
   - Frequency: Medium (API queries)

3. **Geospatial (Viewport):**
   - Query: Get assets in geographic bounding box
   - Performance: < 200ms for viewport query
   - Frequency: Medium (Map viewport updates)

4. **Field Selection:**
   - Query: Get specific fields (core or extended)
   - Performance: Core fields < 200ms, Extended fields < 500ms
   - Frequency: Medium (API queries)
```

---

## 3. Recommended Architecture

### 3.1 Proposed Storage Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Data Ingestion Layer                         │
│  (Data Forwarding from Navixy/OEM → Transformation Pipeline)    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────┐
        │     Transformation Engine              │
        │  - Apply config rules                  │
        │  - Compute status                      │
        │  - Transform fields                    │
        │  - Generate metadata                   │
        └────────────┬───────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌───────────────┐       ┌──────────────────────────┐
│ Raw Storage   │       │   Core + Extended DB     │
│ (Cold)        │       │   (TimescaleDB)          │
│               │       │                          │
│ S3/Azure Blob │       │  ┌────────────────────┐  │
│ - Original    │       │  │ Core Fields        │  │
│   provider    │◄──────┤  │ (Relational)       │  │
│   packets     │       │  │ - location_*       │  │
│ - Permanent   │       │  │ - motion_*         │  │
│   retention   │       │  │ - status_*         │  │
│               │       │  │ - raw_storage_key  │  │
│               │       │  └────────────────────┘  │
│               │       │  ┌────────────────────┐  │
│               │       │  │ Extended Fields    │  │
│               │       │  │ (JSONB)            │  │
│               │       │  │ - sensors          │  │
│               │       │  │ - diagnostics      │  │
│               │       │  │ - ...              │  │
│               │       │  └────────────────────┘  │
│               │       │  ┌────────────────────┐  │
│               │       │  │ Transformation     │  │
│               │       │  │ Metadata (JSONB)   │  │
│               │       │  │ - config_version   │  │
│               │       │  │ - fields_used      │  │
│               │       │  └────────────────────┘  │
│               │       └──────────────────────────┘
│               │
└───────────────┘
```

### 3.2 API Design Recommendations

```
┌─────────────────────────────────────────────────────────────┐
│                    Consumption Layer                         │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────────┐  ┌──────────────────┐
│  WebSocket   │    │  Customer API    │  │  Internal API    │
│  (Real-time) │    │  (REST/GraphQL)  │  │  (Debug/Troubleshoot)│
│              │    │                  │  │                  │
│ - Core fields│    │ - Field selection│  │ - Raw data       │
│ - Delta      │    │ - Historical     │  │ - Metadata       │
│ - Batched    │    │ - Time-series    │  │ - Traceability   │
└──────────────┘    └──────────────────┘  └──────────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   TimescaleDB     │
                    │   (Hot + Warm)    │
                    └───────────────────┘
```

### 3.3 Data Flow Diagrams

**Ingestion Flow (AWS-Specific):**
```
Provider (Navixy/OEM)
    ↓ [Data Forwarding]
AWS Kinesis Data Streams / SQS
    ↓
ECS/EKS Transformation Service (Lambda or Container)
    ├─→ Apply Config Rules
    ├─→ Compute Status
    ├─→ Transform Fields
    └─→ Generate Metadata
    ↓
Parallel Write:
    ├─→ AWS S3 [Cold Storage]
    │   └─→ Lifecycle policies → Glacier for archival
    └─→ RDS PostgreSQL/TimescaleDB [Hot + Warm]
        ├─→ Core Fields (Columns)
        ├─→ Extended Fields (JSONB)
        └─→ Metadata (JSONB)
    ↓
Update ElastiCache (Redis) [Current State Cache]
```

**AWS Services for Ingestion:**

- **Kinesis Data Streams:** Real-time streaming ingestion (recommended for high volume)
- **SQS:** Simple queue service (alternative for lower volume or batch processing)
- **Lambda:** Serverless transformation (good for low-medium volume)
- **ECS/EKS:** Container-based transformation (better for high volume, complex processing)
- **EventBridge:** Event routing and scheduling (for batch recalculation jobs)

**Query Flow (AWS-Specific):**
```
Client Request
    ↓
AWS API Gateway / Application Load Balancer
    ↓
ECS/EKS Service (WebSocket Server / API Server)
    ↓
Query Layer
    ├─→ Cache Check (ElastiCache Redis) [if current state]
    ├─→ Database Query (RDS PostgreSQL/TimescaleDB or EC2)
    │   ├─→ Core Fields (fast)
    │   └─→ Extended Fields (JSONB, if needed)
    └─→ Merge & Filter
    ↓
Response to Client
```

**AWS Services Integration:**

- **API Gateway:** REST API endpoints, WebSocket API for real-time connections
- **Application Load Balancer:** Load balancing for ECS/EKS services
- **ElastiCache (Redis):** Caching layer for current telemetry state
- **RDS PostgreSQL/TimescaleDB:** Primary database (or EC2 for self-managed)
- **CloudWatch:** Monitoring and logging
- **X-Ray:** Distributed tracing for debugging

---

## 4. Implementation Guidance

### 4.1 Product-Level Specifications

**What to Specify to Developers:**

1. **Database Schema Requirements:**
   - Exact core field list (relational columns)
   - JSONB structure for extended fields
   - Required indexes for performance
   - Raw storage linkage columns

2. **API Contract:**
   - REST endpoint definitions
   - WebSocket message formats
   - Request/response schemas
   - Error handling

3. **Performance Targets:**
   - Latency requirements
   - Throughput requirements
   - Query pattern requirements

4. **Data Requirements:**
   - Field priorities
   - Data retention policies
   - Traceability requirements

**What to Leave to Implementation:**
- Specific database technology (PostgreSQL vs others)
- Index optimization strategies
- Caching implementation details
- Code organization/structure

### 4.2 Performance Requirements

See Section 2.6 for detailed performance requirements.

### 4.3 Migration Considerations

**If Starting Fresh:**
- Use TimescaleDB from day one
- No migration needed

**If Migrating from Existing System:**
- Plan phased migration:
  1. Set up new storage architecture
  2. Dual-write to old and new systems
  3. Migrate historical data incrementally
  4. Switch reads to new system
  5. Deprecate old system

---

## 5. Open Questions & Risks

### 5.1 Remaining Uncertainties (RESOLVED)

#### 1. Volume Estimates ✅

**Current State:**
- **Assets:** 20,000 assets
- **Messages per asset per day:** 500 messages/day
- **Total daily messages:** 20,000 × 500 = **10,000,000 messages/day**
- **Messages per second:** ~116 messages/second (peak may be higher)

**Growth Projection:**
- **Year 1-5 growth:** 10,000+ assets per year
- **Year 5 target:** 100,000 assets
- **Year 5 daily messages:** 100,000 × 500 = **50,000,000 messages/day**
- **Year 5 messages per second:** ~579 messages/second (peak may be 2-3x higher)

**Capacity Planning Analysis:**

**Ingestion Throughput:**
- **Today:** ~116 msg/sec = **418,000 msg/hour** (well within Kinesis Data Streams capacity)
- **Year 5:** ~579 msg/sec = **2,084,400 msg/hour** (need 2-3 Kinesis shards)
- **Kinesis Shard Capacity:** 1,000 records/second or 1 MB/second
  - Today: Need 1-2 shards (safe margin)
  - Year 5: Need 2-3 shards (depending on message size)

**Recommendation:** Start with 2 Kinesis shards, auto-scale based on metrics.

#### 2. Query Patterns ✅

**Extended Fields Usage:**
- **API queries:** 100% require extended fields ⚠️ **CRITICAL IMPLICATION**
- **WebSocket queries:** 40% require extended fields

**Analysis:**
- **100% API queries need extended fields** means JSONB performance is **critical**
- Single-database approach (core + extended in same DB) is **essential** - can't avoid JSONB queries
- Need to optimize JSONB query performance from day one
- Consider materialized views or pre-computed aggregations for common API queries

**Historical Query Patterns:**
- **Query frequency:** 5 queries/hour (per customer? or total?)
- **Time range:** 5:00 - 19:00 CET (14 hours active period)
- **Total daily historical queries:** ~70 queries during business hours (if per customer, multiply by customer count)

**Implications:**
- Historical queries are relatively infrequent (not a bottleneck)
- Time-range queries (14 hours) are manageable with proper indexing
- Focus optimization on API queries (100% need extended fields)

**Recommendation:**
- Prioritize JSONB query optimization for API endpoints
- Use GIN indexes on frequently-queried JSONB paths
- Consider caching frequently-accessed historical queries

#### 3. Configuration Versioning ⚠️ NEEDS DECISION

**Configuration Change Frequency:**
- **Current estimate:** Once per month
- **Initial phase:** Possibly more frequent (config refinement period)

**Configuration Rollback:**
- **Requirement:** ✅ YES - must support rollback

**Configuration Conflicts:**
- **Status:** ⚠️ Unknown - needs definition

**Recommended Configuration Versioning Strategy:**

1. **Immutable Configuration Versions:**
   ```sql
   CREATE TABLE telemetry_config_versions (
       config_version VARCHAR(50) PRIMARY KEY, -- Semantic version: "1.2.3"
       config_yaml TEXT NOT NULL, -- Full YAML config (immutable)
       config_hash VARCHAR(64) NOT NULL, -- SHA-256 hash for integrity
       created_at TIMESTAMPTZ NOT NULL,
       created_by VARCHAR(100) NOT NULL,
       description TEXT,
       is_active BOOLEAN DEFAULT false, -- Only one active version per scope
       UNIQUE(config_hash) -- Prevent duplicate configs
   );
   ```

2. **Configuration Scope Hierarchy:**
   ```sql
   CREATE TABLE telemetry_config_assignments (
       assignment_id UUID PRIMARY KEY,
       scope_type VARCHAR(20) NOT NULL, -- 'default', 'customer', 'asset_group', 'asset'
       scope_id UUID, -- Customer ID, Asset Group ID, or Asset ID (NULL for default)
       config_version VARCHAR(50) NOT NULL,
       assigned_at TIMESTAMPTZ NOT NULL,
       assigned_by VARCHAR(100) NOT NULL,
       effective_from TIMESTAMPTZ NOT NULL,
       effective_until TIMESTAMPTZ, -- NULL = currently active
       FOREIGN KEY (config_version) REFERENCES telemetry_config_versions(config_version)
   );
   ```

3. **Conflict Resolution Strategy (RECOMMENDED):**
   - **Priority Order:** Asset > Asset Group > Customer > Default (most specific wins)
   - **Validation:** Prevent circular dependencies in asset group hierarchy
   - **Merge Strategy:** Lower-level configs override higher-level configs (field-by-field merge)
   - **Conflict Detection:** Validate configs on assignment, flag conflicts during merge

4. **Rollback Mechanism:**
   ```sql
   -- Rollback to previous config version
   UPDATE telemetry_config_assignments
   SET effective_until = NOW(),
       rolled_back_at = NOW(),
       rolled_back_by = :user_id
   WHERE assignment_id = :current_assignment_id;
   
   -- Activate previous version
   INSERT INTO telemetry_config_assignments (
       scope_type, scope_id, config_version, 
       assigned_at, assigned_by, effective_from
   )
   SELECT 
       scope_type, scope_id, previous_config_version,
       NOW(), :user_id, NOW()
   FROM telemetry_config_assignments
   WHERE assignment_id = :previous_assignment_id;
   ```

**Conflict Resolution Strategy (RECOMMENDED):**

**Approach: Field-Level Override with Priority Hierarchy**

1. **Priority Order (Most Specific Wins):**
   ```
   Asset Config > Asset Group Config > Customer Config > Default Config
   ```

2. **Merge Algorithm:**
   ```yaml
   # Example: Speed field priority
   Default Config:
     motion.speed:
       sources: [can_speed, obd_speed, gps_speed]
   
   Customer Config (overrides default):
     motion.speed:
       sources: [obd_speed, gps_speed]  # CAN not available for this customer
   
   Asset Group Config (overrides customer):
     motion.speed:
       sources: [gps_speed]  # OBD unreliable for this fleet
   
   Asset Config (overrides group):
     motion.speed:
       sources: [can_speed]  # Manual override for this specific asset
   
   Final Result for Asset:
     motion.speed: [can_speed]  # Asset config wins
   ```

3. **Conflict Detection:**
   - **Validation Rules:**
     - Prevent removing all sources (must have at least one fallback)
     - Prevent invalid field references (field must exist in provider catalog)
     - Prevent circular dependencies in asset group hierarchy
     - Warn when lower-level config significantly changes higher-level behavior

4. **Conflict Resolution UI/API:**
   - Show configuration diff when assigning new config
   - Highlight conflicts (field overrides)
   - Allow preview of effective configuration before saving
   - Require explicit confirmation for significant changes

5. **Audit Trail:**
   - Log all configuration changes (who, what, when, why)
   - Track configuration conflicts and resolutions
   - Maintain history of effective configurations per asset

**Example Conflict Resolution:**

```sql
-- Get effective configuration for an asset (with conflict resolution)
CREATE OR REPLACE FUNCTION get_effective_config(asset_uuid UUID)
RETURNS JSONB AS $$
DECLARE
    effective_config JSONB := '{}'::jsonb;
    default_config JSONB;
    customer_config JSONB;
    group_config JSONB;
    asset_config JSONB;
BEGIN
    -- Load configs in priority order (lowest to highest)
    SELECT config_yaml::jsonb INTO default_config
    FROM telemetry_config_assignments tca
    JOIN telemetry_config_versions tcv ON tcv.config_version = tca.config_version
    WHERE tca.scope_type = 'default' AND tca.effective_until IS NULL
    LIMIT 1;
    
    -- Load customer config (if exists)
    SELECT config_yaml::jsonb INTO customer_config
    FROM telemetry_config_assignments tca
    JOIN telemetry_config_versions tcv ON tcv.config_version = tca.config_version
    WHERE tca.scope_type = 'customer' 
        AND tca.scope_id = (SELECT customer_id FROM assets WHERE id = asset_uuid)
        AND tca.effective_until IS NULL
    LIMIT 1;
    
    -- Load asset group config (if exists)
    SELECT config_yaml::jsonb INTO group_config
    FROM telemetry_config_assignments tca
    JOIN telemetry_config_versions tcv ON tcv.config_version = tca.config_version
    WHERE tca.scope_type = 'asset_group'
        AND tca.scope_id = (SELECT group_id FROM assets WHERE id = asset_uuid)
        AND tca.effective_until IS NULL
    LIMIT 1;
    
    -- Load asset config (if exists)
    SELECT config_yaml::jsonb INTO asset_config
    FROM telemetry_config_assignments tca
    JOIN telemetry_config_versions tcv ON tcv.config_version = tca.config_version
    WHERE tca.scope_type = 'asset' 
        AND tca.scope_id = asset_uuid
        AND tca.effective_until IS NULL
    LIMIT 1;
    
    -- Merge configs (higher priority overrides lower priority)
    effective_config := COALESCE(default_config, '{}'::jsonb);
    IF customer_config IS NOT NULL THEN
        effective_config := effective_config || customer_config;  -- JSONB merge (overwrite)
    END IF;
    IF group_config IS NOT NULL THEN
        effective_config := effective_config || group_config;
    END IF;
    IF asset_config IS NOT NULL THEN
        effective_config := effective_config || asset_config;
    END IF;
    
    RETURN effective_config;
END;
$$ LANGUAGE plpgsql;
```

**Action Items:**
- ✅ Define conflict resolution rules: **Field-level override, most specific wins** (recommended above)
- Design configuration validation rules (see Section 7 of spec)
- Implement configuration diff/compare functionality for rollback preview
- Create configuration audit trail (who changed what, when, why)
- Build configuration preview/validation API before activation

#### 4. Raw Storage Cost 📊 CALCULATED

**Storage Size Calculations:**

**Assumptions:**
- Average raw telemetry packet size: **7.5 KB** (JSON packet with ~340 fields)
- Compression ratio (if compressed): ~70% (compressed = 2.25 KB)
- Storage calculation uses **uncompressed** size (raw JSON packets)

**Current State (20,000 assets):**
- Daily messages: 10,000,000
- Daily storage: 10M × 7.5 KB = **75 GB/day**
- Monthly storage: 75 GB × 30 = **2.25 TB/month**
- Annual storage: 2.25 TB × 12 = **27 TB/year**

**Year 5 Projection (100,000 assets):**
- Daily messages: 50,000,000
- Daily storage: 50M × 7.5 KB = **375 GB/day**
- Monthly storage: 375 GB × 30 = **11.25 TB/month**
- Annual storage: 11.25 TB × 12 = **135 TB/year**

**5-Year Accumulation (No Archive):**
- Year 1: 27 TB
- Year 2: 54 TB (cumulative)
- Year 3: 81 TB (cumulative)
- Year 4: 108 TB (cumulative)
- Year 5: 135 TB (cumulative)
- **Total after 5 years: ~405 TB**

**With Lifecycle Policies (Archive after 5 years):**
- **Active storage (last 5 years):** ~135 TB (Year 5 volume)
- **Archived storage (older than 5 years):** Moves to Glacier Deep Archive

**AWS S3 Storage Cost Calculation:**

**Active Storage (Standard S3 - Last 30 days):**
- Month 1-30: 11.25 TB/month × $0.023/GB = **$264/month**

**Intelligent-Tiering (30-90 days):**
- Month 31-90: 11.25 TB × 3 months = 33.75 TB
- Cost: 33.75 TB × $0.023/GB = **$795** (one-time for 3 months, then transitions)

**Glacier Instant Retrieval (90-365 days):**
- Month 91-365: 11.25 TB × 9 months = 101.25 TB (approximately)
- Cost: 101.25 TB × $0.004/GB = **$414** (one-time, then transitions)

**Glacier Deep Archive (>5 years):**
- Older than 5 years: Moves to Deep Archive
- Cost: ~$0.00099/GB/month = **~$10/TB/month** = Very low cost for archival

**Annual Storage Cost Estimate:**

| Storage Class | Data Volume | Cost per GB/month | Monthly Cost | Notes |
|---------------|-------------|-------------------|--------------|-------|
| **S3 Standard (0-30 days)** | 11.25 TB | $0.023 | **$264** | Active, frequently accessed |
| **Intelligent-Tiering (30-90 days)** | ~34 TB | $0.023 | **$795** | Auto-optimizes cost |
| **Glacier Instant Retrieval (90-365 days)** | ~101 TB | $0.004 | **$414** | Rarely accessed, fast restore |
| **Glacier Deep Archive (>5 years)** | Growing | $0.00099 | **~$10/TB** | Permanent archive |
| **Total Active (Year 5)** | ~135 TB | Mixed | **~$1,473/month** | Estimated |

**Total Annual Cost (Year 5):** ~$17,676/year for raw storage

**Cost Optimization Recommendations:**
1. **Enable S3 Lifecycle Policies** - Automatically transition to cheaper storage classes
2. **Compress raw packets** - Store compressed JSON (gzip) to reduce storage by 70%
   - Compressed: 2.25 KB × 50M = 112.5 GB/day = 3.375 TB/month
   - Cost savings: Reduce from $1,473/month to **~$441/month** (70% reduction)
3. **Archive older than 5 years** - Move to Glacier Deep Archive (~$10/TB/month)
4. **Monitor and optimize** - Use S3 Storage Class Analysis to optimize transitions

**Recommended S3 Lifecycle Policy:**

```json
{
  "Rules": [
    {
      "Id": "RawTelemetryLifecycle",
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "INTELLIGENT_TIERING"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER_IR"
        },
        {
          "Days": 1825,  // 5 years
          "StorageClass": "DEEP_ARCHIVE"
        }
      ]
    }
  ]
}
```

**Action Items:**
- ✅ Volume estimates provided - capacity planning can proceed
- ✅ Storage costs calculated - budget planning available
- ⚠️ **DECISION NEEDED:** Compress raw packets before S3 storage? (Recommended: YES - 70% cost savings)
- ⚠️ **DECISION NEEDED:** Exact retention policy (5 years active, then archive - confirmed)

### 5.2 Critical Recommendations Based on Resolved Uncertainties

#### 🔴 CRITICAL: 100% API Queries Need Extended Fields

**Impact:** This fundamentally changes the architecture priorities.

**Implications:**
1. **JSONB performance is NOT optional** - Every API query will access extended fields
2. **Core-only optimization won't help APIs** - Must optimize JSONB queries from day one
3. **Database sizing must account for JSONB queries** - Need larger instances with more memory
4. **Caching strategy must include extended fields** - Can't cache only core fields for API

**Required Actions:**

1. **Database Instance Sizing:**
   - Start with **db.r5.xlarge or larger** (4+ vCPU, 32GB+ RAM)
   - JSONB queries are memory-intensive
   - Need buffer pool for frequent JSONB access
   - Monitor memory usage closely

2. **JSONB Index Strategy (CRITICAL):**
   ```sql
   -- Index ALL frequently-queried extended fields
   CREATE INDEX idx_extended_sensors ON telemetry_core USING GIN (
       (extended_data->'sensors')
   );
   CREATE INDEX idx_extended_diagnostics ON telemetry_core USING GIN (
       (extended_data->'diagnostics')
   );
   CREATE INDEX idx_extended_fuel ON telemetry_core USING GIN (
       (extended_data->'fuel')
   );
   -- Add more based on API query patterns
   ```

3. **API Query Optimization:**
   - **Avoid full JSONB scans** - Always use indexed paths
   - **Project specific fields** - Don't return entire extended_data JSONB
   - **Consider materialized views** - Pre-compute common API response structures
   - **Implement query result caching** - Cache API responses in ElastiCache

4. **Caching Strategy Update:**
   - Cache **complete API responses** (core + extended) in ElastiCache
   - TTL: 30-60 seconds for current state
   - Cache key: `telemetry:{asset_id}:current:{fields_hash}`
   - Invalidate on telemetry update

#### Volume-Based Capacity Planning

**Database Capacity Requirements:**

**Year 1 (20,000 assets):**
- Messages per second: ~116 msg/sec
- Daily inserts: 10,000,000 records
- Estimated database size (Year 1):
  - Core fields: ~500 bytes per record
  - Extended fields (JSONB): ~2 KB per record
  - Metadata: ~1 KB per record
  - **Total: ~3.5 KB per record**
  - **Year 1 storage: 10M × 365 × 3.5 KB = ~12.8 TB/year**

**Year 5 (100,000 assets):**
- Messages per second: ~579 msg/sec (peak may be 2-3x)
- Daily inserts: 50,000,000 records
- Estimated database size (Year 5):
  - **Year 5 storage: 50M × 365 × 3.5 KB = ~64 TB/year**

**Database Instance Recommendations:**

| Year | Assets | Daily Messages | Recommended Instance | Estimated Cost/month |
|------|--------|----------------|----------------------|---------------------|
| **Year 1** | 20,000 | 10M | db.r5.xlarge (4 vCPU, 32GB) | ~$300 |
| **Year 3** | 50,000 | 25M | db.r5.2xlarge (8 vCPU, 64GB) | ~$600 |
| **Year 5** | 100,000 | 50M | db.r5.4xlarge (16 vCPU, 128GB) | ~$1,200 |

**Considerations:**
- Use **Multi-AZ** for high availability (2x cost)
- Consider **Read Replicas** for API query scaling (Year 3+)
- Use **TimescaleDB compression** to reduce storage costs by 80-90% for older data
- Plan for **horizontal scaling** (partitioning) if single instance becomes bottleneck

**ElastiCache Capacity:**

- **Year 1:** cache.r5.large (2 vCPU, 13GB) - ~$120/month
- **Year 5:** cache.r5.xlarge (4 vCPU, 26GB) - ~$240/month
- Cache current state for all active assets (~5-10% of total assets typically online)

**Kinesis Data Streams:**

- **Year 1:** 2 shards - ~$43/month ($0.015/shard-hour × 2 × 730 hours)
- **Year 5:** 3-4 shards - ~$65-87/month
- Ingestion cost: $0.014/GB
  - Year 1: 75 GB/day × $0.014 = $1.05/day = ~$32/month
  - Year 5: 375 GB/day × $0.014 = $5.25/day = ~$158/month

#### Configuration Versioning Implementation

**Required Features:**

1. **Configuration Version Storage:**
   - Store all config versions in database (immutable)
   - Track which version is active per scope (default, customer, asset_group, asset)
   - Support rollback to any previous version

2. **Conflict Resolution (RECOMMENDED APPROACH):**
   - **Field-level override:** Lower-level configs override higher-level configs field-by-field
   - **Validation:** Prevent circular dependencies in asset group hierarchy
   - **Merge algorithm:** Deep merge with override priority
   - **Conflict detection:** Flag when lower-level config removes/overrides critical fields

3. **Rollback Support:**
   - Track config version history per scope
   - Support rollback to any previous version
   - Maintain audit trail (who rolled back, when, why)
   - **Note:** Rollback affects future telemetry only, not historical data

4. **Configuration Validation:**
   - Validate YAML syntax
   - Validate field mappings (ensure provider fields exist)
   - Validate calculation formulas
   - Test config on sample telemetry before activation

**Implementation Priority:**
- **Phase 1 (MVP):** Single default config, no versioning
- **Phase 2:** Add versioning, support default + customer configs
- **Phase 3:** Add asset group and asset-level configs
- **Phase 4:** Add rollback and conflict resolution

#### Total Cost Estimate (Year 5)

**Monthly Costs (Estimated):**

| Service | Configuration | Monthly Cost |
|---------|---------------|--------------|
| **S3 Raw Storage** | 135 TB (compressed) | ~$441 |
| **RDS PostgreSQL** | db.r5.4xlarge Multi-AZ | ~$2,400 |
| **ElastiCache Redis** | cache.r5.xlarge | ~$240 |
| **Kinesis Data Streams** | 4 shards + ingestion | ~$245 |
| **Data Transfer** | Outbound (estimated) | ~$100 |
| **API Gateway** | REST + WebSocket | ~$50 |
| **ECS/EKS Compute** | Transformation services | ~$300 |
| **CloudWatch/X-Ray** | Monitoring | ~$50 |
| **Total Estimated Monthly Cost** | | **~$3,826/month** |

**Annual Cost (Year 5):** ~$45,912/year

**Cost Optimization Opportunities:**
1. Compress S3 raw packets: **Save ~$1,032/month** (70% reduction)
2. Use TimescaleDB compression for older data: **Save ~$500/month** (database storage)
3. Use S3 Intelligent-Tiering: **Save ~$200/month** (auto-optimization)
4. Consider Reserved Instances: **Save 30-40%** on RDS/ElastiCache ($600-800/month)

**Optimized Annual Cost (Year 5):** ~$36,000-38,000/year

### 5.2 Potential Risks

1. **JSONB Query Performance:**
   - **Risk:** Complex JSONB queries may be slow
   - **Mitigation:** Use GIN indexes, monitor performance, optimize queries
   - **Fallback:** Consider Elasticsearch for complex extended field queries

2. **WebSocket Scalability:**
   - **Risk:** WebSocket connections may not scale to thousands of clients
   - **Mitigation:** Use horizontal scaling, load balancing, connection pooling
   - **Fallback:** Consider Server-Sent Events (SSE) or polling for some clients

3. **Transformation Metadata Overhead:**
   - **Risk:** Storing metadata with every record increases storage costs
   - **Mitigation:** Monitor storage growth, compress metadata, consider selective storage
   - **Fallback:** Store metadata separately for older records (archive strategy)

4. **Configuration Complexity:**
   - **Risk:** Configuration hierarchy may become complex to manage
   - **Mitigation:** Document configuration patterns, provide configuration validation
   - **Fallback:** Simplify configuration model if needed

### 5.3 Recommendations for Further Investigation

1. **Proof of Concept (AWS-Specific):**
   - Build small-scale POC with RDS PostgreSQL + TimescaleDB extension (or EC2 if not supported)
   - Test query performance with realistic data volumes
   - Validate WebSocket performance with multiple concurrent connections
   - Test S3 lifecycle policies and Glacier restore times
   - Validate ElastiCache Redis caching performance

2. **Benchmarking:**
   - Benchmark core-only queries vs core+extended queries on RDS/EC2
   - Benchmark JSONB query performance with various indexes
   - Benchmark WebSocket throughput and latency on API Gateway
   - Benchmark Kinesis Data Streams ingestion throughput
   - Test S3 Select performance for querying raw JSON files

3. **Cost Analysis (AWS-Specific):**
   - **S3 Storage Costs:**
     - Standard: ~$0.023/GB/month
     - Intelligent-Tiering: ~$0.023/GB/month (with monitoring fee)
     - Glacier Instant Retrieval: ~$0.004/GB/month
     - Glacier Deep Archive: ~$0.00099/GB/month
   - **RDS PostgreSQL Costs:**
     - db.t3.medium: ~$60/month (2 vCPU, 4GB RAM)
     - db.r5.xlarge: ~$300/month (4 vCPU, 32GB RAM)
     - Multi-AZ: 2x cost
   - **EC2 Costs (Self-Managed):**
     - t3.large: ~$60/month (2 vCPU, 8GB RAM)
     - r5.xlarge: ~$250/month (4 vCPU, 32GB RAM)
   - **ElastiCache Redis Costs:**
     - cache.t3.medium: ~$60/month (2 vCPU, 3GB RAM)
   - **Kinesis Data Streams:**
     - $0.015 per shard-hour + $0.014 per GB ingested
   - **Data Transfer:**
     - First 100GB/month free, then $0.09/GB (outbound)
   - **Action:** Use AWS Pricing Calculator to estimate costs based on expected volume

4. **Security Review (AWS-Specific):**
   - **IAM Roles:** Use IAM roles for service-to-service authentication (no hardcoded credentials)
   - **Secrets Manager:** Store database credentials in AWS Secrets Manager
   - **VPC:** Deploy RDS/ElastiCache in private subnets, use VPC endpoints for S3 access
   - **Encryption:**
     - S3: Enable bucket encryption (SSE-S3 or SSE-KMS)
     - RDS: Enable encryption at rest (AES-256)
     - ElastiCache: Enable encryption in transit (TLS)
   - **Network Security:**
     - Use Security Groups for network access control
     - Use NACLs for subnet-level filtering
   - **Audit Logging:**
     - CloudTrail for API access logging
     - CloudWatch Logs for application logs
     - RDS audit logs for database access
   - **Access Control:**
     - Use IAM policies for API access control
     - Use RDS IAM database authentication (optional)
     - Use ElastiCache AUTH token for Redis access control

---

## Conclusion

The proposed three-layer storage architecture is **fundamentally sound** but requires refinement in several critical areas. With AWS as the cloud provider, the architecture remains valid but implementation choices are AWS-specific:

1. **✅ Keep the architecture** - Three layers (raw/cold, core/hot, extended/warm) is correct
2. **✅ Use TimescaleDB on AWS** - RDS PostgreSQL with TimescaleDB extension (if supported) or self-managed on EC2
3. **✅ Single database with JSONB** - Simpler than separate databases, works well on AWS RDS
4. **🔴 CRITICAL: Define exact core field set** - "~50 fields" is too vague
5. **🔴 CRITICAL: Store transformation metadata** - Essential for traceability
6. **✅ Optimize WebSocket payloads** - Use delta updates, not full objects
7. **✅ Support field selection in API** - Use REST with `?fields=` parameter
8. **✅ AWS-Specific: Use S3 for raw storage** - With lifecycle policies for cost optimization
9. **✅ AWS-Specific: Use ElastiCache Redis** - For WebSocket caching layer
10. **✅ AWS-Specific: Use Kinesis/SQS** - For ingestion pipeline

**AWS-Specific Next Steps:**
1. **Verify TimescaleDB Support:** Check if RDS PostgreSQL supports TimescaleDB extension, or plan EC2 deployment
2. **Design S3 Structure:** Define S3 bucket structure, lifecycle policies, and access controls
3. **Plan ElastiCache Setup:** Design Redis cluster configuration for caching layer
4. **Design Ingestion Pipeline:** Choose Kinesis Data Streams vs SQS based on volume requirements
5. Define exact core field list (see Section 2.2 recommendation)
6. Design transformation metadata schema (see Section 2.5)
7. Create database schema specification (RDS or EC2)
8. Design API contracts (REST endpoints via API Gateway, WebSocket via API Gateway)
9. Build proof of concept on AWS to validate performance and costs
10. **Cost Estimation:** Use AWS Pricing Calculator to estimate monthly costs based on expected volume

**AWS Architecture Summary:**
- **Raw Storage:** S3 with lifecycle policies (Standard → Intelligent-Tiering → Glacier), **compress packets** for 70% cost savings
- **Core + Extended Storage:** RDS PostgreSQL with TimescaleDB extension (db.r5.xlarge+), **JSONB optimization critical** (100% API queries need extended fields)
- **Caching:** ElastiCache Redis for current state (cache complete API responses, not just core fields)
- **Ingestion:** Kinesis Data Streams (2-4 shards based on volume), handles 116-579 msg/sec
- **API:** API Gateway (REST + WebSocket)
- **Compute:** ECS/EKS for transformation services, Lambda for serverless functions
- **Monitoring:** CloudWatch for metrics and logs, X-Ray for tracing

**Volume-Based Capacity Plan:**
- **Year 1 (20,000 assets):** 10M messages/day, ~$1,500/month infrastructure
- **Year 5 (100,000 assets):** 50M messages/day, ~$3,800/month infrastructure (optimized: ~$3,000/month)

**Critical Success Factors:**
1. **JSONB Performance:** Must optimize JSONB queries from day one (100% API queries need extended fields)
2. **Database Sizing:** Start with db.r5.xlarge or larger for JSONB query performance
3. **Configuration Versioning:** Implement rollback support and conflict resolution (field-level override)
4. **Cost Optimization:** Compress S3 raw packets (70% savings), use lifecycle policies, consider Reserved Instances

This architecture will scale to handle **50M messages/day (100,000 assets)** on AWS while providing fast access for real-time updates and flexible querying for historical analysis. The AWS-native services provide managed infrastructure, reducing operational overhead while maintaining performance and reliability. **The 100% API extended fields requirement means JSONB optimization is not optional** - prioritize database instance sizing and indexing strategy accordingly.

