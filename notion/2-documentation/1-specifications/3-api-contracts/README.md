**Status:** Done

This section contains detailed API contract specifications for REST endpoints that expose Fleeti telemetry data.

# Purpose

API contracts define:
- Endpoint URLs and HTTP methods
- Request/response formats
- Query parameters and filtering
- Pagination
- Authentication and authorization
- Error responses

**Note:** API contracts specify Fleeti fields (from Fleeti Fields Database), not provider fields. Mapping from provider to Fleeti is handled in Epic 2.

---

# Available Contracts

## Telemetry API Endpoints

- [Telemetry Snapshots](./1-telemetry-snapshots.md)
  - Latest telemetry snapshot per asset (customer vs admin tiers)
- [Asset Telemetry History](./2-asset-telemetry-history.md)
  - Time-range history for a single asset (customer vs admin tiers)
- [Telemetry Visibility Rules](./3-telemetry-visibility-rules.md)
  - Role-based field visibility (customer vs admin)

**Status:** Published  
**Priority:** HIGH

---

# Contract Structure

Each contract document includes:
- Endpoint URL and HTTP method
- Authentication requirements
- Request parameters (query, path, body)
- Response format and structure
- Error responses and codes
- Field references (Fleeti fields from database)
- Rate limiting
- Examples
- Visibility rules (customer vs admin)

---

# Storage Tier Considerations

API endpoints may query different storage tiers:
- **Hot Storage**: Fast access to core fields (< 100ms)
- **Warm Storage**: Complete telemetry data (< 500ms)
- **Cold Storage**: Historical data (on-demand)

API contracts should specify which storage tier is used and expected latency.

---

# Related Documentation

- **[Epic 6 - API & Consumption](../E6-API-Consumption/README.md)**: Usage and implementation needs
- **[Fleeti Fields Database](../1-databases/2-fleeti-fields/README.md)**: Field definitions
- **[Storage Strategy](../E4-Storage-Data-Management/README.md)**: Storage tier details

---

**Last Updated:** 2026-01-07  
**Section Status:** Done
