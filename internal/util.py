import random as r
from multiprocessing.connection import Client
from re import compile, findall
from bs4 import BeautifulSoup as bs
from sympy import expand, Symbol
from datetime import datetime as dti, timedelta as td
from xmltodict import parse as xp
from aiohttp import ClientSession
from typing import Optional


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

async def meal(dt: str, mt: int, ntr: bool=False):
    '''
    주어진 인자들로 급식 정보를 얻습니다.
    
    (조건) dt는 YYYYMMDD(연도 4자리-월 2자리-일 2자리)의 형식으로 입력해야 합니다.
           mt는 1(아침), 2(점심), 3(저녁)이어야 합니다.
           ntr은 True(영양소 정보), False(메뉴)여야 합니다.
    '''
    dt = str(dt).replace('-', '')
    p = OLD_P if int(dt) < 20220415 else NEW_P
    n = 'NTR_INFO' if ntr else 'DDISH_NM'
    sMT = '아침' if mt == 1 else ('점심' if mt == 2 else '저녁')
    qData = {
        'ATPT_OFCDC_SC_CODE': 'N10', 'SD_SCHUL_CODE': '8140209',
        'key': 'c3e5ba8a996c4ca19763f7120863f362',
        'TYPE': 'JSON', 'MMEAL_SC_CODE': str(mt), 'MLSV_YMD': dt
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
    except KeyError as e:
        if int(dt) < 20200701:
            d = '2020년 7월 1일보다 이전의 급식은 찾을 수 없습니다.'
        else:
            d = '급식을 찾을 수 없습니다.'
    return {
        'title': f'🍔 {dt[:4]}년 {int(dt[4:6])}월 {int(dt[6:])}일, {sMT}',
        'meal': d
    }


async def _get_covid(
    loc: str, dat: int, an: int, session: Optional[ClientSession]=None
):
    '''
    주어진 인자들로 코로나19 정보를 얻습니다.
    (조건) loc는 ''나 'Sido'
    (권장) an은 _getCovidAC를 통해 입력하는 것을 권장합니다.
    '''
    sess = session or ClientSession()
    a = (dti.today()-td(dat)).strftime('%Y%m%d')
    query = {
        'serviceKey': 'kWsWMpUwzewV4CIR9RxAk++51wSPSggNsBkGmLKYZI5E5DDaYcnr9Fk' \
        		  	  'gLW1v6UpAyGhr5VfScF1/OE4Lxrwb8g==',
        'pageNo': '1',
        'numOfRows': '10',
        'startCreateDt': a,
        'endCreateDt': a
    }
    b = xp(
        (await sess.get(
            url='http://openapi.data.go.kr/openapi/service/rest/Covid19/' \
                f'getCovid19{loc}InfStateJson',
            params=query
        )).text
    )['response']['body']['items']['item']

    if not session:
        await sess.close()
    
    return b if loc else b[an]


async def covid(a: str, session: Optional[ClientSession]=None):
    '''
    a(지역·구분 이름)으로 코로나19 정보를 얻고,
    title(제목 포함 여부)에 따라 제목을 반환합니다.
    '''
    sess = session or ClientSession()
    d = {}
    ac = -1 if a == '한국' else AREA_LIST.index(a)
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
    d['title'] = f'{a}, {dayName}의 코로나19 현황'

    if not session:
        await sess.close()
    
    return d


async def timetable(class_: str, day: str):
    '''
    class_(학급)의 day(요일)의 시간표 정보를 불러옵니다.

    (조건) class_는 0-0(학년-반)의 형식으로 입력해야 합니다.
           day는 monday, tuesday, wednesday, thursday, friday여야 합니다.
    '''
    async with ClientSession() as sess:
        async with sess.get(
            'https://biqapp.com/api/v1/timetable/50494/'
            + class_.replace('-', '/')
        ) as resp:
            d = (
                await resp.json(content_type='text/html')
            )['school']['timetable'][day].items()

    return {
        'timeTable': '\n'.join(
            f'{k}교시: {v["sb"] or "없음"}' for k, v in d if k != '8'
        ),
        'title': class_ + '반 시간표'
    }


def abn(n: int):
    '''
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
    '''
    학교 공지사항을 c개만큼 불러옵니다.
    '''
    BSTR = 'http://seo-il.cnems.kr/boardCnts/updateCnt.do?boardID={}' \
    	   '&viewBoardID={}&boardSeq={}&lev={}&action=view&searchType=null' \
           '&srch2=null&s=seo_il&statusYN=W&page=1'
    async with ClientSession() as sess:
        async with sess.get(
            'http://seo-il.cnems.kr/boardCnts/list.do?' \
            'boardID=30405&m=0505&s=seo_il'
        ) as resp:
            a = bs(await resp.text(), 'lxml').find('div', class_='BD_table')
    title, ls = [], []
    for s in a.find_all('a'):
        title += [s['title']]
        ls += [findall("'(.*?)'", s['onclick'])[:4]]
    writer = (h.text for h in a.find_all('td', class_='ctext')[1::5])
    url = (BSTR.format(*l) for l in ls)
    return zip(title, writer, url)


async def adult_detect(url: str):
    '''
    url의 성인 이미지일 확률을 얻습니다.
    '''
    async with ClientSession() as sess:
        async with sess.post(
            url='https://dapi.kakao.com/v2/vision/adult/detect',
            headers={'Authorization': 'KakaoAK 5431618036a6f520ca2d7af013d4ded2'},
            data={'image_url': url}
        ) as resp:
            return (await resp.json())['result']


def lotto():
    '''무작위로 로또 번호 리스트를 생성합니다.'''
    return sorted(r.sample(range(1, 46), 6))


def is_hangul(s: str) -> bool:
    '''s(문자열)가 한글로만 이루어졌는지 판별합니다.'''
    return len(findall('[\sㄱ-ᇿ・-ーㄱ-ㆎꥠ-ꥼ가-힣ힰ-ퟻﾡ-ￜ]', s)) == len(s)


def is_hanja(s: str) -> bool:
    '''s(문자열)가 한자로만 이루어졌는지 판별합니다.'''
    return len(findall('[一-龿㐀-\u4dbf⺀-\u2eff豈-\ufaff]', s)) == len(s)