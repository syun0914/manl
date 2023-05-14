from dataclasses import asdict
from kakao_template.exceptions import (
    LengthError, ExistError
)
from kakao_template.base import (
    del_empty,
    QReply, Button, Context,
    Profile, Thumbnail, ImageTitle, ItemList, Summary,
    CH, LCI, ICT
)

VERSION = '2.0'


def gtem(
    *templates: list[dict],
    q_replies: list[QReply] | None = None,
    contexts: list[Context] | None = None
) -> dict:
    '''챗봇 템플릿 생성
    
    주어진 인자들로 챗봇 템플릿을 생성합니다.
    
    위치 가변 인자:
        templates: 템플릿
    
    인자:
        q_replies: 바로가기 응답
        contexts: 컨텍스트
    '''
    if not 1 <= len(templates) <= 3:
        raise LengthError('템플릿은 1개 이상 3개 이하여야 합니다.')
    return del_empty({
        'version': VERSION,
        'template': {
            'outputs': templates,
            'quickReplies': (
                q_replies and [del_empty(asdict(q)) for q in q_replies]
            )
        },
        'context': del_empty({
            'values': contexts and [del_empty(asdict(c)) for c in contexts]
        })
    })


def data(contexts: list[Context] | None = None, **kwargs) -> dict:
    '''챗봇 템플릿 (데이터)
    
    주어진 인자들을 챗봇 템플릿으로 변환합니다.

    인자:
        contexts: 컨텍스트

    키워드 가변 인자:
        kwargs: 데이터
    '''
    return del_empty({
        'version': VERSION,
        'data': del_empty(kwargs),
        'context': del_empty({
            'values': contexts and [del_empty(asdict(c)) for c in contexts]
        })
    })


def simpleImage(url: str, alt_text: str | None = None) -> dict:
    '''챗봇 템플릿 (이미지)

    주어진 인자들을 챗봇 템플릿으로 변환합니다.

    인자:
        url: 이미지 URL
        alt_text: 대체 텍스트
    '''
    return {'simpleImage': {'imageUrl': url, 'altText': alt_text}}


def simpleText(
    text: str,
    buttons: list[Button] | None = None,
    forwardable: bool = False
) -> dict:
    '''챗봇 템플릿 (텍스트)

    주어진 인자들을 챗봇 템플릿으로 변환합니다.

    인자:
        text: 텍스트
        buttons: 버튼
        forwardable: 전달 가능 여부
    '''
    return {
        'simpleText': del_empty({
            'text': text, 'forwardable': forwardable,
            'buttons': buttons and [del_empty(asdict(b)) for b in buttons]
        })
    }


def listCard(
    title: str,
    items: list[LCI],
    q_replies: list[QReply] | None = None,
    buttons: list[Button] | None = None,
    forwardable: bool = False,
    contexts: list[Context] | None = None
) -> dict:
    '''챗봇 템플릿 (리스트 카드)

    주어진 인자들을 챗봇 템플릿으로 변환합니다.

    인자:
        title: 제목
        items: 아이템, 최대 5개
        buttons: 버튼, 최대 2개
        forwardable: 전달 가능 여부
    
    예외:
        LengthError:
            아이템은 5개 이하여야 합니다.
            버튼은 2개 이하여야 합니다.
    '''
    if len(items) > 5:
        raise LengthError(
            '아이템은 5개 이하여야 합니다.'
        )
    if buttons and len(buttons) > 2:
        raise LengthError(
            '버튼은 2개 이하여야 합니다.'
        )
    return {
        'listCard': del_empty({
            'header': {'title': title},
            'items': [del_empty(asdict(i)) for i in items],
            'forwardable': forwardable,
            'buttons': buttons and [del_empty(asdict(b)) for b in buttons]
        })
    }


def carousel(
    *templates,
    k_type: str,
    q_replies: list[QReply] | None = None,
    header: CH | None = None,
    contexts: list[Context] | None = None
) -> dict:
    '''챗봇 템플릿 (캐로셀)

    주어진 인자들을 챗봇 템플릿으로 변환합니다.
    
    위치 가변 인자:
        templates: 템플릿

    인자:
        k_type: 템플릿 타입
        q_replies: 바로가기 응답
        header: 캐로셀 헤더
        contexts: 컨텍스트
    
    예외:
        ExistError:
            템플릿 타입이 'listCard'일 때, 캐로셀 헤더를 사용할 수 없습니다.
        LengthError:
            템플릿 타입이 'listCard'일 때, 템플릿은 5개 이하여야 합니다.
            템플릿은 10개 이하여야 합니다.
    '''
    if k_type == 'listCard':
        if len(templates) > 5:
            raise LengthError(
                "템플릿 타입이 'listCard'일 때, 템플릿은 5개 이하여야 합니다."
            )
        if header:
            raise ExistError(
                "템플릿 타입이 'listCard'일 때, 캐로셀 헤더를 사용할 수 없습니다."
            )
    elif len(templates) > 10:
        raise LengthError(
            '템플릿은 10개 이하여야 합니다.'
        )
    return {
        'version': VERSION,
        'template': {
            'outputs': [{'carousel': del_empty({
                'type': k_type,
                'items': templates,
                'header': header and del_empty(asdict(header))
            })}],
            'quickReplies': (
                q_replies and [del_empty(asdict(q)) for q in q_replies]
            )
        },
        'context': del_empty({
            'values': contexts and [del_empty(asdict(c)) for c in contexts]
        })
    }


def basicCard(
    thumbnail: Thumbnail,
    title: str | None = None,
    description: str | None = None,
    buttons: list[Button] | None = None,
    forwardable: bool = False
) -> dict:
    '''챗봇 템플릿 (카드)

    주어진 인자들을 챗봇 템플릿으로 변환합니다.

    인자:
        image_url: 이미지 URL
        title: 제목
        description: 설명
        buttons: 버튼
        forwardable: 전달 가능 여부
    '''
    return {
        'basicCard': del_empty({
            'title': title,
            'description': description,
            'thumbnail': thumbnail and del_empty(asdict(thumbnail)),
            'forwardable': forwardable,
            'buttons': buttons and [del_empty(asdict(b)) for b in buttons]
        })
    }


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
    buttons: list[Button] | None = None,
    button_layout: str | None = None
):
    '''챗봇 템플릿 (아이템 카드)

    주어진 인자들을 챗봇 템플릿으로 변환합니다.

    인자:
        item_lists: 아이템 목록
        alignment: 아이템 정렬, 'left' 또는 'right'
        summary: 가격 정보
        thumbnail: 상단 이미지
        head: 헤드 제목
        profile: 프로필
        image_title: 상단 이미지 아래 정보
        title: 제목
        description: 설명
        buttons: 버튼
        button_layout: 버튼 정렬, 종류와 설명은 아래 [종류]와 같습니다.
            [종류]
            - 'vertical': 버튼을 세로로 정렬합니다.
            - 'horizontal': 버튼을 가로로 정렬합니다.
    
    예외:
        ExistError: head, profile을 같이 사용할 수 없습니다.
    
    주의:
        단일형만 button_layout을 사용할 수 있습니다.
    '''
    if head and profile:
        raise ExistError(
            'head, profile을 같이 사용할 수 없습니다.'
        )
    return {
        'itemCard': del_empty({
            'thumbnail': thumbnail and del_empty(asdict(thumbnail)),
            'head': head and {'title': head},
            'profile': profile and del_empty(asdict(profile)),
            'imageTitle': image_title and del_empty(asdict(image_title)),
            'itemList': [del_empty(asdict(il)) for il in item_lists],
            'itemListAlignment': alignment,
            'itemListSummary': summary and del_empty(asdict(summary)),
            'title': title,
            'description': description,
            'buttons': buttons and [del_empty(asdict(b)) for b in buttons],
            'buttonLayout': button_layout
        })
    }