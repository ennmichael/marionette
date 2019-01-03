from __future__ import annotations

from typing import NamedTuple

from engine.sdl import get_current_time


class Time(NamedTuple):
    current: int
    delta: int

    @staticmethod
    def now() -> Time:
        return Time(current=get_current_time(), delta=0)

    def updated(self) -> Time:
        current_time = get_current_time()
        return Time(current=current_time, delta=current_time - self.current)
