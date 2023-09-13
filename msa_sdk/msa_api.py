"""Module msa_api."""
import json
import logging
import random
import sys

import requests
from msa_sdk import constants, context
from msa_sdk.variables import Variables

logger = logging.getLogger("msa-sdk")

def host_port():
    """
    Hostname and port of the API.

    Returns
    -------
    Hostname and Port

    """
    return('localhost', '8480')


class MSA_API():  # pylint: disable=invalid-name
    """Class MSA API."""

    ENDED = constants.ENDED
    FAILED = constants.FAILED
    RUNNING = constants.RUNNING
    WARNING = constants.WARNING
    PAUSED = constants.PAUSED

    def __init__(self):
        """Initialize."""
        self.url = 'http://{}:{}/ubi-api-rest'.format(*host_port())
        self._token = context['TOKEN']
        self.path = ""
        self.response = None
        self.log_response = True
        self._content = ""
        self.action = self.__class__

    @classmethod
    def process_content(cls, status, comment, new_params, log_response=False):
        """

        Process content.

        Parameters
        ----------
        status: String
            Status ID: 'ENDED', 'FAIL', 'RUNNING', 'WARNING', 'PAUSE'
        comment: String
            Comment
        new_params: Dictionary
            Context
        log_response: Bool
            Write log to a file

        Returns
        -------
        Response content formated

        """
        response = {
            "wo_status": status,
            "wo_comment": comment,
            "wo_newparams": new_params
        }
        if log_response:
            import copy
            woToken = copy.deepcopy(new_params)
            if 'TOKEN' in woToken:
                del woToken['TOKEN']
            pretty_json = json.dumps(woToken, indent=4)
            logger.info(pretty_json)

        json_response = json.dumps(response)
        return json_response

    @classmethod
    def task_error(cls, comment, context, log_response=True):
        """

        Task error and print.

        Parameters
        ----------
        comment: String
            Comment
        new_params: Dictionary
            Context
        log_response: Bool
            Write log to a file

        Returns
        -------
        None

        """
        print(cls.process_content(constants.FAILED, comment, context,
                                  log_response))
        sys.exit(1)

    @classmethod
    def task_success(cls, comment, context, log_response=True):
        """

        Task success and print.

        Parameters
        ----------
        comment: String
            Comment
        new_params: Dictionary
            Context
        log_response: Bool
            Write log to a file

        Returns
        -------
        None

        """
        print(cls.process_content(constants.ENDED, comment, context,
                                  log_response))
        sys.exit(0)

    @property
    def token(self):
        """
        Property API Token.

        Returns
        -------
        Token

        """
        return self._token

    @property
    def content(self):
        """Content of the response."""
        if not self._content:
            return '{}'
        return self._content

    def check_response(self):
        """
        Check reponse of a POST/GET/PUT/DELETE.

        Returns
        --------
        None


        """
        if not self.response.ok:
            json_response = self.response.json()
            self._content = self.process_content(self.FAILED, self.action,
                                                 json_response['message'])

    def _call_post(self, data=None, timeout=60):
        """
        Call -XPOST. This is a private method.

        This method that should not be used outside this sdk scope.

        Returns
        --------
        None

        """
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer {}'.format(self._token),
        }
        self.add_trace_headers(headers)
        if data is None:
            data = {}

        if isinstance(data, dict):
            data = json.dumps(data)
        else:
            raise TypeError('Parameters needs to be a dictionary')

        url = self.url + self.path
        self.response = requests.post(url, headers=headers, data=data,
                                      timeout=timeout)
        self._content = self.response.text
        self.check_response()

    def _call_get(self, timeout=60, params={}):
        """
        Call -XGET. This is a private method.

        This method that should not be used outside this sdk scope.

        Returns
        --------
        None

        """
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer {}'.format(self._token),
        }
        self.add_trace_headers(headers)
        url = self.url + self.path
        self.response = requests.get(url, headers=headers, timeout=timeout,
                                     params=params)
        self._content = self.response.text
        self.check_response()

    def _call_put(self, data=None) -> None:
        """
        Call -XPUT. This is a private method.

        This method that should not be used outside this sdk scope.

        Parameters
        ----------
        data: Data to send

        Returns
        --------
        None

        """
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(self._token),
        }
        self.add_trace_headers(headers)
        url = self.url + self.path
        self.response = requests.put(url, data=data, headers=headers)
        self._content = self.response.text
        self.check_response()

    def _call_delete(self) -> None:
        """
        Call -XDELETE. This is a private method.

        This method that should not be used outside this sdk scope.

        Returns
        --------
        None

        """
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer {}'.format(self._token),
        }
        self.add_trace_headers(headers)
        url = self.url + self.path
        self.response = requests.delete(url, headers=headers)
        self._content = self.response.text
        self.check_response()

    def add_trace_headers(self, headers):
        """Add W3C trace headers."""
        if 'TRACEID' not in context:
            t, s = self.create_trace_id()
            context['TRACEID'] = t
            context['SPANID'] = s
            logger.info("Creating traceId: 00-%s-%s-01", t,s)
        # W3C compatible header
        headers['traceparent'] = '00-{}-{}-01'.format(context['TRACEID'], context['SPANID'])
        # Old X-B3, to be removed.
        headers['X-B3-TraceId'] = context['TRACEID']
        headers['X-B3-SpanId'] = context['SPANID']

    def log_to_process_file(self, processId: str, log_message: str) -> bool:
        """

        Write log string with ISO timestamp to process log file.

        Parameters
        ----------
        process_id: String
                    Process ID of current process
        log_message: String
                     Log text

        Returns
        -------
        True:  log string has been written correctlly
        False: log string has not been written correctlly or the log
            file doesnt exist

        """
        import logging
        logger = logging.getLogger("msa-sdk")
        logger.info(log_message)
        return True

    def create_trace_id(self):
        """Create a new traceId/spanId."""
        trace_id = '%032x' % random.randrange(16**32)
        span_id = '%016x' % random.randrange(6**23)
        return trace_id, span_id
