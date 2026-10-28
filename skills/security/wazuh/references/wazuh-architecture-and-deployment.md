# Wazuh Enterprise Architecture & Scalable Deployment

This reference outlines high-availability deployment patterns, agent communication protocols, and cluster scaling for Wazuh XDR.

---

## 1. Multi-Tier Cluster Architecture

An enterprise Wazuh deployment separates data collection, processing, and indexing across three distinct tiers:

```
 [ Endpoint Agents ] ──(Port 1514 TLS)──> [ Wazuh Server Master & Workers ]
                                                     │
                                       (Port 9200 / 9300 TLS)
                                                     ▼
                                          [ Wazuh Indexer Cluster ]
                                            (OpenSearch Shards)
                                                     │
                                                     ▼
                                          [ Wazuh Dashboard UI ]
                                                (Port 443)
```

### Components
1. **Wazuh Agent:** Installed on endpoints (Linux, Windows, macOS, container hosts). Collects system logs, file checksums, process executions, and open ports.
2. **Wazuh Server (Manager Cluster):**
   - **Master Node:** Handles agent registration (authd on port 1515), centralized configuration synchronization, and cluster orchestration.
   - **Worker Nodes:** Ingest and decode events via multi-threaded analysis daemon (`ossec-analysisd`), evaluate rules, and route alerts.
3. **Wazuh Indexer:** Multi-node OpenSearch distributed document store indexing security events, alerts, and compliance assessments.
4. **Wazuh Dashboard:** Web interface for threat exploration, MITRE ATT&CK mapping, and compliance tracking.

---

## 2. Agent Registration at Scale

Automate agent enrollment via enrollment script or cloud-init with pre-shared tokens or SSL verification:

```bash
# Register agent via CLI
/var/ossec/bin/agent-auth -m wazuh-manager.internal -p 1515 -A "k8s-worker-node-01"

# Environment-based registration on Docker / Cloud-Init
export WAZUH_MANAGER="wazuh-manager.internal"
export WAZUH_AGENT_NAME="$(hostname)"
export WAZUH_AGENT_GROUP="production-linux"
```

---

## 3. Network Ports & Firewall Rules

| Port | Protocol | Source | Destination | Purpose |
|---|---|---|---|---|
| **1514** | TCP / UDP | Agents | Manager Workers | Encrypted agent event streaming |
| **1515** | TCP | Agents | Manager Master | Agent registration (`authd`) |
| **55000** | TCP | Admins / CI | Manager Master | Wazuh REST API |
| **9200** | TCP | Managers / UI | Indexers | OpenSearch REST API |
| **9300** | TCP | Indexers | Indexers | OpenSearch node-to-node cluster communication |
| **443** | TCP | Browser | Dashboard | HTTPS Web Console |
