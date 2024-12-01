from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from components.config import load_environment
from components.api_clients import APIClients
from components.data_fetcher import DataFetcher
from components.parser import Parser
from components.mapper import Mapper
from components.document_generator import DocumentGenerator
from utils.logger import setup_logger
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

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

# Pydanticモデル
class ListRepoFilesRequest(BaseModel):
    repo_name: str
    branch_name: str

class ListRepoFilesResponse(BaseModel):
    files: List[Dict[str, Any]]  # {'name': str, 'type': 'file' | 'directory', 'path': str}

class GenerateDesignDocumentRequest(BaseModel):
    repo_name: str
    branch_name: str
    selected_files: List[str]

class GenerateDesignDocumentResponse(BaseModel):
    final_documents: Dict[str, Any]  # {'file_path': design_document}

@app.post("/list-repo-files", response_model=ListRepoFilesResponse)
async def list_repo_files_endpoint(request: ListRepoFilesRequest):
    try:
        # 環境変数のロード
        env = load_environment()
        logger.info("Environment variables loaded successfully")
        
        # APIクライアントと一時保存管理の初期化
        api_clients = APIClients(
            groq_api_key=env['GROQ_API_KEY'],
            toolhouse_api_key=env['TOOLHOUSE_API_KEY'],
            lingu_key=env['LINGUSTRUCT_LICENSE_KEY'],
            user_id=env['USER_ID']
        )
        storage_manager = None  # TempStorageManager は現在使用していない
        
        # データ取得
        fetcher = DataFetcher(api_clients)
        file_tree = fetcher.fetch_file_tree(request.repo_name, request.branch_name)
        if not file_tree:
            logger.warning("File tree could not be fetched")
            raise HTTPException(status_code=404, detail="File tree could not be fetched")
        
        return {"files": file_tree}
    
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in list_repo_files_endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/generate-design-document", response_model=GenerateDesignDocumentResponse)
async def generate_design_document_endpoint(request: GenerateDesignDocumentRequest):
    try:
        # 環境変数のロード
        env = load_environment()
        logger.info("Environment variables loaded successfully")

        # コンポーネントの初期化
        api_clients = APIClients(
            groq_api_key=env['GROQ_API_KEY'],
            toolhouse_api_key=env['TOOLHOUSE_API_KEY'],
            lingu_key=env['LINGUSTRUCT_LICENSE_KEY'],
            user_id=env['USER_ID']
        )

        # データ取得
        fetcher = DataFetcher(api_clients)
        files_content = fetcher.fetch_files_content(request.repo_name, request.branch_name, request.selected_files)

        if not files_content:
            logger.warning("Selected files content could not be fetched")
            raise HTTPException(status_code=404, detail="Selected files content could not be fetched")

        # 依存関係の解析
        dependencies = fetcher.analyze_dependencies(files_content)

        # 解析
        parser = Parser()
        parsed_data = {}
        for file_path, content in files_content.items():
            file_type = file_path.split('.')[-1].lower()
            parsed = parser.parse_file(file_path, content, file_type)
            parsed_data[file_path] = parsed

        # プロジェクトメタデータの取得（README.mdを解析）
        readme_content = files_content.get("README.md", "")
        project_meta = fetcher.extract_meta_information(readme_content)

        # マッピング
        API_URL = "https://lingustruct.onrender.com/lingu_struct/key_mapping"  # APIエンドポイントURL
        LICENSE_KEY = env['LINGUSTRUCT_LICENSE_KEY']  # 環境変数から取得したライセンスキー

        mapper = Mapper(api_url=API_URL, license_key=LICENSE_KEY)  # 修正箇所
        mapped_data = mapper.map_data_to_modules(parsed_data, dependencies, project_meta)

        # ドキュメント生成
        generator = DocumentGenerator(env['LINGUSTRUCT_LICENSE_KEY'])
        final_document = generator.generate_final_document(mapped_data["modules"], project_id="lingurepo_project", version="1.0")  # 修正箇所

        if not final_document:
            logger.warning("Final document could not be generated")
            raise HTTPException(status_code=500, detail="Final document could not be generated")

        logger.info("Final document generated successfully.")
        return {"final_documents": final_document}
    
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in generate_design_document_endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
