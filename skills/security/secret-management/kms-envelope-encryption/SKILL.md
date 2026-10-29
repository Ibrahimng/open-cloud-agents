---
name: kms-envelope-encryption
description: Implement envelope encryption workflows using KMS (Key Management Service) customer-managed keys (CMK) and data encryption keys (DEK) for high-performance payload encryption.
---

# KMS Envelope Encryption Architecture

## What is Envelope Encryption?
Encrypting large payloads directly with KMS has high network latency, KMS API throttling risks, and per-call costs.

**Envelope Encryption** solves this by:

1. Calling KMS once to generate a symmetric **Data Encryption Key (DEK)** (plaintext + ciphertext).
2. Using the plaintext DEK locally to encrypt the large payload with AES-256-GCM.
3. Wiping the plaintext DEK from memory and storing the ciphertext DEK alongside the encrypted payload.

## Encryption Flow
```text
[Plaintext Data] + [Plaintext DEK] ──(AES-256-GCM)──> [Encrypted Data]
                                                            │
[KMS CMK] ──(GenerateDataKey)──> [Ciphertext DEK] ──────────┼──> Stored Record
```

## Reference Python Implementation (AWS KMS + Cryptography)
```python
import os
import boto3
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

kms = boto3.client('kms', region_name='us-east-1')

def encrypt_payload(data: bytes, kms_key_id: str) -> dict:
    # 1. Generate DEK from KMS
    response = kms.generate_data_key(KeyId=kms_key_id, KeySpec='AES_256')
    plaintext_dek = response['Plaintext']
    ciphertext_dek = response['CiphertextBlob']
    
    # 2. Encrypt locally using AES-GCM
    aesgcm = AESGCM(plaintext_dek)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, data, None)
    
    # 3. Wipe plaintext DEK from memory
    del plaintext_dek
    
    return {
        'ciphertext': ciphertext,
        'ciphertext_dek': ciphertext_dek,
        'nonce': nonce
    }
```

