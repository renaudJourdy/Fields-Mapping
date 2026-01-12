# Feature Documentation Prompt Template

## Purpose

This template guides the creation of comprehensive feature documentation for backend/telemetry mapping features. Use this template to ensure consistency, completeness, and clarity across all feature specifications.

**Usage:** When creating a new feature document, follow this template and include only the sections relevant to your feature type. Reference existing documentation rather than duplicating content.

---

## Feature Type Classification Guide

Before starting, identify your feature type to determine which optional sections to include:

1. **Data Ingestion** (E1): External connections, data forwarding, health monitoring
   - Examples: F1.1 (Navixy Data Forwarding), F1.4 (Health Monitoring)

2. **Data Transformation** (E2): YAML execution, field mapping, configuration
   - Examples: F2.1 (YAML Configuration Execution), F2.2 (Hierarchical Configuration)

3. **Computation** (E3): Status computation, business logic processing
   - Examples: F3.1 (Status Families Computation)

4. **Storage** (E4): Multi-tier storage, retention, data lifecycle
   - Examples: F4.1 (Multi-Tier Storage), F4.2 (Retention Policy)

5. **API/WebSocket** (E6): REST endpoints, real-time streams, data exposure
   - Examples: F6.1-F6.9 (WebSocket streams, REST APIs)

6. **Operational** (E1.4, E1.5, E5): Monitoring, recovery, investigation tools
   - Examples: F1.4 (Health Monitoring), F1.5 (Data Recovery), F5.1 (Investigation Tool)

7. **Architecture** (E1.2, E2.2): Design and architectural readiness
   - Examples: F1.2 (Provider-Agnostic Architecture), F2.2 (Hierarchical Configuration Support)

8. **Configuration** (E7): Configuration management and rules
   - Examples: F7.1 (Provider Priority Rules)

**Decision Tree:**
- Does the feature expose data via REST API or WebSocket? → **API/WebSocket**
- Does the feature transform provider data to Fleeti format? → **Data Transformation**
- Does the feature compute status or business logic? → **Computation**
- Does the feature manage data storage tiers or lifecycle? → **Storage**
- Does the feature connect to external providers? → **Data Ingestion**
- Does the feature monitor, recover, or investigate? → **Operational**
- Does the feature define system architecture? → **Architecture**
- Does the feature manage configuration rules? → **Configuration**

---

## Core Template Structure

### 1. Header & Metadata

```markdown
# F[N].[M] - [Feature Name]

**Epic:** E[N] - [Epic Name]
**Feature Type:** [Ingestion/Transformation/Computation/Storage/API/Operational/Architecture/Configuration]
**Depends on:** [List dependencies: other features, epics, or external services]
**Related Features:** [List related features within the same or other epics]
**Status:** [Draft/In Review/Approved]
```

**Guidance:**
- Use the exact feature number from the epic README
- Be specific about dependencies (e.g., "F2.1 - YAML Configuration Execution")
- List related features that interact with this one
- Update status as feature progresses

---

### 2. Description

**What to include:**
- Clear statement of what the feature does (1-2 sentences)
- Why it exists - problem it solves or business need
- Value delivered - how it contributes to epic goals
- System context - where it fits in the data flow

**Example Questions to Answer:**
- What does this feature do in simple terms?
- What problem does it solve?
- How does it contribute to the epic's objectives?
- Where does it fit in the telemetry pipeline (ingestion → transformation → storage → consumption)?

**Writing Guidelines:**
- Be concise but complete
- Focus on the "what" and "why", not the "how"
- Reference the epic for broader context

---

### 3. Business Logic / Processing Logic

This is the core section. Include all relevant subsections based on your feature type.

#### 3.1 Core Rules and Priorities

**What to include:**
- Priority rules (if applicable)
- Decision logic and order of operations
- Business rules that govern behavior
- Conditions that trigger different behaviors

**Example Questions:**
- What rules determine how this feature behaves?
- In what order are decisions made?
- What conditions change the behavior?
- Are there priority hierarchies (e.g., Connectivity > Immobilization > Engine)?

**Format:**
- Use numbered lists for priority rules
- Use bullet points for decision logic
- Use tables for state matrices or priority hierarchies

#### 3.2 Processing Steps

**What to include:**
- Step-by-step workflow (numbered steps)
- Data flow through the feature
- Transformation logic (if applicable)
- Validation steps

**Example Questions:**
- What are the sequential steps this feature performs?
- How does data flow through this feature?
- What transformations occur at each step?
- Where are validations performed?

**Format:**
- Use numbered lists (1, 2, 3...)
- Be specific about inputs and outputs at each step
- Reference data structures and formats

#### 3.3 Edge Cases and Error Handling

**What to include:**
- Error conditions and how they're handled
- Boundary cases
- Failure modes
- Retry logic (if applicable)

**Example Questions:**
- What happens when input data is missing or invalid?
- What happens when external services are unavailable?
- How are partial failures handled?
- What are the boundary conditions (empty data, null values, etc.)?

**Format:**
- Use bullet points: `**Edge Case:** [Description] → [Expected handling]`
- Group related edge cases together
- Reference error handling documentation when applicable

#### 3.4 State Management (If Applicable)

**What to include:**
- System states
- State transitions
- State persistence
- State recovery

**Example Questions:**
- Does this feature have distinct states?
- What triggers state transitions?
- How is state persisted?
- How is state recovered after failures?

**Format:**
- Use state diagrams or tables
- List states and their descriptions
- Document transition triggers

---

### Feature-Type-Specific Subsections

Include these subsections under "Business Logic / Processing Logic" based on your feature type:

#### For API/WebSocket Features (E6)

**3.5 API/WebSocket Contract**

**What to include:**
- Endpoint URL or stream name
- HTTP method (for REST) or stream version (for WebSocket)
- Request/response formats with examples
- Message types (subscribe, snapshot, delta, update, error)
- Authentication requirements

**Example Questions:**
- What is the endpoint URL or stream name?
- What is the request format?
- What is the response format?
- How is authentication handled?
- What message types are supported?

**Format:**
- Use code blocks for JSON examples
- Reference contract documentation: `notion/2-documentation/2-websocket-contracts/` or `notion/2-documentation/3-api-contracts/`
- Include error response examples

**3.6 Rate Limiting and Throttling**

**What to include:**
- Rate limits (requests per second, messages per second)
- Throttling behavior
- Rate limit headers or error responses

**3.7 Subscription Management (WebSocket only)**

**What to include:**
- Subscription lifecycle
- Viewport updates
- Reconnection logic
- Sequence number handling

**3.8 Message Sequencing (WebSocket only)**

**What to include:**
- Sequence number guarantees
- Gap detection
- Resync procedures
- Idempotency rules

---

#### For Data Processing Features (E2, E3)

**3.5 Input/Output Specifications**

**What to include:**
- Input data sources and formats
- Output data formats
- Validation rules
- Required vs optional fields

**Example Questions:**
- What is the input data format (raw packets, provider fields)?
- What is the output format (Fleeti telemetry)?
- What validation is performed?
- Which fields are required?

**Format:**
- Reference provider field structure: `notion/2-documentation/1-field-mappings-and-databases/1-provider-fields/`
- Reference Fleeti field structure: `notion/2-documentation/1-field-mappings-and-databases/2-fleeti-fields/`
- Use code blocks for data structure examples

**3.6 Data Transformation Logic**

**What to include:**
- Step-by-step transformation process
- Field mapping rules
- Calculation formulas (if applicable)
- Priority-based selection logic (if applicable)

**Example Questions:**
- How are provider fields mapped to Fleeti fields?
- What calculations are performed?
- How are priorities resolved when multiple sources exist?
- What transformations combine multiple fields?

**Format:**
- Reference mapping rules: `notion/2-documentation/1-field-mappings-and-databases/3-mapping-fields/`
- Use formulas for calculations
- Use tables for mapping matrices

**3.7 YAML Configuration References**

**What to include:**
- Which YAML configuration files are used
- How configuration is loaded and applied
- Configuration structure reference

**Example Questions:**
- Which YAML files does this feature use?
- How is configuration loaded?
- What is the configuration structure?

**Format:**
- Reference YAML configuration: `notion/2-documentation/1-field-mappings-and-databases/4-yaml-configuration/`
- Reference YAML mapping reference: `notion/2-documentation/1-field-mappings-and-databases/4-yaml-configuration/yaml-mapping-reference.yaml`

**3.8 Field Mapping References**

**What to include:**
- Provider fields used
- Fleeti fields produced
- Mapping type (direct, prioritized, calculated, transformed, io_mapped)

**Example Questions:**
- Which provider fields are consumed?
- Which Fleeti fields are produced?
- What mapping types are used?

**Format:**
- Reference Mapping Fields Database: `notion/2-documentation/1-field-mappings-and-databases/3-mapping-fields/`
- Use tables for field mappings

**3.9 Computation Formulas (If Applicable)**

**What to include:**
- Mathematical formulas
- Formula parameters
- Unit conversions
- Edge cases in calculations

**Example Questions:**
- What formulas are used?
- What are the formula parameters?
- Are there unit conversions?
- How are calculation errors handled?

**Format:**
- Use mathematical notation or pseudo-code
- Document parameter sources
- Include unit conversion rules

---

#### For Storage Features (E4)

**3.5 Storage Tier Strategy**

**What to include:**
- Which storage tier is used (hot/warm/cold)
- Selection logic for tier placement
- Access patterns

**Example Questions:**
- Which storage tier(s) does this feature use?
- How is tier selection determined?
- What are the access patterns (read frequency, latency requirements)?

**Format:**
- Reference storage strategy: `notion/2-documentation/5-epics-and-features/E4-Storage-Strategy/`
- Use tables for tier characteristics
- Document latency requirements

**3.6 Data Lifecycle**

**What to include:**
- Data creation process
- Update patterns
- Archival procedures
- Deletion rules

**Example Questions:**
- How is data created?
- How is data updated?
- When is data archived?
- When is data deleted?

**3.7 Retention Policies**

**What to include:**
- Retention periods per tier
- Retention rules
- Exception handling

**Example Questions:**
- How long is data retained in each tier?
- What triggers data movement between tiers?
- Are there exceptions to retention rules?

**3.8 Migration Logic**

**What to include:**
- Tier movement procedures
- Migration triggers
- Migration scheduling
- Data consistency during migration

**Example Questions:**
- How is data moved between tiers?
- What triggers migration?
- When does migration occur?
- How is consistency maintained during migration?

**3.9 Query Patterns**

**What to include:**
- Common query patterns
- Query optimization strategies
- Index requirements
- Performance considerations

**Example Questions:**
- What are the common query patterns?
- How are queries optimized?
- What indexes are needed?
- What are the performance requirements?

---

#### For Integration Features (E1)

**3.5 External Service Contracts**

**What to include:**
- Provider API endpoints
- Request/response formats
- Authentication methods
- Rate limits

**Example Questions:**
- What provider APIs are used?
- What is the request/response format?
- How is authentication handled?
- What are the rate limits?

**Format:**
- Reference provider documentation
- Use code blocks for API examples
- Document authentication flows

**3.6 Connection Management**

**What to include:**
- Connection lifecycle
- Connection pooling
- Reconnection logic
- Connection health checks

**Example Questions:**
- How are connections established?
- How are connections maintained?
- What happens on connection failure?
- How are connections monitored?

**3.7 Error Handling**

**What to include:**
- Retry logic
- Error classification
- Failure modes
- Recovery procedures

**Example Questions:**
- What errors can occur?
- How are errors retried?
- What are the failure modes?
- How is recovery handled?

**3.8 Health Monitoring**

**What to include:**
- Health check procedures
- Metrics tracked
- Alert conditions
- Status reporting

**Example Questions:**
- How is health monitored?
- What metrics are tracked?
- When are alerts triggered?
- How is status reported?

**3.9 Data Recovery Procedures**

**What to include:**
- Gap detection logic
- Recovery triggers
- Recovery process
- Data validation after recovery

**Example Questions:**
- How are data gaps detected?
- What triggers recovery?
- How is missing data recovered?
- How is recovered data validated?

---

#### For Operational Features (E1.4, E1.5, E5)

**3.5 Monitoring Metrics**

**What to include:**
- Key metrics to track
- Metric definitions
- Metric collection points
- Metric aggregation

**Example Questions:**
- What metrics are tracked?
- How are metrics defined?
- Where are metrics collected?
- How are metrics aggregated?

**Format:**
- Use tables for metric definitions
- Reference monitoring documentation

**3.6 Alerting Rules**

**What to include:**
- Alert conditions
- Alert thresholds
- Alert severity levels
- Alert notification channels

**Example Questions:**
- What conditions trigger alerts?
- What are the alert thresholds?
- What are the severity levels?
- How are alerts delivered?

**Format:**
- Use tables for alert rules
- Document threshold values

**3.7 Recovery Procedures**

**What to include:**
- Recovery triggers
- Recovery steps
- Recovery validation
- Recovery rollback procedures

**Example Questions:**
- What triggers recovery?
- What are the recovery steps?
- How is recovery validated?
- Can recovery be rolled back?

**3.8 Investigation Workflows**

**What to include:**
- Investigation triggers
- Investigation steps
- Data sources for investigation
- Investigation tools

**Example Questions:**
- What triggers an investigation?
- What are the investigation steps?
- What data is needed for investigation?
- What tools are used?

**3.9 Audit Trail Logic**

**What to include:**
- What is logged
- Log format
- Log retention
- Log querying

**Example Questions:**
- What events are logged?
- What is the log format?
- How long are logs retained?
- How are logs queried?

**3.10 Data Quality Checks**

**What to include:**
- Quality validation rules
- Quality metrics
- Quality thresholds
- Quality reporting

**Example Questions:**
- What quality checks are performed?
- What are the quality metrics?
- What are the quality thresholds?
- How is quality reported?

---

#### For Architecture Features (E1.2, E2.2)

**3.5 Design Principles**

**What to include:**
- Architectural principles
- Design decisions
- Trade-offs considered
- Constraints

**Example Questions:**
- What principles guide the design?
- What key decisions were made?
- What trade-offs were considered?
- What are the constraints?

**Format:**
- Use bullet points for principles
- Document decision rationale

**3.6 Abstraction Layers**

**What to include:**
- Layer definitions
- Layer boundaries
- Layer interfaces
- Layer responsibilities

**Example Questions:**
- What abstraction layers exist?
- What are the layer boundaries?
- What are the layer interfaces?
- What are the layer responsibilities?

**Format:**
- Use diagrams or tables for layer structure
- Document interfaces between layers

**3.7 Future Extensibility**

**What to include:**
- Extension points
- Extension mechanisms
- Backward compatibility
- Migration paths

**Example Questions:**
- How can the system be extended?
- What are the extension points?
- How is backward compatibility maintained?
- What are the migration paths?

**3.8 Implementation Readiness**

**What to include:**
- What needs to be implemented
- Prerequisites
- Implementation phases
- Success criteria

**Example Questions:**
- What needs to be implemented?
- What are the prerequisites?
- What are the implementation phases?
- What are the success criteria?

**3.9 Provider Isolation**

**What to include:**
- Isolation mechanisms
- Isolation boundaries
- Shared vs isolated components
- Isolation testing

**Example Questions:**
- How are providers isolated?
- What are the isolation boundaries?
- What is shared vs isolated?
- How is isolation tested?

**3.10 Configuration Hierarchy**

**What to include:**
- Hierarchy levels
- Resolution order
- Override mechanisms
- Default behaviors

**Example Questions:**
- What are the hierarchy levels?
- What is the resolution order?
- How do overrides work?
- What are the defaults?

---

#### For Configuration Features (E7)

**3.5 Configuration Structure**

**What to include:**
- Configuration format
- Configuration schema
- Configuration validation
- Configuration examples

**Example Questions:**
- What is the configuration format?
- What is the configuration schema?
- How is configuration validated?
- What are example configurations?

**Format:**
- Use code blocks for configuration examples
- Reference configuration documentation

**3.6 Hierarchy Resolution**

**What to include:**
- Resolution order
- Override precedence
- Merge logic
- Conflict resolution

**Example Questions:**
- What is the resolution order?
- How is precedence determined?
- How are configurations merged?
- How are conflicts resolved?

**Format:**
- Use numbered lists for resolution order
- Use examples for merge logic

**3.7 Default Behaviors**

**What to include:**
- Default values
- Default rules
- Fallback logic
- Default inheritance

**Example Questions:**
- What are the default values?
- What are the default rules?
- What is the fallback logic?
- How are defaults inherited?

**3.8 Override Mechanisms**

**What to include:**
- Override levels
- Override syntax
- Override validation
- Override precedence

**Example Questions:**
- At what levels can overrides occur?
- What is the override syntax?
- How are overrides validated?
- What is the override precedence?

**3.9 Priority Rules**

**What to include:**
- Priority definition
- Priority resolution
- Priority conflicts
- Priority examples

**Example Questions:**
- How are priorities defined?
- How are priorities resolved?
- How are conflicts handled?
- What are priority examples?

**3.10 Validation Logic**

**What to include:**
- Validation rules
- Validation errors
- Validation timing
- Validation reporting

**Example Questions:**
- What are the validation rules?
- What errors can occur?
- When is validation performed?
- How are validation errors reported?

---

### 4. Performance Requirements (When Applicable)

**What to include:**
- Latency requirements (response time, processing time)
- Throughput requirements (messages per second, requests per second)
- Resource usage (CPU, memory, storage)
- Scalability considerations

**Example Questions:**
- What are the latency requirements?
- What throughput is needed?
- What are the resource constraints?
- How does it scale?

**Format:**
- Use tables for requirements
- Reference performance documentation
- Include specific numbers with units

**Example:**
```markdown
- **Latency:** < 100ms for hot storage queries, < 500ms for warm storage queries
- **Throughput:** Handle 1000 messages/second per customer
- **Resource Usage:** < 2GB memory per instance, < 50% CPU under normal load
```

---

### 5. Acceptance Criteria

**What to include:**
- Observable behaviors in Given-When-Then format
- Success scenarios
- Error scenarios
- Integration scenarios

**Example Questions:**
- What observable behaviors prove the feature works?
- What are the success scenarios?
- What are the error scenarios?
- How does it integrate with other features?

**Format:**
- Use Given-When-Then format
- Number each criterion (AC1, AC2, etc.)
- Focus on behavior, not implementation details
- Reference API endpoints and field names when relevant

**Writing Guidelines:**
- **Focus on behavior, not implementation**: Don't repeat specific values (timings, sizes) already defined in Business Logic. Use general descriptions like "smoothly", "within acceptable time" instead of "200-300ms".
- **Merge related criteria**: When multiple criteria test similar behaviors, merge them into comprehensive criteria.
- **Keep API/field references**: It's acceptable to reference API endpoints, field names (like `telemetry.location.latitude`), and contract details.
- **Be exhaustive but lean**: Cover all important test cases, but avoid repeating implementation details.

**Example:**
```markdown
### AC1 - Successful Data Forwarding Connection

**Given** a customer is configured for Navixy data forwarding  
**When** the system establishes connection to Navixy endpoint  
**Then** connection is authenticated, subscription is active, and raw packets are received

### AC2 - Connection Failure Handling

**Given** a data forwarding connection is active  
**When** the connection to Navixy endpoint fails  
**Then** the system detects the failure, logs an error, triggers alert, and attempts reconnection with exponential backoff
```

---

### 6. References

**What to include:**
- Related epic documentation
- Related feature documentation
- Database references (Provider Fields, Fleeti Fields, Mapping Fields, YAML Config)
- Contract specifications (WebSocket, API)
- Reference materials (schema, status rules)
- Provider documentation

**Format:**
- Use relative links to documentation
- Group references by category
- Include brief descriptions

**Example:**
```markdown
### Related Documentation
- [Epic 1 - Provider Ingestion & Data Forwarding](../E1-Provider-Ingestion-Data-Forwarding/README.md)
- [F1.1 - Navixy Data Forwarding Integration](../E1-Provider-Ingestion-Data-Forwarding/F1.1-Navixy-Data-Forwarding-Integration.md)

### Database References
- [Fleeti Fields Database](../../1-field-mappings-and-databases/2-fleeti-fields/README.md)
- [Mapping Fields Database](../../1-field-mappings-and-databases/3-mapping-fields/README.md)

### Contract Specifications
- [WebSocket Contracts - Live Map Markers](../../2-websocket-contracts/1-live-map-markers.md)
- [API Contracts - Telemetry Snapshots](../../3-api-contracts/1-telemetry-snapshots.md)

### Reference Materials
- [Telemetry Full Schema](../../4-reference-materials/1-telemetry-full-schema.md)
- [Status Rules](../../4-reference-materials/2-status-rules.md)
```

---

### 7. Non-Goals

**What to include:**
- Explicit out-of-scope items
- Future considerations
- Related but separate features
- Limitations

**Example Questions:**
- What is explicitly out of scope?
- What will be handled in future features?
- What are the known limitations?

**Format:**
- Use bullet points
- Be specific about what's excluded
- Reference related features that handle excluded items

**Example:**
```markdown
- Provider-specific authentication details (handled by provider integration layer)
- Frontend UI implementation (handled by mobile app features)
- Historical data recalculation (handled by F4.2 - Storage Retention Policy)
- Multi-provider support (handled by F1.2 - Provider-Agnostic Architecture)
```

---

## Writing Guidelines

### General Principles

1. **Be Specific**: Use concrete examples, avoid vague language
   - ❌ Bad: "The feature processes data efficiently"
   - ✅ Good: "The feature processes up to 1000 messages/second with < 100ms latency"

2. **Reference Don't Repeat**: Link to existing docs, don't duplicate
   - ❌ Bad: Copying entire field definitions
   - ✅ Good: "See [Fleeti Fields Database](../../1-field-mappings-and-databases/2-fleeti-fields/README.md) for field definitions"

3. **Focus on Behavior**: Describe what happens, not how it's implemented
   - ❌ Bad: "Uses a hash map to store connections"
   - ✅ Good: "Maintains one connection per customer, reuses connections when possible"

4. **Use Tables**: For structured data (states, mappings, configurations)
   - Use markdown tables for state matrices, priority hierarchies, configuration structures

5. **Use Code Blocks**: For technical specs (JSON, YAML, SQL)
   - Use appropriate language tags
   - Include comments for clarity

6. **Be Lean**: Include all important info, avoid redundancy
   - State each concept once
   - Reference other sections when appropriate
   - Consolidate related information

7. **Consider Future**: Document extensibility and future-proofing
   - Mention extension points
   - Document backward compatibility
   - Note future considerations

### Section-Specific Guidelines

**Description:**
- Keep it concise (2-4 paragraphs)
- Focus on "what" and "why"
- Reference the epic for context

**Business Logic:**
- Use numbered steps for workflows
- Use bullet points for rules
- Use tables for matrices
- Document all edge cases

**Acceptance Criteria:**
- Use Given-When-Then format
- Focus on observable behavior
- Include error scenarios
- Don't repeat implementation details

**References:**
- Use relative links
- Group by category
- Include brief descriptions
- Keep links updated

---

## Quick Reference Checklist

Use this checklist when creating a feature document:

### Before Starting
- [ ] Identified feature type
- [ ] Reviewed related features
- [ ] Reviewed epic documentation
- [ ] Identified dependencies

### Header & Metadata
- [ ] Feature number and name match epic README
- [ ] Feature type is identified
- [ ] Dependencies are listed
- [ ] Related features are listed
- [ ] Status is set

### Description
- [ ] What the feature does is clear
- [ ] Why it exists is explained
- [ ] Value delivered is stated
- [ ] System context is provided

### Business Logic / Processing Logic
- [ ] Core rules and priorities are documented
- [ ] Processing steps are numbered and clear
- [ ] Edge cases are documented
- [ ] Feature-type-specific subsections are included as needed
- [ ] All relevant subsections for feature type are included

### Performance Requirements (if applicable)
- [ ] Latency requirements are specified
- [ ] Throughput requirements are specified
- [ ] Resource usage is documented

### Acceptance Criteria
- [ ] All success scenarios are covered
- [ ] Error scenarios are covered
- [ ] Integration scenarios are covered
- [ ] Given-When-Then format is used
- [ ] Observable behaviors are described

### References
- [ ] Related documentation is linked
- [ ] Database references are included
- [ ] Contract specifications are linked
- [ ] Reference materials are linked

### Non-Goals
- [ ] Out-of-scope items are listed
- [ ] Future considerations are noted
- [ ] Related features are referenced

### Final Review
- [ ] No duplication of existing documentation
- [ ] All links are valid
- [ ] Code examples are correct
- [ ] Tables are properly formatted
- [ ] Writing guidelines are followed

---

## Examples by Feature Type

### Example: API/WebSocket Feature (F6.1)

**Feature Type:** API/WebSocket  
**Key Sections:**
- Business Logic includes: API/WebSocket Contract, Rate Limiting, Subscription Management, Message Sequencing
- Performance Requirements: Latency < 100ms for snapshots
- References: WebSocket contract documentation

**What to focus on:**
- Stream name, message formats, subscription parameters
- Authentication and authorization
- Rate limiting and throttling
- Message sequencing and idempotency

### Example: Data Transformation Feature (F2.1)

**Feature Type:** Data Transformation  
**Key Sections:**
- Business Logic includes: Input/Output Specifications, Data Transformation Logic, YAML Configuration References, Field Mapping References
- References: Mapping Fields Database, YAML Configuration Database

**What to focus on:**
- Provider field to Fleeti field mapping
- Transformation rules and formulas
- YAML configuration structure
- Field mapping types (direct, prioritized, calculated, etc.)

### Example: Storage Feature (F4.1)

**Feature Type:** Storage  
**Key Sections:**
- Business Logic includes: Storage Tier Strategy, Data Lifecycle, Retention Policies, Migration Logic, Query Patterns
- Performance Requirements: Latency requirements per tier

**What to focus on:**
- Hot/warm/cold tier selection
- Data lifecycle and retention
- Migration procedures
- Query optimization

### Example: Integration Feature (F1.1)

**Feature Type:** Data Ingestion  
**Key Sections:**
- Business Logic includes: External Service Contracts, Connection Management, Error Handling, Health Monitoring, Data Recovery Procedures
- References: Provider documentation

**What to focus on:**
- Provider API contracts
- Connection lifecycle
- Error handling and retries
- Health monitoring and recovery

### Example: Architecture Feature (F1.2)

**Feature Type:** Architecture  
**Key Sections:**
- Business Logic includes: Design Principles, Abstraction Layers, Future Extensibility, Implementation Readiness, Provider Isolation
- Non-Goals: Actual provider implementations

**What to focus on:**
- Architectural principles
- Abstraction layers
- Extension points
- Implementation readiness (not actual implementation)

---

## Common Pitfalls to Avoid

1. **Duplicating Documentation**: Don't copy entire sections from databases or contracts. Reference them instead.

2. **Too Much Implementation Detail**: Focus on "what" and "why", not "how". Implementation details belong in code, not specifications.

3. **Missing Edge Cases**: Document all error conditions and boundary cases. Don't assume "obvious" behavior.

4. **Vague Acceptance Criteria**: Use specific, observable behaviors. "Works correctly" is not acceptable.

5. **Outdated References**: Keep links updated. Broken links reduce trust in documentation.

6. **Inconsistent Formatting**: Follow the template structure. Consistency makes documentation easier to navigate.

7. **Missing Feature Type Classification**: Always identify the feature type to ensure correct sections are included.

8. **Ignoring Dependencies**: Document all dependencies. Missing dependencies cause implementation delays.

---

## Additional Resources

- **Epic Documentation**: `notion/2-documentation/5-epics-and-features/[Epic-Folder]/README.md`
- **Database Documentation**: `notion/2-documentation/1-field-mappings-and-databases/`
- **Contract Documentation**: `notion/2-documentation/2-websocket-contracts/` and `notion/2-documentation/3-api-contracts/`
- **Reference Materials**: `notion/2-documentation/4-reference-materials/`
- **Feature Template (Mobile App)**: Reference for structure inspiration (different context but similar approach)

---

**Last Updated:** 2026-01-09  
**Version:** 1.0.0
