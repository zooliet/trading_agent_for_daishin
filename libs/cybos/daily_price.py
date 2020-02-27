
import logging
import sys
if sys.platform == 'win32':
    import win32com.client
    import pythoncom

class DailyPrice:
    def __init__(self, redis, logger=None):
        self.redis = redis
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)

    def request(self, asset):
        client = win32com.client.Dispatch("DsCbo1.StockWeek")
        client.SetInputValue(0, asset)
        client.BlockRequest()

        if client.GetDibStatus() == 0:  # ready to send
            self.logger.info(client.GetDibMsg1())
            count = client.GetHeaderValue(1)  # 데이터 개수
            print(count)
            for i in range(count):
                date = client.GetDataValue(0, i)  # 일자
                open = client.GetDataValue(1, i)  # 시가
                high = client.GetDataValue(2, i)  # 고가
                low = client.GetDataValue(3, i)  # 저가
                close = client.GetDataValue(4, i)  # 종가
                diff = client.GetDataValue(5, i)  # 종가
                vol = client.GetDataValue(6, i)  # 종가

                # self.logger.debug(f"{name}({code}): {open}(시가), {low}(저가), {high}(고가), {cprice}(종가), {vol}(거래량)")

            # message = {
            #     'action': 'daily_price'
            #     'code': code,
            #     'name': name,
            #     'low': low,
            #     'high', high,
            #     'open', open,
            #     'current', cprice,
            #     'volume', vol
            # }
            # message = json.dumps(message)
            # self.redis.publish('rekcle:cybos:response', message)
