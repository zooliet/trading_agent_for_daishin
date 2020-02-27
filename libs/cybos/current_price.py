
import logging
import sys
if sys.platform == 'win32':
    import win32com.client
    import pythoncom

class CurrentPrice:
    def __init__(self, redis, logger=None):
        self.redis = redis
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)

    def request(self, asset):
        client = win32com.client.Dispatch("DsCbo1.StockMst")
        client.SetInputValue(0, asset)
        client.BlockRequest()

        if client.GetDibStatus() == 0:  # ready to send
            self.logger.info(client.GetDibMsg1())
            current_price = client.GetHeaderValue(11)
            self.logger.info(f"[현재가] {asset}: {current_price}")
