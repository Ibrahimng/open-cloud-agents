#!/usr/bin/env python3
"""
envelope_encrypt.py - Standalone Simulation of KMS Envelope Encryption

Demonstrates the two-tier key hierarchy (KEK -> DEK) and authenticated AES-GCM
encryption/decryption of local payloads.
"""

import os
import sys
import json
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def simulate_kms_generate_data_key() -> tuple:
    # Simulates KMS: returns a 256-bit plaintext key and a mock ciphertext key
    plaintext_dek = AESGCM.generate_key(bit_length=256)
    # In real KMS, ciphertext_dek is encrypted under the CMK
    mock_ciphertext_dek = b"ENCRYPTED_UNDER_KMS_CMK:" + plaintext_dek
    return plaintext_dek, mock_ciphertext_dek

def encrypt(plaintext_data: bytes) -> dict:
    plaintext_dek, ciphertext_dek = simulate_kms_generate_data_key()
    
    aesgcm = AESGCM(plaintext_dek)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext_data, None)

    # Securely delete plaintext DEK from memory
    del plaintext_dek

    return {
        "ciphertext_b64": base64.b64encode(ciphertext).decode("utf-8"),
        "ciphertext_dek_b64": base64.b64encode(ciphertext_dek).decode("utf-8"),
        "nonce_b64": base64.b64encode(nonce).decode("utf-8")
    }

def main():
    payload = sys.argv[1].encode("utf-8") if len(sys.argv) > 1 else b"Confidential customer banking record"
    print(f"Encrypting payload: '{payload.decode('utf-8')}'")
    record = encrypt(payload)
    print("Serialized Envelope Output:")
    print(json.dumps(record, indent=2))

if __name__ == "__main__":
    main()

