from aiohttp import ClientSession
from bs4 import BeautifulSoup as BS
from comcigan import AsyncSchool
from datetime import timedelta, datetime
from exceptions import NotDigitError
from random import sample
from re import compile, findall, finditer, Pattern
from sympy import expand, Symbol
from xmltodict import parse as xp

FIRST_DAY = '''
친환경기장밥
<br/>냉메밀국수3.5.6.7.18.
<br/>오리훈제/무쌈1.5.
<br/>김치전1.2.5.6.9.10.
<br/>배추김치
<br/>부추샐러드5.6.13.
<br/>친환경수박
'''.replace('\n', '')
OLD_P = compile(r'([\d.]+)')
NEW_P = compile(r'\(([^)]+)\)')
AREA_LIST = [
    '검역', '제주', '경남', '경북', '전남', '전북',
    '충남', '충북', '강원', '경기', '세종', '울산',
    '대전', '광주', '인천', '대구', '부산', '서울'
]
DAY_NAME = {'월요일': 0, '화요일': 1, '수요일': 2, '목요일': 3, '금요일': 4}


def meal_filter(p: Pattern, t: str) -> str:
    return '\n'.join(
        [p.sub(r' \1', s) for s in t.split('<br/>')]
    ).replace('  ', '')


async def meal(
    date: str, meal_time: str, nutrient: bool = False
) -> dict[str, str]:
    '''급식 정보 불러오기

    급식 정보를 불러옵니다.

    인자:
        date: 날짜 8자리(예: 20200608)
        meal_time: 아침, 점심, 저녁
        nutrient: 영양소 정보(True), 메뉴(False)
    '''
    dt = str(date).replace('-', '')
    p = OLD_P if int(dt) < 20220415 else NEW_P
    n = 'NTR_INFO' if nutrient else 'DDISH_NM'
    mt = {'아침': 1, '점심': 2, '저녁': 3}[meal_time]
    params = {
        'ATPT_OFCDC_SC_CODE': 'N10', 'SD_SCHUL_CODE': '8140209',
        'key': 'c3e5ba8a996c4ca19763f7120863f362', 'TYPE': 'JSON',
        'MLSV_YMD': dt
    }
    try:
        if dt == '20200608' and mt == '2':
            content = FIRST_DAY
        else:
            async with ClientSession() as sess:
                async with sess.get(
                    url='https://open.neis.go.kr/hub/mealServiceDietInfo',
                    params=params
                ) as resp:
                    content = (
                        await resp.json(content_type='text/html')
                    )['mealServiceDietInfo'][1]['row'][mt-1][n]
        d = meal_filter(p, content)
    except KeyError:
        if int(dt) < 20200701:
            d = '2020년 7월 1일보다 이전의 급식은 찾을 수 없습니다.'
        else:
            d = '급식을 찾을 수 없습니다.'
    return {
        'title': f'🍔 {dt[:4]}년 {int(dt[4:6])}월 {int(dt[6:])}일, {meal_time}',
        'meal': d
    }


async def meal_unit(
    date: str, nutrient: bool = False
) -> dict[str, str]:
    '''급식 정보 불러오기

    급식 정보를 불러옵니다.

    인자:
        date: 날짜 8자리(예: 20200608)
        nutrient: 영양소 정보(True), 메뉴(False)
    '''
    dt = str(date).replace('-', '')
    p = OLD_P if int(dt) < 20220415 else NEW_P
    n = 'NTR_INFO' if nutrient else 'DDISH_NM'
    params = {
        'ATPT_OFCDC_SC_CODE': 'N10', 'SD_SCHUL_CODE': '8140209',
        'key': 'c3e5ba8a996c4ca19763f7120863f362', 'TYPE': 'JSON',
        'MLSV_YMD': dt
    }
    try:
        async with ClientSession() as sess:
            async with sess.get(
                url='https://open.neis.go.kr/hub/mealServiceDietInfo',
                params=params
            ) as resp:
                content = (
                    await resp.json(content_type='text/html')
                )['mealServiceDietInfo'][1]['row']
        d = '[점심]\n{}\n\n[저녁]\n{}\n'.format(
            *map(lambda x: meal_filter(p, x[n]), content[1:3])
        )
    except KeyError:
        if int(dt) < 20200701:
            d = '2020년 7월 1일보다 이전의 급식은 찾을 수 없습니다.'
        else:
            d = '급식을 찾을 수 없습니다.'
    return {
        'title': f'🍔 {dt[:4]}년 {int(dt[4:6])}월 {int(dt[6:])}일',
        'meal': d
    }


async def _get_covid(
    location: str,
    date: int,
    area_ln: int,
    session: ClientSession | None = None
) -> dict:
    '''코로나19 정보 불러오기

    오늘에서 {date}일 전의 코로나19 정보를 불러옵니다.

    인자:
        location: ''(국내) 또는 'Sido'(시도)
        date: 오늘 날짜에서 뺄 날 수
        area_ln: 지역 번호
        session: 세션
    '''
    sess = session or ClientSession()
    a = (datetime.today() - timedelta(date)).strftime('%Y%m%d')
    query = {
        'serviceKey': 'kWsWMpUwzewV4CIR9RxAk++51wSPSggNsBkGmLKYZI5E5DDaYcnr9FkgLW1v6UpAyGhr5VfScF1/OE4Lxrwb8g==',  # noqa
        'pageNo': '1',
        'numOfRows': '10',
        'startCreateDt': a,
        'endCreateDt': a
    }
    b = xp(
        (await sess.get(
            url=f'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19{location}InfStateJson',  # noqa
            params=query
        )).text
    )['response']['body']['items']['item']

    if not session:
        await sess.close()

    return b if location else b[area_ln]


async def covid(area_name: str, session: ClientSession | None = None) -> dict:
    '''코로나19 정보 불러오기

    대한민국의 코로나19 정보를 불러옵니다.

    인자:
        area_name: 2글자 지역명(예: '충남') 또는 '검역'
        session: 세션
    '''
    sess = session or ClientSession()
    d = {}
    ac = -1 if area_name == '한국' else AREA_LIST.index(area_name)
    loc = '' if ac == -1 else 'Sido'
    bData = await _get_covid(loc, 1, ac, sess)
    try:
        data = await _get_covid(loc, 0, ac, sess)
        dayName = '오늘'
    except KeyError:
        data = bData
        bData = await _get_covid(loc, 2, ac, sess)
        dayName = '어제'

    def am(key):
        k = key if 'Cnt' in key else key+'Cnt'
        _d = int(data[k])
        return f'{_d:,d}명({_d - int(bData[k]):+,d}명)'

    if loc == '':
        d['covid'] = '확진자 수: {}\n사망자 수: {}'.format(
            *map(am, ['decide', 'death'])
        )
    else:
        d['covid'] = '확진자 수: {}\n사망자 수: {}\n지역 발생: {}\n해외 유입: {}'.format(
            *map(am, ['def', 'death', 'localOcc', 'overFlow'])
        )
    d['title'] = f'{area_name}, {dayName}의 코로나19 현황'
    if not session:
        await sess.close()
    return d


async def timetable(class_: str, day: str, school_name: str) -> dict:
    '''시간표 정보 불러오기

    컴시간알리미에서 {class_}의 {day}요일 시간표 정보를 불러옵니다.

    인자:
         class_: 학급 (예: '3-1', '1-4')
         day: 영문 요일명 (예: 'monday')
         school_name: 학교 이름 (예: '서일중학교', '서일고등학교')
     '''
    c = class_.split('-')
    d = (await AsyncSchool.init(school_name)
         )[int(c[0])][int(c[1])][DAY_NAME[day]]

    return {
        'timetable': '\n'.join(
            f'{ct + 1}교시: {sj or "없음"}({tc})'
            for ct, (_, sj, tc) in enumerate(d)
        ),
        'title': f'⌛️ {class_}반 시간표'
    }


def abn(n: int) -> str:
    '''(a+b)의 거듭제곱꼴 전개하기

    (a+b)^{n}의 전개식을 출력합니다.
    '''
    e = str(expand((Symbol('a')+Symbol('b'))**n)).replace('*', '')
    for s in finditer(r'a\d+b\d+|[a|b]\d+', e):
        e = e.replace(s, s.translate({
            48: 8304, 49: 185, 50: 178, 51: 179, 52: 8308,
            53: 8309, 54: 8310, 55: 8311, 56: 8312, 57: 8313
        }))
    return e


async def school_board(url: str, board_id: str, m: str, s: str):
    '''학교 게시판 글 불러오기

    학교 홈페이지 게시판의 글 목록을 불러옵니다.

    인자:
        url: 학교 홈페이지 URL
        board_id: 게시판 ID
        m: 미상의 코드
        s: 학교 주소 앞 부분

    예외:
        NotDigitError: board_id, m은 숫자로 이루어져 있어야 합니다.
    '''
    if not (board_id.isdigit() and m.isdigit()):
        raise NotDigitError('board_id, m은 숫자로 이루어져 있어야 합니다.')
    BSTR = f'{url}/boardCnts/updateCnt.do?boardID={{}}&viewBoardID={{}}&boardSeq={{}}&lev={{}}&action=view&searchType=null&srch2=null&s={s}&statusYN=W&page=1'  # noqa
    async with ClientSession() as sess:
        async with sess.get(
            f'{url}/boardCnts/list.do?boardID={board_id}&m={m}&s={s}'
        ) as resp:
            a = BS(await resp.text(), 'lxml').find('div', class_='BD_table')
    title = []
    ls = []
    t_append = title.append
    l_append = ls.append
    for s in a.find_all('a'):
        t_append(s['title'])
        l_append(findall("'(.*?)'", s['onclick'])[:4])
    writer = (h.text for h in a.find_all('td', class_='ctext')[1::5])
    url = (BSTR.format(*l) for l in ls)
    return zip(title, writer, url)


async def detect_adult(url: str) -> dict:
    '''성인 이미지 판별하기

    카카오 API를 사용하여 URL의 성인 이미지 여부에 대한 정보를 불러옵니다.

    인자:
        url: 이미지 URL
    '''
    async with ClientSession() as sess:
        async with sess.post(
            url='https://dapi.kakao.com/v2/vision/adult/detect',
            headers={'Authorization': 'KakaoAK 5431618036a6f520ca2d7af013d4ded2'},
            data={'image_url': url}
        ) as resp:
            return (await resp.json())['result']


def lotto() -> list[int]:
    '''로또 번호 추첨하기

    무작위로 로또 번호 리스트를 생성합니다.
    '''
    return sorted(sample(range(1, 46), 6))


def is_hangul(s: str) -> bool:
    '''한글 여부 판별하기

    s가 한글로만 이루어졌는지 판별합니다.

    인자:
        s: 문자열

    예외:
        TypeError: s는 문자열이어야 합니다.
    '''
    if type(s) != str:
        raise TypeError('s는 문자열이어야 합니다.')
    return len(findall(r'[\sㄱ-ᇿ・-ーㄱ-ㆎꥠ-ꥼ가-힣ힰ-ퟻﾡ-ￜ]', s)) == len(s)


def is_hanja(s: str) -> bool:
    '''한자 여부 판별하기

    s가 한자로만 이루어졌는지 판별합니다.

    인자:
        s: 문자열

    예외:
        TypeError: s는 문자열이어야 합니다.
    '''
    if type(s) != str:
        raise TypeError('s는 문자열이어야 합니다.')
    return len(findall('[一-龿㐀-\u4dbf⺀-\u2eff豈-\ufaff]', s)) == len(s)


def num_baseball_check(query: str, answer: str) -> str:
    '''숫자야구 결과 확인하기

    입력값을 정답과 비교한 결과를 반환합니다.

    인자:
        query: 입력값
        answer: 정답

    예외:
        NotDigitError: query는 숫자로 이루어져 있어야 합니다.
    '''
    if not query.isdigit():
        raise NotDigitError('query는 숫자로 이루어져 있어야 합니다.')
    strike = 0
    for s1, s2 in zip(query, answer):
        if s1 == s2:
            strike += 1
    ball = len(set(query) & set(answer)) - strike
    return f'{strike}S {ball}B' if strike or ball else 'OUT'
