
import logging
import sys
if sys.platform == 'win32':
    import win32com.client
    import pythoncom

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

        handler = win32com.client.WithEvents(self.obj, self)
        print(handler)
        # handler.set_params(self.objStockCur)
        self.obj.Subscribe()


    def cancel(self, asset):
        obj = win32com.client.Dispatch("DsCbo1.StockCur")


    def OnReceived(self):
        code = self.obj.GetHeaderValue(0)  # 종목코도
        name = self.obj.GetHeaderValue(1)  # 종목명
        timess = self.obj.GetHeaderValue(18)  # 초
        exFlag = self.obj.GetHeaderValue(19)  # 예상체결 플래그
        cprice = self.obj.GetHeaderValue(13)  # 현재가
        diff = self.obj.GetHeaderValue(2)  # 대비
        cVol = self.obj.GetHeaderValue(17)  # 순간체결수량
        vol = self.obj.GetHeaderValue(9)  # 거래량


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
