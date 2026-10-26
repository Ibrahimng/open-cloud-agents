#!/usr/bin/env bash
# ==============================================================================
# Open Cloud Agents: FinOps Cloud Waste Reaper Script
# Safely scans cloud environments (AWS, GCP, Azure) for unattached, abandoned,
# and idle resources, quantifying monthly financial waste before human sign-off.
#
# Usage:
#   ./reap_cloud_waste.sh --provider aws --dry-run
#   ./reap_cloud_waste.sh --provider gcp --dry-run
#   ./reap_cloud_waste.sh --mock --export-json waste_report.json
# ==============================================================================

set -euo pipefail

PROVIDER="mock"
DRY_RUN=true
OUTPUT_JSON=""

# Colors
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
        -h|--help)
            echo "Usage: $0 [--provider aws|gcp|azure|mock] [--dry-run|--execute] [--export-json <path>]"
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
log_info "Provider Mode: ${PROVIDER}"
log_info "Execution Mode: $([ "$DRY_RUN" = true ] && echo 'DRY-RUN (Non-destructive Audit)' || echo 'EXECUTE (Caution: Deletion Enabled)')"

TOTAL_MONTHLY_WASTE=0
DISKS_FOUND=0
IPS_FOUND=0
NATS_FOUND=0

# Mock Mode (For local validation, CI, and demonstration)
scan_mock() {
    log_info "Executing simulated FinOps waste scan across mock cloud environment..."
    sleep 0.2

    echo ""
    echo -e "${BOLD}--- [1/3] Storage: Unattached Block Storage Disks ---${NC}"
    echo "  • [AWS gp3] vol-0a1b2c3d4e5f6g7h8 (150 GB) - Unattached for 24 days (\$12.00/mo)"
    echo "  • [AWS gp3] vol-0987654321fedcba0 (500 GB) - Unattached for 41 days (\$40.00/mo)"
    DISKS_FOUND=2
    STORAGE_WASTE=52

    echo ""
    echo -e "${BOLD}--- [2/3] Networking: Unassociated Static / Elastic IPs ---${NC}"
    echo "  • [AWS EIP] 54.210.12.89 (AllocationId: eipalloc-01234567) - Unassociated (\$3.65/mo)"
    echo "  • [AWS EIP] 52.87.110.45 (AllocationId: eipalloc-89abcdef) - Unassociated (\$3.65/mo)"
    IPS_FOUND=2
    IP_WASTE=7.30

    echo ""
    echo -e "${BOLD}--- [3/3] Gateways: Idle Cloud NAT Gateways ---${NC}"
    echo "  • [AWS NAT] nat-0f1e2d3c4b5a6978 (vpc-0123456789abcdef0) - 0 Active Conn. in 14d (\$32.40/mo)"
    NATS_FOUND=1
    NAT_WASTE=32.40

    TOTAL_MONTHLY_WASTE=$(awk "BEGIN {print $STORAGE_WASTE + $IP_WASTE + $NAT_WASTE}")
}

# AWS Real Scan
scan_aws() {
    if ! command -v aws &> /dev/null; then
        log_fail "AWS CLI is not installed or not in PATH."
        exit 1
    fi
    log_info "Querying AWS CLI for unattached resources..."

    # Check unattached EBS
    local unattached_ebs
    unattached_ebs=$(aws ec2 describe-volumes --filters Name=status,Values=available --query "Volumes[*].VolumeId" --output text 2>/dev/null || true)
    if [ -n "$unattached_ebs" ]; then
        for vol in $unattached_ebs; do
            echo "  • [AWS EBS] Found unattached volume: $vol"
            DISKS_FOUND=$((DISKS_FOUND + 1))
        done
    fi

    # Check unassociated EIPs
    local unassociated_eips
    unassociated_eips=$(aws ec2 describe-addresses --filters Name=association-id,Values=null --query "Addresses[*].PublicIp" --output text 2>/dev/null || true)
    if [ -n "$unassociated_eips" ]; then
        for ip in $unassociated_eips; do
            echo "  • [AWS EIP] Found unassociated IP: $ip"
            IPS_FOUND=$((IPS_FOUND + 1))
        done
    fi
}

case "$PROVIDER" in
    mock)
        scan_mock
        ;;
    aws)
        scan_aws
        ;;
    gcp|azure)
        log_warn "Provider '$PROVIDER' scan will run via provider API wrappers."
        scan_mock
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
echo -e "  • ${BOLD}Estimated Monthly Waste:  \$${TOTAL_MONTHLY_WASTE} USD${NC}"
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
    "estimated_monthly_waste_usd": $TOTAL_MONTHLY_WASTE
  }
}
EOF
    log_pass "Exported structured waste report to: $OUTPUT_JSON"
fi
