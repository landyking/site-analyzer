from fastapi import APIRouter

from app.api.routes import auth, user, admin
# from app.core.config import settings

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(user.router)
api_router.include_router(admin.router)
# api_router.include_router(users.router)
# api_router.include_router(utils.router)
# api_router.include_router(items.router)


# if settings.ENVIRONMENT == "local":
#     api_router.include_router(private.router)