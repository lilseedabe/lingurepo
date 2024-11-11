import json
import re
import requests
from typing import Dict, Any
from components.api_clients import APIClients
from utils.logger import setup_logger

logger = setup_logger(__name__)

class Parser:
    def __init__(self, api_clients: APIClients, lingu_key: str):
        self.client = api_clients.groq
        self.lingu_key = lingu_key

    def load_key_mapping(self) -> Dict[str, Any]:
        """Fetch key_mapping.json from the LinguStruct API."""
        try:
            url = "https://lingustruct.onrender.com/lingu_struct/key_mapping"
            headers = {
                "LINGUSTRUCT_LICENSE_KEY": self.lingu_key
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

    def get_parsing_rules(self, key_mapping: Dict[str, Any]) -> str:
        """Send key_mapping to Groq AI to generate flexible parsing rules."""
        try:
            prompt = (
                "Based on the following key-label mapping, create a set of parsing rules. "
                "The rules should allow for flexible matching based on context, synonyms, section positioning, and partial keyword matches.\n\n"
                f"{json.dumps(key_mapping, ensure_ascii=False, indent=4)}\n\n"
                "For each key-label, analyze the general structure of README.md files to define where this information is usually located, "
                "and provide flexibility to identify the best match even if exact words or formats are not present.\n\n"
                "Example for generating flexible rules:\n"
                "- Project Name: Look for terms like 'Project', 'Title', or 'Repository' near the top.\n"
                "- Version: Identify words such as 'Version', 'Release', or 'Build' and allow them to appear with numbers or dates.\n"
                "- Description: Use paragraphs beginning with 'This project', 'This tool', or similar introductions, "
                "typically in the overview section near the start.\n\n"
                "Please generate a set of detailed parsing rules with flexibility to match varying structures."
            )
            
            messages = [
                {"role": "system", "content": "You are an advanced document parsing engine with adaptable matching capabilities for README analysis."},
                {"role": "user", "content": prompt}
            ]
            
            logger.info("Sending key_mapping.json to Groq AI to generate adaptive parsing rules.")
            response = self.client.chat.completions.create(
                model="llama-3.2-90b-text-preview",
                messages=messages
            )
            
            if response.choices:
                parsing_rules = response.choices[0].message.content
                logger.debug(f"Parsing rules generated successfully from Groq AI: {parsing_rules}")
                return parsing_rules
            else:
                logger.error("Failed to get parsing rules: No choices found in response.")
                raise ValueError("No choices found in response.")

        except Exception as e:
            logger.error(f"Error communicating with Groq AI: {e}")
            raise

    def parse_readme(self, file_content: str, parsing_rules: str) -> Dict[str, Any]:
        """Parse README.md content using Groq AI with instructions for flexible matching and JSON output."""
        try:
            prompt = (
                "Using the following parsing rules, analyze the README.md file content and extract data for each section, "
                "even if exact matches are not found. Use context and synonyms to identify the best matches.\n\n"
                f"{parsing_rules}\n\n"
                "README.md content:\n\n"
                f"{file_content}\n\n"
                "Please provide the parsing result in JSON format only, without any additional commentary or extra text."
            )
            
            messages = [
                {"role": "system", "content": "You are an advanced document parsing engine with flexible matching capabilities."},
                {"role": "user", "content": prompt}
            ]
            
            logger.info("Sending README.md content to Groq AI for flexible parsing")
            response = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=messages
            )
            
            if response.choices:
                parsed_data = response.choices[0].message.content
                logger.debug(f"Raw parsed data from Groq AI: {parsed_data}")

                # Extract JSON structure, correct common errors, and attempt to parse it
                json_match = re.search(r'({[\s\S]*?})', parsed_data)
                if json_match:
                    json_str = json_match.group(1)
                    try:
                        parsed_data_json = json.loads(json_str)
                        logger.debug("README.md content parsed successfully by Groq AI.")
                        return parsed_data_json
                    except json.JSONDecodeError:
                        # Attempt to correct and retry loading JSON if malformed
                        corrected_json_str = json_str.rstrip('}').rstrip(',') + '}'
                        try:
                            parsed_data_json = json.loads(corrected_json_str)
                            logger.debug("Corrected and parsed JSON successfully.")
                            return parsed_data_json
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to decode corrected JSON data: {e}")
                            logger.debug(f"Attempted corrected JSON string: {corrected_json_str}")
                            raise ValueError("Parsed data contains invalid JSON structure.")
                else:
                    logger.error("No valid JSON found in response. Full response for debugging:\n" + parsed_data)
                    raise ValueError("No valid JSON found in response.")
            
        except ValueError as ve:
            logger.error(f"ValueError during parsing: {ve}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error parsing README.md with Groq AI: {e}")
            raise
