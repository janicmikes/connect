import yaml
import os
import logging
import getpass
import keyring
from .exceptions import PasswordException
import jsonschema

logger = logging.getLogger('openhsr_connect.config')


DEFAULT_CONFIG = """
login:
  username: {username}
  email: {mail}

sync:
  global-exclude:
    - .DS_Store
    - Thumbs.db

  conflict-handling:
    local-changes: ask # ask | keep | overwrite | makeCopy
    remote-deleted: ask # ask | delete | keep
"""

SCHEMA = {
    'title': 'open\HSR Connect configuration Schema',
    'type': 'object',
    'properties': {
        'login': {
            'type': 'object',
            'properties': {
                'username': {
                    'type': 'string'
                },
                'email': {
                    'type': 'string',
                    'pattern': '^[a-zA-Z0-9]+\.[a-zA-Z0-9]+\@hsr.ch$'
                }
            },
            'required': ['username', 'email']
        },
        'sync': {
            'type': 'object',
            'properties': {
                'global-exclude': {
                    'type': 'array',
                    'items': {'type': 'string'},
                },
                'conflict-handling': {
                    'type': 'object',
                    'properties': {
                        'local-changes': {
                            'type': 'string',
                            'pattern': '^(ask|keep|overwrite|makeCopy)$'
                        },
                        'remote-deleted': {
                            'type': 'string',
                            'pattern': '^(ask|delete|keep)$'
                        }
                    },
                    'additionalProperties': False
                },
                'repositories': {
                    'type': 'object',
                    'patternProperties': {
                        '^[^\/*&%\s]+$': {
                            'type': 'object',
                            'properties': {
                                'remote-dir': {'type': 'string'},
                                'local-dir': {'type': 'string'},
                                'exclude': {
                                    'type': 'array',
                                    'items': {'type': 'string'},
                                }
                            },
                            'required': ['remote-dir', 'local-dir']
                        }
                    },
                    'additionalProperties': False
                }
            },
            'additionalProperties': False
        }
    },
    'additionalProperties': False,
    'required': ['login', 'sync']
}


def create_default_config(config_path):
    """
    Creates the a default configuration file.
    Prompts for input (username and mail)
    """
    logger.info('Creating default configuration')
    username = input('Dein HSR-Benutzername: ')
    mail = input('Deine HSR-Email (VORNAME.NACHNAME@hsr.ch): ')
    config = DEFAULT_CONFIG.format(username=username, mail=mail)
    with open(config_path, 'w') as f:
        f.write(config)


def load_config(raise_if_incomplete=False):
    """
    Loads the user configuration and creates the default configuration if it does not yet exist.
    """
    config_path = os.path.expanduser('~/.config/openhsr-connect.yaml')

    # create default config if it does not yet exist
    if not os.path.exists(config_path):
        create_default_config(config_path)

    config = None
    with open(config_path, 'r') as f:
        if raise_if_incomplete:
            raise ConfigurationException('Configuration does not yet exist!')
        config = yaml.load(f)

    # Verify if the password is in the keyring
    try:
        get_password(config)
    except PasswordException as e:
        if raise_if_incomplete:
            raise e
        password = getpass.getpass('Dein HSR-Kennwort (wird sicher im Keyring gespeichert): ')
        keyring.set_password('openhsr-connect', config['login']['username'], password)

    # Validate the config
    jsonschema.validate(config, SCHEMA)

    # if "global_exclude" is not (fully) declared:
    if 'global_exclude' not in config['sync']:
        config['sync']['global_exclude'] = []

    # if "conflict_handling" is not (fully) declared:
    if 'conflict_handling' not in config['sync']:
        config['sync']['conflict_handling'] = {}
    if 'local-changes' not in config['sync']['conflict_handling']:
        config['sync']['conflict_handling']['local-changes'] = 'keep'
    if 'remote-deleted' not in config['sync']['conflict_handling']:
        config['sync']['conflict_handling']['remote-deleted'] = 'delete'

    # if repositories is not (fully) declared
    if 'repositories' not in config['sync']:
        config['sync']['repositories'] = {}

    for name, repository in config['sync']['repositories'].items():
        if 'exclude' not in repository:
            repository['exclude'] = []
    return config


def get_password(config):
    """
        This method can throw a PasswordException
    """
    password = keyring.get_password('openhsr-connect', config['login']['username'])
    if password is None:
        raise PasswordException('No password found for user %s' %
                                config['login']['username'])
    else:
        return password