# -*- coding: utf-8 -*-
# 보안을 위해 일부 정보가 삭제되었습니다.
# Syun 제작

import json,xmltodict,datetime as d,pytz,urllib.request as u

x=xmltodict.parse
dt=lambda n: d.datetime.now(pytz.timezone('Asia/Seoul'))-d.timedelta(n)

def lambda_handler(event,context):
    a=json.loads(event['body'])['action']['params']['covidarea']
    
    if a=='충남':
        area='Sido'
    else:
        area=''
    
    def info(n):
        day=dt(n).strftime('%Y%m%d')
        
        with u.urlopen('주소') as url:
            temp=json.loads(json.dumps(x(url.read().decode())))['response']['body']['items']['item']
        
        if area=='':
            return temp
        else:
            return temp[6]
    
    try:
        data=info(0)
        bdata=info(1)
        d='오늘'
    
    except:
        data=info(1)
        bdata=info(2)
        d='어제'
    
    def am(k):
        k+='Cnt'
        return f'{int(data[k]):,d}명({int(data[k])-int(bdata[k]):+,d}명)'
    
    result={
        'version':'2.0',
        'data':{
            'd':f'(알약)  {d}의 코로나 19 현황({a})'
        }
    }
    
    if area=='':
        result['data']['n']=f'''누적 확진자: {am('decide')}
치료 중: {am('care')}
검사 중: {am('exam')}
격리 해제: {am('clear')}
음성 결과: {am('resutlNeg')}
사망 환자: {am('death')}'''
    
    else:
        result['data']['n']=f'''누적 확진자: {am('def')}
격리 중: {am('isolIng')}
격리 해제: {am('isolClear')}
사망 환자: {am('death')}'''
    
    return {
        'statusCode':200,
        'body':json.dumps(result),
        'headers':{'Access-Control-Allow-Origin':'*'}}
