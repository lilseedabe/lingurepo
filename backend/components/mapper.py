import json
from typing import Dict, Any, List
from utils.logger import setup_logger

logger = setup_logger(__name__)

class Mapper:
    def __init__(self, key_mapping: Dict[str, Any]):
        self.key_mapping = key_mapping

        # 各セクション名とテンプレートIDのマッピング
        self.section_to_module = {
            "Meta Information": 1,
            "Architecture Information": 2,
            "Dependency Resolution": 3,
            "Error Handling": 4,
            "Priority Management": 5,
            "Abbreviations and Glossary": 6,
            "Term Mappings": 7,
            "Property Order Definition": 8,
            "Version Control": 9,
            "Technology Stack": 10,
            "TypeScript Module": 11,
            "Python Module": 12,
            "Rust Module": 13,
            "Go Module": 14,
            "JavaScript Module": 15,
            "Generic File Information": 16,
            "Dependency Analysis": 17
        }

        # ファイルタイプと対応するモジュール名
        self.filetype_to_module = {
            "json": "Generic File Information",
            "python": "Python Module",
            "typescript": "TypeScript Module",
            "rust": "Rust Module",
            "go": "Go Module",
            "javascript": "JavaScript Module",
            "markdown": "Meta Information"  # README.mdなどに対応
        }

    def map_data_to_modules(self, parsed_data: Dict[str, Any], dependencies: Dict[str, List[str]], project_meta: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        データをテンプレートのモジュールに割り当て
        """
        modules = []
        
        # モジュール1: Meta Information
        meta_module = {
            "id": self.section_to_module["Meta Information"],
            "name": "Meta Information",
            "path": "lingustruct/templates/m1.json",
            "schema": "lingustruct/templates/m1_s.json",
            "dependencies": [],
            "purpose": "Defines the metadata and project scope.",
            "category": "Metadata",
            "priority": 1,
            "content": project_meta
        }
        modules.append(meta_module)
        logger.debug("Added Meta Information module.")

        # モジュール10: Technology Stack
        tech_stack_module = {
            "id": self.section_to_module["Technology Stack"],
            "name": "Technology Stack",
            "path": "lingustruct/templates/m10.json",
            "schema": "lingustruct/templates/m10_s.json",
            "dependencies": [1],
            "purpose": "Describes the languages, frameworks, and tools used in the project.",
            "category": "Technology",
            "priority": 10,
            "content": {
                "languages": set(),
                "frameworks": set(),
                "tools": set()
            }
        }

        # Collect technology stack information based on parsed data
        for file_type, data in parsed_data.items():
            if "dependencies" in data:
                for dep in data["dependencies"]:
                    tech_stack_module["content"]["tools"].add(dep)
            if file_type in ["python", "typescript", "rust", "go", "javascript"]:
                tech_stack_module["content"]["languages"].add(file_type.capitalize())
        # Convert sets to lists
        tech_stack_module["content"]["languages"] = list(tech_stack_module["content"]["languages"])
        tech_stack_module["content"]["frameworks"] = list(tech_stack_module["content"]["frameworks"])
        tech_stack_module["content"]["tools"] = list(tech_stack_module["content"]["tools"])
        modules.append(tech_stack_module)
        logger.debug("Added Technology Stack module.")

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

            module = {
                "id": module_id,
                "name": module_name,
                "path": f"lingustruct/templates/m{module_id}.json",
                "schema": f"lingustruct/templates/m{module_id}_s.json",
                "dependencies": self.get_module_dependencies(module_id),
                "purpose": self.get_module_purpose(module_name),
                "category": self.get_module_category(module_name),
                "priority": module_id,
                "content": data
            }
            modules.append(module)
            logger.debug(f"Added {module_name} module for file: {file_path}")

        # モジュール17: Dependency Analysis
        dependency_module = {
            "id": self.section_to_module["Dependency Analysis"],
            "name": "Dependency Analysis",
            "path": "lingustruct/templates/m17.json",
            "schema": "lingustruct/templates/m17_s.json",
            "dependencies": [self.section_to_module["Generic File Information"]],
            "purpose": "Tracks file dependencies and relationships.",
            "category": "Dependency Analysis",
            "priority": 17,
            "content": dependencies
        }
        modules.append(dependency_module)
        logger.debug("Added Dependency Analysis module.")

        # モジュール10: Technology Stack の content をリストに変換
        for mod in modules:
            if mod["id"] == self.section_to_module["Technology Stack"]:
                mod["content"]["languages"] = list(mod["content"]["languages"])
                mod["content"]["frameworks"] = list(mod["content"]["frameworks"])
                mod["content"]["tools"] = list(mod["content"]["tools"])

        return modules

    def get_module_dependencies(self, module_id: int) -> List[int]:
        """
        各モジュールの依存関係を返す
        """
        dependencies = []
        # ここに各モジュールの依存関係を定義
        # 例: モジュール2はモジュール1に依存
        if module_id == 2:
            dependencies = [1]
        elif module_id == 3:
            dependencies = [1,2]
        elif module_id == 4:
            dependencies = [1]
        elif module_id == 5:
            dependencies = [1]
        elif module_id == 6:
            dependencies = [1]
        elif module_id == 7:
            dependencies = [1,2]
        elif module_id == 8:
            dependencies = [1,2,3]
        elif module_id == 9:
            dependencies = [1]
        elif module_id == 10:
            dependencies = [1]
        elif module_id in [11,12,13,14,15]:
            dependencies = [1,10]
        elif module_id == 16:
            dependencies = []
        return dependencies

    def get_module_purpose(self, module_name: str) -> str:
        """
        モジュール名に基づいてpurposeを返す
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
            "Dependency Analysis": "Tracks file dependencies and relationships."
        }
        return purposes.get(module_name, "")

    def get_module_category(self, module_name: str) -> str:
        """
        モジュール名に基づいてcategoryを返す
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
            "Dependency Analysis": "Dependency Analysis"
        }
        return categories.get(module_name, "")
