import kakao_template as tem
import orjson as j
import yaml as y

from dependencies import get_api_key, kakao_bot
from fastapi import APIRouter, Depends
from hashlib import new as hasher
from kakao_template import *
from random import sample
from sqlalchemy import and_, delete, func, insert, select, update
from time import time
from urllib.parse import quote
from util import *

from database.crud import (
    get_user_code,
    permission_user as perm_user, permission_admin as perm_admin,
)
from database.models import Notice, NumberBaseball, User
from database.session import get_db
from fastapi.responses import ORJSONResponse
from fastapi.security.api_key import APIKey
from kakao_template.tem import gtem
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix='/api/v1')


@router.post('/skill', response_class=ORJSONResponse)
async def skill(
    k_req: dict = Depends(kakao_bot),
    api_key: APIKey = Depends(get_api_key),
    db: AsyncSession = Depends(get_db)
):
    '''일반 백엔드 API

    마늘 Xllent의 백엔드 API입니다.

    인자:
        k_req: 카카오에서 받은 페이로드
        api_key: API 키
        db: 데이터베이스 세션
    '''
    user_req = k_req['userRequest']
    bot = k_req['bot']
    params = k_req['action']['params']
    block = user_req['block']
    user_key = user_req['user']['properties'].get('plusfriendUserKey')
    bn, bi = block['name'], block['id']
    WEAK = '사용이 허가되지 않았어요.\n관리자에게 문의해주세요.'
    RETRY = tem.QReply('🌀 다시하기', 'block', '🌀 다시하기', bi)
    REFRESH = tem.QReply('🌀 새로고침', 'block', '🌀 새로고침', bi)

    if bn == '급식' or bn == '생일 급식':
        thumbnail = tem.Thumbnail(
            'https://rawcdn.githack.com/syun0914/manl_thumbnail/e05fea172fd6864ae0797e5e9e078cb04c6a543f/spring_2023/meal.png',  # noqa
            tem.Link('http://112.186.226.178:4082/st'), True, 2560, 2560
        )
        if not await perm_user(db, user_key):
            return gtem(
                tem.basicCard(thumbnail, '사용 불가', WEAK), q_replies=[RETRY]
            )
        mt = params['meal_time']
        if mt == '통합':
            d = await meal_unit(j.loads(params['date'])['date'])
        else:
            d = await meal(j.loads(params['date'])['date'], mt)
        return gtem(
            tem.basicCard(
                thumbnail, d['title'], d['meal'],
                forwardable=await perm_user(db, user_key, 2)
            ), q_replies=[RETRY]
        )

    elif bn == '시간표':
        thumbnail = tem.Thumbnail(
            'https://rawcdn.githack.com/syun0914/manl_thumbnail/e05fea172fd6864ae0797e5e9e078cb04c6a543f/spring_2023/timetable.png',  # noqa
            tem.Link('http://112.186.226.178:4082/st'), True, 2560, 2560
        )
        if not await perm_user(db, user_key):
            return gtem(tem.basicCard(thumbnail, '사용 불가', WEAK))
        d = await timetable('1-4', params['day'], '서일고등학교')
        return gtem(
            tem.basicCard(
                thumbnail,
                d['title'], d['timetable'],
                forwardable=True
            ), q_replies=[RETRY]
        )

    elif bn == '사용자 키':
        return gtem(tem.simpleText(user_key))
    
    elif bn == '공지 사항':
        notice = (await db.execute(
            select(func.max(Notice.notice_code),
                   Notice.datetime, Notice.title, Notice.content)
        )).first()
        return gtem(tem.simpleText(
            f'''📢 공지 사항
__________

[{notice.title}]

{notice.datetime.strftime("%Y. %m. %d. %H:%M:%S")}

{notice.content}''',
            [tem.Button('상담직원 연결', 'operator')]
        ), q_replies=[REFRESH])

    elif bn == '학교 공지 사항 목록':
        title = '📢 서일고등학교 공지 사항'
        if not await perm_user(db, user_key):
            return gtem(
                tem.simpleText(f'{title}\n\n{WEAK}'), q_replies=[RETRY]
            )
        b = [tem.LCI(*t[:2], tem.Link(t[2]))
             for t in await school_board(
                 'http://seoilgo.cnehs.kr', '60587', '0401', 'seoilgo'
             )
        ]
        return tem.carousel(
            templates=[tem.listCard(title, b[i*5:i*5+5]) for i in range(5)],
            k_type='listCard', q_replies=[REFRESH]
        )

    elif bn == 'QR코드 생성':
        if not await perm_user(db, user_key):
            return gtem(
                tem.simpleText(f'🏁 QR코드 생성\n\n{WEAK}'), q_replies=[RETRY]
            )
        return gtem(tem.simpleImage(
            f'https://chart.apis.google.com/chart?cht=qr&chs=547x547&chl={quote(params["qr_msg"])}',  # noqa
            'QR코드를 생성하는데 문제가 발생했어요.',
        ), q_replies=[RETRY])
    
    else:
        return tem.data(d='B#다4%^바*-N0+2T|타6!@8')


@router.post('/admin', response_class=ORJSONResponse)
async def admin(
    k_req: dict = Depends(kakao_bot),
    api_key: APIKey = Depends(get_api_key),
    db: AsyncSession = Depends(get_db)
):
    '''관리자 백엔드 API

    Xllent Space의 백엔드 API입니다.
    
    인자:
        k_req: 카카오에서 받은 페이로드
        api_key: API 키
        db: 데이터베이스 세션
    '''
    user_req = k_req['userRequest']
    bot = k_req['bot']
    params = k_req['action']['params']
    block = user_req['block']
    user_key = user_req['user']['properties'].get('plusfriendUserKey')
    bn, bi = block['name'], block['id']
    WEAK = f'권한이 부족해 「{bn}」에 실패했어요.'
    RETRY = tem.QReply('🌀 다시하기', 'block', '🌀 다시하기', bi)
    REFRESH = tem.QReply('🌀 새로고침', 'block', '🌀 새로고침', bi)

    if bn == 'Eval':
        if not await perm_admin(db, user_key, 2):
            return gtem(tem.simpleText(WEAK))
        try:
            res = eval(params['eval'])
        except BaseException as e:
            res = e
        return gtem(tem.simpleText(str(res)[:4010]))

    elif bn == '해시화':
        if not await perm_admin(db, user_key, 1):
            return gtem(tem.simpleText(WEAK))
        h = hasher(params['algorithm'])
        h.update(params['text'].encode())
        return gtem(tem.simpleText(h.hexdigest()))

    elif bn == '사용자 키':
        return gtem(tem.simpleText(user_key))

    elif bn == '공지 사항 작성':
        if not await perm_admin(db, user_key, 1):
            return gtem(tem.simpleText(WEAK))
        try:
            db.execute(
                insert(Notice).values(
                    datetime=func.now(),
                    title=params['title'],
                    content=params['params']
                )
            )
            res1 = '성공'
            res2 = (
                "\n공지 사항 코드는 '"
                + db.execute(select(func.max(Notice.notice_code)).first())
                + "'입니다."
            )
            db.commit()
        except BaseException:
            res1 = '오류가 발생해 실패'
        return gtem(
            tem.simpleText(f'📢 공지 사항 작성에 {res1}했어요.'),
            tem.simpleText(
                "\n공지 사항 코드는 '"
                + db.execute(select(func.max(Notice.notice_code)).first())
                + "'입니다."
            ),
            q_replies=[RETRY]
        )

    elif bn == '공지 사항 삭제':
        if not await perm_admin(db, user_key, 1):
            return gtem(tem.simpleText(WEAK))
        try:
            await db.execute(
                delete(Notice)
                .where(Notice.notice_code == params['notice_code'])
            )
            res = '성공'
            await db.commit()
        except BaseException:
            res = '오류가 발생해 실패'
        return gtem(
            tem.simpleText(f'📢 공지 사항 삭제에 {res}했어요.'),
            q_replies=[RETRY]
        )

    elif bn == '사용자 등록':
        TITLE = '✅ 사용자 등록'
        if not await perm_admin(db, user_key, 1):
            return gtem(tem.simpleText(f'{TITLE}\n\n{WEAK}'))
        try:
            query: dict = y.load(
                stream=params['query'].replace(', ', '\n').replace(',', '\n'),
                Loader=y.FullLoader
            )
        except y.parser.ParserError:
            return gtem(
                tem.simpleText(
                    f'{TITLE}\n\nYAML-Comma 형식으로 보냈는지 확인해주세요.'
                ), q_replies=[RETRY]
            )
        try:
            await db.execute(
                insert(User)
                .values(user_key=query['key'],
                        name=query['name'],
                        student_id=query['sid'],
                        level=query['lvl'],
                        phone=query['phone'],
                        score=0)
            )
            res = '성공'
            await db.commit()
        except:
            res = '실패'
        return gtem(
            tem.simpleText(f'{TITLE}\n\n사용자 추가에 {res}했어요.'),
            q_replies=[RETRY]
        )

    elif bn == '사용자 조회':
        TITLE = '👨🏻‍💼 사용자 조회'
        if not await perm_admin(db, user_key, 1):
            return gtem(tem.simpleText(f'{TITLE}\n\n{WEAK}'))
        try:
            query: dict = y.load(
                stream=params['query'].replace(', ', '\n').replace(',', '\n'),
                Loader=y.FullLoader
            )
            q = {
                'user_key': query.get('key', '%%'),
                'name': query.get('name', '%%'),
                'student_id': query.get('sid', '%%'),
                'phone': query.get('phone', '%%'),
                'user_code': int(query.get('code', 0)) or '%%'
            }
        except y.parser.ParserError:
            return gtem(
                tem.simpleText(
                    f'{TITLE}\n\nYAML-Comma 형식으로 보냈는지 확인해주세요.'
                ), q_replies=[RETRY]
            )
        try:
            u = (await db.execute(
                select(User).
                where(and_(*[getattr(User, k).like(v) for k, v in q.items()]))
            )).first()[0]
            list_items = [
                tem.LCI('사용자 키 / 사용자 번호', f'{u.user_key} / {u.user_code}'),
                tem.LCI('이름 / 학번', f'{u.name} / {u.student_id}'),
                tem.LCI('권한 상태', str(u.level)),
                tem.LCI('전화번호', u.phone),
                tem.LCI('게임 점수', str(u.score))
            ]
            return gtem(
                tem.listCard(
                    '👨🏻‍💼 사용자 정보', list_items,
                    [
                        RETRY,
                        tem.QReply(
                            '제거', 'block',
                            '사용자 제거', '63b115fa2a784f093357cef2'
                        ),
                        tem.QReply(
                            '수정', 'block',
                            '사용자 정보 수정', '63b12e292a784f093357cf9b'
                        )
                    ],
                ),
                contexts=[
                    tem.Context('user_selected', 1, {'query': params['query']})
                ]
            )
        except:
            return gtem(
                tem.simpleText(f'{TITLE}\n\n사용자 조회에 실패했어요.'),
                q_replies=[RETRY]
            )

    if bn == '사용자 제거':
        TITLE = '🗑️ 사용자 제거'
        if not await perm_admin(db, user_key, 1):
            return gtem(tem.simpleText(f'{TITLE}\n\n{WEAK}'))
        try:
            query: dict = y.load(
                stream=params['query'].replace(', ', '\n').replace(',', '\n'),
                Loader=y.FullLoader
            )
            q = {
                'user_key': query.get('key', '%%'),
                'name': query.get('name', '%%'),
                'student_id': query.get('sid', '%%'),
                'phone': query.get('phone', '%%'),
                'user_code': query.get('code', '%%')
            }
        except y.parser.ParserError:
            return gtem(
                tem.simpleText(
                    f'{TITLE}\n\nYAML-Comma 형식으로 보냈는지 확인해주세요.'
                ), q_replies=[RETRY]
            )
        try:
            await db.execute(
                delete(User).
                where(and_(*[getattr(User, k).like(v) for k, v in q.items()]))
            )
            res = '성공'
            await db.commit()
        except:
            res = '실패'
        return gtem(
            tem.simpleText(f'{TITLE}\n\n사용자 제거에 {res}했어요.'),
            q_replies=[
                RETRY,
                tem.QReply(
                    '조회', 'block', '사용자 조회', '63b115302a784f093357cee8'
                )
            ]
        )

    elif bn == '사용자 정보 수정':
        TITLE = '🔃 사용자 정보 수정'
        if not await perm_admin(db, user_key, 1):
            return gtem(tem.simpleText(f'{TITLE}\n\n{WEAK}'))
        try:
            query: dict = y.load(
                stream=params['query'].replace(', ', '\n').replace(',', '\n'),
                Loader=y.FullLoader
            )
            q = {
                'user_key': query.get('key', '%%'),
                'name': query.get('name', '%%'),
                'student_id': query.get('sid', '%%'),
                'phone': query.get('phone', '%%'),
                'user_code': query.pop('code', '%%')
            }
            new_query: dict = y.load(
                stream=(
                    params['new_query'].
                    replace(', ', '\n').replace(',', '\n')
                ),
                Loader=y.FullLoader
            )
            nq = tem.del_empty({
                'user_key': new_query.get('key', '%%'),
                'name': new_query.get('name', '%%'),
                'student_id': new_query.get('sid', '%%'),
                'phone': new_query.get('phone', '%%'),
                'score': new_query.get('code', '%%')
            })
        except TypeError:
            return gtem(
                tem.simpleText(
                    f'{TITLE}\n\nlvl을 자연수로 보냈는지 확인해주세요.',
                ), q_replies=[RETRY]
            )
        except BaseException:
            return gtem(
                tem.simpleText(
                    f'{TITLE}\n\nYAML-Comma 형식으로 보냈는지 확인해주세요.'
                ), q_replies=[RETRY]
            )
        try:
            await db.execute(
                update(User).
                where(and_(*[getattr(User, k).like(v) for k, v in q.items()])).
                values(**nq).
                execution_options(synchronize_session="fetch")
            )
            res = '성공'
            await db.commit()
        except:
            res = '실패'
        return gtem(
            tem.simpleText(f'{TITLE}\n\n사용자 정보 수정에 {res}했어요.'),
            q_replies=[
                RETRY,
                tem.QReply(
                    '조회', 'block', '사용자 조회', '63b115302a784f093357cee8'
                )
            ]
        )

    else:
        return tem.data(d='B#다4%^바*-N0+2T|타6!@8')


@router.post('/etc', response_class=ORJSONResponse)
async def etc(
    k_req: dict = Depends(kakao_bot),
    api_key: APIKey = Depends(get_api_key),
    db: AsyncSession = Depends(get_db)
):
    '''기타 백엔드 API

    마늘의 기타 백엔드 API입니다.
    '''
    user_req = k_req['userRequest']
    bot = k_req['bot']
    params = k_req['action']['params']
    block = user_req['block']
    user_key = user_req['user']['properties'].get('plusfriendUserKey')
    bn, bi = block['name'], block['id']
    WEAK = '사용이 허가되지 않았어요.\n관리자에게 문의해주세요.'
    RETRY = tem.QReply('🌀 다시하기', 'block', '🌀 다시하기', bi)
    REFRESH = tem.QReply('🌀 새로고침', 'block', '🌀 새로고침', bi)

    if bn == '성인 이미지 판별':
        TITLE = ''
        return tem.itemCard(
            [tem.ItemList(*t) for t in [
                ('정답', ''),
                ('횟수', '')]],
            alignment='right', head=TITLE,
            q_replies=[RETRY]
        )

    else:
        return tem.data(d='B#다4%^바*-N0+2T|타6!@8')


@router.post('/game', response_class=ORJSONResponse)
async def game(
    k_req: dict = Depends(kakao_bot),
    api_key: APIKey = Depends(get_api_key),
    db: AsyncSession = Depends(get_db)
):
    '''게임 백엔드 API

    마늘 Xllent의 게임 API입니다.

    인자:
        k_req: 카카오에서 받은 페이로드
        api_key: API 키
        db: 데이터베이스 세션
    '''
    user_req = k_req['userRequest']
    bot = k_req['bot']
    params = k_req['action']['params']
    block = user_req['block']
    user_key = user_req['user']['properties'].get('plusfriendUserKey')
    user_code = await get_user_code(db, user_key)
    bn, bi = block['name'], block['id']
    WEAK = f'권한이 부족해 「{bn}」에 실패했어요.'
    RETRY = tem.QReply('🌀 다시하기', 'block', '🌀 다시하기', bi)
    CONTINUE = tem.QReply('🌀 이어하기', 'block', '🌀 이어하기', bi)

    if bn == '숫자 야구':
        TITLE = '⚾️  숫자 야구'
        if not await perm_user(db, user_key):
            return gtem(
                tem.simpleText(f'{TITLE}\n\n{WEAK}'), q_replies=[RETRY]
            )
        query = params['query']

        if '도움말' in query:
            return gtem(
                tem.simpleText(
                    f'''{TITLE} 도움말

- 바로가기 버튼 -
게임 종료: 게임을 종료해요.
도움말: 이 도움말을 띄워요.

- 게임 정보 -
1. 숫자를 맞추는 게임이에요.
2. 횟수가 적을수록 좋지만 너무 신경쓰지는 마세요.
3. 중복되지 않은 0에서 9까지의 숫자 4자리를 입력해야 해요.
4. 숫자는 맞지만 위치가 틀리면 '볼(B)'이에요.
5. 숫자가 맞고, 위치도 맞으면 '스트라이크(S)'예요.
6. 어떠한 숫자도 맞지 않으면 '아웃(OUT)'이에요.'''
                ), q_replies=[RETRY]
            )

        stmt = (select(NumberBaseball)
                .where(NumberBaseball.user_code == user_code))
        ud = (await db.execute(stmt)).first()

        if not ud:
            await db.execute(
                insert(NumberBaseball)
                .values(user_code=user_code,
                        answer=''.join(map(str, sample(range(9), 4))),
                        count=0, datetime=func.now())
            )
            await db.commit()
            ud = (await db.execute(stmt)).first()[0]
        else:
            ud = ud[0]

        if '종료' in query:
            await db.execute(
                delete(NumberBaseball)
                .where(NumberBaseball.user_code == user_code)
            )
            await db.commit()

            return gtem(
                tem.itemCard(
                    [tem.ItemList(*t) for t in [
                        ('정답', ud.answer), ('횟수', str(ud.count))
                    ]],
                    alignment='right', head=TITLE,
                    summary=tem.Summary('점수', '0')
                ), q_replies=[RETRY]
            )
        elif len(set(query)) != 4 or not query.isdigit():
            return gtem(
                tem.simpleText(
                    '\n\n'.join((TITLE, '올바르지 않은 입력값이에요.'))
                ), q_replies=[RETRY]
            )
        else:
            bt = num_baseball_check(query, ud.answer)
            count = ud.count + 1
            msg = '성공' if bt == '4S 0B' else '실패'
            if msg == '성공':
                score = 10000-(count-1)**3 if 1 <= count <= 22 else 0
                await db.execute(
                    delete(NumberBaseball)
                    .where(NumberBaseball.user_code == user_code)
                )
                await db.execute(
                    update(User)
                    .values(score=User.score + int(score))
                    .where(User.user_code == user_code)
                )
                summary = tem.Summary('점수', str(int(score)))
                q_reply = [RETRY]
            elif msg == '실패':
                await db.execute(
                    update(NumberBaseball)
                    .values(count=count)
                    .where(NumberBaseball.user_code == user_code)
                )
                summary = None
                q_reply = [CONTINUE]
            await db.commit()
            return gtem(
                tem.itemCard(
                    item_lists=[
                        tem.ItemList('입력값', query),
                        tem.ItemList('결과', f'{msg}, {bt}'),
                        tem.ItemList('횟수', str(count))
                    ],
                    alignment='right', head=TITLE, summary=summary
                ), q_replies=q_reply
            )

    elif bn == '끝말잇기':
        ...

    else:
        return tem.data(d='B#다4%^바*-N0+2T|타6!@8')
