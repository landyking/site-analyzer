import os
# titiler uses rasterio, which relies on GDAL. By default, GDAL performs a HEAD request before a GET request.
# Since our pre-signed URLs only allow GET requests, we set this environment variable to prevent GDAL from making HEAD requests.
os.environ["CPL_VSIL_CURL_USE_HEAD"] = "NO"

from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, FastAPI, HTTPException, Query
from app.utils import consts
from titiler.core.factory import TilerFactory, ColorMapFactory
import logging
from app.api.deps import CurrentUser, SessionDep
from app import crud
from app.models import MapTaskFileDB
from app.core.security import gen_tile_signature

logger = logging.getLogger(__name__)


# Create a TilerFactory for Cloud-Optimized GeoTIFFs
cog = TilerFactory()
colormap = ColorMapFactory()

router = APIRouter(prefix="/titiler")

router.include_router(cog.router, tags=["Cloud Optimized GeoTIFF"])
logger.info("Registered COG TilerFactory with prefix /titiler")
router.include_router(colormap.router, tags=["Color Map"])
logger.info("Registered ColorMapFactory with prefix /titiler")

def DatasetPathParams2(url: Annotated[str, Query(description="dataset URL")]) -> str:
    """Create dataset path from args"""
    logger.error("###########DatasetPathParams2 called with url=%s", url)
    return url


def customize_application(app: FastAPI) -> None:
    logger.info("Customized Titiler application")
    # app.dependency_overrides[cog.path_dependency] = DatasetPathParams2
    