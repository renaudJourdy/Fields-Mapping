**Status:** 🎯 Structure Created - Content To Be Developed

This section contains comprehensive technical specifications for the Fleeti Telemetry Mapping system, organized by epics and features.

---

# Overview

The specifications section provides structured technical documentation covering:

- **Epic-Based Structure**: Specifications organized into 6 major epics (E1-E6)
- **Feature Breakdown**: Each epic contains multiple features (F[N].[M]) with detailed specifications
- **Databases**: Three critical databases (Provider Fields, Fleeti Fields, Mapping Fields) as single source of truth
- **API Contracts**: WebSocket and REST API contract specifications

---

# Epic Structure

The specifications are organized into 6 epics, each delivering major functional capabilities:

## [E1 – Ingestion & Provider Integration](./E1-Ingestion-Provider-Integration/README.md)

Receive and parse telemetry packets from multiple providers (Navixy, Teltonika, OEM).

**Features:**
- F1.1: Receive Provider Packets
- F1.2: Validate Packet Schema
- F1.3: Parse Provider Format
- F1.4: Save to Cold Storage

**Status:** 🎯 Draft

---

## [E2 – Field Mapping & Transformation](./E2-Field-Mapping-Transformation/README.md)

Transform provider telemetry into Fleeti format using configuration-driven mappings.

**Features:**
- F2.1: Load Hierarchical Configuration
- F2.2: Apply Direct Field Mappings
- F2.3: Apply Priority Rules
- F2.4: Compute Calculated Fields
- F2.5: Transform Fields with Static Data
- F2.6: Map I/O to Semantic Fields

**Status:** 🎯 Draft

---

## [E3 – Status Computation](./E3-Status-Computation/README.md)

Compute status families (Connectivity, Transit, Engine, Immobilization) and top status.

**Features:**
- F3.1: Compute Connectivity Status
- F3.2: Compute Transit Status
- F3.3: Compute Engine Status
- F3.4: Compute Immobilization Status
- F3.5: Compute Top Status

**Status:** 🎯 Draft

---

## [E4 – Storage & Data Management](./E4-Storage-Data-Management/README.md)

Multi-tier storage (hot, warm, cold) and data management capabilities.

**Features:**
- F4.1: Store to Hot Storage
- F4.2: Store to Warm Storage
- F4.3: Historical Recalculation
- F4.4: Data Retention Management
- F4.5: Schema Evolution

**Status:** 🎯 Draft

---

## [E5 – Configuration & Management](./E5-Configuration-Management/README.md)

Generate, store, deploy, and manage configuration files for field mapping.

**Features:**
- F5.1: Generate Configuration from Databases
- F5.2: Store and Version Configuration
- F5.3: Manage Hierarchical Configuration
- F5.4: Deploy Configuration
- F5.5: Validate Configuration

**Status:** 🎯 Draft

---

## [E6 – API & Consumption](./E6-API-Consumption/README.md)

Expose telemetry data via WebSocket streams and REST APIs.

**Features:**
- F6.1: WebSocket Stream for Live Map Markers
- F6.2: REST API for Hot Storage
- F6.3: REST API for Warm Storage
- F6.4: API Authentication & Authorization
- F6.5: Rate Limiting & Performance

**Status:** 🎯 Draft

---

# Databases

Three critical databases serve as the single source of truth for field definitions and mappings:

## [Databases](./databases/README.md)

- **[Provider Fields Database](./databases/provider-fields/README.md)**: Catalog of all provider-specific telemetry fields
- **[Fleeti Fields Database](./databases/fleeti-fields/README.md)**: Catalog of all Fleeti telemetry fields (~343+ fields)
- **[Mapping Fields Database](./databases/mapping-fields/README.md)**: Field transformation rules linking provider to Fleeti fields

**Status:** 🎯 Structure Created - Content To Be Developed

---

# API Contracts

Detailed contract specifications for WebSocket streams and REST APIs:

## [WebSocket Contracts](./websocket-contracts/README.md)

- **[Live Map Markers](./websocket-contracts/live-map-markers.md)**: Real-time marker updates for live map

**Status:** 🎯 Structure Created - Content To Be Developed

## [API Contracts](./api-contracts/README.md)

REST API contract specifications for hot and warm storage access.

**Status:** 🎯 Structure Created - Content To Be Developed

---

# Feature Index

See [FEATURE_PAGES_INDEX.md](./FEATURE_PAGES_INDEX.md) for a complete list of all features across all epics.

---

# Legacy Specifications

Legacy specification documents have been moved to `docs/legacy/` for reference:

- `telemetry-system-specification.md` - Complete system specification (validated)
- `status-rules.md` - Status computation rules (validated)
- `schema-specification.md` - Schema specification (validated)

**Note:** These legacy documents are for reference only. The new epic-based structure is the primary specification system.

---

# Related Documentation

- **[Field Mappings](../2-field-mappings/README.md)**: Field catalogs and mapping rules
- **[Requirements](../4-requirements/README.md)**: Functional and product requirements
- **[Overview & Vision](../../1-overview-vision/README.md)**: Project overview and architecture
- **[Developer Resources](../../3-developer-resources/README.md)**: Implementation guides and developer documentation

---

**Last Updated:** 2025-01-XX  
**Section Status:** 🎯 Structure Created - Content To Be Developed
