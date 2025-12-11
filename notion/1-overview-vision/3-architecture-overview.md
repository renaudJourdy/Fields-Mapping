# Introduction

The Fleeti Telemetry Mapping system is designed as a **provider-agnostic, configuration-driven telemetry transformation pipeline** that ingests raw telemetry from multiple providers, transforms it into a unified Fleeti format, and stores it in multiple tiers for different access patterns.

# High-Level Architecture

```
┌─────────────┐
│   Provider  │  (Navixy, OEM, Future Providers)
│  Telemetry  │
└──────┬──────┘
       │
       │ Raw Telemetry Packets
       ▼
┌─────────────────────────────────────┐
│      Ingestion Layer                │
│  - Provider Parsers                 │
│  - Data Forwarding Handler          │
│  - Validation & Normalization       │
└──────┬──────────────────────────────┘
       │
       │ Provider-Agnostic Telemetry
       ▼
┌─────────────────────────────────────┐
│   Transformation Pipeline           │
│  - Field Mapping Engine             │
│  - Priority Rules                   │
│  - Calculation Engine               │
│  - Status Computation               │
│  - Configuration Loader             │
└──────┬──────────────────────────────┘
       │
       │ Fleeti Telemetry Format
       ▼
┌─────────────────────────────────────┐
│      Storage Tiers                  │
│  - Raw Archive (Cold)               │
│  - Core Fields (Hot)                │
│  - Extended Fields (Warm)           │
└──────┬──────────────────────────────┘
       │
       │ Query APIs
       ▼
┌─────────────────────────────────────┐
│      Consumption Layer              │
│  - Fleeti One Frontend              │
│  - Customer APIs (REST/GraphQL)     │
│  - Future: Streaming (WebSocket/SSE)│
└─────────────────────────────────────┘
```

# Data Flow

## 1. Ingestion

**Provider → Ingestion Layer**

- **Data Forwarding**: Real-time telemetry packets from Navixy
- **OEM APIs**: Direct integration with manufacturer APIs (future)
- **Provider Parsers**: Convert provider-specific format to provider-agnostic structure
- **Validation**: Ensure data integrity and completeness

## 2. Transformation

**Provider-Agnostic Telemetry → Fleeti Telemetry**

The transformation pipeline applies:

- **Direct Mapping**: 1:1 field mapping with optional unit conversion
- **Priority Rules**: Select best source when multiple provider fields available
- **Calculations**: Derive new fields from existing data (e.g., cardinal direction from heading)
- **Transformed Fields**: Combine telemetry with static asset metadata
- **I/O Mapping**: Map raw I/O signals to semantic fields based on installation metadata
- **Status Computation**: Compute status families (Connectivity, Transit, Engine, Immobilization)

## 3. Storage

**Fleeti Telemetry → Multi-Tier Storage**

- **Raw Archive (Cold)**: Original provider packets, permanent retention
- **Core Fields (Hot)**: ~25-30 essential fields for real-time map updates (< 100ms)
- **Extended Fields (Warm)**: All Fleeti telemetry fields for detail views (< 500ms)

## 4. Consumption

**Storage → Applications**

- **Fleeti One**: Real-time map markers and asset detail views
- **Customer APIs**: REST/GraphQL access to live and historical telemetry
- **Future Streaming**: WebSocket/SSE for real-time updates (planned)

# Key Components

## 1. Ingestion Layer

**Purpose**: Receive and parse telemetry from multiple providers

**Components**:

- **Provider Parsers**: Convert provider-specific formats to unified structure
- **Data Forwarding Handler**: Process Navixy Data Forwarding packets
- **Validation Engine**: Ensure data integrity and completeness
- **Error Handling**: Gracefully handle malformed or missing data

**Key Features**:

- Provider-agnostic interface
- Extensible parser architecture
- Real-time processing
- Error recovery and logging

## 2. Transformation Pipeline

**Purpose**: Transform provider telemetry into Fleeti format

**Components**:

- **Configuration Loader**: Load and merge hierarchical configurations
- **Field Mapping Engine**: Apply direct, prioritized, and calculated mappings
- **Priority Rules Engine**: Select best source when multiple fields available
- **Calculation Engine**: Derive calculated fields (cardinal direction, status, etc.)
- **Status Computation**: Compute status families based on telemetry and asset metadata
- **Asset Service Integration**: Retrieve installation metadata and asset specifications

**Key Features**:

- Configuration-driven (no hardcoding)
- Hierarchical configuration (default → customer → asset group → asset)
- Real-time transformation
- Extensible calculation framework

## 3. Storage Tiers

**Purpose**: Store telemetry in multiple tiers optimized for different access patterns

**Tiers**:

- **Raw Archive (Cold)**: Permanent storage of original provider packets
- **Core Fields (Hot)**: Fast access to essential fields for real-time updates
- **Extended Fields (Warm)**: Complete telemetry data for detail views and APIs

## 4. Configuration System

**Purpose**: Define field mappings and transformation rules

**Components**:

- **Configuration Files**: YAML-based field mapping definitions
- **Configuration Hierarchy**: Default, customer, asset group, asset levels
- **Configuration Runtime**: Load, merge, and apply configurations
- **Configuration API**: Manage and update configurations (future)

**Key Features**:

- YAML-based configuration
- Hierarchical override system
- Runtime configuration loading
- No code changes required for new mappings

## 5. API Layer

**Purpose**: Expose Fleeti telemetry to consumers

**Components**:

- **REST API**: Standard REST endpoints for telemetry access
- **GraphQL API**: Flexible query interface (future)
- **WebSocket/SSE**: Real-time streaming (future)
- **Authentication & Authorization**: Secure access control

**Key Features**:

- Standard REST interface
- Flexible query capabilities
- Real-time and historical access
- Customer-facing and internal APIs

# Provider-Agnostic Design Principles

## 1. Abstract Provider Interface

All providers implement a common interface:

- **Parse**: Convert provider format to provider-agnostic structure
- **Validate**: Ensure data integrity
- **Normalize**: Standardize field names and types

## 2. Unified Transformation

Regardless of provider, transformation pipeline:

- Applies same configuration rules
- Produces same Fleeti telemetry format
- Handles provider-specific differences transparently

## 3. Extensible Parser Architecture

New providers can be added by:

- Implementing provider parser interface
- Defining provider-specific field mappings
- No changes to transformation pipeline

# Storage Strategy

## Overview

The telemetry system stores data in **three tiers** to balance performance, cost, and data preservation:

1. **Fast Access (Hot)** - Core fields for real-time map updates
2. **Complete Data (Warm)** - All fields for detail views and API access
3. **Raw Archive (Cold)** - Original provider packets for historical recalculation

## Storage Tiers

### Fast Access Storage (Hot)

**Product Need**: Real-time map marker updates require instant access to essential telemetry fields.

- **Stored**: ~25-30 core fields (location, speed, status, basic vehicle state)
- **Performance**: < 100ms query latency for current asset state
- **Use Cases**: Map display, live tracking, real-time updates
- **Volume**: High-frequency reads and writes
- **Retention**: Last 30 days (optimized for real-time queries)

### Complete Data Storage (Warm)

**Product Need**: Asset detail views and customer API queries require access to all telemetry fields (300+ fields).

- **Stored**: All Fleeti telemetry fields (core + extended)
- **Performance**: < 500ms load time for asset detail view, < 2 seconds for 1-month historical query
- **Use Cases**: Asset detail views, customer API (100% need extended fields), historical analysis
- **Volume**: On-demand queries, batch historical queries
- **Retention**: 1-5 years (optimized for historical queries)

### Raw Archive Storage (Cold)

**Product Need**: Historical recalculation requires access to original provider packets.

- **Stored**: All raw provider telemetry packets (original format, permanent retention)
- **Performance**: On-demand access (seconds to minutes acceptable for archive restore)
- **Use Cases**: Historical recalculation when new fields are added, troubleshooting, debugging
- **Volume**: Rarely accessed (batch processing for recalculation only)
- **Retention**: Permanent (required for historical recalculation)

## Data Transformation & Storage Flow

**Ingestion Flow:**

1. Store raw provider packet in Cold Storage (permanent archive)
2. Transform provider fields to Fleeti format (apply configuration rules)
3. Store core fields in Fast Access Storage
4. Store all fields (core + extended) in Complete Data Storage

**Transformation Requirements:**

- Apply priority rules (field selection from multiple sources)
- Apply calculation rules (derive new fields from existing data)
- Preserve all provider fields in extended storage for traceability

## Historical Recalculation

**Product Need**: When new Fleeti telemetry fields are added, customers must have complete historical data for those fields.

**Capability Required:**

- System must be able to scan all historical raw packets
- System must apply new transformation rules to old data
- System must update Complete Data Storage with newly calculated fields
- Customers see complete historical data for new fields (no gaps)

**Requirement**: Raw archive storage must be permanent/very long-term to enable historical recalculation.

## Cost Optimization

Data older than 5 years may be archived to slower, cheaper storage tiers while remaining accessible for recalculation.

# Configuration System Overview

## Configuration Philosophy

**Critical requirement**: We must **avoid hardcoding** transformation rules. Instead, use **configuration files** (YAML) to define:

- Field mappings (direct, prioritized, calculated, transformed)
- Priority rules (source selection when multiple provider fields available)
- Calculation formulas (derived fields, aggregations)
- Static field transformations (combining telemetry with asset metadata)
- I/O to semantic field mappings (with default fallbacks)

**Rationale**: When a customer requests a different configuration (e.g., use OBD speed instead of CAN speed), we must handle it gracefully without code changes.

## Configuration Hierarchy

Configuration can be associated at multiple levels:

1. **Default/Global**: Base configuration for all assets
2. **Customer-level**: Override default configuration for a specific customer
3. **Asset Group**: Override customer configuration for a group of assets
4. **Single Asset**: Override group configuration for a specific asset

**Example**:

```
Default Config: speed = can_speed > obd_speed > gps_speed
Customer A Config: speed = obd_speed > gps_speed (CAN not available)
Asset Group "Fleet B": speed = gps_speed (OBD unreliable)
Asset "Truck-123": speed = can_speed (highest priority, manually set)
```

**Rule**: Lower-level configurations override higher-level configurations

## Configuration Scope

**What's configured here**:

- Provider field → Fleeti field mappings
- Priority rules for field selection
- Calculation formulas
- I/O to semantic field mappings (with default fallbacks)
- Static field transformations (references to asset metadata)

**What's NOT configured here** (stored in Asset Service):

- Installation metadata (`asset.installation.ignition_input_number`, etc.)
- Asset specifications (tank capacity, engine size, etc.)
- Accessory configurations (`asset.accessories[]`)

**Integration**: Transformation pipeline accesses Asset Service to retrieve installation metadata and asset specifications when needed for field computation.

# Integration Points

## Asset Service

- **Purpose**: Retrieve asset metadata, installation configuration, and specifications
- **Integration**: Transformation pipeline queries Asset Service during field computation
- **Data**: Installation metadata, asset properties, accessory configurations

## Geofence Service

- **Purpose**: Determine which geofences an asset is currently inside
- **Integration**: Computed during transformation based on location
- **Data**: Geofence IDs and names for current location

## Driver Catalog (future)

- **Purpose**: Lookup driver information from hardware key
- **Integration**: Driver identification during transformation
- **Data**: Driver ID and name from hardware key lookup