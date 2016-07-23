import json


class HeaderInfo(object):
    '''
    File name: head_info.py
    Author: Chenglong Wei, chwei@linkedin.com, weichenglong@gmail.com
    Date created: 6/28/2016
    Python Version: 2.6.6
    Functions: Wrapped header information.
    '''

    def __init__(self, js=None, state_machine_id=None, hook_id=None, plugin_name=None, timestamps=None, tag=None,
                 sequence=None, client_request=None, server_request=None, server_response=None, client_response=None):
        if js is not None:
            # If strict is False (True is the default), the control characters ('\t', '\n', '\r', '\0')
            # will be allowed inside the strings.
            self.__dict__ = json.loads(js, strict=False)
            return

        self.state_machine_id = state_machine_id
        self.hook_id = hook_id
        self.plugin_name = plugin_name
        self.timestamps = timestamps
        self.tag = tag
        self.sequence = sequence

        self.client_request = client_request
        self.server_request = server_request
        self.server_response = server_response
        self.client_response = client_response

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

if __name__ == '__main__':
    header_info1 = HeaderInfo(hook_id="TS_HTTP_SEND_RESPONSE_HDR_HOOK")
    print (header_info1.to_json())
    print header_info1.to_json()

    header_info2 = HeaderInfo(js='{"hook_id" : "TS_HTTP_SEND_RESPONSE_HDR_HOOK", "timestamps": 123456}')
    print (header_info2.to_json())

    header_info3 = HeaderInfo(js='''{"hook_id" : "TS_HTTP_SEND_RESPONSE_HDR_HOOK", "timestamps" : 1467230796, "tag" :
    "After Plugin", "client_request" : "GET http://127.0.0.1:8080/?abcd=abcd,efgh&dddd=xxxxx/ HTTP/1.1
    Host: 127.0.0.1:8080
    Connection: keep-alive
    Cache-Control: max-age=0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36
    Accept-Encoding: gzip
    Accept-Language: en-US,en;q=0.8
    X-Important-1: 1
    Y-Important-1: 1
    X-Important-2: 2
    Y-Important-2: 2

    ", "server_request" : "GET /?abcd=abcd,efgh&dddd=xxxxx/ HTTP/1.1
    Host: 127.0.0.1:8080
    Cache-Control: max-age=0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36
    Accept-Encoding: gzip
    Accept-Language: en-US,en;q=0.8
    X-Important-1: 1
    Y-Important-1: 1
    X-Important-2: 2
    Y-Important-2: 2
    Client-ip: 127.0.0.1
    X-Forwarded-For: 127.0.0.1
    Via: http/1.1 chwei-ld1[26200119500022C190FFC7C8A65022BB] (ApacheTrafficServer/7.0.0)
    X-Important-4: 4
    Y-Important-4: 4

    ", "server_response" : "HTTP/1.0 200 OK
    Server: SimpleHTTP/0.6 Python/2.6.6
    Date: Wed, 29 Jun 2016 20:06:36 GMT
    Content-type: text/html; charset=UTF-8
    Content-Length: 1100
    X-Important-5: 5
    Y-Important-5: 5

    ", "client_response" : "HTTP/1.1 200 OK
    Server: ATS/7.0.0
    Date: Wed, 29 Jun 2016 20:06:36 GMT
    Content-type: text/html; charset=UTF-8
    Content-Length: 1100
    X-Important-5: 5
    Y-Important-5: 5
    Age: 0
    Connection: keep-alive
    X-Important-6: 6
    Y-Important-6: 6

    ", "sequence" : 67}''')

    print (header_info3.to_json())