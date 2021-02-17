# 마늘 서버
# 제작: Syun
# 일부 정보는 개인정보 상의 이유로 삭제했습니다.

from flask import Flask, request
import urllib.request as u
import json
import tem
import manldb
import hashlib
import xmltodict as xtd
from datetime import datetime as dti, timedelta as td
from re import sub
from urllib import parse as p

owner = '주인 ID'
q = p.quote
xml = xtd.parse
settings = manldb.bot()  # 설정 불러오기
admins = manldb.admins()  # 관리자 목록 불러오기


def urlRequest(x):
    return u.urlopen(u.Request(x, headers={'User-Agent': 'Mozilla'}))


def covid(x, y):  # x: 지역, y: 날짜
    a = (dti.today()-td(y)).strftime('%Y%m%d')
    with u.urlopen('URL') as url:
        b = xml(url)['response']['body']['items']['item']
    return b if x == '' else b[6]


app = Flask(__name__)


@app.route('/')
def alive():
    return json.dumps({'alive': True})


@app.route('/skill', methods=['POST'])
def skill():
    global admins
    kakao = request.get_json()
    userReq = kakao['userRequest']
    block = userReq['block']['name']
    params = kakao['action']['params']

    if block == '급식 블록':
        dt = json.loads(params['date'])['value'].replace('-', '')

        with urlRequest('URL') as url:
            try:
                d = sub('[0-9.]', '', json.loads(url.read().decode().replace(
                    "'", '"'))['mealServiceDietInfo'][1]['row'][0]['DDISH_NM']
                       ).replace('<br/>', '\n')
            except BaseException:
                d = '급식을 조회할 수 없어요!'

        return tem.data(f'(밥)  {dt[:4]}년 {dt[4:6]}월 {dt[6:]}일\n\n{d}')

    elif block == 'QR코드 생성 블록':
        return tem.image('URL'), 'QR코드가 유효하지 않습니다.')

    elif block == '코로나 19 블록':
        a = params['covidarea']
        area = '' if a == '국내' else 'Sido'

        try:
            bdata = covid(area, 1)
            data = covid(area, 0)
            day = '오늘'
        except BaseException:
            data = bdata
            bdata = covid(area, 2)
            day = '어제'

        def am(x):  # x: 키
            x += 'Cnt'
            data2 = int(str(data[x]))
            return f'{data2:,d}명({data2 - int(str(bdata[x])):+,d}명)'

        base = f'{day}의 코로나 19 현황({a})\n\n'
        return tem.data(base + (f'''누적 확진자: {am('decide')}
치료 중: {am('care')}
검사 중: {am('exam')}
격리 해제: {am('clear')}
음성 결과: {am('resutlNeg')}
사망 환자: {am('death')}''' if area == '' else f'''누적 확진자: {am('def')}
격리 중: {am('isolIng')}
격리 해제: {am('isolClear')}
사망 환자: {am('death')}'''))

    elif block == '시간표 블록':
        d = ''

        with urlRequest('URL') as url:
            x = json.loads(url.read().decode())['school'][params['day']]

        for i in range(1, 8):
            y = x[str(i)]['sb']
            d += f'{i}교시: {"없음" if y == "" else y}\n'

        return tem.data(d)

    elif block == '자가진단 블록':
        birth = json.loads(params["birth"])["value"][2:].replace("-", "")

        with u.urlopen('URL') as url:
            try:
                json.loads(url.read().decode())['result']['registerDtm']
                d = '성공'
            except BaseException:
                d = '실패'

        return tem.data(d)

    elif block == '공지 블록':
        return tem.data(settings['notice'])

    else:
        return tem.data('테스트 성공')


@app.route('/admin', methods=['POST'])
def admin():
    global admins
    kakao = request.get_json()
    userReq = kakao['userRequest']
    block = userReq['block']['name']
    params = kakao['action']['params']
    userid = userReq['user']['id']
    isOwner = (userid == owner)
    isAdmin = userid in admins

    if block == '해싱 블록':
        return tem.data(hashlib.new(params['algo'].replace('-', '_'),
                                    params['text'].encode()).hexdigest())

    elif block == '관리자 목록 블록':
        return tem.data('\n\n'.join(admins) if isAdmin else (
            '권한이 없어 불러오기에 실패하였습니다.'))

    elif block == '관리자 수정 블록':
        adminpm = params['adminpm']
        adminid = params['userid']

        if adminpm == '추가':
            manldb.query(f"insert into admins values ('{adminid}');")

        else:
            manldb.query(f"delete from admins where userid='{adminid}';")

        admins = manldb.admins()

        return tem.data(adminpm + ('에 성공' if isAdmin and (
            adminid != owner) else '에 권한이 없어 실패'))

    elif block == '사용자 ID 블록':
        return tem.data(f'{userid}, {isOwner}, {isAdmin}')


@app.route('/hash')
def hash():
    return hashlib.new(request.args.get('algo').replace('-', '_'),
                       request.args.get('text').encode()).hexdigest()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)
