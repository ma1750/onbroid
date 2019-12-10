import asyncio
import discord
from config import Config

class Onbroid(discord.Client):
    def __init__(self, config):
        self.config = config
        super().__init__()

    async def start(self):
        await super().start(self.config.token)

    async def on_ready(self):
        print('ready')

    async def cp(self, message, msg_id, *_):
        '''
        対象のメッセージを任意のチャンネルに投稿する
        Usage: cp message_ID dest_channel1 (dest_channel2 ...)
        '''
        try:
            msg_id = int(msg_id)
        except ValueError:
            await message.channel.send('fuck you: message_ID must be int')
            return False
        payload = await self.resolve_message(msg_id)
        channels = message.channel_mentions or [message.channel]
        channels = set(channels) #重複を削除

        if not payload:
            print(f'message resolve failed')
            return

        for channel in channels:
            try:
                embed = await self.make_embed(payload)
                if embed:
                    payload.embeds.append(embed)
                for embed in payload.embeds:
                    await channel.send(embed=embed)
            except Exception as e:
                print(f'send message faild: {e}')
                return
        await message.delete()
        return True

    async def mv(self, message, msg_id, *_):
        '''
        対象のメッセージを削除して任意のチャンネルに投稿する
        Usage: mv message_ID dest_channel1 (dest_channel2 ...)
        '''
        if await self.cp(message=message, msg_id=msg_id):
            try:
                target = await self.resolve_message(msg_id)
                await target.delete()
            except Exception as e:
                print(f'some error occered deleting message: {e}')

    async def fuck(self, message, msg_id, *_):
        '''
        対象のメッセージに `f,u,c,k,middle_finger` のリアクションを付ける
        Usage: fuck message_ID
        '''
        try:
            msg_id = int(msg_id)
        except ValueError:
            await message.channel.send('fuck you: message_ID must be int')
            return
        target = await self.resolve_message(msg_id)
        fuck_emote = ['\U0001F1EB', '\U0001F1FA', '\U0001F1E8', '\U0001F1F0', '\U0001F595']
        for emote in fuck_emote:
            self.loop.create_task(target.add_reaction(emote))
        await message.delete()

    async def resolve_message(self, msg_id):
        '''
        Parameters
        ----------
        msg_id: int -- The message ID to look for.

        Returns
        -------
        message: discord.Message
        '''
        for message in self.cached_messages:
            if message.id == msg_id:
                return message

        for channel in self.get_all_channels():
            if isinstance(channel, discord.TextChannel):
                try:
                    return await channel.fetch_message(msg_id)
                except discord.Forbidden as e:
                    print(f'permission error: {e}')
                    return None
                except (discord.NotFound, discord.HTTPException):
                    continue

    async def make_embed(self, message:discord.Message):
        '''
        Parameters
        ----------
        message: discord.Message

        Returns
        -------
        embed: discord.embed
        '''
        content = message.content
        if not content:
            return None
        user = message.author
        timestamp = message.created_at

        embed = discord.Embed(
            title=content,
            color=0x2ee21f,
            timestamp=timestamp
        )

        embed.set_author(name=user.name, icon_url=user.avatar_url_as(static_format="png"))

        return embed


    async def on_message(self, message):
        if message.author.bot:
            return

        if not message.content[:len(self.config.prefix)].startswith(self.config.prefix):
            return

        message_content = message.content[len(self.config.prefix):].strip()
        command, *args = message_content.split(' ')

        if not args:
            print(f'fuck you: {message_content}')
            return

        if command == 'cp':
            await self.cp(message, *args)
        elif command == 'mv':
            await self.mv(message, *args)
        elif command == 'fuck':
            await self.fuck(message, *args)
