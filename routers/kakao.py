import orjson as j
import internal.num_baseball as nb
import internal.tem as tem
import yaml as y

from databases.database import con, cur, permission, IntegrityError
from dependencies import api_key, kakao_bot
from fastapi import APIRouter, Depends
from re import findall
from time import time

from fastapi.security.api_key import APIKey
from internal.util import *

router = APIRouter()


@router.post('/skill')
async def skill(k_req=Depends(kakao_bot), api_key: APIKey = Depends(api_key)):
    '''
    일반 백엔드 API
    -----
    마늘의 일반 백엔드 API입니다.
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
        if not await permission(user_key):
            return tem.data(d=WEAK, t='사용 불가')
        mt = params['mealtime']
        d = await meal(
            j.loads(params['date'])['value'],
            1 if mt == '조식' else (2 if mt == '중식' else 3)
        )
        return tem.data(d=d['meal'], t=d['title'])

    elif bn == '코로나19 현황':
        if not await permission(user_key):
            return tem.data(d=WEAK, t='사용 불가')
        d = await covid(params['area'], True)
        return tem.data(d=d['covid'], t=d['title'])

    elif bn == '시간표':
        if not await permission(user_key):
            return tem.data(d=WEAK, t='사용 불가')
        d = await timetable('3-1', params['day'])
        return tem.data(d=d['timeTable'], t=d['title'])
    
    elif bn == '사용자 키':
        return tem.simpleText(user_key)
    
    elif bn == '공지':
        cur.execute("SELECT content FROM bot WHERE field='notice';")
        return tem.data(d=cur.fetchone()[0])

    elif bn == '학교 공지 목록':
        title = '📢 서일중학교 공지'
        if not await permission(user_key):
            return tem.simpleText(f'{title}\n\n{WEAK}', [RETRY])
        b = [tem.KList(*t[:2], '', {'web': t[2]}) \
             for t in await school_notice()]
        return tem.carousel(
            'listCard',
            [tem.listCard(title, b[i*5:i*5+5]) for i in range(5)],
            [REFRESH]
        )

    elif bn == 'QR코드 생성':
        if not await permission(user_key):
            return tem.simpleText(f'🏁 QR코드 생성\n\n{WEAK}', [RETRY])
        return tem.image(
            f'https://chart.apis.google.com/chart?cht=qr&chs=547x547&chl={params["qrmsg"]}'
            'QR코드를 생성하는데 문제가 발생했어요.',
            [RETRY]
        )
    
    if bn == '건의':
        if not await permission(user_key):
            return tem.simpleText(WEAK)
        mt = params['mealtime']
        d = await meal(
            j.loads(params['date'])['value'],
            1 if mt == '조식' else (2 if mt == '중식' else 3)
        )
        return tem.data(d=d['meal'], t=d['title'])
    
    else:
        return tem.data(d='B#다4%^바*-N0+2T|타6!@8')


@router.post('/admin')
async def admin(k_req=Depends(kakao_bot), api_key: APIKey = Depends(api_key)):
    '''
    관리자 백엔드 API
    -----
    마늘의 관리자 백엔드 API입니다.
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
        if not await permission(user_key, 4):
            return tem.simpleText(WEAK)
        try:
            res = eval(params['eval'])
        except BaseException as e:
            res = e
        return tem.simpleText(str(res)[:4010])

    elif bn == '공지 수정':
        if not await permission(user_key, 3):
            return tem.simpleText(WEAK)
        text = params['text']
        try:
            cur.execute('UPDATE `notice` SET notice=? where num=0;', (text,))
            res = '성공'
            con.commit()
        except:
            res = '오류가 발생해 실패'
        return tem.simpleText(f'📢 공지 수정에 {res}했어요.', [RETRY])
    
    elif bn == '사용자 관리':
        TITLE = '👨🏻‍💼 사용자 관리'
        if not await permission(user_key, 4):
            return tem.simpleText(f'{TITLE}\n\n{WEAK}')

        menu: str = params['menu']
        try:
            query: dict[str, str] = y.load(params['query'].replace(', ', '\n'), Loader=y.FullLoader)
        except:
            return tem.simpleText(
                f'{TITLE}\n\n올바르지 않은 행동이에요. YAML+쉼표 형식으로 보냈는지 확인해주세요.',
                [RETRY]
            )
        
        if menu == '추가' and len(query) == 4:
            try:
                cur.execute(
                    'INSERT OR IGNORE INTO `users` VALUES (?, ?, ?, ?)',
                    (query['user_key'], query['name'],
                     query['student_ID'], query['level'])
                )
                res = '성공'
                con.commit()
            except:
                res = '실패'

            return tem.simpleText(
                f'{TITLE}\n\n사용자 추가에 {res}했어요.', [RETRY]
            )
        elif menu == '제거' and len(query) > 0:
            try:
                cur.execute(f'''
                    DELETE FROM `users` WHERE
                    {" AND ".join(f"{k} LIKE '{v}'" for k, v in query.items())}
                ''')
                res = '성공'
                con.commit()
            except:
                res = '실패'
            return tem.simpleText(
                f'{TITLE}\n\n사용자 제거에 {res}했어요.', [RETRY]
            )
        elif menu == '조회' and len(query) > 0:
            try:
                cur.execute(f'''
                    SELECT * FROM `users` WHERE
                    {" AND ".join(f"{k} LIKE '{v}'" for k, v in query.items())}
                ''')
                userdata = cur.fetchone()
                res = [
                    ('사용자 키', userdata[0]),
                    ('이름', userdata[1]), ('학번', userdata[2]),
                    ('등급·허가 상태', userdata[3])
                ]
                return tem.listCard(TITLE, [tem.KList(*t) for t in res], [RETRY])
            except:
                return tem.simpleText(f'{TITLE}\n\n사용자 조회에 실패했어요.', [RETRY])
        elif menu == '등급' and len(query) > 1:
            try:
                cur.execute(
                    f'''UPDATE users SET level=? WHERE {
                    	' AND '.join(
                        f"{k} LIKE '{v}'" for k, v in query.items()
                        if k != 'level')
                    }''',
                    (query['level'],)
                )
                res = '성공'
                con.commit()
            except:
                res = '실패'
            return tem.simpleText(
                f'{TITLE}\n\n사용자 등급·허가 상태 변경에 {res}했어요.', [RETRY]
            )
        else:
            return tem.simpleText(
                f'{TITLE}\n\n올바르지 않은 행동이에요. YAML+쉼표 형식으로 보냈는지 확인해주세요.',
                [RETRY]
            )

    elif bn == '관리자 목록':
        TITLE = '👨🏻‍💼 관리자 목록(클래식)'
        SEP = '\n----------\n> '
        if not await permission(user_key, 2):
            return tem.simpleText(WEAK)
        cur.execute('SELECT * FROM users WHERE level>1')
        l = cur.fetchall()
        return tem.simpleText(
            '\n'.join(
                TITLE, SEP, SEP.join('\n> '.join(map(str, t)) for t in l), SEP
            ),
            [
                REFRESH, tem.QReply('👨🏻‍💼 사용자 관리', 'block',
                    	            '👨🏻‍💼 사용자 관리', '631b2af35a905f23599f6bea')
            ]
        )

    else:
        return tem.data(d='B#다4%^바*-N0+2T|타6!@8')


@router.post('/etc')
async def etc(k_req=Depends(kakao_bot), api_key: APIKey = Depends(api_key)):
    '''
    기타 백엔드 API
    -----
    마늘의 기타 백엔드 API입니다.
    '''
    user_req = k_req['userRequest']
    bot = k_req['bot']
    params = k_req['action']['params']
    block = user_req['block']
    user_key = user_req['user']['properties']['plusfriendUserKey']
    bn, bi = block['name'], block['id']
    RETRY = tem.QReply('🌀 다시하기', 'block', '🌀 다시하기', bi)
    REFRESH = tem.QReply('🌀 새로고침', 'block', '🌀 새로고침', bi)
    
    if bn == '도서관 책 검색':
        return tem.simpleText('「도서관 책 검색」이 2022년 7월 22일에 서비스가 종료되었어요.')

    else:
        return tem.data(d='B#다4%^바*-N0+2T|타6!@8')


@router.post('/game')
async def game(k_req=Depends(kakao_bot), api_key: APIKey = Depends(api_key)):
    '''
    게임 백엔드 API
    -----
    마늘의 게임 백엔드 API입니다.
    '''
    user_req = k_req['userRequest']
    bot = k_req['bot']
    params = k_req['action']['params']
    block = user_req['block']
    user_key = user_req['user']['properties']['plusfriendUserKey']
    bn, bi = block['name'], block['id']
    WEAK = '사용이 허가되지 않았어요.\n관리자에게 문의해주세요.'
    RETRY = tem.QReply('🌀 다시하기', 'block', '🌀 다시하기', bi)
    REFRESH = tem.QReply('🌀 새로고침', 'block', '🌀 새로고침', bi)

    if bn == '숫자야구':
        TITLE = '⚾️  숫자야구'
        if not await permission(user_key):
            return tem.simpleText('\n\n'.join((TITLE, WEAK)))
        input_ = params['input']

        if '시작' in input_:
            try:
                cur.execute(
                	'INSERT INTO num_baseball VALUES (?, ?, 0, ?);',
                	(user_key, nb.new(), time())
            	)
                message = '게임을 시작했어요. 숫자야구를 다시 실행해 숫자를 입력해주세요.'
                con.commit()
            except IntegrityError:
                message = '이미 게임이 시작되었어요. 숫자야구를 다시 실행해 숫자를 입력해주세요.'
            except:
                message = '알 수 없는 오류가 발생했어요.'
            return tem.simpleText('\n\n'.join((TITLE, message)), [RETRY])
            
        elif '도움말' in input_:
            return tem.simpleText(
                f'{TITLE} 도움말\n\n' \
                '〈바로가기 버튼〉\n' \
                '게임 시작: 게임을 시작해요.\n' \
                '게임 종료: 게임을 종료해요.\n' \
                '도움말: 이 도움말을 띄워요.\n\n' \
                '〈게임 정보〉\n' \
                '1. 숫자를 맞추는 게임이에요.\n' \
                '2. 횟수가 적을수록 좋지만 너무 신경쓰지는 마세요.\n' \
                '3. 중복되지 않는 0에서 9까지의 숫자 4자리를 입력해야 해요.\n' \
                "4. 숫자는 맞지만 위치가 틀렸을 때는 '볼(B)'이에요.\n" \
                "5. 숫자가 맞고, 위치도 맞았을 때는 '스트라이크(S)'예요.\n" \
                "6. 어떠한 숫자도 맞지 않았을 때는 '아웃(OUT)'이에요.",
                [RETRY]
            )

        try:
            cur.execute(
                'SELECT * FROM num_baseball WHERE user_key=?;', (user_key,)
            )
            userdata = cur.fetchall()[0]
        except:
            return tem.simpleText('\n\n'.join((TITLE, '알 수 없는 오류가 발생했어요.')), [RETRY])

        if '종료' in input_:
            try:
                cur.execute(
                    'DELETE FROM num_baseball WHERE user_key=?', (user_key,)
                )
            except:
                return tem.simpleText('\n\n'.join((TITLE, '게임을 종료하지 못했어요.')), [RETRY])
            else:
                con.commit()
                res = [('정답', userdata[1]), ('횟수', str(userdata[2]))]
            return tem.listCard(
                TITLE, [tem.KList(*t) for t in res], [RETRY]
            )
        elif len(set(input_)) != 4 or not input_.isdigit():
            return tem.simpleText('\n\n'.join((TITLE, '올바르지 않은 입력값이에요.')), [RETRY])
        else:
            bt = nb.check(input_, userdata[1])
            count = userdata[2] + 1
            msg = '성공' if bt == '4S 0B' else '실패'
            if msg == '성공':
                cur.execute(
                    'DELETE FROM num_baseball WHERE user_key=?', (user_key,)
                )
            elif msg == '실패':
                cur.execute(
                    'UPDATE num_baseball SET count=? WHERE user_key=?',
                    (count, user_key)
                )
            con.commit()
            res = [('입력값', input_),
                   ('결과', ', '.join(msg, count)),
                   ('횟수', str(count))]
            return tem.listCard(
                TITLE, [tem.KList(*t) for t in res], [RETRY]
            )

    else:
        return tem.data(d='B#다4%^바*-N0+2T|타6!@8')
    # https://builder.pingpong.us/api/builder/5f362984e4b00e31991555f5/chat/simulator?query=%EC%9A%95%ED%95%B4%EB%B4%90