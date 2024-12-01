import requests
import json
from typing import List, Dict, Any
from utils.logger import setup_logger

logger = setup_logger(__name__)

class DocumentGenerator:
    def __init__(self, lingu_key: str):
        self.lingu_key = lingu_key

    def fetch_template(self, module_id: int) -> Dict[str, Any]:
        """Fetch the structure of individual template files like m1.json, m2.json from API."""
        url = f"https://lingustruct.onrender.com/lingu_struct/modules/{module_id}"
        headers = {
            "LINGUSTRUCT_LICENSE_KEY": self.lingu_key
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            template_data = response.json()["data"]
            logger.info(f"Template for module {module_id} loaded successfully from API.")
            return template_data
        except requests.HTTPError as http_err:
            if response.status_code == 404:
                logger.warning(f"Template for module {module_id} not found: {http_err}")
            else:
                logger.error(f"HTTP error occurred when fetching module {module_id}: {http_err}")
            return None
        except Exception as e:
            logger.error(f"Failed to load template for module {module_id}: {e}")
            return None

    def generate_final_document(self, mapped_data: List[Dict[str, Any]], project_id: str, version: str) -> Dict[str, Any]:
        """
        Generate the final design document.
        """
        try:
            modules_with_fields = []
            for module in mapped_data:
                if not isinstance(module, dict):
                    logger.error(f"Module is not a dictionary: {module}")
                    continue

                module_id = module["id"]
                template_data = self.fetch_template(module_id)
                if not template_data:
                    logger.warning(f"Skipping module {module_id} due to missing template.")
                    continue

                module["fields"] = template_data.get("fields", {})
                modules_with_fields.append(module)
                logger.debug(f"Module {module_id} fields populated.")

            # Add relationships
            relationships = self.generate_relationships(modules_with_fields)

            # Add Adaptive Patterns and Quality Assurance
            adaptive_patterns = self.generate_adaptive_patterns(modules_with_fields)
            quality_assurance = self.generate_quality_assurance()

            # Generate CI/CD pipeline
            ci_cd_pipeline = self.generate_ci_cd_pipeline({
                "project_name": project_id,
                "version": version
            })

            # Generate test cases
            test_cases = self.generate_test_cases(modules_with_fields)

            # Construct the final document
            final_document = {
                "meta": {
                    "document_type": "system_design_document",
                    "description": "This document defines the modular structure, dependencies, and adaptive components of the system.",
                    "template_version": "1.0"
                },
                "project_id": project_id,
                "version": version,
                "modules": modules_with_fields,
                "relationships": relationships,
                "adaptive_patterns": adaptive_patterns,
                "quality_assurance": quality_assurance,
                "ci_cd_pipeline": ci_cd_pipeline,
                "test_cases": test_cases
            }

            logger.info("Final document generated successfully.")
            return final_document

        except Exception as e:
            logger.error(f"Failed to generate final document: {e}", exc_info=True)
            raise

    def generate_relationships(self, modules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Define relationships between modules.
        """
        relationships = [
            {
                "source": 1,
                "target": 2,
                "type": "sequential",
                "description": "Meta information must be processed before defining the architecture."
            },
            {
                "source": 2,
                "target": 3,
                "type": "dependency",
                "description": "The architecture module depends on dependency resolution strategies."
            },
            {
                "source": 4,
                "target": 8,
                "type": "feedback",
                "description": "Error handling strategies affect property order processing."
            },
            {
                "source": 5,
                "target": 10,
                "type": "influences",
                "description": "Priority management influences the technology stack selection."
            }
        ]
        logger.debug("Relationships defined.")
        return relationships

    def generate_adaptive_patterns(self, modules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Define Adaptive Patterns.
        """
        adaptive_patterns = {
            "high_security": {
                "modules": [2, 4, 6],
                "adaptation": {
                    "multi_factor_authentication": True,
                    "enhanced_error_logging": True
                }
            },
            "high_load": {
                "modules": [3, 5, 10],
                "adaptation": {
                    "caching": True,
                    "load_balancing": True
                }
            }
        }
        logger.debug("Adaptive patterns defined.")
        return adaptive_patterns

    def generate_quality_assurance(self) -> Dict[str, Any]:
        """
        Define Quality Assurance.
        """
        quality_assurance = {
            "coverage": {
                "dimensions": ["functionality", "security", "performance"],
                "depth": "comprehensive"
            },
            "coherence_check": {
                "pattern_matching": "consistent",
                "conflict_resolution": "automated"
            }
        }
        logger.debug("Quality assurance defined.")
        return quality_assurance

    def generate_ci_cd_pipeline(self, project_meta: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate CI/CD pipeline configuration.
        """
        pipeline = {
            "stages": ["build", "test", "deploy"],
            "jobs": {
                "build": {
                    "script": ["npm install", "npm run build"]
                },
                "test": {
                    "script": ["pytest tests/"]
                },
                "deploy": {
                    "script": ["docker build -t project:latest .", "docker push registry/project:latest"]
                }
            }
        }
        logger.debug("CI/CD pipeline generated.")
        return pipeline

    def generate_test_cases(self, modules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate test cases for each module.
        """
        test_cases = []
        for module in modules:
            test_cases.append({
                "moduleName": module["name"],
                "description": f"Test cases for {module['name']} functionality."
            })
        logger.debug("Test cases generated.")
        return test_cases
