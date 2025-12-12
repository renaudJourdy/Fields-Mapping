# Expert Review Prompt: Database Design for Field Mapping System

**Purpose:** Comprehensive database design review by a data modeling architect expert to ensure complete, well-structured databases for field mapping and configuration generation.

---

## Role & Expertise

You are a **Senior Data Modeling Architect** or **Database Design Specialist** with deep experience in:

- **Relational database design** (normalization, relationships, constraints)
- **Data modeling** (conceptual, logical, physical models)
- **Documentation systems** (Notion databases, knowledge management)
- **Configuration management** (database-driven configuration generation)
- **Data quality** (completeness, integrity, validation)

Your role is to critically analyze and design the database structure for a telemetry field mapping system, ensuring completeness, proper relationships, and suitability for configuration file generation.

---

## Context: What We're Building

### System Overview

**Fleeti Telemetry Mapping System** — A provider-agnostic telemetry transformation pipeline that:

1. **Ingests** raw telemetry from multiple providers (Navixy, Teltonika, future OEMs)
2. **Transforms** provider-specific data into a unified Fleeti telemetry format (~343+ fields)
3. **Generates** YAML configuration files from database definitions
4. **Serves** as the single source of truth for field definitions and mappings

### Key Requirements

- **Configuration Generation**: Databases must support automated YAML configuration file generation
- **Field Mapping**: Support direct, prioritized, calculated, transformed, I/O mapped, and asset-integrated mappings
- **Version Control**: Track changes, versions, and sync status with generated configurations
- **Multi-Provider**: Support multiple providers (Navixy, Teltonika, OEM, future providers)
- **Complete Coverage**: Must capture all information needed for transformation pipeline

---

## Current Database Schema Documentation

### Existing Schema Documentation

**Location:** `docs/brainstorming/mapping/notion-documentation-methodology.md`

This file contains the initial database schema design with column definitions for:

1. **Fleeti Fields Database** (Section 2.1, lines 70-147)
2. **Provider Fields Database** (Section 2.2, lines 151-195)
3. **Mapping Fields Database** (Section 2.3, lines 198-267+)
4. **Change History Database** (Section 2.4, lines 278-300)

### Database Overview

The system requires **three core databases** (plus optional Change History):

```
┌─────────────────────┐
│  Fleeti Fields DB   │
│  (~343+ fields)     │
└──────────┬──────────┘
           │
           │ many-to-many
           │ (via Field Mappings)
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

## Your Task: Complete Database Design Review

### Primary Objective

Review the existing database schema design and provide a **complete, production-ready database specification** that ensures:

1. **Completeness**: All required fields are present
2. **Correctness**: Field types, constraints, and relationships are correct
3. **Usability**: Databases support all use cases (configuration generation, field mapping, versioning)
4. **Maintainability**: Structure is clear and easy to maintain
5. **Extensibility**: Can accommodate future requirements

### Analysis Framework

Evaluate the database design across these dimensions:

#### 1. **Database Structure**
- Are all required tables/databases present?
- Are fields properly organized and categorized?
- Are field types appropriate (Title, Text, Select, Relation, etc.)?
- Are required fields properly marked?

#### 2. **Relationships**
- Are relationships correctly defined (one-to-many, many-to-many)?
- Are foreign keys properly established?
- Are relationship directions correct?
- Do relationships support all use cases?

#### 3. **Data Completeness**
- Are all fields needed for configuration generation present?
- Are all mapping types supported (direct, prioritized, calculated, transformed, I/O, asset-integrated)?
- Are versioning and change tracking fields complete?
- Are validation and error handling fields present?

#### 4. **Configuration Generation Support**
- Can YAML configuration files be generated from these databases?
- Are all mapping rules captured in the database?
- Are priority orders, formulas, and transformations properly stored?
- Are dependencies tracked correctly?

#### 5. **Data Quality**
- Are validation rules defined?
- Are constraints appropriate?
- Are default values specified where needed?
- Are status fields properly defined?

---

## Expected Output

Provide a comprehensive database design specification with:

### 1. **Complete Database Tables Specification**

For each database, provide:

#### Table Format

**Database Name:** [Database Name]

| Column Name | Type | Required | Description | Example | Notes |
|-------------|------|----------|-------------|---------|-------|
| Column 1 | Type | ✅ Yes / ❌ No | Description | Example value | Additional notes |
| Column 2 | Type | ✅ Yes / ❌ No | Description | Example value | Additional notes |

**Example:**
```
Database Name: Fleeti Telemetry Fields

| Column Name | Type | Required | Description | Example | Notes |
|-------------|------|----------|-------------|---------|-------|
| Field Name | Title | ✅ Yes | Semantic field name (path) | `fuel.level` | Primary key |
| Field Path | Text | ✅ Yes | Full path in telemetry object | `fuel.level` | Must match Field Name |
| Category | Select | ✅ Yes | Section/category | `fuel` | Options: fuel, location, motion, etc. |
| Priority | Select | ✅ Yes | Implementation priority | `P0` | Options: P0, P1, P2, P3, T, BL |
| ... | ... | ... | ... | ... | ... |
```

#### Additional Information for Each Database

- **Purpose**: What is this database used for?
- **Primary Key**: What uniquely identifies each record?
- **Indexes**: What fields should be indexed for performance?
- **Views**: What views are needed (list with filters/sorts)?
- **Formulas**: What calculated fields are needed?
- **Validation Rules**: What validation rules apply?

### 2. **Relationship Diagram**

Provide a clear diagram showing:

- **All databases** and their relationships
- **Relationship types** (one-to-many, many-to-many)
- **Relationship directions** (which side has the foreign key)
- **Cardinality** (1:1, 1:N, N:M)

**Format:**
```
┌─────────────────────────┐
│  Database 1             │
│                         │
│  - Primary Key          │
│  - Field 1              │
│  - Field 2              │
└──────────┬──────────────┘
           │
           │ 1-to-many
           │ (via Foreign Key)
           │
           ▼
┌─────────────────────────┐
│  Database 2             │
│                         │
│  - Primary Key          │
│  - Foreign Key → DB1    │
│  - Field 1              │
└─────────────────────────┘
```

### 3. **Relationship Details**

For each relationship, specify:

- **From Database**: [Database Name]
- **To Database**: [Database Name]
- **Relationship Type**: One-to-Many / Many-to-Many / One-to-One
- **Via Field**: [Field name that establishes relationship]
- **Cardinality**: [1:1, 1:N, N:M]
- **Required**: Is the relationship required?
- **Cascade Rules**: What happens on delete/update?

**Example:**
```
Relationship: Fleeti Fields → Field Mappings

From Database: Fleeti Telemetry Fields
To Database: Field Mappings
Relationship Type: One-to-Many
Via Field: Fleeti Field (Relation field in Field Mappings)
Cardinality: 1:N (one Fleeti field can have many mappings)
Required: Yes (mapping must reference a Fleeti field)
Cascade Rules: If Fleeti field is deleted, mappings should be marked deprecated
```

### 4. **Missing Fields Analysis**

Identify any missing fields that are needed for:

- **Configuration Generation**: Fields needed to generate YAML configs
- **Field Mapping**: Fields needed to support all mapping types
- **Version Control**: Fields needed for versioning and change tracking
- **Data Quality**: Fields needed for validation and error handling
- **Operations**: Fields needed for monitoring and troubleshooting

For each missing field:
- **Field Name**: [Proposed field name]
- **Type**: [Field type]
- **Required**: Yes/No
- **Description**: [Why it's needed]
- **Example**: [Example value]

### 5. **Field Type Recommendations**

Review field types and recommend improvements:

- **Current Type**: [Current type from documentation]
- **Recommended Type**: [Better type if applicable]
- **Rationale**: [Why the change is needed]
- **Impact**: [What this affects]

**Example:**
```
Field: Priority Order
Current Type: Text
Recommended Type: JSON (or structured text)
Rationale: Priority order needs structured data for parsing
Impact: YAML generation can parse JSON directly
```

### 6. **Validation Rules**

Specify validation rules for critical fields:

- **Field**: [Field name]
- **Validation Rule**: [Rule description]
- **Error Message**: [What error to show if validation fails]
- **When Applied**: [When validation occurs]

**Example:**
```
Field: Field Path
Validation Rule: Must match Field Name format (dot-separated, lowercase)
Error Message: "Field Path must be in format 'category.field'"
When Applied: On create/update
```

### 7. **Indexes & Performance**

Recommend indexes for performance:

- **Index Name**: [Index name]
- **Fields**: [Fields included in index]
- **Type**: [Unique, Non-unique, Full-text]
- **Purpose**: [Why this index is needed]

**Example:**
```
Index Name: idx_fleeti_field_path
Fields: Field Path
Type: Unique
Purpose: Fast lookup by field path, ensure uniqueness
```

### 8. **Views & Queries**

Specify views needed for common queries:

- **View Name**: [View name]
- **Purpose**: [What this view is used for]
- **Filters**: [Filter criteria]
- **Sorts**: [Sort order]
- **Grouping**: [Group by fields]

**Example:**
```
View Name: Unmapped Fleeti Fields
Purpose: Find Fleeti fields that don't have mappings
Filters: Field Mappings is empty AND Status = active
Sorts: Priority (ascending), then Field Path (ascending)
Grouping: None
```

---

## Specific Questions to Answer

### For Each Database:

1. **Completeness**
   - Are all fields needed for configuration generation present?
   - Are all mapping types supported?
   - Are versioning fields complete?
   - Are there any missing fields?

2. **Correctness**
   - Are field types appropriate?
   - Are relationships correctly defined?
   - Are constraints properly specified?
   - Are default values appropriate?

3. **Usability**
   - Can developers easily add/modify fields?
   - Can configuration files be generated reliably?
   - Are queries efficient?
   - Are views helpful?

### For Relationships:

1. **Are all relationships defined?**
   - Fleeti Fields ↔ Field Mappings
   - Provider Fields ↔ Field Mappings
   - Field Mappings ↔ Change History
   - Fleeti Fields ↔ Dependencies (self-relation)

2. **Are relationship types correct?**
   - One-to-many vs many-to-many
   - Required vs optional
   - Cascade rules

3. **Are junction tables needed?**
   - For many-to-many relationships
   - For tracking additional relationship metadata

### For Configuration Generation:

1. **Can all mapping types be generated?**
   - Direct mappings
   - Prioritized mappings (with priority order)
   - Calculated mappings (function reference, formula, code-based)
   - Transformed mappings
   - I/O mappings
   - Asset-integrated mappings

2. **Are all required fields present?**
   - Priority JSON for prioritized mappings
   - Calculation Formula for calculated mappings
   - Backend Function Name for function references
   - Implementation Location for code-based
   - Dependencies for calculated/transformed fields

3. **Is versioning supported?**
   - Version tracking
   - Change history
   - YAML sync status

---

## Key Principles

1. **Completeness First**: Ensure all required fields are present
2. **Configuration Generation**: Design must support automated YAML generation
3. **Data Integrity**: Relationships and constraints must ensure data quality
4. **Maintainability**: Structure must be clear and easy to maintain
5. **Extensibility**: Design must accommodate future requirements
6. **Performance**: Indexes and views must support efficient queries

---

## Review Approach

1. **Read the existing schema documentation** (`docs/brainstorming/mapping/notion-documentation-methodology.md`)
2. **Review related documentation** (field mapping requirements, configuration generation needs)
3. **Analyze each database** for completeness and correctness
4. **Review relationships** for proper structure
5. **Identify gaps** and missing fields
6. **Provide recommendations** for improvements
7. **Create complete specification** in table format

---

## Success Criteria

Your database design review should result in:

- ✅ **Complete table specifications** for all databases (all fields with descriptions)
- ✅ **Clear relationship diagram** showing how databases connect
- ✅ **Detailed relationship specifications** (types, cardinality, cascade rules)
- ✅ **Missing fields identified** (if any)
- ✅ **Field type recommendations** (if improvements needed)
- ✅ **Validation rules** specified for critical fields
- ✅ **Indexes recommended** for performance
- ✅ **Views specified** for common queries
- ✅ **Configuration generation support** verified (all mapping types can be generated)

---

## Additional Context

### Related Documentation

- **Database Schema Design**: `docs/brainstorming/mapping/notion-documentation-methodology.md` (Sections 2.1-2.4)
- **Field Mapping Requirements**: `notion/2-documentation/4-requirements/field-mapping-requirements.md`
- **Configuration Generation**: `docs/brainstorming/configuration-file/README.md`
- **Mapping Rules**: `notion/2-documentation/2-field-mappings/mapping-rules.md`

### Configuration Generation Requirements

The databases must support generating YAML configuration files with:

- **Direct mappings**: `source: "provider_field"`
- **Prioritized mappings**: `sources: [{priority: 1, field: "field1"}, ...]`
- **Calculated mappings**: `calculation: "formula_or_function()"`, `depends_on: [...]`
- **Transformed mappings**: `transformation: "formula"`, `depends_on: [...]`
- **I/O mappings**: `io_mapping: {default_source: "...", installation_metadata: "..."}`
- **Asset-integrated mappings**: `asset_integration: {...}`

### Mapping Types to Support

1. **Direct**: 1:1 provider field → Fleeti field
2. **Prioritized**: Multiple provider fields → one Fleeti field (with priority order)
3. **Calculated**:
   - **Function Reference**: Backend function call (e.g., `derive_from_heading()`)
   - **Parseable Formula**: Simple math expression (e.g., `(a / b) * 100`)
   - **Code-Based**: Complex logic in separate code file
4. **Transformed**: Combines telemetry with static asset metadata
5. **I/O Mapped**: Maps raw I/O signals to semantic fields using installation metadata
6. **Asset-Integrated**: Combines asset metadata with telemetry

---

## Expected Deliverables

### 1. **Database Tables Specification**

Complete table format for each database showing:
- All columns with types
- Required vs optional
- Descriptions
- Examples
- Notes

### 2. **Relationship Diagram**

Visual diagram showing:
- All databases
- Relationships between them
- Relationship types and directions
- Cardinality

### 3. **Relationship Details**

Detailed specification for each relationship:
- From/To databases
- Relationship type
- Via field
- Cardinality
- Cascade rules

### 4. **Missing Fields Analysis**

List of any missing fields with:
- Field name
- Type
- Description
- Rationale

### 5. **Recommendations**

- Field type improvements
- Validation rules
- Indexes
- Views
- Best practices

---

**Please provide a comprehensive database design review that ensures completeness, correctness, and suitability for configuration file generation. Focus on ensuring nothing is missing and all relationships are properly defined.**

---

## References

- **Database Schema Documentation**: `docs/brainstorming/mapping/notion-documentation-methodology.md`
- **Field Mapping Requirements**: `notion/2-documentation/4-requirements/field-mapping-requirements.md`
- **Configuration Generation**: `docs/brainstorming/configuration-file/README.md`
- **Current Database Structure**: `notion/2-documentation/1-specifications/databases/README.md`

