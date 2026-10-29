# Wazuh Custom Decoders & Rules Syntax

This guide explains how to construct custom XML decoders and detection rules within `/var/ossec/etc/rules/local_rules.xml` and `/var/ossec/etc/decoders/local_decoder.xml`.

---

## 1. Event Decoding Flow

```
  Raw Log Line ➔ Parent Decoder ➔ Sibling/Child Decoder ➔ Decoded Fields ➔ Rules Engine
```

### Custom Decoder Example

```xml
<!-- In /var/ossec/etc/decoders/local_decoder.xml -->
<decoder name="custom-app">
  <prematch>^[AppSecurityEvent]</prematch>
</decoder>

<decoder name="custom-app-fields">
  <parent>custom-app</parent>
  <regex>user: (\S+) src_ip: (\S+) action: (\S+)</regex>
  <order>user, srcip, action</order>
</decoder>
```

---

## 2. Rule Hierarchy & Severity Levels

Alert severity spans Level 0 to Level 16:

| Level Range | Category | Action |
|---|---|---|
| **0 - 2** | Ignored / Informational | No alert generated; log disregarded. |
| **3 - 6** | Low Severity / Notice | Routine user login, normal status codes. |
| **7 - 9** | Medium Severity / Warning | Multiple bad logins, configuration changes. |
| **10 - 12** | High Severity / Error | Brute force attack, FIM modification to `/etc/shadow`. Active Response triggered. |
| **13 - 16** | Critical / Emergency | Known rootkit detected, container breakout, active ransomware encryption. Host isolated immediately. |

---

## 3. Production Custom Rule Specifications

```xml
<!-- In /var/ossec/etc/rules/local_rules.xml -->
<group name="enterprise_threats,">

  <!-- Rule 100100: Base Application Event -->
  <rule id="100100" level="3">
    <decoded_as>custom-app</decoded_as>
    <description>Custom application security log received</description>
  </rule>

  <!-- Rule 100101: Unauthorized API Token Generation -->
  <rule id="100101" level="10">
    <if_sid>100100</if_sid>
    <match>action: token_generate_unauthorized</match>
    <description>Unauthorized API token minted for user $(user)</description>
    <mitre>
      <id>T1078</id>
      <id>T1098</id>
    </mitre>
  </rule>

  <!-- Rule 100102: Frequency Rule - Brute Force Authentication Threshold -->
  <rule id="100102" level="12" frequency="6" timeframe="120">
    <if_matched_sid>100100</if_matched_sid>
    <match>action: login_failed</match>
    <same_source_ip />
    <description>Multiple login failures detected from IP $(srcip) (Brute Force)</description>
    <mitre>
      <id>T1110</id>
    </mitre>
  </rule>

</group>
```

---

## 4. Testing Rules with `wazuh-logtest`

Verify parsing and rule matching in real time:

```bash
/var/ossec/bin/wazuh-logtest
# Input:
# [AppSecurityEvent] user: admin src_ip: 198.51.100.42 action: token_generate_unauthorized

# Expected Output:
# **Phase 1: Completed decoding.
#        decoder: 'custom-app'
#        user: 'admin'
#        srcip: '198.51.100.42'
#        action: 'token_generate_unauthorized'
# **Phase 2: Completed rule inspection.
#        Rule id: '100101'
#        Level: '10'
#        Description: 'Unauthorized API token minted for user admin'
```
