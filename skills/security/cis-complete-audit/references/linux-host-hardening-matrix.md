# CIS Linux Host Hardening Matrix (Ubuntu 22.04/24.04 & RHEL 8/9)

This reference outlines system configurations, PAM settings, `auditd` rules, and kernel sysctl parameters required for CIS Linux Benchmark compliance (Level 1 and Level 2).

---

## 1. Filesystem Partitioning & Mount Options

| Partition / Mount | Recommended Options | Rationale |
|---|---|---|
| `/tmp` | `nodev,nosuid,noexec` | Prevents executing binaries or exploiting SUID programs out of temporary directories. |
| `/var/tmp` | `nodev,nosuid,noexec` | Hardens secondary world-writable temporary storage. |
| `/dev/shm` | `nodev,nosuid,noexec` | Secures shared memory segment against malicious binary execution. |
| `/home` | `nodev,nosuid` | Prevents regular users from creating local device nodes or SUID exploits. |

### Verification Command

```bash
mount | grep -E '\s/(tmp|var/tmp|dev/shm|home)\s'
```

---

## 2. PAM, Password & Account Security

### 2.1 `/etc/login.defs` Requirements

```ini
PASS_MAX_DAYS   90
PASS_MIN_DAYS   7
PASS_WARN_AGE   14
ENCRYPT_METHOD  SHA512
```

### 2.2 Account Lockout (`pam_faillock` / `pam_tally2`)

Configure `/etc/pam.d/common-auth` or `/etc/pam.d/system-auth`:

```
auth required pam_faillock.so preauth silent audit deny=5 unlock_time=900
auth [default=die] pam_faillock.so authfail audit deny=5 unlock_time=900
auth sufficient pam_faillock.so authsucc
```

### 2.3 SSH Server Hardening (`/etc/ssh/sshd_config`)

```ini
Protocol 2
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
MaxAuthTries 4
ClientAliveInterval 300
ClientAliveCountMax 0
X11Forwarding no
AllowTcpForwarding no
LoginGraceTime 60
LogLevel VERBOSE
```

---

## 3. Kernel Network Parameters (`/etc/sysctl.d/60-cis-hardening.conf`)

Apply these parameters to harden the host TCP/IP stack against spoofing and redirection attacks:

```ini
# IP Forwarding disabled (non-router)
net.ipv4.ip_forward = 0
net.ipv6.conf.all.forwarding = 0

# Disable Source Routing
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.default.accept_source_route = 0

# Disable ICMP Redirects
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0

# Enable Reverse Path Filtering (anti-spoofing)
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1

# Ignore ICMP Broadcast Echoes (Smurf attack defense)
net.ipv4.icmp_echo_ignore_broadcasts = 1

# Log Bogus ICMP Responses
net.ipv4.icmp_ignore_bogus_error_responses = 1

# TCP SYN Cookies (SYN flood mitigation)
net.ipv4.tcp_syncookies = 1

# Address Space Layout Randomization (ASLR)
kernel.randomize_va_space = 2
```

Apply via:
```bash
sudo sysctl -p /etc/sysctl.d/60-cis-hardening.conf
```

---

## 4. System Audit Daemon (`auditd`) Rules

Place in `/etc/audit/rules.d/audit.rules` and reload with `augenrules --load`:

```ini
# Record modifications to system time
-a always,exit -F arch=b64 -S adjtimex -S settimeofday -k time-change
-a always,exit -F arch=b64 -S clock_settime -k time-change
-w /etc/localtime -p wa -k time-change

# Record modifications to identity databases
-w /etc/group -p wa -k identity
-w /etc/passwd -p wa -k identity
-w /etc/gshadow -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/security/opasswd -p wa -k identity

# Record network configuration modifications
-a always,exit -F arch=b64 -S sethostname -S setdomainname -k system-locale
-w /etc/issue -p wa -k system-locale
-w /etc/hosts -p wa -k system-locale
-w /etc/network/ -p wa -k system-locale

# Record unprivileged attempts to access system calls (permission denied)
-a always,exit -F arch=b64 -S open -S openat -S truncate -S ftruncate -F exit=-EACCES -F auid>=1000 -F auid!=unset -k access
-a always,exit -F arch=b64 -S open -S openat -S truncate -S ftruncate -F exit=-EPERM -F auid>=1000 -F auid!=unset -k access

# Make audit configuration immutable (must reboot to alter)
-e 2
```
