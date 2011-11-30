# -*- coding:utf-8 -*-
import unittest

from sc.s17.proxy import proxy
from paste.fixture import TestApp

class ProxyTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_paste_website(self):
        app = proxy.make_proxy({},'http://pythonpaste.org')
        app = TestApp(app)
        res = app.get('/')
        self.assertTrue('documentation' in res)

