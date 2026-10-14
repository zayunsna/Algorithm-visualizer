"""Reversible events. Algorithm modules have no dependency on the renderer."""
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Iterator
from enum import Enum


class Removal(Enum):
    KEY = 'remove'


DELETE = Removal.KEY


@dataclass
class Event:
    action: str
    message: str
    changes: dict[tuple, Any]


def event(action, message, **values):
    return Event(action, message, {(key,): value for key, value in values.items()})


class Timeline:
    def __init__(self, source: Iterator[Event]):
        self.source = iter(source)
        self.events = []
        self.undo = []
        self.state = {}
        self.cursor = 0
        self.exhausted = False

    @property
    def message(self):
        return self.events[self.cursor - 1].message if self.cursor else "Ready"

    def forward(self):
        if self.cursor == len(self.events):
            if self.exhausted:
                return False
            try:
                self.events.append(deepcopy(next(self.source)))
            except StopIteration:
                self.exhausted = True
                return False
        current = self.events[self.cursor]
        old = []
        for path, value in current.changes.items():
            target = self.state
            for part in path[:-1]:
                target = target[part]
            key = path[-1]
            old.append((path, key in target, deepcopy(target.get(key))))
            if value is DELETE:
                target.pop(key, None)
            else:
                target[key] = deepcopy(value)
        if self.cursor == len(self.undo):
            self.undo.append(old)
        self.cursor += 1
        return True

    def back(self):
        if not self.cursor:
            return False
        for path, existed, value in reversed(self.undo[self.cursor - 1]):
            target = self.state
            for part in path[:-1]:
                target = target[part]
            if existed:
                target[path[-1]] = deepcopy(value)
            else:
                target.pop(path[-1], None)
        self.cursor -= 1
        return True

    def rewind(self):
        while self.back():
            pass

    def finish(self):
        while self.forward():
            pass
        return self.state
