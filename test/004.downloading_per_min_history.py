#!/usr/bin/env python
# ./004.downloading_per_min_history.py --assets A005930,A000660,A003540 -v1 --no-debug

# system path 셋팅
import sys
sys.path.insert(0, '.')
sys.path.insert(0, '..')
# print(sys.path)

import asyncio
from hbmqtt.client import MQTTClient, ConnectException
from hbmqtt.mqtt.constants import QOS_1, QOS_2
import aioconsole
import aiofiles
import aiocron
import json
import datetime
import re
import pandas as pd
from os import path

class App:
    def __init__(self, args, logger):
        self.logger = logger

        if args['assets']:
            self.assets = [x.strip() for x in args.get('assets').split(",")]
        else:
            self.assets = []

        self.mqtt_broker_address = args.get('mqtt', '127.0.0.1')

    async def async_init(self):
        self.mqtt = MQTTClient()
        await self.mqtt.connect(f'mqtt://{self.mqtt_broker_address}')

    async def user_input(self):
        while True:
            msg = await aioconsole.ainput()
            self.logger.debug(msg)
            if msg == 'quit':
                break
            elif re.match("^A[\d]{6}$", msg):
                if msg not in self.assets:
                    self.assets.append(msg)
                    self.logger.info(self.assets)
                await self.request_for_download(assets=[msg])

            else:
                pass

    async def mqtt_reader(self):
        mqtt = MQTTClient()
        await mqtt.connect(f'mqtt://{self.mqtt_broker_address}')
        await mqtt.subscribe([('rekcle/cybos/response', QOS_1)])

        while True:
            msg = await mqtt.deliver_message()
            packet = msg.publish_packet
            payload = packet.payload.data.decode('utf-8')
            payload = json.loads(payload)
            # self.logger.debug(f'{payload}\n')
            if payload['action'] == 'per_min_history':
                filename = f"dataset/{payload['code']}.1m.history.csv"
                del payload['action']
                del payload['code']

                self.logger.debug(f'{len(payload)} received')
                async with aiofiles.open(filename, 'a+') as f:
                    if await f.tell() == 0: # if size is 0
                        await f.write("date,current,volume\n")
                    for d in payload:
                        date = datetime.datetime.strptime(d, '%Y%m%d %H%M')
                        # date = date.strftime("%d/%m/%Y %H:%M:%S")
                        date = date.strftime("%Y-%m-%d %H:%M:%S")
                        current = payload[d]['price']
                        volume = payload[d]['volume']
                        line = f"{date}, {price}, {volume}\n"
                        await f.write(line)

                # df = pd.DataFrame.from_dict(payload, orient="index", columns=['current', 'volume'])
                # if not path.exists('data.csv'):
                #     df.to_csv("data.csv", mode='w', header=True)
                # else:
                #     df.to_csv("data.csv", mode='a', header=False)


    async def request_for_download(self, assets=[]):
        if assets:
            msg = {'action': 'get_per_min_history', 'assets': assets}
            msg = json.dumps(msg)
            msg = bytearray(msg, 'utf-8')
            await self.mqtt.publish('rekcle/cybos', msg, qos=QOS_1)


async def main(args, logger):
    app = App(args, logger)
    await app.async_init()
    tasks = [
        asyncio.create_task(app.mqtt_reader()), asyncio.create_task(app.user_input())
    ]
    await app.request_for_download(app.assets)

    # await asyncio.gather(*tasks)
    for t in asyncio.as_completed(tasks):
        res = await t
        break


if __name__ == '__main__':
    # logger 셋팅
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)

    # debugger 셋팅
    import pdb
    import rlcompleter
    pdb.Pdb.complete=rlcompleter.Completer(locals()).complete

    import argparse
    from libs.utils import BooleanAction
    ap = argparse.ArgumentParser()
    ap.add_argument('-a', '--assets', help='종목1, 종목2, 종목3')  # A005930, A000660, A003540
    ap.add_argument('-m', '--mqtt', default='127.0.0.1', help='mqtt broker address') # rekcleml.duckdns.org
    ap.add_argument('-v', '--verbose', type=int, default=0, help='verbose level: 0*')
    ap.add_argument('--debug', '--no-debug', dest='debug', default=False, action=BooleanAction, help='whether or not to print debug message: T*')

    args = vars(ap.parse_args())
    if args['verbose']:
        logger.setLevel(logging.DEBUG)

    if args['debug']:
        pdb.set_trace()

    logger.info("Started...")
    logger.debug(f"Argument: {args}")
    logger.info("Type 'quit' to exit")
    logger.info("종목을 추가하려면 AXXXXXX 형태의 종목 코드를 입력")

    asyncio.run(main(args, logger))
