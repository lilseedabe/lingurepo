import os
import requests
import logging
import json
from dotenv import load_dotenv
from toolhouse import Toolhouse
from groq import Groq
from lingustruct import LinguStruct

# ログ設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 環境変数のロード
load_dotenv()

# 必要な情報を取得
LINGUSTRUCT_KEY = os.getenv('LINGUSTRUCT_LICENSE_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
TOOLHOUSE_API_KEY = os.getenv('TOOLHOUSE_API_KEY')
REPO_NAME = os.getenv('REPO_NAME')
BRANCH_NAME = os.getenv('BRANCH_NAME')
USER_ID = os.getenv('USER_ID', 'default_user')

# API初期化とメタデータ設定
client = Groq(api_key=GROQ_API_KEY)
th = Toolhouse(api_key=TOOLHOUSE_API_KEY)
th.set_metadata('id', USER_ID)
lingu = LinguStruct()

def verify_environment():
    """環境変数の検証"""
    required_vars = {
        'LINGUSTRUCT_LICENSE_KEY': LINGUSTRUCT_KEY,
        'GROQ_API_KEY': GROQ_API_KEY,
        'TOOLHOUSE_API_KEY': TOOLHOUSE_API_KEY,
        'REPO_NAME': REPO_NAME,
        'BRANCH_NAME': BRANCH_NAME
    }
    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")
    else:
        logger.info("Environment variables verified successfully.")
        for var, value in required_vars.items():
            logger.debug(f"{var}: {value}")

def verify_toolhouse_setup():
    """Toolhouseの設定と利用可能なツールを確認"""
    try:
        tools = th.get_tools()
        available_tools = [tool.get('name') for tool in tools if 'name' in tool]
        
        logger.debug(f"Retrieved tools: {available_tools}")
        
        if not tools:
            raise ValueError("No tools available in Toolhouse configuration")
            
        if 'github_file' not in available_tools:
            logger.error(f"Expected tool 'github_file' not found. Available tools: {available_tools}")
            raise ValueError("github_file tool is not available in Toolhouse")
            
        logger.info(f"Available Toolhouse tools: {available_tools}")
        return True
        
    except Exception as e:
        logger.error(f"Toolhouse setup verification failed: {e}")
        return False

def fetch_readme_content():
    """Toolhouseを使用してGitHubリポジトリからREADME.mdファイルを取得"""
    try:
        if not verify_toolhouse_setup():
            logger.error("Toolhouse setup verification failed, github_file tool is unavailable.")
            return None

        # パラメータを詳細にログ出力
        logger.debug(f"Requesting README.md with parameters: repo={REPO_NAME}, branch={BRANCH_NAME}")

        messages = [{
            "role": "user",
            "content": (
                f"Use the github_file tool to read the content of README.md "
                f"in the {REPO_NAME} repository on branch {BRANCH_NAME}. "
                f"The operation should be 'read'."
            )
        }]

        logger.info("Fetching README.md content using Toolhouse")
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages,
            tools=th.get_tools()
        )
        logger.debug(f"Groq Response for README.md: {response}")

        result = th.run_tools(response)
        logger.debug(f"Toolhouse Response for README.md: {result}")

        if not result or not any(item['role'] == 'tool' for item in result):
            raise ValueError("Toolhouse returned an invalid or empty response for README.md")

        tool_response = next(item for item in result if item['role'] == 'tool')
        file_content = tool_response['content']
        
        if "404" in file_content or "error" in file_content.lower():
            logger.error(f"File not found or error in response: {file_content}")
            return None
            
        if not file_content.strip():
            logger.error("Empty content returned for README.md")
            return None

        logger.info("Successfully fetched README.md content")
        return file_content

    except Exception as e:
        logger.error(f"Error fetching README.md: {e}", exc_info=True)
        return None

def load_key_mapping():
    """LinguStruct APIからkey_mapping.jsonを取得する"""
    try:
        url = "https://lingustruct.onrender.com/lingu_struct/key_mapping"
        headers = {
            "LINGUSTRUCT_LICENSE_KEY": LINGUSTRUCT_KEY
        }
        logger.info("Fetching key_mapping.json from LinguStruct API")
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            key_mapping = response.json()
            logger.debug("Key mapping loaded successfully from API.")
            return key_mapping
        else:
            logger.error(f"Failed to fetch key mapping: {response.status_code} {response.text}")
            response.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to load key mapping via API: {e}")
        raise

def get_parsing_rules_from_groq(key_mapping):
    """Groq AIにkey_mappingを送信し、解析ルールを取得する"""
    try:
        prompt = (
            "以下のキーとラベルのマッピングに基づいて、ドキュメントを解析するためのルールを作成してください。\n\n"
            f"{json.dumps(key_mapping, ensure_ascii=False, indent=4)}\n\n"
            "このルールを使用して、README.mdファイルの内容を解析し、各セクションに対応するデータを抽出してください。"
        )
        
        messages = [
            {"role": "system", "content": "あなたは優れたドキュメント解析エンジンです。"},
            {"role": "user", "content": prompt}
        ]
        
        logger.info("Sending key_mapping.json to Groq AI to generate parsing rules")
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages
        )
        
        parsing_rules = response.choices[0].message.content
        logger.debug("Parsing rules generated successfully from Groq AI.")
        return parsing_rules

    except Exception as e:
        logger.error(f"Error communicating with Groq AI: {e}")
        raise

def parse_readme_with_groq(file_content, parsing_rules):
    """Groq AIを使用してREADME.mdの内容を解析する"""
    try:
        prompt = (
            "以下の解析ルールに基づいて、README.mdファイルの内容を解析し、各セクションに対応するデータを抽出してください。\n\n"
            f"{parsing_rules}\n\n"
            "README.mdの内容:\n\n"
            f"{file_content}\n\n"
            "解析結果をJSON形式で提供してください。"
        )
        
        messages = [
            {"role": "system", "content": "あなたは優れたドキュメント解析エンジンです。"},
            {"role": "user", "content": prompt}
        ]
        
        logger.info("Sending README.md content to Groq AI for parsing")
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages
        )
        
        parsed_data = response.choices[0].message.content
        parsed_data_json = json.loads(parsed_data)
        logger.debug("README.md content parsed successfully by Groq AI.")
        return parsed_data_json

    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode parsed data from Groq AI: {e}")
        raise
    except Exception as e:
        logger.error(f"Error parsing README.md with Groq AI: {e}")
        raise

def map_data_to_templates(parsed_data, key_mapping):
    """解析されたデータを適切なテンプレートにマッピングする"""
    try:
        section_to_module = {
            "Meta Information": 1,
            "Architecture Information": 2,
            "Dependency Resolution": 3,
            "Error Handling": 4,
            "Priority Management": 5,
            "Abbreviations and Glossary": 6,
            "Term Mappings": 7,
            "Property Order Definition": 8,
            "Version Control": 9,
            "Technology Stack": 10
        }
        
        modules_data = []
        
        for section, data in parsed_data.items():
            module_id = section_to_module.get(section)
            if not module_id:
                logger.warning(f"No template mapping found for section '{section}'. Skipping.")
                continue
            
            template_path = f"lingustruct/templates/m{module_id}.json"
            schema_path = f"lingustruct/templates/m{module_id}_s.json"
            
            module_data = {
                "id": module_id,
                "name": section,
                "path": template_path,
                "schema": schema_path,
                "dependencies": [],
                "purpose": f"Defines the {section.lower()}.",
                "category": section.split()[0],
                "priority": module_id
            }
            
            module_data_content = {}
            for key, value in data.items():
                mapped_key = key_mapping.get(key, key)
                module_data_content[mapped_key] = value
            
            modules_data.append(module_data_content)
            logger.debug(f"Mapped data for section '{section}': {module_data_content}")
        
        logger.info("Data mapped to templates successfully.")
        return modules_data
    
    except Exception as e:
        logger.error(f"Error mapping data to templates: {e}")
        raise

def generate_final_document(mapped_data):
    """LinguStructテンプレートを使って最終設計書を生成"""
    try:
        if not mapped_data:
            raise ValueError("No mapped data available to generate document")

        url = "https://lingustruct.onrender.com/lingu_struct/generate_master"
        headers = {
            "Content-Type": "application/json",
            "LINGUSTRUCT_LICENSE_KEY": LINGUSTRUCT_KEY
        }
        data = {
            "project_id": "moduvo_project",
            "version": "1.0",
            "modules": mapped_data
        }

        logger.info("Sending request to generate final document")
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()
        logger.info("Successfully generated final document")
        return result

    except Exception as e:
        logger.error(f"Failed to generate final document: {e}", exc_info=True)
        return None

def generate_design_document():
    """GitHubからREADME.mdファイルを取得し設計書を生成"""
    try:
        verify_environment()
        
        # Toolhouseのセットアップを確認
        if not verify_toolhouse_setup():
            logger.error("Toolhouse setup verification failed")
            return
        
        key_mapping = load_key_mapping()
        parsing_rules = get_parsing_rules_from_groq(key_mapping)
        readme_content = fetch_readme_content()
        if not readme_content:
            logger.warning("README.md content could not be fetched")
            return

        parsed_data = parse_readme_with_groq(readme_content, parsing_rules)
        mapped_data = map_data_to_templates(parsed_data, key_mapping)
        if not mapped_data:
            logger.warning("No data was mapped successfully")
            return

        final_document = generate_final_document(mapped_data)
        if final_document:
            logger.info("Design document generation completed successfully")
            logger.info(f"Final Document:\n{json.dumps(final_document, indent=4)}")
            return final_document

    except Exception as e:
        logger.error(f"Error in generate_design_document: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        logger.info("Starting design document generation process")
        generate_design_document()
        logger.info("Process completed")
    except Exception as e:
        logger.error("Process failed", exc_info=True)
        raise
