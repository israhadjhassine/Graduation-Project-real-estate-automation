import base64
import hashlib
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

# Derive a 32-byte key from JWT_SECRET_KEY or a custom key
jwt_secret = os.getenv("JWT_SECRET_KEY", "doublechawarma")
key = hashlib.sha256(jwt_secret.encode("utf-8")).digest()

# Derive a fixed 16-byte IV from the key to make the encryption deterministic
iv = hashlib.md5(key).digest()

def encrypt_telegram_id(raw_chat_id: str) -> str:
    """
    Encrypts a raw telegram chat ID using AES-256-CBC with a deterministic IV.
    The resulting ciphertext is base64url-encoded.
    """
    if not raw_chat_id:
        return ""
    
    clean_id = str(raw_chat_id).strip().encode("utf-8")
    
    # Pad to block size (128 bits / 16 bytes)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(clean_id) + padder.finalize()
    
    # Encrypt
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    
    return base64.urlsafe_b64encode(ciphertext).decode("utf-8")

def decrypt_telegram_id(encrypted_chat_id: str) -> str:
    """
    Decrypts a base64url-encoded ciphertext back to a raw telegram chat ID.
    If decryption fails, returns the input string itself (safe fallback for unencrypted values).
    """
    if not encrypted_chat_id:
        return ""
    
    try:
        ciphertext = base64.urlsafe_b64decode(encrypted_chat_id.encode("utf-8"))
        
        # Decrypt
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Unpad
        unpadder = padding.PKCS7(128).unpadder()
        decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()
        
        return decrypted.decode("utf-8")
    except Exception:
        # Fallback for unencrypted values or formatting mismatch
        return encrypted_chat_id
