# Project Reorganization & Notion Sync Infrastructure - Implementation Guide

This document provides a complete step-by-step guide for implementing the project reorganization and Notion sync infrastructure.

## Overview

This reorganization introduces:
- **Notion sync infrastructure** for bidirectional synchronization between local markdown files and Notion databases
- **Reorganized folder structure** to support Notion workflows and YAML configuration generation
- **Automation scripts** for sync, validation, conflict detection, and YAML generation
- **Safety mechanisms** including backups, validation, and conflict resolution

## Phase 1: Folder Structure Setup

### Step 1.1: Create New Directories

The new folder structure has been created with the following directories:

```
Fleeti - Telemetry Mapping/
├── notion/                 # NEW: Notion-synced markdown files
│   ├── fleeti-fields/
│   ├── provider-fields/
│   └── field-mappings/
├── configs/                # NEW: YAML configuration files
├── scripts/                # RENAMED: From Scripts/ (lowercase)
│   ├── notion/
│   └── validation/
├── docs/                   # EXISTING: Reference documentation
├── Wiki/                   # EXISTING: Canonical specifications
└── working/                # EXISTING: Work-in-progress documents
```

### Step 1.2: Move Existing Scripts

**Action Required:**

1. Move existing validation scripts:
   ```bash
   # Windows PowerShell
   Move-Item "Scripts\validate_navixy_completeness.py" "scripts\validation\"
   Move-Item "Scripts\navixy_fields_completeness_check.md" "scripts\validation\"
   ```

2. Delete old Scripts folder (after verifying move):
   ```bash
   Remove-Item -Recurse -Force "Scripts"
   ```

### Step 1.3: Create Empty Subdirectories

**Action Required:**

Create empty subdirectories for field files:

```bash
# Create field file directories
New-Item -ItemType Directory -Force "notion\fleeti-fields\fields"
New-Item -ItemType Directory -Force "notion\provider-fields\providers\navixy"
New-Item -ItemType Directory -Force "notion\provider-fields\providers\oem-trackunit"
New-Item -ItemType Directory -Force "notion\field-mappings\mappings"
```

## Phase 2: Notion Setup

### Step 2.1: Create Notion Databases

Follow the instructions in `working/notion-documentation-methodology.md` Section 7 to create:

1. **Fleeti Telemetry Fields** database
2. **Provider Telemetry Fields** database
3. **Field Mappings** database
4. **Field Change History** database (optional but recommended)

### Step 2.2: Configure Notion API Access

1. **Create Notion Integration:**
   - Go to https://www.notion.so/my-integrations
   - Click "New integration"
   - Name it "Fleeti Telemetry Sync"
   - Select capabilities: Read, Update, Insert content
   - Copy the "Internal Integration Token"

2. **Share Databases with Integration:**
   - Open each Notion database
   - Click "..." → "Connections" → Add your integration
   - Repeat for all databases

3. **Get Database IDs:**
   - Open each database in Notion
   - Copy the database URL
   - Extract the database ID from the URL (the part between the last `/` and `?`)
   - Example: `https://notion.so/workspace/abc123def456?v=...` → ID is `abc123def456`

### Step 2.3: Configure Scripts

**Action Required:**

1. Copy configuration template:
   ```bash
   Copy-Item "scripts\notion\config.yaml.template" "scripts\notion\config.yaml"
   ```

2. Edit `scripts/notion/config.yaml`:
   ```yaml
   notion:
     api_token: "secret_xxx..."  # From Step 2.2
     databases:
       fleeti_fields:
         id: "abc123def456"  # From Step 2.2
       provider_fields:
         id: "def456ghi789"
       field_mappings:
         id: "ghi789jkl012"
   ```

   **OR** set environment variables:
   ```powershell
   $env:NOTION_API_TOKEN = "secret_xxx..."
   $env:NOTION_FLEETI_FIELDS_DB_ID = "abc123def456"
   $env:NOTION_PROVIDER_FIELDS_DB_ID = "def456ghi789"
   $env:NOTION_FIELD_MAPPINGS_DB_ID = "ghi789jkl012"
   ```

## Phase 3: Install Dependencies

### Step 3.1: Install Python Dependencies

**Action Required:**

1. Create virtual environment (recommended):
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. Install dependencies:
   ```bash
   pip install -r scripts\notion\requirements.txt
   ```

### Step 3.2: Verify Installation

Test that scripts can run:

```bash
python scripts\notion\validate_sync.py --help
python scripts\notion\sync_to_notion.py --help
```

## Phase 4: Initial Content Migration

### Step 4.1: Create Sample Field Files

**Action Required:**

1. Create a sample Fleeti field file in `notion/fleeti-fields/fields/location-latitude.md`:
   - Use the template from `notion/fleeti-fields/README.md`
   - Fill in frontmatter and content
   - Leave `notion_id` empty (will be set after first sync)

2. Create a sample provider field file in `notion/provider-fields/providers/navixy/lat.md`
   - Use the template from `notion/provider-fields/README.md`
   - Fill in frontmatter and content

3. Create a sample mapping file in `notion/field-mappings/mappings/location-latitude-navixy-mapping.md`
   - Use the template from `notion/field-mappings/README.md`
   - Fill in frontmatter and content

### Step 4.2: Validate Initial Files

**Action Required:**

```bash
# Validate all files
python scripts\notion\validate_sync.py --database all

# Check for issues and fix them before syncing
```

### Step 4.3: Test Sync (Dry Run)

**Action Required:**

```bash
# Test sync without applying changes
python scripts\notion\sync_to_notion.py --database fleeti-fields --dry-run

# Review output and verify everything looks correct
```

### Step 4.4: Perform First Sync

**Action Required:**

```bash
# Sync to Notion (actual)
python scripts\notion\sync_to_notion.py --database fleeti-fields

# Check Notion database to verify files were created
# Update notion_id in frontmatter if needed (future enhancement)
```

## Phase 5: Update Documentation

### Step 5.1: Update Main README

**Action Required:**

The main README has been updated with the new folder structure. Review and adjust as needed.

### Step 5.2: Create Implementation Checklist

**Action Required:**

Create a checklist document for tracking implementation progress:

```markdown
# Notion Sync Implementation Checklist

## Setup
- [ ] Notion databases created
- [ ] Notion API integration configured
- [ ] Database IDs collected
- [ ] Configuration file created
- [ ] Dependencies installed

## Initial Sync
- [ ] Sample field files created
- [ ] Files validated
- [ ] Dry-run sync tested
- [ ] First sync completed

## Workflow Testing
- [ ] Local → Notion sync tested
- [ ] Notion → Local sync tested
- [ ] Conflict detection tested
- [ ] YAML generation tested
```

## Phase 6: Workflow Validation

### Step 6.1: Test Local → Notion Sync

**Action Required:**

1. Modify a local markdown file
2. Validate changes:
   ```bash
   python scripts\notion\validate_sync.py --database fleeti-fields
   ```
3. Check for conflicts:
   ```bash
   python scripts\notion\detect_conflicts.py --database fleeti-fields
   ```
4. Sync to Notion:
   ```bash
   python scripts\notion\sync_to_notion.py --database fleeti-fields
   ```
5. Verify changes in Notion

### Step 6.2: Test Notion → Local Sync

**Action Required:**

1. Make a change in Notion
2. Pull changes locally:
   ```bash
   python scripts\notion\sync_from_notion.py --database fleeti-fields
   ```
3. Verify local file was updated

### Step 6.3: Test Conflict Detection

**Action Required:**

1. Modify a file locally
2. Modify the same entry in Notion
3. Run conflict detection:
   ```bash
   python scripts\notion\detect_conflicts.py --database fleeti-fields
   ```
4. Review conflict report
5. Resolve conflict manually

### Step 6.4: Test YAML Generation

**Action Required:**

1. Ensure field mappings are created and synced
2. Generate YAML:
   ```bash
   python scripts\notion\generate_yaml.py --provider navixy --dry-run
   ```
3. Review generated YAML
4. Generate actual YAML:
   ```bash
   python scripts\notion\generate_yaml.py --provider navixy --output configs\navixy-mapping.yaml
   ```
5. Validate YAML syntax:
   ```bash
   python scripts\notion\validate_sync.py --yaml configs\navixy-mapping.yaml
   ```

## Phase 7: Production Readiness

### Step 7.1: Create Backup Strategy

**Action Required:**

1. Set up automated backups before sync operations
2. Test backup restore process
3. Document backup retention policy

### Step 7.2: Establish Workflow Guidelines

**Action Required:**

1. Document workflow for team members
2. Create pull request checklist
3. Set up code review process for Notion changes

### Step 7.3: Monitor and Iterate

**Action Required:**

1. Monitor sync operations for errors
2. Collect feedback from team
3. Iterate on workflow and scripts as needed

## Troubleshooting

### Common Issues

**Issue: "NOTION_API_TOKEN not found"**
- Solution: Set environment variable or update config.yaml

**Issue: "Database ID not found"**
- Solution: Verify database IDs in config.yaml or environment variables
- Check that databases are shared with integration

**Issue: "Lock file exists"**
- Solution: Check if another sync is running, or manually remove `.notion-sync.lock`

**Issue: "Conflict detected"**
- Solution: Run `detect_conflicts.py` to view conflicts, then resolve manually

**Issue: "Validation errors"**
- Solution: Run `validate_sync.py` to see specific errors, fix frontmatter or content

### Getting Help

- Review `scripts/notion/README.md` for script usage
- Check `notion/README.md` for workflow documentation
- Consult `working/notion-documentation-methodology.md` for Notion setup

## Next Steps

After completing this reorganization:

1. **Migrate existing field documentation** to Notion format
2. **Set up automated sync workflows** (CI/CD integration)
3. **Train team members** on Notion sync workflow
4. **Create field documentation templates** for common patterns
5. **Integrate YAML generation** into deployment pipeline

## Summary

This reorganization establishes:
- ✅ Clear folder structure for Notion sync
- ✅ Automation scripts for sync operations
- ✅ Safety mechanisms (validation, backups, conflict detection)
- ✅ Comprehensive documentation
- ✅ YAML generation from Notion documentation

The infrastructure is ready for use once Notion databases are created and configured.

