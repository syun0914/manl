from config import BOT_IDS, SUPER_KEY
from fastapi import HTTPException, Request, Security

from fastapi.security.api_key import APIKeyCookie, APIKeyHeader, APIKeyQuery 

api_key_cookie = APIKeyCookie(name='key', auto_error=False)
api_key_header = APIKeyHeader(name='key', auto_error=False)
api_key_query = APIKeyQuery(name='key', auto_error=False)


async def api_key(
    api_key_query: str = Security(api_key_query),
    api_key_header: str = Security(api_key_header),
    api_key_cookie: str = Security(api_key_cookie),
) -> dict | HTTPException:
    if api_key_query == SUPER_KEY:
        return api_key_query
    elif api_key_header == SUPER_KEY:
        return api_key_header
    elif api_key_cookie == SUPER_KEY:
        return api_key_cookie
    else:
        raise HTTPException(401)


async def kakao_bot(request: Request) -> dict | HTTPException:
    try:
        req: dict = await request.json()
    except:
        req = dict()
    if req.get('bot') and req['bot']['id'] in BOT_IDS:
        return req
    else:
        raise HTTPException(401)