from config import DB_SETTING
from sqlite3 import connect, IntegrityError

con = connect('databases/kakao.db', **DB_SETTING)
cur = con.cursor()


async def permission(user_key: str, r: int = 1) -> bool:
    '''
    권한 판별하기
    -----
    user_key의 권한과 r(최소 권한)로 특정 기능의 사용 가능 여부를 판별합니다.
    
    단, user_key가 등록되어 있지 않다면 그의 권한은 0으로 판단합나다.
    '''
    cur.execute('SELECT level FROM users WHERE user_key=?;', (user_key,))
    f = cur.fetchone()
    if not f:
        return r <= 0
    return r <= f[0]
