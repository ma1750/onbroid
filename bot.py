import asyncio
import discord
from config import Config

class Onbroid(discord.Client):
    def __init__(self, config):
        self.config = config
        self.message_cache = {}
        super().__init__()

    async def start(self):
        await super().start(self.config.token)

    async def on_ready(self):
        print('ready')

    async def cp(self, message, msg_idable, *_):
        '''
        対象のメッセージを任意のチャンネルに投稿する
        Usage: cp message_(ID|Link) dest_channel1 (dest_channel2 ...)
        '''
        msg_id = self.get_msgid(msg_idable)
        if not msg_id:
            await message.channel.send('invalid mesage ID or URL')
            return False
        payload = await self.resolve_message(message.channel, msg_id)
        if not payload.id in self.message_cache:
            self.message_cache[payload.id] = payload
        channels = message.channel_mentions or [message.channel]
        channels = set(channels) #重複を削除

        if not payload:
            print(f'message resolve failed')
            return False

        for channel in channels:
            try:
                embed = await self.make_embed(payload)
                if embed:
                    payload.embeds.insert(0,embed)
                for embed in payload.embeds:
                    await channel.send(embed=embed)
            except Exception as e:
                print(f'send message faild: {e}')
                return False
        await message.delete()
        return True

    async def mv(self, message, msg_idable, *_):
        '''
        対象のメッセージを削除して任意のチャンネルに投稿する
        Usage: mv message_(ID|Link) dest_channel1 (dest_channel2 ...)
        '''
        if await self.cp(message=message, msg_idable=msg_idable):
            try:
                target = await self.resolve_message(message.channel, self.get_msgid(msg_idable))
                if target:
                    await target.delete()
            except Exception as e:
                print(f'some error occered deleting message: {e}')

    async def fuck(self, message, msg_id, *_):
        '''
        対象のメッセージに `f,u,c,k,middle_finger` のリアクションを付ける
        Usage: fuck message_(ID|Link)
        '''
        msg_id = self.get_msgid(msg_id)
        if not msg_id:
            await message.channel.send('invalid mesage ID or URL')
            return
        target = await self.resolve_message(message.channel, msg_id)
        if not target:
            return
        fuck_emote = ['\U0001F1EB', '\U0001F1FA', '\U0001F1E8', '\U0001F1F0', '\U0001F595']
        for emote in fuck_emote:
            self.loop.create_task(target.add_reaction(emote))
        await message.delete()

    async def on_reaction_add(self, reaction, _):
        if str(reaction.emoji) == '\U0001F4CC':
            await reaction.message.pin()

    def get_msgid(self, msg_idable):
        '''
        message ID もしくは message Linkからdiscord.Message.idを返す

        Parameters
        ----------
        msg_idable: str

        Returns
        -------
        id: int
        '''
        try:
            msg_id = int(msg_idable)
        except ValueError:
            if msg_idable.startswith('http'):
                msg_idable = msg_idable.split('/')[-1]
                return self.get_msgid(msg_idable)
            else:
                return None
        return msg_id

    async def resolve_message(self, channel, msg_id):
        '''
        Parameters
        ----------
        channel: discord.TextChannel -- search for message in this channel
        msg_id: int -- The message ID to look for.

        Returns
        -------
        message: discord.Message
        '''
        return self.message_cache.get(msg_id) or await self._search_message(channel, msg_id)

    async def _search_message(self, channel, msg_id):
        '''
        search un_cached message

        Parameters
        ----------
        channel: discord.TextChannel -- search for message in this channel
        msg_id: int -- The message ID to look for.

        Returns
        -------
        message: discord.Message
        '''
        try:
            return await channel.fetch_message(msg_id)
        except discord.Forbidden as e:
            print(f'permission error: {e}')
            return None
        except (discord.NotFound, discord.HTTPException) as e:
            print(e)
            return None

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
        self.message_cache[message.id] = message

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

    async def on_message_delete(self, message):
        if message.id in self.message_cache:
            del self.message_cache[message.id]