#!/usr/bin/env bash
#
# CIS Remediation Helper Script
# Automates hardening of Linux host network parameters, SSH server, and Docker daemon.
#
# Usage:
#   bash cis_remediation_helper.sh --dry-run
#   bash cis_remediation_helper.sh --apply
#

set -euo pipefail

MODE="dry-run"

if [[ $# -gt 0 ]]; then
  case "$1" in
    --apply)
      MODE="apply"
      ;;
    --dry-run)
      MODE="dry-run"
      ;;
    *)
      echo "Usage: $0 [--dry-run|--apply]"
      exit 1
      ;;
  esac
fi

echo "============================================================"
echo " 🛡️  CIS Hardening & Remediation Helper (Mode: ${MODE})"
echo "============================================================"

# 1. Kernel sysctl network hardening
SYSCTL_FILE="/etc/sysctl.d/60-cis-hardening.conf"
echo "[1/3] Hardening Host Network Parameters (sysctl)..."
if [[ "${MODE}" == "dry-run" ]]; then
  echo "  [DRY-RUN] Would create ${SYSCTL_FILE} with:"
  echo "    net.ipv4.ip_forward = 0"
  echo "    net.ipv4.conf.all.send_redirects = 0"
  echo "    net.ipv4.conf.all.accept_redirects = 0"
  echo "    net.ipv4.conf.all.rp_filter = 1"
  echo "    net.ipv4.tcp_syncookies = 1"
  echo "    kernel.randomize_va_space = 2"
else
  if [[ $EUID -ne 0 ]]; then
    echo "  [WARN] Root/sudo privileges required to write to /etc/sysctl.d. Skipping write."
  else
    cat << 'EOF' > "${SYSCTL_FILE}"
net.ipv4.ip_forward = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1
net.ipv4.tcp_syncookies = 1
kernel.randomize_va_space = 2
EOF
    sysctl -p "${SYSCTL_FILE}" >/dev/null 2>&1 || true
    echo "  [APPLIED] Updated ${SYSCTL_FILE}."
  fi
fi

# 2. SSH Server Configuration
SSHD_CONFIG="/etc/ssh/sshd_config"
echo "[2/3] Hardening SSH Daemon Configuration..."
if [[ "${MODE}" == "dry-run" ]]; then
  echo "  [DRY-RUN] Would enforce in ${SSHD_CONFIG}:"
  echo "    PermitRootLogin no"
  echo "    PasswordAuthentication no"
  echo "    X11Forwarding no"
  echo "    MaxAuthTries 4"
else
  if [[ -f "${SSHD_CONFIG}" && $EUID -eq 0 ]]; then
    sed -i.bak -E 's/^#?PermitRootLogin.*/PermitRootLogin no/' "${SSHD_CONFIG}"
    sed -i.bak -E 's/^#?PasswordAuthentication.*/PasswordAuthentication no/' "${SSHD_CONFIG}"
    sed -i.bak -E 's/^#?X11Forwarding.*/X11Forwarding no/' "${SSHD_CONFIG}"
    sed -i.bak -E 's/^#?MaxAuthTries.*/MaxAuthTries 4/' "${SSHD_CONFIG}"
    echo "  [APPLIED] Hardened ${SSHD_CONFIG} (backup created as sshd_config.bak)."
  else
    echo "  [INFO] Skipped SSH write (no root or file not found)."
  fi
fi

# 3. Docker Daemon Configuration
DOCKER_DAEMON="/etc/docker/daemon.json"
echo "[3/3] Inspecting Docker Daemon Hardening (${DOCKER_DAEMON})..."
if [[ "${MODE}" == "dry-run" ]]; then
  echo "  [DRY-RUN] Recommended /etc/docker/daemon.json parameters:"
  echo '    {"icc": false, "no-new-privileges": true, "live-restore": true}'
else
  echo "  [INFO] Manual merge recommended for /etc/docker/daemon.json to avoid overwriting network or registry settings."
fi

echo "============================================================"
echo " Hardening inspection complete."
