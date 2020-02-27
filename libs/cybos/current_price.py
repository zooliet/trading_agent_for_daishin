
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
            code = client.GetHeaderValue(0)  #종목코드
            name= client.GetHeaderValue(1)  # 종목명
            time= client.GetHeaderValue(4)  # 시간
            cprice= client.GetHeaderValue(11) # 종가
            diff= client.GetHeaderValue(12)  # 대비
            open= client.GetHeaderValue(13)  # 시가
            high= client.GetHeaderValue(14)  # 고가
            low= client.GetHeaderValue(15)   # 저가
            offer = client.GetHeaderValue(16)  #매도호가
            bid = client.GetHeaderValue(17)   #매수호가
            vol= client.GetHeaderValue(18)   #거래량
            vol_value= client.GetHeaderValue(19)  #거래대금
            self.logger.debug(f"{name}({code}): {open}(시가), {low}(저가), {high}(고가), {cprice}(종가), {vol}(거래량)")

            message = {
                'action': 'current_price',
                'code': code,
                'name': name,
                'low': low,
                'high', high,
                'open', open,
                'current', cprice,
                'volume', vol
            }
            message = json.dumps(message)
            self.redis.publish('rekcle:cybos:response', message)
