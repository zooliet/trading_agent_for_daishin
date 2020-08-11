

import logging
import json
import sys
if sys.platform == 'win32':
    import win32com.client
    import pythoncom

from datetime import datetime
import time
import asyncio

class PerMinHistory:
    def __init__(self, mqtt, logger=None):
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
            
        self.mqtt = mqtt

    async def request(self, asset):
        num_requested = 200 # upto 200000 (하루 약 400개=> 200000/400 = 500일)
        client = win32com.client.Dispatch("CpSysDib.StockChart")
        client.SetInputValue(0, asset)
        client.SetInputValue(1, ord('2')) # 갯수로 받기
        client.SetInputValue(4, num_requested) # 조회 갯수
        client.SetInputValue(5, [0,1,2,3,4,5,8]) # 날짜, 시간, 시가, 고가, 저가, 종가, 거래량 
        client.SetInputValue(6, ord('m'))  # '차트 주기 - 분/틱
        client.SetInputValue(7, 1)  # 분틱차트 주기
        client.SetInputValue(9, ord('1'))  # 수정주가 사용

        received_total = 0
        while received_total < num_requested: 
            client.BlockRequest()
            if client.GetDibStatus() == 0:  # ready to send
                message = {'action': 'per_min_history', 'code': asset}
                count = client.GetHeaderValue(3)  # 수신 개수
                # code = client.GetHeaderValue(0)  #종목코드
                # name= client.GetHeaderValue(1)  # 종목명
                for i in range(count):
                    received_total += 1
                    if received_total > num_requested:
                        break
                    date=client.GetDataValue(0, i)
                    time=client.GetDataValue(1, i)
                    open=client.GetDataValue(2, i)
                    close=client.GetDataValue(5, i)
                    vol=client.GetDataValue(6, i)
                    # self.logger.debug(f"[{received_total}/{num_requested}] {date} {time}: {open}(o), {close}(c), {vol}(v)")
                    # date_time = datetime.strptime(f'{date} {time:04d}', '%Y%m%d %H%M')
                    date_time = f'{date} {time:04d}'
                    # message[date_time] = { 'current': close, 'volume': vol }
                    message[date_time] = (close, vol)

                self.logger.debug(f"[{received_total}/{num_requested}]")
                message = bytearray(json.dumps(message), 'utf-8')
                await self.mqtt.publish('rekcle/cybos/response', message, qos=0x00)
                await asyncio.sleep(0.25)
            else:
                status_message = client.GetDibMsg1()
                self.logger.info(f'통신오류: {status_message}')
                break


