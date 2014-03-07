from HTTP_requests import POST_request
from os import path
import json
import codecs

CRED_FILENAME = '.pylogger_pushover_credentials'

API_ENDPOINT = 'https://api.pushover.net/1/messages.json'

MSG_KEYS = {'greet': ('No API credentials found in %s' % path.expanduser('~')),
            'app_key': 'Please provide app key: ',
            'user_key': 'Please provide user key: ',
            'end': ('Credentials stored in %s' %
                    path.join(path.expanduser('~'), CRED_FILENAME))}

API_PARAMS = ['token', 'user', 'device', 'title', 'url', 'message',
              'url_title', 'priority', 'timestamp', 'sound']


class InputError(Exception):
    """docstring for InputError"""
    def __init__(self, msg=None):
        super(InputError, self).__init__(msg)


class PyLogger(object):
    """docstring for PyLogger"""
    def __init__(self, api_endpoint=None, app_key=None, user_key=None):
        keys = self._get_credentials()
        self.app_key = keys['app_key']
        self.user_key = keys['user_key']
        if not api_endpoint:
            self.api_endpoint = API_ENDPOINT
        else:
            self.api_endpoint = api_endpoint
        self.post_request = POST_request(self.api_endpoint,
                                         request_params=API_PARAMS,
                                         default_request_params={
                                         'token': self.app_key,
                                         'user': self.user_key
                                         })

    def _get_credentials(self):
        cred_path = path.join(path.expanduser('~'), CRED_FILENAME)
        if path.exists(cred_path):
            with codecs.open(cred_path, 'r', 'utf-8') as f:
                ret_di = json.load(f)
        else:
            print(MSG_KEYS['greet'])
            try:
                # Python 2
                app_key = raw_input(MSG_KEYS['app_key'])
                user_key = raw_input(MSG_KEYS['user_key'])
            except NameError:
                # Python 3
                app_key = input(MSG_KEYS['app_key'])
                user_key = input(MSG_KEYS['user_key'])
            with codecs.open(cred_path, 'w', 'utf-8') as f:
                ret_di = {'app_key': app_key, 'user_key': user_key}
                json.dump(ret_di, f)
                print(MSG_KEYS['end'])

        return ret_di

    def __call__(self, **kwargs):
        return self.send_log(**kwargs)

    def send_log(self, **kwargs):
        # testing if the keyword arguments are all in the
        # set of parameters for the POST call
        if not(set(kwargs.keys()) <= set(API_PARAMS)):
            raise InputError('extra arguments provided.')

        print kwargs
        self.post_request(**kwargs)
        return True
