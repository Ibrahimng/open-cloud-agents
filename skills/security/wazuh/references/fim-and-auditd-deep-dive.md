# File Integrity Monitoring (FIM / `syscheck`) & Auditd Integration

This guide provides an in-depth reference for configuring Wazuh **syscheck** to detect unauthorized file creations, modifications, permissions alterations, and deletions.

---

## 1. FIM Modes: Periodic vs Real-Time vs Who-Data

| Feature | Periodic (`check_all="yes"`) | Real-Time (`realtime="yes"`) | Who-Data (`whodata="yes"`) |
|---|---|---|---|
| **Underlying Mechanism** | Periodic directory walk (e.g. every 12h) | Linux `inotify` kernel subsystem | Linux `auditd` kernel audit subsystem |
| **Alert Latency** | High (waits for next scan cycle) | Instantaneous ($< 1$ second) | Instantaneous ($< 1$ second) |
| **User & Process Context** | None (only detects hash/size change) | None (only file path and hash) | **Full attribution: User ID, Process Name, Audit ID, Parent Process** |
| **Resource Overhead** | Low CPU bursts during scan | Low constant memory | Medium CPU/I/O (uses kernel audit rules) |
| **Recommendation** | Large static directories | Configuration directories without auditd | **Production critical directories (`/etc`, `/bin`, `/root/.ssh`)** |

---

## 2. Who-Data Configuration (`ossec.conf`)

Ensure the Linux `auditd` package is installed on the host, then configure `ossec.conf`:

```xml
<syscheck>
  <disabled>no</disabled>
  <frequency>43200</frequency>
  <scan_on_start>yes</scan_on_start>

  <!-- Enable Who-Data monitoring on critical system binaries and configurations -->
  <directories check_all="yes" whodata="yes">/etc</directories>
  <directories check_all="yes" whodata="yes">/bin,/sbin,/usr/bin,/usr/sbin</directories>
  <directories check_all="yes" whodata="yes">/root/.ssh</directories>
  <directories check_all="yes" whodata="yes">/boot</directories>

  <!-- Windows Registry Monitoring (when deployed on Windows hosts) -->
  <windows_registry arch="both">HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Run</windows_registry>
  <windows_registry arch="both">HKEY_LOCAL_MACHINE\System\CurrentControlSet\Services</windows_registry>

  <!-- Exclude noisy, volatile paths -->
  <ignore>/etc/mtab</ignore>
  <ignore>/etc/hosts.deny</ignore>
  <ignore>/etc/mail/statistics</ignore>
  <ignore>/etc/random-seed</ignore>
  <ignore>/etc/adjtime</ignore>
  <ignore type="sregex">^/var/log</ignore>
  <ignore type="sregex">^/tmp</ignore>
</syscheck>
```

---

## 3. Who-Data Alert Telemetry Structure

When `/etc/shadow` is modified, Wazuh emits a rich JSON alert containing:

```json
{
  "timestamp": "2026-10-28T10:14:22Z",
  "rule": {
    "level": 12,
    "id": "550",
    "description": "Integrity checksum changed for: '/etc/shadow'"
  },
  "syscheck": {
    "path": "/etc/shadow",
    "event": "modified",
    "size_before": 1240,
    "size_after": 1312,
    "md5_before": "a1b2c3d4...",
    "md5_after": "e5f6g7h8...",
    "sha256_after": "9f8e7d6c5b4a...",
    "audit": {
      "user": {
        "id": "0",
        "name": "root"
      },
      "process": {
        "id": "4210",
        "name": "/usr/sbin/useradd",
        "ppid": "4105"
      }
    }
  }
}
```
