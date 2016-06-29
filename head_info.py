import json


class HeaderInfo(object):
    '''
    File name: head_info.py
    Author: Chenglong Wei, chwei@linkedin.com, weichenglong@gmail.com
    Date created: 6/28/2016
    Python Version: 2.6.6
    Functions: Wrapped header information.
    '''

    def __init__(self, js=None, hook_id=None, timestamps=None, tag=None, sequence=None,
                 client_request=None, server_request=None, server_response=None, client_response=None):
        if js is not None:
            self.__dict__ = json.loads(js)
            return

        self.hook_id = hook_id
        self.timestamps = timestamps
        self.tag = tag
        self.sequence = sequence

        self.client_request = client_request
        self.server_request = server_request
        self.server_response = server_response
        self.client_response = client_response

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)


header_info1 = HeaderInfo(hook_id="TS_HTTP_SEND_RESPONSE_HDR_HOOK")
print (header_info1.to_json())
print header_info1.to_json()

header_info2 = HeaderInfo(js='{"hook_id" : "TS_HTTP_SEND_RESPONSE_HDR_HOOK", "timestamps": 123456}')
print (header_info2.to_json())