# SOC 2 Type II Evidence Requirements Matrix

## Trust Services Criteria & Audit Artifacts

| Control ID | Trust Criteria | Required Audit Evidence Artifact | Retention Period |
|---|---|---|---|
| **CC6.1** | Logical Access Security | Identity Provider (IdP) SSO & MFA enforcement policy report; active user rosters. | 12 Months |
| **CC6.3** | Access Modifications & Revocation | Quarterly access review sign-off sheets; ticketing tickets for employee offboarding deprovisioning within 24h. | 12 Months |
| **CC6.6** | Perimeter Defense & Firewalls | Security group & firewall rule exports showing 0.0.0.0/0 restrictions on internal ports. | 12 Months |
| **CC6.7** | Data Transmission Encryption | ALB, CloudFront, and Ingress TLS configuration exports enforcing minimum TLS 1.2 with HSTS. | 12 Months |
| **CC7.1** | Infrastructure Monitoring | Alert rule definitions in Prometheus / CloudWatch and on-call escalation policies (PagerDuty/Opsgenie). | 12 Months |
| **CC8.1** | Change Management | Git commit history, pull request approvals, peer reviews, and automated CI test results prior to prod merge. | 12 Months |
