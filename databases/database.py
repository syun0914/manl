from config import DB_SETTING
from pymysql import connect

con = connect(**DB_SETTING)
cur = con.cursor()


async def permission(user_key: str, r: int = 1) -> bool:
    '''권한 판별하기

    {user_key}의 권한과 {r}로 특정 기능의 사용 가능 여부를 판별합니다.
    단, user_key가 DB에 등록되어 있지 않다면 그의 권한은 0으로 판단합나다.

    인자:
        user_key: 사용자 키
        r: 최소 권한
    '''
    cur.execute('SELECT level FROM users WHERE user_key=%s;', (user_key,))
    f = cur.fetchone()
    if not f:
        return r <= 0
    return r <= f[0]


async def permission_admin(user_key: str, r: int = 1) -> bool:
    '''관리자 권한 판별하기

    {user_key}의 권한과 {r}로 특정 기능의 사용 가능 여부를 판별합니다.
    단, user_key가 관리자 DB에 등록되어 있지 않다면 그의 권한은 0으로 판단합나다.

    인자:
        user_key: 사용자 키
        r: 최소 권한
    '''
    cur.execute('SELECT level FROM admins WHERE user_key=%s;', (user_key,))
    f = cur.fetchone()
    if not f:
        return r <= 0
    return r <= f[0]
