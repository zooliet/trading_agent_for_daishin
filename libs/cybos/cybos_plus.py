
import sys
import logging
import time

windows_platform = False
if sys.platform == 'win32':
    import win32com.client
    import pythoncom
    windows_platform = True

from libs.cybos import CurrentPrice, RealtimePrice, DailyPrice

class CybosPlus:
    def __init__(self, redis, logger=None):
        self.redis = redis
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)

        self.watched = []


    def process(self, tokens=[]):
        self.logger.info(tokens)

        if not self.check_connection():
            self.logger.warn("Cybos Plus 서버 연결 실패")
            return

        eval(f"self.{tokens[0]}({tokens[1:]})")

    def check_connection(self):
        if windows_platform:
            client = win32com.client.Dispatch("CpUtil.CpCybos")
            bConnect = client.IsConnect
            return bConnect  # 0: fail, 1: success
        else:
            return 0

    def get_current_price(self, assets):
        for asset in assets:
            client = CurrentPrice(self.redis, self.logger)
            client.request(asset)

    def get_realtime_price(self, assets):
        watched = list(map(lambda x: x.asset, self.watched))
        for asset in assets:
            if asset not in watched:
                client = RealtimePrice(self.redis, self.logger)
                client.join(asset)
                self.watched.append(client)

    def cancel_realtime_price(self, assets):
        for asset in assets:
            clients = list(filter(lambda x: x.asset == asset, self.watched))
            if clients:
                client = clients[0]
                client.cancel(asset)
                self.watched.remove(client)

    def get_daily_price(self, assets):
        for asset in assets:
            client = DailyPrice(self.redis, self.logger)
            client.request(asset)
