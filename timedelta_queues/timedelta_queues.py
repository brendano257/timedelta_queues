import numpy as np

from typing import Any
from collections import deque
from collections.abc import Callable
from datetime import datetime, timedelta

__all__ = [
    'TimedeltaQueue',
    'FastWindowedStatsQueue',
    'TimedeltaBufferQueue'
]


class TimedeltaQueue:
    """
    A queue that will evict values off the tail as they become older than the most recent date, minus some provided
    delta.
    """

    def __init__(self, delta: timedelta, date_getter: Callable[[Any], datetime]):
        self.delta = delta
        self.date_getter = date_getter
        self._q = deque()  # no maxlen

    def append(self, obj) -> list[Any]:
        """
        Adds an item to this queue, potentially evicting objects that are older than it's date, minus self.delta.

        :param Object obj: an object to append; expects that the provided
        :return: list of any objects evicted from the tail as a result of adding obj
        """
        date = self.date_getter(obj)
        self._q.append(obj)

        evict_date = date - self.delta
        evicted = []

        while self.date_getter(self._q[0]) < evict_date:
            evicted.append(self._q.popleft())

        return evicted

    def __len__(self) -> int:
        return len(self._q)


class FastWindowedStatsQueue(TimedeltaQueue):
    """
    An identical queue to TimedeltaQueue, that maintains internal state to allow retrieving the mean and standard
    deviation of the queue in O(1) time per append or retrieval.
    """

    def __init__(self, delta: timedelta, attr_getter: Callable[[Any], Any], date_getter: Callable[[Any], datetime]):
        super().__init__(delta, date_getter)
        self.attr_getter = attr_getter
        self._n = 0
        self._sum = 0
        self._sum_squares = 0

    @property
    def mean(self) -> float:
        return self._sum / self._n

    @property
    def std(self) -> float:
        return np.sqrt(self._sum_squares / self._n - (self._sum / self._n)**2)

    def append(self, obj: Any) -> list[Any]:
        """
        Adds an item to this queue, potentially evicting objects that are older than it's date, minus self.delta.
        Updates internal state to reflect the new mean and standard deviation of values in the queue after appending
        and evicting any old values.

        :param Object obj: an object to append; expects that the provided
        :return: list of any objects evicted from the tail as a result of adding obj
        """
        self._n += 1
        evicted = super().append(obj)
        self._n -= len(evicted)

        value = self.attr_getter(obj)

        self._sum += value
        self._sum_squares += value**2

        for elem in evicted:
            removed = self.attr_getter(elem)
            self._sum -= removed
            self._sum_squares -= removed**2

        return evicted

    def __len__(self) -> int:
        return self._n


class TimedeltaBufferQueue:
    """
    A combo-queue that holds some timedelta of values in reserve, only adding them to the statistics queue after some
    timedelta condition has been met.
    """

    def __init__(
            self, buffer_delta: timedelta, queue_delta: timedelta, attr_getter: Callable[[Any], Any],
            date_getter: Callable[[Any], datetime]
    ):
        self.buffer_delta = buffer_delta
        self.queue_delta = queue_delta
        self.attr_getter = attr_getter
        self.date_getter = date_getter

        self._buffer = TimedeltaQueue(delta=buffer_delta, date_getter=date_getter)
        self._stats_q = FastWindowedStatsQueue(delta=self.queue_delta, attr_getter=attr_getter, date_getter=date_getter)

    @property
    def mean(self) -> float:
        return self._stats_q.mean

    @property
    def std(self) -> float:
        return self._stats_q.std

    def append(self, obj: Any) -> list[Any]:
        """
        Adds an item to the buffer, potentially forcing values out of the buffer and into the statistics queue (which
        may in turn force items to be evicted from the statistics queue). Items evicted from the statistics queue are
        returned for any additional book-keeping or testing.

        :param Object obj: an object to append; expects that the provided
        :return: list of any objects evicted from the statistics's queue tail as a result of adding obj
        """
        buffer_evicted = self._buffer.append(obj)

        evicted = []
        for elem in buffer_evicted:
            stats_evicted = self._stats_q.append(elem)
            evicted.extend(stats_evicted)

        return evicted

    def __len__(self):
        return NotImplemented  # not fair to ask length of a two-part queue
