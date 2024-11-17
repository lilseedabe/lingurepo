import json
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
                # Toolhouse 仕様に基づいたリクエストを作成
                messages = [{
                    "role": "user",
                    "content": f'github_file({{"operation": "read", "path": "{file_path}"}})'
                }]
                logger.info(f"Fetching content of file: {file_path}")
                
                # Groq AI へのリクエストを送信
                response = self.client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=messages,
                    tools=self.toolhouse.get_tools()
                )

                # ツール実行結果を取得
                result = self.toolhouse.run_tools(response)
                if not result or not any(item['role'] == 'tool' for item in result):
                    raise ValueError(f"Toolhouse returned an invalid or empty response for file: {file_path}")

                # ツールのレスポンスを処理
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
