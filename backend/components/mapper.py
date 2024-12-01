import json
from typing import Dict, Any, List, Optional
from utils.logger import setup_logger
import os
import requests

logger = setup_logger(__name__)

class Mapper:
    def __init__(self, api_url: str, license_key: str):
        """
        コンストラクタはLinguStruct APIからkey_mapping.jsonを取得します。

        :param api_url: LinguStruct APIのkey_mappingエンドポイントURL
        :param license_key: APIアクセスに必要なライセンスキー
        """
        # LinguStruct APIからkey_mapping.jsonを取得
        try:
            headers = {
                'accept': 'application/json',
                'LINGUSTRUCT_LICENSE_KEY': license_key
            }
            logger.info(f"Fetching key mapping from API: {api_url}")
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()  # HTTPエラーがあれば例外を発生させる
            self.key_mapping = response.json()
            logger.info("Key mapping loaded successfully from API.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch key mapping from API: {e}")
            self.key_mapping = {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format received from API: {e}")
            self.key_mapping = {}

        # モジュールマッピング
        self.section_to_module = {
            "Meta Information": 1,
            "Technology Stack": 10,
            "Dependency Analysis": 17,
            "Error Handling": 18,
            # 他のモジュールも必要に応じて追加
        }

        # ファイルタイプマッピング
        self.filetype_to_module = {
            "json": "Generic File Information",
            "python": "Python Module",
            "typescript": "TypeScript Module",
            "rust": "Rust Module",
            "go": "Go Module",
            "javascript": "JavaScript Module",
            "markdown": "Meta Information",  # README.mdなどに対応
            # その他のファイルタイプも必要に応じて追加
        }

    def map_data_to_modules(self, parsed_data: Dict[str, Any], dependencies: Dict[str, Dict[str, List[str]]], project_meta: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        データをテンプレートのモジュールに割り当てます。

        :param parsed_data: 各ファイルからパースされたデータ
        :param dependencies: 各ファイルの依存関係
        :param project_meta: プロジェクトのメタ情報
        :return: モジュールのリスト
        """
        modules = []
        
        # モジュール1: Meta Information
        meta_module = self._create_meta_information_module(project_meta)
        modules.append(meta_module)
        logger.debug("Added Meta Information module.")
        
        # モジュール10: Technology Stack
        tech_stack_module = self._create_technology_stack_module(parsed_data)
        modules.append(tech_stack_module)
        logger.debug("Added Technology Stack module.")
        
        # モジュール17: Dependency Analysis
        dependency_module = self._create_dependency_analysis_module(dependencies)
        modules.append(dependency_module)
        logger.debug("Added Dependency Analysis module.")
        
        # モジュール18: Error Handling
        error_handling_module = self._create_error_handling_module()
        modules.append(error_handling_module)
        logger.debug("Added Error Handling module.")
        
        # 他のファイルごとのモジュールを追加
        for file_path, data in parsed_data.items():
            # ファイル拡張子からファイルタイプを判定
            file_type = file_path.split('.')[-1].lower()
            module_name = self.filetype_to_module.get(file_type, "Generic File Information")
            module_id = self.section_to_module.get(module_name)

            if not module_id:
                logger.warning(f"No module ID found for module name: {module_name}")
                continue

            # 既にモジュールが追加されている場合はスキップ
            if any(mod["id"] == module_id for mod in modules):
                logger.debug(f"Module {module_name} already added. Skipping.")
                continue

            # フィールドのキーをマッピング
            mapped_content = self._map_fields(data)

            module = {
                "id": module_id,
                "name": module_name,
                "path": f"lingustruct/templates/m{module_id}.json",
                "schema": f"lingustruct/templates/m{module_id}_s.json",
                "dependencies": self.get_module_dependencies(module_id),
                "purpose": self.get_module_purpose(module_name),
                "category": self.get_module_category(module_name),
                "priority": module_id,
                "content": mapped_content
            }
            modules.append(module)
            logger.debug(f"Added {module_name} module for file: {file_path}")

        return modules

    def _create_meta_information_module(self, project_meta: Dict[str, Any]) -> Dict[str, Any]:
        """
        Meta Informationモジュールを作成します。

        :param project_meta: プロジェクトのメタ情報
        :return: Meta Informationモジュールの辞書
        """
        # フィールドのキーをマッピング
        mapped_meta = self._map_fields(project_meta)
        return {
            "id": self.section_to_module["Meta Information"],
            "name": "Meta Information",
            "path": "lingustruct/templates/m1.json",
            "schema": "lingustruct/templates/m1_s.json",
            "dependencies": [],
            "purpose": "Defines the metadata and project scope.",
            "category": "Metadata",
            "priority": 1,
            "content": mapped_meta,
        }

    def _create_technology_stack_module(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Technology Stackモジュールを作成します。

        :param parsed_data: 各ファイルからパースされたデータ
        :return: Technology Stackモジュールの辞書
        """
        tech_stack_content = {
            "languages": set(),
            "frameworks": set(),
            "tools": set(),
        }
        for file_path, file_data in parsed_data.items():
            # ライブラリ依存関係からツールを収集
            if "tools" in file_data:
                tech_stack_content["tools"].update(file_data["tools"])
            # ファイルタイプから言語を収集
            file_type = file_path.split('.')[-1].lower()
            language = self._map_language(file_type)
            if language:
                tech_stack_content["languages"].add(language)
            # フレームワークの収集ロジックがあれば追加
            # ここでは簡略化のため省略
                
        return {
            "id": self.section_to_module["Technology Stack"],
            "name": "Technology Stack",
            "path": "lingustruct/templates/m10.json",
            "schema": "lingustruct/templates/m10_s.json",
            "dependencies": [1],
            "purpose": "Describes the languages, frameworks, and tools used in the project.",
            "category": "Technology",
            "priority": 10,
            "content": {
                "languages": sorted(list(tech_stack_content["languages"])),
                "frameworks": sorted(list(tech_stack_content["frameworks"])),
                "tools": sorted(list(tech_stack_content["tools"]))
            },
        }

    def _create_dependency_analysis_module(self, dependencies: Dict[str, Dict[str, List[str]]]) -> Dict[str, Any]:
        """
        Dependency Analysisモジュールを作成します。

        :param dependencies: 各ファイルの依存関係
        :return: Dependency Analysisモジュールの辞書
        """
        # フィールドのキーをマッピング
        mapped_dependencies = {}
        for file, deps in dependencies.items():
            mapped_dependencies[file] = {
                "standard_libraries": deps.get("standard_libraries", []),
                "external_libraries": deps.get("external_libraries", []),
                "custom_modules": deps.get("custom_modules", []),
                "dependencies": deps.get("dependencies", [])
            }
        return {
            "id": self.section_to_module["Dependency Analysis"],
            "name": "Dependency Analysis",
            "path": "lingustruct/templates/m17.json",
            "schema": "lingustruct/templates/m17_s.json",
            "dependencies": [16],  # Generic File Information に依存
            "purpose": "Tracks dependency relationships between files.",
            "category": "Dependency Analysis",
            "priority": 17,
            "content": mapped_dependencies,
        }

    def _create_error_handling_module(self) -> Dict[str, Any]:
        """
        Error Handlingモジュールを作成します。

        :return: Error Handlingモジュールの辞書
        """
        # デフォルトのエラーハンドリング内容を使用
        error_handling_content = {
            "error_type": "Runtime",
            "recovery_strategy": "Retry",
            "logging": True,
            "notification": "Email"
        }
        # フィールドのキーをマッピング
        mapped_error_handling = self._map_fields(error_handling_content)
        return {
            "id": self.section_to_module["Error Handling"],
            "name": "Error Handling",
            "path": "lingustruct/templates/m18.json",
            "schema": "lingustruct/templates/m18_s.json",
            "dependencies": [],
            "purpose": "Defines the method for handling errors.",
            "category": "Error Management",
            "priority": 18,
            "content": mapped_error_handling
        }

    def get_module_dependencies(self, module_id: int) -> List[int]:
        """
        各モジュールの依存関係を返します。

        :param module_id: モジュールのID
        :return: 依存モジュールのIDリスト
        """
        dependencies = []
        # 各モジュールの依存関係を定義
        if module_id == 2:
            dependencies = [1]
        elif module_id == 3:
            dependencies = [1, 2]
        elif module_id == 4:
            dependencies = [1]
        elif module_id == 5:
            dependencies = [1]
        elif module_id == 6:
            dependencies = [1]
        elif module_id == 7:
            dependencies = [1, 2]
        elif module_id == 8:
            dependencies = [1, 2, 3]
        elif module_id == 9:
            dependencies = [1]
        elif module_id == 10:
            dependencies = [1]
        elif module_id in [11, 12, 13, 14, 15]:
            dependencies = [1, 10]
        elif module_id == 16:
            dependencies = []
        elif module_id == 17:
            dependencies = [16]
        elif module_id == 18:
            dependencies = []
        return dependencies

    def get_module_purpose(self, module_name: str) -> str:
        """
        モジュール名に基づいてpurposeを返します。

        :param module_name: モジュール名
        :return: モジュールのpurpose
        """
        purposes = {
            "Meta Information": "Defines the metadata and project scope.",
            "Architecture Information": "Describes the system's architecture and components.",
            "Dependency Resolution": "Specifies the dependency resolution strategy between modules.",
            "Error Handling": "Defines error handling strategies for different system components.",
            "Priority Management": "Manages task priorities across the system.",
            "Abbreviations and Glossary": "Defines abbreviations and key terms used in the project.",
            "Term Mappings": "Maps key concepts to implementation patterns and dependencies.",
            "Property Order Definition": "Defines the order in which properties are processed and prioritized.",
            "Version Control": "Specifies the versioning strategy for the project.",
            "Technology Stack": "Describes the languages, frameworks, and tools used in the project.",
            "TypeScript Module": "Describes key aspects of TypeScript files in the project.",
            "Python Module": "Describes key aspects of Python files in the project.",
            "Rust Module": "Describes key aspects of Rust files in the project.",
            "Go Module": "Describes key aspects of Go files in the project.",
            "JavaScript Module": "Describes key aspects of JavaScript files in the project.",
            "Generic File Information": "Stores general file metadata.",
            "Dependency Analysis": "Tracks dependency relationships between files.",
            "Error Handling": "Defines the method for handling errors."
        }
        return purposes.get(module_name, "")

    def get_module_category(self, module_name: str) -> str:
        """
        モジュール名に基づいてcategoryを返します。

        :param module_name: モジュール名
        :return: モジュールのcategory
        """
        categories = {
            "Meta Information": "Metadata",
            "Architecture Information": "Architecture",
            "Dependency Resolution": "Configuration",
            "Error Handling": "Error Management",
            "Priority Management": "Task Management",
            "Abbreviations and Glossary": "Documentation",
            "Term Mappings": "Mapping",
            "Property Order Definition": "Configuration",
            "Version Control": "Versioning",
            "Technology Stack": "Technology",
            "TypeScript Module": "File Specific",
            "Python Module": "File Specific",
            "Rust Module": "File Specific",
            "Go Module": "File Specific",
            "JavaScript Module": "File Specific",
            "Generic File Information": "General",
            "Dependency Analysis": "Dependency Analysis",
            "Error Handling": "Error Management"
        }
        return categories.get(module_name, "")

    def _map_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        key_mapping.json を使用してフィールド名をマッピングします。

        :param data: 元のデータ
        :return: マッピングされたデータ
        """
        mapped_data = {}
        for key, value in data.items():
            mapped_key = self.key_mapping.get(key, key)  # マッピングがなければそのまま
            mapped_data[mapped_key] = value
        return mapped_data

    def _map_language(self, file_type: str) -> Optional[str]:
        """
        ファイルタイプから言語名をマッピングします。

        :param file_type: ファイルの拡張子
        :return: 言語名
        """
        language_mapping = {
            "python": "Python",
            "typescript": "TypeScript",
            "javascript": "JavaScript",
            "rust": "Rust",
            "go": "Go"
            # 必要に応じて追加
        }
        return language_mapping.get(file_type.lower())
