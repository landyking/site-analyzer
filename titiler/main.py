import os
# titiler uses rasterio, which relies on GDAL. By default, GDAL performs a HEAD request before a GET request.
# Since our pre-signed URLs only allow GET requests, we set this environment variable to prevent GDAL from making HEAD requests.
os.environ["CPL_VSIL_CURL_USE_HEAD"] = "NO"

from fastapi import FastAPI
from titiler.core.factory import TilerFactory, ColorMapFactory

from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (for development - be more specific in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a TilerFactory for Cloud-Optimized GeoTIFFs
cog = TilerFactory()
colormap = ColorMapFactory()

# Register all the COG endpoints automatically
app.include_router(cog.router,prefix="/titiler", tags=["Cloud Optimized GeoTIFF"])
# logger.info("Registered COG TilerFactory with prefix /titiler")
app.include_router(colormap.router, prefix="/titiler", tags=["Color Map"])
# logger.info("Registered ColorMapFactory with prefix /titiler")


# Optional: Add a welcome message for the root endpoint
@app.get("/")
def read_index():
    return {"message": "Welcome to TiTiler"}