import asyncio
import os
from datetime import datetime
import socks
from telethon.sessions import SQLiteSession
from telethon import TelegramClient
from telethon.errors import ChatAdminRequiredError
from telethon.tl.types import InputMessagesFilterDocument

import time

# connecting to API Telegram
api_id = 'int'  # API ID -> int
api_hash = "...."  # API Hash -> str
session_path = ".... .session"  # session string

# File searching options
chat_name = 'https://t.me/........'  # Chat name from you want to get files
date_from = datetime(year=2023, month=4, day=28)  # hour=
date_to = datetime(year=2023, month=4, day=29)  # hour=
folder_path = "downloads"


# Connecting to Tg, getting chat_id

async def main():
    # connecting to API Telegram
    client = TelegramClient(SQLiteSession(session_path),
                            api_id,
                            api_hash,
                            proxy=(socks.SOCKS5,
                                   "IP - str",
                                   'Port -> int',
                                   True, "Login -> str",
                                   "Password -> str")
                            )

    # authorization check
    if not client.is_connected():
        await client.connect()

    # getting chat_id by chat name
    try:
        entity = await client.get_entity(chat_name)
        chat_id = entity.id
    except ChatAdminRequiredError:
        print("Error: not enough permissions to get  chat_id.")
        await client.disconnect()
        return
    except Exception as e:
        print("Error while getting chat_id:", e)
        await client.disconnect()
        return

    # Getting needed files in time delta
    try:
        pre_first_msg = await client.get_messages(chat_id,
                                                  offset_date=date_from,
                                                  limit=1
                                                  )
        first_msg = await client.get_messages(chat_id, min_id=pre_first_msg[0].id, limit=1, reverse=True)
        print(first_msg)
        last_msg = await client.get_messages(chat_id, offset_date=date_to, limit=1)
        print(last_msg)
        messages = await client.get_messages(chat_id, limit=3000, filter=InputMessagesFilterDocument(),
                                             min_id=first_msg[0].id - 1, max_id=last_msg[0].id + 1)
        print(messages)
    except Exception as e:
        print("Error while getting list of files:", e)
        await client.disconnect()
        return

    # Downloading files and sorting them by date

    for msg in messages:
        file_name = msg.document.attributes[0].file_name
        file_date = msg.date.strftime('%Y-%m-%d')
        file_path = os.path.join(folder_path, file_date)
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        await client.download_media(msg, file=os.path.join(file_path, file_name))
        print(f"File {file_name} saved in directory {file_date}.")

        files = sorted(os.listdir(os.path.dirname(file_path)), key=lambda f: (f[:12]))

    await client.disconnect()


asyncio.run(main())
