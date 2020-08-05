#!/usr/bin/env python
# ./001.polling_current_price.py --assets A005930,A006660,A003540 -v1 --no-debug

# system path 셋팅
import sys
sys.path.insert(0, '.')
sys.path.insert(0, '..')
# print(sys.path)

# logger 셋팅
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# debugger 셋팅
import pdb
import rlcompleter
pdb.Pdb.complete=rlcompleter.Completer(locals()).complete

import asyncio
from hbmqtt.client import MQTTClient, ConnectException
from hbmqtt.mqtt.constants import QOS_1, QOS_2
import aioconsole
import aiofiles
import aiocron
import json
import datetime
import re

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
            self.logger.debug(f'{payload}\n')
            if payload['action'] == 'current_price':
                filename = f"dataset/{payload['code']}.csv"
                async with aiofiles.open(filename, 'a+') as f:
                    date = datetime.date.today().strftime("%Y-%m-%d")
                    # date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    low = payload['low']
                    high = payload['high']
                    open = payload['open']
                    current = payload['current']
                    volume = payload['volume']

                    line = f"{date}, {open}, {high}, {low}, {current}, {volume}\n"
                    await f.write(line)

    async def cron_job(self):
        if self.assets:
            msg = {'action': 'get_current_price', 'assets': self.assets}
            msg = json.dumps(msg)
            msg = bytearray(msg, 'utf-8')
            await self.mqtt.publish('rekcle/cybos', msg, qos=QOS_1)

async def main(args, logger):
    app = App(args, logger)
    await app.async_init()
    tasks = [
        asyncio.create_task(app.mqtt_reader()), asyncio.create_task(app.user_input())
    ]

    cron = aiocron.crontab('*/1 * * * * 0', func=app.cron_job, start=True) # every 1 min
    # cron = aiocron.crontab('0 15 * * 1-5 0', func=app.cron_job, start=True) # 월-금, 15:00:00
    # i = 0
    # while True:
    #     i += 1
    #     res = await cron.next(i)

    # await asyncio.gather(*tasks)
    for t in asyncio.as_completed(tasks):
        res = await t
        cron.stop()
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
    ap.add_argument('-a', '--assets', help='종목1, 종목2, 종목3')  # A005930, A006660, A003540
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



