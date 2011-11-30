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
        self.setUpServer()

    def setUpServer(self):

        def my_wsgi_app(environ, start_response):
            start_response('200 OK', [('content-type', 'text/html')])
            if environ.get('HTTP_X_REMOTE_USER', '') == 'FooBar':
                return 'User FooBar'
            return 'Just Foo'

        server = serve(my_wsgi_app, host='127.0.0.1', port=9876)
        self.server = server

    def tearDown(self):
        self.server.stop()
        time.sleep(.5)
        del(self.server)

    def test_proxy_no_header(self):
        app = proxy.make_proxy({},
                               'http://localhost:9876',
                               remote_user_header="HTTP_X_REMOTE_USER")
        app = TestApp(app)
        self.server.accept(1)
        res = app.get('/')
        self.assertTrue('Just Foo' in res)

    def test_paste_with_remote_user(self):
        app = proxy.make_proxy({},
                               'http://localhost:9876',
                               remote_user_header="HTTP_X_REMOTE_USER")
        app = TestApp(app)
        self.server.accept(1)
        res = app.get('/', extra_environ={'REMOTE_USER': 'FooBar'})
        self.assertTrue('User FooBar' in res)
