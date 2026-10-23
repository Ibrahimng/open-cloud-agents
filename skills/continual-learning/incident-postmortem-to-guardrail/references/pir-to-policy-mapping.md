# Post-Incident Review (PIR) to Guardrail Crosswalk

## Translating Incidents to Policies

| SRE Incident Finding | Root Cause Mechanism | Target Guardrail Engine | Generated Policy Rule |
|---|---|---|---|
| **Incident A:** Unbudgeted NAT Gateway Bill (\$14,000) | S3 data lake requests routed through NAT rather than free S3 VPC Gateway Endpoint. | Checkov / TFLint (IaC) | Enforce `aws_vpc_endpoint` of type `Gateway` for `com.amazonaws.<region>.s3` in every VPC with private subnets. |
| **Incident B:** CoreDNS 502 Outage | Default `ndots: 5` caused 4 unnecessary recursive UDP lookups per outgoing request. | Kyverno / OPA Rego (K8s) | Validate that high-throughput deployments declare `dnsConfig.options.ndots: "2"`. |
| **Incident C:** Leaked CI/CD Secret | `pull_request_target` event executed code from fork PR with repository secret access. | actionlint (CI/CD) | Flag `pull_request_target` workflows that check out `github.event.pull_request.head.sha`. |

