# Data Quality Issues Runbook

**Severity:** Medium  
**Estimated Resolution Time:** 30-90 minutes  
**Epic Association:** Epic 2 (Transformation), Epic 4 (Storage)

---

## Symptom

- Missing required fields
- Invalid field values
- Schema violations
- Alert: "Data quality issues detected"

---

## Impact

- **Severity:** Medium
- **Affected Systems:** Transformation pipeline, storage
- **User Impact:** Missing or incorrect data, calculation errors

---

## Immediate Mitigation Steps

1. **Assess Data Quality:**
   - Check data quality metrics
   - Identify affected fields
   - Determine scope of impact

2. **Review Recent Changes:**
   - Check configuration changes
   - Review field mapping updates
   - Check provider changes

3. **Isolate Affected Data:**
   - Identify affected assets/time ranges
   - Check if issue is provider-specific
   - Determine if historical recalculation needed

---

## Root Cause Analysis

### How to Diagnose

1. **Check Data Quality Metrics:**
   - `telemetry.quality.fields.missing`
   - `telemetry.quality.values.invalid`
   - `telemetry.quality.schema.violations`

2. **Review Error Logs:**
   - Check validation errors
   - Review field mapping failures
   - Check schema violations

3. **Verify Configuration:**
   - Check field mapping configuration
   - Verify validation rules
   - Review provider field availability

### Common Causes

- Provider field changes
- Configuration error
- Validation rule too strict
- Missing provider fields
- Data transformation error

---

## Resolution Steps

1. **If Provider Field Changes:**
   - Update field mappings
   - Adjust priority chains
   - Add fallback values

2. **If Configuration Error:**
   - Fix configuration
   - Update validation rules
   - Redeploy configuration

3. **If Historical Data Affected:**
   - Run historical recalculation
   - Fix data quality issues
   - Verify data quality

---

## Post-Incident Actions

- [ ] Document root cause
- [ ] Update field mappings if needed
- [ ] Review validation rules
- [ ] Implement prevention measures
- [ ] Run historical recalculation if needed

---

## Prevention Measures

- Monitor data quality continuously
- Set up data quality alerts
- Validate configuration before deployment
- Test provider field changes
- Regular data quality audits

---

**Related Documentation:**
- [Data Quality](../data-quality/README.md)
- [Field Mappings](../../field-mappings/README.md)
- [Monitoring & Observability](../monitoring-observability.md)

