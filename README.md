# timedelta_queues
Simple timedelta-based queues that keep values only if they fit within a particular timedelta-based window from
the most-recently-added value's date attribute.

### TimedeltaQueue
Expects to be fed objects that have some increasing date attribute (retrieved with a provided getter function), and keeps only those
that are within a provided timedelta of the most-recently added item. Note that out-of-order objects are NOT supported
to keep things simple.

### FastWindowedStatsQueue
`FastWindowedStatsQueue` operates on the same idea as a `TimedeltaQueue`, but updates internal state to track the 
queue's mean and standard deviation (in O(n) time or O(1) per insert), retrievable at any time using `FastWindowedStatsQueue.mean` and
`FastWindowedStatsQueue.std`.

### TimedeltaBufferQueue
`TimedeltaBufferQueue` joins both a `TimedeltaQueue` and `FastWindowedStatsQueue` to provide functionality of having
some buffer between when stats are available to be calculated, and when they are processed. This is a common issue 
in timeseries machine learning tasks, where one might need a windowed average and standard deviation over some period
(the queue_delta), but it cannot include values that are within some buffer period (the buffer_delta) to prevent
leaking future values such astarget values/predictions that have yet to occur.

`TimedeltaBufferQueue` will hold values from some period (say one hour) in a buffer queue, and only release them into the statistics queue
once the most recently added value to the `TimedeltaBufferQueue` has a date that exceeds the provided buffer delta.
