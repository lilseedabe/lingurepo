import requests
import json
import os
from typing import List, Dict, Any
from utils.logger import setup_logger

logger = setup_logger(__name__)

class DocumentGenerator:
    def __init__(self, lingu_key: str):
        self.lingu_key = lingu_key

    def fetch_template(self, module_id: int) -> Dict[str, Any]:
        """Fetch the structure of individual template files like m1.json, m2.json from API."""
        url = f"https://lingustruct.onrender.com/lingu_struct/modules/{module_id}"
        headers = {
            "LINGUSTRUCT_LICENSE_KEY": self.lingu_key
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            template_data = response.json()["data"]
            logger.info(f"Template for module {module_id} loaded successfully from API.")
            return template_data
        except requests.HTTPError as http_err:
            logger.error(f"HTTP error occurred when fetching module {module_id}: {http_err}")
            raise
        except Exception as e:
            logger.error(f"Failed to load template for module {module_id}: {e}")
            raise

    def generate_final_document(self, mapped_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        try:
            if not mapped_data:
                raise ValueError("No mapped data available to generate document")

            # 各モジュールの詳細情報を統合する
            modules_with_fields = []
            for module in mapped_data:
                module_id = module["id"]
                # APIからテンプレートデータを取得し`fields`として格納
                template_data = self.fetch_template(module_id)
                module["fields"] = template_data.get("fields", {})
                modules_with_fields.append(module)

            # `master.json` データ生成のためのリクエストデータ構造
            final_document = {
                "project_id": "moduvo_project",
                "version": "1.0",
                "modules": modules_with_fields  # 統合されたフィールド情報付きモジュール
            }

            # master.jsonファイルとして保存
            file_path = os.path.join(os.getcwd(), "master.json")
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(final_document, file, ensure_ascii=False, indent=4)

            logger.info(f"Document saved successfully as {file_path}")
            return final_document

        except Exception as e:
            logger.error(f"Failed to generate final document: {e}", exc_info=True)
            raise
