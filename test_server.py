#!/usr/bin/env python


import asyncio
import aioredis
import aioconsole
import aiofiles
import aiocron
import json
import datetime
import re

class App:
    def __init__(self, assets=[], logger=None):
        self.assets = assets
        self.logger = logger

    async def user_input(self):
        self.redis_pub = await aioredis.create_redis('redis://rekcleml.duckdns.org')
        while True:
            msg = await aioconsole.ainput()
            # self.logger.info(msg)
            if msg == 'quit':
                break
            elif re.match("^A[\d]{6}$", msg):
                if msg not in self.assets:
                    self.assets.append(msg)
                    self.logger.info(self.assets)

                # for testing
                # await self.redis_pub.publish('rekcle:cybos', f'get_current_price:{msg}')
            else:
                pass

    async def redis_reader(self):
        redis = await aioredis.create_redis('redis://rekcleml.duckdns.org')
        (redis_ch, ) = await redis.subscribe('rekcle:cybos:response')
        while await redis_ch.wait_message():
            msg = await redis_ch.get(encoding='utf-8')
            msg = json.loads(msg)
            self.logger.info(f'{msg}\n')
            if msg['action'] == 'current_price':
                filename = f"dataset/{msg['code']}.csv"
                async with aiofiles.open(filename, 'a+') as f:
                    date = datetime.date.today().strftime("%Y-%m-%d")
                    # date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    low = msg['low']
                    high = msg['high']
                    open = msg['open']
                    current = msg['current']
                    volume = msg['volume']

                    line = f"{date}, {open}, {high}, {low}, {current}, {volume}\n"
                    await f.write(line)


    async def cron_job(self):
        for asset in self.assets:
            await self.redis_pub.publish('rekcle:cybos', f'get_current_price:{asset}')



async def main(assets, logger):
    app = App(assets, logger)
    tasks = [asyncio.create_task(app.redis_reader()), asyncio.create_task(app.user_input())]

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
    import logging
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    import argparse
    from libs.utils import BooleanAction

    ap = argparse.ArgumentParser()
    ap.add_argument('-a', '--assets', help='종목1, 종목2, 종목3')  # A005930, A000660, A003540
    ap.add_argument('-v', '--verbose', type=int, default=0, help='verbose level: 0*')

    args = vars(ap.parse_args())
    if args['verbose']:
        logger.setLevel(logging.DEBUG)

    logger.info("Started...")
    logger.info("Type 'quit' to exit")
    logger.info("종목을 추가하려면 AXXXXXX 형태의 종목 코드를 입력")
    if args['assets']:
        assets = [x.strip() for x in args.get('assets').split(",")]
    else:
        assets = []
    asyncio.run(main(assets, logger))
