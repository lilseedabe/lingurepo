import os
import requests
from dotenv import load_dotenv

# .env ファイルから環境変数をロード
load_dotenv()

class AISupport:
    def __init__(self, api_key=None):
        # APIキーを引数か環境変数から取得
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("Groq API key must be provided or set in the GROQ_API_KEY environment variable.")

        # エンドポイントの設定（仮のURL、実際のものに置き換える必要あり）
        self.endpoint = "https://api.groq.com/v1/completions"

    def complete_design(self, section, content):
        # プロンプトの準備
        prompt = f"Complete the following section for system design:\nSection: {section}\nContent: {content}\n"

        # リクエスト用のヘッダーとペイロードの設定
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.2-90b-text-preview",  # 使用するAIモデル
            "prompt": prompt,
            "max_tokens": 150,
            "temperature": 0.7
        }

        try:
            # Groq API にPOSTリクエストを送信
            response = requests.post(self.endpoint, json=payload, headers=headers)
            response.raise_for_status()  # ステータスコードが200以外の場合例外を発生

            # レスポンスをパースして結果を取得
            data = response.json()
            completion = data.get("choices", [{}])[0].get("text", "").strip()
            return completion
        except requests.exceptions.HTTPError as http_err:
            return f"HTTPエラーが発生しました: {http_err}"
        except Exception as err:
            return f"AI補完中にエラーが発生しました: {err}"
