# Ingestion Stopped Runbook

**Severity:** Critical  
**Estimated Resolution Time:** 10-30 minutes  
**Epic Association:** Epic 1 (Ingestion)

---

## Symptom

- No telemetry packets received from any provider
- `telemetry.ingestion.packets.received` metric is zero
- Alert: "Data ingestion stopped"

---

## Impact

- **Severity:** Critical
- **Affected Systems:** Entire telemetry pipeline
- **User Impact:** No telemetry updates, stale data

---

## Immediate Mitigation Steps

1. **Verify Ingestion Service Status:**
   - Check service health endpoints
   - Verify service is running
   - Check service logs

2. **Check Provider Connectivity:**
   - Verify provider endpoints are reachable
   - Test provider API connectivity
   - Check network connectivity

3. **Review Recent Changes:**
   - Check recent deployments
   - Review configuration changes
   - Check for service restarts

---

## Root Cause Analysis

### How to Diagnose

1. **Check Ingestion Metrics:**
   - `telemetry.ingestion.packets.received`
   - `telemetry.ingestion.packets.failed`
   - `telemetry.ingestion.parse.errors`

2. **Review Service Logs:**
   - Check for errors
   - Review startup logs
   - Check for crashes

3. **Verify Infrastructure:**
   - Check service availability
   - Verify resource limits (CPU, memory)
   - Check queue status

### Common Causes

- Service crash or restart
- Configuration error
- Network connectivity issue
- Resource exhaustion
- Provider outage (all providers)

---

## Resolution Steps

1. **If Service Down:**
   - Restart ingestion service
   - Verify service health
   - Monitor packet reception

2. **If Configuration Error:**
   - Review recent configuration changes
   - Rollback if needed
   - Fix configuration and redeploy

3. **If Resource Exhaustion:**
   - Scale up service
   - Increase resource limits
   - Optimize resource usage

---

## Post-Incident Actions

- [ ] Document root cause
- [ ] Review monitoring/alerting
- [ ] Update runbook
- [ ] Implement prevention measures

---

## Prevention Measures

- Set up service health monitoring
- Implement automatic restarts
- Monitor resource usage
- Test configuration changes in staging
- Set up alerting for zero packet rate

---

**Related Documentation:**
- [Provider Outage](./provider-outage.md)
- [Error Handling](../error-handling.md)
- [Monitoring & Observability](../monitoring-observability.md)

