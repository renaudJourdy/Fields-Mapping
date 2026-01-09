# Provider Outage Runbook

**Severity:** Critical  
**Estimated Resolution Time:** 15-60 minutes  
**Epic Association:** Epic 1 (Ingestion)

---

## Symptom

- No packets received from provider (Navixy, OEM, etc.)
- Provider-specific error rates spike
- Provider health check fails

---

## Impact

- **Severity:** Critical
- **Affected Systems:** Ingestion layer, transformation pipeline
- **User Impact:** No telemetry updates for affected assets

---

## Immediate Mitigation Steps

1. **Verify Provider Status:**
   - Check provider status page
   - Verify provider API health
   - Check network connectivity

2. **Enable Circuit Breaker:**
   - Activate circuit breaker for affected provider
   - Prevent retry storms
   - Log incident

3. **Notify Stakeholders:**
   - Alert operations team
   - Notify affected customers (if applicable)
   - Update status page

---

## Root Cause Analysis

### How to Diagnose

1. **Check Provider Metrics:**
   - `telemetry.ingestion.{provider}.packets.received`
   - `telemetry.ingestion.{provider}.errors`
   - Provider-specific dashboards

2. **Review Logs:**
   - Search for provider errors
   - Check authentication failures
   - Review network errors

3. **Verify Configuration:**
   - Check provider credentials
   - Verify API endpoints
   - Check rate limits

### Common Causes

- Provider service outage
- Network connectivity issues
- Authentication/authorization failures
- Rate limiting
- Configuration errors

---

## Resolution Steps

1. **If Provider Outage:**
   - Wait for provider to restore service
   - Monitor provider status
   - Resume processing when available

2. **If Network Issue:**
   - Check network connectivity
   - Verify firewall rules
   - Test connectivity

3. **If Authentication Issue:**
   - Verify API keys/credentials
   - Check token expiration
   - Rotate credentials if needed

4. **If Rate Limited:**
   - Reduce request rate
   - Implement backoff
   - Contact provider for limit increase

---

## Post-Incident Actions

- [ ] Document incident details
- [ ] Update runbook with lessons learned
- [ ] Review monitoring/alerting
- [ ] Implement prevention measures

---

## Prevention Measures

- Monitor provider health continuously
- Set up provider status page monitoring
- Implement circuit breakers
- Maintain provider contact information
- Test failover procedures regularly

---

**Related Documentation:**
- [Error Handling](../error-handling.md)
- [Monitoring & Observability](../monitoring-observability.md)

