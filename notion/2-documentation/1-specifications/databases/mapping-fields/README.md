**Status:** 🎯 Structure Created - Content To Be Developed

## Purpose

The Mapping Fields Database contains field transformation rules and priority chains that link provider fields to Fleeti fields.

## What This Database Contains

- **Direct mappings**: 1:1 provider field → Fleeti field mappings
- **Priority chains**: Multiple provider fields → one Fleeti field (with priority order)
- **Calculation rules**: Formulas and logic for calculated fields
- **I/O mappings**: Raw I/O fields → semantic fields (with installation metadata)
- **Transformation logic**: Static data transformations (e.g., fuel level % → liters)

## Database Structure

[Column structure and schema to be defined]

## How to Use

This database is used to:
- Generate configuration files for the transformation pipeline
- Understand how provider data maps to Fleeti format
- Track mapping rule changes
- Support historical recalculation

## Related Documentation

- **[Provider Fields Database](../provider-fields/README.md)**: Source provider fields
- **[Fleeti Fields Database](../fleeti-fields/README.md)**: Target Fleeti fields
- **[Mapping Rules](../../2-field-mappings/mapping-rules.md)**: Mapping rules documentation

---

**Last Updated:** 2025-01-XX  
**Status:** 🎯 Structure Created - Content To Be Developed

