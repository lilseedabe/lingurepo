import ast
import json
import yaml
from typing import Optional, List, Dict, Union
from components.api_clients import APIClients
from utils.logger import setup_logger

logger = setup_logger(__name__)

class DataFetcher:
    def __init__(self, api_clients: APIClients):
        self.client = api_clients.groq
        self.toolhouse = api_clients.toolhouse

    def fetch_file_tree(self, repo_name: str, branch_name: str) -> Optional[List[Dict[str, Union[str, List]]]]:
        """
        リポジトリ内のフォルダ名とファイル名を取得し、再帰的に構造化して返します。
        """
        try:
            messages = [{
                "role": "user",
                "content": f'github_file({{"operation": "read", "path": "/"}})'
            }]
            
            logger.info(f"Fetching repository file tree for repo: {repo_name}, branch: {branch_name}")
            response = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=messages,
                tools=self.toolhouse.get_tools()
            )

            result = self.toolhouse.run_tools(response)
            
            if not result or not any(item['role'] == 'tool' for item in result):
                raise ValueError("Toolhouse returned an invalid or empty response.")
            
            tool_response = next(item for item in result if item['role'] == 'tool')
            logger.debug(f"Tool response content: {tool_response['content']}")

            # フラットなパスリストを作成
            file_paths = [line.strip().split()[0] for line in tool_response['content'].splitlines() if line.strip()]
            logger.debug(f"Extracted file paths: {file_paths}")

            # ファイルパスからツリー構造を構築
            file_tree = self.build_file_tree(file_paths)

            logger.info("Successfully fetched and structured repository file tree")
            return file_tree

        except Exception as e:
            logger.error(f"Error fetching repository file tree: {e}", exc_info=True)
            return None

    def build_file_tree(self, file_paths: List[str]) -> List[Dict[str, Union[str, List]]]:
        """
        フラットなファイルパスのリストからディレクトリツリーを構築します。
        """
        tree: Dict[str, Dict] = {}
        for path in file_paths:
            parts = path.strip("/").split("/")  # パスを分割
            current_level = tree
            for part in parts[:-1]:  # ファイル名以外の部分（ディレクトリ）
                if part not in current_level:
                    current_level[part] = {"type": "directory", "children": {}}
                current_level = current_level[part]["children"]
            current_level[parts[-1]] = {"type": "file", "path": path}  # ファイル

        def dict_to_list(d: Dict) -> List[Dict]:
            """
            ツリー構造の辞書をリスト形式に変換します。
            """
            result = []
            for name, info in d.items():
                if info["type"] == "directory":
                    result.append({
                        "name": name,
                        "type": "directory",
                        "children": dict_to_list(info["children"])  # 再帰的に子を処理
                    })
                else:
                    result.append({
                        "name": name,
                        "type": "file",
                        "path": info["path"]
                    })
            return result

        return dict_to_list(tree)

    def fetch_files_content(self, repo_name: str, branch_name: str, file_paths: List[str]) -> Dict[str, str]:
        """
        選択された複数のファイルの内容を取得します。
        """
        if not file_paths:
            logger.warning("No file paths provided for fetching content.")
            return {}

        file_contents = {}
        for file_path in file_paths:
            try:
                messages = [{
                    "role": "user",
                    "content": f'github_file({{"operation": "read", "path": "{file_path}"}})'
                }]
                logger.info(f"Fetching content of file: {file_path}")
                
                response = self.client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=messages,
                    tools=self.toolhouse.get_tools()
                )

                result = self.toolhouse.run_tools(response)
                if not result or not any(item['role'] == 'tool' for item in result):
                    raise ValueError(f"Toolhouse returned an invalid or empty response for file: {file_path}")

                tool_response = next(item for item in result if item['role'] == 'tool')
                content = tool_response.get('content', '').strip()
                
                if not content:
                    logger.warning(f"Content for {file_path} is empty. Skipping.")
                    continue
                
                file_contents[file_path] = content
                logger.info(f"Successfully fetched content of file: {file_path}")

            except ValueError as ve:
                logger.error(f"Validation error for file: {file_path}: {ve}")
            except Exception as e:
                logger.error(f"Error fetching content of file: {file_path}: {e}", exc_info=True)

        if not file_contents:
            logger.warning("No file contents were successfully fetched.")
        return file_contents

    def analyze_dependencies(self, file_contents: Dict[str, str]) -> Dict[str, Dict[str, List[str]]]:
        """
        ファイル間の依存関係を解析し、分類
        """
        dependencies = {}
        for file_path, content in file_contents.items():
            if file_path.endswith(".py"):
                dependencies[file_path] = self._analyze_python_dependencies(content)
            elif file_path.endswith((".json", ".yaml", ".yml")):
                dependencies[file_path] = self._analyze_json_yaml_dependencies(content)
            else:
                dependencies[file_path] = {"standard_libraries": [], "external_libraries": [], "custom_modules": []}
        logger.debug(f"Dependencies: {dependencies}")
        return dependencies

    def _analyze_python_dependencies(self, content: str) -> Dict[str, List[str]]:
        """
        Pythonファイルの依存関係を分類
        """
        try:
            tree = ast.parse(content)
            standard_libraries = []
            external_libraries = []
            custom_modules = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self._classify_dependency(alias.name, standard_libraries, external_libraries, custom_modules)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    self._classify_dependency(module, standard_libraries, external_libraries, custom_modules)
            return {
                "standard_libraries": standard_libraries,
                "external_libraries": external_libraries,
                "custom_modules": custom_modules
            }
        except Exception as e:
            logger.error(f"Error analyzing Python dependencies: {e}")
            return {"standard_libraries": [], "external_libraries": [], "custom_modules": []}

    def _classify_dependency(self, module_name: str, std_libs: List[str], ext_libs: List[str], custom_mods: List[str]):
        """
        依存関係を分類
        """
        if module_name in {"os", "sys", "time", "json", "re", "logging"}:
            std_libs.append(module_name)
        elif module_name in {"dotenv", "fastapi", "requests", "psycopg2"}:
            ext_libs.append(module_name)
        else:
            custom_mods.append(module_name)

    def _analyze_json_yaml_dependencies(self, content: str) -> Dict[str, List[str]]:
        """
        JSONやYAMLファイルの依存関係を解析
        """
        try:
            data = yaml.safe_load(content)
            if isinstance(data, dict):
                return {"dependencies": data.get("dependencies", [])}
            return {"dependencies": []}
        except yaml.YAMLError:
            logger.warning("Invalid YAML/JSON content.")
        except Exception as e:
            logger.error(f"Error analyzing JSON/YAML dependencies: {e}")
        return {"dependencies": []}

    def extract_meta_information(self, readme_content: str) -> Dict[str, str]:
        """
        README.md からプロジェクトのメタ情報を抽出
        """
        meta_info = {}
        lines = readme_content.splitlines()
        for line in lines:
            if "Project Name:" in line:
                meta_info["project_name"] = line.split(":", 1)[1].strip()
            elif "Version:" in line:
                meta_info["version"] = line.split(":", 1)[1].strip()
        return meta_info
