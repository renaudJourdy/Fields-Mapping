# F[N].[M] – [Feature Name]

**Epic:** E[N] – [Epic Name]  
**Depends on:** [List dependencies: other features, epics, or external services]  
**Related Features:** [List related features within the same or other epics]

---

## 1. Description

[Concise, user-focused description of the feature. What does it do? What value does it deliver?]

### 1.1 Purpose

[Why does this feature exist? What problem does it solve?]

### 1.2 Context

[Provide context about where this feature fits in the system. What triggers it? When is it used?]

### 1.3 Value Proposition

[What value does this feature deliver? How does it contribute to the epic's goals?]

---

## 2. Business Logic

### 2.1 Rules & Priority

[Enumerate priority rules, decision order, and business logic that governs this feature's behavior]

**Priority Rules:**
- [Rule 1]
- [Rule 2]
- [Rule 3]

**Decision Logic:**
- [How decisions are made]
- [What conditions trigger different behaviors]

### 2.2 States & Behaviors

[Define all states, state transitions, and behaviors]

**States:**
- **State 1:** [Description]
- **State 2:** [Description]
- **State 3:** [Description]

**State Transitions:**
- [State 1] → [State 2]: [Trigger condition]
- [State 2] → [State 3]: [Trigger condition]

**Behaviors:**
- [Behavior 1]: [Description]
- [Behavior 2]: [Description]

### 2.3 Edge Cases

[List all edge cases and expected handling]

- **Edge Case 1:** [Description] → [Expected handling]
- **Edge Case 2:** [Description] → [Expected handling]
- **Edge Case 3:** [Description] → [Expected handling]

**Writing Guidelines:**
- **Avoid repetition**: State each concept once. If information is already covered in another section, reference it rather than repeating.
- **Be lean**: Consolidate related information. Don't repeat the same details across multiple paragraphs.
- **Include all important specifications**: Don't remove important information, just avoid saying it multiple times.

---

## 3. Technical Specification

### 3.1 Inputs

[Define all inputs to this feature]

- **Input 1:** [Type, format, validation rules]
- **Input 2:** [Type, format, validation rules]
- **Input 3:** [Type, format, validation rules]

### 3.2 Processing Logic

[Describe how the feature processes inputs]

1. [Step 1]
2. [Step 2]
3. [Step 3]

### 3.3 Outputs

[Define all outputs from this feature]

- **Output 1:** [Type, format, description]
- **Output 2:** [Type, format, description]

### 3.4 Data Structures

[Define any data structures, schemas, or formats used]

```json
{
  "example": "data structure"
}
```

---

## 4. Integration & Contracts

### 4.1 API Contracts

[If this feature exposes or consumes APIs, document the contracts]

**Endpoint:** `[HTTP Method] /api/v1/[endpoint]`

**Request:**
```json
{
  "example": "request"
}
```

**Response:**
```json
{
  "example": "response"
}
```

**Error Responses:**
- `400 Bad Request`: [Error condition]
- `500 Internal Server Error`: [Error condition]

### 4.2 Database Schema

[If this feature interacts with databases, document the schema]

**Table:** `[table_name]`

| Column | Type | Description |
|--------|------|-------------|
| column1 | type | description |
| column2 | type | description |

### 4.3 External Service Integration

[If this feature integrates with external services, document the integration]

**Service:** [Service name]
**Integration Type:** [REST API, WebSocket, Message Queue, etc.]
**Authentication:** [How authentication is handled]

---

## 5. Cross-Cutting Concerns

This feature must address cross-cutting concerns. **Reference the dedicated documentation** rather than duplicating content:

### 5.1 Security

**Reference:** [`../../7-security/README.md`](../../7-security/README.md)

[Brief note on security considerations specific to this feature. For example: "This feature must authenticate provider requests using API keys as specified in the security documentation."]

### 5.2 Data Quality

**Reference:** [`../../6-data-quality/README.md`](../../6-data-quality/README.md)

[Brief note on data quality considerations. For example: "Input data must be validated according to the data quality validation rules."]

### 5.3 Error Handling

**Reference:** [`../../5-operations/error-handling.md`](../../5-operations/error-handling.md)

[Brief note on error handling. For example: "Transient errors must be retried using exponential backoff as specified in the error handling documentation."]

### 5.4 Monitoring & Observability

**Reference:** [`../../5-operations/monitoring-observability.md`](../../5-operations/monitoring-observability.md)

[Brief note on monitoring. For example: "This feature must emit metrics for [specific metrics] as defined in the monitoring documentation."]

---

## 6. Acceptance Criteria

Each acceptance criterion follows the Given-When-Then format:

### AC1 – [Criterion Name]

**Given** [initial context]  
**When** [action or event]  
**Then** [expected outcome]

### AC2 – [Criterion Name]

**Given** [initial context]  
**When** [action or event]  
**Then** [expected outcome]

### AC3 – [Criterion Name]

**Given** [initial context]  
**When** [action or event]  
**Then** [expected outcome]

**Writing Guidelines:**
- **Focus on behavior, not implementation details**: Don't repeat specific values (timings, sizes, percentages) that are already defined in Business Logic. Use general descriptions like "smoothly", "adequately", "within acceptable time" instead of "200-300ms", "10% padding", "2px → 4px".
- **Merge related criteria**: When multiple acceptance criteria test similar behaviors or edge cases, merge them into comprehensive criteria rather than having separate ones.
- **Keep API/field references**: It's acceptable to reference API endpoints, field names (like `telemetry.location.latitude`), and contract details as these are part of the technical specification.
- **Be exhaustive but lean**: Cover all important test cases, but avoid repeating implementation details already specified in Business Logic sections.

---

## 7. Performance Requirements

[Define performance requirements specific to this feature]

- **Latency:** [Expected latency, e.g., "< 100ms for core fields"]
- **Throughput:** [Expected throughput, e.g., "Handle 1000 messages/second"]
- **Resource Usage:** [CPU, memory, storage constraints]

---

## 8. Testing Strategy

### 8.1 Unit Tests

[What unit tests are needed?]

- [Test case 1]
- [Test case 2]

### 8.2 Integration Tests

[What integration tests are needed?]

- [Test case 1]
- [Test case 2]

### 8.3 End-to-End Tests

[What E2E tests are needed?]

- [Test case 1]
- [Test case 2]

---

## 9. References

### 9.1 Related Documentation

- [Link to related epic specification]
- [Link to related feature specifications]
- [Link to schema specifications]
- [Link to architecture documents]

### 9.2 External References

- [Link to provider documentation]
- [Link to API documentation]
- [Link to research or design documents]

---

## 10. Non-Goals

[Clarify what is explicitly out of scope for this feature]

- [Out of scope item 1]
- [Out of scope item 2]
- [Out of scope item 3]

---

## 11. Open Questions

[Questions that need to be answered before implementation can begin]

1. [Question 1]
2. [Question 2]
3. [Question 3]

---

## 12. Change History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| YYYY-MM-DD | 1.0 | [Author] | Initial feature specification |

---

**Note:** This feature specification is standalone and deliverable. It can be implemented independently (subject to dependencies) and provides value when completed.

