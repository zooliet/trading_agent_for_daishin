
import logging
import win32com.client
import pythoncom

class StockMst:
    def __init__(self, redis, logger=None):
        self.redis = redis
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)

    def request(self, asset):
        obj = win32com.client.Dispatch("DsCbo1.StockMst")
        obj.SetInputValue(0, asset)
        obj.BlockRequest()

        if obj.GetDibStatus() == 0:  # ready to send
            self.logger.info(obj.GetDibMsg1())
            current_price = obj.GetHeaderValue(11)
            self.logger.info(f"[현재가] {asset}: {current_price}")
            return 1
        else:
            return 0
