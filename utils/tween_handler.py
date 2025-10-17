from __future__ import annotations
import typing
import uuid
import math

TWEENS: dict[str, Tween] = {}
LOOPS: dict[str, Loop] = {}

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

def elastic(v: float):
    decay = 6.0
    frequency = 6.5
    # pick so that math.cos(f*pi*t) = 0
    return 1 - math.exp(decay * -v) * math.cos(frequency * math.pi * v)

EASE_STYLE: dict[str, typing.Callable[[float], float]] = {
    'linear': linear,
    'ease_in_quad': ease_in_quad,
    'ease_out_quad': ease_out_quad,
    'ease_in_out_quad': ease_in_out_quad,
    'bounce': ease_out_bounce,
    'elastic': elastic
}

class Tween:
    """
    Tween class allowing you to tween value A->B
    """
    def __init__(self, time: float, target: float, initial: float, easeStyle: str = 'linear', callback: typing.Union[typing.Callable[[float]], None] = None):
        self.Value = initial
        self.A = initial
        self.B = target
        self.Time = 0.0
        self.Delay = time
        self.Alpha = 0.0
        self.EaseStyle = easeStyle
        self.Callback = callback
        self.Active = True

        self.Index = str(uuid.uuid4())
        TWEENS[self.Index] = self

    def get_now(self) -> typing.Any:
        """
        Gets the current value.
        """
        alpha = self.Alpha
        if self.EaseStyle in EASE_STYLE:
            alpha = EASE_STYLE[self.EaseStyle](alpha)
        return self.A+((self.B-self.A)*alpha)
    
    def kill(self):
        self.Active = False
    
class TweenTuple(Tween):
    def __init__(self, time: float, target: list[float], initial: list[float], easeStyle: str = 'linear', callback: typing.Union[typing.Callable[[float]], None] = None) -> None:
        super().__init__(time, 0, 0, easeStyle, callback)
        self.A = initial
        self.B = target 
    
    def get_now(self):
        """
        Gets the current value.
        """
        alpha = self.Alpha
        if self.EaseStyle in EASE_STYLE:
            alpha = EASE_STYLE[self.EaseStyle](alpha)
        RESULT = []
        for i, v in enumerate(self.A):
            A, B = v, self.B[i]
            RESULT.append(A+((B-A)*alpha))

        return tuple(RESULT)
    
class Loop:
    """
    Loop class allowing you to have a callback every n float.
    """
    def __init__(self, time: float, callback: typing.Union[typing.Callable[[int]], None] = None, timeout: typing.Union[float, None] = None) -> None:
        self.Time = 0.0
        self.Count = 0
        self.Delay = time
        self.Callback = callback
        self.Timeout = timeout
        self.Active = True

        self.Index = str(uuid.uuid4())
        LOOPS[self.Index] = self

    def kill(self):
        self.Active = False

def update_all(dt: float):
    del_list = []
    for self in TWEENS.values():
        self.Time += dt
        self.Alpha = 1 if self.Delay <= 0 else min(self.Time/self.Delay, 1)

        if (self.Alpha >= 1) or not self.Active:
            del_list.append(self.Index)
            continue

        if self.Callback:
            try:
                self.Callback(self.get_now())
            except Exception as e:
                print(f'error at tween {e}')
                continue
    for v in del_list:
        del TWEENS[v]

    del_list = []
    for self in LOOPS.values():
        self.Time += dt
        if (self.Timeout and self.Time >= self.Timeout) or not self.Active:
            del_list.append(self.Index)
            continue
        if self.Time >= (self.Count*self.Delay):
            self.Count += 1
            if self.Callback:
                try:
                    self.Callback(self.Count)
                except Exception as e:
                    print(f'error at loop {e}')
                    continue
    for v in del_list:
        del LOOPS[v]
