
import sys
import logging
import time

windows_platform = False
if sys.platform == 'win32':
    import win32com.client
    import pythoncom
    windows_platform = True

from libs.cybos import CurrentPrice, RealtimeEvent, DailyPrice, PerMinHistory

class CybosPlus:
    def __init__(self, mqtt, logger=None):
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)

        self.mqtt = mqtt
        self.watched = []

    async def process(self, params={}):
        self.logger.info(params)

        if not self.check_connection():
            self.logger.warning("Cybos Plus 서버 연결 실패")
            return

        await eval(f"{self.params['action']}({params})")

    def check_connection(self):
        if windows_platform:
            client = win32com.client.Dispatch("CpUtil.CpCybos")
            bConnect = client.IsConnect
            return bConnect  # 0: fail, 1: success
        else:
            return 0

    async def get_current_price(self, params={}):
        for asset in params['assets']:
            client = CurrentPrice(self.mqtt, self.logger)
            await client.request(asset)

    def join_realtime_event(self, params={}):
        watched = list(map(lambda x: x.asset, self.watched))
        for asset in paramsi['assets']:
            if asset not in watched:
                client = RealtimeEvent(self.mqtt, self.logger)
                client.join(asset)
                self.watched.append(client)

    def cancel_realtime_event(self, params={}):
        for asset in params['assets']:
            clients = list(filter(lambda x: x.asset == asset, self.watched))
            if clients:
                client = clients[0]
                client.cancel(asset)
                self.watched.remove(client)

    def get_daily_price(self, params={}):
        for asset in params['assets']:
            client = DailyPrice(self.mqtt, self.logger)
            client.request(asset)

    def get_per_min_history(self, params={}):
        for asset in params['assets']:
            client = PerMinHistory(self.mqtt, self.logger)
            client.request(asset)

