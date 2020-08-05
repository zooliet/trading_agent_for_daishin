
import logging
import json
import sys
if sys.platform == 'win32':
    import win32com.client
    import pythoncom

class CurrentPrice:
    def __init__(self, mqtt, logger=None):
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)

        self.mqtt = mqtt

    async def request(self, asset):
        client = win32com.client.Dispatch("DsCbo1.StockMst")
        client.SetInputValue(0, asset)
        client.BlockRequest()

        if client.GetDibStatus() == 0:  # ready to send
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
            self.logger.debug(f"{name}({code}): {open}(시가), {low}(저가), {high}(고가), {cprice}(현재가), {vol}(거래량)")

            message = {
                'action': 'current_price',
                'code': code,
                'name': name,
                'low': low,
                'high': high,
                'open': open,
                'current': cprice,
                'volume': vol
            }
            message = bytearray(json.dumps(message), 'utf-8')
            await self.mqtt.publish('rekcle/cybos/response', message, qos=0x00)
        else:
            status_message = client.GetDibMsg1()
            self.logger.info(f'통신오류: {status_message}')
