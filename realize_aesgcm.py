#加密实现
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import bcrypt
# 256-bit key
MASTER_KEY = os.environ.get("MASTER_KEY") or AESGCM.generate_key(bit_length=256)

def encrypt_secret(plaintext: str) -> dict:
    aesgcm = AESGCM(MASTER_KEY)
    nonce = os.urandom(12) 
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)#真正加密的一步,密文加认证标签
    return {
        "nonce": nonce,
        "ciphertext": ciphertext
    }

def decrypt_secret(nonce: bytes, ciphertext: bytes) -> str:
    aesgcm = AESGCM(MASTER_KEY)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode()
#AES-256-GCM 加密
#秘密存储前已加密
#解密只发生在使用时（内存中）

#密码哈希
def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def verify_password(password: str, password_hash: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash)