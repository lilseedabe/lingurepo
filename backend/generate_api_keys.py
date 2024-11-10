import os
from lingustruct.license_manager import LicenseManager
from dotenv import load_dotenv

def main():
    # .envファイルを読み込む
    load_dotenv()

    # 環境変数からLICENCES_JSONとLINGUSTRUCT_LICENSE_KEYを読み込む
    license_data = os.getenv("LICENCES_JSON")
    secret_key = os.getenv('LINGUSTRUCT_LICENSE_KEY')

    if not license_data:
        print("LICENCES_JSON environment variable is not set.")
        return

    if not secret_key:
        print("LINGUSTRUCT_LICENSE_KEY environment variable is not set.")
        return

    # LicenseManagerのインスタンスを作成（test_mode=False）
    license_manager = LicenseManager(license_data=license_data, test_mode=False)

    # 各ライセンスキーに対応するユーザー情報を取得
    for original_api_key, user_info in license_manager.licenses.items():
        signed_api_key = license_manager.generate_api_key(user_info)
        print(f"Original API Key: {original_api_key}")
        print(f"Signed API Key: {signed_api_key}\n")

if __name__ == "__main__":
    main()
