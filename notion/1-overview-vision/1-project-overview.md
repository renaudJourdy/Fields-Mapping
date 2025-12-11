# Introduction

The Fleeti Telemetry Mapping project is creating a **provider-agnostic telemetry system** that aggregates telemetry data from multiple GPS tracking providers into a unified Fleeti telemetry format. This system enables Fleeti to become independent of any single provider while preserving complete historical data for recalculation and analysis.

# Current State

## Existing Architecture

Fleeti currently uses **Navixy as a white-labeling platform** for GPS tracking:

1. **Device → Navixy**: GPS devices send telemetry data to Navixy's platform
2. **Navixy Storage**: Navixy receives, parses, and stores all telemetry in their own database
3. **Navixy API**: Navixy exposes telemetry data to Fleeti and customers through their API

This architecture creates a dependency on Navixy's platform and limits Fleeti's ability to:

- Integrate with other telemetry providers (OEM manufacturers, other GPS platforms)
- Control data transformation and field mapping
- Preserve raw telemetry for historical recalculation
- Customize telemetry processing for specific customer needs

## Data Forwarding Investigation

We have investigated a **new data ingestion method called "Data Forwarding"**:

- **Real-time forwarding**: As soon as a device sends records to Navixy, Navixy forwards us the **raw parsed telemetry** immediately
- **No API polling required**: Eliminates the need to poll Navixy's API
- **Direct access**: We receive the data stream directly from Navixy's infrastructure

## POC Validation Results

We completed a Proof of Concept (POC) to validate Data Forwarding:

- ✅ **Received all telemetry** from test devices
- ✅ **Validated data integrity**: Compared Data Forwarding packets with Navixy API exports
- ✅ **Field catalog created**: Aggregated all unique telemetry fields found (~340 distinct fields)
- ✅ **Result**: Data Forwarding is viable and provides complete telemetry access

# Problem Statement

## Why We Need a Provider-Agnostic System

**Current Limitations:**

1. **Provider Dependency**: Fleeti is locked into Navixy's platform and API limitations
2. **Limited Integration**: Cannot easily integrate with OEM manufacturers or other GPS providers
3. **Data Control**: Cannot control how telemetry is transformed, stored, or accessed
4. **Historical Recalculation**: Cannot recalculate historical telemetry when new fields are added
5. **Customization**: Limited ability to customize field mappings and transformations per customer

**Business Impact:**

- **Scalability**: Cannot scale to support multiple providers without major refactoring
- **Flexibility**: Cannot adapt to customer-specific requirements or new telemetry sources
- **Data Preservation**: Risk of losing historical data or being unable to enhance it retroactively
- **Competitive Advantage**: Dependency on a single provider limits strategic options

# Project Goals and Vision

## Primary Objective

**Create Fleeti's own telemetry system** based on telemetry received through Navixy (and future providers), making Fleeti **provider-agnostic** and **provider-proof**.

## Vision Statement

> *"We need to aggregate any possible fields from any provider into a dedicated Fleeti telemetry. This Fleeti telemetry will be consumed by Fleeti One (web/mobile), exposed via API for customers, and potentially streamed in the future. All raw data must be preserved so we can recalculate historical Fleeti telemetry when new fields are introduced."*
> 

## Key Goals

1. **Provider Independence**: Work with Navixy, OEM manufacturers, and any future telemetry providers
2. **Complete Data Preservation**: Store all raw telemetry permanently for historical recalculation
3. **Unified Telemetry Format**: Transform provider-specific data into a consistent Fleeti format
4. **Flexible Configuration**: Support customer and asset-level field mapping customization
5. **Scalable Architecture**: Design for growth from 20,000 to 100,000+ assets

# Telemetry Sources

## Current Provider: Navixy

- **Source**: White-label GPS tracking platform
- **Format**: Raw parsed telemetry packets via Data Forwarding
- **Fields**: ~340 identified fields (see `docs/reference/navixy-field-catalog.csv`)
- **Status**: ✅ Active integration via Data Forwarding

## Future Providers

### OEM Direct Integration

- **Source**: Vehicle/machine manufacturers
- **Connection**: Direct OEM integration via credentials
- **Format**: Provider-specific telemetry format (AEMP 2.0)
- **Examples**: TrackUnit, CareTrack, Mecalac, Manitou, Liebher
- **Status**: Planned for future implementation

### Other Providers

- **Unknown providers**: System must handle providers not yet identified (Abeeway, etc.)
- **Flexible ingestion**: Architecture must accept any telemetry format
- **Field mapping**: New provider fields must be mappable to Fleeti telemetry

# Key Stakeholders and Use Cases

## Primary Users

1. **Fleet Managers**: Monitor fleet activity, view asset details, analyze historical trends
2. **Fleeti One Users**: Access real-time and historical telemetry via web and mobile applications
3. **API Customers**: Programmatically access telemetry data for integration and analysis
4. **Internal Teams**: Troubleshoot issues, analyze data, manage configurations

## Key Use Cases

1. **Real-Time Map Display**: Live map markers showing current asset locations and status
2. **Asset Detail Views**: Complete telemetry information when clicking on map markers
3. **Historical Analysis**: Time-series visualization of any telemetry field over days, weeks, or months
4. **Customer API Access**: Programmatic access to live and historical telemetry data
5. **Troubleshooting**: Access raw provider data and transformation history for debugging

# Project Scope and Boundaries

## In Scope

- ✅ Provider-agnostic telemetry ingestion and transformation
- ✅ Unified Fleeti telemetry format and schema
- ✅ Configuration-driven field mapping system
- ✅ Multi-tier storage strategy (raw, core, extended)
- ✅ Historical recalculation capability
- ✅ Customer and asset-level configuration overrides
- ✅ API access to Fleeti telemetry
- ✅ Integration with Fleeti One frontend

## Out of Scope (Initial Phase)

- ❌ Real-time streaming (WebSocket/SSE) - planned for future
- ❌ Event processing and alerts - handled by separate system
- ❌ Geofence computation - handled by separate service
- ❌ Trip detection and management - handled by separate service
- ❌ Driver identification catalog - handled by separate service

## Boundaries

- **Asset Metadata**: Asset specifications, installation metadata, and accessories are managed by the Asset Service, not the telemetry system
- **Configuration Storage**: Field mapping configurations are managed by the telemetry system, but asset-level installation metadata is stored in Asset Service
- **Status Computation**: Status families (Connectivity, Transit, Engine, Immobilization) are computed by the telemetry system, but asset type compatibility is determined by Asset Service

# Success Criteria

## Functional Requirements

- ✅ Receive telemetry from Navixy via Data Forwarding
- ✅ Store all raw telemetry permanently (cold storage)
- ✅ Transform to Fleeti telemetry using configuration
- ✅ Store core telemetry for fast queries (< 100ms)
- ✅ Store extended telemetry for complete data (< 500ms)
- ✅ Expose Fleeti telemetry via API
- ✅ Display in Fleeti One (live + historical)
- ✅ Detect and flag new provider fields
- ✅ Support customer/asset-level configuration

## Non-Functional Requirements

- ✅ Provider-agnostic architecture
- ✅ Configuration-driven (no hardcoding)
- ✅ Scalable to multiple providers
- ✅ Historical recalculation capability
- ✅ Complete field documentation
- ✅ Fast query performance (core fields)
- ✅ Complete data preservation

# Next Steps

1. **Review and validate** this specification
2. **Define core field schema** (~50 fields) aligned with frontend requirements
3. **Create field mapping configuration** (YAML) for all Navixy fields
4. **Design database schema** (raw, core, extended tables)
5. **Prototype transformation pipeline**