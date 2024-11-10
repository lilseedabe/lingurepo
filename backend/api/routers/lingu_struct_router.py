from fastapi import APIRouter, HTTPException, Depends, Header, Response, Request
from pydantic import BaseModel, Field
from lingustruct.core import LinguStruct
from lingustruct.rate_limiter import RateLimiter
from lingustruct.converters import (
    lingu_struct_to_human_readable,
    human_readable_to_lingu_struct,
    lingu_struct_to_markdown,
    markdown_to_pdf
)
from lingustruct.templates import load_template, TemplateManager  # TemplateManagerをインポート
from lingustruct.license_manager import LicenseManager, validate_license_key  # 修正
import os
import json
import logging
from typing import Optional, Dict
import redis.asyncio as redis

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Redisクライアントの初期化
redis_url = os.getenv("REDIS_URL")
if not redis_url:
    raise EnvironmentError("REDIS_URL 環境変数が設定されていません。")
redis_client = redis.from_url(redis_url, decode_responses=True)

# LicenseManagerの初期化
license_manager = LicenseManager(redis_client)

# RateLimiterの初期化
rate_limiter = RateLimiter(free_calls=5, period=3600, redis_client=redis_client)

lingu_struct = LinguStruct()

# TemplateManagerの初期化
template_manager = TemplateManager()

# データモデル定義
class MasterInput(BaseModel):
    project_id: str
    version: str

class OverviewInput(BaseModel):
    meta_description: str
    arch_description: str
    dep_res_description: str
    err_handling_description: str
    prio_description: str
    abbr_description: str
    map_description: str
    p_order_description: str
    version_description: str
    tech_description: str

class ConversionRequest(BaseModel):
    module_id: int = Field(1, description="Module ID to convert")  # デフォルト値を1に設定
    source_format: str
    target_format: str
    data: Optional[dict] = None

class LicenseInput(BaseModel):
    api_key: str
    user_info: dict

class AutoMapInput(BaseModel):
    data: Dict

# 共通のAPIキー取得関数
async def get_api_key(api_key: Optional[str] = Header(None, alias="LINGUSTRUCT_LICENSE_KEY")) -> dict:
    """
    APIキーが提供されている場合は検証し、ユーザー情報を返す。
    提供されていない場合は、無料ユーザーとして扱う。
    """
    if api_key:
        try:
            user_info = await validate_license_key(api_key, license_manager)
            if user_info.get("plan") == "paid":
                logger.info(f"Paid user authenticated with API key: {api_key}")
                return {"plan": "paid"}
            else:
                logger.warning(f"API key {api_key} is not associated with a paid plan.")
                raise HTTPException(status_code=403, detail="This feature is available to paid users only.")
        except Exception as e:
            logger.error(f"API key validation failed: {str(e)}")
            raise HTTPException(status_code=401, detail=str(e))
    else:
        # APIキーが提供されていない場合、無料ユーザーとして扱う
        logger.info("No API key provided. Treating as free user.")
        return {"plan": "free"}

# 共通のレートリミット適用関数
async def enforce_rate_limit(user_info: dict, request: Request):
    await rate_limiter.enforce_limit(request, user_info)

@router.get("/redis/status")
async def redis_status():
    """Redisの接続テストと診断"""
    try:
        await redis_client.set("test_key", "test_value")
        value = await redis_client.get("test_key")
        info = await redis_client.info()
        return {"message": f"Redis connected: {value}", "info": info}
    except Exception as e:
        logger.error(f"Redis status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")

@router.get("/templates/{template_name}")
async def get_template(
    template_name: str, 
    request: Request,  # デフォルト値を持たない引数を先に配置
    user_info: dict = Depends(get_api_key)  # デフォルト値を持つ引数を後に配置
):
    """指定されたテンプレート名のJSONファイルを取得"""
    await enforce_rate_limit(user_info, request)
    try:
        template = load_template(template_name)
        logger.info(f"Template '{template_name}' fetched successfully.")
        return template
    except FileNotFoundError:
        logger.warning(f"Template '{template_name}' not found.")
        raise HTTPException(status_code=404, detail="Template not found.")
    except Exception as e:
        logger.error(f"Error loading template '{template_name}': {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate_master")
async def generate_master(
    master_input: MasterInput, 
    request: Request, 
    user_info: dict = Depends(get_api_key)
):
    await enforce_rate_limit(user_info, request)

    replacements = {"PROJECT_ID": master_input.project_id, "VERSION": master_input.version}
    try:
        lingu_struct.generate_master_json(replacements, output_path='master.json')
        logger.info("master.json generated successfully.")
        return {"message": "master.json generated successfully."}
    except Exception as e:
        logger.error(f"Error generating master.json: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate_overview")
async def generate_overview(
    overview_input: OverviewInput, 
    request: Request, 
    user_info: dict = Depends(get_api_key)
):
    await enforce_rate_limit(user_info, request)

    replacements = {key.upper(): value for key, value in overview_input.dict().items()}
    try:
        lingu_struct.generate_overview_json(replacements, output_path='overview.json')
        logger.info("overview.json generated successfully.")
        return {"message": "overview.json generated successfully."}
    except Exception as e:
        logger.error(f"Error generating overview.json: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/modules/{module_id}")
async def get_module(
    module_id: int, 
    request: Request, 
    user_info: dict = Depends(get_api_key)
):
    await enforce_rate_limit(user_info, request)

    try:
        project_dir = "/opt/render/project/src"
        data = lingu_struct.load_module(module_id, project_dir=project_dir)
        logger.info(f"Module {module_id} fetched successfully.")
        return {"module_id": module_id, "data": data}
    except FileNotFoundError:
        logger.warning(f"Module {module_id} not found.")
        raise HTTPException(status_code=404, detail="Module not found.")
    except Exception as e:
        logger.error(f"Error loading module {module_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/convert")
async def convert_module(
    conversion_request: ConversionRequest, 
    request: Request, 
    user_info: dict = Depends(get_api_key)
):
    await enforce_rate_limit(user_info, request)

    try:
        with open('mappings/key_mapping.json', 'r', encoding='utf-8') as f:
            key_mapping = json.load(f)
    except FileNotFoundError:
        logger.error("Key mapping file not found.")
        raise HTTPException(status_code=404, detail="Key mapping file not found.")
    except Exception as e:
        logger.error(f"Error loading key mapping: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    try:
        if conversion_request.source_format == 'lingu_struct' and conversion_request.target_format == 'human_readable':
            data = lingu_struct.load_module(conversion_request.module_id)
            human_readable = lingu_struct_to_human_readable(data, key_mapping)
            logger.info(f"Converted module {conversion_request.module_id} to human-readable format.")
            return {"human_readable": human_readable}

        elif conversion_request.source_format == 'human_readable' and conversion_request.target_format == 'markdown':
            data = conversion_request.data
            markdown = lingu_struct_to_markdown(data, key_mapping)
            logger.info("Converted human-readable format to markdown.")
            return {"markdown": markdown}

        elif conversion_request.source_format == 'markdown' and conversion_request.target_format == 'pdf':
            markdown_text = conversion_request.data.get("markdown", "")
            pdf_binary = markdown_to_pdf(markdown_text)
            headers = {'Content-Disposition': 'attachment; filename=output.pdf'}
            logger.info("Converted markdown to PDF.")
            return Response(content=pdf_binary, media_type="application/pdf", headers=headers)

        logger.warning("Unsupported format conversion requested.")
        raise HTTPException(status_code=400, detail="Unsupported format.")

    except FileNotFoundError:
        logger.error("Module not found during conversion.")
        raise HTTPException(status_code=404, detail="Module not found.")
    except Exception as e:
        logger.error(f"Error during conversion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/convert_to_pdf")
async def convert_to_pdf(
    module_id: int, 
    request: Request, 
    user_info: dict = Depends(get_api_key)
):
    await enforce_rate_limit(user_info, request)

    try:
        data = lingu_struct.load_module(module_id)
        markdown_text = lingu_struct_to_markdown(data, {})
        pdf_binary = markdown_to_pdf(markdown_text)
        headers = {'Content-Disposition': f'attachment; filename=module_{module_id}.pdf'}
        logger.info(f"Converted module {module_id} to PDF.")
        return Response(content=pdf_binary, media_type="application/pdf", headers=headers)
    except Exception as e:
        logger.error(f"Error converting module {module_id} to PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add_license_admin")
async def add_license_admin(
    license_input: LicenseInput, 
    admin_key: str = Header(...)
):
    if admin_key != os.getenv('ADMIN_SECRET'):
        logger.warning(f"Unauthorized license addition attempt with key: {admin_key}")
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        await license_manager.add_license(license_input.api_key, license_input.user_info)
        logger.info(f"License added successfully for API key: {license_input.api_key}")
        return {"message": "License added successfully."}
    except Exception as e:
        logger.error(f"Error adding license: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 自動マッピング機能のエンドポイントを追加
@router.post("/auto_map")
async def auto_map(
    auto_map_input: AutoMapInput,  # 入力モデルを使用
    request: Request,
    user_info: dict = Depends(get_api_key)
):
    """自動マッピング機能（有料ユーザー限定）"""
    await enforce_rate_limit(user_info, request)

    if user_info.get("plan") != "paid":
        raise HTTPException(status_code=403, detail="This feature is available to paid users only.")

    try:
        result = template_manager.auto_map_data(auto_map_input.data)
        logger.info("Auto mapping completed successfully.")
        return result
    except ValueError as e:
        logger.warning(f"Auto mapping failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during auto mapping: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))