import disnake
from disnake.ext import commands
from loguru import logger
from os import path, getenv
from dotenv import load_dotenv


## Подгрузка ENV среды.
load_dotenv()

## Путь к директории main файла.
DIRPATH = path.dirname(__file__)

## Другие константы. 

## Названия команд, используемых через <BOT_PREFIX>
PREFIX_COMMANDS: list = [
    "!оборот",
    "!пинг",
    "!очистка",
    "!баланс",
    "!штраф",
    "!начислить",
    "!таймаут",
    "!снять-таймаут",
    "!кик",
    "!бан",
    "!пинг"
    "!выход",
    "!сброс_ии",
    "!начисление",
    "!бот"
]


## ID-s
CREATOR_ID: list = [1048955787227176970, 1202978226415337573, 1048960192877953094]
GUILD_ID: int = 1202980243648815125

PRIVATE_CHANNELS_CATEGORY_ID_TEXT: int = 1209563008599064687
PRIVATE_CHANNELS_CATEGORY_ID_VOICE: int = 1209563008599064687
## Канал для уведомлений о начале стрима.
STREAM_NOTIFICATION_CHANNEL: int = 1202980244139671564

## Касаемо стримера.
STREAMER_NAME: str = "NoNiFoW"
TWITCH: str = "https://www.twitch.tv/nonifow"
DONAT: str = "https://www.donationalerts.com/r/nonifow"
TG: str = "https://t.me/NoNiFoW_Door"
BOOSTY: str = "https://boosty.to/nonifow"
BOT_NAME: str = "Just Door's _BOT_"
FOOTER_TEXT: str = "Ваша любимая дверь."

## Изображения
DOOR_IMG_URL: str = "https://cdn.discordapp.com/attachments/1262663005783719957/1262663067603439668/door.jpg?ex=66976a1e&is=6696189e&hm=778179c6bfc2e86e05dd6d59d72a51cbce6df6e755538c1146315bf6e7b7a5c6&"
DOOR_GIF_URL: str = "https://cdn.discordapp.com/attachments/1262663005783719957/1262663090365927434/door_open.gif?ex=66976a23&is=669618a3&hm=f4869884780834aa8494cad5cce8f9c5382eb47d05cc0df16a8fd3c3cb006539&"
ITS_OPENING_IMG_URL: str = "https://cdn.discordapp.com/attachments/1262663005783719957/1262663080186347540/its_opening.png?ex=66976a21&is=669618a1&hm=a442ea54032593ad41ec677a4043c8e204419c65e212ffe40f8287b305cd573c&"
EMPTY_IMG_URL: str = "https://cdn.discordapp.com/attachments/1262663005783719957/1262663081826320404/not_found.jpeg?ex=66976a21&is=669618a1&hm=bd572d491066d7994d09b63b2e11a0f0e1686785f4e63eea0af0c9dc9a8b9935&"
ADS_IMG_URL: str = "https://cdn.discordapp.com/attachments/1262663005783719957/1262663065447567412/ads.png?ex=66976a1d&is=6696189d&hm=d070ecf667c6734e9e5a94c1cd848637843cdacea8ca10004f06bc81848a6d88&"
ANON_DOOR: str = "https://cdn.discordapp.com/attachments/1208854198112886814/1209940925716107376/scale_1200.png?ex=6696c64c&is=669574cc&hm=318fa7d4090b09b9c83001ba8e0af994a04ad267723ad0ccf049287db88231c5&"
HELLO_IMG_URL: str = "https://cdn.discordapp.com/attachments/1262663005783719957/1268963924632539136/85bca13086722386.png?ex=66ae563f&is=66ad04bf&hm=87d6d71877290362313aa76dc3f01f3ebd8ebad7245c3a9a4931f7d00f69472c&"


## Создание логгера для отладки ошибок.
logger.add(
    f"{DIRPATH}/LOGS.log",
    rotation="1 MB",
    compression="zip"
)

## Создание экземпляра бота.
BOT_PREFIX: str = "!"
bot: commands.Bot = commands.Bot(
    command_prefix=BOT_PREFIX,
    activity=disnake.Game(
        name="Дверное казино",
        platform="Python"
    ),
    intents=disnake.Intents.all()
)

## Дополнительная настройка бота.
bot.remove_command("help")
bot.load_extensions("Cogs/")

## Запуск бота.
TOKEN: str = getenv("TOKEN")

try:    
    bot.run(TOKEN)
except Exception as error:
    logger.error(f"""
        {BOT_NAME} error LOGGER >>>
        При использовании <MAIN>
        с агрументами <<NONE>>
        произошла ошибка: <<<{error}>>>
        на строке №90.
        <<<
        """
    )