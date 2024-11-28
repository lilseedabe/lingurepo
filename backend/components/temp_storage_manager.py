import os
import json
from typing import Any

class TempStorageManager:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.base_dir = os.path.join("temp_storage", self.user_id)
        os.makedirs(self.base_dir, exist_ok=True)  # ディレクトリを自動作成

    def save(self, key: str, data: Any):
        """指定されたキーでデータをJSONファイルとして保存"""
        file_path = os.path.join(self.base_dir, f"{key}.json")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)  # 必要なディレクトリを作成
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def load(self, key: str) -> Any:
        """指定されたキーに対応するJSONファイルを読み込む"""
        file_path = os.path.join(self.base_dir, f"{key}.json")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found for key: {key}")
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def delete(self, key: str):
        """指定されたキーに対応するファイルを削除"""
        file_path = os.path.join(self.base_dir, f"{key}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
