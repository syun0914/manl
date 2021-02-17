# Manl Template

# 마늘 카카오톡 템플릿
# 제작: Syun

import json


def data(x, **y):  # x: 기본 데이터, y: 가변 데이터
    a = {
        'version': '2.0',
        'data': {
            'd': x
        }
    }

    try:
        for k, v in y.items():
            a['data'][k] = v
    except BaseException:
        pass

    return json.dumps(a, ensure_ascii=False)


def image(x, y='이미지 정보를 불러올 수 없습니다.'):  # x: 이미지 Url, y: 오류 메시지
    return json.dumps({
        'version': '2.0',
        'template': {
            'outputs': [
                {
                    'simpleImage': {
                        'imageUrl': x,
                        'altText': y
                    }
                }
            ]
        }
    }, ensure_ascii=False)
