# CIS Foundations Benchmark Control Mappings

## Multi-Cloud Control Crosswalk

| Security Domain | AWS CIS v3.0 | Azure CIS v2.1 | GCP CIS v3.0 | Mandatory Enforcement Rule |
|---|---|---|---|---|
| **Identity & Access** | Section 1.5-1.14 | Section 1.1-1.8 | Section 1.1-1.6 | MFA on all consoles, no static root access keys, 90-day key rotation. |
| **Logging & Audit** | Section 3.1-3.11 | Section 5.1-5.4 | Section 2.1-2.12 | Multi-region trail enabled, bucket logging active, log encryption via CMK. |
| **Networking** | Section 5.1-5.4 | Section 6.1-6.6 | Section 3.1-3.8 | Disallow 0.0.0.0/0 on ports 22 (SSH) and 3389 (RDP). |
| **Storage Security** | Section 2.1.1-2.1.5 | Section 3.1-3.8 | Section 5.1-5.2 | Block Public Access enabled at account & bucket level; TLS 1.2+ mandatory. |
| **Database Encryption** | Section 2.3.1 | Section 4.1-4.4 | Section 6.1-6.3 | Mandatory storage encryption at rest with customer-managed keys (CMEK). |

