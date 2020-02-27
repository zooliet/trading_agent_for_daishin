
import logging
import sys
if sys.platform == 'win32':
    import win32com.client
    import pythoncom

class EventHandler:
    def set_params(self, client):
        self.client = client

    def OnReceived(self):
        print("here")
        code = self.client.GetHeaderValue(0)  # 종목코도
        name = self.client.GetHeaderValue(1)  # 종목명
        timess = self.client.GetHeaderValue(18)  # 초
        exFlag = self.client.GetHeaderValue(19)  # 예상체결 플래그
        cprice = self.client.GetHeaderValue(13)  # 현재가
        diff = self.client.GetHeaderValue(2)  # 대비
        cVol = self.client.GetHeaderValue(17)  # 순간체결수량
        vol = self.client.GetHeaderValue(9)  # 거래량



class RealtimePrice:
    def __init__(self, redis, logger=None):
        self.redis = redis
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)

    def join(self, asset):
        self.obj = win32com.client.Dispatch("DsCbo1.StockCur")
        self.obj.SetInputValue(0, asset)

        handler = win32com.client.WithEvents(self.obj, EventHandler)
        print(handler)
        # handler.set_params(self.objStockCur)
        self.obj.Subscribe()


    def cancel(self, asset):
        obj = win32com.client.Dispatch("DsCbo1.StockCur")




    # def request(self, asset):
    #     obj = win32com.client.Dispatch("DsCbo1.StockMst")
    #     obj.SetInputValue(0, asset)
    #     obj.BlockRequest()
    #
    #     if obj.GetDibStatus() == 0:  # ready to send
    #         self.logger.info(obj.GetDibMsg1())
    #         current_price = obj.GetHeaderValue(11)
    #         self.logger.info(f"[현재가] {asset}: {current_price}")
    #         return 1
    #     else:
    #         return 0
