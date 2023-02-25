from aiohttp import web
from plugins import web_server

import pyromod.listen
from pyrogram import Client
import sys
from datetime import datetime

from config import API_HASH, APP_ID, TG_BOT_TOKEN, CHANNEL_ID, PORT


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="filesharingBot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=100,
            bot_token=TG_BOT_TOKEN
        )

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()
        self.username = usr_bot_me.username
        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id = db_channel.id, text = "Test Message")
            await test.delete()
        except Exception as e:
            print(e)
        #web-response
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()
        print(f"@{usr_bot_me.username} is started")

    async def stop(self, *args):
        await super().stop()
        print("bot stoped")

bot=Bot()
bot.run()
