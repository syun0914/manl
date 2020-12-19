# -*- coding: utf-8 -*-
# 보안을 위해 일부 정보가 삭제되었습니다.
# Syun 제작

import json,re,urllib.request as u
from urllib import parse as p
q=p.quote

def lambda_handler(event,context):
    params=json.loads(event['body'])['action']['params']
    name=q(params['name'])
    pw=q(params['pw'])
    birth=q(json.loads(params['birth'])['value'].replace('-','')[2:])
    
    with u.urlopen('주소') as url:
        r=url.read().decode()
    
    try:
        json.loads(r)['registerDtm']
        d='자가진단이 완료되었습니다.'
    except:
        d='자가진단이 실패하였습니다.'
    
    result={
        'version':'2.0',
        'data':{
            'd':d
        }
    }

    return {
        'statusCode':200,
        'body':json.dumps(result),
        'headers':{'Access-Control-Allow-Origin':'*'}}
