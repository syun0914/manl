from fastapi import FastAPI, Request
from routers import kakao
import pyotp

app = FastAPI()


@app.get('/')
async def index():
    '''루트'''
    return {'alive': True}


@app.get('/show_OTP')
async def show_OTP(request: Request):
    '''TOTP 키 보여주기

    생성된 TOTP 키를 1회에 한해 보여줍니다.
    '''
    ...

app.include_router(kakao.router)