Batch-processing and latency
============================

A Twitter keyword search streamer.

    $ python twitter_streaming.py --timeout 30 london paris 'new york' moscow

Components
----------

Decouple processing. Have something like `twthread`, that will take care of
keywords in a streaming manner. This can be totally separate.

Let `twthread` (or any other real-timeish data adapter) write out results in
regular intervals.

    /tmp/twthread/2011-03-02/1405.ldj
    /tmp/twthread/2011-03-02/1410.ldj

Real-time up to 60s.

    /tmp/twthread/2011-03-02/1401.ldj
    /tmp/twthread/2011-03-02/1402.ldj
    /tmp/twthread/2011-03-02/1403.ldj

`twthread` can care care of stream restarts, retries with various policies.

Add redundancy by running `twthread` on `n` machines. Daily, hourly syncs.
