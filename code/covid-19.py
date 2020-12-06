# -*- coding: utf-8 -*-
# 보안을 위해 일부 정보가 삭제되었습니다.
# Syun 제작

import json,xmltodict,datetime,pytz,urllib.request as u

x=xmltodict.parse
d=datetime
p=pytz.timezone
dt=d.datetime.now(p('Asia/Seoul'))
td=d.timedelta

def lambda_handler(event,context):
    area=json.loads(event['body'])['action']['params']['covidarea']
    
    def info(day):
        day=day.strftime('%Y%m%d')
        s=''
        if area=='국내':
            s='Sido'
        with u.urlopen(f'http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19{s}InfStateJson?serviceKey=서비스키&pageNo=1&numOfRows=10&startCreateDt={day}&endCreateDt={day}') as url:
            temp=json.loads(json.dumps(x(url.read().decode())))['response']['body']['items']['item']
        if area=='지역':
            return temp[번호]
        return temp
    
    try:
        data=info(dt)
        bdata=info(dt-td(1))
        today=dt.strftime('%Y%m%d일(오늘)')
        
    except:
        data=info(dt-td(1))
        bdata=info(dt-td(2))
        today=(dt-td(1)).strftime('%Y%m%d일(어제)')
    
    def am(key):
        key+='Cnt'
        data2=data[key]
        bdata2=bdata[key]
        return f'{int(data2):,d}명({int(data2)-int(bdata2):+,d}명)'
    
    result={
        'version':'2.0',
        'data':{
            'd':f'{today[0:4]}년 {today[4:6]}월 {today[6:]}',
            'area':area
        }
    }
    
    if area=='국내':
        result['data']['n']=f'''누적 확진자: {am('decide')}
        치료 중: {am('care')}
        검사 중: {am('exam')}
        격리 해제: {am('clear')}
        사망 환자: {am('death')}
        음성 결과: {am('resutlNeg')}'''.replace(' '*4,'')
    
    if area=='지역':
        result['data']['n']=f'''누적 확진자: {am('def')}
        격리 중: {am('isolIng')}
        격리 해제: {am('isolClear')}
        사망 환자: {am('death')}'''.replace(' '*4,'')
    
    return {
        'statusCode':200,
        'body':json.dumps(result),
        'headers':{'Access-Control-Allow-Origin':'*'}}
