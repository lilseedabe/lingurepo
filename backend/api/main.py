from fastapi import FastAPI
from api.routers import lingu_struct_router

app = FastAPI(
    title="LinguStruct API",
    description="API for interacting with the LinguStruct system design framework.",
    version="0.2.0"
)

app.include_router(lingu_struct_router.router, prefix="/lingu_struct", tags=["LinguStruct"])
