import asyncio
import math

import numpy as np

from datetime import datetime, timedelta
from collections import namedtuple
from unittest import TestCase

from timedelta_queues import FastWindowedStatsQueue


class FastWindowedStatsQueueCases(TestCase):

    def setUp(self):
        self.rng = np.random.default_rng(42)
        self.obj = namedtuple('thing', 'date x')
        self.n = 100_000
        self.objs = [
            self.obj(
                datetime(2021, 1, 1) + timedelta(minutes=1 * x),
                self.rng.integers(-10_000, 10_000)
            )
            for x in range(self.n)
        ]

    def tearDown(self):
        pass

    def test_basic_behavior(self):
        """Identical test as TimedeltaQueue; unmodified to show behavior is identical."""
        date_getter = lambda i: i.date
        attr_getter = lambda i: i.x

        t = FastWindowedStatsQueue(delta=timedelta(minutes=31), date_getter=date_getter, attr_getter=attr_getter)

        for i, obj in enumerate(self.objs):
            evicted = t.append(obj)

            if i < 32:
                self.assertEqual(i + 1, len(t._q))
                self.assertEqual(0, len(evicted))
            else:
                self.assertEqual(32, len(t._q))
                self.assertEqual(1, len(evicted))

        clearing_date = self.objs[-1].date + timedelta(minutes=32)
        new_obj = self.obj(clearing_date, 0)

        # should force evict all others since it's newer than the rest of the q by at least the q's delta
        evicted = t.append(new_obj)
        self.assertEqual(32, len(evicted))
        self.assertEqual(1, len(t._q))

    def test_statistics_behavior(self):
        """Identical test as TimedeltaQueue; unmodified to show behavior is identical."""
        date_getter = lambda i: i.date
        attr_getter = lambda i: i.x

        t = FastWindowedStatsQueue(delta=timedelta(minutes=31), date_getter=date_getter, attr_getter=attr_getter)

        values = np.array([obj.x for obj in self.objs])  # collect all values in np array for convenience

        for i, obj in enumerate(self.objs):
            evicted = t.append(obj)

            if i < 32:
                self.assertEqual(i + 1, len(t._q))
                self.assertEqual(0, len(evicted))
                self.assertTrue(math.isclose(np.mean(values[:i + 1]), t.mean, abs_tol=.00000001))
                self.assertTrue(math.isclose(np.std(values[:i + 1]), t.std, abs_tol=.00000001))

            elif i < self.n - 1:
                self.assertEqual(32, len(t._q))
                self.assertEqual(1, len(evicted))

                self.assertTrue(math.isclose(np.mean(values[i - 31 : i + 1]), t.mean, abs_tol=.00000001))
                self.assertTrue(math.isclose(np.std(values[i - 31 : i + 1]), t.std, abs_tol=.00000001))

            else:
                """Technically, does not test behavior at the very end of queue, which should be no different..."""

        clearing_date = self.objs[-1].date + timedelta(minutes=32)
        new_obj = self.obj(clearing_date, 0)

        # should force evict all others since it's newer than the rest of the q by at least the q's delta
        evicted = t.append(new_obj)
        self.assertEqual(32, len(evicted))
        self.assertEqual(1, len(t._q))
