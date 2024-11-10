from cryptography.fernet import Fernet
import os

def encrypt_template(file_path: str, encryption_key: str):
    """テンプレートファイルを暗号化します。"""
    fernet = Fernet(encryption_key)
    with open(file_path, 'rb') as f:
        data = f.read()
    encrypted = fernet.encrypt(data)
    with open(file_path, 'wb') as f:
        f.write(encrypted)

def decrypt_template(file_path: str, encryption_key: str):
    """テンプレートファイルを復号化します。"""
    fernet = Fernet(encryption_key)
    with open(file_path, 'rb') as f:
        encrypted = f.read()
    decrypted = fernet.decrypt(encrypted)
    with open(file_path, 'wb') as f:
        f.write(decrypted)