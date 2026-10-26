#!/usr/bin/env bash
# ==============================================================================
# Open Cloud Agents: FinOps Cloud Waste Reaper Script
# Safely scans cloud environments (AWS, GCP, Azure, or Mock) for unattached,
# abandoned, and idle resources, quantifying monthly financial waste before human sign-off.
#
# Usage:
#   ./reap_cloud_waste.sh --provider mock --export-json /tmp/waste.json --export-markdown /tmp/waste.md
#   ./reap_cloud_waste.sh --provider aws --dry-run
#   ./reap_cloud_waste.sh --provider gcp --dry-run
#   ./reap_cloud_waste.sh --provider azure --dry-run
# ==============================================================================

set -euo pipefail

PROVIDER="mock"
DRY_RUN=true
OUTPUT_JSON=""
OUTPUT_MARKDOWN=""

# ANSI Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_pass() {
    echo -e "${GREEN}✔${NC} $1"
}

log_fail() {
    echo -e "${RED}✖${NC} $1"
}

# Parse Arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --provider)
            PROVIDER="$2"
            shift 2
            ;;
        --mock)
            PROVIDER="mock"
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --execute)
            DRY_RUN=false
            shift
            ;;
        --export-json)
            OUTPUT_JSON="$2"
            shift 2
            ;;
        --export-markdown)
            OUTPUT_MARKDOWN="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [--provider aws|gcp|azure|mock] [--dry-run|--execute] [--export-json <path>] [--export-markdown <path>]"
            exit 0
            ;;
        *)
            echo "Unknown argument: $1"
            exit 1
            ;;
    esac
done

echo "========================================================================"
echo -e " ${BOLD}💰 Open Cloud Agents: FinOps Cloud Waste Reaper${NC}"
echo "========================================================================"
log_info "Provider Mode:  ${PROVIDER}"
log_info "Execution Mode: $([ "$DRY_RUN" = true ] && echo 'DRY-RUN (Non-destructive Audit)' || echo 'EXECUTE (Caution: Inviolable Rule 01 enforced)')"

DISKS_FOUND=0
IPS_FOUND=0
NATS_FOUND=0
LBS_FOUND=0

STORAGE_WASTE="0.00"
IP_WASTE="0.00"
NAT_WASTE="0.00"
LB_WASTE="0.00"
TOTAL_MONTHLY_WASTE="0.00"

# Mock Mode (Demonstration, local testing, and CI regression)
scan_mock() {
    log_info "Executing simulated FinOps waste scan across mock cloud environment..."

    echo ""
    echo -e "${BOLD}--- [1/4] Storage: Unattached Block Storage Disks ---${NC}"
    echo "  • [AWS gp3] vol-0a1b2c3d4e5f6g7h8 (150 GB) - Unattached for 24 days (\$12.00/mo)"
    echo "  • [AWS gp3] vol-0987654321fedcba0 (500 GB) - Unattached for 41 days (\$40.00/mo)"
    DISKS_FOUND=2
    STORAGE_WASTE="52.00"

    echo ""
    echo -e "${BOLD}--- [2/4] Networking: Unassociated Static / Elastic IPs ---${NC}"
    echo "  • [AWS EIP] 54.210.12.89 (AllocationId: eipalloc-01234567) - Unassociated (\$3.65/mo)"
    echo "  • [AWS EIP] 52.87.110.45 (AllocationId: eipalloc-89abcdef) - Unassociated (\$3.65/mo)"
    IPS_FOUND=2
    IP_WASTE="7.30"

    echo ""
    echo -e "${BOLD}--- [3/4] Gateways: Idle Cloud NAT Gateways ---${NC}"
    echo "  • [AWS NAT] nat-0f1e2d3c4b5a6978 (vpc-0123456789abcdef0) - 0 Active Conn. in 14d (\$32.40/mo)"
    NATS_FOUND=1
    NAT_WASTE="32.40"

    echo ""
    echo -e "${BOLD}--- [4/4] Load Balancers: Idle / Empty Load Balancers ---${NC}"
    echo "  • [AWS ALB] app/dead-endpoint-alb/50dc6c495c0c9188 - 0 Healthy Targets for 18d (\$16.20/mo)"
    LBS_FOUND=1
    LB_WASTE="16.20"

    TOTAL_MONTHLY_WASTE=$(python3 -c "print(f'{$STORAGE_WASTE + $IP_WASTE + $NAT_WASTE + $LB_WASTE:.2f}')")
}

# AWS Real Scan
scan_aws() {
    if ! command -v aws &> /dev/null; then
        log_fail "AWS CLI ('aws') is not installed or not in PATH."
        exit 1
    fi
    log_info "Querying AWS CLI for unattached resources..."

    echo ""
    echo -e "${BOLD}--- [1/4] Storage: Unattached EBS Volumes ---${NC}"
    local raw_vols
    raw_vols=$(aws ec2 describe-volumes --filters Name=status,Values=available --query "Volumes[*].{ID:VolumeId,Size:Size,Type:VolumeType}" --output json 2>/dev/null || echo "[]")
    DISKS_FOUND=$(echo "$raw_vols" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data))")
    STORAGE_WASTE=$(echo "$raw_vols" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'{sum(v.get(\"Size\", 0) * 0.08 for v in data):.2f}')")
    echo "$raw_vols" | python3 -c '
import sys, json
for v in json.load(sys.stdin):
    cost = v.get("Size", 0) * 0.08
    print(f"  • [AWS EBS] {v.get(\"ID\")} ({v.get(\"Size\")} GB {v.get(\"Type\")}) - Unattached (${cost:.2f}/mo)")
'

    echo ""
    echo -e "${BOLD}--- [2/4] Networking: Unassociated Elastic IPs ---${NC}"
    local raw_ips
    raw_ips=$(aws ec2 describe-addresses --filters Name=association-id,Values=null --query "Addresses[*].{IP:PublicIp,ID:AllocationId}" --output json 2>/dev/null || echo "[]")
    IPS_FOUND=$(echo "$raw_ips" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data))")
    IP_WASTE=$(echo "$raw_ips" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'{len(data) * 3.65:.2f}')")
    echo "$raw_ips" | python3 -c '
import sys, json
for a in json.load(sys.stdin):
    print(f"  • [AWS EIP] {a.get(\"IP\")} ({a.get(\"ID\")}) - Unassociated ($3.65/mo)")
'

    echo ""
    echo -e "${BOLD}--- [3/4] Gateways: Active NAT Gateways (Check Traffic) ---${NC}"
    local raw_nats
    raw_nats=$(aws ec2 describe-nat-gateways --filter Name=state,Values=available --query "NatGateways[*].{ID:NatGatewayId,VPC:VpcId}" --output json 2>/dev/null || echo "[]")
    NATS_FOUND=$(echo "$raw_nats" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data))")
    NAT_WASTE=$(echo "$raw_nats" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'{len(data) * 32.40:.2f}')")
    echo "$raw_nats" | python3 -c '
import sys, json
for n in json.load(sys.stdin):
    print(f"  • [AWS NAT] {n.get(\"ID\")} ({n.get(\"VPC\")}) - Audit connection metrics ($32.40/mo base)")
'

    echo ""
    echo -e "${BOLD}--- [4/4] Load Balancers: Application Load Balancers ---${NC}"
    local raw_lbs
    raw_lbs=$(aws elbv2 describe-load-balancers --query "LoadBalancers[*].{ARN:LoadBalancerArn,DNS:DNSName}" --output json 2>/dev/null || echo "[]")
    LBS_FOUND=$(echo "$raw_lbs" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data))")
    LB_WASTE=$(echo "$raw_lbs" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'{len(data) * 16.20:.2f}')")
    echo "$raw_lbs" | python3 -c '
import sys, json
for lb in json.load(sys.stdin):
    name = lb.get("ARN", "").split("/")[-2] if "/" in lb.get("ARN", "") else "ALB"
    print(f"  • [AWS ALB] {name} ({lb.get(\"DNS\")}) - Audit target health ($16.20/mo base)")
'

    TOTAL_MONTHLY_WASTE=$(python3 -c "print(f'{$STORAGE_WASTE + $IP_WASTE + $NAT_WASTE + $LB_WASTE:.2f}')")
}

# GCP Real Scan
scan_gcp() {
    if ! command -v gcloud &> /dev/null; then
        log_fail "Google Cloud SDK ('gcloud') is not installed or not in PATH."
        exit 1
    fi
    log_info "Querying Google Cloud SDK for unattached resources..."

    echo ""
    echo -e "${BOLD}--- [1/3] Storage: Unattached Persistent Disks ---${NC}"
    local raw_disks
    raw_disks=$(gcloud compute disks list --filter="-users:*" --format="json(name,zone,sizeGb,type,status)" 2>/dev/null || echo "[]")
    DISKS_FOUND=$(echo "$raw_disks" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data))")
    STORAGE_WASTE=$(echo "$raw_disks" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'{sum(float(d.get(\"sizeGb\", 0)) * 0.08 for d in data):.2f}')")
    echo "$raw_disks" | python3 -c '
import sys, json
for d in json.load(sys.stdin):
    cost = float(d.get("sizeGb", 0)) * 0.08
    print(f"  • [GCP PD] {d.get(\"name\")} ({d.get(\"sizeGb\")} GB in {d.get(\"zone\")}) - Unattached (${cost:.2f}/mo)")
'

    echo ""
    echo -e "${BOLD}--- [2/3] Networking: Unassociated Static External IPs ---${NC}"
    local raw_ips
    raw_ips=$(gcloud compute addresses list --filter="status=RESERVED AND -users:*" --format="json(name,region,address,status)" 2>/dev/null || echo "[]")
    IPS_FOUND=$(echo "$raw_ips" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data))")
    IP_WASTE=$(echo "$raw_ips" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'{len(data) * 3.65:.2f}')")
    echo "$raw_ips" | python3 -c '
import sys, json
for a in json.load(sys.stdin):
    print(f"  • [GCP IP] {a.get(\"address\")} ({a.get(\"name\")} in {a.get(\"region\")}) - Unassociated ($3.65/mo)")
'

    TOTAL_MONTHLY_WASTE=$(python3 -c "print(f'{$STORAGE_WASTE + $IP_WASTE:.2f}')")
}

# Azure Real Scan
scan_azure() {
    if ! command -v az &> /dev/null; then
        log_fail "Azure CLI ('az') is not installed or not in PATH."
        exit 1
    fi
    log_info "Querying Azure CLI for unattached resources..."

    echo ""
    echo -e "${BOLD}--- [1/2] Storage: Unattached Managed Disks ---${NC}"
    local raw_disks
    raw_disks=$(az disk list --query "[?managedBy==null].{name:name,rg:resourceGroup,sizeGb:diskSizeGb,tier:sku.name}" -o json 2>/dev/null || echo "[]")
    DISKS_FOUND=$(echo "$raw_disks" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data))")
    STORAGE_WASTE=$(echo "$raw_disks" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'{sum(float(d.get(\"sizeGb\", 0)) * 0.08 for d in data):.2f}')")
    echo "$raw_disks" | python3 -c '
import sys, json
for d in json.load(sys.stdin):
    cost = float(d.get("sizeGb", 0)) * 0.08
    print(f"  • [Azure Disk] {d.get(\"name\")} ({d.get(\"sizeGb\")} GB in {d.get(\"rg\")}) - Unattached (${cost:.2f}/mo)")
'

    echo ""
    echo -e "${BOLD}--- [2/2] Networking: Unassociated Public IPs ---${NC}"
    local raw_ips
    raw_ips=$(az network public-ip list --query "[?ipConfiguration==null].{name:name,rg:resourceGroup,ip:ipAddress}" -o json 2>/dev/null || echo "[]")
    IPS_FOUND=$(echo "$raw_ips" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data))")
    IP_WASTE=$(echo "$raw_ips" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'{len(data) * 3.65:.2f}')")
    echo "$raw_ips" | python3 -c '
import sys, json
for a in json.load(sys.stdin):
    print(f"  • [Azure IP] {a.get(\"ip\")} ({a.get(\"name\")}) - Unassociated ($3.65/mo)")
'

    TOTAL_MONTHLY_WASTE=$(python3 -c "print(f'{$STORAGE_WASTE + $IP_WASTE:.2f}')")
}

case "$PROVIDER" in
    mock)
        scan_mock
        ;;
    aws)
        scan_aws
        ;;
    gcp)
        scan_gcp
        ;;
    azure)
        scan_azure
        ;;
    *)
        log_fail "Unsupported provider: $PROVIDER"
        exit 1
        ;;
esac

echo ""
echo "========================================================================"
echo -e " ${BOLD}Reaper Audit Summary${NC}"
echo "========================================================================"
echo "  • Unattached Disks:       $DISKS_FOUND"
echo "  • Unassociated IPs:       $IPS_FOUND"
echo "  • Idle NAT Gateways:      $NATS_FOUND"
echo "  • Idle Load Balancers:    $LBS_FOUND"
echo -e "  • ${BOLD}Estimated Monthly Waste:  \$${TOTAL_MONTHLY_WASTE} USD${NC}"
ANNUAL_WASTE=$(python3 -c "print(f'{$TOTAL_MONTHLY_WASTE * 12:.2f}')")
echo -e "  • ${BOLD}Annualized Savings:       \$${ANNUAL_WASTE} USD/year${NC}"
echo "========================================================================"

if [ "$DRY_RUN" = true ]; then
    log_pass "Dry-run complete. Zero modifications executed."
    log_info "To reclaim assets safely, create a task plan for the DevSecOps Engineer."
else
    log_warn "Executing in real mode. Inviolable Rule 01 prohibits autonomous deletion."
    log_fail "Interactive confirmation required before issuing delete calls."
fi

# Export JSON if requested
if [ -n "$OUTPUT_JSON" ]; then
    cat <<EOF > "$OUTPUT_JSON"
{
  "provider": "$PROVIDER",
  "dry_run": $DRY_RUN,
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "summary": {
    "unattached_disks": $DISKS_FOUND,
    "unassociated_ips": $IPS_FOUND,
    "idle_nat_gateways": $NATS_FOUND,
    "idle_load_balancers": $LBS_FOUND,
    "estimated_monthly_waste_usd": $TOTAL_MONTHLY_WASTE,
    "estimated_annual_waste_usd": $ANNUAL_WASTE
  }
}
EOF
    log_pass "Exported structured waste report to: $OUTPUT_JSON"
fi

# Export Markdown Report if requested
if [ -n "$OUTPUT_MARKDOWN" ]; then
    cat <<EOF > "$OUTPUT_MARKDOWN"
# 💰 FinOps Cloud Waste Reaper: Audit Report

> **Generated:** $(date -u +"%Y-%m-%d %H:%M:%SZ") | **Provider:** \`$PROVIDER\` | **Execution Mode:** \`$([ "$DRY_RUN" = true ] && echo "DRY-RUN (Non-destructive)" || echo "EXECUTE")\`

## Executive Summary

Autonomous waste discovery scanned cloud resources and identified the following idle, unattached, or abandoned assets:

| Waste Category | Detected Count | Est. Monthly Cost (USD) | Est. Annualized Cost (USD) |
|---|---|---|---|
| **Unattached Storage Disks** | $DISKS_FOUND | \$$STORAGE_WASTE | \$$(python3 -c "print(f'{$STORAGE_WASTE * 12:.2f}')") |
| **Unassociated Static/Elastic IPs** | $IPS_FOUND | \$$IP_WASTE | \$$(python3 -c "print(f'{$IP_WASTE * 12:.2f}')") |
| **Idle NAT Gateways** | $NATS_FOUND | \$$NAT_WASTE | \$$(python3 -c "print(f'{$NAT_WASTE * 12:.2f}')") |
| **Idle Load Balancers** | $LBS_FOUND | \$$LB_WASTE | \$$(python3 -c "print(f'{$LB_WASTE * 12:.2f}')") |
| **TOTAL WASTE FOOTPRINT** | **$((DISKS_FOUND + IPS_FOUND + NATS_FOUND + LBS_FOUND))** | **\$$TOTAL_MONTHLY_WASTE** | **\$$ANNUAL_WASTE** |

---

## 🛡️ Guardrails & Reclamation Sign-Off

Per [**Rule 01: Zero Unplanned Destruction**](../../../rules/01-destructive-actions.md), autonomous deletion is strictly prohibited without human operator verification:

- [ ] **Exemption Check:** Confirm none of the targeted assets are tagged with \`Environment=Production\` or \`DoNotDelete=true\`.
- [ ] **Snapshot Safety:** Final point-in-time snapshots must be taken prior to deleting any persistent block storage volumes.
- [ ] **Route Table Audit:** Verify no active private subnets depend on the identified NAT Gateways for outbound internet connectivity.
- [ ] **Engineer Handoff:** Submit structured task plan to [**DevSecOps Engineer**](../../../agents/7-agent-master-suite/devsecops-engineer.md) for surgical removal.
EOF
    log_pass "Exported markdown report to: $OUTPUT_MARKDOWN"
fi
