 <# Documentation Structure Comparison

**Purpose:** Visual comparison of current (reference-oriented) vs. proposed (developer-oriented) structure

---

## Current Structure (Reference-Oriented)

```
documentation/
├── README.md                          # Section overview (reference-focused)
│
├── specifications/                    # 📚 Reference: Technical specs
│   ├── README.md
│   ├── telemetry-system-specification.md
│   ├── status-rules.md
│   └── schema-specification.md
│
├── field-mappings/                    # 📚 Reference: Field catalogs
│   ├── README.md
│   ├── fleeti-fields-catalog.md
│   ├── provider-fields-catalog.md
│   └── mapping-rules.md
│
├── reference-materials/               # 📚 Reference: Additional refs
│   ├── README.md
│   ├── provider-catalogs.md
│   ├── enum-definitions.md
│   └── legacy-documentation.md
│
└── requirements/                      # 📚 Reference: Requirements
    ├── README.md
    ├── field-mapping-requirements.md
    └── storage-product-requirements.md
```

**Characteristics:**
- ❌ Organized by document type (specs, mappings, reference, requirements)
- ❌ Reference-first (what is, not how to)
- ❌ Nested folders for end-user content
- ❌ Hard to discover workflows
- ❌ Missing implementation guidance

---

## Proposed Structure (Developer-Oriented)

```
documentation/
├── README.md                          # 🎯 Navigation hub (workflow-focused)
│
├── fleeti-fields.md                   # 🛠️ How to work with Fleeti fields
├── provider-fields.md                 # 🛠️ How to work with provider fields
├── configuration-files.md             # 🛠️ How to create/manage YAML configs
├── mapping-rules.md                   # 🛠️ How to implement mapping rules
├── status-computation.md              # 🛠️ How to implement status computation
├── storage-strategy.md                # 🛠️ How to understand/work with storage
│
└── reference/                         # 📚 Reference materials (secondary)
    ├── README.md
    ├── specifications.md              # Links to complete specs
    ├── provider-catalogs.md           # Complete provider catalogs
    ├── enum-definitions.md           # Enum definitions
    └── legacy-documentation.md        # Legacy docs (deprecated)
```

**Characteristics:**
- ✅ Organized by developer workflow (what developers need to do)
- ✅ Action-first (how to, not just what is)
- ✅ Direct markdown files (following overview-vision pattern)
- ✅ Easy to discover workflows
- ✅ Implementation guidance and examples

---

## Content Flow Comparison

### Current Flow (Reference-Oriented)

```
Developer Need: "How do I add a new field?"
  ↓
Search through folders
  ↓
Find "field-mappings/fleeti-fields-catalog.md"
  ↓
Read catalog (what fields exist)
  ↓
Still need to find "how to add" guidance
  ↓
Check specifications/schema-specification.md
  ↓
Still missing step-by-step workflow
```

**Problem:** Information scattered, no clear workflow

---

### Proposed Flow (Developer-Oriented)

```
Developer Need: "How do I add a new field?"
  ↓
Go to documentation/fleeti-fields.md
  ↓
Find "Adding New Fields" section
  ↓
Follow step-by-step workflow
  ↓
See practical examples
  ↓
Link to reference/specifications.md if need complete spec
```

**Solution:** Clear workflow, actionable guidance, reference when needed

---

## Page-by-Page Mapping

### Current → Proposed

| Current Location | Proposed Location | Transformation |
|-----------------|-------------------|----------------|
| `specifications/schema-specification.md` | `fleeti-fields.md` | Extract "how to" → Main page<br>Complete spec → `reference/specifications.md` |
| `field-mappings/fleeti-fields-catalog.md` | `fleeti-fields.md` | Extract "how to add" → Main page<br>Complete catalog → `reference/` |
| `field-mappings/provider-fields-catalog.md` | `provider-fields.md` | Extract "how to" → Main page<br>Complete catalog → `reference/provider-catalogs.md` |
| `field-mappings/mapping-rules.md` | `mapping-rules.md` | Transform to "how to" format<br>Keep in place, enhance with workflows |
| `specifications/status-rules.md` | `status-computation.md` | Extract "how to" → Main page<br>Complete rules → `reference/specifications.md` |
| `specifications/telemetry-system-specification.md` | Multiple pages | Config system → `configuration-files.md`<br>Storage → `storage-strategy.md`<br>Complete spec → `reference/specifications.md` |
| `specifications/*` | `reference/specifications.md` | Consolidate all specs with links |
| `reference-materials/*` | `reference/*` | Move to reference subfolder |

---

## Developer Journey Comparison

### Current Journey: Adding a New Field

1. **Discover:** Search through folders, find `field-mappings/`
2. **Read Catalog:** Read `fleeti-fields-catalog.md` (what fields exist)
3. **Find Spec:** Read `specifications/schema-specification.md` (field structure)
4. **Find Requirements:** Read `requirements/field-mapping-requirements.md` (requirements)
5. **Still Missing:** No clear "how to add" workflow
6. **Result:** Confusion, trial and error

**Time:** 15-30 minutes, still incomplete understanding

---

### Proposed Journey: Adding a New Field

1. **Discover:** Go to `documentation/fleeti-fields.md`
2. **Follow Workflow:** "Adding New Fields" section with step-by-step
3. **See Examples:** Real examples of field definitions
4. **Reference When Needed:** Link to `reference/specifications.md` for complete spec
5. **Result:** Clear understanding, actionable steps

**Time:** 5-10 minutes, complete understanding

---

## Key Improvements

### 1. Discovery
- **Before:** Must know document type to find content
- **After:** Find by workflow (what you need to do)

### 2. Actionability
- **Before:** "What is" (reference)
- **After:** "How to" (guidance)

### 3. Organization
- **Before:** By document type (specs, mappings, reference)
- **After:** By developer workflow (fields, configs, mappings, status, storage)

### 4. Content Focus
- **Before:** Complete specifications (exhaustive)
- **After:** Focused guidance with reference links

### 5. Pattern Consistency
- **Before:** Inconsistent structure
- **After:** Follows `overview-vision/` pattern (direct markdown files)

---

## Migration Impact

### Low Risk
- ✅ Reference materials still accessible
- ✅ Complete specs still available
- ✅ Can migrate incrementally
- ✅ Old structure can coexist during transition

### High Value
- ✅ Faster developer onboarding
- ✅ Clearer implementation guidance
- ✅ Reduced support questions
- ✅ Better documentation quality

---

## Success Metrics

### Before Migration
- Developers spend 15-30 min finding information
- Information scattered across multiple files
- Missing "how to" workflows
- Reference-first organization

### After Migration
- Developers find information in 5-10 min
- Information organized by workflow
- Clear "how to" workflows
- Action-first organization

---

**Status:** Ready for review and implementation



