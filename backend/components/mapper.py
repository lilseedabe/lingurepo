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
            "CSS Module": 19,  # 新規追加
            "Generic File Information": 16,  # 新規追加
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
            "css": "CSS Module",  # 新規追加
            # その他のファイルタイプも必要に応じて追加
        }

        # モジュール名からフィールド定義へのマッピング
        self.module_to_fields = {
            "Meta Information": {
                "t_v": {
                    "type": "string",
                    "label": "Template Version",
                    "priority": 1,
                    "required": True
                },
                "p_n": {
                    "type": "string",
                    "label": "Project Name",
                    "priority": 2,
                    "required": True
                },
                "p_v": {
                    "type": "string",
                    "label": "Project Version",
                    "priority": 3,
                    "required": True
                },
                "desc": {
                    "type": "string",
                    "label": "Description",
                    "priority": 4,
                    "required": True
                },
                "scale": {
                    "type": "string",
                    "enum": [
                        "s",
                        "m",
                        "l",
                        "e"
                    ],
                    "label": "Scale",
                    "priority": 5,
                    "required": True
                }
            },
            "Technology Stack": {
                "v": {
                    "type": "string",
                    "label": "Technology Version",
                    "priority": 1,
                    "required": True
                },
                "languages": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "label": "Programming Languages",
                    "priority": 2,
                    "required": True
                },
                "frameworks": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "label": "Frameworks",
                    "priority": 3,
                    "required": False
                },
                "tools": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "label": "Development Tools",
                    "priority": 4,
                    "required": False
                }
            },
            "Dependency Analysis": {
                "dep_tree": {
                    "type": "object",
                    "label": "Dependency Tree",
                    "priority": 1,
                    "required": True,
                    "properties": {
                        "file": {
                            "type": "string",
                            "label": "File Path",
                            "priority": 1,
                            "required": True
                        },
                        "standard_libraries": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "label": "Standard Libraries",
                            "priority": 2,
                            "required": False
                        },
                        "external_libraries": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "label": "External Libraries",
                            "priority": 3,
                            "required": False
                        },
                        "custom_modules": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "label": "Custom Modules",
                            "priority": 4,
                            "required": False
                        },
                        "dependencies": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "label": "Dependencies",
                            "priority": 5,
                            "required": False
                        }
                    }
                }
            },
            "Error Handling": {
                "error_type": {
                    "type": "string",
                    "label": "Error Type",
                    "enum": [
                        "Runtime",
                        "Logic",
                        "Network",
                        "Validation",
                        "Unknown"
                    ],
                    "priority": 1,
                    "required": True
                },
                "recovery_strategy": {
                    "type": "string",
                    "label": "Recovery Strategy",
                    "enum": [
                        "Retry",
                        "Fallback",
                        "Abort",
                        "Log Only",
                        "Ignore"
                    ],
                    "priority": 2,
                    "required": False
                },
                "logging": {
                    "type": "boolean",
                    "label": "Enable Logging",
                    "priority": 3,
                    "required": False
                },
                "notification": {
                    "type": "string",
                    "label": "Notification Method",
                    "enum": [
                        "Email",
                        "Slack",
                        "Webhook",
                        "None"
                    ],
                    "priority": 4,
                    "required": False
                }
            },
            "CSS Module": {
                "selectors": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "label": "CSS Selectors",
                    "priority": 1,
                    "required": False
                }
            },
            "Generic File Information": {
                "file_name": {
                    "type": "string",
                    "label": "File Name",
                    "priority": 1,
                    "required": True
                },
                "file_type": {
                    "type": "string",
                    "label": "File Type",
                    "priority": 2,
                    "required": True
                },
                "size": {
                    "type": "integer",
                    "label": "File Size (bytes)",
                    "priority": 3,
                    "required": False
                },
                "last_modified": {
                    "type": "string",
                    "format": "date-time",
                    "label": "Last Modified",
                    "priority": 4,
                    "required": False
                }
            }
            # Add more module fields as needed
        }

    def map_data_to_modules(self, parsed_data: Dict[str, Any], dependencies: Dict[str, Dict[str, List[str]]], project_meta: Dict[str, Any]) -> Dict[str, Any]:
        """
        データをテンプレートのモジュールに割り当てます。

        :param parsed_data: 各ファイルからパースされたデータ
        :param dependencies: 各ファイルの依存関係
        :param project_meta: プロジェクトのメタ情報
        :return: 完成した設計書のデータ構造
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

        # モジュール19: CSS Module (新規追加)
        css_module = self._create_css_module(parsed_data)
        if css_module:
            modules.append(css_module)
            logger.debug("Added CSS Module.")

        # モジュール16: Generic File Information (ファイルごとに追加)
        generic_module_id = self.section_to_module.get("Generic File Information")
        if not generic_module_id:
            logger.error("Generic File Information module ID is not defined.")
            # Alternatively, define a default ID or raise an error
            raise ValueError("Generic File Information module ID is not defined.")

        # 他のファイルごとのモジュールを追加
        for file_path, data in parsed_data.items():
            # ファイル拡張子からファイルタイプを判定
            file_type = file_path.split('.')[-1].lower()
            module_name = self.filetype_to_module.get(file_type, "Generic File Information")
            module_id = self.section_to_module.get(module_name)

            if not module_id:
                logger.warning(f"No module ID found for module name: {module_name}")
                continue

            if module_name == "Generic File Information":
                # Create a unique entry for each file
                mapped_content = self._map_fields(data)
                fields = self.module_to_fields.get(module_name, {})

                # Add additional file-specific fields
                mapped_content["file_name"] = os.path.basename(file_path)
                mapped_content["file_type"] = file_type
                # Assuming 'size' and 'last_modified' are available; if not, they can be omitted or fetched elsewhere

                module = {
                    "id": module_id,
                    "name": module_name,
                    "path": f"lingustruct/templates/m{module_id}.json",
                    "schema": f"lingustruct/templates/m{module_id}_s.json",
                    "dependencies": self.get_module_dependencies(module_id),
                    "purpose": self.get_module_purpose(module_name),
                    "category": self.get_module_category(module_name),
                    "priority": module_id,
                    "content": mapped_content,
                    "fields": fields
                }
                modules.append(module)
                logger.debug(f"Added {module_name} module for file: {file_path}")
            else:
                # For non-generic modules, skip if already added
                if any(mod["id"] == module_id for mod in modules):
                    logger.debug(f"Module {module_name} already added. Skipping.")
                    continue

                # For other modules, map as usual
                mapped_content = self._map_fields(data)
                fields = self.module_to_fields.get(module_name, {})

                module = {
                    "id": module_id,
                    "name": module_name,
                    "path": f"lingustruct/templates/m{module_id}.json",
                    "schema": f"lingustruct/templates/m{module_id}_s.json",
                    "dependencies": self.get_module_dependencies(module_id),
                    "purpose": self.get_module_purpose(module_name),
                    "category": self.get_module_category(module_name),
                    "priority": module_id,
                    "content": mapped_content,
                    "fields": fields
                }
                modules.append(module)
                logger.debug(f"Added {module_name} module for file: {file_path}")

        # Optional: Add relationships based on dependencies
        relationships = self._create_relationships(dependencies)

        # Construct final data structure
        final_data = {
            "meta": {
                "document_type": "system_design_document",
                "description": "This document defines the modular structure, dependencies, and adaptive components of the system.",
                "template_version": "1.0"
            },
            "project_id": project_meta.get("project_id", "lingurepo_project"),
            "version": project_meta.get("project_version", "1.0"),
            "modules": modules,
            "relationships": relationships,
            # Other sections can be added here (adaptive_patterns, quality_assurance, etc.)
        }

        return final_data

    def _create_meta_information_module(self, project_meta: Dict[str, Any]) -> Dict[str, Any]:
        """
        Meta Informationモジュールを作成します。

        :param project_meta: プロジェクトのメタ情報
        :return: Meta Informationモジュールの辞書
        """
        # フィールドのキーをマッピング
        mapped_meta = self._map_fields(project_meta)
        fields = self.module_to_fields.get("Meta Information", {})
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
            "fields": fields
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
            # Collect languages based on file type
            file_type = file_path.split('.')[-1].lower()
            language = self._map_language(file_type)
            if language:
                tech_stack_content["languages"].add(language)

            # Collect external libraries and custom modules as tools
            external_libraries = file_data.get("external_libraries", [])
            custom_modules = file_data.get("custom_modules", [])
            tech_stack_content["tools"].update(external_libraries)
            tech_stack_content["tools"].update(custom_modules)

            # If frameworks are part of external libraries, you might need to separate them
            # For simplicity, assuming frameworks are identified separately
            # You can implement additional logic to classify frameworks if needed

        # Optionally, define frameworks based on known frameworks
        known_frameworks = {"FastAPI", "React", "Django", "Flask", "Express", "Vue", "Angular"}
        tech_stack_content["frameworks"] = tech_stack_content["tools"].intersection(known_frameworks)
        tech_stack_content["tools"] = tech_stack_content["tools"].difference(known_frameworks)

        fields = self.module_to_fields.get("Technology Stack", {})

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
            "fields": fields
        }

    def _create_dependency_analysis_module(self, dependencies: Dict[str, Dict[str, List[str]]]) -> Dict[str, Any]:
        """
        Dependency Analysisモジュールを作成します。

        :param dependencies: 各ファイルの依存関係
        :return: Dependency Analysisモジュールの辞書
        """
        # フィールドのキーをマッピング
        dep_tree = {}
        for file, deps in dependencies.items():
            dep_tree[file] = {
                "standard_libraries": deps.get("standard_libraries", []),
                "external_libraries": deps.get("external_libraries", []),
                "custom_modules": deps.get("custom_modules", []),
                "dependencies": deps.get("dependencies", [])
            }

        fields = self.module_to_fields.get("Dependency Analysis", {})

        return {
            "id": self.section_to_module["Dependency Analysis"],
            "name": "Dependency Analysis",
            "path": "lingustruct/templates/m17.json",
            "schema": "lingustruct/templates/m17_s.json",
            "dependencies": [16],  # Generic File Information に依存
            "purpose": "Tracks dependency relationships between files.",
            "category": "Dependency Analysis",
            "priority": 17,
            "content": dep_tree,
            "fields": fields
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
        fields = self.module_to_fields.get("Error Handling", {})
        return {
            "id": self.section_to_module["Error Handling"],
            "name": "Error Handling",
            "path": "lingustruct/templates/m18.json",
            "schema": "lingustruct/templates/m18_s.json",
            "dependencies": [],
            "purpose": "Defines the method for handling errors.",
            "category": "Error Management",
            "priority": 18,
            "content": mapped_error_handling,
            "fields": fields
        }

    def _create_css_module(self, parsed_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        CSS Moduleを作成します。

        :param parsed_data: 各ファイルからパースされたデータ
        :return: CSS Moduleの辞書またはNone
        """
        css_selectors = set()
        for file_path, file_data in parsed_data.items():
            file_type = file_path.split('.')[-1].lower()
            if file_type == "css":
                selectors = file_data.get("selectors", [])
                css_selectors.update(selectors)
        
        if not css_selectors:
            return None

        fields = self.module_to_fields.get("CSS Module", {})

        return {
            "id": self.section_to_module["CSS Module"],
            "name": "CSS Module",
            "path": "lingustruct/templates/m19.json",
            "schema": "lingustruct/templates/m19_s.json",
            "dependencies": [],
            "purpose": "Describes the CSS selectors used in the project.",
            "category": "Style",
            "priority": 19,
            "content": {
                "selectors": sorted(list(css_selectors))
            },
            "fields": fields
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
        elif module_id == 19:
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
            "CSS Module": "Describes key aspects of CSS files in the project.",
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
            "CSS Module": "File Specific",
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

    def _create_relationships(self, dependencies: Dict[str, Dict[str, List[str]]]) -> List[Dict[str, Any]]:
        """
        依存関係から関係性を生成します。

        :param dependencies: 各ファイルの依存関係
        :return: 関係性のリスト
        """
        relationships = []
        file_to_module_id = {}  # ファイルパスからモジュールIDを取得

        # Assign unique IDs to file-specific modules
        # For 'Generic File Information', since it can represent multiple files, assign module ID to each file
        generic_module_id = self.section_to_module.get("Generic File Information")
        if generic_module_id:
            for file_path in dependencies.keys():
                file_to_module_id[file_path] = generic_module_id

        # Create relationships based on dependencies
        for source_file, deps in dependencies.items():
            source_id = file_to_module_id.get(source_file)
            if not source_id:
                continue
            for dep in deps.get("dependencies", []):
                # Find the target module ID
                target_id = file_to_module_id.get(dep)
                if target_id:
                    relationship = {
                        "source": source_id,
                        "target": target_id,
                        "type": "dependency",
                        "description": f"{source_file} depends on {dep}"
                    }
                    relationships.append(relationship)
        return relationships
