import json
from typing import Dict, Any, List
from utils.logger import setup_logger

logger = setup_logger(__name__)

class Mapper:
    def __init__(self, key_mapping: Dict[str, Any]):
        self.key_mapping = key_mapping

        # 各セクション名とテンプレートIDのマッピング
        self.section_to_module = {
            "Template Version": 1,
            "Project Name": 2,
            "Project Version": 3,
            "Description": 4,
            "Scale": 5,
            "Style": 6,
            "Component Name": 7,
            "Component Type": 8,
            "Component Path": 9,
            "Component Dependencies": 10,
            # 必要に応じて他のマッピングを追加
        }

        # Groq AI からのパース結果とテンプレート内セクションの対応
        self.field_mapping = {
            "t_v": "Template Version",
            "p_n": "Project Name",
            "p_v": "Project Version",
            "desc": "Description",
            "scale": "Scale",
            "st": "Style",
            "c_n": "Component Name",
            "c_t": "Component Type",
            "c_p": "Component Path",
            "c_dep": "Component Dependencies",
            # 必要に応じて他のフィールドマッピングを追加
        }

    def map_data(self, parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            modules_data = []
            
            for section, data in parsed_data.items():
                # パース結果のキーをテンプレート内のセクション名に変換
                mapped_section = self.field_mapping.get(section)
                if not mapped_section:
                    logger.warning(f"No template mapping found for section '{section}'. Skipping.")
                    continue

                module_id = self.section_to_module.get(mapped_section)
                if not module_id:
                    logger.warning(f"No module ID found for mapped section '{mapped_section}'. Skipping.")
                    continue
                
                module_data = {
                    "id": module_id,
                    "name": mapped_section,
                    "purpose": f"Defines the {mapped_section.lower()}.",
                    "category": mapped_section.split()[0],
                    "priority": module_id,
                    "content": data  # Groqからのデータを格納
                }
                
                modules_data.append(module_data)
                logger.debug(f"Mapped data for section '{mapped_section}': {data}")
            
            logger.info("Data mapped to templates successfully.")
            return modules_data
        
        except Exception as e:
            logger.error(f"Error mapping data to templates: {e}")
            raise
