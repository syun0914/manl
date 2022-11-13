import pyotp

from fastapi import FastAPI, Request
from routers import kakao

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse ,ORJSONResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title='Manl', description='마늘 Core', version='1.0')
templates = Jinja2Templates('templates')


@app.get('/', response_class=ORJSONResponse)
async def index():
    '''루트'''
    return {'alive': True}


@app.get('/totp', response_class=HTMLResponse)
async def TOTP(request: Request, key: str):
    '''TOTP 키 보여주기

    생성된 TOTP 키를 1회에 한해 보여줍니다.
    '''
    return templates.TemplateResponse(
        'totp.html', {'request': request, 'key': key}
    )

app.include_router(kakao.router)
app.mount("/static", StaticFiles(directory='static'), name='static')