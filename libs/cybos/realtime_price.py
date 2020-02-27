
import logging
import sys
if sys.platform == 'win32':
    import win32com.client
    import pythoncom

class EventHandler:
    def set_params(self, caller):
        self.caller = caller

    def OnReceived(self):
        self.caller.on_received()


class RealtimePrice:
    def __init__(self, redis, logger=None):
        self.redis = redis
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)

    def join(self, asset):
        self.asset = asset
        self.client = win32com.client.Dispatch("DsCbo1.StockCur")
        self.client.SetInputValue(0, asset)

        handler = win32com.client.WithEvents(self.client, EventHandler)
        handler.set_params(self)
        self.client.Subscribe()


    def on_received(self):
        code = self.client.GetHeaderValue(0)  # 종목코도
        name = self.client.GetHeaderValue(1)  # 종목명
        timess = self.client.GetHeaderValue(18)  # 초
        exFlag = self.client.GetHeaderValue(19)  # 예상체결 플래그
        cprice = self.client.GetHeaderValue(13)  # 현재가
        diff = self.client.GetHeaderValue(2)  # 대비
        cVol = self.client.GetHeaderValue(17)  # 순간체결수량
        vol = self.client.GetHeaderValue(9)  # 거래량
        self.logger.info(f"{name}({code}): {cprice}")


    def cancel(self, asset):
        self.client.Unsubscribe()
