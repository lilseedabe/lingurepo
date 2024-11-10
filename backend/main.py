import os
import requests
from dotenv import load_dotenv
from lingustruct.core import LinguStruct
from lingustruct.validator import Validator

# 環境変数のロード
load_dotenv()

# APIキーと情報の取得
TOOLHOUSE_API_KEY = os.getenv('TOOLHOUSE_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
LINGUSTRUCT_LICENSE_KEY = os.getenv('LINGUSTRUCT_LICENSE_KEY')
repo_name = os.getenv('REPO_NAME')
branch = os.getenv('BRANCH_NAME')

# APIリクエストのヘッダー設定
headers = {
    'Authorization': f'Bearer {TOOLHOUSE_API_KEY}',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

def list_target_files(repo, branch):
    """Toolhouse APIでリポジトリのファイル一覧を取得"""
    url = "https://api.toolhouse.ai/files"  # Toolhouse APIのエンドポイント

    payload = {
        "repo": repo,
        "branch": branch,
        "metadata": {
            "id": "unique_user_id_123",  # ユーザーID（ユニークである必要あり）
            "timezone": "0"
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # HTTPエラーが発生した場合に例外を発生

        data = response.json()
        # .pyファイルのみを対象にする
        return [f["path"] for f in data if f["path"].endswith(".py")]

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTPエラーが発生しました: {http_err}")
    except Exception as e:
        print(f"その他のエラーが発生しました: {e}")
    return []

def read_file_content(file_path):
    """指定されたファイルの内容を取得"""
    url = f"https://api.toolhouse.ai/files/content?path={file_path}"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        return response.text  # ファイル内容を返す

    except requests.exceptions.RequestException as e:
        print(f"ファイル内容取得中にエラーが発生しました: {e}")
        return ""

def generate_final_template(files):
    """LinguStructでテンプレートを生成"""
    components = {}
    for file in files:
        content = read_file_content(file)
        components[file] = content

    # 依存関係解析結果を作成（簡易版）
    completion = f"Analyzed components: {components}"

    # LinguStructを使用してテンプレートを生成
    replacements = {"COMPONENTS": completion}
    return lingu_struct.generate_master_json(replacements)

if __name__ == "__main__":
    lingu_struct = LinguStruct()
    validator = Validator()

    # 対象ファイルを取得
    files = list_target_files(repo_name, branch)

    if files:
        # テンプレートを生成し、バリデーションを実行
        final_template = generate_final_template(files)
        is_valid, message = validator.validate(final_template)

        print(f"Validation Result: {message}")
        print("Final Template:", final_template)
    else:
        print("対象ファイルが見つかりませんでした。")
