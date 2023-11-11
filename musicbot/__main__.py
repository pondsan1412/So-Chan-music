import os
import sys
import random
import discord
from discord.ext import commands,tasks

from config import config
from musicbot.bot import MusicBot
from musicbot.utils import OutputWrapper, check_dependencies

initial_extensions = [
    "musicbot.commands.music",
    "musicbot.commands.general",
]


intents = discord.Intents.all()
if config.BOT_PREFIX:
    intents.message_content = True
    prefix = config.BOT_PREFIX
else:
    config.BOT_PREFIX = config.actual_prefix
    prefix = " "  # messages can't start with space
if config.MENTION_AS_PREFIX:
    prefix = commands.when_mentioned_or(prefix)

if config.ENABLE_BUTTON_PLUGIN:
    intents.message_content = True
    initial_extensions.append("musicbot.plugins.button")

bot = MusicBot(
    command_prefix=prefix,
    case_insensitive=True,
    status=discord.Status.online,
    
    intents=intents,
    allowed_mentions=discord.AllowedMentions.none(),
    
)

    
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    elif message.author.name =="So-Chan":
        return message.author
    elif message.author.name =="Xenon V2 Result Notifer":return
    username = str(message.author).split('#')[0]
    user_message = str(message.content)
    channel = str(message.channel.name)
    ch = bot.get_channel(config.console_fetchmsg)
    await ch.send(f"{username}  'พูดว่า'  `{user_message}`  ' in '  {channel}")
    if message.channel.name == bot.user:
        return
    if message.content.startswith('!get_servers'):
    # ดึง server ทั้งหมดที่บอทเชื่อมต่ออยู่
        servers = bot.guilds
        # ส่งข้อความกลับไปยัง channel ที่รับข้อความเข้ามา
        await message.channel.send(f'The bot is currently in {len(servers)} servers:')
        for server in servers:
            await message.reply(server.name)
    if message.content == "!sv_in":
        servers = bot.guilds
        await message.channel.send(f"{len(servers)}servers!")
    await bot.process_commands(message)
    random_num = random.randint(1, 10)
    #if random_num <= 5:
        #random_emoji = random.choice(config.emoji_sochan)
        #await message.add_reaction(random_emoji)
@bot.event
async def on_member_join(member): 
    guild = bot.get_guild(config.main_guild) # ใส่ ID ของ Guild เข้าไป
    random_message = random.choice(config.welcome_message)
    if member.guild == guild:
        channel = bot.get_channel(config.welcome_ch)
        embed = discord.Embed(title=f"{member.name}", description=f"{random_message}\n {member.mention}", color=0x00ff00)
        embed.set_thumbnail(url=member.avatar.url)
        await channel.send(embed=embed)
        await member.create_dm()
        await member.dm_channel.send("สวัสดีค่ะ ")
    # สร้าง Role ชื่อ Members ถ้ายังไม่มี
    role = discord.utils.get(member.guild.roles, name="Members")
    if role is not None:
        await member.add_roles(role)

@bot.event
async def on_member_remove(member):
    guild = bot.get_guild(config.main_guild) # ใส่ ID ของ Guild เข้าไป
    if member.guild == guild:
        channel = bot.get_channel(config.leave_ch) # ใส่ ID ของ Channel ที่ต้องการส่งข้อความ
        await channel.send(f'{member.mention} ได้ออกจาก server ของเราแล้ว หวังว่าจะได้พบกันใหม่นะคะ') # ข้อความต้อนรับเมื่อออกจาก Guild

if __name__ == "__main__":

    config.ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))
    config.COOKIE_PATH = config.ABSOLUTE_PATH + config.COOKIE_PATH

    sys.stdout = OutputWrapper(sys.stdout)
    sys.stderr = OutputWrapper(sys.stderr)

    if "--run" in sys.argv:
        print(os.getpid())

    check_dependencies()

    if not config.BOT_TOKEN:
        print("Error: No bot token!")
        exit()

    bot.load_extensions(*initial_extensions)

    bot.run(config.BOT_TOKEN, reconnect=True)
