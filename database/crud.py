from sqlalchemy import select

from database.models import User, Admin
from sqlalchemy.ext.asyncio import AsyncSession


async def permission_user(
    db: AsyncSession, user_key: str, least_level: int = 1
) -> bool:
    '''권한 판별 (사용자)

    특정 기능의 사용 가능 여부를 판별합니다.
    * 사용자 키가 미등록 상태라면 그의 권한은 0으로 간주합나다.

    인자:
        db: 데이터베이스 세션
        user_key: 사용자 키
        least_level: 최소 권한
    '''
    return getattr((await db.execute(
        select(User.level).where(User.user_key == user_key)
    )).first(), 'level', 0) >= least_level


async def permission_admin(
    db: AsyncSession, user_key: str, least_level: int = 1
) -> bool:
    '''권한 판별 (관리자)

    특정 기능의 사용 가능 여부를 판별합니다.
    * 사용자 키가 미등록 상태라면 그의 권한은 0으로 간주합나다.

    인자:
        db: 데이터베이스 세션
        user_key: 사용자 키
        least_level: 최소 권한
    '''
    return getattr((await db.execute(
        select(Admin.level).where(Admin.user_key == user_key)
    )).first(), 'level', 0) >= least_level


async def get_user_code(db: AsyncSession, user_key: str) -> int:
    '''사용자 코드 얻기
   
    사용자의 사용자 코드를 반환합니다.
    * 사용자 키가 미등록 상태라면 사용자 코드는 -1로 간주합니다.

    인자:
        db: 데이터베이스 세션
        user_key: 사용자 키
    '''
    return getattr((await db.execute(
        select(User.user_code).where(User.user_key == user_key)
    )).first(), 'user_code', -1)