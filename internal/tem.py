from sys import _getframe
from typing import Optional, Union
from dataclasses import field, asdict, dataclass


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


def del_empty(object: Union[dict, list]) -> Union[dict, list]:
    t = type(object)
    if t == dict:
        return {k: v for k, v in object.items() if v}
    elif t == list:
        return [c for c in object if c]


def t_filter(td: dict) -> dict:
    funcName = _getframe(1).f_code.co_name
    qReplies = td['template'].get('quickReplies')
    home = td['template']['outputs'][0][funcName]
    if not qReplies and qReplies != None:
        del td['template']['quickReplies']
    td['template']['outputs'][0][funcName] = del_empty(home)
    return td


def data(**x):
    '''
    주어진 인자들을 data 챗봇 템플릿으로 변환합니다.
    '''
    return {'version': '2.0', 'data': del_empty(x)}


def simpleImage(
    url: str,
    altText: Optional[str]=None,
    qReplies: Optional[list[QReply]]=None,
    buttons: Optional[list[Button]]=None
):
    '''
    주어진 인자들을 simpleImage 챗봇 템플릿으로 변환합니다.
    (조건) qReplies는 qReply, buttons는 button 클래스를 통해 입력해야 합니다.
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
    
    return t_filter(a)


def simpleText(
    text: str,
    qReplies: Optional[list[QReply]]=None,
    buttons: Optional[list[Button]]=None,
    fw: bool=False
):
    '''
    주어진 인자들을 simpleText 챗봇 템플릿으로 변환합니다.
    (조건) qReplies는 qReply, buttons는 button 클래스를 통해 입력해야 합니다.
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
    return t_filter(a)


def listCard(
    title: str,
    kLists: list[KList],
    qReplies: Optional[list[QReply]]=None,
    buttons: Optional[list[Button]]=None,
    fw: bool=False
):
    '''
    주어진 인자들을 listCard 챗봇 템플릿으로 변환합니다.
    (조건) qReplies는 qReply, buttons는 button 클래스를 통해 입력해야 합니다.
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
    return t_filter(a)


def carousel(
    kType: str, templates: list, qReplies: Optional[list[QReply]]=None
):
    '''
    주어진 인자들을 carousel 챗봇 템플릿으로 변환합니다.
    (조건) templates는 이 모듈의 다른 함수들을,
           qReplies는 qReply, buttons는 button 클래스를 통해 입력해야 합니다.
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
    return t_filter(a)
