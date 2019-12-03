import asyncio

from bot import Onbroid
from config import Config

if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    config = Config('./config.json')

    bot = Onbroid(config)

    loop.create_task(bot.start())
    loop.run_forever()