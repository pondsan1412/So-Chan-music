import asyncio
import discord
from config import config
from discord.ext import commands, bridge
from discord.ext.commands import has_permissions
from musicbot.bot import Context, MusicBot
from musicbot.audiocontroller import AudioController
import time

class General(commands.Cog):
    """A collection of the commands for moving the bot around in you server.

    Attributes:
        bot: The instance of the bot that is executing the commands.
    """

    def __init__(self, bot: MusicBot):
        self.bot = bot

    # logic is split to uconnect() for wide usage
    @bridge.bridge_command(
        name="join",
        description=config.HELP_CONNECT_LONG,
        help=config.HELP_CONNECT_SHORT,
        aliases=["c"],
    )
    async def _connect(self, ctx: Context):  # dest_channel_name: str
        audiocontroller = ctx.bot.audio_controllers[ctx.guild]
        if await audiocontroller.uconnect(ctx):
            await ctx.send("เชื่อมต่อแล้ว.")

    @bridge.bridge_command(
        name="leave",
        description=config.HELP_DISCONNECT_LONG,
        help=config.HELP_DISCONNECT_SHORT,
        aliases=["dc"],
    )
    async def _disconnect(self, ctx: Context):
        audiocontroller = ctx.bot.audio_controllers[ctx.guild]
        if await audiocontroller.udisconnect():
            await ctx.send("ตัดขาดการเชื่อมต่อ.")
        else:
            await ctx.send(config.NOT_CONNECTED_MESSAGE)
        ch_send = self.bot.get_channel(config.console_commanduse)
        await ch_send.send(f"{ctx.author} `using leave`")
    @bridge.bridge_command(
        name="reset",
        description=config.HELP_RESET_LONG,
        help=config.HELP_RESET_SHORT,
        aliases=["rs", "restart", "cc"],  # this command replaces removed changechannel
    )
    async def _reset(self, ctx: Context):
        await ctx.defer()
        if await ctx.bot.audio_controllers[ctx.guild].udisconnect():
            # bot was connected and need some rest
            await asyncio.sleep(1)

        audiocontroller = ctx.bot.audio_controllers[ctx.guild] = AudioController(
            self.bot, ctx.guild
        )
        if await audiocontroller.uconnect(ctx):
            await ctx.send(
                "{} เชื่อมต่อไปยัง {}".format(
                    ":white_check_mark:", ctx.author.voice.channel.name
                )
            )
        ch_send = self.bot.get_channel(config.console_commanduse)
        await ch_send.send(f"{ctx.author} `using reset`")

    @bridge.bridge_command(
        name="setting",
        description=config.HELP_SETTINGS_LONG,
        help=config.HELP_SETTINGS_SHORT,
        aliases=["settings", "set"],
    )
    @has_permissions(administrator=True)
    async def _settings(self, ctx: Context, setting=None, *, value=None):

        sett = ctx.bot.settings[ctx.guild]

        if setting is None and value is None:
            await ctx.send(embed=sett.format(ctx))
            return

        if setting is None or value is None:
            await ctx.send("Error: setting or value is missing.")
            return

        response = await sett.process_setting(setting, value, ctx)

        if response is None:
            await ctx.send("`Error: Setting not found`")
        elif response is True:
            async with ctx.bot.DbSession() as session:
                session.add(sett)
                await session.commit()
            await ctx.send("Setting updated!")

    @bridge.bridge_command(
        name="addbot",
        description=config.HELP_ADDBOT_LONG,
        help=config.HELP_ADDBOT_SHORT,
    )
    async def _addbot(self, ctx):
        embed = discord.Embed(
            title="Invite",
            description=config.ADD_MESSAGE
            + "({})".format(discord.utils.oauth_url(self.bot.user.id)),
        )

        await ctx.send(embed=embed)
    @bridge.bridge_command(name='credit', description=config.HELP_CREDIT_LONG, help=config.HELP_CREDIT_SHORT)
    async def _credit(self, ctx):
        global embedDonate,donate_url
        
        embed = discord.Embed(title='Developer of So-Chan',description="",color=discord.Color.blue())
        embed.set_image(url="https://camo.githubusercontent.com/84cff396f554e61c599fbab6e32959abd4862298944e26c68b8bb0a2579feddf/68747470733a2f2f7376312e7069637a2e696e2e74682f696d616765732f323032332f30322f32382f654e463772382e6d642e706e67")
        embed.set_footer(text="ชื่อบัญชี \n ธนาคารไทยพานิชย์ & พร้อมเพย์ \n เลขที่บัญชี 408-052219-9 \n พร้อมเพย์ 0639520317 ")
        await ctx.send(embed=embed)
    @bridge.bridge_command(
        name="feedback",
        help="feedback หา dev เผื่อเหตการณ์บอทเสียหรือต้องการแนะนำติเตือนใดๆ พร้อมรับฟังทั้งหมดครับ",
        description="this is like feedback dm to dev immediatly"
    )
    async def _feedback(self,ctx:commands.Context,ฝากข้อความถึงผู้พัฒนา):
        try:
            owner_bot = self.bot.get_channel(config.feedback_channel_id)
            await owner_bot.send(f"`{ctx.author}`{ฝากข้อความถึงผู้พัฒนา}")
            member = await self.bot.fetch_user(324207503816654859)
            await member.send(f"{ctx.author}{ฝากข้อความถึงผู้พัฒนา}")
            await ctx.send(f"ทางเราได้รับ feedback จากคุณ{ctx.author.mention} เรียบร้อยแล้วนะคะ")
            time.sleep(3)
            await ctx.send(f"จะมีการอัพเดทภายหลังโปรดติดตามการเคลื่อนไหวที่เพจ So-Chan ค่ะ {config.shy_cat}")
            
        except:
             pass
#donate 
embedDonate = discord.Embed(title='ชื่อบัญชี',description='ธนาคารไทยพานิชย์ & พร้อมเพย์ \n เลขที่บัญชี 408-052219-9 \n พร้อมเพย์ 0639520317')
donate_url = "https://i.pinimg.com/236x/eb/c8/c5/ebc8c5eb8077eca566b83387b6169ab2.jpg"

def setup(bot: MusicBot):
    bot.add_cog(General(bot))
