"""BoB Test Environment"""

import os
import json
import uuid
import logging
from typing import Dict, Tuple
from datetime import datetime, timezone
from ruamel import yaml
import requests


DEFAULT_CONF = "./config.yaml"
DEFAULT_MAX_TTL = 3600


class DebugSession(requests.Session):


    def send(self, *args, **kwargs):
        """Send request, log request and response"""

        tag = str(uuid.uuid4())
        request = args[0]
        logging.debug("REQUEST %s METHOD: %s", tag, request.method)
        logging.debug("REQUEST %s URL: %s", tag, request.url)
        logging.debug("REQUEST %s HEADERS: %s", tag, request.headers)
        logging.debug("REQUEST %s CERT: %s", tag, kwargs.get('cert'))
        
        proxies = kwargs.get('proxies')
        if proxies is not None:
            logging.debug("REQUEST %s PROXIES: %s", tag, proxies)

        response = super().send(*args, **kwargs)

        logging.debug("RESPONSE %s STATUS: %d", tag, response.status_code)
        logging.debug("RESPONSE %s HEADERS: %s", tag, response.headers)
        logging.debug("RESPONSE %s CONTENT: %s", tag, response.text)

        return response


class TestEnvironment(object):
    """BoB Test Environment helper class"""

    def __init__(self, config: Dict, base_dir: str) -> None:
        self.config = config
        self.base_dir = base_dir
        self.logger = logging.getLogger(__name__)
        self.macros = self.config.get('macros', {})
        self.httpconfig = self.config.get('http')
        self.authconfig = self.config.get('global')
        self.entity_id = self.authconfig.get('entity_id')
        self.cert_filename = self.get_filepath(self.authconfig.get('cert'))
        self.key_filename = self.get_filepath(self.authconfig.get('key'))

    def close(self) -> None:
        """Close test environment"""
        pass

    def endpoint(self, api: str) -> str:
        """Get endpoint by API"""
        return self.config['test'][api]['endpoint']

    def authenticate(self, session: requests.Session, api: str = None) -> None:
        """Add BoB authentication to session (use static token if configured) """
        token = self.authconfig.get('token', self.get_auth_jwt_compact(api))
        session.headers["X-BoB-AuthToken"] = token

    def get_session(self) -> requests.Session:
        """Get session with proxies and auth"""
        session = DebugSession()
        session.cert = (self.cert_filename, self.key_filename)
        if self.httpconfig is not None:
            session.verify = self.httpconfig.get('verify', True)
            session.proxies = self.httpconfig.get('proxies')
        return session

    def get_auth_response(self,
                          api: str = None,
                          entity_id: str = None,
                          cert: Tuple[str, str] = None) -> requests.Response:
        """Get authentication response"""
        if api is not None:
            if 'entity_id' in self.config['test'][api]:
                entity_id = self.config['test'][api]['entity_id']
        if entity_id is None:
            entity_id = self.entity_id
        if cert is None:
            cert = (self.cert_filename, self.key_filename)
        if self.httpconfig is not None:
            verify = self.httpconfig.get('verify', True)
            proxies = self.httpconfig.get('proxies')
        else:
            verify = True
            proxies = None
        endpoint = self.endpoint('authentication')
        request_uri = '{}/auth/{}'.format(endpoint, entity_id)
        with DebugSession() as session:
            response = session.get(url=request_uri, cert=cert, verify=verify, proxies=proxies)
        return response

    def get_auth_jwt_compact(self, api: str = None) -> str:
        """Get authentication JWT compact"""
        response = self.get_auth_response(api=api)
        if response.status_code != 200:
            response.raise_for_status()
        data = response.json()
        return data['jwtCompact']

    def get_filepath(self, filename: str = None) -> str:
        """Get absolute file path"""
        if filename is not None:
            return self.base_dir + '/' + filename
        return None

    def update_dict_macros(self, data: dict) -> dict:
        """Update dict values using macros"""
        for key, val in data.items():
            if not isinstance(val, str):
                continue
            if val in self.config['macros']:
                data[key] = self.macros[val]
            elif val == 'UUID':
                data[key] = str(uuid.uuid4())
            elif val == 'TIMESTAMP':
                data[key] = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        return data

    @classmethod
    def create_from_config_file(cls, filename: str = DEFAULT_CONF):
        """Load configuration as YAML"""
        logging.debug("Reading configuration from %s", filename)
        with open(filename, "rt") as file:
            config_dict = yaml.load(file, Loader=yaml.Loader)
        base_dir = os.path.dirname(filename)
        return cls(config_dict, base_dir)
