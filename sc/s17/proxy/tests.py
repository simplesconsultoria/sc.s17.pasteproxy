# -*- coding:utf-8 -*-
# Parts of this are
# (c) 2005 Clark C. Evans

import time
import unittest

from paste import httpserver
from paste.fixture import TestApp

from sc.s17.proxy import proxy


class WSGIRegressionServer(httpserver.WSGIServer):
    """
    A threaded WSGIServer for use in regression testing.  To use this
    module, call serve(application, regression=True), and then call
    server.accept() to let it handle one request.  When finished, use
    server.stop() to shutdown the server. Note that all pending requests
    are processed before the server shuts down.
    """
    defaulttimeout = 10

    def __init__(self, *args, **kwargs):
        httpserver.WSGIServer.__init__(self, *args, **kwargs)
        self.stopping = []
        self.pending = []
        self.timeout = self.defaulttimeout
        # this is a local connection, be quick
        self.socket.settimeout(2)

    def serve_forever(self):
        from threading import Thread
        thread = Thread(target=self.serve_pending)
        thread.start()

    def reset_expires(self):
        if self.timeout:
            self.expires = time.time() + self.timeout

    def close_request(self, *args, **kwargs):
        httpserver.WSGIServer.close_request(self, *args, **kwargs)
        self.pending.pop()
        self.reset_expires()

    def serve_pending(self):
        self.reset_expires()
        while not self.stopping or self.pending:
            now = time.time()
            if now > self.expires and self.timeout:
                # note regression test doesn't handle exceptions in
                # threads very well; so we just print and exit
                print "\nWARNING: WSGIRegressionServer timeout exceeded\n"
                break
            if self.pending:
                self.handle_request()
            time.sleep(.1)

    def stop(self):
        """ stop the server (called from tester's thread) """
        self.stopping.append(True)

    def accept(self, count = 1):
        """ accept another request (called from tester's thread) """
        assert not self.stopping
        [self.pending.append(True) for x in range(count)]


def serve(application, host=None, port=None, handler=None):
    server = WSGIRegressionServer(application,
                                  (host, port),
                                  httpserver.WSGIHandler)
    server.serve_forever()
    return server


class ProxyTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_paste_website(self):
        app = proxy.make_proxy({}, 'http://pythonpaste.org')
        app = TestApp(app)
        res = app.get('/')
        self.assertTrue('documentation' in res)
