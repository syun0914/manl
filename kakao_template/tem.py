from dataclasses import asdict, dataclass
from kakao_template.base import *

VERSION = '2.0'


def data(contexts: list[Context] | None = None, **kwargs) -> dict:
    '''챗봇 템플릿 (데이터)
    
    주어진 인자들을 챗봇 템플릿으로 변환합니다.

    키워드 인자:
        kwargs: 데이터
    '''
    return del_empty({
        'version': VERSION,
        'data': del_empty(kwargs),
        'context': del_empty({
            'values': contexts and [del_empty(asdict(c)) for c in contexts]
        })
    })


def simpleImage(
    url: str,
    alt_text: str | None = None,
    q_replies: list[QReply] | None = None,
    buttons: list[Button] | None = None,
    contexts: list[Context] | None = None
) -> dict:
    '''챗봇 템플릿 (이미지)

    주어진 인자들을 챗봇 템플릿으로 변환합니다.

    인자:
        url: 이미지 URL
        alt_text: 대체 텍스트
        q_replies: 바로가기 응답
        buttons: 버튼
        contexts: 컨텍스트
    '''
    a = {
        'version': VERSION,
        'template': {
            'outputs': [{'simpleImage': {
                'imageUrl': url,
                'altText': alt_text,
                'buttons': buttons and [del_empty(asdict(b)) for b in buttons]
            }}],
            'quickReplies': (
                q_replies and [del_empty(asdict(q)) for q in q_replies]
            )
        },
        'context': del_empty({
            'values': contexts and [del_empty(asdict(c)) for c in contexts]
        })
    }
    
    return t_filter(del_empty(a), 'simpleImage')


def simpleText(
    text: str,
    q_replies: list[QReply] | None = None,
    buttons: list[Button] | None = None,
    forwardable: bool = False,
    contexts: list[Context] | None = None
) -> dict:
    '''챗봇 템플릿 (텍스트)

    주어진 인자들을 챗봇 템플릿으로 변환합니다.

    인자:
        text: 텍스트
        q_replies: 바로가기 응답
        buttons: 버튼
        forwardable: 전달 가능 여부
        contexts: 컨텍스트
    '''
    a = {
        'version': VERSION,
        'template': {
            'outputs': [{'simpleText': {
                'text': text,
                'forwardable': forwardable,
                'buttons': buttons and [del_empty(asdict(b)) for b in buttons]
            }}],
            'quickReplies': (
                q_replies and [del_empty(asdict(q)) for q in q_replies]
            )
        },
        'context': del_empty({
            'values': contexts and [del_empty(asdict(c)) for c in contexts]
        })
    }
    return t_filter(del_empty(a), 'simpleText')


def listCard(
    title: str,
    list_items: list[LCI],
    q_replies: list[QReply] | None = None,
    buttons: list[Button] | None = None,
    forwardable: bool = False,
    contexts: list[Context] | None = None
) -> dict:
    '''챗봇 템플릿 (리스트 카드)

    주어진 인자들을 챗봇 템플릿으로 변환합니다.

    인자:
        title: 제목
        kLists: 카카오 리스트
        q_replies: 바로가기 응답
        buttons: 버튼
        forwardable: 전달 가능 여부
        contexts: 컨텍스트
    '''
    a = {
        'version': VERSION,
        'template': {
            'outputs': [{'listCard': {
                'header': {'title': title},
                'items': [del_empty(asdict(l)) for l in list_items],
                'forwardable': forwardable,
                'buttons': buttons and [del_empty(asdict(b)) for b in buttons]
            }}],
            'quickReplies': (
                q_replies and [del_empty(asdict(q)) for q in q_replies]
            )
        },
        'context': del_empty({
            'values': contexts and [del_empty(asdict(c)) for c in contexts]
        })
    }
    return t_filter(del_empty(a), 'listCard')


def carousel(
    k_type: str,
    templates: list[dict],
    q_replies: list[QReply] | None = None,
    contexts: list[Context] | None = None
) -> dict:
    '''챗봇 템플릿 (캐로셀)

    주어진 인자들을 챗봇 템플릿으로 변환합니다.

    인자:
        k_type: 카카오 챗봇 템플릿 타입
        templates: 카카오 챗봇 템플릿 본문
        q_replies: 카카오 챗봇 바로가기 응답
        contexts: 컨텍스트
    '''
    a = {
        'version': VERSION,
        'template': {
            'outputs': [{'carousel': {
                'type': k_type,
                'items': [
                    t['template']['outputs'][0][k_type] for t in templates
                ],
            }}],
            'quickReplies': (
                q_replies and [del_empty(asdict(q)) for q in q_replies]
            )
        },
        'context': del_empty({
            'values': contexts and [del_empty(asdict(c)) for c in contexts]
        })
    }
    return t_filter(del_empty(a), 'carousel')


def basicCard(
    thumbnail: Thumbnail,
    title: str | None = None,
    description: str | None = None,
    buttons: list[Button] | None = None,
    q_replies: list[QReply] | None = None,
    forwardable: bool = False,
    contexts: list[Context] | None = None
) -> dict:
    '''챗봇 템플릿 (카드)

    주어진 인자들을 챗봇 템플릿으로 변환합니다.

    인자:
        image_url: 이미지 URL
        title: 제목
        description: 설명
        buttons: 버튼
        q_replies: 바로가기 응답
        forwardable: 전달 가능 여부
        contexts: 컨텍스트
    '''
    a = {
        'version': VERSION,
        'template': {
            'outputs': [{'basicCard': {
                'title': title,
                'description': description,
                'thumbnail': thumbnail and del_empty(asdict(thumbnail)),
                'forwardable': forwardable,
                'buttons': buttons and [del_empty(asdict(b)) for b in buttons]
            }}],
            'quickReplies': (
                q_replies and [del_empty(asdict(q)) for q in q_replies]
            )
        },
        'context': del_empty({
            'values': contexts and [del_empty(asdict(c)) for c in contexts]
        })
    }
    return t_filter(del_empty(a), 'basicCard')


def itemCard(
    item_lists: list[ItemList],
    alignment: str | None = None,
    summary: Summary | None = None,
    thumbnail: ICT | None = None,
    head: str | None = None,
    profile: Profile | None = None,
    image_title: ImageTitle | None = None,
    title: str | None = None,
    description: str | None = None,
    q_replies: list[QReply] | None = None,
    buttons: list[Button] | None = None,
    button_layout: str | None = None,
    contexts: list[Context] | None = None
):
    '''챗봇 템플릿 (아이템 카드)

    주어진 인자들을 챗봇 템플릿으로 변환합니다.

    인자:
        item_lists: 아이템 목록 정보
        alignment: 아이템 정렬
        summary: 가격 정보
        thumbnail: 상단 이미지
        head: 헤드 제목
        profile: 프로필
        image_title: 상단 이미지 아래 정보
        title: 제목
        description: 설명
        q_replies: 바로가기 응답
        buttons: 버튼
        button_layout: 버튼 배치
        contexts: 컨텍스트
    '''
    a = {
        'version': VERSION,
        'template': {
            'outputs': [{'itemCard': {
                'thumbnail': thumbnail and del_empty(asdict(thumbnail)),
                'head': head and {'title': head},
                'profile': profile and del_empty(asdict(profile)),
                'imageTitle': image_title and del_empty(asdict(image_title)),
                'itemList': [del_empty(asdict(il)) for il in item_lists],
                'itemListSummary': summary and del_empty(asdict(summary)),
                'title': title,
                'description': description,
                'buttons': buttons and [del_empty(asdict(b)) for b in buttons],
                'buttonLayout': button_layout
            }}],
            'quickReplies': (
                q_replies and [del_empty(asdict(q)) for q in q_replies]
            )
        },
        'context': del_empty({
            'values': contexts and [del_empty(asdict(c)) for c in contexts]
        })
    }
    return t_filter(del_empty(a), 'itemCard')