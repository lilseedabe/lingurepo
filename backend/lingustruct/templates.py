import json
import os
import logging  # Import logging module
from typing import Dict, Set

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set log level as needed
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")


def load_template(template_name: str) -> dict:
    """
    Load the JSON file for the specified template name.
    
    Args:
        template_name (str): Name of the template to load (without extension).
    
    Returns:
        dict: Contents of the template.
    
    Raises:
        FileNotFoundError: If the template file does not exist.
        json.JSONDecodeError: If the JSON parsing fails.
    """
    file_path = os.path.join(TEMPLATE_DIR, f"{template_name}.json")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{template_name}.json not found.")
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def calculate_match_score(data_keys: Set[str], template_fields: Dict) -> int:
    """
    Calculate the number of matching keys between data and template fields.
    
    Args:
        data_keys (Set[str]): Set of data keys.
        template_fields (Dict): Template field information.
    
    Returns:
        int: Number of matches.
    """
    template_keys = set(template_fields.keys())
    score = len(data_keys & template_keys)
    logger.debug(f"Matching {data_keys} with {template_keys}: Score {score}")
    return score


def auto_detect_template(data: Dict) -> str:
    """
    Automatically select the best template based on the data keys.
    
    Args:
        data (Dict): Data to be mapped.
    
    Returns:
        str: Name of the selected template.
    
    Raises:
        ValueError: If no suitable template is found.
    """
    if not data:
        raise ValueError("Input data is empty. Please provide at least one field.")
    
    best_match = None
    highest_score = 0

    for template_file in os.listdir(TEMPLATE_DIR):
        if template_file.endswith(".json"):
            template_name = template_file.replace(".json", "")
            try:
                template = load_template(template_name)
                score = calculate_match_score(set(data.keys()), template.get("fields", {}))
                logger.debug(f"Template '{template_name}' score: {score}")
                if score > highest_score:
                    highest_score = score
                    best_match = template_name
            except Exception as e:
                logger.error(f"Error loading template '{template_name}': {str(e)}")

    if not best_match:
        raise ValueError("No suitable template found.")

    return best_match


class TemplateManager:
    def __init__(self, data_path='lingustruct/data/data.json'):
        self.data_path = data_path
        self.templates = self.load_templates()
        # Load templates for automatic mapping
        self.auto_mapping_templates = self.load_auto_mapping_templates()

    def load_templates(self):
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"{self.data_path} not found.")
        with open(self.data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('fields', [])

    def load_auto_mapping_templates(self) -> Dict[str, dict]:
        """
        Load all templates from the template directory.
        
        Returns:
            Dict[str, dict]: Dictionary with template names as keys and their contents.
        """
        templates = {}
        for template_file in os.listdir(TEMPLATE_DIR):
            if template_file.endswith(".json"):
                template_name = template_file.replace(".json", "")
                try:
                    templates[template_name] = load_template(template_name)
                    logger.debug(f"Loaded template: {template_name}")
                except Exception as e:
                    logger.error(f"Failed to load template {template_name}: {str(e)}")
        return templates

    def get_field(self, field_name: str):
        for field in self.templates:
            if field['name'] == field_name:
                return field
        return None

    def add_field(self, field: dict):
        self.templates.append(field)
        self.save_templates()

    def save_templates(self):
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump({"fields": self.templates}, f, ensure_ascii=False, indent=4)

    def auto_map_data(self, data: dict) -> dict:
        """
        Automatically map the data to the most suitable template.
        
        Args:
            data (dict): Data to be mapped.
        
        Returns:
            dict: Selected template name and mapped data.
        
        Raises:
            ValueError: If no suitable template is found.
        """
        template_name = auto_detect_template(data)
        template = self.auto_mapping_templates.get(template_name)

        if not template:
            raise ValueError(f"Template '{template_name}' is not loaded.")

        # Create a mapping of labels to keys from the template fields
        mapping = {field_info["label"]: key for key, field_info in template.get("fields", {}).items()}
        mapped_data = {mapping.get(k, k): v for k, v in data.items()}

        return {"template": template_name, "mapped_data": mapped_data}