
import logging
import json
import sys
if sys.platform == 'win32':
    import win32com.client
    import pythoncom

class DailyPrice:
    def __init__(self, mqtt, logger=None):
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)

        self.mqtt = mqtt

    async def request(self, asset):
        client = win32com.client.Dispatch("DsCbo1.StockWeek")
        client.SetInputValue(0, asset)
        client.BlockRequest()

        if client.GetDibStatus() == 0:  # ready to send
            count = client.GetHeaderValue(1)  # 데이터 개수
            for i in range(1): # latest
                date = client.GetDataValue(0, i)  # 일자
                open = client.GetDataValue(1, i)  # 시가
                high = client.GetDataValue(2, i)  # 고가
                low = client.GetDataValue(3, i)  # 저가
                close = client.GetDataValue(4, i)  # 종가
                diff = client.GetDataValue(5, i)  # 종가
                vol = client.GetDataValue(6, i)  # 종가
                self.logger.debug(f"{asset}: {date}(날짜), {open}(시가), {low}(저가), {high}(고가), {close}(종가), {vol}(거래량)")

            message = {
                'action': 'daily_price',
                'code': asset,
                'date': date,
                'low': low,
                'high': high,
                'open': open,
                'close': close,
                'volume': vol
            }
            message = bytearray(json.dumps(message), 'utf-8')
            await self.mqtt.publish('rekcle/cybos/response', message, qos=0x00)
        else:
            status_message = client.GetDibMsg1()
            self.logger.info(f'통신오류: {status_message}')

