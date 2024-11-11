from components.config import load_environment
from components.api_clients import APIClients
from components.data_fetcher import DataFetcher
from components.parser import Parser
from components.mapper import Mapper
from components.document_generator import DocumentGenerator
from utils.logger import setup_logger
import json

logger = setup_logger(__name__)

def generate_design_document():
    try:
        # 環境変数のロードと検証
        env = load_environment()
        logger.info("Environment variables loaded successfully")
        
        # APIクライアントの初期化
        api_clients = APIClients(
            groq_api_key=env['GROQ_API_KEY'],
            toolhouse_api_key=env['TOOLHOUSE_API_KEY'],
            lingu_key=env['LINGUSTRUCT_LICENSE_KEY'],
            user_id=env['USER_ID']
        )
        
        # データ取得
        fetcher = DataFetcher(api_clients)
        readme_content = fetcher.fetch_readme_content(env['REPO_NAME'], env['BRANCH_NAME'])
        if not readme_content:
            logger.warning("README.md content could not be fetched")
            return
        
        # 解析
        parser = Parser(api_clients, env['LINGUSTRUCT_LICENSE_KEY'])
        key_mapping = parser.load_key_mapping()
        parsing_rules = parser.get_parsing_rules(key_mapping)
        parsed_data = parser.parse_readme(readme_content, parsing_rules)

        # parsed_data の内容を確認
        logger.info("Parsed data output:")
        logger.info(json.dumps(parsed_data, indent=4, ensure_ascii=False))
        
        # マッピング
        mapper = Mapper(key_mapping)
        mapped_data = mapper.map_data(parsed_data)
        if not mapped_data:
            logger.warning("No data was mapped successfully")
            return
        
        # mapped_data の内容を確認
        logger.info("Mapped data output:")
        logger.info(json.dumps(mapped_data, indent=4, ensure_ascii=False))

        # ドキュメント生成
        generator = DocumentGenerator(env['LINGUSTRUCT_LICENSE_KEY'])
        final_document = generator.generate_final_document(mapped_data)
        if final_document:
            logger.info("Design document generation completed successfully")
            logger.info(f"Final Document:\n{json.dumps(final_document, indent=4, ensure_ascii=False)}")
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
