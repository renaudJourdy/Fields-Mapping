**Status:** 🎯 Structure Created - Content To Be Developed

# Purpose

The Change History Database tracks all changes to fields and mappings for audit, versioning, and compliance purposes. This database is **optional but recommended** for maintaining a complete audit trail.

**Important:** This database is optional. If not implemented, the `Change History` relation columns in other databases can be left empty or removed.

# What This Database Contains

- **Change records**: All modifications to Fleeti Fields, Provider Fields, and Field Mappings
- **Change metadata**: Who changed what, when, and why
- **Version tracking**: Links changes to configuration versions
- **Sync status**: Tracks whether changes are reflected in generated YAML configurations

# Database Structure

## Column Definitions

| Column Name | Type | Required | Description | Example | Why It's Important |
|-------------|------|----------|-------------|---------|-------------------|
| **Change ID** | Title | ✅ Yes | Unique change identifier | `CHG-2025-01-15-001` | Primary key - uniquely identifies each change record. Enables change tracking and audit queries. |
| **Change Type** | Select | ✅ Yes | Type of change | `field_added`, `field_modified`, `field_deprecated`, `mapping_added`, `mapping_modified`, `mapping_deleted`, `priority_updated`, `formula_updated` | Categorizes changes for filtering and reporting. Options: `field_added`, `field_modified`, `field_deprecated`, `mapping_added`, `mapping_modified`, `mapping_deleted`, `priority_updated`, `formula_updated`, `unit_changed`, `description_updated`. |
| **Entity Type** | Select | ✅ Yes | What type of entity was changed | `fleeti_field`, `provider_field`, `field_mapping` | Identifies which database the change affects. Enables filtering by entity type. Required for proper relation setup. |
| **Entity** | Relation | ✅ Yes | Links to changed entity | Links to Fleeti Fields, Provider Fields, or Field Mappings | Direct link to the entity that was changed. Enables navigation from change record to entity. Critical for audit trail. |
| **Field Changed** | Text | ❌ No | Which property/column changed | `Priority`, `Calculation Formula`, `Priority Order`, `Status` | Documents which specific field/property was modified. Useful for detailed change tracking and impact analysis. |
| **Old Value** | Text | ❌ No | Previous value before change | `P1`, `can_speed`, `active` | Captures the value before change. Critical for rollback scenarios and understanding change impact. |
| **New Value** | Text | ❌ No | New value after change | `P0`, `can_speed, obd_speed`, `deprecated` | Captures the value after change. Enables before/after comparison and change validation. |
| **Change Reason** | Text | ❌ No | Why the change was made | `Promoted to P0 for customer API requirements`, `Updated priority based on field availability analysis` | Documents the business reason for the change. Important for compliance, audit, and understanding change context. |
| **Version** | Text | ✅ Yes | Configuration version when change occurred | `1.2.3` | Links change to configuration version. Enables version-based change queries and rollback planning. |
| **Changed By** | Person | ✅ Yes | Who made the change | (Notion person) | Accountability and audit trail. Enables questions and collaboration. Critical for compliance. |
| **Changed At** | Date | ✅ Yes | When change occurred | `2025-01-15 14:30:00` | Timestamp of change. Enables chronological change tracking and "recent changes" views. |
| **YAML Synced** | Checkbox | ❌ No | Whether change is reflected in YAML config | ☑️ | Tracks sync status with generated configuration. Helps identify changes needing configuration regeneration. Critical for configuration management workflow. |
| **Related Changes** | Relation | ❌ No | Links to related changes | Links to other Change History entries | Tracks related changes (e.g., when multiple fields change together). Enables change grouping and batch operations. |

## Primary Key

**Change ID** serves as the primary key. Should be unique and follow format: `CHG-YYYY-MM-DD-###` (e.g., `CHG-2025-01-15-001`).

## Indexes & Performance

- **Index on Entity + Changed At**: Fast lookups of changes for a specific entity
- **Index on Changed At**: Efficient chronological sorting
- **Index on Change Type**: Fast filtering by change type
- **Index on Version**: Quick version-based queries
- **Index on YAML Synced**: Fast identification of unsynced changes

## Validation Rules

- **Change ID**: Must be unique
- **Entity Type**: Must be one of: `fleeti_field`, `provider_field`, `field_mapping`
- **Entity**: Must link to an entity matching the Entity Type
- **Changed At**: Must be a valid timestamp
- **Version**: Should follow semantic versioning (e.g., `1.2.3`)

## Recommended Views

**View 1: Recent Changes**
- Sort: Changed At (descending)
- Limit: Last 100 changes
- Purpose: Quick overview of recent activity

**View 2: By Version**
- Sort: Version (descending), then Changed At (descending)
- Group: By Version
- Purpose: See all changes in a specific configuration version

**View 3: Unsynced Changes**
- Filter: `YAML Synced` = false
- Sort: Changed At (ascending)
- Purpose: Identify changes needing configuration regeneration

**View 4: By Change Type**
- Filter: `Changed At` > last 30 days
- Group: By Change Type
- Purpose: Analyze change patterns and frequency

**View 5: By Entity**
- Filter: Entity = [selected entity]
- Sort: Changed At (descending)
- Purpose: Complete change history for a specific field or mapping

# How to Use

This database is used to:
- Track all changes to fields and mappings
- Maintain audit trail for compliance
- Identify changes needing configuration regeneration
- Analyze change patterns and frequency
- Support rollback planning

# Related Documentation

- **[📥 Provider Fields Database](../1-provider-fields/README.md)**: Source of provider field changes
- **[🎯 Fleeti Fields Database](../2-fleeti-fields/README.md)**: Source of Fleeti field changes
- **[🔀 Mapping Fields Database](../3-mapping-fields/README.md)**: Source of mapping rule changes
- **[Configuration Management](../../E5-Configuration-Management/README.md)**: How changes trigger configuration updates

---

**Last Updated:** 2025-01-XX  
**Status:** 🎯 Structure Created - Content To Be Developed

