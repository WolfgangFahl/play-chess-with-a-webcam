"""
Created on 2019-12-13

@author: wf

Event handling module see https://stackoverflow.com/a/1925836/1497139
"""


class Event(object):
    """an Event"""

    pass


class Observable(object):
    """an Observable"""

    def __init__(self):
        self.callbacks = []

    def subscribe(self, callback):
        self.callbacks.append(callback)

    def unsubscribe(self, callback):
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def fire(self, **attrs):
        e = Event()
        e.source = self
        for k, v in attrs.items():
            setattr(e, k, v)
        for fn in self.callbacks:
            fn(e)
