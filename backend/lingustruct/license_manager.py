import json
import os

def validate_api_key(api_key, test_mode=False):
    license_path = "licenses.json"

    # テストモードならモックデータを返す
    if test_mode:
        return {"user": "test_user", "plan": "free"}

    if not os.path.exists(license_path):
        raise FileNotFoundError("licenses.json file is missing.")

    with open(license_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if not content.strip():
            raise ValueError("licenses.json file is empty.")

        licenses = json.loads(content)

    if api_key not in licenses:
        raise ValueError("Invalid API key.")

    return licenses[api_key]