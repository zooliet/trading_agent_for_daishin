#!/usr/bin/env python


import asyncio
# import paho.mqtt.publish as publish
# import paho.mqtt.client as paho
from hbmqtt.client import MQTTClient, ConnectException
from hbmqtt.mqtt.constants import QOS_1, QOS_2

import tkinter as tk
from tkinter import messagebox, filedialog, ttk

from libs.cybos import CybosPlus

class App(tk.Tk):
    def __init__(self, loop, args, logger=None, interval=1/120):
        super().__init__()
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)

        self.mqtt_broker_address = args.get('mqtt', '127.0.0.1')
        self.loop = loop # asyncio loop
        self.tasks = []
        self.init_ui()

    async def async_init(self):
        self.tasks.append(loop.create_task(self.updater(interval)))
        self.tasks.append(loop.create_task(self.mqtt_reader()))

        self.mqtt = MQTTClient()
        await self.mqtt.connect(f'mqtt://{self.mqtt_broker_address}')
        self.cybos = CybosPlus(self.mqtt, self.logger)

    def init_ui(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        w = 260
        h = 60
        # x = (screen_width/2) - (w/2)
        # y = (screen_height/2) - (h/2)
        x = (screen_width - w)
        y = 0
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.title("Trading agent")
        button = tk.Button(self, text='종료 (Exit)', command=lambda: self.close())
        button.pack(expand=1, fill='both', padx=12, pady=12)
        # button.configure(font='Helvetica 16 bold')
        # tk.Button(self, text='테스트', command=lambda: self.test()).pack(fill='both', padx=20, pady=(0,5))
        self.protocol('WM_DELETE_WINDOW', self.close)

    def close(self):
        # if messagebox.askokcancel("종료?", "프로그램을 종료합니다."):
        for task in self.tasks:
            task.cancel()
        self.loop.stop()
        # self.destroy()

    # def test(self):
    #     msg = {'action': 'test:action', 'params': 'hello mqtt'}
    #     msg = json.dumps(msg)
    #     msg = bytearray(msg, 'utf-8')
    #     await self.mqtt.publish('rekcle/cybos', msg, qos=QOS_1)
        

    async def updater(self, interval):
        while True:
            self.update()
            await asyncio.sleep(interval)

    async def mqtt_reader(self):
        client = MQTTClient()
        await client.connect(f'mqtt://{self.mqtt_broker_address}')
        await client.subscribe([('rekcle/cybos', QOS_1)])

        while True:
            msg = await client.deliver_message()
            packet = msg.publish_packet
            payload = packet.payload.data.decode('utf-8')
            payload = json.loads(payload)
            # tokens = [x.stripe() for x in packet.payload.data.decode('utf-8').split(":")]
            # if tokens[0] == 'quit':
            #     pass
            
            if payload['action'] == 'quit':
                await client.disconnect() # close the sub channel
                await self.mqtt.disconnect() # close the pub channel
                break
            else:
                await self.cybos.process(payload)

        self.close()

if __name__ == '__main__':
    # debugger 셋팅
    import pdb
    import rlcompleter
    pdb.Pdb.complete=rlcompleter.Completer(locals()).complete

    # logger 셋팅
    import json
    import logging
    import logging.config

    with open('./config/logging.conf.json', 'rt') as f:
        config = json.load(f)

    logging.config.dictConfig(config)
    logger = logging.getLogger(__name__)
    logger.info("Started...")

    # CLI 파싱
    import argparse
    from libs.utils import BooleanAction

    ap = argparse.ArgumentParser()
    ap.add_argument('-m', '--mqtt', default='127.0.0.1', help='mqtt broker address') # rekcleml.duckdns.org
    ap.add_argument('--debug', '--no-debug', dest='debug', default=False, action=BooleanAction, help='디버거 사용 유무')
    ap.add_argument('-v', '--verbose', type=int, default=0, help='verbose level: 0*')

    args = vars(ap.parse_args())
    if args['verbose']:
        logger.setLevel(logging.DEBUG)

    if args['debug']:
        pdb.set_trace()
        import code
        code.interact(local=locals())

    loop = asyncio.get_event_loop()
    app = App(loop, args, logger=logger)
    await app.async_init()
    # app.mainloop()
    # 주1. gui loop와 asyncio loop를 같이 사용할 수 없기 때문에 gui loop는 수동으로 실행
    # 주2. https://stackoverflow.com/questions/47895765/use-asyncio-and-tkinter-or-another-gui-lib-together-without-freezing-the-gui
    loop.run_forever()
    loop.close()
    # app.destroy()
