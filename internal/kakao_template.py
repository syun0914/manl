from dataclasses import asdict, dataclass, field

VERSION = '2.0'


@dataclass
class QReply:
    '''카카오 챗봇 바로가기 응답

    카카오 챗봇에서 바로가기로 제공되는 응답입니다.

    속성:
        label: 사용자에게 노출될 응답 표시
        action: 눌렀을 때 수행할 동작, 'block' 또는 'message'
        messageText: action == 'message'일 경우 사용자의 발화로 내보냅니다.
        blockId: action == 'message'일 경우 {blockId}인 블록을 호출합니다.
        extra: 스킬 서버에 추가적으로 제공하는 정보
    '''
    label: str = ''
    action: str = ''
    messageText: str = ''
    blockId: str = ''
    extra: str = ''


@dataclass
class ListItem:
    '''카카오 챗봇 리스트 아이템

    카카오 리스트 카드 템플릿에 들어갈 아이템입니다.

    속성:
        title: 제목
        description: 설명
        imageUrl: 이미지 URL
        link: 연결 링크, 보이는 우선 순위는 pc = mobile < web입니다.
            pc: PC에서 보일 링크
            mobile: 모바일에서 보일 링크
            web: 웹에서 보일 링크
        action: 눌렀을 때 수행할 동작, 'block' 또는 'message'입니다.
        blockId: action == 'message'일 경우 {blockId}인 블록을 호출합니다.
        messageText: action == 'message'일 경우 사용자의 발화로 내보냅니다.
        extra: 스킬 서버에 추가적으로 제공할 정보
    '''
    title: str
    description: str = ''
    imageUrl: str = ''
    link: dict = field(default_factory=dict)
    action: str = ''
    blockId: str = ''
    messageText: str = ''
    extra: str = None


@dataclass
class Button:
    pass


def del_empty(object: dict | list) -> dict | list:
    '''{object}에서 빈 내용 지우기
    
    {object}에서 False인 내용을 지우고 반환합니다.

    인자:
        object: 딕셔너리나 리스트
    
    예외:
        TypeError: object는 딕셔너리나 리스트여야 합니다.
    '''
    t = type(object)
    if t == dict:
        return {k: v for k, v in object.items() if v}
    elif t == list:
        return [c for c in object if c]
    else:
        raise TypeError('object는 딕셔너리나 리스트여야 합니다.')

def t_filter(td: dict, k_type: str) -> dict:
    '''카카오 챗봇 템플릿에서 빈 내용 지우기
    
    카카오 챗봇 템플릿에서 빈 내용을 지우고 반환합니다.

    인자:
        td: 카카오 챗봇 템플릿
        k_type: 카카오 챗봇 템플릿의 타입
    '''
    qReplies = td['template'].get('quickReplies')
    home = td['template']['outputs'][0][k_type]
    if not qReplies and type(qReplies) != list:
        del td['template']['quickReplies']
    td['template']['outputs'][0][k_type] = del_empty(home)
    return td


def data(**kwargs) -> dict:
    '''카카오 챗봇 템플릿 (데이터)
    
    주어진 인자들을 data 챗봇 템플릿으로 변환합니다.

    키워드 인자:
        kwargs: 데이터
    '''
    return {'version': VERSION, 'data': del_empty(kwargs)}


def simpleImage(
    url: str,
    alt_text: str | None = None,
    q_replies: list[QReply] | None = None,
    buttons: list[Button] | None = None
) -> dict:
    '''카카오 챗봇 템플릿 (이미지)

    주어진 인자들을 simpleImage 챗봇 템플릿으로 변환합니다.

    인자:
        url: 이미지 URL
        alt_text: 대체 텍스트
        q_replies: 바로가기 응답
        buttons: 버튼
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
        }
    }
    
    return t_filter(a, 'simpleImage')


def simpleText(
    text: str,
    q_replies: list[QReply] | None = None,
    buttons: list[Button] | None = None,
    forwardable: bool = False
) -> dict:
    '''카카오 챗봇 템플릿 (텍스트)

    주어진 인자들을 simpleText 챗봇 템플릿으로 변환합니다.

    인자:
        text: 텍스트
        q_replies: 바로가기 응답
        buttons: 버튼
        forwardable: 전달 가능 여부
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
        }
    }
    return t_filter(a, 'simpleText')


def listCard(
    title: str,
    list_items: list[ListItem],
    q_replies: list[QReply] | None = None,
    buttons: list[Button] | None = None,
    forwardable: bool = False
) -> dict:
    '''카카오 챗봇 템플릿 (리스트 카드)

    주어진 인자들을 listCard 챗봇 템플릿으로 변환합니다.

    인자:
        title: 제목
        kLists: 카카오 리스트
        q_replies: 바로가기 응답
        buttons: 버튼
        forwardable: 전달 가능 여부
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
        }
    }
    return t_filter(a, 'listCard')


def carousel(
    k_type: str, templates: list[dict], q_replies: list[QReply] | None = None
) -> dict:
    '''카카오 챗봇 템플릿 (캐로셀)

    주어진 인자들을 carousel 챗봇 템플릿으로 변환합니다.

    인자:
        k_type: 카카오 챗봇 템플릿 타입
        templates: 카카오 챗봇 템플릿 본문
        q_replies: 카카오 챗봇 바로가기 응답
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
        }
    }
    return t_filter(a, 'carousel')
