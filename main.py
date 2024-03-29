from fastapi import FastAPI

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, ORJSONResponse
from fastapi.templating import Jinja2Templates
from routers.v1 import kakao as kakao_v1

app = FastAPI(title="Manl", description="마늘 Core", version="1.0")
templates = Jinja2Templates("templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=ORJSONResponse)
async def index():
    """루트"""
    return {"alive": True}


@app.get("/favicon.ico")
async def favicon():
    return FileResponse(
        path="./static/favicon.ico",
        headers={"Content-Disposition": "attachment; filename=favicon.ico"},
    )


app.include_router(kakao_v1.router)
