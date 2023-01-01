from dataclasses import asdict, dataclass, field

VERSION = '2.0'


@dataclass
class QReply:
    '''바로가기 응답

    챗봇에서 바로가기로 제공되는 응답입니다.

    속성:
        label: 사용자에게 노출될 응답 표시
        action: 눌렀을 때 수행할 동작, 'block' 또는 'message'
        messageText: {action}이 'message'일 경우 사용자의 발화로 내보냅니다.
        blockId: {action}이 'message'일 경우 {blockId}인 블록을 호출합니다.
        extra: 스킬 서버에 추가적으로 제공하는 정보
    '''
    label: str = ''
    action: str = ''
    messageText: str = ''
    blockId: str = ''
    extra: str = ''


@dataclass
class Link:
    '''링크

    챗봇에서 링크로 들어갑니다.
    보이는 우선 순위는 web > pc = mobile입니다.

    속성:
        web: 웹에서 보일 링크
        pc: PC에서 보일 링크
        mobile: 모바일에서 보일 링크
    '''
    web: str = None
    pc: str = None
    mobile: str = None


@dataclass
class ListItem:
    '''챗봇 리스트 아이템

    리스트 카드 템플릿에 들어갈 아이템입니다.

    속성:
        title: 제목
        description: 설명
        imageUrl: 이미지 URL
        link: 링크
        action: 눌렀을 때 수행할 동작, 종류와 설명은 아래 [종류]와 같습니다.
            종류:
                'block': {blockId}를 갖는 블록을 호출합니다.
                'message': 사용자의 발화로 {messageText}를 실행합니다.
        blockId: {action}이 'block'일 경우 호출할 블록 ID
        messageText: {action}이 'message'일 경우 사용자의 발화로 내보낼 텍스트
        extra: 스킬 서버에 추가적으로 제공할 정보
    '''
    title: str
    description: str = ''
    link: Link = None
    imageUrl: str = ''
    action: str = ''
    blockId: str = ''
    messageText: str = ''
    extra: str = None

    def __post_init__(self):
        link = self.link
        self.link = link and del_empty(asdict(link))


@dataclass
class Button:
    '''버튼

    챗봇에서 버튼으로 들어갑니다.

    속성:
        label: 적히는 문구
        action: 눌렀을 때 수행할 동작, 종류와 설명은 아래 [종류]와 같습니다.
            종류:
                'block': {blockID}를 갖는 블록을 호출합니다.
                'message': 사용자의 발화로 {messageText}를 실행합니다.
                'webLink': {webLinkUrl}의 URL로 이동합니다.
                'phone': {phoneNumber}의 전화번호로 전화를 겁니다.
                'share': 말풍선을 다른 사용자에게 공유합니다.
                'operator': 상담직원을 연결합니다.
        webLinkUrl: {action}이 'webLink'일 경우 버튼을 눌렀을 때 이동할 URL
        phoneNumber: {action}이 'phone'일 경우 버튼을 눌렀을 때 전화할 전화번호
        blockId: {action}이 'message'일 경우 {blockId}인 블록을 호출합니다.
        messageText: {action}이 'message', 'block'일 경우 사용자의 발화로 내보낼 텍스트
        extra: 스킬 서버에 추가적으로 제공할 정보
    '''
    label: str
    action: str
    webLinkUrl: str = ''
    messageText: str = ''
    phoneNumber: str = ''
    blockID: str = ''
    extra: str = None


@dataclass
class Thumbnail:
    '''썸네일

    챗봇에서 썸네일로 들어갑니다.

    속성:
        imageUrl: 이미지 URL
        link: 링크
        fixedRatio: 이미지 비율
        width: 가로 크기
        height: 세로 크기
    '''
    imageUrl: str
    link: Link = None
    fixedRatio: bool = None
    width: int = None
    height: int = None

    def __post_init__(self):
        link = self.link
        self.link = link and del_empty(asdict(link))


@dataclass
class Context:
    '''컨텍스트

    속성:
        name: 이름
        lifeSpan: 지속 시간
        params: 데이터
    '''
    name: str
    lifeSpan: int
    params: dict = None


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
    '''챗봇 템플릿에서 빈 내용 지우기
    
    카카오 챗봇 템플릿에서 빈 내용을 지우고 반환합니다.

    인자:
        td: 챗봇 템플릿
        k_type: 챗봇 템플릿의 타입
    '''
    qReplies = td['template'].get('quickReplies')
    home = td['template']['outputs'][0][k_type]
    if not qReplies and type(qReplies) != list:
        del td['template']['quickReplies']
    td['template']['outputs'][0][k_type] = del_empty(home)
    return td


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
    list_items: list[ListItem],
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