from random import randint


def check(input_: str, answer: str) -> str:
    '''
    숫자야구 정답 확인하기
    -----
    '0S 0B'의 형식으로 정답과 비교한 결과를 반환합니다.
    '''
    strike = 0
    for s1, s2 in zip(input_, answer):
        if s1 == s2:
            strike += 1
    ball = len(set(input_) & set(answer)) - strike
    return f'{strike}S {ball}B' if strike or ball else 'OUT'


def new(i: str | None = None) -> str:
    '''
    숫자야구 정답 생성하기
    -----
    0~9의 중복되지 않는 4자리 숫자를 생성합니다.
    '''
    while not i or len(set(i)) < 4:
        i = str(randint(123, 9876)).zfill(4)
    return i
    