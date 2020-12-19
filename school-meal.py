# -*- coding: utf-8 -*-
# 보안을 위해 일부 정보가 삭제되었습니다.
# Syun 제작

import json,re,urllib.request as u

def lambda_handler(event,context):
    
    
    params=json.loads(event['body'])['action']['params']
    dt=str(json.loads(params['date'])['value']).replace('-','')
    
    if params['mealtime']=='석식':
        mt='3'
    else:
        mt='2'
    
    with u.urlopen('주소') as url:
        try:
            data=re.sub('[0-9.]','',json.loads(url.read())['mealServiceDietInfo'][1]['row'][0]['DDISH_NM'].replace('<br/>','\n'))
        except:
            data='급식이 없어요!'
    
    result={
        'version':'2.0',
        'data':{
            'd':f'{dt[:4]}년 {dt[4:6]}월 {dt[6:]}일',
            'm':data
        }
    }

    return {
        'statusCode':200,
        'body':json.dumps(result),
        'headers':{'Access-Control-Allow-Origin':'*'}}
