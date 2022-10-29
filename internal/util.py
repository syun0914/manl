from aiohttp import ClientSession
from datetime import datetime, timedelta
from comcigan import AsyncSchool
from bs4 import BeautifulSoup as BS
from random import sample
from re import compile, findall
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
DAY_NAME = {
    'monday': 0,
    'tuesday': 1,
    'wednesday': 2,
    'thursday': 3,
    'friday': 4
}

async def meal(
    date: str, mealtime: int, nutrient: bool = False
) -> dict[str, str]:
    '''급식 정보 불러오기

    급식 정보를 불러옵니다.

    인자:
        date: 날짜 8자(예: 20200608)
        mealtime: 1(아침) 또는 2(점심) 또는 3(저녁)
        nutrient: True(영양소 정보) 또는 False(메뉴)
    '''
    dt = str(date).replace('-', '')
    p = OLD_P if int(dt) < 20220415 else NEW_P
    n = 'NTR_INFO' if nutrient else 'DDISH_NM'
    sMT = '아침' if mealtime == 1 else ('점심' if mealtime == 2 else '저녁')
    qData = {
        'ATPT_OFCDC_SC_CODE': 'N10', 'SD_SCHUL_CODE': '8140209',
        'key': 'c3e5ba8a996c4ca19763f7120863f362',
        'TYPE': 'JSON', 'MMEAL_SC_CODE': str(mealtime), 'MLSV_YMD': dt
    }
    try:
        if dt == '20200608':
            l = FIRST_DAY
        else:
            async with ClientSession() as sess:
                async with sess.get(
                    url='https://open.neis.go.kr/hub/mealServiceDietInfo',
                    params=qData
                ) as resp:
                    l = (
                        await resp.json(content_type='text/html')
                    )['mealServiceDietInfo'][1]['row'][0][n]
        d = '\n'.join(
            [p.sub(r' \1', s) for s in l.split('<br/>')]
        ).replace('  ', '')
    except KeyError:
        if int(dt) < 20200701:
            d = '2020년 7월 1일보다 이전의 급식은 찾을 수 없습니다.'
        else:
            d = '급식을 찾을 수 없습니다.'
    return {
        'title': f'🍔 {dt[:4]}년 {int(dt[4:6])}월 {int(dt[6:])}일, {sMT}',
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
        date: 오늘 날짜에서 뺄 날
        area_ln: 지역 번호
        session: 세션
    '''
    sess = session or ClientSession()
    a = (datetime.today() - timedelta(date)).strftime('%Y%m%d')
    query = {
        'serviceKey': 'kWsWMpUwzewV4CIR9RxAk++51wSPSggNsBkGmLKYZI5E5DDaYcnr9FkgLW1v6UpAyGhr5VfScF1/OE4Lxrwb8g==',
        'pageNo': '1',
        'numOfRows': '10',
        'startCreateDt': a,
        'endCreateDt': a
    }
    b = xp(
        (await sess.get(
            url=f'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19{location}InfStateJson',
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


async def timetable(class_: str, day: str) -> dict:
    '''시간표 정보 불러오기

    컴시간알리미에서 시간표 정보를 불러옵니다.

    인자:
        class_: 학급(예: 3학년 1반 -> '3-1')
        day: 영문 요일명(예: 'monday')
    '''
    class_ = class_.split('-')
    d = AsyncSchool('서일중학교')[class_[0]][class_[1]][DAY_NAME[day]]

    return {
        'timeTable': '\n'.join(
            f'{k}교시: {v["sb"] or "없음"}' for k, v in d if k != '8'
        ),
        'title': class_ + '반 시간표'
    }


def abn(n: int) -> str:
    '''(a+b)^n 전개하기

    (a+b)^n의 전개식을 출력합니다.
    '''
    e = str(expand((Symbol('a')+Symbol('b'))**n)).replace('*', '')
    for s in findall('a\d+b\d+|[a|b]\d+', e):
        e = e.replace(s, s.translate({
        	48: 8304, 49:  185, 50:  178, 51:  179, 52: 8308,
       		53: 8309, 54: 8310, 55: 8311, 56: 8312, 57: 8313
    	}))
    return e


async def school_notice():
    '''학교 공지사항 불러오기

    서일중학교 공지사항을 불러옵니다.
    '''
    BSTR = 'http://seo-il.cnems.kr/boardCnts/updateCnt.do?boardID={}&viewBoardID={}&boardSeq={}&lev={}&action=view&searchType=null&srch2=null&s=seo_il&statusYN=W&page=1'
    async with ClientSession() as sess:
        async with sess.get(
            'http://seo-il.cnems.kr/boardCnts/list.do?boardID=30405&m=0505&s=seo_il'
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


async def adult_detect(url: str) -> dict:
    '''성인 이미지 판별하기

    카카오 API를 사용하여 {url}의 성인 이미지 여부에 대한 정보를 불러옵니다.

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
    return len(findall('[\sㄱ-ᇿ・-ーㄱ-ㆎꥠ-ꥼ가-힣ힰ-ퟻﾡ-ￜ]', s)) == len(s)


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


def num_baseball_check(input_: str, answer: str) -> str:
    '''숫자야구 결과 확인하기

    '{int}S {int}B' 또는 'OUT' 형식으로 숫자를 정답과 비교한 결과를 반환합니다.

    인자:

    '''
    strike = 0
    for s1, s2 in zip(input_, answer):
        if s1 == s2:
            strike += 1
    ball = len(set(input_) & set(answer)) - strike
    return f'{strike}S {ball}B' if strike or ball else 'OUT'