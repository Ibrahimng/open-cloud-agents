# KMS Envelope Encryption Specification

## The Cryptographic Architecture

Envelope encryption uses a two-tier key hierarchy:

1. **Key Encryption Key (KEK) / Customer Master Key (CMK):**
    - Managed inside the Hardware Security Module (HSM) of AWS KMS, Azure Key Vault, or GCP Cloud KMS.
    - Never leaves the HSM unencrypted.
2. **Data Encryption Key (DEK):**
    - A 256-bit symmetric key (`AES-256`) generated on-demand by KMS.
    - KMS returns both the **Plaintext DEK** (used immediately in client RAM) and the **Ciphertext DEK** (encrypted under the CMK).

## AES-GCM Payload Structure

When serializing encrypted payloads to storage:

```text
┌─────────────────┬──────────────┬──────────────────┬──────────────┐
│ Ciphertext DEK  │ Nonce / IV   │ Ciphertext Data  │ Auth Tag     │
│ (e.g. 512 bytes)│ (12 bytes)   │ (Variable size)  │ (16 bytes)   │
└─────────────────┴──────────────┴──────────────────┴──────────────┘
```

- **AES-GCM (Galois/Counter Mode)** provides both confidentiality and authenticated integrity. If the ciphertext or nonce is modified in transit, decryption will fail immediately.

