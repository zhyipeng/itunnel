import functools
import os
import time
from threading import Thread

import rumps

from app.config import load_config, CONFIG_FILE
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
        super().__init__("🌐")
        self.menu = ['⚙️Preferences', '🔄Refresh'] + list(tunnels.keys())

    @rumps.clicked('⚙️Preferences')
    def preferences(self, _):
        os.system(f'open {CONFIG_FILE.parent}')

    @rumps.clicked('🔄Refresh')
    def refresh(self, _):
        for n, t in tunnels.items():
            if not t.is_active:
                continue

            t.restart()


def check():
    tasks = []
    for t in tunnels.values():
        if not t.is_active:
            continue

        t = Thread(target=t.sshtunnel.check_tunnels)
        t.start()
        tasks.append(t)

    for t in tasks:
        t.join()

    for n, t in tunnels.items():
        if t.is_active and not t.is_alive:
            try:
                t.restart()
            except:
                pass


def run_check_thread():
    while 1:
        time.sleep(10)
        check()


if __name__ == "__main__":
    Thread(target=run_check_thread).start()
    App().run()
