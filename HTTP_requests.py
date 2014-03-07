"""HTTP requests library (utterly incomplete!)"""

from urllib import urlencode
from urllib2 import (Request, urlopen)


class ParametersError(Exception):
    """Error for invalid parameters in request."""
    def __init__(self, request_type):
        msg = 'Invalid parameter in %s request.' % request_type
        return super(ParametersError, self).__init__(msg)


class DefaultParametersError(Exception):
    """Error for missing parameters in request."""
    def __init__(self, request_type):
        msg = 'No default parameter for this %s request.' % request_type
        return super(ParametersError, self).__init__(msg)


class POST_request(object):
    """ Main interface for issuing a POST request.
        The __init__ method requires a base_url and
        allows for two optional parameters:
            request_params: is a list of parameters for
                            the POST request
            default_request_params: is a dictionary
                                    containing one or
                                    more default values
                                    for parameters.
        To use this class, initialize it, then call it
        directly using the POST request parameters as
        kwargs values."""
    def __init__(self, base_url,
                 request_params=None,
                 default_request_params=None):
        self.base_url = base_url
        self.request_params = request_params

        # initializes
        if self.request_params:
            self.default_request_params = {k: None
                                           for k in self.request_params}
        self.set_constant_params(**default_request_params)

    def set_constant_params(self, **kwargs):
        if not self.request_params:
            raise DefaultParametersError('POST')

        for k, v in kwargs.items():
            if not(k in self.request_params):
                raise ParametersError('POST')

            self.default_request_params[k] = v

        return True

    def request(self, **kwargs):
        return self.__call__(kwargs)

    def __call__(self, **kwargs):
        if self.request_params:
            values = {k: v for k, v in self.default_request_params.items()}
            for kw in kwargs:
                if not(kw in values):
                    raise ParametersError('POST')
                else:
                    values[kw] = kwargs[kw]
        else:
            values = kwargs
        values = {v: values[v] for v in values if values[v]}
        print values
        data = urlencode(values)
        req = Request(self.base_url, data)
        response = urlopen(req)

        return response
