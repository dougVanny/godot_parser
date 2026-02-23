from random import choice
from string import ascii_lowercase, digits
from typing import Any


class BaseGenerator(object):
    def generate(self, section: Any, index: int):
        return ""


class RandomIdGenerator(BaseGenerator):
    def __init__(self, length: int = 5, pool: str = ascii_lowercase + digits):
        self.length = length
        self.pool = pool

    def generate(self, section: Any, index: int):
        return "%s_%s" % (
            index,
            "".join((choice(self.pool) for _ in range(self.length))),
        )


class SequentialHexGenerator(BaseGenerator):
    def __init__(self):
        self.counter = 0

    def generate(self, section: Any, index: int):
        self.counter += 1
        return "%s_%x" % (index, self.counter)
