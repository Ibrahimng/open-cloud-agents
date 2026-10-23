# AWS Agent Skills — Open Cloud Agents Remix

Curated agent skills, MCP plugins, and operational rules for Amazon Web Services (AWS), remixed and integrated into the **Open Cloud Agents** ecosystem.

These skills equip autonomous agents (Principal Cloud Architect, DevSecOps Engineer, SRE, and FinOps Optimizer) with deep operational capabilities across AWS services.

---

## Directory Structure

```text
skills/csp/aws/
├── skills/
│   ├── core-skills/            # Bedrock, Billing/FinOps, CDK, CloudFormation, Containers, IAM, Serverless
│   └── specialized-skills/     # Analytics, Databases (Aurora/DynamoDB), Networking (VPC/Route53), Storage
├── plugins/                    # MCP server plugins
│   ├── aws-core/               # Core AWS service selection, deployment, and management
│   ├── aws-agents/             # Amazon Bedrock and AgentCore integration
│   ├── aws-agents-for-devsecops/ # Automated incident investigation and vulnerability scanning
│   └── aws-data-analytics/     # S3 Tables, AWS Glue, and Athena analytics
├── rules/                      # AWS-specific agent operational guidelines
│   └── aws-agent-rules.md
└── tools/                      # Validation utilities
    └── validate.py
```

---

## Key Capabilities by Well-Architected Pillar

* **Operational Excellence:** AWS CDK, CloudFormation, and Serverless deployment workflows.
* **Security & Identity:** IAM least-privilege policy generation, IAM Identity Center, and KMS encryption.
* **Reliability:** Multi-AZ Aurora cluster patterns, DynamoDB Global Tables, and Route53 DNS failover.
* **Performance Efficiency:** ECS/EKS container optimization, Lambda memory tuning, and CloudFront caching.
* **Cost Optimization (FinOps):** AWS Cost Explorer queries, S3 Lifecycle tiering (Glacier/Intelligent-Tiering), and NAT Gateway cost elimination.

---

## Upstream Attribution

Original foundation adapted from the [AWS Agent Toolkit](https://github.com/aws/agent-toolkit-for-aws), published by Amazon Web Services under the [Apache License 2.0](./LICENSE).
