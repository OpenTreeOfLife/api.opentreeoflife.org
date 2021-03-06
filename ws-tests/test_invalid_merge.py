#!/usr/bin/env python
from opentreetesting import test_http_json_method, writable_api_host_and_oauth_or_exit
import sys
DOMAIN, auth_token = writable_api_host_and_oauth_or_exit(__file__)
SUBMIT_URI = DOMAIN + '/phylesystem/merge/v1/master/master'
data = {'auth_token': 'bogus'
}
if test_http_json_method(SUBMIT_URI,
                         'PUT',
                         data=data,
                         expected_status=400):
    sys.exit(0)
sys.exit(1)
