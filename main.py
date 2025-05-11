import discord
import os

from functools import partial


class MessageCounterClient(discord.Client):
    async def on_message(self, message: discord.Message):
        match message.content.strip().split():
            case ["!count", "from", channel_mention, "by", user_mention]:
                channel_to_search = await self.or_fetch(
                    partial(self.get_channel, self.extract_mention(channel_mention))
                )()

                if channel_to_search is None:
                    await message.channel.send("the channel doesn't exist idiot!")
                    return

                user_to_search = await self.or_fetch(
                    partial(self.get_user, self.extract_mention(user_mention))
                )()

                print(self.extract_mention(user_mention))

                if user_to_search is None:
                    await message.channel.send("the user doesn't exist idiot!")
                    return

                count = 0

                try:
                    async for msg in channel_to_search.history():
                        if msg.author == user_to_search:
                            count += 1
                except Exception:
                    # Simpler than matching the kind of channel it is (e.g. private channel)
                    await message.channel.send("can't access the channel history :(")
                    return

                await message.channel.send(str(count))
                return

            case _:
                return

    def extract_mention(self, mention: str) -> int:
        match list(mention):
            case ["<", "#", *channel_id, ">"]:
                return int("".join(channel_id))
            case ["<", "@", *user_id, ">"]:
                return int("".join(user_id))
            case _:
                return -1

    def or_fetch(self, f):
        async def wrapper():
            if (_ := f()) is not None:
                return _

            fetch_function = getattr(self, f.func.__name__.replace("get_", "fetch_"))

            return await fetch_function(*f.args)

        return wrapper


intents = discord.Intents.default()
intents.message_content = True

client = MessageCounterClient(intents=intents)
client.run(os.getenv("CC_BOT_TOKEN", ""))
