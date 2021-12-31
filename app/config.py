import os
from dataclasses import dataclass, is_dataclass
from pathlib import Path
from typing import Optional

import paramiko
import yaml

HOME = Path(os.getenv('HOME'))


def nested_dataclass(*args, **kwargs):
    def wrapper(cls):
        cls = dataclass(cls, **kwargs)
        original_init = cls.__init__
        def __init__(self, *args, **kwargs):
            for name, value in kwargs.items():
                field_type = cls.__annotations__.get(name, None)
                if is_dataclass(field_type) and isinstance(value, dict):
                     new_obj = field_type(**value)
                     kwargs[name] = new_obj
            original_init(self, *args, **kwargs)
        cls.__init__ = __init__
        return cls
    return wrapper(args[0]) if args else wrapper


@dataclass
class ConnConf:
    host: str
    port: int
    user: str = None
    password: str = None


@nested_dataclass
class ConfigItem:
    name: str
    ssh: ConnConf
    remote: ConnConf
    local: ConnConf
    primary_key: str = None

    @property
    def RSA_key(self) -> Optional[paramiko.RSAKey]:
        if self.primary_key:
            path = Path(self.primary_key)
        else:
            path = (HOME / Path('.ssh/id_rsa'))
        if path.exists():
            return paramiko.RSAKey.from_private_key_file(str(path))

    @property
    def ssh_address_or_host(self) -> tuple[str, int]:
        return self.ssh.host, self.ssh.port

    @property
    def remote_bind_address(self) -> tuple[str, int]:
        return self.remote.host, self.remote.port

    @property
    def local_bind_address(self) -> tuple[str, int]:
        return self.local.host, self.local.port


CONFIG_FILE = HOME / Path('.config/itunnel/conf.yaml')


def create_default_config():
    if not CONFIG_FILE.parent.exists():
        CONFIG_FILE.parent.mkdir(parents=True)

    with CONFIG_FILE.open('w') as f:
        f.write('''# test:
#     ssh:
#         host: localhost
#         port: 1231
#     local:
#         host: 127.0.0.1
#         port: 1231
#     remote:
#         host: localhost
#         port: 4567

''')


class ConfigFileFormatError(Exception):
    pass


def load_config() -> list[ConfigItem]:
    if not CONFIG_FILE.exists():
        create_default_config()
        return []

    with CONFIG_FILE.open() as f:
        data = yaml.load(f, yaml.FullLoader)

    if data is None:
        return []

    configs = []
    for name, item in data.items():
        try:
            configs.append(
                ConfigItem(name=name, **item)
            )
        except TypeError as e:
            raise ConfigFileFormatError(*e.args)

    return configs


if __name__ == '__main__':
    load_config()
