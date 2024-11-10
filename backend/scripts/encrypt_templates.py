import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# .envファイルのロード
load_dotenv()

def encrypt_template(file_path, encryption_key):
    """テンプレートファイルを暗号化します。"""
    fernet = Fernet(encryption_key)
    with open(file_path, 'rb') as f:
        data = f.read()
    encrypted = fernet.encrypt(data)
    with open(file_path, 'wb') as f:
        f.write(encrypted)

if __name__ == "__main__":
    encryption_key = os.getenv('LINGUSTRUCT_ENCRYPTION_KEY')
    if not encryption_key:
        raise ValueError("LINGUSTRUCT_ENCRYPTION_KEY is not set.")

    templates_dir = 'lingustruct/templates'
    for filename in os.listdir(templates_dir):
        if filename.endswith('.json'):
            encrypt_template(os.path.join(templates_dir, filename), encryption_key)
    print("Templates encrypted.")
