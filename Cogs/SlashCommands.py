
## Модули Disnake.
import disnake
from disnake.ext import commands
from disnake.ui import Button, View

## Другие модули.
import asyncio
import os
import random
import datetime
from requests import RequestException
from time import time

## Модули бота.
from main import STREAMER_NAME, TWITCH, DONAT, TG,\
    BOOSTY, DOOR_IMG_URL, ITS_OPENING_IMG_URL,\
    ADS_IMG_URL, ANON_DOOR, BOT_NAME, FOOTER_TEXT, BOT_PREFIX, \
    PRIVATE_CHANNELS_CATEGORY_ID_TEXT, PRIVATE_CHANNELS_CATEGORY_ID_VOICE, \
    DIRPATH
from bot_modules.casino_game.json_write import write_user_balance, get_bot_money, get_user_balance, add_balance_all_users
from bot_modules.casino_game import random_choise
from bot_modules.credit.write_credit_file import check_credit_file_exists, create_credit_file
from bot_modules.parsing_photo import FreepikImagesParser
from bot_modules.private_channels.text_channels.WriteJsonFile import write_text_channel_info
from bot_modules.private_channels.voice_channels.WriteJsonFileVoice import write_voice_channel_info
from bot_modules.investions import user_invest, set_invest
from bot_modules.investions.invest_graph import CourseJsonWriter
from bot_modules.command_logger import command_logger, cog_logger, error_logger
from bot_modules.words_game.parse_words import WordsParserGame, get_word_hash
from bot_modules.words_game.is_game_active_writer import check_game_state, write_new_game_state
from bot_modules.words_game.last_word_writer import write_new_last_word, check_last_word
from bot_modules.words_game.words_game_count import write_new_words_count, check_words_count
from bot_modules.words_game.hash_writer import check_old_hash, new_word_hash_write
from bot_modules.BotStats.ErrorsWriter import error_write
from bot_modules.work_game.user_work_writer import write_user_work, get_user_work_info

class SlashCommands(commands.Cog):
    """
    Ког с коммандами, выполняемыми через слэш ("/")
    """
    def __init__(
        self,
        bot=commands.Bot
    ) -> None:
        self.bot = bot


    @commands.slash_command(
        name="start_work",
        description="Начни получать деревяшки пока твой аватар \"работает\"!",
    )
    async def start_work(
        self,
        inter: disnake.AppCommandInteraction,
    ) -> None:
        """Команда записи .json файла о начале работы пользователя. 
        Если пользователю повезёт (90%), то он получит 100 деревяшек через 4 часа. Иначе ничего не получает.

        Args:
            inter (disnake.AppCommandInteraction): Disnake Interaction.
        """
        ## ожидание исполнения команды.
        await inter.response.defer()
        
        ## логирование команды.
        command_logger(
            global_name=inter.author.global_name,
            name=inter.author.name,
            command_name="start_work"
        )
        
        user_work_info: tuple = get_user_work_info(
            user_name=inter.author.name
        )
        if user_work_info is not None:
            await inter.send(
            embed=disnake.Embed(
                title="Не удалось начать работу",
                description=f"""
Уважаемый {inter.author.mention}, вы уже работаете `прямо сейчас`. :factory_worker:
"""
            )
            .set_author(
                name=BOT_NAME,
                icon_url=DOOR_IMG_URL
            )
            .set_footer(
                text=FOOTER_TEXT,
                icon_url=DOOR_IMG_URL
            )
            .set_thumbnail(
                url=ANON_DOOR
            )
        )
        
        ## Получаем случайное число между 0 и 1.
        random_num: float = round(random.random(), 2)
        
        ## Проводим подсчёт того, получит ли пользователь деревяшек.
        if random_num <= 0.90:
            add_wood: bool = True
        else:
            add_wood: bool = False
        
        ## Получаем количество секунд с начала эпохи.
        start_time: float = time()
        
        ## Записываем информацию о работе пользователя.
        write_user_work(
            user_name=inter.author.name,
            work_start_time=start_time,
            add_wood=add_wood,
            id=inter.author.id
        )
        
        await inter.send(
            embed=disnake.Embed(
                title="Работа начата",
                description=f"""
Уважаемый {inter.author.mention}, вы начали свою работу на нашем сервере. :factory_worker:
Возвращайтесь через 4 часа и `почти` наверняка получите свои **100** деревяшек! :wood:
"""
            )
            .set_author(
                name=BOT_NAME,
                icon_url=DOOR_IMG_URL
            )
            .set_footer(
                text=FOOTER_TEXT,
                icon_url=DOOR_IMG_URL
            )
            .set_thumbnail(
                url=ANON_DOOR
            )
        )


    @commands.slash_command(
        name="words_game",
        description="Хочешь поиграть в слова? Тогда попробуй отгадать загаданное слово! Меньше попыток - больше награда!"
    )
    async def words_game(
        self,
        inter: disnake.AppCommandInteraction,
        word: str
    ) -> None:
        """Игра в слова. Пользователь вводит слово. В ответ получает близость слова в процентах к загаданному.

        Args:
            inter (disnake.AppCommandInteraction)
            word (str): слово, которое вводит пользователь.
        """
        ## Ожидание исполнения команды.
        await inter.response.defer()
        
        ## Переводим word в нижний регистр для избежания проблем.
        word: str = word.lower()
        
        command_logger(
            global_name=inter.author.global_name,
            name=inter.author.name,
            command_name="/words_game",
            args=f"""
            word: {word}
            """
        )

        ## Сверка старого и нового хэша слов.
        old_word_hash: str = check_old_hash()
        new_hash: str = get_word_hash()
        
        if not old_word_hash == new_hash:
            new_word_hash_write(new_word_hash=new_hash)
            write_new_game_state(is_active=True)
            ## Запись в JSON всей необходимой информации.
            write_new_last_word(
                last_word=None,
                percent=0,
                angle=0
            )
            write_new_words_count(new_count=1)
        
        ## Если игра закончилась:
        if check_game_state() is False:
            await inter.send(
                embed=disnake.Embed(
                    title="Игра закончилась! :game_die:",
                    description=f"{inter.author.mention}, возвращайтесь завтра, чтобы попробовать угадать слово вновь!",
                    timestamp=datetime.datetime.now(),
                    color=disnake.Color.random()
                )
                .set_author(
                    name=BOT_NAME,
                    url=DOOR_IMG_URL,
                )
                .set_footer(
                    text=FOOTER_TEXT,
                    icon_url=DOOR_IMG_URL
                )
            )
            try:
                words_parser: WordsParserGame = WordsParserGame(word=None)
            except Exception:
                pass
            
            return None
        
        try:
            words_parser: WordsParserGame = WordsParserGame(word=word)
        except RequestException:
            await inter.send(
                embed=disnake.Embed(
                    title="Я не знаю такого слова!",
                    description=f"{inter.author.mention}, слово **\"{word}\"** мне неизвестно. Попробуйте другое.",
                    timestamp=datetime.datetime.now(),
                    color=disnake.Color.red()
                )
                .set_author(
                    name=BOT_NAME,
                    url=DOOR_IMG_URL,
                )
                .set_footer(
                    text=FOOTER_TEXT,
                    icon_url=DOOR_IMG_URL
                )
            )
            return None


        if words_parser.percent == 100:
            ## Получаем номер единственного сервера бота.
            guild: disnake.Guild = self.bot.guilds[0]
            ## Получаем число пользователей.
            all_members: int = guild.member_count
            words_count: int = check_words_count()
            ## Получаем число деревяшек, необходимых для деления на всех пользователей.
            money_to_add: int = round((all_members * 1_000) / words_count, 2)
            ## Количество слов, затраченных на отгадку.
            all_words_count: int = check_words_count()
            
            await inter.send(
                embed=disnake.Embed(
                    title=f"Мои поздравления! Слово было угадано за {all_words_count} попыток!",
                    description=f"""
{inter.author.mention}, слово **\"{word}\"** оказалось верным. Все участники сервера
получат по {money_to_add} деревяшек""",
                    timestamp=datetime.datetime.now(),
                    color=disnake.Color.green()
                )
                .set_author(
                    name=BOT_NAME,
                    url=DOOR_IMG_URL,
                )
                .set_footer(
                    text=FOOTER_TEXT,
                    icon_url=DOOR_IMG_URL
                )
            )
            ## Запись в JSON всей необходимой информации.
            write_new_game_state(is_active=False)
            write_new_last_word(
                last_word=None,
                percent=0
            )
            write_new_words_count(new_count=1)
            ## Добавляем деревяшки всем пользователям на сервере.
            try:
                add_balance_all_users(count=money_to_add)
            except Exception as error:
                error_logger(
                    error=error,
                    command_name="/words_game",
                    user_name=inter.author.global_name,
                    args=word,
                    line=174
                )
                error_write(
                    error=error
                )
            return None
        
        else:
            low_percent_variants: tuple = (
                "Слово оказалось неверным.",
                "Вы не угадали.",
                "Данное слово даже рядом не стоит с загаданным!"
            )
            middle_percent_variats: tuple = (
                "Неверно, загадано иное слово.",
                "Вы двигаетесь в верном направлении.",
                "Кажется, загаданное слово имеет другое значение."
            )
            high_percent_variants: tuple = (
                "Вы близки к разгадке!",
                "Уже почти отгадали!",
                "Слово уже близко!",
            )
            
            ## Получаем все необходимые переменные для дальнейшей работы действий.
            last_high_percent: int = check_last_word()[1]
            words_to_answer: tuple = None
            last_high_percent_word: str = check_last_word()[0]
            last_high_angle: int = check_last_word()[2]
            all_words_count: int = check_words_count()
            
            ## Проверка всех необходимых условий для добавления нового ближнего слова к загаданному.
            if words_parser.percent >= last_high_percent:
                write_new_last_word(
                    last_word=word,
                    percent=words_parser.percent,
                    angle=words_parser.angle
                )
                last_high_angle: int = words_parser.angle
                last_high_percent_word: str = words_parser.word
                last_high_percent: int = words_parser.percent
                
                
            ## Проверка близости слов к отгаданному для разнообразия ответов.
            if words_parser.percent < 50:
                words_to_answer = low_percent_variants
            elif words_parser.percent >= 50 and words_parser.percent <= 75:
                words_to_answer = middle_percent_variats
            else:
                words_to_answer = high_percent_variants
            
            await inter.send(
                embed=disnake.Embed(
                    title=random.choice(words_to_answer),
                    description=f"{inter.author.mention}, слово **\"{word}\"** оказалось неверным.",
                    timestamp=datetime.datetime.now(),
                    color=disnake.Color.red()
                )
                .add_field(
                    name="Процент угадывания:   |",
                    value=f"**{words_parser.percent}%**"
                )
                .add_field(
                    name="Угол нахождения слова относительно центра окружности: ",
                    value=f"**{words_parser.angle}°**",
                )
                .add_field(
                    name="Последнее слово с наивысшим процентом и его значение: ",
                    value=f"**{last_high_percent_word}** | **{last_high_percent}%** | **{last_high_angle}°**" ,
                    inline=False
                )
                .add_field(
                    name="Всего совершено попыток: ",
                    value=f"**{all_words_count}**",
                    inline=False
                )
                .set_author(
                    name=BOT_NAME,
                    url=DOOR_IMG_URL,
                )
                .set_footer(
                    text=FOOTER_TEXT,
                    icon_url=DOOR_IMG_URL
                )
            )
            ## Запись всех необходимых новых значений в файлы.
            write_new_words_count(
                new_count=all_words_count + 1
            )
            return None


    @commands.slash_command(
        name="random-choise",
        description="Случайно выбирает один из введённых вариантов. Пиши варианты только через пробел.",
    )
    async def random_choise(
        self,
        inter: disnake.AppCommandInteraction,
        variants: str
    ) -> None:
        """Случайно выбирает из предложенных вариантов один.
    
        Args:
            variants (str): Переданные варианты. 
        """
        
        ## Ожидание исполнения команды для избежания ошибок.
        await inter.response.defer()
        
        command_logger(
            global_name=inter.author.global_name,
            name=inter.author.name,
            command_name="/random-choise",
            args=f"Variants: {variants}"
        )
        
        ## Получение случайного варианта.
        if len(variants) > 220:
            await inter.send(
                content="В запросе слишком много символов, попрошу вас сократить его.",
                ephemeral=True
            )
            return None
        
        variants_list: list = list(variants.split())
        choise: str = random.choice(variants_list)
        
        ## Отправка сообщения.
        await inter.send(
            embed=disnake.Embed(
                title=f"<<<**{choise}**>>>",
                description=f'Среди вариантов "{variants}", я выбрал: "**{choise}**" :thinking:',
                color=disnake.Color.random(),
            )
            .set_author(name=inter.author.global_name, icon_url=inter.author.avatar.url)
            .set_footer(text=FOOTER_TEXT, icon_url=DOOR_IMG_URL)
            .set_thumbnail(url=ITS_OPENING_IMG_URL),
            ephemeral=True,
        )


    @commands.slash_command(
        name="help",
        description="Помощь и описание бота."
    )
    async def help(
        self,
        inter: disnake.AppCommandInteraction
    ) -> None:
        """
        Отправляет сообщение с описанием команд бота.
        """
        
        ## Ожидание исполнения команды для избежания ошибок.
        await inter.response.defer()
        
        command_logger(
            global_name=inter.author.global_name,
            name=inter.author.name,
            command_name="/help"
        )
        
        ## Текст для помощи пользователю.
        description: str = f"""
Бот, созданный специально для сервера "Дверной ДС"
НАШ БОТ "Just Door's __BOT__" - произведение искусства, разрабатываемое моим хорошим другом и настоящим компьютерным гением @Warnik
(От осознания, что этот текст писал не я, стало приятно :kissing_heart: ).

Это чудо - фундамент сервера с множеством возможностей, буквально наши МФЦ, банк, СМИ и т.п. 

ВСЕ команды для бота можно посмотреть, прописав "/" в строку ввода, а также хочу упомянуть, что бот способен отвечать на ваши вопросы,
если его упомянать через символ "@" или же отвечать на сообщения. Пользуйтесь, это бесплатно.
Основные особенности прописанны в канале "про-нашего-бота", советую туда заглянуть, если ещё не видел. :pushpin:

Для модерации и участников с повышенными правами есть команда "{BOT_PREFIX}помощь".
"""
        embed: disnake.Embed = disnake.Embed(
            title="/help",
            description=description,
            timestamp=datetime.datetime.now(),
            colour=disnake.Color.random(),
        ).set_footer(text=STREAMER_NAME, icon_url=DOOR_IMG_URL)
        
        button_money_help: Button = Button(
            label='Экономика',
            custom_id='economy_help_btn',
            style=disnake.ButtonStyle.green
        )
        view: View = View()
        view.add_item(button_money_help)
        
        await inter.send(
            embed=embed,
            ephemeral=True,
            view=view
        )


    @commands.slash_command(
        name="anonym_message",
        description="отправляет пользователю анонимное сообщение. (250)",
    )
    @commands.has_any_role()
    async def anonym_message(
        self,
        inter: disnake.ApplicationCommandInteraction,
        user_to_send: disnake.Member,
        message: str,
    ) -> None:
        """Отправляет пользоватю <user_to_send> анонимное сообщение <message>.
    
        Args:
            user_to_send (str): Пользователь для отправки сообщения. 
            message (str): Сообщение для отправки.
        """
        print("START COMMAND")
        
        ## Ожидание исполнения команды для избежания ошибок.
        await inter.response.defer()
        
        command_logger(
            global_name=inter.author.global_name,
            name=inter.author.name,
            command_name="/anonym_message",
            args=f"""
            user_to_send: {user_to_send}
            message: {message}
            """
        )
        
        
        ## Получение баланса бота и пользователя.
        bot_balance: float = get_bot_money()
        user_balance: float = get_user_balance(user_name=inter.author.name)
        
        ## Проверка хватает ли пользователю баланса.
        if user_balance < 250:
            await inter.send('У вас недостаточно деревяшек. Необходимо: 250')
            return None
            
        try:
            await user_to_send.send(
                embed=disnake.Embed(
                    title="Анонимное сообщение от кого-то  :eyes::",
                    description=message
                )
                .set_author(
                    name=STREAMER_NAME,
                    icon_url=DOOR_IMG_URL
                )
                .set_thumbnail(url=ANON_DOOR)
                .set_footer(
                    text=FOOTER_TEXT,
                    icon_url=DOOR_IMG_URL
                )
            )
            
            await inter.send(
                embed=disnake.Embed(
                    title="Сообщение отправлено! :thumbsup:"
                )
                .set_author(name=STREAMER_NAME, icon_url=DOOR_IMG_URL),
                    ephemeral=True
            )
            
            ## Снятие баланса у пользователя и его добавление в баланс бота.
            write_user_balance(
                user_name=inter.author.name,
                count=user_balance-250
                )
            write_user_balance(
                user_name=BOT_NAME,
                count=bot_balance + 250
                )
        
        except Exception:
            await inter.send(
                embed=disnake.Embed(
                    title="""
Отправить сообщение не удалось, скорее всего,
пользователь не принимает сообщений от неизвестных аккаунтов.
Либо же меня добавили в чёрный список. :cry:"""
                )
                .set_author(name=STREAMER_NAME, icon_url=DOOR_IMG_URL),
                    ephemeral=True
            )


    @commands.slash_command(
        name="image_request",
        description="Отправляет запрос в интернет и выводит картинку. (100)",
    )
    async def pictures_request(
            self,
            inter: disnake.CommandInteraction,
            request: str
        ) -> None:
        """Получает из интернета случайную картинку по запросу <request>.
    
        Args:
            request (str): Запрос для поиска картинок.
        """
        
        ## Ожидание исполнения команды для избежания ошибок.
        await inter.response.defer()
        
        command_logger(
            global_name=inter.author.global_name,
            name=inter.author.name,
            command_name="/image_request",
            args=f"""
            request: {request}
            """
        )
        
        ## Получение баланса пользователя и бота.
        bot_balance: float = get_bot_money()
        user_balance: float = get_user_balance(user_name=inter.author.name)
        
        ## Проверка хватает ли баланса пользователю.
        if user_balance < 100:
            await inter.send('У вас недостаточно деревяшек. Небходимо: *100*.')
            return None
        
        images_parser: FreepikImagesParser = FreepikImagesParser(request=request)
        image_url: str = images_parser.image_url
        ## Проверка результата работы парсера.
        await inter.send(
            embed=disnake.Embed(
                title=f'''Изображение по запросу "{request}" {random.choice([
                    ':thumbsup:', ':clap:', ':fire:', ':art:', ':heart:'
                    ])}''',
                color=disnake.colour.Color.random()
            )
            .set_author(
                name=STREAMER_NAME,
                icon_url=DOOR_IMG_URL
            )
            .set_footer(
                text=FOOTER_TEXT,
                icon_url=DOOR_IMG_URL
            )
            .set_image(image_url)
        )
        
        write_user_balance(
            user_name=inter.author.name,
            count=user_balance - 100
        )
        write_user_balance(
            user_name=BOT_NAME,
            count=bot_balance + 100
        )


    @commands.slash_command(
        name="casino_game",
        description="Ставь ставку, а вот выиграешь или нет - решать не тебе ;)",
    )
    async def casino_game(
            self,
            inter: disnake.CommandInteraction,
            bet: float
        ) -> None:
        """Наше личное казино. Пользователь ставит ставку, получает GIF изображение,
        в зависимости от проигрыша / выигрыша он получает или теряет монеты (деревяшки).
    
        Args:
            bet (float): Количество монет, которые ставит пользователь.
        """
        
        ## С целью избежания проблем округляем ставку.
        bet: float = round(bet, 2)
        
        ## Ожидание исполнения команды.
        await inter.response.defer()
        
        command_logger(
            global_name=inter.author.global_name,
            name=inter.author.name,
            command_name="/casino_game",
            args=f"""
            bet: {bet}
            """
        )
        
        ## Множитель монет при выигрыше.
        coefficent: int = 0
        
        ## Проверка является ли ставка положительной.
        if bet <= 0:
            await inter.send(
                "Ваша ставка должна составлять минимум **1** деревяшку и не быть отрицательной.",
                ephemeral=True,
                delete_after=5,
            )
            return None
        
        ## Получение баланса пользователя для проверки.
        user_balance_for_check: float = get_user_balance(user_name=inter.author.name)
        
        ## Если баланс пользователя больше ставки.
        if user_balance_for_check - bet < 0:
            await inter.send(
                "Вы не можете ставить деревяшек больше, чем их есть у вас.",
                ephemeral=True,
                delete_after=5,
            )
            return None
        
        ## Выбор победы / поражения случайным образом.
        choise: bool = random_choise.win_or_defeat()

        if choise:
            ## Могут быть 3 типа победы (если три одинаковых слота): RRR, DDD и PPP, их расчёт.
            win_type: str = random_choise.calc_inwin()

            if win_type == "RRR":
                file = disnake.File(
                    f"{DIRPATH}/images-for-bot/Spins_gif/rrr.gif", filename="spin.gif"
                )
                coefficent = 1
            elif win_type == "PPP":
                file = disnake.File(
                    f"{DIRPATH}/images-for-bot/Spins_gif/ppp.gif", filename="spin.gif"
                )
                coefficent = 4
            else:
                file = disnake.File(
                    f"{DIRPATH}/images-for-bot/Spins_gif/ddd.gif", filename="spin.gif"
                )
                coefficent = 9

            await inter.send(
                file=file,
                embed=disnake.Embed(
                    title="Спин-машина:",
                    color=disnake.Color.random(),
                )
                .set_author(
                    name=inter.author.global_name,
                    icon_url=inter.author.avatar.url
                )
                .set_image(url="attachment://spin.gif"),
                delete_after=8
            )
            ## Ожидание удаления spin-gif файла и вывод экрана победы.
            await asyncio.sleep(8)
            
            ## Вычисляем новый баланс пользователя и получаем баланс бота.
            user_balance: float = get_user_balance(user_name=inter.author.name)
            bot_balance: float = get_bot_money()
            new_user_balance: float = user_balance + bet * coefficent
            
            await inter.send(
                content="Вы выиграли!",
                embed=disnake.Embed(
                    title=f"Вы выиграли! Ваша ставка {bet}.   :clap:",
                    description=f"""
Ваш счёт **{new_user_balance}** деревяшек.
Множитель победы: {coefficent + 1} :moneybag:
                    """,
                    color=disnake.colour.Color.random(),
                )
                .set_author(
                    name=inter.author.global_name, icon_url=inter.author.avatar.url
                )
                .set_footer(text="Дверное казино."),
                delete_after=5,
            )
            write_user_balance(
                user_name=inter.author.name,
                count=new_user_balance
            )
            
            write_user_balance(
                user_name=BOT_NAME,
                count=bot_balance - bet * coefficent
            )

        else:
            
            file: disnake.File = disnake.File(
                f"{DIRPATH}/images-for-bot/Spins_gif/{random_choise.get_random_filename_defeat()}",
                filename="spin.gif",
            )
            
            await inter.send(
                file=file,
                embed=disnake.Embed(
                    title="Спин-машина:",
                    color=disnake.Color.random(),
                    )
                    .set_author(
                        name=inter.author.global_name, icon_url=inter.author.avatar.url
                    )
                    .set_image(url="attachment://spin.gif"),
                delete_after=8
            )
            ## Ожидание перед удалением spin.gif айла
            await asyncio.sleep(8)
            ## Новый баланс пользователя после проигрыша, получаем баланс бота.
            user_balance: float = get_user_balance(user_name=inter.author.name)
            bot_balance: float = get_bot_money()
            new_user_balance: float = user_balance - bet
            
            await inter.send(
                content="Вы проиграли!",
                embed=disnake.Embed(
                    title=f"Вы проиграли! Ваша ставка {bet}.   :thumbsdown:",
                    description=f"Ваш счёт **{new_user_balance}** деревяшек. :money_with_wings:",
                    color=disnake.colour.Color.random(),
                )
                .set_author(
                    name=inter.author.global_name, icon_url=inter.author.avatar.url
                )
                .set_footer(text="Дверное казино."),
                delete_after=5,
            )
            
            write_user_balance(
                user_name=inter.author.name,
                count=new_user_balance,
            ),
            write_user_balance(
                user_name=BOT_NAME,
                count=bot_balance + bet
            )


    @commands.slash_command(
        name="cells_casino",
        description="Попробуй угадать, под какими кнопками спрятан приз!",
    )
    async def cells_casino(
        self,
        inter: disnake.AppCommandInteraction
    ) -> None:
        
        ## Ожидание исполнения команды для избежания ошибок.
        await inter.response.defer()
        
        command_logger(
            global_name=inter.author.global_name,
            name=inter.author.name,
            command_name="/cells_casino",
            )
        
        ## Создание кнопок для казино.
        button_cell_1 = Button(
            style=disnake.ButtonStyle.red,
            label=1,
            custom_id="cell_1"
            )
        button_cell_2 = Button(
            style=disnake.ButtonStyle.green,
            label=2,
            custom_id="cell_2"
            )
        button_cell_3 = Button(
            style=disnake.ButtonStyle.primary,
            label=3,
            custom_id="cell_3"
            )
        button_cell_4 = Button(
            style=disnake.ButtonStyle.green,
            label=4,
            custom_id="cell_4"
            )
        button_cell_5 = Button(
            style=disnake.ButtonStyle.red,
            label=5,
            custom_id="cell_5"
            )

        ## Расположение кнопок на объекте View
        view = View()
        view.add_item(button_cell_1)
        view.add_item(button_cell_2)
        view.add_item(button_cell_3)
        view.add_item(button_cell_4)
        view.add_item(button_cell_5)
        
        await inter.send(
            embed=disnake.Embed(
                title="Дверное казино!",
                color=disnake.Color.random(),
                description="""
Нажми на кнопку, чтоб узнать что она скрывает.
Только одна принесёт прибыль. (кнопка постоянно меняется)
                """,
                )
                .set_author(
                    name=STREAMER_NAME,
                    icon_url=DOOR_IMG_URL
                )
                .set_thumbnail(
                    url=ITS_OPENING_IMG_URL
                ),
            view=view
        )   


    @commands.slash_command(
        name="get_user_avatar",
        description="Выводит аватар пользователя. (150)"
    )
    @commands.has_any_role()
    async def get_user_avatar(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member
    ) -> None:
        
        ## Ожидание исполнения команды для избежания ошибок.
        await inter.response.defer()
        
        command_logger(
            global_name=inter.author.global_name,
            name=inter.author.name,
            command_name="/get_user_avatar",
            args=f"""
            member: {member.global_name}
            """
        )
        
        bot_balance: float = get_bot_money()
        user_balance: float = get_user_balance(user_name=inter.author.name)
        
        if user_balance < 150:
            await inter.send(
                content='У вас недостаточно деревяшек. Необходимо *150*.',
                ephemeral=True
            )
            return None
        
        ## Получаем ссылку на изображение аватара пользователя.
        icon_url: str = member.avatar.url
        await inter.send(
            embed=disnake.Embed(
                title=f"Аватар пользователя **{member.global_name}** :maple_leaf::"
                )
                .set_image(url=icon_url)
                .set_footer(
                    icon_url=DOOR_IMG_URL,
                    text=FOOTER_TEXT
            )
        )

        write_user_balance(
            user_name=inter.author.name,
            count=user_balance - 150
        )
        write_user_balance(
            user_name=BOT_NAME,
            count=bot_balance + 150
        )


    @commands.slash_command(
        name="create_text_channel",
        description="Создаёт личный текстовый канал пользователя. (500)"
    )
    @commands.has_any_role()
    async def create_text_channel(
        self,
        inter: disnake.AppCommandInteraction,
        channel_name: str
    ) -> None:
        
        ## Ожидание исполнения команды для избежания ошибок.
        await inter.response.defer()
        
        command_logger(
            global_name=inter.author.global_name,
            name=inter.author.name,
            command_name="/create_text_channel",
            args=f"""
            channel_name: {channel_name}
            """
        )
        
        bot_balance: float = get_bot_money()
        user_balance: float = get_user_balance(user_name=inter.author.name)
        
        if user_balance < 500:
            await inter.send(
                'Недостаточно деревяшек для создания канала. Необходимо: *500*.',
                ephemeral=True
            )
            return None

        ## Получаем по ID категорию, куда будем создавать каналы.
        category: disnake.CategoryChannel = inter.guild.get_channel(PRIVATE_CHANNELS_CATEGORY_ID_TEXT)
        ## Проверка на существование канала с таким же названием.
        for channel in category.channels:
            if channel.name == channel_name:
                await inter.send(f"Канал с таким названием уже существует: {channel_name}.")
                return None
        
        if len(channel_name) >= 100:
            await inter.send(
                "Название канала должно быть менее 100 символов в длину.",
                ephemeral=True
            )
            return None
        
        channel: disnake.TextChannel = await category.create_text_channel(name=f"{channel_name}")
        write_text_channel_info(
            channel_name=channel_name,
            channel_id=channel.id,
        )
        ## Обновление канала.
        await channel.edit()
        
        write_user_balance(
            user_name=inter.author.name,
            count=user_balance - 500
        )
        write_user_balance(
            user_name=BOT_NAME,
            count=bot_balance + 500
        )
        
        await inter.send(
            embed=disnake.Embed(
                title="Отчёт о создании",
                description=f"Создан канал {channel.mention} в категории {category.name}. С вас списано 500 деревяшек.",
                color=disnake.Color.random(),
                timestamp=datetime.datetime.now(),
                )
                .set_footer(text="Ваша любимая дверь", icon_url=DOOR_IMG_URL),
            delete_after=20
        )


    @commands.slash_command(
        name="create_voice_channel",
        description="Создаёт личный голосовой канал пользователя. (500)"
    )
    @commands.has_any_role()
    async def create_voice_channel(
        self,
        inter: disnake.AppCommandInteraction,
        channel_name: str
    ):
        ## Ожидание исполнения команды для избежания ошибок.
        await inter.response.defer()

        command_logger(
            global_name=inter.author.global_name,
            name=inter.author.name,
            command_name="/create_voice_channel",
            args=f"""
            channel_name: {channel_name}
            """
        )
        
        bot_balance: float = get_bot_money()
        user_balance: float = get_user_balance(user_name=inter.author.name)
        
        if user_balance < 500:
            await inter.send(
                'Недостаточно деревяшек для создания канала. Необходимо *500* деревяшек.',
                ephemeral=True
            )
            return None
        
        ## Получаем категорию по её ID.
        category: disnake.CategoryChannel = inter.guild.get_channel(PRIVATE_CHANNELS_CATEGORY_ID_VOICE)

        for channel in category.channels:
            if channel.name == channel_name:
                await inter.send(f"Канал с таким названием уже существует: {channel_name}.")
                return 
        
        if len(channel_name) >= 100:
            await inter.send(
                "Название канала должно быть менее 100 символов в длину.",
                ephemeral=True
            )
            return None
            
        channel: disnake.VoiceChannel = await category.create_voice_channel(name=f"{channel_name}")
        write_voice_channel_info(
            channel_name=channel_name,
            channel_id=channel.id,
        )
        ## Обновляем канал.
        await channel.edit()
        
        write_user_balance(
            user_name=inter.author.name,
            count=user_balance - 500
        )
        write_user_balance(
            user_name=BOT_NAME,
            count=bot_balance + 500
        )
        
        await inter.send(
            embed=disnake.Embed(
                title="Отчёт о создании",
                description=f"Создан канал {channel.mention} в категории {category.name}. С вас списано 500 деревяшек.",
                color=disnake.Color.random(),
                timestamp=datetime.datetime.now(),
                )
                .set_footer(text="Ваша любимая дверь", icon_url=DOOR_IMG_URL),
            delete_after=20
        )


    @commands.slash_command(
        name="ads",
        description="Выводит список наших соц сетей."
    )
    async def show_ads(
        self,
        inter: disnake.AppCommandInteraction
    ) -> None:
        
        ## Ожидание исполнения команды для избежания ошибок.
        await inter.response.defer()
        
        command_logger(
            global_name=inter.author.global_name,
            name=inter.author.name,
            command_name="/ads"
        )
        
        description = f"""
Twitch: {TWITCH}
Telegram: {TG}
Boosty: {BOOSTY}
Donation alerts: {DONAT}
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Эй, т-сс, тут можно кинуть шекель на помощь нам     o((>ω< ))o"""
    
        await inter.send(
            embed=disnake.Embed(
                title="Наши ссылки",
                color=disnake.Color.random(),
                description=description
                )
                .set_footer(text=FOOTER_TEXT, icon_url=DOOR_IMG_URL)
                .set_author(name=STREAMER_NAME, icon_url=DOOR_IMG_URL)
                .set_image(url=ADS_IMG_URL)
        )


    @commands.slash_command(
        name="balance",
        description="Выводит ваш баланс деревяшек."
    )
    async def get_balance(
        self,
        inter: disnake.ApplicationCommandInteraction
    ) -> None:
        
        ## Ожидание исполнения команды для избежания ошибок.
        await inter.response.defer()
        
        user_icon: str = inter.author.avatar.url
        ## Получаем баланс пользователя.
        user_balance: float = get_user_balance(inter.author.name)
        
        command_logger(
            global_name=inter.author.global_name,
            name=inter.author.name,
            command_name="/balance"
        )
        
        await inter.send(
            embed=disnake.Embed(
                title="Баланс: ",
                description=f"**{inter.author.global_name}**, ваш баланс **{user_balance}** деревяшек(и) :moneybag:",
                )
                .set_author(
                    icon_url=user_icon,
                    name=inter.author.global_name
                )
                .set_footer(
                    icon_url=DOOR_IMG_URL,
                    text=FOOTER_TEXT
                ),
            delete_after=5
        )


    @commands.slash_command(
        name="transfer_money",
        description="Переводит пользователю (member) (count) деревяшек из вашего личного счёта. Комиссия: 5%",
    )
    @commands.has_any_role()
    async def transfer_money(
        self,
        inter: disnake.AppCommandInteraction,
        member: disnake.Member,
        count: float
    ) -> None:
        
        ## С целью избежания проблем округляем значение.
        count: float = round(count, 2)
        ## Ожидание исполнения команды для избежания ошибок.
        await inter.response.defer()
        
        command_logger(
            global_name=inter.author.global_name,
            name=inter.author.name,
            command_name="/transfer_money",
            args=f"""
            member: {member},
            count: {count}
            """
        )
        
        if member.name == BOT_NAME:
            await inter.send(
                "Безусловно, я рад вашему желанию помочь финансами мне, но такой необходимости нет :slight_smile:.",
                ephemeral=True,
            )
            return None
        
        if inter.author.name == member.name:
            await inter.send(
                "Вы не можете отсылать деревяшки **самому себе**.",
                ephemeral=True,
            )
            return None
        
        if count <= 0:
            await inter.send(
                "Вы не можете перевести ненатуральное число.",
                ephemeral=True,
            )
            return None
        
        bot_balance: float = get_bot_money()
        ## Баланс пользователя, который переводит
        user_balance: float = get_user_balance(user_name=inter.author.name)
        ## Баланс пользователя, которому переводят.
        member_to_transfer_balance: float = get_user_balance(user_name=member.name)
        ## Сумма, которую получит второй пользователь с учётом комиссиия 5 %.
        with_comission_count: float = round(count * 0.95, 2)

        if user_balance - count < 0:
            await inter.send(
                "Вы не можете отослать больше деревяшек, чем есть у вас.",
                ephemeral=True,
            )
            return None
        
        ## Получаем новые значения балансов пользователей.
        new_user_balance: float = user_balance - count
        new_member_to_transfer_balance: float = member_to_transfer_balance + with_comission_count
        
        write_user_balance(
            user_name=inter.author.name,
            count=new_user_balance
        )
        write_user_balance(
            user_name=member.name,
            count=new_member_to_transfer_balance
        )
        
        write_user_balance(
            user_name=BOT_NAME,
            count=bot_balance + (count - with_comission_count)
        )
        
        await inter.send(
            embed=disnake.Embed(
                title="Информация о переводе.",
                description=f"""
**{with_comission_count}** деревяшек(и) оправлены пользователю **{member.global_name}**.
Комиссия: **{count - with_comission_count}** :white_check_mark:""",
                timestamp=datetime.datetime.now(),
            )
            .set_footer(text=FOOTER_TEXT, icon_url=DOOR_IMG_URL),
            delete_after=6)


    @commands.slash_command(
        name="take_credit",
        description="Берёт кредит на <money> деревяшек."
    )
    async def take_credit(
        self,
        inter: disnake.AppCommandInteraction,
        money: float
    ) -> None:
        ## Ожидание исполнения команды для избежания ошибок.
        await inter.response.defer()
        money: float = round(money, 2)
        
        command_logger(
            global_name=inter.author.global_name,
            name=inter.author.name,
            command_name="/take_credit",
            args=f"""
            money: {money}
            """
        )
        
        if check_credit_file_exists(inter.author.name) is True:
            await inter.send(
                content="У вас уже есть незакрытый кредит.",
                ephemeral=True
                )
            return None
        
        user_balance: float = get_user_balance(user_name=inter.author.name)
        bot_balance: float = get_bot_money()

        if money <= 0:
            await inter.send(
                "Вы не можете брать кредит на сумму меньше 1-ой деревяшки.",
                ephemeral=True
            )

        elif user_balance < -50:
            await inter.send(
                "Вы не можете брать кредит с большим отрицательным счётом.",
                ephemeral=True
            )

        elif user_balance - money < -50:
            await inter.send(
                "Мы не можем выдать вам кредит т.к. он уведёт вас в минус более, чем на 50 деревяшек.",
                ephemeral=True
            )

        else:
            write_user_balance(
                user_name=inter.author.name,
                count=user_balance + money
            )
            create_credit_file(
                user_name=inter.author.name,
                count=money,
                author_id=inter.author.id
            )
            write_user_balance(
                user_name=BOT_NAME,
                count=bot_balance - money
            )
            
            ## Прочие вычисления для рассчёта выплаты кредита.
            credit_procent: float = money * 0.1
            money_to_return: float = round(money + credit_procent, 2)
            
            await inter.send(
                embed=disnake.Embed(
                    title=f"Уважаемый **{inter.author.global_name}**, вы взяли у нас кредит на **{money}** деревяшек.",
                    description=f"Через час мы изымаем взятые деревяшки с поверх наложенным процентом: 10%. Вы должны вернуть нам **{money_to_return}**.",
                ).set_footer(
                    text="Ваша любимая дверь",
                    icon_url=DOOR_IMG_URL
                    ),
                delete_after=10,
            )


    @commands.slash_command(
        name='buy_investments',
        description='Инвестируй в нашу валюту!'
        )
    async def buy_invest(
            self,
            inter: disnake.AppCommandInteraction,
            money: float
        ) -> None:
        
        ## Ожидание исполнения команды для избежания ошибок.
        await inter.response.defer()
        
        command_logger(
            global_name=inter.author.global_name,
            name=inter.author.name,
            command_name="/buy_investments",
            args=f"""
            money: {money}
            """
        )
        
        if money <= 0:
            await inter.send(
                'Вы не можете вкладывать ненатуральные числа.',
                ephemeral=True
            )
            return None
        
        bot_balance: float = get_bot_money()
        user_balance: float = get_user_balance(user_name=inter.author.name)
        
        if user_balance - money < 0:
            await inter.send(
                'У вас недостаточно баланса для данного вклада.',
                ephemeral=True
            )
            return None

        class_invest: user_invest.InvestJsonActions = user_invest.InvestJsonActions(inter.author.name)
        course: set_invest.InvestJsonActions = set_invest.InvestJsonActions().read_course_invest()
        
        ## Попытка чтения файла с инвестициями.
        try:
            user_investitions: float = class_invest.read_user_invest()
            
        except Exception:
            user_investitions: float = 0.0
        
        class_invest.write_user_invest(
            money=user_investitions + money / course
        )
        
        write_user_balance(
                user_name=inter.author.name,
                count=user_balance-money
        )
        write_user_balance(
                user_name=BOT_NAME,
                count=bot_balance+money
        )
        await inter.send(
            embed=disnake.Embed(
                title='Благодарим за вклад.',
                color=disnake.Color.random(),
                timestamp=datetime.datetime.now()
            )
            .add_field(name='Вы вложили:  |', value=money)
            .add_field(name='По курсу:  |', value=course)
            .add_field(name='На данный момент у вас:', value=class_invest.read_user_invest())
            .set_author(name=inter.author.global_name, url=inter.author.avatar),
            delete_after=10
        )


    @commands.slash_command(
        name='sell_investments',
        description='Продайте все свои инвестиции и получайте деревяшки! Налог: 10%'
        )
    async def sell_invest(
            self,
            inter: disnake.AppCommandInteraction,
        ) -> None:
        
        ## Ожидание исполнения команды для избежания ошибок.
        await inter.response.defer()
        
        command_logger(
            global_name=inter.author.global_name,
            name=inter.author.name,
            command_name="/sell_investments"
        )
        
        class_invest: user_invest.InvestJsonActions = user_invest.InvestJsonActions(inter.author.name)
        user_money: float = class_invest.read_user_invest()
        
        if user_money < 0:
            await inter.send(
                'У вас пустой баланс.',
                ephemeral=True
            )
            return None
        
        ## Получаем курс инвестиций.
        invest_course: float = set_invest.InvestJsonActions().read_course_invest()
        ## Балансы бота и пользователя.
        bot_balance: float = get_bot_money()
        user_balance: float = get_user_balance(user_name=inter.author.name)
        ## Вычисляем прибыль пользователя и комиссию.
        invest_balance: float = user_money * invest_course
        commission: float =  invest_balance * 0.1
        
        write_user_balance(
            user_name=inter.author.name,
            count=user_balance + (invest_balance - commission)
        )
        write_user_balance(
            user_name=BOT_NAME,
            count=bot_balance - (invest_balance - commission)
        )
        
        await inter.send(
            embed=disnake.Embed(
                title=f'Вы продали свои инвестиции в кол-ве {user_money}.',
                color=disnake.Color.random(),
                timestamp=datetime.datetime.now(),
            )
            .add_field(
                name='При продаже вы получили:  |',
                value=f'{invest_balance - commission} деревяшек.'
            )
            .add_field(
                name='По курсу:  |',
                value=invest_course
                )
            .add_field(
                name='Ваш баланс:',
                value=f'{round(user_balance + (invest_balance - commission)), 2}. (Учитывая 10% налога на прибыль)'
            )
            .set_author(
                name=inter.author.global_name,
                url=inter.author.avatar
            ),
            delete_after=10
        )
        os.remove(f'{user_invest.InvestJsonActions.USER_PATH}//{inter.author.name}.json')


    @commands.slash_command(
        name='check_investments',
        description='Узнайте курс валюты и её количество у вас.'
        )
    async def check_invest(
            self,
            inter: disnake.AppCommandInteraction,
        ) -> None:
        
        ## Ожидание исполнения команды для избежания ошибок.
        await inter.response.defer()
        
        command_logger(
            global_name=inter.author.global_name,
            name=inter.author.name,
            command_name="/check_investments"
        )
        
        ## Получаем курс инвестиций, создаём график инвестиций на его основе.
        invest: float = set_invest.InvestJsonActions().read_course_invest()
        course: CourseJsonWriter = CourseJsonWriter(invest)
        
        ## Попытка чтения файла.
        try:
            user_investitions: float = user_invest.InvestJsonActions(inter.author.name).read_user_invest()
        except Exception:
            user_investitions: float = 0.0
        
        await inter.send(
            embed=disnake.Embed(
                title='Информация о инвестициях.',
                color=disnake.Color.random(),
                timestamp=datetime.datetime.now(),
            )
            .add_field(
                name='Курс валюты: |',
                value=invest
            )
            .add_field(
                name='Ваш баланс валюты:',
                value=user_investitions
            )
            .set_author(
                name=inter.author.global_name,
                url=inter.author.avatar
            )
            .set_image(
                file=disnake.File(
                    fp=f"{course.DIRPATH}//graph.png",
                    filename="graph.png"
                    )
                ),
			ephemeral=True
        )




    ## Проверка нажатия кнопок. =========================================================================================================
    @commands.Cog.listener('on_button_click')
    async def cell_casino_check_bnt_click(
        self,
        inter: disnake.AppCommandInteraction
    ) -> None:
    
        
        command_logger(
            global_name=inter.author.global_name,
            name=inter.author.name,
            command_name="/cell_casino_check_bnt_click"
        )
        
        button_id: int = inter.component.custom_id
        button_num: str = inter.component.label
        lucky_btn_1: str = random.choice(["cell_1", "cell_2", "cell_3", "cell_4", "cell_5"])
        ## Получаем баланс пользователя и бота.
        user_balance: float = get_user_balance(user_name=inter.author.name)
        bot_balance: float = get_bot_money()
        
        if button_id == lucky_btn_1:
            await inter.send(
                f"""
Уважаемый {inter.author.global_name}, кнопка "{button_num}" верная! Вы получили 20 деревяшек! :clap:.
Ваш счёт: {user_balance + 20.0} деревяшек.""",
                delete_after=5
            )
            
            write_user_balance(
                user_name=inter.author.name,
                count=user_balance + 20.0
            )
            
            write_user_balance(
                user_name=BOT_NAME,
                count=bot_balance - 20.0
            )

        elif user_balance <= -200.0:
            await inter.send(
                "Кажется, вы наш должник на 200 деревяшек. Не переживайте. Мы дадим вам шанс выйти из долгов. Вам начисленно 50 деревяшек.",
                ephemeral=True,
            )
            
            write_user_balance(
                user_name=inter.author.name,
                count=user_balance + 50.0
            )
            write_user_balance(
                user_name=BOT_NAME,
                count=bot_balance - 50.0
            )
        
        elif button_id != lucky_btn_1 and button_id in ["cell_1", "cell_2", "cell_3", "cell_4", "cell_5"]:
            await inter.send(
                f"""
Упсс... Кнопка "{button_num}" неверная. С вас 5 деревяшек. :thumbsdown: 
Ваш счёт: {user_balance - 5} деревяшек.""",
                ephemeral=True,
                delete_after=5,
            )
            write_user_balance(
                user_name=inter.author.name,
                count=user_balance - 5.0
            )
            write_user_balance(
                user_name=BOT_NAME,
                count=bot_balance + 5.0
            )


    @commands.Cog.listener('on_button_click')
    async def check_help_btn_click(
        self,
        inter: disnake.AppCommandInteraction
    ) -> None:
        
        command_logger(
            global_name=inter.author.global_name,
            name=inter.author.name,
            command_name="/check_help_btn_click"
        )
        
        if inter.component.custom_id == 'economy_help_btn':
            description = '''
            На нашем сервере присутствует своя единая экономическая единица - деревяшки. :wood:
            '''
            embed=disnake.Embed(
                title='Информация о экономике.',
                description=description,
                timestamp=datetime.datetime.now(),
                color=disnake.Color.random()
            )
            embed.set_author(
                name=inter.author.global_name,
                icon_url=inter.author.avatar.url
                )
            embed.set_footer(
                text=FOOTER_TEXT,
                icon_url=DOOR_IMG_URL
                )
            embed.add_field(
                name="Их вы можете получать через такие команды, как:",
                value='''
                /casino_game,
                /cells_casino,
                /rand_number,
                /buy_investmens,
                /sell_investmens,
                /take_credit. -> потом необходима выплата с наложенными поверх
                :keycap_ten:%-ми.
                ''',
            )
            embed.add_field(
                name="Вы можете узнать свой баланс через комманду: ",
                value='''
                /balance. :bank:
                '''
            )
            embed.add_field(
                name="Перевод деревяшек можно осуществлять через команду:",
                value='''
                /transfer_money. При этом при переводе существует комиссия
                :five:%.
                ''',
            )
            embed.add_field(
                name="Дополнительная информация: ",
                value='''
                Помимо этого, за деревяшки может браться плата за совершение различных комманд.
                Тут пропишу с чего и сколько берут: :books:
                /create_text_channel - 500 деревяшек.
                /create_voice_channel - 500 деревяшек.
                /wiki_request - 250 деревяшек.
                /anonym_message - 250 деревяшек.
                /get_user_avatar - 150 деревяшек.
                /image_request - 100 деревяшек..
                ''',
            )
            
            await inter.send(
                embed=embed,
                ephemeral=True
            )

# Код для запуска и индeнтификации когов =============================================================================================================
def setup(bot=commands.Bot):
    bot.add_cog(SlashCommands(bot))
    cog_logger(cog_name="SlashCommands")
