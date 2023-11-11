import json
import os
from typing import TYPE_CHECKING, Dict, List, Optional

import discord
from discord.ext import commands
import sqlalchemy
from sqlalchemy import Column, String, Integer, Boolean, select
from sqlalchemy.orm import declarative_base
from alembic.migration import MigrationContext
from alembic.autogenerate import produce_migrations, render_python_code
from alembic.operations import Operations

from musicbot import utils
from config import config

# avoiding circular import
if TYPE_CHECKING:
    from musicbot.bot import MusicBot, Context

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
LEGACY_SETTINGS = DIR_PATH + "/generated/settings.json"
DEFAULT_CONFIG = {
    "command_channel": None,
    "start_voice_channel": None,
    "user_must_be_in_vc": True,
    "button_emote": None,
    "default_volume": 100,
    "vc_timeout": config.VC_TIMOUT_DEFAULT,
    "announce_songs": sqlalchemy.false(),
}
ID_LENGTH = 25  # more than enough to be sure :)
Base = declarative_base()


class GuildSettings(Base):
    __tablename__ = "settings"

    # use String for ids to be sure we won't hit overflow
    guild_id: str = Column(String(ID_LENGTH), primary_key=True)
    command_channel: Optional[str] = Column(String(ID_LENGTH))
    start_voice_channel: Optional[str] = Column(String(ID_LENGTH))
    user_must_be_in_vc: bool = Column(Boolean, nullable=False)
    button_emote: Optional[str] = Column(String(ID_LENGTH))
    default_volume: int = Column(Integer, nullable=False)
    vc_timeout: bool = Column(Boolean, nullable=False)
    announce_songs: bool = Column(
        Boolean, nullable=False, server_default=DEFAULT_CONFIG["announce_songs"]
    )

    @classmethod
    async def load(cls, bot: "MusicBot", guild: discord.Guild) -> "GuildSettings":
        "Load object from database or create a new one and commit it"
        guild_id = str(guild.id)
        async with bot.DbSession() as session:
            sett = (
                await session.execute(
                    select(GuildSettings).where(GuildSettings.guild_id == guild_id)
                )
            ).scalar_one_or_none()
            if sett:
                return sett
            session.add(GuildSettings(guild_id=guild_id, **DEFAULT_CONFIG))
            # avoiding incomplete detached object
            sett = (
                await session.execute(
                    select(GuildSettings).where(GuildSettings.guild_id == guild_id)
                )
            ).scalar_one()
            await session.commit()
            return sett

    @classmethod
    async def load_many(
        cls, bot: "MusicBot", guilds: List[discord.Guild]
    ) -> Dict[discord.Guild, "GuildSettings"]:
        """Load list of objects from database and create new ones when not found.
        Returns dict with guilds as keys and their settings as values"""
        ids = [str(g.id) for g in guilds]
        async with bot.DbSession() as session:
            settings = (
                (
                    await session.execute(
                        select(GuildSettings).where(GuildSettings.guild_id.in_(ids))
                    )
                )
                .scalars()
                .fetchall()
            )
            missing = set(ids) - {sett.guild_id for sett in settings}
            for new_id in missing:
                session.add(GuildSettings(guild_id=new_id, **DEFAULT_CONFIG))
            settings.extend(
                (
                    await session.execute(
                        select(GuildSettings).where(GuildSettings.guild_id.in_(missing))
                    )
                )
                .scalars()
                .fetchall()
            )
            await session.commit()
        # ensure the correct order
        settings.sort(key=lambda x: ids.index(x.guild_id))
        return {g: sett for g, sett in zip(guilds, settings)}

    def format(self, ctx: "Context"):
        embed = discord.Embed(
            title="Settings", description=ctx.guild.name, color=config.EMBED_COLOR
        )

        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
        embed.set_footer(
            text="Usage: {}set setting_name value".format(config.BOT_PREFIX)
        )

        # exclusion_keys = ['id']

        for key in DEFAULT_CONFIG.keys():
            # if key in exclusion_keys:
            #     continue

            if not getattr(self, key):
                embed.add_field(name=key, value="Not Set", inline=False)
                continue

            elif key == "start_voice_channel":
                vc = ctx.guild.get_channel(int(self.start_voice_channel))
                embed.add_field(
                    name=key, value=vc.name if vc else "Invalid VChannel", inline=False
                )
                continue

            elif key == "command_channel":
                chan = ctx.guild.get_channel(int(self.command_channel))
                embed.add_field(
                    name=key,
                    value=chan.name if chan else "Invalid Channel",
                    inline=False,
                )
                continue

            elif key == "button_emote":
                emote = utils.get_emoji(ctx.guild, self.button_emote)
                embed.add_field(name=key, value=emote, inline=False)
                continue

            embed.add_field(name=key, value=getattr(self, key), inline=False)

        return embed

    async def process_setting(
        self, setting: str, value: str, ctx: "Context"
    ) -> Optional[bool]:

        if setting not in DEFAULT_CONFIG:
            return None

        return await getattr(self, "set_" + setting)(setting, value, ctx)

    # -----setting methods-----

    async def set_command_channel(self, setting, value, ctx):

        if value.lower() == "unset":
            self.command_channel = None
            return True

        chan = None
        for converter in (
            commands.TextChannelConverter,
            commands.VoiceChannelConverter,
        ):
            try:
                chan = await converter().convert(ctx, value)
                break
            except commands.ChannelNotFound:
                pass

        if not chan:
            await ctx.send(
                "`Error: Channel not found`\nUsage: {}set {} channel\nOther options: unset".format(
                    config.BOT_PREFIX, setting
                )
            )
            return False
        self.command_channel = str(chan.id)
        return True

    async def set_start_voice_channel(self, setting, value, ctx):

        if value.lower() == "unset":
            self.start_voice_channel = None
            return True

        try:
            vc = await commands.VoiceChannelConverter().convert(ctx, value)
        except commands.ChannelNotFound:
            await ctx.send(
                "`Error: Voice channel not found`\nUsage: {}set {} vchannel\nOther options: unset".format(
                    config.BOT_PREFIX, setting
                )
            )
            return False
        self.start_voice_channel = str(vc.id)
        return True

    async def set_user_must_be_in_vc(self, setting, value, ctx):
        if value.lower() == "true":
            self.user_must_be_in_vc = True
        elif value.lower() == "false":
            self.user_must_be_in_vc = False
        else:
            await ctx.send(
                "`Error: Value must be True/False`\nUsage: {}set {} True/False".format(
                    config.BOT_PREFIX, setting
                )
            )
            return False
        return True

    async def set_button_emote(self, setting, value, ctx):
        if not config.ENABLE_BUTTON_PLUGIN:
            await ctx.send("`Error: Button plugin is disabled`")
            return False

        if value.lower() == "unset":
            self.button_emote = None
            return True

        emoji = utils.get_emoji(ctx.guild, value)
        if emoji is None:
            await ctx.send(
                "`Error: Invalid emote`\nUsage: {}set {} emote\nOther options: unset".format(
                    config.BOT_PREFIX, setting
                )
            )
            return False
        elif isinstance(emoji, discord.Emoji):
            emoji = str(emoji.id)
        self.button_emote = emoji
        return True

    async def set_default_volume(self, setting, value, ctx):
        try:
            value = int(value)
        except ValueError:
            await ctx.send(
                "`Error: Value must be a number`\nUsage: {}set {} 0-100".format(
                    config.BOT_PREFIX, setting
                )
            )
            return False

        if value > 100 or value < 0:
            await ctx.send(
                "`Error: Value must be a number`\nUsage: {}set {} 0-100".format(
                    config.BOT_PREFIX, setting
                )
            )
            return False

        self.default_volume = value
        return True

    async def set_vc_timeout(self, setting, value, ctx):

        if not config.ALLOW_VC_TIMEOUT_EDIT:
            await ctx.send("`Error: This value cannot be modified`")
            return False

        if value.lower() == "true":
            self.vc_timeout = True
            self.start_voice_channel = None
        elif value.lower() == "false":
            self.vc_timeout = False
        else:
            await ctx.send(
                "`Error: Value must be True/False`\nUsage: {}set {} True/False".format(
                    config.BOT_PREFIX, setting
                )
            )
            return False
        return True

    async def set_announce_songs(self, setting, value, ctx):
        if value.lower() == "true":
            self.announce_songs = True
        elif value.lower() == "false":
            self.announce_songs = False
        else:
            await ctx.send(
                "`Error: Value must be True/False`\nUsage: {}set {} True/False".format(
                    config.BOT_PREFIX, setting
                )
            )
            return False
        return True


def run_migrations(connection):
    "Automatically creates or deletes tables and columns, reflecting code changes"
    ctx = MigrationContext.configure(connection)
    code = render_python_code(
        produce_migrations(ctx, Base.metadata).upgrade_ops, migration_context=ctx
    )
    if connection.engine.echo:
        # debug mode
        print(code)
    with Operations.context(ctx) as op:
        variables = {"op": op, "sa": sqlalchemy}
        exec("def run():\n" + code, variables)
        variables["run"]()
    connection.commit()


async def extract_legacy_settings(bot: "MusicBot"):
    "Load settings from deprecated json file to DB"
    if not os.path.isfile(LEGACY_SETTINGS):
        return
    with open(LEGACY_SETTINGS) as file:
        json_data = json.load(file)
    async with bot.DbSession() as session:
        existing = (
            (
                await session.execute(
                    select(GuildSettings.guild_id).where(
                        GuildSettings.guild_id.in_(list(json_data))
                    )
                )
            )
            .scalars()
            .fetchall()
        )
        for guild_id, data in json_data.items():
            if guild_id in existing:
                continue
            new_settings = DEFAULT_CONFIG.copy()
            new_settings.update({k: v for k, v in data.items() if k in new_settings})
            session.add(GuildSettings(guild_id=guild_id, **new_settings))
        await session.commit()
    os.rename(LEGACY_SETTINGS, LEGACY_SETTINGS + ".back")
