import json
from typing import Optional, List, Dict, Union
from components.api_clients import APIClients
from utils.logger import setup_logger

logger = setup_logger(__name__)

class DataFetcher:
    def __init__(self, api_clients: APIClients):
        self.client = api_clients.groq  # Groqを利用しているため
        self.toolhouse = api_clients.toolhouse

    def fetch_readme_content(self, repo_name: str, branch_name: str) -> Optional[str]:
        try:
            messages = [{
                "role": "user",
                "content": (
                    f"Use the github_file tool to read the content of README.md "
                    f"in the {repo_name} repository on branch {branch_name}. "
                    f"The operation should be 'read'."
                )
            }]
            
            logger.info("Fetching README.md content")
            response = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=messages,
                tools=self.toolhouse.get_tools()
            )

            result = self.toolhouse.run_tools(response)
            
            if not result or not any(item['role'] == 'tool' for item in result):
                raise ValueError("Toolhouse returned an invalid or empty response.")
            
            tool_response = next(item for item in result if item['role'] == 'tool')
            file_content = tool_response['content']
            logger.info("Successfully fetched README.md content")
            return file_content

        except Exception as e:
            logger.error(f"Error fetching README.md content: {e}", exc_info=True)
            return None

    def fetch_file_tree(self, repo_name: str, branch_name: str) -> Optional[List[Dict[str, Union[str, List]]]]:
        """
        リポジトリ内のフォルダ名とファイル名を取得し、再帰的に構造化して返します。
        """
        try:
            # Toolhouse の github_file ツールを使用してディレクトリの内容を取得
            messages = [{
                "role": "user",
                "content": f'github_file({{"operation": "read", "path": "/", "content": {{"repo_name": "{repo_name}", "branch_name": "{branch_name}"}}}})'
            }]
            
            logger.info("Fetching repository file tree from root")
            response = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=messages,
                tools=self.toolhouse.get_tools()
            )

            result = self.toolhouse.run_tools(response)
            
            if not result or not any(item['role'] == 'tool' for item in result):
                raise ValueError("Toolhouse returned an invalid or empty response.")
            
            tool_response = next(item for item in result if item['role'] == 'tool')
            logger.debug(f"Tool response content for root: {tool_response['content']}")

            # ツールから取得した全ファイルパスをリストにする
            file_paths = []
            lines = tool_response['content'].splitlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # 各行の形式が "path type:file bytes:xxxx" であると仮定
                parts = line.split()
                if len(parts) >= 2:
                    path = parts[0]
                    item_type_part = parts[1]
                    if 'type:' in item_type_part:
                        item_type = item_type_part.split(":")[1]
                        if item_type == 'file':
                            file_paths.append(path)
                        # ディレクトリ情報が含まれている場合は必要に応じて処理

            # ファイルパスからディレクトリ構造を構築
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
            parts = path.strip("/").split("/")
            current_level = tree
            current_path = ""
            for part in parts[:-1]:  # ファイル名以外の部分（ディレクトリ）
                current_path = f"{current_path}/{part}" if current_path else part
                if part not in current_level:
                    current_level[part] = {"type": "directory", "children": {}, "path": current_path}
                current_level = current_level[part]["children"]
            # 最後の部分はファイル
            file_name = parts[-1]
            file_path = path
            current_level[file_name] = {"type": "file", "path": file_path}

        # 再帰的に辞書をリスト形式に変換
        def dict_to_list(d: Dict, current_path: str) -> List[Dict]:
            result = []
            for name, info in d.items():
                if info["type"] == "directory":
                    result.append({
                        "name": name,
                        "type": "directory",
                        "path": info["path"],
                        "children": dict_to_list(info["children"], info["path"])
                    })
                elif info["type"] == "file":
                    result.append({
                        "name": name,
                        "type": "file",
                        "path": info["path"]
                    })
            return result

        return dict_to_list(tree, "")

    def fetch_files_content(self, repo_name: str, branch_name: str, file_paths: List[str]) -> Dict[str, str]:
        """
        選択された複数のファイルの内容を取得します。
        """
        file_contents = {}
        for file_path in file_paths:
            try:
                messages = [{
                    "role": "user",
                    "content": (
                        f'github_file({{"operation": "read", "path": "{file_path}", "content": {{"repo_name": "{repo_name}", "branch_name": "{branch_name}"}}}})'
                    )
                }]
                logger.info(f"Fetching content of {file_path}")
                response = self.client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=messages,
                    tools=self.toolhouse.get_tools()
                )

                result = self.toolhouse.run_tools(response)

                if not result or not any(item['role'] == 'tool' for item in result):
                    raise ValueError(f"Toolhouse returned an invalid or empty response for {file_path}.")

                tool_response = next(item for item in result if item['role'] == 'tool')
                content = tool_response['content']
                file_contents[file_path] = content
                logger.info(f"Successfully fetched content of {file_path}")
            except Exception as e:
                logger.error(f"Error fetching content of {file_path}: {e}", exc_info=True)
                file_contents[file_path] = ""

        return file_contents
