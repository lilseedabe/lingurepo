import json
import re
from typing import Dict, Any, List
from utils.logger import setup_logger

logger = setup_logger(__name__)

class Parser:
    def __init__(self):
        pass

    def parse_file(self, file_path: str, file_content: str, file_type: str) -> Dict[str, Any]:
        logger.info(f"Parsing file: {file_path} of type: {file_type}")

        if file_type == "json":
            return self.parse_json(file_content)
        elif file_type == "python":
            return self.parse_python_code(file_content)
        elif file_type == "typescript":
            return self.parse_typescript_code(file_content)
        elif file_type == "rust":
            return self.parse_rust_code(file_content)
        elif file_type == "go":
            return self.parse_go_code(file_content)
        elif file_type == "javascript":
            return self.parse_javascript_code(file_content)
        elif file_type == "markdown":
            return self.parse_markdown(file_content)
        else:
            logger.warning(f"Unsupported file type: {file_type}")
            return {"error": "Unsupported file type"}

    def parse_json(self, file_content: str) -> Dict[str, Any]:
        try:
            data = json.loads(file_content)
            logger.debug("Parsed JSON successfully.")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON: {e}")
            raise ValueError("Invalid JSON format")

    def parse_python_code(self, file_content: str) -> Dict[str, Any]:
        try:
            functions = re.findall(r'def (\w+)\(', file_content)
            classes = re.findall(r'class (\w+)\(', file_content)
            imports = re.findall(r'from (\S+) import', file_content) + re.findall(r'import (\S+)', file_content)
            logger.debug(f"Parsed Python code: {len(functions)} functions, {len(classes)} classes, {len(imports)} imports.")
            return {
                "functions": functions,
                "classes": classes,
                "dependencies": imports
            }
        except Exception as e:
            logger.error(f"Error parsing Python code: {e}")
            raise ValueError("Error parsing Python code")

    def parse_typescript_code(self, file_content: str) -> Dict[str, Any]:
        try:
            interfaces = re.findall(r'interface (\w+)', file_content)
            functions = re.findall(r'function (\w+)\(', file_content)
            classes = re.findall(r'class (\w+)\(', file_content)
            logger.debug(f"Parsed TypeScript code: {len(interfaces)} interfaces, {len(functions)} functions, {len(classes)} classes.")
            return {
                "interfaces": interfaces,
                "functions": functions,
                "classes": classes
            }
        except Exception as e:
            logger.error(f"Error parsing TypeScript code: {e}")
            raise ValueError("Error parsing TypeScript code")

    def parse_rust_code(self, file_content: str) -> Dict[str, Any]:
        try:
            functions = re.findall(r'fn (\w+)\(', file_content)
            structs = re.findall(r'struct (\w+)', file_content)
            enums = re.findall(r'enum (\w+)', file_content)
            imports = re.findall(r'use (\S+);', file_content)
            logger.debug(f"Parsed Rust code: {len(functions)} functions, {len(structs)} structs, {len(enums)} enums, {len(imports)} imports.")
            return {
                "functions": functions,
                "structs": structs,
                "enums": enums,
                "dependencies": imports
            }
        except Exception as e:
            logger.error(f"Error parsing Rust code: {e}")
            raise ValueError("Error parsing Rust code")

    def parse_go_code(self, file_content: str) -> Dict[str, Any]:
        try:
            functions = re.findall(r'func (\w+)\(', file_content)
            structs = re.findall(r'type (\w+) struct', file_content)
            imports = re.findall(r'import\s+"([^"]+)"', file_content)
            logger.debug(f"Parsed Go code: {len(functions)} functions, {len(structs)} structs, {len(imports)} imports.")
            return {
                "functions": functions,
                "structs": structs,
                "dependencies": imports
            }
        except Exception as e:
            logger.error(f"Error parsing Go code: {e}")
            raise ValueError("Error parsing Go code")

    def parse_javascript_code(self, file_content: str) -> Dict[str, Any]:
        try:
            functions = re.findall(r'function (\w+)\(', file_content)
            classes = re.findall(r'class (\w+)\s+{', file_content)
            imports = re.findall(r'import .* from [\'"]([^\'"]+)[\'"]', file_content)
            logger.debug(f"Parsed JavaScript code: {len(functions)} functions, {len(classes)} classes, {len(imports)} imports.")
            return {
                "functions": functions,
                "classes": classes,
                "dependencies": imports
            }
        except Exception as e:
            logger.error(f"Error parsing JavaScript code: {e}")
            raise ValueError("Error parsing JavaScript code")

    def parse_markdown(self, file_content: str) -> Dict[str, Any]:
        try:
            headers = re.findall(r'^(#+)\s+(.*)', file_content, re.MULTILINE)
            logger.debug(f"Parsed Markdown: {len(headers)} headers.")
            return {"headers": headers}
        except Exception as e:
            logger.error(f"Error parsing Markdown: {e}")
            raise ValueError("Error parsing Markdown")
