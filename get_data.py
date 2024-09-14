import asyncio
from telethon import TelegramClient

api_id = 517165
api_hash = 'eedeaede1361e4b77e0bb41305d6f5ec'


async def fetch_messages(client, channel_entity, limit=100):
    messages = await client.get_messages(channel_entity, limit=limit)
    return messages


async def main():
    client = TelegramClient('crawler', api_id, api_hash)
    await client.start()

    # Get the entity of the channel you want to fetch messages from
    channel_username = 'https://t.me/sut_tw'
    channel_entity = await client.get_entity(channel_username)

    # Fetch messages asynchronously
    messages = await fetch_messages(client, channel_entity, limit=50)

    # Process the messages
    for message in messages:
        print(message.text)

    await client.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
