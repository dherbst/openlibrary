"""http server for testing.

    >>> server = HTTPServer(port=8090)
    >>> server.request('/hello/world', method='GET').should_return('hello, world!', headers={'content-type': 'text/plain'})

    >>> response = requests.get('http://0.0.0.0:8090/hello/world')
    >>> response.text()
    'hello, world!'
    >>> response.headers['Content-Type']
    'text/plain'

    >>> server.stop()
    >>> requests.get('http://0.0.0.0:8090/hello/world')
    Traceback (most recent call last):
    ...
    IOError: [Errno socket error] (61, 'Connection refused')
"""
from cheroot.wsgi import Server as CherryPyWSGIServer
import requests  # for doctest
import threading
import time
from urllib.parse import urlencode


class HTTPServer:
    def __init__(self, port=8090):
        self.mappings = {}
        self.port = port
        self.server = CherryPyWSGIServer(("0.0.0.0", port), self, server_name="localhost")
        self.started = False
        self.t = threading.Thread(target=self._start)
        self.t.start()
        time.sleep(0.1)

    def _start(self):
        try:
            self.server.start()
        except Exception as e:
            print('ERROR: failed to start server', str(e))

    def stop(self):
        self.server.stop()
        self.t.join()

    def request(self, path, method='GET', query=None):
        query = query or {}
        response = Respose()

        if isinstance(query, dict):
            query = urlencode(query)

        self.mappings[path, method, query] = response
        return response

    def __call__(self, environ, start_response):
        _method = environ.get('REQUEST_METHOD', 'GET')
        _path = environ.get('PATH_INFO')

        for (path, method, query_string), response in self.mappings.items():
            if _path == path and _method == method:
                return response(start_response)

        return Respose()(start_response)


class Respose:
    def __init__(self):
        self.status = '404 Not Found'
        self.data = "not found"
        self.headers = {}

    def should_return(self, data, status="200 OK", headers=None):
        headers = headers or {}
        self.status = status
        self.data = data
        self.headers = headers

    def __call__(self, start_response):
        start_response(self.status, self.headers.items())
        return self.data


if __name__ == "__main__":
    import doctest
    doctest.testmod()
