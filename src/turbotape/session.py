import os
import logging
from pathlib import Path
from typing import Union
from time import sleep
import datetime

import requests

log = logging.getLogger(__file__)


class TapeSession(requests.Session):
    def __init__(self, tape_api_key, robust=True):
        super().__init__()
        self.headers.update({
            'authorization': f'Bearer {tape_api_key}',
        })
        self.enable_robustness = robust is True

    def request(self, method, url, data=None, headers=None, **kwargs):
        # the usual way of doing requests
        if not self.enable_robustness:
            return super().request(
                method, 
                url,
                data=data,
                headers=headers, 
                **kwargs
            )

        # robust way that tries to deal with most of the occuring errors
        # (e.g. 502 Bad Gateway). The request is retried five times.
        retry_counter = 5
        while True:
            try:
                response = super().request(
                    method, url,
                    data=data,
                    headers=headers,
                    **kwargs)
            except requests.exceptions.ConnectionError as err:
                log.warning('ConnectionError while trying to access the Podio API.')
                # Connection error means we wait one second and try again.
                retry_counter -= 1
                if retry_counter < 1:
                    raise err
                else:
                    sleep(3.0)
                    continue

            # all retries have been used up. Return the response regardless of the status code.
            if retry_counter < 1:
                return response

            # everything went well
            if response.status_code < 400:
                return response

            if 429 == response.status_code:
                # Rate-limit exceeded
                retry_counter -= 1
                reset_time_raw = response.headers['X-Retry-Reset']
                reset_time = datetime.datetime.strptime(reset_time_raw, "%Y-%m-%d %H:%M:%S")
                # Create a time-zone aware version of the `X-Retry-Reset` time.
                tz_reset_time = reset_time.replace(tzinfo=datetime.timezone.utc)
                # Use max() to avoid negative wait times.
                seconds = max((tz_reset_time - datetime.datetime.now(datetime.timezone.utc)).total_seconds(), 1.0)
                log.warning(f"HTTP 429 Client Error: Too Many Requests, waiting till {reset_time} ({seconds + 1.0} s)")
                sleep(seconds + 1.0)
                continue

            if 400 <= response.status_code < 500:
                log.error("HTTP Error happened, status: %s" % response.status_code)
                log.error('* method: %s' % method)
                log.error('* url: %s' % url)
                if kwargs.get('json'):
                    log.error('* json: %s' % repr(kwargs['json']))
                log.error('* server response: %s' % repr(response.content))
                sleep(3.0)
                # Errors like 404 or 403 are most likely our own fault and we return immediately
                return response

            if 500 <= response.status_code < 600:
                # Most likely, we have encountered a 502 Bad gateway or 504 Gateway timeout error.
                retry_counter -= 1
                log.warning('Response from URL "%s" with status code %d. Retrying in 3 seconds ...' % (url, response.status_code))
                sleep(3.0)
                continue


def make_tape_client(token: str, check=True, robust: bool=True) -> TapeSession:
    if token is None or token == "":
        raise Exception("Tape API key not given or key is empty.")
    session = TapeSession(tape_api_key=token, robust=robust, )
    session.headers.update({
        'authorization': f'Bearer {token}',
    })
    return session


def try_environment_token():
    """
    Try to get the token from the environment variable TAPE_API_KEY.
    :return:
    """
    try:
        access_token = os.environ['TAPE_API_KEY']
    except KeyError as e:
        log.info('Environment variable TAPE_API_KEY is not set.')
        return None
    log.info('Loading OAuth2 token from environment.')
    return str(access_token)


def load_token(creds_file: Union[Path, str]) -> str:
    """
    Load the token from the file name tape_credentials.txt (unless specified otherwise)
    """
    token = ""
    with open(creds_file, mode="r", encoding='utf-8') as fh:
        token = fh.readline()
    return token.strip()


def create_tape_session(credentials_file=None, credentials=None, check=True, robust=True):
    token = None
    if credentials is not None:
        token = credentials
    else:
        token = try_environment_token()
    if token is None:
        log.info('Loading Tape API key from credentials file.')
        if credentials_file is None:
            token = load_token('tape_credentials.txt')
        else:
            token = load_token(credentials_file)
    tape = make_tape_client(token, check=check, robust=robust)
    return tape
