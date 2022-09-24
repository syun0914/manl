from random import randint


def check(input_: str, answer: str) -> str:
    strike = 0
    for s1, s2 in zip(input_, answer):
        if s1 == s2:
            strike += 1
    ball = len(set(input_) & set(answer)) - strike
    return f'{strike}S {ball}B' if strike or ball else 'OUT'


def new(i: str | None = None) -> str:
    while not i or len(set(i)) < 4:
        i = str(randint(123, 9876)).zfill(4)
    return i
    