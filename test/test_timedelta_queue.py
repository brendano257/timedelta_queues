import asyncio

from datetime import datetime, timedelta
from collections import namedtuple
from unittest import TestCase

from timedelta_queues import TimedeltaQueue


class TimedeltaQueueCases(TestCase):

    def setUp(self):
        self.obj = namedtuple('thing', 'date x')
        self.objs = [self.obj(datetime(2021, 1, 1) + timedelta(minutes=1 * x), x) for x in range(1000)]

    def tearDown(self):
        pass

    def test_basic_behavior(self):
        date_getter = lambda i: i.date

        t = TimedeltaQueue(delta=timedelta(minutes=31), date_getter=date_getter)

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
