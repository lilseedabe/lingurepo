from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from components.config import load_environment
from components.api_clients import APIClients
from components.data_fetcher import DataFetcher
from components.parser import Parser
from components.mapper import Mapper
from components.document_generator import DocumentGenerator
from utils.logger import setup_logger
import json
from fastapi.middleware.cors import CORSMiddleware

logger = setup_logger(__name__)
app = FastAPI()

# CORS設定
origins = [
    "http://localhost:3000",  # フロントエンドのURL
    # 必要に応じて他のオリジンを追加
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DesignDocumentRequest(BaseModel):
    repo_name: str
    branch_name: str

@app.post("/generate-design-document")
async def generate_design_document_endpoint(request: DesignDocumentRequest):
    try:
        # 環境変数のロードと検証（APIキーなどは.envから取得）
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
        readme_content = fetcher.fetch_readme_content(request.repo_name, request.branch_name)
        if not readme_content:
            logger.warning("README.md content could not be fetched")
            raise HTTPException(status_code=404, detail="README.md content could not be fetched")
        
        # 解析
        parser = Parser(api_clients, env['LINGUSTRUCT_LICENSE_KEY'])
        key_mapping = parser.load_key_mapping()
        parsing_rules = parser.get_parsing_rules(key_mapping)
        parsed_data = parser.parse_readme(readme_content, parsing_rules)

        # マッピング
        mapper = Mapper(key_mapping)
        mapped_data = mapper.map_data(parsed_data)
        if not mapped_data:
            logger.warning("No data was mapped successfully")
            raise HTTPException(status_code=400, detail="No data was mapped successfully")
        
        # ドキュメント生成
        generator = DocumentGenerator(env['LINGUSTRUCT_LICENSE_KEY'])
        final_document = generator.generate_final_document(mapped_data)
        if not final_document:
            logger.warning("Final document could not be generated")
            raise HTTPException(status_code=500, detail="Final document could not be generated")
        
        return {"final_document": final_document}
    
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in generate_design_document_endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
