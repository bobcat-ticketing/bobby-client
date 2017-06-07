"""BoB Test Environment"""

import os
import json
import uuid
import logging
from typing import Dict, Tuple
from datetime import datetime, timezone
from ruamel import yaml
import requests


DEFAULT_CONF = "examples/config.yaml"
DEFAULT_MAX_TTL = 3600


class TestEnvironment(object):
    """BoB Test Environment helper class"""

    def __init__(self, config: Dict, base_dir: str):
        self.config = config
        self.base_dir = base_dir

        self.logger = logging.getLogger(__name__)

        metadata_filename = self.get_filepath(self.config.get('metadata'))
        if metadata_filename is not None:
            with open(metadata_filename) as metadata_file:
                metadata_list = json.load(metadata_file)
            self.metadata = {}
            for entry in metadata_list:
                pid = entry['pid']
                self.metadata[str(pid)] = entry
        else:
            self.metadata = None

        self.macros = self.config.get('macros', {})
        self.httpconfig = self.config.get('http')
        self.authconfig = self.config.get('authentication')
        self.entity_id = self.authconfig.get('entity_id')
        self.cert_filename = self.get_filepath(self.authconfig.get('cert'))
        self.key_filename = self.get_filepath(self.authconfig.get('key'))

    def close(self) -> None:
        """Close test environment"""
        pass

    def endpoint(self, api: str) -> str:
        """Get endpoint by API"""
        return self.config['test'][api]['endpoint']

    def authenticate(self, session: requests.Session) -> None:
        """Add BoB authentication to session (use static token if configured) """
        token = self.authconfig.get('token', self.get_auth_jwt_compact())
        session.headers["X-BoB-AuthToken"] = token

    def get_session(self) -> requests.Session:
        """Get session with proxies and auth"""
        session = requests.Session()
        session.cert = (self.cert_filename, self.key_filename)
        if self.httpconfig is not None:
            session.verify = self.httpconfig.get('verify', True)
            session.proxies = self.httpconfig.get('proxies')
        return session

    def get_auth_response(self,
                          entity_id: str = None,
                          cert: Tuple[str, str] = None) -> requests.Response:
        """Get authentication response"""
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
        return requests.get(url=request_uri, cert=cert, verify=verify, proxies=proxies)

    def get_auth_jwt_compact(self) -> str:
        """Get authentication JWT compact"""
        response = self.get_auth_response()
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
