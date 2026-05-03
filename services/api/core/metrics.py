"""Lightweight in-memory business metrics.

This module keeps the existing service-level metric API (`inc`, `labels`,
`set`) without relying on external monitoring stacks.
"""

from collections import defaultdict
from threading import Lock


class _CounterHandle:
    """Label-bound counter handle."""

    def __init__(self, counter: "InMemoryCounter", key: tuple[str, ...]):
        self._counter = counter
        self._key = key

    def inc(self, amount: float = 1.0) -> None:
        """Increment the bound counter value."""
        self._counter.inc_for_key(self._key, amount)


class InMemoryCounter:
    """Simple thread-safe counter with optional labels."""

    def __init__(self, label_names: tuple[str, ...] = ()):
        """Initialize counter with an optional tuple of label names."""
        self._label_names = label_names
        self._values: dict[tuple[str, ...], float] = defaultdict(float)
        self._lock = Lock()

    def labels(self, **labels: str) -> _CounterHandle:
        """Return a label-bound counter handle."""
        if set(labels.keys()) != set(self._label_names):
            expected = ", ".join(self._label_names) or "<none>"
            received = ", ".join(sorted(labels.keys())) or "<none>"
            raise ValueError(f"Expected labels [{expected}], received [{received}]")
        key = tuple(str(labels[name]) for name in self._label_names)
        return _CounterHandle(self, key)

    def inc(self, amount: float = 1.0) -> None:
        """Increment the unlabelled counter value."""
        self.inc_for_key((), amount)

    def inc_for_key(self, key: tuple[str, ...], amount: float) -> None:
        """Increment counter for a concrete label key."""
        with self._lock:
            self._values[key] += amount

    def total(self) -> float:
        """Return aggregate counter value across all labels."""
        with self._lock:
            return float(sum(self._values.values()))


class InMemoryGauge:
    """Simple thread-safe gauge."""

    def __init__(self):
        """Initialize gauge with a default value of 0.0."""
        self._value = 0.0
        self._lock = Lock()

    def set(self, value: float) -> None:
        """Set gauge value."""
        with self._lock:
            self._value = float(value)

    def get(self) -> float:
        """Get current gauge value."""
        with self._lock:
            return self._value


EXPENSE_CREATED = InMemoryCounter(("category",))
EXPENSE_DELETED = InMemoryCounter()
LOGIN_SUCCESS = InMemoryCounter()
LOGIN_FAILURE = InMemoryCounter()
BUDGET_EXCEEDED = InMemoryCounter()

ACTIVE_USERS = InMemoryGauge()
