# lingustruct/validator.py

import json
from jsonschema import validate, ValidationError
from pathlib import Path

class Validator:
    def __init__(self, schema_path='templates_server/s/schema.json'):
        self.schema_path = schema_path
        self.schema = self.load_schema()

    def load_schema(self):
        schema_file = Path(self.schema_path)
        if not schema_file.exists():
            raise FileNotFoundError(f"{self.schema_path} が見つかりません。")
        with open(schema_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def validate(self, data):
        try:
            validate(instance=data, schema=self.schema)
            return True, "データはスキーマに準拠しています。"
        except ValidationError as e:
            return False, f"バリデーションエラー: {e.message}"
