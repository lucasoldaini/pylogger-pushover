from HTTP_requests import POST_request
from os import path
import json
import codecs

####   START CONFIGURATION    ####

CRED_FILENAME = '.pylogger_pushover_credentials'
KEYCHAIN_NAME = 'pylogger_pushover_credentials'

UPATH = path.expanduser('~')
UNPATH = path.join(path.expanduser('~'), CRED_FILENAME)

MSG_KEYS = {'greet_2f': ('No API credentials found in {0}'.format(UPATH)),
            'greet_kr': ('No API credentials found in system keyring.'),
            'warn_2f': ('No keyring module found. Keys will be stored as\
                         plain text in {0}. Is it ok? [y/n]: '.format(UPATH)),
            'app_key': 'Please provide app key: ',
            'user_key': 'Please provide user key: ',
            'end_2f': ('Credentials stored in {0}'.format(UNPATH)),
            'end_kr': ('Credentials stored in system keyring.'),
            'end_notstr': ('Credentials were not stored.')}

API_ENDPOINT = 'https://api.pushover.net/1/messages.json'
API_PARAMS = ['token', 'user', 'device', 'title', 'url', 'message',
              'url_title', 'priority', 'timestamp', 'sound']

####    END CONFIGURATION   ####

YN_INPUT = set(('y', 'Y', 'n', 'N'))

try:
    from keyring import (set_password, get_password)
    HAS_KEYRING = True
except ImportError:
    HAS_KEYRING = False


def agnostic_input(msg):
    try:
        inp = raw_input(msg)
    except NameError:
        inp = input(msg)
    return inp


class InputError(Exception):
    """docstring for InputError"""
    def __init__(self, msg=None):
        super(InputError, self).__init__(msg)


class PyLogger(object):
    """docstring for PyLogger"""
    def __init__(self, api_endpoint=None, app_key=None, user_key=None):

        if app_key and user_key:
            self._set_credentials(app_key=app_key, user_key=user_key)
            self.app_key = app_key
            self.user_key = user_key
        else:
            keys = self._set_credentials()
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

    def _set_credentials(self, app_key=None, user_key=None):

        retrieved_keys = self._get_credentials()
        if retrieved_keys:
            return retrieved_keys

        if HAS_KEYRING:
            print(MSG_KEYS['greet_kr'])
        else:
            print(MSG_KEYS['greet_2f'])
            warn_flag = None

        if not(app_key) and not(user_key):
            app_key = agnostic_input(MSG_KEYS['app_key'])
            user_key = agnostic_input(MSG_KEYS['user_key'])

        if HAS_KEYRING:
            set_password(KEYCHAIN_NAME, 'app_key', app_key)
            set_password(KEYCHAIN_NAME, 'user_key', user_key)
        else:
            while not(warn_flag in YN_INPUT):
                warn_flag = agnostic_input(MSG_KEYS['warn_2f'])
            if warn_flag in set(('y', 'Y')):
                with codecs.open(UNPATH, 'w', 'utf-8') as f:
                    ret_di = {'app_key': app_key, 'user_key': user_key}
                    json.dump(ret_di, f)
                print(MSG_KEYS['end_2f'])
            else:
                print(MSG_KEYS['end_notstr'])

        return {'app_key': app_key, 'user_key': user_key}

    def _get_credentials(self):
        if HAS_KEYRING:
            app_key = get_password(KEYCHAIN_NAME, 'app_key')
            user_key = get_password(KEYCHAIN_NAME, 'user_key')
            if not(app_key) and not(user_key):
                return False
            return {'app_key': app_key, 'user_key': user_key}
        else:
            try:
                with codecs.open(UNPATH, 'r', 'utf-8') as f:
                    return json.load(f)
            except IOError:
                return False

    def __call__(self, **kwargs):
        return self.send_log(**kwargs)

    def send_log(self, **kwargs):
        # testing if the keyword arguments are all in the
        # set of parameters for the POST call
        if not(set(kwargs.keys()) <= set(API_PARAMS)):
            raise InputError('extra arguments provided.')

        self.post_request(**kwargs)
        return True
