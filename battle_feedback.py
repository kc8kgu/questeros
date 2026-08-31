"""Presentation timing for short battle hit effects."""
from dataclasses import dataclass

HIT_DURATION = 0.32
TARGETS = ("player", "monster")


@dataclass(frozen=True)
class HitEvent:
    target: str
    damage: int
    slash: bool = False

    def __post_init__(self):
        if self.target not in TARGETS:
            raise ValueError(f"Unknown hit target: {self.target!r}")
        if self.damage < 1:
            raise ValueError("Hit damage must be positive")


class BattleFeedback:
    def __init__(self):
        self.events = []
        self.elapsed = 0.0

    @property
    def active(self):
        return bool(self.events)

    @property
    def current(self):
        return self.events[0] if self.events else None

    @property
    def progress(self):
        if not self.active:
            return 0.0
        return min(1.0, self.elapsed / HIT_DURATION)

    def start(self, events):
        events = list(events)
        if not all(isinstance(event, HitEvent) for event in events):
            raise TypeError("Battle feedback requires HitEvent values")
        self.events = events
        self.elapsed = 0.0

    def update(self, dt):
        if dt < 0:
            raise ValueError("Feedback time cannot move backwards")
        while self.events and dt:
            remaining = HIT_DURATION - self.elapsed
            if dt < remaining:
                self.elapsed += dt
                break
            dt -= remaining
            self.events.pop(0)
            self.elapsed = 0.0
