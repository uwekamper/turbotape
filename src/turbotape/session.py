import os
import logging
from requests import Session

log = logging.getLogger(__file__)


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
    return {
      "access_token": str(access_token),
      "token_type": "bearer"
    }


def create_tape_session(credentials_file=None, credentials=None, check=True, robust=False):
    token = None
    if credentials is not None:
        token = credentials
    else:
        token = try_environment_token()
    if token is None:
        log.info('Loading OAuth2 token from credentials file.')
        if credentials_file is None:
            token = podio_auth.load_token()
        else:
            token = podio_auth.load_token(credentials_file)
    podio = podio_auth.make_client(token['client_id'], token, check=check, enable_robustness=robust)
    return podio


def create_app_auth_session(client_id:str, client_secret:str, app_id:int, app_token:str, robust=False):
    return podio_auth.make_app_auth_client(client_id, client_secret, app_id, app_token, robust=robust)
