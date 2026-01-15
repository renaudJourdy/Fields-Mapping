# 📋 Overview & Vision

> *This section provides a comprehensive overview of the Fleeti Telemetry Mapping project, including its objectives, architecture, and key concepts. It serves as the entry point for understanding the project's vision, goals, and technical approach.*
> 

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

[Field Mappings & Databases](https://www.notion.so/Field-Mappings-Databases-2c73e766c90180b083a7e1447ee4967c?pvs=21)

Four databases that serve as the single source of truth for field definitions and mappings: Provider Fields Database, Fleeti Fields Database, Mapping Fields Database, and YAML Configuration Database.

> *These databases are the definitive source of truth for field definitions. They provide complete catalogs of provider-specific telemetry fields, unified Fleeti telemetry fields, transformation rules linking provider to Fleeti fields, and versioned tracking of generated YAML configuration files.*
> 

**Audience:** Backend developers, Developer Architect & Product Team

---

[WebSocket Contracts](https://www.notion.so/WebSocket-Contracts-2c73e766c90180fab506dba058ba2310?pvs=21)

WebSocket contract specifications for real-time telemetry streaming to frontend applications, including Live Map Markers, Asset List, and Asset Details streams.

> *WebSocket contracts define stream names, message formats, subscription parameters, update patterns (snapshot/delta), and error handling. Contracts specify which Fleeti fields are included in each stream, referencing field definitions from the Fleeti Fields Database.*
> 

**Audience:** Frontend developers and backend developers

---

[API Contracts](https://www.notion.so/API-Contracts-2c73e766c901807faafee6b8a3dd2d30?pvs=21)

REST API contract specifications for telemetry endpoints including snapshots, asset history, and visibility rules with customer vs admin tiers.

> *API contracts define endpoint URLs, request/response formats, query parameters, pagination, authentication, and error responses. Contracts specify Fleeti fields from the database and indicate which storage tiers are used (hot/warm/cold) for each endpoint.*
> 

**Audience:** Frontend developers and backend developers

---

[Reference Materials](https://www.notion.so/Reference-Materials-2c03e766c9018090b4aee76077d0af11?pvs=21)

Reference documentation including telemetry full schema, status rules, and provider field catalogs (Navixy, Flespi, Teltonika).

> *Reference materials providing complete telemetry schema reference with Navixy field mappings, status compatibility matrix for asset types, and provider field catalogs in CSV format for Navixy, Flespi, and Teltonika devices.*
> 

**Audience:** Developers and Product Team

---

[Developer Documentation](https://www.notion.so/Developer-Documentation-2e83e766c9018065871bca1012f3e15c?pvs=21)

*(✅ Validated)*

Developer documentation requirements and implementation specifications extracted from feature documentation.

> Developer documentation requirements and backend implementation details extracted from feature specifications. Includes API integration details, automation scripts, field extraction logic, and technical implementation requirements that developers need to document and implement.
> 

**Audience:** Backend developers and implementation team

---

[Epics & Features](https://www.notion.so/Epics-Features-2c63e766c901808fbe72fc6d698a85bf?pvs=21)

*(⚠️ In Progess)*

Complete technical specifications including telemetry system specification, status computation rules, and schema definitions.

> *Technical specifications covering system architecture, field types, transformation rules, status computation, and complete telemetry schema structure.*
> 

**Audience:** Developers and technical stakeholders

---

[[Requirements](https://www.notion.so/2-documentation/requirements/README.md)](https://www.notion.so/Requirements-2c63e766c90180268542cb6574a5bb81?pvs=21)

*(🎯 To Be Created)*

Functional and product requirements including field mapping requirements and storage product requirements.

> *Requirements documentation covering field mapping requirements, field documentation needs, and storage product requirements (⚠️ Under Review).*
> 

**Audience:** Product team, developers, and stakeholders

---

[[Operations](https://www.notion.so/2-documentation/operations/README.md)](https://www.notion.so/Operations-2c63e766c90180e9815adacfa1f5d7ae?pvs=21)

*(🎯 To Be Created)*

Operational documentation including error handling, monitoring, performance, disaster recovery, storage operations, and incident response runbooks.

> *Operational procedures for running and maintaining the telemetry system in production. Includes error handling strategies, monitoring specifications, performance tuning, disaster recovery procedures, and incident response runbooks.*
> 

**Audience:** Operations team, SRE, on-call engineers

---

[[Data Quality](https://www.notion.so/2-documentation/data-quality/README.md)](https://www.notion.so/Data-Quality-2c63e766c90180939f8fe11d162b9fbf?pvs=21)

*(🎯 To Be Created)*

Data quality and reliability documentation including validation, monitoring, data lineage, and idempotency handling.

> *Documentation for ensuring data quality, reliability, and integrity. Covers data validation rules, quality monitoring, data lineage tracking, and duplicate handling strategies.*
> 

**Audience:** Data engineers, operations team

---

[[Security](https://www.notion.so/2-documentation/security/README.md)](https://www.notion.so/Security-2c63e766c90180bbaa72f5dc8449fe41?pvs=21)

*(🎯 To Be Created)*

Security documentation including authentication, authorization, data privacy, compliance, and network security.

> *Security policies and procedures for securing the telemetry system. Covers authentication, authorization, data privacy, GDPR/CCPA compliance, and network security configuration.*
> 

**Audience:** Security team, operations team, developers

---

[[Integration](https://www.notion.so/2-documentation/integration/README.md)](https://www.notion.so/Integration-2c63e766c901802d9b18f14788ac8fd1?pvs=21)

*(🎯 To Be Created)*

Provider integration and onboarding documentation including step-by-step onboarding procedures and integration patterns.

> *Guide for integrating new telemetry providers and onboarding provider integrations. Includes provider onboarding checklist, integration patterns, and testing procedures.*
> 

**Audience:** Integration engineers, developers

**Priority:** 🟡 MEDIUM (High Risk)

---

[[Deployment](https://www.notion.so/2-documentation/deployment/README.md)](https://www.notion.so/Deployment-2c63e766c901806484d6fd2133e9c346?pvs=21)

*(🎯 To Be Created)*

Deployment and release management documentation including deployment procedures, configuration deployment, and rollback procedures.

> *Procedures for deploying code and configurations safely. Covers deployment strategies, CI/CD pipeline, zero-downtime deployment, configuration deployment, and rollback procedures.*
> 

**Audience:** DevOps, operations team

---

[[Data Management](https://www.notion.so/2-documentation/data-management/README.md)](https://www.notion.so/Data-Management-2c63e766c9018093905bcced1eb8e9cc?pvs=21)

*(🎯 To Be Created)*

Data management documentation including schema evolution, historical recalculation, and data retention policies.

> *Procedures for managing data lifecycle including schema changes, historical recalculation operations, and data retention policies. Covers migration strategies and archival procedures.*
> 

**Audience:** Data engineers, operations team

---

# 🛠️ Developer Resources

> *Practical guides and resources for developers implementing the system.*
> 

## Quicklinks

### Databases

[](https://www.notion.so/2c73e766c901806d9bacd1bf72f6014d?pvs=21) 

[](https://www.notion.so/2c73e766c901801d9ec1dbd299d1e30e?pvs=21) 

[](https://www.notion.so/2cc3e766c901806b9904e69fec02b085?pvs=21) 

[](https://www.notion.so/2cc3e766c90180199843f5b0ce72e2ed?pvs=21) 

### Websocket Contracts

[Live Map Markers](https://www.notion.so/Live-Map-Markers-2c73e766c901808cb15fc3c35294fb02?pvs=21) 

[Assets List](https://www.notion.so/Assets-List-2c73e766c90180659b37c2fc7679e481?pvs=21) 

[Asset Details](https://www.notion.so/Asset-Details-2c73e766c901803baf77eb85471e9f02?pvs=21) 

### Complex Computation Approach

[](https://www.notion.so/2c73e766c901801d9ec1dbd299d1e30e?pvs=21) 

### API Contracts

[Telemetry Snapshots](https://www.notion.so/Telemetry-Snapshots-2e13e766c9018092b37cc1d66f15eaee?pvs=21) 

[Asset Telemetry History](https://www.notion.so/Asset-Telemetry-History-2e13e766c9018052b7bcf345f02f3dd7?pvs=21) 

## **Subsections: (to be ignored)**

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

[Telemetry Mapping -  Product](https://www.notion.so/2d13e766c90180df9512d8b96768b033?pvs=21)

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

[Telemetry Database Design](https://www.notion.so/Telemetry-Database-Design-2d43e766c90180babeacf9be08607ced?pvs=21)

---