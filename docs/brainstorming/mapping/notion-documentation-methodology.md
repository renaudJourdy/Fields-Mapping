# Notion Documentation Methodology for Fleeti Telemetry Field Mapping & Versioning

**Document Version:** 1.0  
**Date:** 2025-01-XX  
**Status:** Draft - Implementation Guide  
**Owner:** Documentation & Development Teams

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Database Schema Design](#2-database-schema-design)
3. [Field Type Handling](#3-field-type-handling)
4. [Versioning System](#4-versioning-system)
5. [YAML Sync Methodology](#5-yaml-sync-methodology)
6. [Developer Guide](#6-developer-guide)
7. [Notion Setup Instructions](#7-notion-setup-instructions)
8. [Automation & Scripts](#8-automation--scripts)

---

## 1. Executive Summary

### Purpose

This methodology defines a comprehensive Notion documentation system for Fleeti's telemetry field mapping architecture. It enables:

- **Complete field documentation** for all Fleeti fields and provider fields
- **Mapping relationship tracking** between Fleeti and provider fields
- **Version synchronization** between Notion documentation and YAML configuration files
- **Developer-friendly workflows** for maintaining field mappings
- **Automated validation** to ensure consistency between docs and configs

### Key Design Decisions

1. **Database Structure**: Three databases (Fleeti Fields, Provider Fields, Field Mappings) for clarity and maintainability
2. **Field Granularity**: Document at semantic level (`fuel.level`), not property level (`fuel.level.value`)
3. **Mapping Rules Storage**: Dedicated Field Mappings database for complex many-to-many relationships
4. **Versioning**: Semantic versioning with change history tracking
5. **Sync Strategy**: Documentation-first workflow with YAML generation and validation

### Architecture Overview

```
┌─────────────────────┐
│  Fleeti Fields DB   │
│  (300+ fields)      │
└──────────┬──────────┘
           │
           │ many-to-many
           │
┌──────────▼──────────┐
│ Field Mappings DB   │
│ (mapping rules)     │
└──────────┬──────────┘
           │
           │ many-to-many
           │
┌──────────▼──────────┐
│ Provider Fields DB  │
│ (provider-specific) │
└─────────────────────┘
```

---

## 2. Database Schema Design

### 2.1 Database 1: Fleeti Fields

**Purpose**: Document all Fleeti telemetry fields (semantic level), their properties, priorities, and relationships.

**Database Name**: `Fleeti Telemetry Fields`

#### Properties

| Property Name | Type | Description | Required | Example |
|--------------|------|-------------|----------|---------|
| **Field Name** | Title | Semantic field name (path) | ✅ Yes | `fuel.level` |
| **Field Path** | Text | Full path in telemetry object | ✅ Yes | `fuel.level` |
| **Category** | Select | Section/category | ✅ Yes | `fuel`, `location`, `motion`, `status`, `power`, `diagnostics`, `sensors`, `driving_behavior`, `device`, `connectivity`, `io`, `driver`, `other`, `metadata` |
| **Priority** | Select | Implementation priority | ✅ Yes | `P0`, `P1`, `P2`, `P3`, `T`, `BL`, `?`, `ignored`, `later` |
| **Field Type** | Select | Mapping type | ✅ Yes | `direct`, `prioritized`, `calculated`, `aggregated`, `transformed`, `io_mapped`, `asset_integrated` |
| **Structure Type** | Select | Data structure | ✅ Yes | `simple_value`, `value_unit_object`, `nested_object`, `array` |
| **Data Type** | Select | JSON data type | ✅ Yes | `number`, `string`, `boolean`, `object`, `array`, `null` |
| **Unit** | Text | Standard unit (if applicable) | ❌ No | `km/h`, `°C`, `l`, `%` |
| **Description** | Text | What the field represents | ✅ Yes | `Current fuel level in liters` |
| **Use Cases** | Text | Where/how field is used | ❌ No | `Asset detail view, fuel consumption reports` |
| **Provider Fields** | Relation | Links to Provider Fields DB | ❌ No | (many-to-many via Field Mappings) |
| **Field Mappings** | Relation | Links to Field Mappings DB | ❌ No | (one-to-many) |
| **Dependencies** | Relation | Other Fleeti fields this depends on | ❌ No | Links to other Fleeti Fields |
| **Calculation Formula** | Text | Formula/logic (if calculated) | ❌ No | `derive_from_heading(location.heading)` |
| **Transformation Rule** | Text | Transformation logic (if transformed) | ❌ No | `(fuel.level_percent / 100) * static.tank_capacity_liters` |
| **Status** | Select | Field status | ✅ Yes | `active`, `deprecated`, `planned`, `under_review` |
| **Version Added** | Text | Version when field was added | ✅ Yes | `1.0.0` |
| **Last Modified** | Date | Last modification date | ✅ Yes | `2025-01-15` |
| **Modified By** | Person | Who last modified | ✅ Yes | (Notion person) |
| **Change History** | Relation | Links to Change History DB | ❌ No | (one-to-many) |
| **YAML Config Version** | Text | Last synced YAML version | ❌ No | `1.2.3` |
| **Notes** | Text | Additional notes or context | ❌ No | `Requires Asset Service integration` |

#### Views

**View 1: By Priority**
- Filter: `Priority` = P0, P1, P2, P3, T, BL
- Sort: Priority (ascending), then Field Path (ascending)
- Group: By Priority

**View 2: By Category**
- Filter: `Status` = active
- Sort: Category (ascending), then Field Path (ascending)
- Group: By Category

**View 3: By Field Type**
- Filter: `Status` = active
- Sort: Field Type (ascending), then Field Path (ascending)
- Group: By Field Type

**View 4: Needs Mapping**
- Filter: `Field Mappings` is empty AND `Status` = active
- Sort: Priority (ascending)

**View 5: Recently Modified**
- Sort: Last Modified (descending)
- Limit: Last 30 days

**View 6: By Provider**
- Filter: `Provider Fields` is not empty
- Group: By Provider (via rollup from Provider Fields relation)

#### Formulas

**Formula 1: Mapping Status**
```
if(empty(prop("Field Mappings")), "⚠️ Unmapped", "✅ Mapped")
```

**Formula 2: Has Dependencies**
```
if(empty(prop("Dependencies")), "No", "Yes")
```

**Formula 3: Days Since Last Modified**
```
dateBetween(prop("Last Modified"), now(), "days")
```

---

### 2.2 Database 2: Provider Fields

**Purpose**: Document all provider-specific telemetry fields, their properties, and availability.

**Database Name**: `Provider Telemetry Fields`

#### Properties

| Property Name | Type | Description | Required | Example |
|--------------|------|-------------|----------|---------|
| **Field Name** | Title | Provider field name | ✅ Yes | `can_speed` |
| **Provider** | Select | Provider name | ✅ Yes | `navixy`, `oem-trackunit`, `oem-volvo`, `future-provider` |
| **Field Path** | Text | Full path in provider packet | ✅ Yes | `params.can_speed` |
| **Data Type** | Select | Provider data type | ✅ Yes | `number`, `string`, `boolean`, `object`, `array` |
| **Unit** | Text | Provider unit (if applicable) | ❌ No | `km/h`, `m/s`, `mph` |
| **Example Value** | Text | Example value from provider | ❌ No | `65.5` |
| **Description** | Text | What provider field represents | ✅ Yes | `CAN bus speed reading` |
| **Availability** | Select | Field availability | ✅ Yes | `always`, `conditional`, `rare`, `deprecated` |
| **Fleeti Fields** | Relation | Links to Fleeti Fields DB | ❌ No | (many-to-many via Field Mappings) |
| **Field Mappings** | Relation | Links to Field Mappings DB | ❌ No | (one-to-many) |
| **Status** | Select | Field status | ✅ Yes | `active`, `deprecated`, `unavailable` |
| **Version Added** | Text | Version when field was documented | ✅ Yes | `1.0.0` |
| **Last Modified** | Date | Last modification date | ✅ Yes | `2025-01-15` |
| **Modified By** | Person | Who last modified | ✅ Yes | (Notion person) |
| **Notes** | Text | Additional notes | ❌ No | `Requires CAN bus connection` |

#### Views

**View 1: By Provider**
- Filter: `Status` = active
- Sort: Provider (ascending), then Field Name (ascending)
- Group: By Provider

**View 2: Unmapped Fields**
- Filter: `Field Mappings` is empty AND `Status` = active
- Sort: Provider (ascending), then Field Name (ascending)

**View 3: By Availability**
- Filter: `Status` = active
- Group: By Availability

**View 4: Recently Added**
- Sort: Version Added (descending)
- Limit: Last 30 days

---

### 2.3 Database 3: Field Mappings

**Purpose**: Document mapping rules between Fleeti fields and provider fields, including priorities, formulas, and transformation logic.

**Database Name**: `Field Mappings`

#### Properties

| Property Name | Type | Description | Required | Example |
|--------------|------|-------------|----------|---------|
| **Mapping Name** | Title | Descriptive mapping name | ✅ Yes | `motion.speed from Navixy` |
| **Fleeti Field** | Relation | Links to Fleeti Fields DB | ✅ Yes | `motion.speed` |
| **Provider** | Select | Provider name | ✅ Yes | `navixy` |
| **Provider Fields** | Relation | Links to Provider Fields DB | ✅ Yes | `can_speed`, `obd_speed`, `speed` (multiple) |
| **Mapping Type** | Select | Type of mapping | ✅ Yes | `direct`, `prioritized`, `calculated`, `aggregated`, `transformed`, `io_mapped`, `asset_integrated` |
| **Priority Order** | Text | Priority order (for prioritized mappings) | ❌ No | `can_speed (1) > obd_speed (2) > speed (3)` |
| **Priority JSON** | Text | Structured priority data (JSON) | ❌ No | `[{"priority": 1, "field": "can_speed"}, {"priority": 2, "field": "obd_speed"}]` |
| **Calculation Type** | Select | How calculation is executed | ❌ No | `formula` (parseable), `function_reference` (backend function), `code_based` (complex logic) |
| **Calculation Formula** | Text | Formula/logic (for calculated fields) | ❌ No | `derive_from_heading(location.heading)` or `(fuel.level_percent / 100) * static.tank_capacity_liters` |
| **Backend Function Name** | Text | Function name in backend registry (if function_reference) | ❌ No | `derive_from_heading` |
| **Function Parameters** | Text | Parameters passed to backend function | ❌ No | `location.heading` |
| **Implementation Location** | Text | File path or documentation link to backend code | ❌ No | `telemetry-transformation-service/src/functions/cardinal.py:derive_cardinal_direction` |
| **Transformation Rule** | Text | Transformation logic (for transformed fields) | ❌ No | `(fuel.level_percent / 100) * static.tank_capacity_liters` |
| **Dependencies** | Relation | Other Fleeti fields this depends on | ❌ No | Links to Fleeti Fields |
| **Unit Conversion** | Text | Unit conversion rule (if applicable) | ❌ No | `multiply by 0.00390625` |
| **Default Value** | Text | Default value if no source available | ❌ No | `null`, `0`, `unknown` |
| **Error Handling** | Text | What to do if mapping fails | ❌ No | `use_fallback`, `return_null`, `throw_error` |
| **I/O Mapping Config** | Text | I/O mapping configuration (JSON) | ❌ No | `{"default_source": "io.inputs.individual.input_1", "installation_metadata": "asset.installation.ignition_input_number"}` |
| **Asset Service Integration** | Text | Asset Service fields needed | ❌ No | `asset.installation.ignition_input_number`, `static.tank_capacity_liters` |
| **Configuration Level** | Select | Where this mapping applies | ✅ Yes | `default`, `customer`, `asset_group`, `asset` |
| **Customer Override** | Text | Customer-specific override (if applicable) | ❌ No | `Customer A: obd_speed > gps_speed` |
| **Status** | Select | Mapping status | ✅ Yes | `active`, `deprecated`, `under_review`, `planned` |
| **Version Added** | Text | Version when mapping was added | ✅ Yes | `1.0.0` |
| **Last Modified** | Date | Last modification date | ✅ Yes | `2025-01-15` |
| **Modified By** | Person | Who last modified | ✅ Yes | (Notion person) |
| **Change History** | Relation | Links to Change History DB | ❌ No | (one-to-many) |
| **YAML Config Version** | Text | Last synced YAML version | ❌ No | `1.2.3` |
| **YAML Path** | Text | Path in YAML config file | ❌ No | `mappings.motion.speed` |
| **Notes** | Text | Additional notes | ❌ No | `CAN speed most accurate, use when available` |

#### Views

**View 1: By Fleeti Field**
- Filter: `Status` = active
- Sort: Fleeti Field (ascending), then Provider (ascending)
- Group: By Fleeti Field

**View 2: By Provider**
- Filter: `Status` = active
- Sort: Provider (ascending), then Fleeti Field (ascending)
- Group: By Provider

**View 3: By Mapping Type**
- Filter: `Status` = active
- Sort: Mapping Type (ascending), then Fleeti Field (ascending)
- Group: By Mapping Type

**View 4: Prioritized Mappings**
- Filter: `Mapping Type` = prioritized AND `Status` = active
- Sort: Fleeti Field (ascending), then Priority Order (ascending)

**View 5: Calculated Mappings**
- Filter: `Mapping Type` = calculated AND `Status` = active
- Sort: Fleeti Field (ascending)

**View 6: Needs YAML Sync**
- Filter: `YAML Config Version` is empty OR `YAML Config Version` ≠ current version
- Sort: Last Modified (descending)

**View 7: By Calculation Type**
- Filter: `Mapping Type` = calculated AND `Status` = active
- Sort: Calculation Type (ascending), then Fleeti Field (ascending)
- Group: By Calculation Type

**View 8: Function References (Needs Implementation)**
- Filter: `Mapping Type` = calculated AND `Calculation Type` = function_reference AND `Implementation Location` is empty
- Sort: Last Modified (descending)

---

### 2.4 Database 4: Change History (Optional but Recommended)

**Purpose**: Track all changes to fields and mappings for audit and versioning.

**Database Name**: `Field Change History`

#### Properties

| Property Name | Type | Description | Required | Example |
|--------------|------|-------------|----------|---------|
| **Change ID** | Title | Unique change identifier | ✅ Yes | `CHG-2025-01-15-001` |
| **Change Type** | Select | Type of change | ✅ Yes | `field_added`, `field_modified`, `field_deprecated`, `mapping_added`, `mapping_modified`, `mapping_deleted`, `priority_updated`, `formula_updated` |
| **Entity Type** | Select | What was changed | ✅ Yes | `fleeti_field`, `provider_field`, `field_mapping` |
| **Entity** | Relation | Links to changed entity | ✅ Yes | Links to Fleeti Fields, Provider Fields, or Field Mappings |
| **Field Changed** | Text | Which property changed | ❌ No | `Priority`, `Calculation Formula`, `Priority Order` |
| **Old Value** | Text | Previous value | ❌ No | `P1` |
| **New Value** | Text | New value | ❌ No | `P0` |
| **Change Reason** | Text | Why the change was made | ❌ No | `Promoted to P0 for customer API requirements` |
| **Version** | Text | Version when change occurred | ✅ Yes | `1.2.3` |
| **Changed By** | Person | Who made the change | ✅ Yes | (Notion person) |
| **Changed At** | Date | When change occurred | ✅ Yes | `2025-01-15 14:30:00` |
| **YAML Synced** | Checkbox | Whether change is reflected in YAML | ❌ No | ☑️ |
| **Related Changes** | Relation | Links to related changes | ❌ No | Links to other Change History entries |

#### Views

**View 1: Recent Changes**
- Sort: Changed At (descending)
- Limit: Last 100 changes

**View 2: By Version**
- Sort: Version (descending), then Changed At (descending)
- Group: By Version

**View 3: Unsynced Changes**
- Filter: `YAML Synced` = false
- Sort: Changed At (ascending)

**View 4: By Change Type**
- Filter: `Changed At` > last 30 days
- Group: By Change Type

---

## 3. Field Type Handling

### 3.1 Direct Mapping

**Description**: 1:1 mapping from provider field to Fleeti field.

**Notion Representation**:
- **Fleeti Field**: `Field Type` = `direct`
- **Field Mapping**: `Mapping Type` = `direct`, `Provider Fields` = single provider field
- **Priority Order**: (empty)
- **Calculation Formula**: (empty)

**Example**:
- **Fleeti Field**: `location.latitude`
- **Field Mapping**: `Mapping Type` = `direct`, `Provider Fields` = `lat` (Navixy)
- **Unit Conversion**: (if needed) `degrees`

**YAML Output**:
```yaml
mappings:
  location.latitude:
    source: "lat"
    unit: "degrees"
```

---

### 3.2 Prioritized Mapping

**Description**: Multiple provider fields map to one Fleeti field with priority order.

**Notion Representation**:
- **Fleeti Field**: `Field Type` = `prioritized`
- **Field Mapping**: `Mapping Type` = `prioritized`, `Provider Fields` = multiple provider fields
- **Priority Order**: `can_speed (1) > obd_speed (2) > speed (3)`
- **Priority JSON**: `[{"priority": 1, "field": "can_speed"}, {"priority": 2, "field": "obd_speed"}, {"priority": 3, "field": "speed"}]`

**Example**:
- **Fleeti Field**: `motion.speed`
- **Field Mapping**: `Mapping Type` = `prioritized`
- **Provider Fields**: `can_speed`, `obd_speed`, `speed` (all Navixy)
- **Priority JSON**: `[{"priority": 1, "field": "can_speed"}, {"priority": 2, "field": "obd_speed"}, {"priority": 3, "field": "speed"}]`

**YAML Output**:
```yaml
mappings:
  motion.speed:
    sources:
      - priority: 1
        field: "can_speed"
      - priority: 2
        field: "obd_speed"
      - priority: 3
        field: "speed"
```

---

### 3.3 Calculated Field

**Description**: Derived from multiple telemetry fields or conditions. Calculations can be executed in two ways:

1. **Function Reference**: References a backend function that implements the calculation logic
2. **Parseable Formula**: Simple mathematical expressions that can be parsed and evaluated directly

**When to Use Each Approach:**

- **Function Reference**: Use for complex logic, algorithms, or reusable transformations (e.g., converting heading to cardinal direction, status computation)
- **Parseable Formula**: Use for simple mathematical operations that can be expressed as a formula (e.g., unit conversions, percentage calculations)

**Notion Representation**:

**Option A: Function Reference (Complex Logic)**
- **Fleeti Field**: `Field Type` = `calculated`, `Calculation Type` = `function_reference`
- **Field Mapping**: `Mapping Type` = `calculated`, `Calculation Type` = `function_reference`
- **Calculation Formula**: Function call string (for YAML reference)
- **Backend Function Name**: Name of function in backend registry
- **Function Parameters**: Parameters passed to function
- **Implementation Location**: File path or documentation link
- **Dependencies**: Relation to other Fleeti fields this depends on

**Example A: Function Reference**
- **Fleeti Field**: `location.cardinal_direction`
- **Field Mapping**: `Mapping Type` = `calculated`, `Calculation Type` = `function_reference`
- **Calculation Formula**: `derive_from_heading(location.heading)` (YAML reference)
- **Backend Function Name**: `derive_from_heading`
- **Function Parameters**: `location.heading`
- **Implementation Location**: `telemetry-transformation-service/src/functions/cardinal.py:derive_cardinal_direction`
- **Dependencies**: `location.heading`

**YAML Output (Function Reference)**:
```yaml
mappings:
  location.cardinal_direction:
    calculation: "derive_from_heading(location.heading)"
    depends_on: ["location.heading"]
```

**Backend Implementation** (for function reference):
```python
# Backend function registry
FUNCTION_REGISTRY = {
    "derive_from_heading": derive_cardinal_direction,
    # ... other functions
}

def derive_cardinal_direction(heading_value):
    """Convert heading (0-359°) to cardinal direction (N, NE, E, etc.)"""
    if heading_value is None:
        return None
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    index = int((heading_value + 22.5) / 45) % 8
    return directions[index]
```

**Option B: Parseable Formula (Simple Math)**
- **Fleeti Field**: `Field Type` = `calculated`, `Calculation Type` = `formula`
- **Field Mapping**: `Mapping Type` = `calculated`, `Calculation Type` = `formula`
- **Calculation Formula**: Parseable mathematical expression
- **Dependencies**: Relation to other Fleeti fields this depends on

**Example B: Parseable Formula**
- **Fleeti Field**: `fuel.consumption_rate_liters_per_100km`
- **Field Mapping**: `Mapping Type` = `calculated`, `Calculation Type` = `formula`
- **Calculation Formula**: `(fuel.consumed_trip / trip.distance) * 100`
- **Dependencies**: `fuel.consumed_trip`, `trip.distance`

**YAML Output (Parseable Formula)**:
```yaml
mappings:
  fuel.consumption_rate_liters_per_100km:
    calculation: "(fuel.consumed_trip / trip.distance) * 100"
    depends_on: ["fuel.consumed_trip", "trip.distance"]
```

**Backend Implementation** (for parseable formula):
```python
# Backend parses and evaluates formula directly
def evaluate_formula(formula_str, telemetry_data):
    """Parse and evaluate formula string"""
    # Replace field references with actual values
    formula = formula_str.replace("fuel.consumed_trip", str(telemetry_data["fuel"]["consumed_trip"]["value"]))
    formula = formula_str.replace("trip.distance", str(telemetry_data["trip"]["distance"]["value"]))
    # Evaluate: (10 / 50) * 100 = 20
    result = safe_eval(formula)  # Use AST evaluation for safety
    return result
```

**Option C: Code-Based (Complex Logic)**
- **Fleeti Field**: `Field Type` = `calculated`, `Calculation Type` = `code_based`
- **Field Mapping**: `Mapping Type` = `calculated`, `Calculation Type` = `code_based`
- **Implementation Location**: Link to code documentation or file
- **Notes**: Explanation of complex logic

**Example C: Code-Based (Status Computation)**
- **Fleeti Field**: `status.top_status`
- **Field Mapping**: `Mapping Type` = `calculated`, `Calculation Type` = `code_based`
- **Implementation Location**: `Wiki/telemetry-status-rules.md`
- **Notes**: `Complex status computation logic with priority hierarchy (Connectivity > Immobilization > Engine > Transit)`

**YAML Output (Code-Based)**:
```yaml
mappings:
  status.top_status:
    calculation: "compute_status(telemetry, config)"  # Reference to code
    depends_on: ["power.ignition", "motion.speed", "connectivity.signal_strength"]
    # Implementation: See Wiki/telemetry-status-rules.md
```

---

### 3.4 Aggregated Field

**Description**: Time-based aggregations or cumulative calculations.

**Notion Representation**:
- **Fleeti Field**: `Field Type` = `aggregated`, `Calculation Formula` = aggregation logic
- **Field Mapping**: `Mapping Type` = `aggregated`, `Calculation Formula` = aggregation formula
- **Dependencies**: Relation to source fields

**Example**:
- **Fleeti Field**: `driving_behavior.daily_summary.driving_duration`
- **Field Mapping**: `Mapping Type` = `aggregated`
- **Calculation Formula**: `cumulative_time_when(motion.speed > 0)`
- **Dependencies**: `motion.speed`

**YAML Output**:
```yaml
mappings:
  driving_behavior.daily_summary.driving_duration:
    aggregation: "cumulative_time_when(motion.speed > 0)"
    depends_on: ["motion.speed"]
```

---

### 3.5 Transformed Field

**Description**: Combines static asset metadata with telemetry.

**Notion Representation**:
- **Fleeti Field**: `Field Type` = `transformed`, `Transformation Rule` = formula text
- **Field Mapping**: `Mapping Type` = `transformed`, `Transformation Rule` = formula text
- **Asset Service Integration**: List of Asset Service fields needed
- **Dependencies**: Relation to source telemetry fields

**Example**:
- **Fleeti Field**: `fuel.level_liters`
- **Field Mapping**: `Mapping Type` = `transformed`
- **Transformation Rule**: `(fuel.level_percent / 100) * static.tank_capacity_liters`
- **Dependencies**: `fuel.level_percent`
- **Asset Service Integration**: `static.tank_capacity_liters`

**YAML Output**:
```yaml
mappings:
  fuel.level_liters:
    source: "fuel.level_percent"
    transformation: "(fuel.level_percent / 100) * static.tank_capacity_liters"
    depends_on: ["fuel.level_percent", "static.tank_capacity_liters"]
```

---

### 3.6 I/O Mapped Field

**Description**: Maps I/O inputs to semantic fields using installation metadata.

**Notion Representation**:
- **Fleeti Field**: `Field Type` = `io_mapped`
- **Field Mapping**: `Mapping Type` = `io_mapped`, `I/O Mapping Config` = JSON config
- **Asset Service Integration**: Installation metadata field name

**Example**:
- **Fleeti Field**: `power.ignition`
- **Field Mapping**: `Mapping Type` = `io_mapped`
- **I/O Mapping Config**: `{"default_source": "io.inputs.individual.input_1", "installation_metadata": "asset.installation.ignition_input_number", "bitmask_extraction": "din"}`
- **Asset Service Integration**: `asset.installation.ignition_input_number`

**YAML Output**:
```yaml
mappings:
  power.ignition:
    io_mapping:
      default_source: "io.inputs.individual.input_1"
      installation_metadata: "asset.installation.ignition_input_number"
      bitmask_extraction: "din"
```

---

### 3.7 Asset Integrated Field

**Description**: Combines asset metadata with telemetry (sensor identity, driver lookup, geofence context).

**Notion Representation**:
- **Fleeti Field**: `Field Type` = `asset_integrated`
- **Field Mapping**: `Mapping Type` = `asset_integrated`, `Asset Service Integration` = integration details
- **Dependencies**: Relation to source telemetry fields

**Example**:
- **Fleeti Field**: `sensors.environment[]` (with sensor identity)
- **Field Mapping**: `Mapping Type` = `asset_integrated`
- **Asset Service Integration**: `asset.accessories[].sensors[]` (metadata) + `sensors.environment[]` (telemetry)
- **Dependencies**: `sensors.environment[]`

**YAML Output**:
```yaml
mappings:
  sensors.environment:
    asset_integration:
      sensor_identity: "asset.accessories[].sensors[]"
      telemetry_source: "sensors.environment[]"
```

---

## 4. Versioning System

### 4.1 Version Numbering Scheme

**Semantic Versioning**: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (field removed, mapping structure changed)
- **MINOR**: New fields added, new mappings added, non-breaking changes
- **PATCH**: Bug fixes, documentation updates, minor corrections

**Examples**:
- `1.0.0` - Initial version
- `1.1.0` - Added 10 new fields
- `1.1.1` - Fixed typo in field description
- `2.0.0` - Removed deprecated field, breaking change

### 4.2 Version Tracking in Notion

**Version Fields**:
- **Fleeti Fields**: `Version Added`, `YAML Config Version`
- **Provider Fields**: `Version Added`
- **Field Mappings**: `Version Added`, `YAML Config Version`
- **Change History**: `Version` (version when change occurred)

**Version Workflow**:
1. When adding/modifying fields or mappings, update `Version Added` or create new Change History entry
2. When syncing to YAML, update `YAML Config Version` to match YAML file version
3. Track all changes in Change History database with version number

### 4.3 Linking Documentation to YAML Versions

**YAML File Structure**:
```yaml
version: "1.2.3"
provider: "navixy"
last_updated: "2025-01-15T14:30:00Z"
mappings:
  # ... mappings ...
```

**Notion Sync**:
- **YAML Config Version** field in Fleeti Fields and Field Mappings should match YAML `version`
- When YAML is updated, update `YAML Config Version` in Notion
- Use Change History to track when versions were synced

### 4.4 Viewing Version History

**Notion Views**:
1. **Change History → By Version**: See all changes in a specific version
2. **Fleeti Fields → Recently Modified**: See fields modified in recent versions
3. **Field Mappings → Needs YAML Sync**: See mappings not yet synced to YAML

**Rollback Process**:
1. Find previous version in Change History
2. Review changes made in that version
3. Create new Change History entries to revert changes
4. Update fields/mappings to previous values
5. Increment version number appropriately

---

## 5. YAML Sync Methodology

### 5.1 Workflow: Documentation-First

**Recommended Workflow**: Update Notion → Generate/Validate YAML → Deploy

**Steps**:
1. **Update Notion Documentation**
   - Add/modify Fleeti fields, provider fields, or mappings
   - Update version numbers
   - Create Change History entries

2. **Generate YAML from Notion**
   - Export Notion data (via API or manual export)
   - Generate YAML structure from Notion data
   - Validate YAML syntax

3. **Validate YAML**
   - Check YAML syntax
   - Verify all mappings are complete
   - Ensure version numbers match

4. **Update Version Numbers**
   - Update `YAML Config Version` in Notion to match generated YAML version
   - Mark Change History entries as `YAML Synced` = true

5. **Commit YAML to Version Control**
   - Commit YAML files to Git repository
   - Tag release with version number

6. **Deploy YAML to Transformation Pipeline**
   - Deploy YAML configs to transformation service
   - Verify deployment success

### 5.2 YAML Generation from Notion

**YAML Structure** (per provider):
```yaml
version: "1.2.3"
provider: "navixy"
last_updated: "2025-01-15T14:30:00Z"
generated_from: "notion-db-version-1.2.3"

mappings:
  # Direct mappings
  location.latitude:
    source: "lat"
    unit: "degrees"
  
  # Prioritized mappings
  motion.speed:
    sources:
      - priority: 1
        field: "can_speed"
      - priority: 2
        field: "obd_speed"
      - priority: 3
        field: "speed"
  
  # Calculated mappings - Function Reference (complex logic)
  location.cardinal_direction:
    calculation: "derive_from_heading(location.heading)"
    calculation_type: "function_reference"  # Optional: indicates backend function
    depends_on: ["location.heading"]
  
  # Calculated mappings - Parseable Formula (simple math)
  fuel.consumption_rate_liters_per_100km:
    calculation: "(fuel.consumed_trip / trip.distance) * 100"
    calculation_type: "formula"  # Optional: indicates parseable formula
    depends_on: ["fuel.consumed_trip", "trip.distance"]
  
  # Transformed mappings
  fuel.level_liters:
    source: "fuel.level_percent"
    transformation: "(fuel.level_percent / 100) * static.tank_capacity_liters"
    depends_on: ["fuel.level_percent", "static.tank_capacity_liters"]
  
  # I/O mappings
  power.ignition:
    io_mapping:
      default_source: "io.inputs.individual.input_1"
      installation_metadata: "asset.installation.ignition_input_number"
      bitmask_extraction: "din"

field_groups:
  p0:
    - location.*
    - status.*
    - motion.speed
  p1_p2:
    - fuel.*
    - driving_behavior.*
  t:
    - device.*
    - connectivity.*
  bl:
    - power.ignition
    - io.*
```

**Generation Logic**:
1. Query Notion API for all Field Mappings where `Provider` = target provider
2. For each mapping, generate YAML entry based on `Mapping Type`:
   - **Direct**: Generate `source` field
   - **Prioritized**: Generate `sources` array with priority order
   - **Calculated**: 
     - If `Calculation Type` = `function_reference`: Generate `calculation` with function call string, optionally include `calculation_type: "function_reference"`
     - If `Calculation Type` = `formula`: Generate `calculation` with parseable formula, optionally include `calculation_type: "formula"`
     - If `Calculation Type` = `code_based`: Generate `calculation` with code reference, include `implementation_location` in comments
   - **Transformed**: Generate `transformation` with formula
   - **I/O Mapped**: Generate `io_mapping` object
3. Include `depends_on` array from Dependencies relation
4. Include priority order, formulas, transformations as stored in Notion
5. Generate `field_groups` from Fleeti Fields `Priority` values

**Example Generation Logic (Python pseudo-code)**:
```python
def generate_calculation_yaml(mapping):
    """Generate YAML for calculated field based on calculation type"""
    calculation_type = mapping.get("Calculation Type")
    calculation_formula = mapping.get("Calculation Formula")
    
    yaml_entry = {
        "depends_on": [dep["Field Path"] for dep in mapping.get("Dependencies", [])]
    }
    
    if calculation_type == "function_reference":
        # Function reference: backend function name
        yaml_entry["calculation"] = calculation_formula  # e.g., "derive_from_heading(location.heading)"
        yaml_entry["calculation_type"] = "function_reference"  # Optional metadata
        # Backend function name stored in Notion but not in YAML (implementation detail)
        
    elif calculation_type == "formula":
        # Parseable formula: simple math expression
        yaml_entry["calculation"] = calculation_formula  # e.g., "(fuel.consumed_trip / trip.distance) * 100"
        yaml_entry["calculation_type"] = "formula"  # Optional metadata
        
    elif calculation_type == "code_based":
        # Code-based: complex logic in separate code file
        yaml_entry["calculation"] = calculation_formula  # e.g., "compute_status(telemetry, config)"
        yaml_entry["implementation_location"] = mapping.get("Implementation Location")
        # Note: Backend must implement this function
    
    return yaml_entry
```

### 5.3 YAML Validation Against Notion

**Validation Checks**:
1. **Completeness**: All active Fleeti fields have mappings (or are marked as unmapped)
2. **Version Sync**: YAML version matches Notion `YAML Config Version`
3. **Priority Order**: Prioritized mappings have valid priority order
4. **Dependencies**: Calculated/transformed fields have all dependencies mapped
5. **Calculation Types**:
   - **Function References**: Backend function name exists in Notion `Backend Function Name` field
   - **Parseable Formulas**: Formula syntax is valid (can be parsed/evaluated)
   - **Code-Based**: Implementation location is documented in Notion
6. **Backend Functions**: All function references have corresponding backend function implementations
7. **Provider Fields**: All provider fields referenced in mappings exist in Provider Fields DB

**Validation Script** (pseudo-code):
```python
def validate_yaml_against_notion(yaml_file, notion_data):
    errors = []
    
    # Check version sync
    if yaml_file.version != notion_data.yaml_config_version:
        errors.append("Version mismatch")
    
    # Check all mappings exist in Notion
    for mapping in yaml_file.mappings:
        if mapping not in notion_data.field_mappings:
            errors.append(f"Mapping {mapping} not found in Notion")
    
    # Check prioritized mappings have priority order
    for mapping in yaml_file.mappings:
        if mapping.type == "prioritized":
            if not mapping.priority_order:
                errors.append(f"Prioritized mapping {mapping} missing priority order")
    
    # Check dependencies
    for mapping in yaml_file.mappings:
        if mapping.depends_on:
            for dep in mapping.depends_on:
                if dep not in notion_data.fleeti_fields:
                    errors.append(f"Dependency {dep} not found")
    
    # Check calculation types
    for mapping in yaml_file.mappings:
        if mapping.type == "calculated":
            calculation_type = mapping.get("calculation_type")
            calculation_formula = mapping.get("calculation")
            
            if calculation_type == "function_reference":
                # Verify backend function exists
                function_name = extract_function_name(calculation_formula)
                notion_mapping = find_notion_mapping(mapping.fleeti_field)
                if notion_mapping.get("Backend Function Name") != function_name:
                    errors.append(f"Function reference {function_name} doesn't match Notion backend function name")
                # Verify function is implemented in backend (separate check)
                
            elif calculation_type == "formula":
                # Validate formula syntax
                if not is_valid_formula(calculation_formula):
                    errors.append(f"Invalid formula syntax: {calculation_formula}")
    
    return errors
```

### 5.4 Handling Conflicts

**Conflict Scenarios**:
1. **Notion Updated, YAML Not**: Update YAML from Notion (documentation-first)
2. **YAML Updated, Notion Not**: Update Notion from YAML (manual sync required)
3. **Both Updated Differently**: Review changes, decide which is source of truth, update both

**Conflict Resolution Process**:
1. Identify conflicting changes
2. Review Change History in Notion
3. Determine source of truth (usually Notion)
4. Update conflicting system to match source of truth
5. Create Change History entry documenting resolution

---

## 6. Developer Guide

### 6.1 Adding a New Fleeti Field

**Steps**:
1. **Create Fleeti Field Entry**
   - Go to `Fleeti Telemetry Fields` database
   - Click "New" to create new entry
   - Fill in required properties:
     - **Field Name**: `fuel.level_liters`
     - **Field Path**: `fuel.level_liters`
     - **Category**: `fuel`
     - **Priority**: `P1`
     - **Field Type**: `transformed`
     - **Structure Type**: `value_unit_object`
     - **Data Type**: `object`
     - **Unit**: `l`
     - **Description**: `Fuel level in liters (calculated from percentage and tank capacity)`
     - **Status**: `active`
     - **Version Added**: `1.2.3` (current version)

2. **Create Field Mapping Entry**
   - Go to `Field Mappings` database
   - Click "New" to create new entry
   - Fill in required properties:
     - **Mapping Name**: `fuel.level_liters from Navixy`
     - **Fleeti Field**: Link to `fuel.level_liters` (created above)
     - **Provider**: `navixy`
     - **Provider Fields**: Link to `fuel.level_percent` (provider field)
     - **Mapping Type**: `transformed`
     - **Transformation Rule**: `(fuel.level_percent / 100) * static.tank_capacity_liters`
     - **Dependencies**: Link to `fuel.level_percent` (Fleeti field)
     - **Asset Service Integration**: `static.tank_capacity_liters`
     - **Configuration Level**: `default`
     - **Status**: `active`
     - **Version Added**: `1.2.3`

3. **Create Change History Entry**
   - Go to `Field Change History` database
   - Click "New" to create new entry
   - Fill in:
     - **Change Type**: `field_added`
     - **Entity Type**: `fleeti_field`
     - **Entity**: Link to `fuel.level_liters`
     - **Version**: `1.2.3`
     - **Changed By**: (your name)
     - **Changed At**: (current date/time)
     - **Change Reason**: `Added fuel level in liters for customer reporting requirements`

4. **Update Version Numbers**
   - Increment version number (minor version for new field)
   - Update `Version Added` in both Fleeti Field and Field Mapping entries

5. **Sync to YAML**
   - Generate YAML from Notion (see Section 8)
   - Validate YAML syntax
   - Update `YAML Config Version` in Notion entries
   - Mark Change History entry as `YAML Synced` = true

---

### 6.2 Adding a New Provider Field

**Steps**:
1. **Create Provider Field Entry**
   - Go to `Provider Telemetry Fields` database
   - Click "New" to create new entry
   - Fill in required properties:
     - **Field Name**: `can_fuel_level`
     - **Provider**: `navixy`
     - **Field Path**: `params.can_fuel_level`
     - **Data Type**: `number`
     - **Unit**: `%`
     - **Example Value**: `75.5`
     - **Description**: `CAN bus fuel level reading (percentage)`
     - **Availability**: `conditional` (requires CAN bus)
     - **Status**: `active`
     - **Version Added**: `1.2.3`

2. **Create Change History Entry**
   - Document the addition in Change History database

3. **Create Mapping (if applicable)**
   - If this provider field maps to a Fleeti field, create Field Mapping entry (see Section 6.1, step 2)

---

### 6.3 Updating a Field Mapping

**Steps**:
1. **Find Existing Mapping**
   - Go to `Field Mappings` database
   - Find mapping to update (use views: By Fleeti Field, By Provider)

2. **Update Mapping Properties**
   - Modify properties as needed (priority order, formula, transformation rule, etc.)
   - Update `Last Modified` date
   - Update `Modified By` person

3. **Create Change History Entry**
   - Document what changed:
     - **Change Type**: `mapping_modified`
     - **Entity Type**: `field_mapping`
     - **Entity**: Link to updated mapping
     - **Field Changed**: `Priority Order` (or whatever changed)
     - **Old Value**: Previous value
     - **New Value**: New value
     - **Change Reason**: Why the change was made
     - **Version**: Increment version number

4. **Sync to YAML**
   - Regenerate YAML from Notion
   - Update `YAML Config Version` in mapping entry
   - Mark Change History entry as synced

---

### 6.4 Updating Priority Order

**Steps**:
1. **Find Prioritized Mapping**
   - Go to `Field Mappings` database
   - Filter: `Mapping Type` = `prioritized`
   - Find mapping to update

2. **Update Priority Order**
   - Modify `Priority Order` text field
   - Update `Priority JSON` field (structured data)
   - Update `Last Modified` date

3. **Update Provider Fields Relation**
   - Ensure all provider fields in priority order are linked in `Provider Fields` relation
   - Order should match priority order

4. **Create Change History Entry**
   - Document priority change

5. **Sync to YAML**
   - Regenerate YAML (priority order will be updated)

---

### 6.5 Adding a Calculated Field

**Steps for Function Reference (Complex Logic)**:

1. **Create Fleeti Field Entry**
   - **Field Name**: `location.cardinal_direction`
   - **Field Type**: `calculated`
   - **Priority**: `P1`
   - **Description**: `Cardinal direction derived from heading (N, NE, E, SE, S, SW, W, NW)`

2. **Create Field Mapping Entry**
   - **Mapping Type**: `calculated`
   - **Calculation Type**: `function_reference`
   - **Calculation Formula**: `derive_from_heading(location.heading)` (YAML reference)
   - **Backend Function Name**: `derive_from_heading`
   - **Function Parameters**: `location.heading`
   - **Implementation Location**: `telemetry-transformation-service/src/functions/cardinal.py:derive_cardinal_direction`
   - **Dependencies**: Link to `location.heading`

3. **Implement Backend Function** (if not exists)
   ```python
   # telemetry-transformation-service/src/functions/cardinal.py
   def derive_cardinal_direction(heading_value):
       """Convert heading (0-359°) to cardinal direction"""
       if heading_value is None:
           return None
       directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
       index = int((heading_value + 22.5) / 45) % 8
       return directions[index]
   
   # Register in function registry
   FUNCTION_REGISTRY["derive_from_heading"] = derive_cardinal_direction
   ```

4. **Create Change History Entry**
   - Document the addition and implementation location

5. **Sync to YAML**
   - Generate YAML (will include `calculation: "derive_from_heading(location.heading)"`)

**Steps for Parseable Formula (Simple Math)**:

1. **Create Fleeti Field Entry**
   - **Field Name**: `fuel.consumption_rate_liters_per_100km`
   - **Field Type**: `calculated`
   - **Priority**: `P1`
   - **Description**: `Fuel consumption rate in liters per 100km`

2. **Create Field Mapping Entry**
   - **Mapping Type**: `calculated`
   - **Calculation Type**: `formula`
   - **Calculation Formula**: `(fuel.consumed_trip / trip.distance) * 100`
   - **Dependencies**: Link to `fuel.consumed_trip`, `trip.distance`
   - **Backend Function Name**: (empty - not needed for formulas)
   - **Implementation Location**: (empty - parsed directly)

3. **Create Change History Entry**
   - Document the addition

4. **Sync to YAML**
   - Generate YAML (will include parseable formula string)

**Decision Guide: Function Reference vs Formula**

**Use Function Reference when:**
- Logic is complex (multiple conditions, loops, algorithms)
- Logic is reusable across multiple fields
- Logic requires external libraries or services
- Logic is better expressed in code than formula
- Examples: `derive_from_heading()`, `compute_status()`, `lookup_driver()`

**Use Parseable Formula when:**
- Logic is simple mathematical operations
- Logic can be expressed as a single expression
- No complex conditionals or loops needed
- Examples: `(fuel.level_percent / 100) * static.tank_capacity_liters`, `speed * 3.6` (convert m/s to km/h)

---

### 6.6 Common Workflows

**Workflow 1: Adding New Provider Support**
1. Create Provider Fields entries for all provider fields
2. Create Field Mappings for each provider field → Fleeti field mapping
3. Generate YAML config for new provider
4. Validate YAML against Notion
5. Deploy YAML to transformation pipeline

**Workflow 2: Deprecating a Field**
1. Update Fleeti Field: `Status` = `deprecated`
2. Update Field Mappings: `Status` = `deprecated` (for all mappings)
3. Create Change History entry: `Change Type` = `field_deprecated`
4. Update YAML (remove or mark as deprecated)
5. Update version (major version if breaking change)

**Workflow 3: Promoting Field Priority**
1. Update Fleeti Field: `Priority` = new priority (e.g., P1 → P0)
2. Create Change History entry: `Change Type` = `priority_updated`
3. Update `field_groups` in YAML if needed
4. Sync to YAML

---

## 7. Notion Setup Instructions

### 7.1 Creating the Databases

**Step 1: Create Fleeti Telemetry Fields Database**
1. In Notion, create a new database
2. Name it: `Fleeti Telemetry Fields`
3. Add all properties listed in Section 2.1
4. Set up relations:
   - `Provider Fields` → Relation to `Provider Telemetry Fields`
   - `Field Mappings` → Relation to `Field Mappings`
   - `Dependencies` → Self-relation (Fleeti Fields → Fleeti Fields)
   - `Change History` → Relation to `Field Change History`

**Step 2: Create Provider Telemetry Fields Database**
1. Create new database: `Provider Telemetry Fields`
2. Add all properties listed in Section 2.2
3. Set up relations:
   - `Fleeti Fields` → Relation to `Fleeti Telemetry Fields`
   - `Field Mappings` → Relation to `Field Mappings`

**Step 3: Create Field Mappings Database**
1. Create new database: `Field Mappings`
2. Add all properties listed in Section 2.3
3. Set up relations:
   - `Fleeti Field` → Relation to `Fleeti Telemetry Fields`
   - `Provider Fields` → Relation to `Provider Telemetry Fields`
   - `Dependencies` → Relation to `Fleeti Telemetry Fields`
   - `Change History` → Relation to `Field Change History`

**Step 4: Create Field Change History Database**
1. Create new database: `Field Change History`
2. Add all properties listed in Section 2.4
3. Set up relations:
   - `Entity` → Relation to `Fleeti Telemetry Fields`, `Provider Telemetry Fields`, `Field Mappings` (multi-select relation)
   - `Related Changes` → Self-relation (Change History → Change History)

### 7.2 Setting Up Views

**For each database, create the views listed in Sections 2.1-2.4:**

1. **Fleeti Telemetry Fields Views**:
   - By Priority
   - By Category
   - By Field Type
   - Needs Mapping
   - Recently Modified
   - By Provider

2. **Provider Telemetry Fields Views**:
   - By Provider
   - Unmapped Fields
   - By Availability
   - Recently Added

3. **Field Mappings Views**:
   - By Fleeti Field
   - By Provider
   - By Mapping Type
   - Prioritized Mappings
   - Calculated Mappings
   - Needs YAML Sync

4. **Field Change History Views**:
   - Recent Changes
   - By Version
   - Unsynced Changes
   - By Change Type

### 7.3 Setting Up Formulas

**Add formulas to Fleeti Telemetry Fields database**:

1. **Mapping Status Formula**:
   - Property name: `Mapping Status`
   - Formula: `if(empty(prop("Field Mappings")), "⚠️ Unmapped", "✅ Mapped")`

2. **Has Dependencies Formula**:
   - Property name: `Has Dependencies`
   - Formula: `if(empty(prop("Dependencies")), "No", "Yes")`

3. **Days Since Last Modified Formula**:
   - Property name: `Days Since Modified`
   - Formula: `dateBetween(prop("Last Modified"), now(), "days")`

### 7.4 Creating Templates

**Create templates for common operations**:

1. **Template: New Fleeti Field**
   - Pre-fill: `Status` = `active`, `Version Added` = (current version)
   - Include instructions in template

2. **Template: New Provider Field**
   - Pre-fill: `Status` = `active`, `Version Added` = (current version)
   - Include instructions in template

3. **Template: New Field Mapping**
   - Pre-fill: `Status` = `active`, `Configuration Level` = `default`, `Version Added` = (current version)
   - Include instructions in template

4. **Template: Calculated Field - Function Reference**
   - Pre-fill: `Mapping Type` = `calculated`, `Calculation Type` = `function_reference`, `Status` = `active`
   - Include instructions: Fill in `Backend Function Name`, `Function Parameters`, `Implementation Location`
   - Include reminder: Backend function must be implemented before deployment

5. **Template: Calculated Field - Parseable Formula**
   - Pre-fill: `Mapping Type` = `calculated`, `Calculation Type` = `formula`, `Status` = `active`
   - Include instructions: Fill in `Calculation Formula` with parseable math expression

6. **Template: Change History Entry**
   - Pre-fill: `Changed At` = `now()`, `Changed By` = (current user)
   - Include instructions in template

### 7.5 Importing Initial Data

**If you have existing field documentation**:

1. **Export existing data** (from markdown files, spreadsheets, etc.)
2. **Transform to Notion format** (CSV import or API)
3. **Import into databases**:
   - Fleeti Fields → `Fleeti Telemetry Fields`
   - Provider Fields → `Provider Telemetry Fields`
   - Mappings → `Field Mappings`
4. **Set up relations** after import (Notion may require manual linking)
5. **Create Change History entries** for initial import

**Import Format (CSV)**:
```csv
Field Name,Field Path,Category,Priority,Field Type,Structure Type,Data Type,Unit,Description,Status,Version Added
fuel.level,fuel.level,fuel,P0,direct,value_unit_object,object,l,Fuel level in liters,active,1.0.0
motion.speed,motion.speed,motion,P0,prioritized,value_unit_object,object,km/h,Vehicle speed,active,1.0.0
```

---

## 8. Automation & Scripts

### 8.1 Notion API Integration

**Prerequisites**:
- Notion API token
- Notion database IDs for all databases

**Script: Export Notion to YAML**
```python
import requests
import yaml
from datetime import datetime

NOTION_API_TOKEN = "your_token"
FLEETI_FIELDS_DB_ID = "db_id_1"
PROVIDER_FIELDS_DB_ID = "db_id_2"
FIELD_MAPPINGS_DB_ID = "db_id_3"

def get_notion_database(database_id):
    """Query Notion database via API"""
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_API_TOKEN}",
        "Notion-Version": "2022-06-28"
    }
    response = requests.post(url, headers=headers)
    return response.json()

def generate_yaml_from_notion(provider="navixy"):
    """Generate YAML config from Notion data"""
    # Get all field mappings for provider
    mappings_db = get_notion_database(FIELD_MAPPINGS_DB_ID)
    
    # Filter by provider and active status
    active_mappings = [
        m for m in mappings_db["results"]
        if m["properties"]["Provider"]["select"]["name"] == provider
        and m["properties"]["Status"]["select"]["name"] == "active"
    ]
    
    # Build YAML structure
    yaml_data = {
        "version": "1.2.3",  # Get from Notion
        "provider": provider,
        "last_updated": datetime.now().isoformat(),
        "generated_from": "notion-db-version-1.2.3",
        "mappings": {}
    }
    
    # Process each mapping
    for mapping in active_mappings:
        fleeti_field = mapping["properties"]["Fleeti Field"]["relation"][0]["id"]
        mapping_type = mapping["properties"]["Mapping Type"]["select"]["name"]
        
        # Generate mapping entry based on type
        if mapping_type == "direct":
            yaml_data["mappings"][fleeti_field] = {
                "source": mapping["properties"]["Provider Fields"]["relation"][0]["id"]
            }
        elif mapping_type == "prioritized":
            # Parse Priority JSON
            priority_json = json.loads(mapping["properties"]["Priority JSON"]["rich_text"][0]["plain_text"])
            yaml_data["mappings"][fleeti_field] = {
                "sources": [
                    {"priority": p["priority"], "field": p["field"]}
                    for p in priority_json
                ]
            }
        elif mapping_type == "calculated":
            calculation_type = mapping["properties"]["Calculation Type"]["select"]["name"]
            calculation_formula = mapping["properties"]["Calculation Formula"]["rich_text"][0]["plain_text"]
            
            yaml_entry = {
                "calculation": calculation_formula
            }
            
            # Add calculation_type metadata (optional but helpful)
            if calculation_type:
                yaml_entry["calculation_type"] = calculation_type
            
            # Add depends_on if available
            dependencies = mapping["properties"]["Dependencies"]["relation"]
            if dependencies:
                yaml_entry["depends_on"] = [dep["id"] for dep in dependencies]
            
            # For code_based, add implementation location as comment
            if calculation_type == "code_based":
                impl_location = mapping["properties"]["Implementation Location"]["rich_text"][0]["plain_text"]
                yaml_entry["# implementation_location"] = impl_location
            
            yaml_data["mappings"][fleeti_field] = yaml_entry
        elif mapping_type == "transformed":
            transformation_rule = mapping["properties"]["Transformation Rule"]["rich_text"][0]["plain_text"]
            yaml_data["mappings"][fleeti_field] = {
                "transformation": transformation_rule
            }
        # ... handle other mapping types (io_mapped, asset_integrated, etc.)
    
    # Write YAML file
    with open(f"{provider}-mapping.yaml", "w") as f:
        yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False)
    
    return yaml_data

if __name__ == "__main__":
    generate_yaml_from_notion("navixy")
```

### 8.2 YAML Validation Script

**Script: Validate YAML Against Notion**
```python
import yaml
import requests

def validate_yaml_against_notion(yaml_file_path, notion_data):
    """Validate YAML file against Notion documentation"""
    with open(yaml_file_path, "r") as f:
        yaml_data = yaml.safe_load(f)
    
    errors = []
    warnings = []
    
    # Check version sync
    notion_version = notion_data.get("yaml_config_version")
    yaml_version = yaml_data.get("version")
    if notion_version != yaml_version:
        errors.append(f"Version mismatch: Notion={notion_version}, YAML={yaml_version}")
    
    # Check all mappings exist in Notion
    notion_mappings = {m["fleeti_field"] for m in notion_data["field_mappings"]}
    yaml_mappings = set(yaml_data["mappings"].keys())
    
    missing_in_notion = yaml_mappings - notion_mappings
    if missing_in_notion:
        errors.append(f"Mappings in YAML but not in Notion: {missing_in_notion}")
    
    missing_in_yaml = notion_mappings - yaml_mappings
    if missing_in_yaml:
        warnings.append(f"Mappings in Notion but not in YAML: {missing_in_yaml}")
    
    # Check prioritized mappings have priority order
    for fleeti_field, mapping in yaml_data["mappings"].items():
        if "sources" in mapping:
            priorities = [s.get("priority") for s in mapping["sources"]]
            if None in priorities:
                errors.append(f"Prioritized mapping {fleeti_field} missing priority values")
    
    return errors, warnings

if __name__ == "__main__":
    # Load Notion data (from API or export)
    notion_data = load_notion_data()
    
    # Validate YAML
    errors, warnings = validate_yaml_against_notion("navixy-mapping.yaml", notion_data)
    
    if errors:
        print("ERRORS:")
        for error in errors:
            print(f"  - {error}")
    
    if warnings:
        print("WARNINGS:")
        for warning in warnings:
            print(f"  - {warning}")
```

### 8.3 CI/CD Integration

**GitHub Actions Workflow**:
```yaml
name: Validate YAML Against Notion

on:
  pull_request:
    paths:
      - 'configs/**/*.yaml'
  push:
    branches:
      - main

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install pyyaml requests
      
      - name: Fetch Notion data
        env:
          NOTION_API_TOKEN: ${{ secrets.NOTION_API_TOKEN }}
        run: |
          python scripts/fetch_notion_data.py
      
      - name: Validate YAML files
        run: |
          python scripts/validate_yaml.py
      
      - name: Check version sync
        run: |
          python scripts/check_version_sync.py
```

---

## 9. Best Practices

### 9.1 Documentation Maintenance

1. **Always create Change History entries** when modifying fields or mappings
2. **Update version numbers** when making changes
3. **Sync to YAML** after significant changes
4. **Validate YAML** before deploying
5. **Review unmapped fields** regularly (use "Needs Mapping" view)

### 9.2 Field Naming Conventions

1. **Use semantic names**: `fuel.level`, not `fuel_level` or `fuelLevel`
2. **Follow path structure**: Match JSON structure (`location.latitude`, not `lat`)
3. **Be consistent**: Use same naming pattern across all fields

### 9.3 Mapping Rules

1. **Document priority rationale**: Why is `can_speed` priority 1?
2. **Include unit conversions**: Document unit conversion rules
3. **Specify error handling**: What happens if mapping fails?
4. **Track dependencies**: Always link dependent fields
5. **Choose calculation type appropriately**:
   - Use **function_reference** for complex logic, algorithms, reusable transformations (e.g., `derive_from_heading()`, `compute_status()`)
   - Use **formula** for simple mathematical expressions (e.g., `(fuel.level_percent / 100) * static.tank_capacity_liters`)
   - Use **code_based** for very complex logic that requires separate code files (e.g., status computation)
   - Always document `Backend Function Name` and `Implementation Location` for function references
6. **Verify backend functions exist**: Before deploying YAML with function references, ensure backend functions are implemented and registered in the function registry

### 9.4 Version Management

1. **Use semantic versioning**: `MAJOR.MINOR.PATCH`
2. **Increment appropriately**: 
   - PATCH for bug fixes
   - MINOR for new fields/mappings
   - MAJOR for breaking changes
3. **Keep versions in sync**: Notion and YAML versions must match

### 9.5 Collaboration

1. **Assign owners**: Use `Modified By` field to track who made changes
2. **Use Change History**: Document why changes were made
3. **Review before sync**: Review changes before syncing to YAML
4. **Communicate breaking changes**: Use Change History `Change Reason` field

---

## 10. Troubleshooting

### 10.1 Common Issues

**Issue: Relations not working**
- **Solution**: Ensure both databases have the relation property set up correctly
- **Check**: Both sides of relation must be configured

**Issue: Formulas not calculating**
- **Solution**: Check formula syntax, ensure property names match exactly
- **Check**: Property types must be compatible (e.g., date for dateBetween)

**Issue: YAML generation fails**
- **Solution**: Check Notion API token, database IDs, and API rate limits
- **Check**: Ensure all required properties are filled in

**Issue: Version sync mismatch**
- **Solution**: Update `YAML Config Version` in Notion after generating YAML
- **Check**: Ensure version numbers follow semantic versioning

### 10.2 Getting Help

- **Notion Documentation**: https://www.notion.so/help
- **Notion API Docs**: https://developers.notion.com/
- **Internal Wiki**: See `Wiki/telemetry-system-specification.md`
- **Schema Reference**: See `working/fleeti-telemetry-schema-specification.md`

---

## Appendix A: Field Granularity Decision

**Decision**: Document fields at **semantic level** (`fuel.level`), not property level (`fuel.level.value`).

**Rationale**:
- Matches how developers think about the data model
- Aligns with YAML config structure (mappings are at semantic level)
- Reduces documentation complexity (fewer entries to maintain)
- Structure information (`{ value, unit }` vs simple value) is metadata, not separate fields

**Examples**:
- ✅ **Fleeti Field**: `fuel.level` (structure: `{ value: number, unit: "l" }`)
- ❌ **NOT**: `fuel.level.value` and `fuel.level.unit` as separate fields

**Implementation**:
- Document `fuel.level` as single field entry
- Use `Structure Type` property to indicate structure (`value_unit_object`)
- Use `Data Type` property to indicate JSON type (`object`)
- Use `Unit` property to indicate standard unit (`l`)

---

## Appendix B: Database Relationship Diagram

```
┌─────────────────────────┐
│  Fleeti Telemetry       │
│  Fields                 │
│                         │
│  - Field Name           │
│  - Category             │
│  - Priority             │
│  - Field Type           │
│  - Description          │
└──────────┬──────────────┘
           │
           │ 1-to-many
           │
           ▼
┌─────────────────────────┐
│  Field Mappings         │
│                         │
│  - Mapping Name         │
│  - Fleeti Field (FK)    │
│  - Provider Fields (FK) │
│  - Mapping Type         │
│  - Priority Order       │
│  - Formula              │
└──────────┬──────────────┘
           │
           │ many-to-many
           │
           ▼
┌─────────────────────────┐
│  Provider Telemetry     │
│  Fields                 │
│                         │
│  - Field Name           │
│  - Provider             │
│  - Data Type            │
│  - Unit                 │
│  - Description          │
└─────────────────────────┘

┌─────────────────────────┐
│  Field Change History   │
│                         │
│  - Change Type          │
│  - Entity (FK)          │
│  - Old Value            │
│  - New Value            │
│  - Version              │
│  - Changed By           │
└─────────────────────────┘
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-01-XX | Documentation Team | Initial methodology document |

---

**End of Document**

