# -*- coding:utf-8 -*-

from paste import proxy
from paste.util.converters import aslist

class Proxy(proxy.Proxy):

    def __init__(self, address, **kwargs):
        self.remote_user_header = kwargs['remote_user_header']
        del(kwargs['remote_user_header'])
        super(Proxy, self).__init__(address, **kwargs)

    def __call__(self, environ, start_response):
        # If we have a REMOTE_USER, we pass that to the backend
        if 'REMOTE_USER' in environ and environ['REMOTE_USER']:
            environ[self.remote_user_header] = environ['REMOTE_USER'] 
        return super(Proxy, self).__call__(environ, start_response)

def make_proxy(global_conf,
               address, allowed_request_methods="",
               suppress_http_headers="",
               remote_user_header="HTTP_X_REMOTE_USER"):
    """
    Make a WSGI application that proxies to another address:
    
    ``address``
        the full URL ending with a trailing ``/``
        
    ``allowed_request_methods``:
        a space seperated list of request methods (e.g., ``GET POST``)
        
    ``suppress_http_headers``
        a space seperated list of http headers (lower case, without
        the leading ``http_``) that should not be passed on to target
        host
    ``remote_user_header``
        the name of the header to be passed to the backend. defaulf: 
        ``HTTP_X_REMOTE_USER``
    """
    allowed_request_methods = aslist(allowed_request_methods)
    suppress_http_headers = aslist(suppress_http_headers)
    return Proxy(
        address,
        allowed_request_methods=allowed_request_methods,
        suppress_http_headers=suppress_http_headers,
        remote_user_header=remote_user_header)
