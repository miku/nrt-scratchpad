#!/usr/bin/env python2
# coding: utf-8

"""
Environment variables:

    # where to store data artifacts,
    # defaults to os.path.join(tempfile.gettempdir(), 'artifacts')
    NRT_SCRATCHPAD_BASE=/path/to/dir

    # duration of one stream or interval between streams
    NRT_SCRATCHPAD_INTERVAL=60

"""

from gluish.task import BaseTask
from gluish.utils import shellout
import datetime
import luigi
import os
import tempfile

BASE = os.environ.get('NRT_SCRATCHPAD_BASE', os.path.join(tempfile.gettempdir(), 'artifacts'))
INTERVAL = os.environ.get('NRT_SCRATCHPAD_INTERVAL', 60)

def every(seconds=10):
    """
    Map current date into `seconds` long bins.
    """
    now = datetime.datetime.now()
    daystart = datetime.datetime(now.year, now.month, now.day)
    offset = (now - daystart).seconds // seconds * seconds
    return daystart + datetime.timedelta(seconds=offset)

class Task(BaseTask):
    """
    BASE is the directory, where data artifacts will be stored.
    """
    BASE = os.environ.get('NRT_SCRATCHPAD_BASE', os.path.join(tempfile.gettempdir(), 'artifacts'))

class TwitterQuery(Task):
    """
    Query twitter for one or more keywords. Run with:

        $ python main.go TwitterQuery --kw "New York" --kw "Berlin" --kw "Moscow"

    """
    indicator = luigi.Parameter(default=every(seconds=INTERVAL).strftime("%s"))
    kw = luigi.Parameter(is_list=True)

    def run(self):
        keywords = " ".join(['"%s"' % kw for kw in self.kw])
        output = shellout("twitter_streaming.py -t {interval} {keywords} > {output}", keywords=keywords, interval=INTERVAL)
        luigi.File(output).move(self.output().path)

    def output(self):
        return luigi.LocalTarget(path=self.path(digest=True))

if __name__ == '__main__':
    luigi.run()
