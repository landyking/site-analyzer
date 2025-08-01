from fastapi import FastAPI

from .utils import consts

app = FastAPI()


@app.get("/")
async def root():
    return {"message": consts.test_content}