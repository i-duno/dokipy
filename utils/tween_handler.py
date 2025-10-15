from __future__ import annotations
import typing
import uuid

TWEENS: dict[str, Tween] = {}

def ease_out_bounce(v: float) -> float: #thx chatgpt for this
    n1 = 7.5625
    d1 = 2.75

    if v < 1 / d1:
        return n1 * v * v
    elif v < 2 / d1:
        v -= 1.5 / d1
        return n1 * v * v + 0.75
    elif v < 2.5 / d1:
        v -= 2.25 / d1
        return n1 * v * v + 0.9375
    else:
        v -= 2.625 / d1
        return n1 * v * v + 0.984375

def ease_in_out_quad(v: float) -> float:
    if v < 0.5:
        return 2 * v * v
    else:
        return 1 - pow(-2 * v + 2, 2) / 2

def ease_out_quad(v: float) -> float:
    return 1 - (1 - v) * (1 - v)

def ease_in_quad(v: float):
    return v * v

def linear(v: float):
    return v

EASE_STYLE: dict[str, typing.Callable[[float], float]] = {
    'linear': linear,
    'ease_in_quad': ease_in_quad,
    'ease_out_quad': ease_out_quad,
    'ease_in_out_quad': ease_in_out_quad,
    'bounce': ease_out_bounce
}

class Tween:
    def __init__(self, time: float, target: int, initial: int, easeStyle: str = 'linear', callback: typing.Union[typing.Callable[[float]], None] = None) -> None:
        self.Value = initial
        self.A = initial
        self.B = target
        self.Time = 0.0
        self.Delay = time
        self.Alpha = 0.0
        self.EaseStyle = easeStyle
        self.Callback = callback

        self.Index = str(uuid.uuid4())
        TWEENS[self.Index] = self

    def get_now(self):
        alpha = self.Alpha
        if self.EaseStyle in EASE_STYLE:
            alpha = EASE_STYLE[self.EaseStyle](alpha)
        return self.A+((self.B-self.A)*alpha)

def update_all(dt: float):
    del_list = []
    for self in TWEENS.values():
        self.Time += dt
        self.Alpha = min(self.Time/self.Delay, 1)

        if self.Alpha >= 1:
            del_list.append(self.Index)

        if self.Callback:
            try:
                self.Callback(self.get_now())
            except Exception as e:
                print(f'error at tween {e}')
                continue
    for v in del_list:
        del TWEENS[v]