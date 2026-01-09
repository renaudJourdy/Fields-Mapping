# Provider Priority Configuration Specification

**Status:** 🎯 Specification  
**Version:** 1.0.0  
**Last Updated:** 2026-01-08

---

## Overview

This specification defines the **Provider Priority Configuration** system that enables assets with multiple gateways to have field-level provider selection rules. This determines which provider's telemetry data is used for each Fleeti field when multiple gateways are active on a single asset.

**Key Concepts:**
- **Gateway**: A device that communicates directly with a telemetry provider (e.g., Navixy tracker, OEM device)
- **Provider**: The telemetry service/system (e.g., "navixy", "oem", "trackunit")
- **Asset**: A vehicle, equipment, site, or phone that can have multiple gateways
- **Provider Priority**: Field-level rules defining which provider's data to prefer

---

## Use Cases

### Use Case 1: Camera + Tracker
- **Scenario**: Asset has both a camera gateway and a Navixy tracker gateway
- **Requirement**: Use tracker for all telemetry fields (camera stream visualized elsewhere)
- **Configuration**: All fields prefer "navixy" (tracker), ignore camera provider

### Use Case 2: OEM + Tracker
- **Scenario**: Asset has OEM telemetry (e.g., TrackUnit) and Navixy tracker
- **Requirements**:
  - Location fields: Navixy preferred (more frequent updates for accurate track drawing)
  - Counters (odometer, engine_hours): OEM preferred (more accurate, direct from vehicle)
  - I/O fields: Navixy preferred (accessories connected to tracker)
  - Motion fields: OEM preferred (CAN bus more accurate)
- **Configuration**: Field-specific provider priorities

### Use Case 3: Multiple Same-Provider Gateways
- **Scenario**: Asset has two Navixy trackers (e.g., primary + backup)
- **Requirement**: Use most up-to-date data when both gateways are from the same provider
- **Configuration**: Default behavior for same-provider selection

---

## Architecture

### Data Flow

```
1. Ingestion Layer
   - Receive telemetry packets from multiple gateways
   - Each packet: { gateway_id, provider, telemetry_data }

2. Transformation Pipeline (Per Gateway)
   - Transform each gateway independently
   - Apply provider-specific YAML mapping
   - Output: gateway_telemetry[gateway_id] = fleeti_data

3. Storage (Per Gateway)
   - Store transformed Fleeti telemetry per gateway
   - Maintain gateway_id association

4. Query/Aggregation Layer
   - Load provider priority rules (from Asset Service)
   - For each Fleeti field:
     a. Get all gateway telemetries for asset
     b. Apply provider priority rule
     c. Select best provider's value
     d. Handle same-provider selection (most recent)
   - Return merged asset telemetry

5. Consumption Layer
   - WebSocket streams (live.map.markers, live.assets.list, live.asset.details)
   - REST APIs (telemetry snapshots, asset history)
```

### Key Principles

1. **Transform First, Select Later**: Each gateway is transformed independently using provider-specific YAML. Provider selection happens during query/aggregation.
2. **Field-Aware Selection**: Different Fleeti fields can prefer different providers.
3. **Hierarchical Configuration**: Provider priority rules can be defined at default, customer, asset group, or asset level.
4. **Same-Provider Handling**: When multiple gateways from the same provider are selected, use most up-to-date data (by `last_updated_at` timestamp).

---

## Configuration Structure

### Storage Location

Provider priority configuration is stored in **Asset Service** (asset-specific metadata), not in YAML files. This separation maintains:
- **YAML files**: Provider-agnostic field mapping (reusable across assets)
- **Asset Service**: Asset-specific gateway selection rules

### Configuration Format

```json
{
  "asset_id": "uuid",
  "telemetry": {
    "provider_priority": {
      "version": "1.0.0",
      "rules": {
        "location.*": {
          "priority": ["navixy", "oem"],
          "same_provider_strategy": "most_recent"
        },
        "counters.odometer": {
          "priority": ["oem", "navixy"],
          "same_provider_strategy": "most_recent"
        },
        "counters.engine_hours": {
          "priority": ["oem", "navixy"],
          "same_provider_strategy": "most_recent"
        },
        "fuel.tank_level.value": {
          "priority": ["oem", "navixy"],
          "same_provider_strategy": "most_recent"
        },
        "motion.speed": {
          "priority": ["oem", "navixy"],
          "same_provider_strategy": "most_recent"
        },
        "io.*": {
          "priority": ["navixy"],
          "same_provider_strategy": "most_recent"
        },
        "*": {
          "priority": ["navixy", "oem"],
          "same_provider_strategy": "most_recent"
        }
      }
    }
  }
}
```

### Configuration Hierarchy

Provider priority rules follow the same hierarchy as field mapping configuration:

1. **Default/Global**: Base rules for all assets
2. **Customer-level**: Override default rules for a specific customer
3. **Asset Group**: Override customer rules for a group of assets
4. **Asset-level**: Override group rules for a specific asset (highest priority)

**Rule**: Lower-level configurations override higher-level configurations (same as field mapping hierarchy).

### Field Pattern Matching

Rules use field path patterns with wildcard support:

- **Exact Match**: `"counters.odometer"` matches only `counters.odometer`
- **Wildcard Pattern**: `"location.*"` matches all fields under `location` (e.g., `location.latitude`, `location.longitude`, `location.heading`)
- **Default Fallback**: `"*"` matches all fields not matched by more specific patterns

**Matching Order**: Most specific pattern wins (exact match > wildcard > default).

### Provider Names

Provider names must match the provider identifier used in:
- YAML configuration files (`provider: "navixy"`)
- Gateway metadata (`gateway.provider`)
- Provider field references in mappings

**Standard Provider Names:**
- `"navixy"`: Navixy telemetry provider
- `"oem"`: OEM telemetry (TrackUnit, etc.)
- Future providers as they are added

---

## Selection Algorithm

### Step 1: Provider Priority Selection

For each Fleeti field in the requested telemetry:

1. **Find Matching Rule**: Match field path against provider priority rules (most specific first)
2. **Get Provider Priority List**: Extract `priority` array from matching rule
3. **Iterate Through Providers**: For each provider in priority order:
   - Find all gateways for this asset with matching provider
   - If gateways found, proceed to Step 2 (Same-Provider Selection)
   - If no gateways found, continue to next provider
4. **Return Value**: Return selected value or `null` if no provider has data

### Step 2: Same-Provider Selection

When multiple gateways from the same provider are found:

1. **Check Strategy**: Read `same_provider_strategy` from rule (default: `"most_recent"`)
2. **Apply Strategy**:
   - **`"most_recent"`** (default): Select gateway with most recent `last_updated_at` timestamp
3. **Return Value**: Return value from selected gateway

### Selection Logic Pseudocode

```typescript
function selectProviderValue(
  fieldPath: string,
  assetId: string,
  gatewayTelemetries: Map<gatewayId, FleetiTelemetry>,
  priorityRules: ProviderPriorityRules
): any {
  // Step 1: Find matching rule
  const rule = findMatchingRule(fieldPath, priorityRules);
  
  // Step 2: Try providers in priority order
  for (const provider of rule.priority) {
    const providerGateways = findGatewaysByProvider(assetId, provider);
    
    if (providerGateways.length === 0) {
      continue; // No gateways for this provider
    }
    
    // Step 3: Same-provider selection
    const selectedGateway = selectFromSameProvider(
      providerGateways,
      gatewayTelemetries,
      rule.same_provider_strategy
    );
    
    const value = getFieldValue(fieldPath, gatewayTelemetries[selectedGateway]);
    
    // Step 4: Check if value is non-empty
    if (value !== null && value !== undefined && value !== "") {
      return value;
    }
  }
  
  return null; // No provider has value
}

function selectFromSameProvider(
  gateways: Gateway[],
  gatewayTelemetries: Map<gatewayId, FleetiTelemetry>,
  strategy: string
): gatewayId {
  if (strategy === "most_recent") {
    // Select gateway with most recent last_updated_at
    return gateways
      .map(g => ({
        gatewayId: g.id,
        lastUpdated: gatewayTelemetries[g.id].last_updated_at
      }))
      .sort((a, b) => b.lastUpdated.localeCompare(a.lastUpdated))[0]
      .gatewayId;
  }
  
  throw new Error(`Unknown strategy: ${strategy}`);
}
```

---

## Integration with WebSocket Contracts

Provider priority selection applies to all WebSocket streams that return asset telemetry:

- **`live.map.markers`** ([specification](./2-websocket-contracts/1-live-map-markers.md))
- **`live.assets.list`** ([specification](./2-websocket-contracts/2-asset-list.md))
- **`live.asset.details`** ([specification](./2-websocket-contracts/3-asset-details.md))

**Processing**: Backend applies provider priority rules when generating snapshot/delta messages. Each field in the response is the result of provider selection. Client receives merged asset telemetry (no gateway information exposed).

---

## Integration with API Contracts

Provider priority selection applies to all REST API endpoints that return asset telemetry:

- **`GET /api/v1/telemetry/snapshots`** ([specification](./3-api-contracts/1-telemetry-snapshots.md))
- **`GET /api/v1/admin/telemetry/snapshots`** ([specification](./3-api-contracts/1-telemetry-snapshots.md))
- **`GET /api/v1/telemetry/assets/{asset_id}/history`** ([specification](./3-api-contracts/2-asset-telemetry-history.md))
- **`GET /api/v1/admin/telemetry/assets/{asset_id}/history`** ([specification](./3-api-contracts/2-asset-telemetry-history.md))

**Processing**: Backend applies provider priority rules when generating responses. Each field in the response is the result of provider selection. Response contains merged asset telemetry (no gateway information).

---

## Configuration Examples

### Example 1: Camera + Tracker

**Scenario**: Asset has camera gateway and Navixy tracker. Use tracker for all fields.

```json
{
  "provider_priority": {
    "rules": {
      "*": {
        "priority": ["navixy"],
        "same_provider_strategy": "most_recent"
      }
    }
  }
}
```

**Result**: All Fleeti fields use Navixy tracker data. Camera gateway data is ignored.

---

### Example 2: OEM + Tracker

**Scenario**: Asset has OEM (TrackUnit) and Navixy tracker. Field-specific priorities.

```json
{
  "provider_priority": {
    "rules": {
      "location.*": {
        "priority": ["navixy", "oem"],
        "same_provider_strategy": "most_recent"
      },
      "counters.odometer": {
        "priority": ["oem", "navixy"],
        "same_provider_strategy": "most_recent"
      },
      "counters.engine_hours": {
        "priority": ["oem", "navixy"],
        "same_provider_strategy": "most_recent"
      },
      "fuel.tank_level.value": {
        "priority": ["oem", "navixy"],
        "same_provider_strategy": "most_recent"
      },
      "motion.speed": {
        "priority": ["oem", "navixy"],
        "same_provider_strategy": "most_recent"
      },
      "io.*": {
        "priority": ["navixy"],
        "same_provider_strategy": "most_recent"
      },
      "*": {
        "priority": ["navixy", "oem"],
        "same_provider_strategy": "most_recent"
      }
    }
  }
}
```

**Result**:
- Location fields: Navixy (more frequent updates)
- Odometer/Engine Hours: OEM (more accurate)
- Fuel Level: OEM (direct from vehicle)
- Speed: OEM (CAN bus more accurate)
- I/O fields: Navixy only (accessories on tracker)
- All other fields: Navixy preferred, OEM fallback

---

### Example 3: Multiple Same-Provider Gateways

**Scenario**: Asset has two Navixy trackers (primary + backup).

```json
{
  "provider_priority": {
    "rules": {
      "*": {
        "priority": ["navixy"],
        "same_provider_strategy": "most_recent"
      }
    }
  }
}
```

**Selection Behavior**:
1. Rule matches: `"*"` → priority `["navixy"]`
2. Find gateways: Both trackers are `"navixy"` provider
3. Same-provider selection: Use `"most_recent"` strategy
4. Compare `last_updated_at` timestamps:
   - Tracker A: `2025-10-23T13:59:50Z`
   - Tracker B: `2025-10-23T13:59:45Z`
5. Result: Use Tracker A (most recent)

---

## Implementation Requirements

### Backend Requirements

1. **Gateway Telemetry Storage**: Store transformed Fleeti telemetry per gateway (maintain `gateway_id` association)

2. **Provider Priority Rules Loading**: Load rules from Asset Service with hierarchy support (default → customer → group → asset)

3. **Field Selection Engine**: Implement selection algorithm with pattern matching and same-provider handling

4. **Query/Aggregation Layer**: Apply provider selection when generating WebSocket messages and API responses

5. **Performance**: Provider selection should be efficient (consider caching rules, optimizing gateway lookups)

### Asset Service Requirements

1. **Configuration Storage**: Store provider priority rules in asset metadata

2. **Hierarchy Support**: Support configuration at default, customer, asset group, and asset levels

3. **API Endpoints**: Provide endpoints to read/update provider priority rules (admin-only)

### Frontend Requirements

1. **No Changes Required**: Frontend receives merged asset telemetry (no gateway information exposed)

2. **Transparency**: Frontend should not be aware of multiple gateways or provider selection

---

## Edge Cases and Error Handling

### Edge Case 1: No Matching Provider

**Scenario**: Rule specifies `["oem", "navixy"]` but asset has neither provider.

**Handling**: Return `null` for the field (no value available).

### Edge Case 2: Provider Has Empty Value

**Scenario**: OEM has odometer value `null` or empty string.

**Handling**: Continue to next provider in priority list (Navixy). If all providers have empty values, return `null`.

### Edge Case 3: Same Timestamp for Multiple Gateways

**Scenario**: Two Navixy gateways have identical `last_updated_at` timestamp.

**Handling**: Select first gateway found (deterministic but arbitrary).

### Edge Case 4: Missing Configuration

**Scenario**: Asset has multiple gateways but no provider priority rules defined.

**Handling**: Use default rule `"*": ["navixy", "oem"]` with `"most_recent"` strategy.

### Edge Case 5: Invalid Provider Name

**Scenario**: Rule specifies provider `"invalid_provider"` that doesn't exist.

**Handling**: Skip invalid provider, continue to next provider in priority list.

---

## Related Documentation

- **[WebSocket Contracts](./2-websocket-contracts/README.md)**: Real-time streaming contracts
- **[API Contracts](./3-api-contracts/README.md)**: REST API specifications
- **[YAML Configuration](./1-databases/4-yaml-configuration/README.md)**: Field mapping configuration
- **[Architecture Overview](../1-overview-vision/3-architecture-overview.md)**: System architecture

---

**Last Updated:** 2026-01-08  
**Status:** 🎯 Specification
