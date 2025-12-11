# Primary Objective

**Create Fleeti's own telemetry system** based on telemetry received through Navixy (and future providers), making Fleeti **provider-agnostic** and **provider-proof**.

This objective addresses the fundamental need to:

- Aggregate telemetry from multiple providers into a unified format
- Maintain independence from any single provider
- Preserve complete historical data for future enhancements
- Support flexible configuration and customization

# Key Requirements

## 1. Provider-Agnostic Design

**Requirement**: The system must work with Navixy, OEM manufacturers, and any future telemetry providers.

**Rationale**:

- Fleeti cannot be locked into a single provider
- Different customers may use different providers
- OEM direct integration is a strategic priority
- Future providers must be easily integrated

**Implementation**:

- Abstract provider-specific parsers
- Unified ingestion interface
- Provider-agnostic transformation pipeline
- Consistent Fleeti telemetry output regardless of source

## 2. Provider-Proof Architecture

**Requirement**: System must be able to aggregate **any possible fields from any provider** into a unified Fleeti telemetry format.

**Rationale**:

- Providers have different field sets and capabilities
- New fields may be introduced by providers over time
- System must handle unknown fields gracefully
- No field should be lost or ignored

**Implementation**:

- Flexible field mapping configuration
- Support for unknown/new fields
- Watchdog system to detect new provider fields
- Extended storage for all fields (known and unknown)

## 3. Future-Proof Design

**Requirement**: Architecture must support new providers and field types without major refactoring.

**Rationale**:

- New providers will be added over time
- Field definitions may evolve
- Customer requirements may change
- System must adapt without breaking changes

**Implementation**:

- Configuration-driven field mappings (no hardcoding)
- Extensible provider parser architecture
- Versioned field schemas
- Backward-compatible API design

## 4. Complete Data Preservation

**Requirement**: Store all raw telemetry to enable historical recalculation when new Fleeti telemetry fields are added.

**Rationale**:

- Customers need complete historical data for new fields
- Cannot recalculate without raw source data
- Historical analysis requires full data preservation
- Compliance and audit requirements

**Implementation**:

- Permanent raw archive storage (cold tier)
- Complete provider packet preservation
- Historical recalculation capability
- Traceability from Fleeti data to raw provider data

# Vision Components

1. **Unified Telemetry Format**: Single Fleeti telemetry structure regardless of provider
2. **Multi-Channel Consumption**: Fleeti One, customer APIs, and future streaming
3. **Complete Historical Data**: All raw data preserved for recalculation
4. **Continuous Enhancement**: Ability to add new fields and recalculate history

# Success Criteria

## Functional Success Criteria

- ✅ **Ingestion**: Successfully receive telemetry from Navixy via Data Forwarding
- ✅ **Storage**: Store all raw telemetry permanently (cold storage)
- ✅ **Transformation**: Transform provider fields to Fleeti format using configuration
- ✅ **Performance**: Core fields queryable in < 100ms, extended fields in < 500ms
- ✅ **API Access**: Expose Fleeti telemetry via REST API
- ✅ **Frontend Integration**: Display telemetry in Fleeti One (live + historical)
- ✅ **Field Detection**: Detect and flag new provider fields automatically
- ✅ **Configuration**: Support customer/asset-level configuration overrides

## Non-Functional Success Criteria

- ✅ **Provider-Agnostic**: Architecture supports multiple providers without code changes
- ✅ **Configuration-Driven**: No hardcoded transformation rules
- ✅ **Scalable**: Handles growth from 20,000 to 100,000+ assets
- ✅ **Historical Recalculation**: Can recalculate historical data when new fields added
- ✅ **Complete Documentation**: All fields documented with sources and transformations
- ✅ **Fast Performance**: Core field queries meet latency requirements
- ✅ **Data Preservation**: All raw telemetry preserved permanently

# Key Principles

## 1. Configuration Over Code

**Principle**: Transformation rules must be defined in configuration files (YAML), not hardcoded in application code.

**Rationale**:

- Customer-specific requirements without code changes
- Faster adaptation to new fields and providers
- Easier testing and validation
- Reduced deployment risk

**Implementation**:

- YAML-based field mapping configuration
- Hierarchical configuration (default → customer → asset group → asset)
- Runtime configuration loading and merging

## 2. Complete Data Preservation

**Principle**: All raw provider telemetry must be preserved permanently.

**Rationale**:

- Historical recalculation requires raw data
- Troubleshooting and debugging need source data
- Compliance and audit requirements
- Future field additions need historical context

**Implementation**:

- Permanent raw archive storage (cold tier)
- Complete provider packet preservation
- Traceability links from Fleeti to raw data

## 3. Provider Independence

**Principle**: System must not depend on any single provider's platform or API.

**Rationale**:

- Strategic flexibility
- Risk mitigation
- Competitive advantage
- Customer choice

**Implementation**:

- Abstract provider interfaces
- Unified ingestion layer
- Provider-agnostic transformation
- Consistent output format

## 4. Scalability and Performance

**Principle**: System must scale efficiently and meet performance requirements.

**Rationale**:

- Growth from 20,000 to 100,000+ assets
- Real-time map updates require low latency
- Historical queries must complete in acceptable time
- Cost-effective scaling

**Implementation**:

- Multi-tier storage (hot, warm, cold)
- Optimized query paths for common use cases
- Efficient data structures and indexing
- Horizontal scaling capability

# Constraints

## Technical Constraints

1. **Data Forwarding Format**: Must work with Navixy Data Forwarding packet format
2. **Asset Service Integration**: Must integrate with existing Asset Service for metadata
3. **Frontend Compatibility**: Must output format compatible with Fleeti One requirements
4. **API Compatibility**: Must maintain backward compatibility with existing APIs

## Business Constraints

1. **Timeline**: Must deliver core functionality within project timeline
2. **Cost**: Storage and compute costs must be reasonable
3. **Risk**: Cannot break existing functionality during migration
4. **Resources**: Limited development and infrastructure resources

## Operational Constraints

1. **Monitoring**: System must be monitorable and debuggable
2. **Maintenance**: Configuration changes must not require code deployments
3. **Support**: Must support troubleshooting and customer configuration changes
4. **Documentation**: All fields and transformations must be documented

# Measurement and Validation

## How We Measure Success

1. **Functional Validation**: All success criteria met and tested
2. **Performance Validation**: Query latencies meet requirements
3. **Scalability Validation**: System handles projected load
4. **Data Integrity Validation**: Raw data preserved and traceable
5. **Configuration Validation**: Customer configurations work as expected

## Validation Methods

- **POC Results**: Data Forwarding POC validated ingestion capability
- **Field Catalog**: ~340 Navixy fields identified and cataloged
- **Data Integrity**: Compared Data Forwarding packets with Navixy API exports
- **Performance Testing**: Query latency testing for core and extended fields
- **Configuration Testing**: Customer configuration override testing