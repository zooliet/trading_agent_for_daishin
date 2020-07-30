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
import aioredis
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

        self.redis_address = args.get('redis', '127.0.0.1')
        self.redis_pub = None

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

                await self.request_for_fetching([msg])
            else:
                pass

    async def redis_reader(self):
        redis = await aioredis.create_redis(f'redis://{self.redis_address}')
        (redis_ch, ) = await redis.subscribe('rekcle:cybos:response')
        while await redis_ch.wait_message():
            msg = await redis_ch.get(encoding='utf-8')
            msg = json.loads(msg)
            self.logger.debug(f'{msg}\n')
            if msg['action'] == 'daily_price':
                pass # do something

    async def request_for_fetching(self, assets):
        if not self.redis_pub:
            self.redis_pub = await aioredis.create_redis(f'redis://{self.redis_address}')
        if assets:
            assets = ":".join(assets)
            await self.redis_pub.publish('rekcle:cybos', f'get_daily_price:{assets}')


async def main(args, logger):
    app = App(args, logger)
    tasks = [
        asyncio.create_task(app.redis_reader()), asyncio.create_task(app.user_input())
    ]

    await app.request_for_fetching(app.assets)

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
    ap.add_argument('-r', '--redis', default='127.0.0.1', help='redis server address') # rekcleml.duckdns.org
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



