from sqlalchemy import func, select

from sqlalchemy.orm import Session

from database.models import User, Admin, Notice

async def permission_user(
    db: Session, user_key: str, least_level: int = 1
) -> bool:
    '''권한 판별 (사용자)

    특정 기능의 사용 가능 여부를 판별합니다.
    * 사용자 키가 데이터베이스에 미등록 상태라면 그의 권한은 0으로 간주합나다.

    인자:
        db: 데이터베이스 세션
        user_key: 사용자 키
        least_level: 최소 권한
    '''
    user = db.execute(
        select(User.level).where(User.user_key == user_key)
    ).first()
    return getattr(user, 'level', 0) >= least_level


async def permission_admin(
    db: Session, user_key: str, least_level: int = 1
) -> bool:
    '''권한 판별 (관리자)

    특정 기능의 사용 가능 여부를 판별합니다.
    * 사용자 키가 데이터베이스에 미등록 상태라면 그의 권한은 0으로 간주합나다.

    인자:
        db: 데이터베이스 세션
        user_key: 사용자 키
        least_level: 최소 권한
    '''
    admin = db.execute(
        select(Admin.level).where(Admin.user_key == user_key)
    ).first()
    return getattr(admin, 'level', 0) >= least_level


def get_user_code(db: Session, user_key: str):
    '''사용자 코드 얻기
   
    * 사용자 키가 데이터베이스에 미등록 상태라면 사용자 코드는 -1로 간주합니다.

    인자:
        db: 데이터베이스 세션
        user_key: 사용자 키
    '''
    user = db.execute(
        select(User.user_code).where(User.user_key == user_key)
    ).first()
    return getattr(user, 'user_code', -1)