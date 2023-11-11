# fmt: off

import os
import json

from musicbot.utils import get_env_var, alchemize_url


DEFAULTS = {
    "BOT_TOKEN": "MTA2NjM2MjYzMDY2NDYxNzk5NA.GJCxEd.r0G3Xfv5VTtD7dNaODhogRdTD-jvfJDIfHyFS0",
    "SPOTIFY_ID": "edfd77eaf8ce45beb5044a60c23891c4",
    "SPOTIFY_SECRET": "14975270a1b146e9b931b7638305130f",

    "BOT_PREFIX": "!",  # set to empty string to disable
    "ENABLE_SLASH_COMMANDS": True,

    "VC_TIMEOUT": 600,  # seconds
    "VC_TIMOUT_DEFAULT": True,  # default template setting for VC timeout true= yes, timeout false= no timeout

    "MAX_SONG_PRELOAD": 5,  # maximum of 25
    "MAX_HISTORY_LENGTH": 10,
    "MAX_TRACKNAME_HISTORY_LENGTH": 15,

    # if database is not one of sqlite, postgres or MySQL
    # you need to provide the url in SQL Alchemy-supported format.
    # Must be async-compatible
    # CHANGE ONLY IF YOU KNOW WHAT YOU'RE DOING
    "DATABASE_URL": os.getenv("HEROKU_DB") or "sqlite:///settings.db",
}


if os.path.isfile("config.json"):
    with open("config.json") as f:
        DEFAULTS.update(json.load(f))
elif not os.getenv("DANDELION_INSTALLING"):
    with open("config.json", "w") as f:
        json.dump(DEFAULTS, f, indent=2)


for key, default in DEFAULTS.items():
    globals()[key] = get_env_var(key, default)


MENTION_AS_PREFIX = True

ENABLE_BUTTON_PLUGIN = True

EMBED_COLOR = 0x4dd4d0  # replace after'0x' with desired hex code ex. '#ff0188' >> '0xff0188'

SUPPORTED_EXTENSIONS = (".webm", ".mp4", ".mp3", ".avi", ".wav", ".m4v", ".ogg", ".mov")


COOKIE_PATH = "/config/cookies/cookies.txt"

GLOBAL_DISABLE_AUTOJOIN_VC = True

ALLOW_VC_TIMEOUT_EDIT = True  # allow or disallow editing the vc_timeout guild setting


actual_prefix = (  # for internal use
    BOT_PREFIX
    if BOT_PREFIX
    else ("/" if ENABLE_SLASH_COMMANDS else "@bot ")
)

# set db url during install even if it's overriden by env
if os.getenv("DANDELION_INSTALLING") and not DATABASE_URL:
    DATABASE_URL = DEFAULTS["DATABASE_URL"]
DATABASE = alchemize_url(DATABASE_URL)
DATABASE_LIBRARY = DATABASE.partition("+")[2].partition(":")[0]


STARTUP_MESSAGE = "Starting Bot..."
STARTUP_COMPLETE_MESSAGE = "Startup Complete"

NO_GUILD_MESSAGE = "Error: โปรดเข้าร่วมช่องเสียงหรือป้อนคำสั่งในแชท server"
USER_NOT_IN_VC_MESSAGE = "Error: โปรดเข้าร่วมช่องเสียงก่อนใช้คำสั่ง"
WRONG_CHANNEL_MESSAGE = "Error: โปรดใช้ช่องคำสั่งที่กำหนดค่าไว้"
NOT_CONNECTED_MESSAGE = "Error: บอทไม่ได้เชื่อมต่อกับช่องเสียงใดๆค่ะ"
ALREADY_CONNECTED_MESSAGE = "Error: เชื่อมต่อกับช่องเสียงอยู่แล้วค่ะ"
CHANNEL_NOT_FOUND_MESSAGE = "Error: หาห้องไม่เจอค่ะ"
DEFAULT_CHANNEL_JOIN_FAILED = "Error: ไม่สามารถเข้าร่วม default voice channel"
INVALID_INVITE_MESSAGE = "Error: ลิงก์คำเชิญไม่ถูกต้อง"

ADD_MESSAGE = "ในการเพิ่มบอทนี้ไปยังเซิร์ฟเวอร์ของคุณเอง, click [here]"  # brackets will be the link text

INFO_HISTORY_TITLE = "Songs Played:"

SONGINFO_UPLOADER = "ผู้อัพโหลด: "
SONGINFO_DURATION = "ระยะเวลา:  "
SONGINFO_SECONDS = "s"
SONGINFO_LIKES = "Likes: "
SONGINFO_DISLIKES = "Dislikes: "
SONGINFO_NOW_PLAYING = "Now Playing"
SONGINFO_QUEUE_ADDED = "ถูกเพิ่มไปยัง Queue"
SONGINFO_SONGINFO = "Song info"
SONGINFO_ERROR = "Error: ไม่สามารถเล่นเพลงนี้ได้ อาจจะติดปัญหาจำกัดอายุ หรือ content ที่ เป็นเฉพาะ member \n หรืออื่นๆ"
SONGINFO_PLAYLIST_QUEUED = "Queued playlist :page_with_curl:"
SONGINFO_UNKNOWN_DURATION = "Unknown"
QUEUE_EMPTY = "Queue is empty :x:"

HELP_ADDBOT_SHORT = "เพิ่ม Bot ไปยังเซิร์ฟเวอร์อื่น"
HELP_ADDBOT_LONG = "ให้ลิงค์สำหรับเพิ่มบอทนี้ไปยังเซิร์ฟเวอร์อื่นของคุณ."
HELP_CONNECT_SHORT = "เชื่อมต่อบอทกับช่องเสียง"
HELP_CONNECT_LONG = "เชื่อมต่อบอทกับช่องเสียงที่คุณอยู่"
HELP_DISCONNECT_SHORT = "ตัดการเชื่อมต่อบอทจากช่องเสียง"
HELP_DISCONNECT_LONG = "ตัดการเชื่อมต่อบอทจากช่องเสียงและหยุดเสียง."

HELP_SETTINGS_SHORT = "ดูและตั้งค่าบอท"
HELP_SETTINGS_LONG = "View and set bot settings in the server. Usage: {}settings setting_name value".format(actual_prefix)

HELP_HISTORY_SHORT = "แสดงประวัติของเพลง"
HELP_HISTORY_LONG = "แสดง " + str(MAX_TRACKNAME_HISTORY_LENGTH) + " เพลงที่เล่นล่าสุด."
HELP_PAUSE_SHORT = "หยุดเพลงชั่วคราว"
HELP_PAUSE_LONG = "หยุด AudioPlayer ชั่วคราว ใช้อีกครั้งเพื่อเล่นต่อ."
HELP_VOL_SHORT = "Change volume %"
HELP_VOL_LONG = "Changes the volume of the AudioPlayer. Argument specifies the % to which the volume should be set."
HELP_PREV_SHORT = "ย้อนกลับไปเพลงก่อนหน้า"
HELP_PREV_LONG = "เล่นเพลงก่อนหน้าอีกครั้ง."
HELP_SKIP_SHORT = "ข้ามเพลง"
HELP_SKIP_LONG = "ข้ามเพลงที่กำลังเล่นอยู่และไปที่รายการถัดไปในคิว."
HELP_SONGINFO_SHORT = "ข้อมูลเกี่ยวกับเพลงปัจจุบัน"
HELP_SONGINFO_LONG = "แสดงรายละเอียดเกี่ยวกับเพลงที่กำลังเล่นและโพสต์ลิงก์ไปยังเพลง."
HELP_STOP_SHORT = "หยุดเพลง"
HELP_STOP_LONG = "Stops the AudioPlayer and clears the songqueue"
HELP_MOVE_LONG = f"{actual_prefix}move [position] [new position]"
HELP_MOVE_SHORT = "ย้ายแทร็กในคิว"
HELP_YT_SHORT = "เล่นเพลงที่ด้วย link หรือ พิมพ์ keyword"
HELP_YT_LONG = f"{actual_prefix}p [link/video title/keywords/playlist/soundcloud link/spotify link/bandcamp link/twitter link]"
HELP_PING_SHORT = "Pong"
HELP_PING_LONG = "Test bot response status"
HELP_CLEAR_SHORT = "เคลียร์คิว."
HELP_CLEAR_LONG = "ล้างคิวและข้ามเพลงปัจจุบัน."
HELP_LOOP_SHORT = "วนซ้ำเพลงหรือคิวที่กำลังเล่นอยู่."
HELP_LOOP_LONG = "วนซ้ำเพลงหรือคิวที่กำลังเล่นอยู่. Modes are all/single/off."
HELP_QUEUE_SHORT = "แสดงเพลงในคิว."
HELP_QUEUE_LONG = "Shows the number of songs in queue, up to 10."
HELP_SHUFFLE_SHORT = "สับเปลี่ยนคิว"
HELP_SHUFFLE_LONG = "สุ่มเรียงเพลงในคิวปัจจุบัน"
HELP_RESET_SHORT = "ตัดการเชื่อมต่อและเชื่อมต่อใหม่"
HELP_RESET_LONG = "หยุดเครื่องเล่น ตัดการเชื่อมต่อ และเชื่อมต่อกับช่องที่คุณอยู่อีกครั้ง"
HELP_REMOVE_SHORT = "ลบเพลง"
HELP_REMOVE_LONG = "อนุญาตให้ลบเพลงออกจากคิวโดยพิมพ์ตำแหน่ง (ค่าเริ่มต้นคือเพลงสุดท้าย)."
HELP_CREDIT_SHORT = "ข้อมูลนักพัฒนาบอท So-Chan"
HELP_CREDIT_LONG = "ข้อมูลของนักพัฒนา discord bot `So-Chan` และผู้ร่วมลงทุนการพัฒนาบอทตัวนี้"
HELP_LYRICS_SHORT = "แสดงเนื้อเพลงต่างๆ เช่น `!lyrics fix you coldplay` "
HELP_LYRICS_LONG = "แสดงเนื้อเพลงตา่งๆที่ เราต้องการ แต่ไม่ support เพลงไทย"
ABSOLUTE_PATH = ""  # do not modify
#variable to keep string
welcome_message = [
        'สวัสดีค่ะ',
        'ยินดีต้อนรับค่ะ',
        'ขอบคุณที่เป็นส่วนหนึ่งของ support! ',
        'จ๊ะเอ๋ ไครเอ่ย สวัสดีค่าาา',
        'สวัสดีค่ะ เราชื่อ Sochiki น้าา',
        'landing สู่พื้นที่ราบแห่งเสียงเพลง!!!',
        'ระหว่าง หนูกับ gpt ใครเจ๋งกว่ากัน ก็ต้องหนูอยู่แล้วเพราะหนูเปิดเพลงได้!',
        'นายท่านคนนี้ชื่ออะไรน้า ?? ',
        'welcome',
        'Sochiki is happy because you are here!',
        'เธอๆ ชื่ออะไรหรอ'
    ]
#embed_set_footer string
footer_string = "ติดตามข่าวสารการอัพเดทของหนูได้ที่ https://www.facebook.com/SoChanbot"
#channel variable to send feedback
feedback_channel_id = 1091711073603825684
console_fetchmsg = 1091710526100357202
console_commanduse = 1091710872453394503
welcome_ch = 1091610073664606230
leave_ch = 1091696684603551794
#guilds
main_guild = 1091610073073205288

#emoji
shy_cat = "<:cattoblush:1043380595595673600>"
anime_girl_dance = "<a:emoji_3:981139432059072513>"
emoji_sochan = [
    "<a:star1:965527914336624640>",
    "<a:2182shakethecat:981752511734108241>",
    "<a:3581catdead:981752511088177264>",
    "<:5608zerotwoflushed:981752702759493632>",
    "<:8785zerouwu:981752702402977865>",
    "<:9263zerotwoveryhappy:981752702994374687>",
    "<a:emoji_3:981139432059072513>",
    "<a:joyrow:1043380805541568512>",
    "<a:coco:1043380621910736896>",
    "<:3301kittyblush:981625562793660436>",
    "<a:capoo:1043380579523100773>",
    "<a:Verify:1048059234291564544>"
    ]
cute_bunny = "<a:uwu:1048059229904326736>"
#user_id
dev_pond = 324207503816654859

#embed image url
set_image_sochan = "https://cdn.discordapp.com/attachments/1082055411462586499/1099250694915104769/2.gif"
pfp_sochan = "https://cdn.discordapp.com/attachments/1082055411462586499/1082374273861161101/332154821_143394278332108_2809636197604585268_n.png"

