import json
from typing import Optional
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
