#!/usr/bin/env python2
# coding: utf-8

"""
Adapted from: http://adilmoujahid.com/posts/2014/07/twitter-analytics/

Query with a timeout (defaults to 60s) and some keywords:

    $ python twitter_streaming.py --timeout 30 london paris 'new york' moscow

"""

from __future__ import print_function, unicode_literals
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
import argparse
import os
import signal
import sys
import time

class Shutdown(Exception):
    """ To distinguish between errors and regular shutdowns. """
    pass

# cf. http://git.io/vYuI5
access_token = unicode(os.environ.get('TWITTER_ACCESS_TOKEN'))
access_token_secret = unicode(os.environ.get('TWITTER_ACCESS_TOKEN_SECRET'))
consumer_key = unicode(os.environ.get('TWITTER_CONSUMER_KEY'))
consumer_secret = unicode(os.environ.get('TWITTER_CONSUMER_SECRET'))

should_shutdown = False

class timeout:
    def __init__(self, seconds=60, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message
    def handle_timeout(self, signum, frame):
        """
        To give busy streams a window to gracefully write their data out, 
        set global `should_shutdown` and wait a seconds before raising Shutdown.
        """
        global should_shutdown
        should_shutdown = True
        time.sleep(1)
        raise Shutdown
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)
    def __exit__(self, type, value, traceback):
        signal.alarm(0)

class StdOutListener(StreamListener):
    """
    This is a basic listener that just prints received tweets to stdout.
    """
    def on_data(self, data):
        if should_shutdown:
            raise Shutdown()
        sys.stdout.write(data)
        sys.stdout.flush()
        return True

    def on_error(self, status):
        print(status, file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-t', '--timeout', metavar='TIMEOUT', default=60, type=int)
    parser.add_argument('keywords', metavar='KEYWORD', nargs='+')

    args = parser.parse_args()

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    listener = StdOutListener()
    stream = Stream(auth, listener)

    try:
        with timeout(seconds=args.timeout):
            stream.filter(track=args.keywords)
    except Shutdown:
        sys.exit(0)
    except Exception as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
