# -*- coding: utf-8 -*-
# 보안을 위해 일부 정보가 삭제되었습니다.
# Syun 제작

import json,re,urllib.request

def lambda_handler(event,context):
    
    req_body=json.loads(event['body'])
    params=req_body['action']['params']
    date=str(json.loads(params['date'])['date']).replace('-','')
    mealtime=params['mealtime'].replace('중식','2').replace('석식','3')
    
    with urllib.request.urlopen(f'https://open.neis.go.kr/hub/mealServiceDietInfo?ATPT_OFCDC_SC_CODE=N10&SD_SCHUL_CODE=8140209&KEY=키&TYPE=JSON&MMEAL_SC_CODE={mealtime}&MLSV_YMD={date}') as url:
        try:
            data=re.sub('[0-9.]','',json.loads(url.read())['mealServiceDietInfo'][1]['row'][0]['DDISH_NM'].replace('<br/>','\n'))
        
        except:
            data='급식이 없어요!'
    result={
        'version':'2.0',
        'data':{
            'd':f'{date[0:4]}년 {date[4:6]}월 {date[6:8]}일',
            'm':data
        }
    }

    return {
        'statusCode':200,
        'body':json.dumps(result),
        'headers':{'Access-Control-Allow-Origin':'*'}}
