import logging
import time

from sshtunnel import SSHTunnelForwarder

from app.config import ConfigItem


class Tunnel:

    def __init__(self, conf: ConfigItem):
        self.conf = conf
        self.sshtunnel: SSHTunnelForwarder = SSHTunnelForwarder(
            ssh_address_or_host=conf.ssh_address_or_host,
            ssh_pkey=conf.RSA_key,
            ssh_username=conf.ssh.user,
            ssh_password=conf.ssh.password,
            remote_bind_address=conf.remote_bind_address,
            local_bind_address=conf.local_bind_address,
        )

    def start(self):
        logging.info(f'Tunnel {self.conf.name} starting...')
        self.sshtunnel.start()
        logging.info(f'Success bound to '
                     f'{self.sshtunnel.local_bind_host}'
                     f':{self.sshtunnel.local_bind_port}')

    def stop(self):
        self.sshtunnel.stop()
        logging.info(f'Tunnel {self.conf.name} closed.')

    def restart(self):
        self.stop()
        time.sleep(1)
        self.start()
        # self.sshtunnel.restart()
        # logging.info(f'Tunnel {self.conf.name} restart.')

    @property
    def is_active(self) -> bool:
        return self.sshtunnel.is_active

    @property
    def is_alive(self) -> bool:
        return self.sshtunnel.tunnel_is_up[self.sshtunnel.local_bind_address]
