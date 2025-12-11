# YAML Configuration Files

This directory contains YAML configuration files that define field mappings and transformation rules for telemetry providers.

## Overview

YAML configs are **generated from Notion documentation** using `scripts/notion/generate_yaml.py`. The generation process:

1. Reads Notion databases (Fleeti Fields, Provider Fields, Field Mappings)
2. Converts mapping rules to YAML structure
3. Validates YAML syntax
4. Outputs provider-specific config files

## Configuration Files

Each provider has its own YAML configuration file:

- `navixy-mapping.yaml` - Navixy provider mappings
- `oem-trackunit-mapping.yaml` - OEM TrackUnit mappings
- `{provider}-mapping.yaml` - Future provider mappings

## File Structure

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
  
  # Calculated mappings
  location.cardinal_direction:
    calculation: "derive_from_heading(location.heading)"
    depends_on: ["location.heading"]
  
  # Transformed mappings
  fuel.level_liters:
    source: "fuel.level_percent"
    transformation: "(fuel.level_percent / 100) * static.tank_capacity_liters"
    depends_on: ["fuel.level_percent", "static.tank_capacity_liters"]

field_groups:
  p0:
    - location.*
    - motion.speed
  p1_p2:
    - fuel.*
```

## Workflow

### Generating YAML from Notion

1. **Update Notion documentation** - Add/modify fields and mappings in Notion
2. **Generate YAML** - Run `python scripts/notion/generate_yaml.py --provider navixy`
3. **Validate YAML** - YAML syntax is validated automatically
4. **Review changes** - Review generated YAML file
5. **Commit to version control** - Commit YAML file after validation

### Manual YAML Editing (Not Recommended)

While YAML files can be edited manually, this is **not recommended** because:
- Changes will be overwritten on next generation
- Risk of syntax errors
- Version sync issues with Notion

**Recommended approach**: Update Notion, then regenerate YAML.

## Version Synchronization

YAML files include version numbers that should match Notion database versions:

- YAML `version` field should match Notion `YAML Config Version`
- Update versions in Notion when regenerating YAML
- Track version changes in Change History database

## Validation

YAML files are validated for:
- Syntax correctness
- Required fields present
- Mapping completeness
- Version consistency with Notion

Run validation:
```bash
python scripts/notion/validate_sync.py --yaml configs/navixy-mapping.yaml
```

## Provider-Specific Configs

### Navixy

- **File**: `navixy-mapping.yaml`
- **Fields**: ~340 provider fields mapped
- **Status**: Active development

### OEM TrackUnit

- **File**: `oem-trackunit-mapping.yaml`
- **Fields**: Provider fields being documented
- **Status**: In progress

## Related Documentation

- `scripts/notion/generate_yaml.py` - YAML generation script
- `working/notion-documentation-methodology.md` - Notion methodology (Section 5: YAML Sync)
- `notion/README.md` - Notion sync overview

