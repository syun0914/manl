from fastapi import Depends, FastAPI, Security
from dependencies import api_key
from routers import kakao

from fastapi.security.api_key import APIKey

app = FastAPI()


@app.get('/')
async def index():
    '''루트'''
    return {'alive': True}


@app.get('/test')
async def test(api_key: APIKey = Depends(api_key)):
    '''테스트'''
    return api_key

app.include_router(kakao.router)