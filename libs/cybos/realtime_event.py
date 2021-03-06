
import logging
import json
import sys
if sys.platform == 'win32':
    import win32com.client
    import pythoncom

import asyncio

class EventHandler:
    def set_params(self, caller):
        self.caller = caller

    def OnReceived(self):
        self.caller.on_received()


class RealtimeEvent:
    def __init__(self, mqtt, logger=None):
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)

        self.mqtt = mqtt

    def join(self, asset):
        self.asset = asset
        self.client = win32com.client.Dispatch("DsCbo1.StockCur")
        self.client.SetInputValue(0, asset)

        handler = win32com.client.WithEvents(self.client, EventHandler)
        handler.set_params(self)
        self.client.Subscribe()

    def cancel(self, asset):
        self.client.Unsubscribe()

    def on_received(self):
        code = self.client.GetHeaderValue(0)  # 종목코도
        name = self.client.GetHeaderValue(1)  # 종목명
        timess = self.client.GetHeaderValue(18)  # 초
        exFlag = self.client.GetHeaderValue(19)  # 예상체결 플래그
        cprice = self.client.GetHeaderValue(13)  # 현재가
        diff = self.client.GetHeaderValue(2)  # 대비
        cVol = self.client.GetHeaderValue(17)  # 순간체결수량
        vol = self.client.GetHeaderValue(9)  # 거래량
        self.logger.debug(f"{name}({code}): {cprice} {vol}")

        message = {
            'action': 'realtime_event',
            'code': code,
            'name': name,
            'current': cprice,
            'volume': vol
        }
        message = bytearray(json.dumps(message), 'utf-8')
        t = [asyncio.create_task(self.mqtt_pub(message))]

    async def mqtt_pub(self, message):
        await self.mqtt.publish('rekcle/cybos/response', message, qos=0x00)
