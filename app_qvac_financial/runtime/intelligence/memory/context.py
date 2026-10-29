"""Small, deterministic context window; no secrets or private keys permitted."""
from collections import deque

class SessionContext:
    def __init__(self, max_items=20):
        if not 1 <= max_items <= 100: raise ValueError("Invalid context size")
        self._items=deque(maxlen=max_items)

    def add_public_note(self, text):
        if not isinstance(text,str) or len(text)>4000: raise ValueError("Invalid note")
        self._items.append(text)

    def snapshot(self): return tuple(self._items)
