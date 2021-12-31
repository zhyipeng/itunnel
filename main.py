import functools

import rumps

from app.config import load_config
from app.tunnel import Tunnel

configs = load_config()

tunnels: dict[str, Tunnel] = {}


def switch_tunnel(name: str, sender):
    sender.state = not sender.state
    if sender.state:
        tunnels[name].start()
        rumps.notification(name, '', f'{name} connected.')
    else:
        tunnels[name].stop()
        rumps.notification(name, '', f'{name} disconnected.')


for conf in configs:
    t = Tunnel(conf)
    tunnels[conf.name] = t
    rumps.clicked(conf.name)(functools.partial(switch_tunnel, conf.name))


class App(rumps.App):

    def __init__(self):
        super().__init__("iTunnel")
        self.menu = ['Refresh'] + list(tunnels.keys())

    @rumps.clicked('Refresh')
    def refresh(self, _):
        for n, t in tunnels.items():
            if not t.is_active:
                continue

            t.restart()
            # t.sshtunnel.check_tunnels()
            # print(t.sshtunnel.tunnel_is_up[t.sshtunnel.local_bind_address])


if __name__ == "__main__":
    App().run()
