from dataclasses import asdict, dataclass


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
class ListCardItem:
    '''리스트 카드 아이템

    리스트 카드 템플릿에 들어갈 아이템입니다.

    속성:
        title: 제목
        description: 설명
        imageUrl: 이미지 URL
        link: 링크
        action: 눌렀을 때 수행할 동작, 종류와 설명은 아래 [종류]와 같습니다.
            [종류]
            - 'block': {blockId}를 갖는 블록을 호출합니다.
            - 'message': 사용자의 발화로 {messageText}를 실행합니다.
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


@dataclass
class Profile:
    '''아이템 카드 프로필
    
    아이템 카드 템플릿에 들어갈 프로필입니다.
    
    속성:
        title: 프로필 제목
        imageUrl: 이미지 URL
        width: 가로 크기
        height: 세로 크기
    '''
    title: str
    imageUrl: str = None
    width: int = None
    height: int = None


@dataclass
class ItemCardThumbnail:
    '''아이템 카드 썸네일
    
    아이템 카드 템플릿에 들어갈 썸네일입니다.
    
    속성:
        imageUrl: 이미지 URL
        width: 가로 크기
        height: 세로 크기
    '''
    imageUrl: str
    width: int
    height: int


@dataclass
class ImageTitle:
    '''아이템 카드 이미지
    
    아이템 카드 템플릿에 들어갈 이미지입니다.
    
    속성:
        title: 제목
        description: 설명
        imageUrl: 이미지 URL
    '''
    title: str
    description: str = None
    imageUrl: str = None


@dataclass
class ItemList:
    '''아이템 카드 목록
    
    아이템 카드 템플릿에 들어갈 아이템입니다.
    
    속성:
        title: 제목
        description: 설명
    '''
    title: str
    description: str


@dataclass
class Summary:
    '''아이템 카드 가격
    
    아이템 카드 템플릿에 들어갈 가격입니다.
    
    속성:
        title: 제목
        description: 설명
    '''
    title: str
    description: str


class LCI(ListCardItem):
    ...


class ICT(ItemCardThumbnail):
    ...