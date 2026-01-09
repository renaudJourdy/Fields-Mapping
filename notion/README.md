# 📋 Overview & Vision

This section provides a comprehensive overview of the Fleeti Telemetry Mapping project, including its objectives, architecture, and key concepts. It serves as the entry point for understanding the project's vision, goals, and technical approach.

## Purpose

The **Overview & Vision** section is designed for:

- **Stakeholders**: High-level understanding of project goals, business value, and strategic direction
- **Developers**: Technical context, architecture decisions, and implementation guidance
- **New Team Members**: Quick onboarding and project orientation

## Section Contents

[Project Overview](https://www.notion.so/Project-Overview-2c03e766c901806080acd920c92cc6bc?pvs=21)

> *High-level project description covering current state and context, problem statement, project goals and vision, key stakeholders and use cases, and project scope and boundaries.*
> 

**Audience:** Stakeholders and developers

---

[Objectives & Goals](https://www.notion.so/Objectives-Goals-2c03e766c90180ea8e88cebf8521e8f9?pvs=21)

> *Primary objectives and requirements including provider-agnostic system vision, key requirements (provider-agnostic, provider-proof, future-proof), success criteria, and key principles and constraints.*
> 

**Audience:** Stakeholders and developers

---

[Architecture Overview](https://www.notion.so/Architecture-Overview-2c03e766c9018084a191f727ed099a59?pvs=21)

> System architecture and design including high-level system architecture, data flow and transformation pipeline, key components and their roles, storage strategy, and configuration system.
> 

**Audience:** Developers and technical stakeholders

---

[Key Concepts](https://www.notion.so/Key-Concepts-2c03e766c90180288bfaf5d119307445?pvs=21)

> *Terminology and fundamental concepts including provider-agnostic vs. provider-specific, Fleeti telemetry format, field types and transformation rules, priority levels and status families, and configuration hierarchy.*
> 

**Audience:** All audiences

---

# 📚 Documentation

> *This section contains comprehensive technical documentation for the Fleeti Telemetry Mapping project, including specifications, field mappings, reference materials, requirements, operations, security, integration, deployment, and data management.*
> 

## Purpose

The **Documentation** section provides:

- **Specifications**: Complete technical specifications for the telemetry system
- **Field Mappings**: Field catalogs and mapping rules
- **Reference Materials**: Provider catalogs and legacy documentation
- **Requirements**: Functional and product requirements
- **Operations**: Operational procedures, monitoring, and incident response
- **Security**: Security policies, authentication, and compliance
- **Integration**: Provider onboarding and integration patterns
- **Deployment**: Deployment and release management procedures
- **Data Management**: Schema evolution, historical recalculation, and data retention

## Section Contents

### [Specifications](./2-documentation/specifications/README.md)

*(✅ Validated)*

Complete technical specifications including telemetry system specification, status computation rules, and schema definitions.

> *Technical specifications covering system architecture, field types, transformation rules, status computation, and complete telemetry schema structure.*
> 

**Audience:** Developers and technical stakeholders

---

### [Databases](./2-documentation/1-specifications/1-databases/README.md)

*(✅ Done)*

Four databases that serve as the single source of truth for field definitions and mappings: Provider Fields Database, Fleeti Fields Database, Mapping Fields Database, and YAML Configuration Database.

> *These databases are the definitive source of truth for field definitions. They provide complete catalogs of provider-specific telemetry fields, unified Fleeti telemetry fields, transformation rules linking provider to Fleeti fields, and versioned tracking of generated YAML configuration files.*
> 

**Audience:** Developers and field mapping specialists

---

### [WebSocket Contracts](./2-documentation/1-specifications/2-websocket-contracts/README.md)

*(🎯 Structure Created - Content To Be Developed)*

WebSocket contract specifications for real-time telemetry streaming to frontend applications, including Live Map Markers, Asset List, and Asset Details streams.

> *WebSocket contracts define stream names, message formats, subscription parameters, update patterns (snapshot/delta), and error handling. Contracts specify which Fleeti fields are included in each stream, referencing field definitions from the Fleeti Fields Database.*
> 

**Audience:** Frontend developers and backend developers

---

### [API Contracts](./2-documentation/1-specifications/3-api-contracts/README.md)

*(✅ Done)*

REST API contract specifications for telemetry endpoints including snapshots, asset history, and visibility rules with customer vs admin tiers.

> *API contracts define endpoint URLs, request/response formats, query parameters, pagination, authentication, and error responses. Contracts specify Fleeti fields from the database and indicate which storage tiers are used (hot/warm/cold) for each endpoint.*
> 

**Audience:** Frontend developers and backend developers

---

### [Reference Materials](./2-documentation/4-reference-materials/README.md)

*(✅ Validated)*

Reference documentation including telemetry full schema, status rules, and provider field catalogs (Navixy, Flespi, Teltonika).

> *Reference materials providing complete telemetry schema reference with Navixy field mappings, status compatibility matrix for asset types, and provider field catalogs in CSV format for Navixy, Flespi, and Teltonika devices.*
> 

**Audience:** Developers and reference users

---

### [Requirements](./2-documentation/requirements/README.md)

*(⚠️ Mixed Status)*

Functional and product requirements including field mapping requirements and storage product requirements.

> *Requirements documentation covering field mapping requirements, field documentation needs, and storage product requirements (⚠️ Under Review).*
> 

**Audience:** Product team, developers, and stakeholders

---

### [Operations](./2-documentation/operations/README.md)

*(🎯 To Be Created)*

Operational documentation including error handling, monitoring, performance, disaster recovery, storage operations, and incident response runbooks.

> *Operational procedures for running and maintaining the telemetry system in production. Includes error handling strategies, monitoring specifications, performance tuning, disaster recovery procedures, and incident response runbooks.*
> 

**Audience:** Operations team, SRE, on-call engineers  
**Priority:** 🔴 HIGH (Blocking Production)

---

### [Data Quality](./2-documentation/data-quality/README.md)

*(🎯 To Be Created)*

Data quality and reliability documentation including validation, monitoring, data lineage, and idempotency handling.

> *Documentation for ensuring data quality, reliability, and integrity. Covers data validation rules, quality monitoring, data lineage tracking, and duplicate handling strategies.*
> 

**Audience:** Data engineers, operations team  
**Priority:** 🟡 MEDIUM (High Risk)

---

### [Security](./2-documentation/security/README.md)

*(🎯 To Be Created)*

Security documentation including authentication, authorization, data privacy, compliance, and network security.

> *Security policies and procedures for securing the telemetry system. Covers authentication, authorization, data privacy, GDPR/CCPA compliance, and network security configuration.*
> 

**Audience:** Security team, operations team, developers  
**Priority:** 🔴 HIGH (Blocking Production)

---

### [Integration](./2-documentation/integration/README.md)

*(🎯 To Be Created)*

Provider integration and onboarding documentation including step-by-step onboarding procedures and integration patterns.

> *Guide for integrating new telemetry providers and onboarding provider integrations. Includes provider onboarding checklist, integration patterns, and testing procedures.*
> 

**Audience:** Integration engineers, developers  
**Priority:** 🟡 MEDIUM (High Risk)

---

### [Deployment](./2-documentation/deployment/README.md)

*(🎯 To Be Created)*

Deployment and release management documentation including deployment procedures, configuration deployment, and rollback procedures.

> *Procedures for deploying code and configurations safely. Covers deployment strategies, CI/CD pipeline, zero-downtime deployment, configuration deployment, and rollback procedures.*
> 

**Audience:** DevOps, operations team  
**Priority:** 🔴 HIGH (Blocking Production)

---

### [Data Management](./2-documentation/data-management/README.md)

*(🎯 To Be Created)*

Data management documentation including schema evolution, historical recalculation, and data retention policies.

> *Procedures for managing data lifecycle including schema changes, historical recalculation operations, and data retention policies. Covers migration strategies and archival procedures.*
> 

**Audience:** Data engineers, operations team  
**Priority:** 🟡 MEDIUM (High Risk)

---

# 🛠️ Developer Resources

> *Practical guides and resources for developers implementing the system.*
> 

**Subsections:**

[Getting Started](https://www.notion.so/Getting-Started-2c03e766c90180849f59f7394e2e224b?pvs=21)

[Implementation Guides](https://www.notion.so/Implementation-Guides-2c03e766c90180e98575dc91b78753af?pvs=21)

[API Documentation](https://www.notion.so/API-Documentation-2c03e766c90180648727dea68b6464c9?pvs=21)

[Configuration Guide](https://www.notion.so/Configuration-Guide-2c03e766c9018052b2e4fe342df87c38?pvs=21)

[Technical Specifications](https://www.notion.so/Technical-Specifications-2c03e766c90180669955e8c47691b210?pvs=21)

[Developer Guidelines](https://www.notion.so/Developer-Guidelines-2c03e766c90180809ee1d3ce5cb046e9?pvs=21)

[Troubleshooting](https://www.notion.so/Troubleshooting-2c03e766c9018084852ed0306f3eae00?pvs=21)

---

# 📝 Project Management

> *Project status, roadmap, decisions, and ongoing work tracking.*
> 

**Subsections:**

[Current Status](https://www.notion.so/Current-Status-2c03e766c901802ab8b7f973ebef3b28?pvs=21)

[Ongoing Work](https://www.notion.so/Ongoing-Work-2c03e766c901803aaae0dd0c5e661b5f?pvs=21)

[Roadmap](https://www.notion.so/Roadmap-2c03e766c90180f6a6b2eed7286d704a?pvs=21)

[Decision Records](https://www.notion.so/Decision-Records-2c03e766c901802ba11ddde55d166958?pvs=21)

[Meeting Notes](https://www.notion.so/Meeting-Notes-2c03e766c90180ae9eb4c40c27856ce0?pvs=21)

---

# 🔧 Technical Pages

> *Space for developers to contribute their own technical pages, notes, and examples.*
> 

---

[Legacy](https://www.notion.so/Legacy-2c03e766c9018090b4aee76077d0af11?pvs=21)
