
import sys
import logging
import time

windows_platform = False
if sys.platform == 'win32':
    import win32com.client
    import pythoncom
    windows_platform = True

    from .stock_mst import StockMst

class CybosPlus:
    def __init__(self, redis, logger=None):
        self.redis = redis
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)


    def process(self, tokens=[]):
        self.logger.info(tokens)

        if not self.check_connection():
            self.logger.warn("Cybos Plus 서버와 연결이 되지 않습니다.")
            return

        eval(f"self.{tokens[0]}({tokens[1:]})")

    def check_connection(self):
        if windows_platform:
            objCpCybos = win32com.client.Dispatch("CpUtil.CpCybos")
            bConnect = objCpCybos.IsConnect
            return bConnect  # 0: fail, 1: success
        else:
            return 0

    def get_price(self, assets):
        for asset in assets:
            obj = StockMst(self.redis, self.logger)
            status = obj.request(asset)

    # def get_realtime_price(assets):
    #     watched = list(map(lambda x: x.asset, self.watch_list))
    #     for asset in assets:
    #         if asset not in watched:
    #             obj = StockCur(asset, self.logger)
    #             status = obj.request()
    #             if status:
    #                 self.watch_list.append(obj)
    #
    # def cancel_realtime_price(assets):
    #     watched = list(map(lambda x: x.asset, self.watch_list))
    #     for asset in assets:
    #         if asset not in watched:
    #             obj = StockCur(asset, self.logger)
    #             status = obj.request()
    #             if status:
    #                 self.watch_list.append(obj)




            stockMst = win32com.client.Dispatch("DsCbo1.StockMst")
            stockMst.SetInputValue(0, asset)
            stockMst.BlockRequest()

            while stockMst.GetDibStatus() == 1:
                time.sleep(0.1)

            if stockMst.GetDibMsg1() == 0:
                current_price = stockMst.GetHeaderValue(11)
                self.logger.info(f"{code} 현재가: {current_price}")
