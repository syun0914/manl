from dataclasses import asdict, dataclass, field
from sys import _getframe


@dataclass
class QReply:
    messageText: str = ''
    action: str = ''
    label: str = ''
    blockId: str = ''


@dataclass
class KList:
    title: str
    description: str
    imageUrl: str = ''
    link: dict = field(default_factory=dict)


@dataclass
class Button:
    pass


def del_empty(object: dict | list) -> dict | list:
    t = type(object)
    if t == dict:
        return {k: v for k, v in object.items() if v}
    elif t == list:
        return [c for c in object if c]


def t_filter(td: dict, k_type: str) -> dict:
    qReplies = td['template'].get('quickReplies')
    home = td['template']['outputs'][0][k_type]
    if not qReplies and type(qReplies) != list:
        del td['template']['quickReplies']
    td['template']['outputs'][0][k_type] = del_empty(home)
    return td


def data(**x) -> dict:
    '''
    챗봇 템플릿 (데이터)
    -----
    주어진 인자들을 data 챗봇 템플릿으로 변환합니다.
    '''
    return {'version': '2.0', 'data': del_empty(x)}


def simpleImage(
    url: str,
    altText: str | None = None,
    qReplies: list[QReply] | None = None,
    buttons: list[Button] | None = None
) -> dict:
    '''
    챗봇 템플릿 (이미지)
    -----
    주어진 인자들을 simpleImage 챗봇 템플릿으로 변환합니다.
    '''
    a = {
        'version': '2.0',
        'template': {
            'outputs': [{'simpleImage': {
                'imageUrl': url,
                'altText': altText,
                'buttons': buttons and [del_empty(asdict(b)) for b in buttons]
            }}],
            'quickReplies': (
                qReplies and [del_empty(asdict(q)) for q in qReplies]
            )
        }
    }
    
    return t_filter(a, 'simpleImage')


def simpleText(
    text: str,
    qReplies: list[QReply] | None = None,
    buttons: list[Button] | None = None,
    fw: bool = False
) -> dict:
    '''
    챗봇 템플릿 (텍스트)
    -----
    주어진 인자들을 simpleText 챗봇 템플릿으로 변환합니다.
    '''
    a = {
        'version': '2.0',
        'template': {
            'outputs': [{'simpleText': {
                'text': text,
                'forwardable': fw,
                'buttons': buttons and [del_empty(asdict(b)) for b in buttons]
            }}],
            'quickReplies': (
                qReplies and [del_empty(asdict(q)) for q in qReplies]
            )
        }
    }
    return t_filter(a, 'simpleText')


def listCard(
    title: str,
    kLists: list[KList],
    qReplies: list[QReply] | None = None,
    buttons: list[Button] | None = None,
    fw: bool = False
) -> dict:
    '''
    챗봇 템플릿 (리스트 카드)
    -----
    주어진 인자들을 listCard 챗봇 템플릿으로 변환합니다.
    '''
    a = {
        'version': '2.0',
        'template': {
            'outputs': [{'listCard': {
                'header': {'title': title},
                'items': [del_empty(asdict(k)) for k in kLists],
                'forwardable': fw,
                'buttons': buttons and [del_empty(asdict(b)) for b in buttons]
            }}],
            'quickReplies': (
                qReplies and [del_empty(asdict(q)) for q in qReplies]
            )
        }
    }
    return t_filter(a, 'listCard')


def carousel(
    kType: str, templates: list, qReplies: list[QReply] | None = None
) -> dict:
    '''
    챗봇 템플릿 (캐로셀)
    -----
    주어진 인자들을 carousel 챗봇 템플릿으로 변환합니다.
    '''
    a = {
        'version': '2.0',
        'template': {
            'outputs': [{'carousel': {
                'type': kType,
                'items': [
                    t['template']['outputs'][0][kType] for t in templates
                ],
            }}],
            'quickReplies': (
                qReplies and [del_empty(asdict(q)) for q in qReplies]
            )
        }
    }
    return t_filter(a, 'carousel')
