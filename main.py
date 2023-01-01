import pyotp

from fastapi import FastAPI, Request
from routers.v1 import kakao as kakao_v1

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse ,ORJSONResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title='Manl', description='마늘 Core', version='1.0')
templates = Jinja2Templates('templates')


@app.get('/', response_class=ORJSONResponse)
async def index():
    '''루트'''
    return {'alive': True}


app.include_router(kakao_v1.router)