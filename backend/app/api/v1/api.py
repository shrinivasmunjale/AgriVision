from fastapi import APIRouter
from app.api.v1.endpoints import auth, predictions, admin, chat, misc

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(misc.router, prefix="/misc", tags=["misc"])
