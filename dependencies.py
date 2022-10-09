from config import BOT_IDS, SUPER_KEY
from fastapi import HTTPException, Request, Security

from fastapi.security.api_key import APIKeyCookie, APIKeyHeader, APIKeyQuery

api_key_cookie = APIKeyCookie(name='key', auto_error=False)
api_key_header = APIKeyHeader(name='key', auto_error=False)
api_key_query = APIKeyQuery(name='key', auto_error=False)


async def get_api_key(
    api_key_query: str = Security(api_key_query),
    api_key_header: str = Security(api_key_header),
    api_key_cookie: str = Security(api_key_cookie),
) -> str:
    '''
    API KEY 검증하기
    -----
    * API KEY를 받아 검증하여 SUPER_KEY와 일치하지 않는 경우, 401 Unauthrized를 반환합니다.
    * API KEY를 받아 검증하여 SUPER_KEY와 일치하는 경우, API KEY를 반환합니다.
    
    '''
    if SUPER_KEY in {api_key_query, api_key_header, api_key_cookie}:
        return api_key_query
    else:
        raise HTTPException(401)


async def kakao_bot(request: Request) -> dict:
    '''
    신뢰할 수 있는 카카오 봇 검증하기
    -----
    * 봇 ID를 검증하여 BOT_IDS에 등록되지 않은 경우, 401 Unauthrized를 반환합니다.
    * 봇 ID를 검증하여 BOT_IDS에 등록된 경우, 리퀘스트(딕셔너리)를 반환합니다.
    '''
    try:
        req: dict = await request.json()
    except:
        req = dict()
    if req.get('bot') and req['bot']['id'] in BOT_IDS:
        return req
    else:
        raise HTTPException(401)