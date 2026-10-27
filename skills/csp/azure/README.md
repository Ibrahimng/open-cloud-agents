# Azure Agent Skills — Open Cloud Agents Remix

Curated agent skills for Microsoft Azure cloud development and infrastructure management, remixed and integrated into the **Open Cloud Agents** ecosystem.

This catalog contains **193 specialized service skills** following the open agent skill standard, powering autonomous cloud engineering across compute, identity, networking, databases, and AI.

---

## Directory Structure

```text
skills/csp/azure/
├── skills/                     # 193 production-ready Azure service skills
│   ├── azure-app-service/      # Web apps, deployment slots, custom domains
│   ├── azure-kubernetes-service/ # AKS cluster operations, ingress, scaling
│   ├── azure-cosmos-db/        # Multi-region replication, consistency levels
│   ├── azure-functions/        # Serverless triggers, bindings, execution plans
│   ├── azure-virtual-network/  # VNets, NSGs, Azure Firewall, peering
│   ├── azure-active-directory/ # Microsoft Entra ID, service principals, RBAC
│   ├── azure-monitor/          # Log Analytics, Application Insights, alert rules
│   └── ...                     # Complete coverage across all Azure resource providers
└── README.md
```

---

## Key Capabilities by Well-Architected Pillar

* **Reliability:** Azure Availability Zones, Cosmos DB multi-master writes, and Traffic Manager/Front Door routing.
* **Security:** Microsoft Entra ID Managed Identities, Key Vault envelope encryption, and Defender for Cloud recommendations.
* **Cost Optimization (FinOps):** Azure Advisor cost recommendations, Blob Storage lifecycle management (Cool/Archive tiering), and reserved instance capacity planning.
* **Operational Excellence:** Azure CLI automation, Bicep declarative templates, and Azure Monitor workbook diagnostics.

---

## Upstream Attribution

Original foundation adapted from the [Azure Agent Skills](https://github.com/MicrosoftDocs/Agent-Skills) project, licensed under the [MIT License](./LICENSE) and [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).
