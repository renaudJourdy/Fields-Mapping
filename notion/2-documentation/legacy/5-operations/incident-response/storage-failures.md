# Storage Failures Runbook

**Severity:** Critical  
**Estimated Resolution Time:** 30-120 minutes  
**Epic Association:** Epic 4 (Storage)

---

## Symptom

- Storage write failures
- High storage error rates
- Storage tier unavailable
- Alert: "Storage write failures"

---

## Impact

- **Severity:** Critical
- **Affected Systems:** Storage tiers (hot/warm/cold)
- **User Impact:** Data loss risk, query failures

---

## Immediate Mitigation Steps

1. **Identify Affected Tier:**
   - Check which storage tier is failing
   - Verify tier availability
   - Check error rates by tier

2. **Check Storage Health:**
   - Verify database connectivity
   - Check disk space
   - Review storage metrics

3. **Enable Failover (if available):**
   - Switch to backup storage
   - Activate read-only mode
   - Queue writes for retry

---

## Root Cause Analysis

### How to Diagnose

1. **Check Storage Metrics:**
   - `telemetry.storage.{tier}.write.errors`
   - `telemetry.storage.{tier}.write.duration`
   - Storage health metrics

2. **Review Storage Logs:**
   - Check database errors
   - Review connection errors
   - Check disk space warnings

3. **Verify Infrastructure:**
   - Check database availability
   - Verify network connectivity
   - Check resource limits

### Common Causes

- Database unavailable
- Disk full
- Connection pool exhausted
- Network connectivity issue
- Database corruption

---

## Resolution Steps

1. **If Database Unavailable:**
   - Restart database service
   - Check database health
   - Verify connectivity

2. **If Disk Full:**
   - Free up disk space
   - Archive old data
   - Scale storage

3. **If Connection Pool Exhausted:**
   - Increase connection pool size
   - Optimize connection usage
   - Scale database

---

## Post-Incident Actions

- [ ] Document root cause
- [ ] Review storage capacity planning
- [ ] Update monitoring/alerting
- [ ] Implement prevention measures

---

## Prevention Measures

- Monitor disk usage continuously
- Set up storage capacity alerts
- Implement automatic scaling
- Regular backup verification
- Test failover procedures

---

**Related Documentation:**
- [Storage Operations](../storage-operations.md)
- [Disaster Recovery](../disaster-recovery.md)
- [Monitoring & Observability](../monitoring-observability.md)

