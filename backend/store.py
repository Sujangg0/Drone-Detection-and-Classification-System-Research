from collections import deque
import time

class InMemoryStore:
    def __init__(self, max_events=500):
        self.latest = None
        self.events = deque(maxlen=max_events)
        self.running = False

    def set_latest(self, obj):
        self.latest = obj

    def add_event(self, evt):
        self.events.appendleft(evt)

    def get_latest(self):
        return self.latest

    def get_events(self, limit=50):
        return list(self.events)[:limit]

STORE = InMemoryStore()
