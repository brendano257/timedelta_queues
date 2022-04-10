import asyncio
import math

import numpy as np

from datetime import datetime, timedelta
from collections import namedtuple
from unittest import TestCase

from timedelta_queues import TimedeltaBufferQueue


class TimedeltaBufferQueueCases(TestCase):

    def setUp(self):
        self.rng = np.random.default_rng(42)
        self.obj = namedtuple('thing', 'date x')
        self.n = 100_000
        self.objs = [
            self.obj(
                datetime(2021, 1, 1) + timedelta(minutes=1 * x),
                self.rng.integers(-100_000, 100_000)
            )
            for x in range(self.n)
        ]

    def tearDown(self):
        pass

    def test_statistics_behavior(self):
        """Identical test as TimedeltaQueue; unmodified to show behavior is identical."""
        date_getter = lambda i: i.date
        attr_getter = lambda i: i.x

        values = np.array([obj.x for obj in self.objs])  # collect all values in np array for convenience

        tdbq = TimedeltaBufferQueue(
            buffer_delta=timedelta(minutes=10),
            queue_delta=timedelta(minutes=31),
            date_getter=date_getter,
            attr_getter=attr_getter
        )

        for i, obj in enumerate(self.objs):
            evicted = tdbq.append(obj)

            if i < 11:
                self.assertEqual(0, len(tdbq._stats_q))
                self.assertEqual(i + 1, len(tdbq._buffer))
                self.assertEqual(0, len(evicted))
            else:
                self.assertEqual(min(32, (i - 10)), len(tdbq._stats_q))
                self.assertEqual(11, len(tdbq._buffer))

                if i > 42:  # one should get evicted for every minute added after the first 11 in the buffer and 31 in the stats q
                    self.assertEqual(1, len(evicted))
                else:
                    self.assertEqual(0, len(evicted))

                q_start = max(0, i - 42)
                q_end = min(i - 10, self.n)

                self.assertTrue(math.isclose(np.mean(values[q_start: q_end]), tdbq.mean, abs_tol=.00000001))
                self.assertTrue(math.isclose(np.std(values[q_start: q_end]), tdbq.std, abs_tol=.00000001))
