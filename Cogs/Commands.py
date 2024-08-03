
## Модули Disnake.
import disnake
from disnake.ext import commands

## Другие модули.
from loguru import logger
import json
from os import listdir
import datetime

## Модули бота.
from main import BOT_PREFIX, DIRPATH, GUILD_ID, CREATOR_ID,\
    DOOR_IMG_URL, BOT_NAME
from bot_modules.casino_game.json_write import get_bot_money, get_user_balance, write_user_balance, get_turnover
from bot_modules import articles
from bot_modules.BotStats.SpeedTest import calculate_download_speed
from bot_modules.BotStats.ErrorsWriter import error_write
from bot_modules.ai_response.json_writter import JSON_PATH
from bot_modules.ai_response.ai_response import get_response
from bot_modules.ai_response.json_writter import write_into_json
from bot_modules.command_logger import cog_logger, command_logger

## TODO: Если баланс бота ушёл в минус или пользователь превысил миллион, сделать события. Сделать скрытые команды.

class Commands(commands.Cog):
    """
    Класс с командами, вызываемых через <BOT_PREFIX>.
    """
    
    def __init__(
        self,
        bot=commands.Bot
    ) -> None:
        self.bot = bot


    @commands.command(
        name="сброс_ии",
        brief=f"{BOT_PREFIX}сброс_ии"
        )
    @commands.has_guild_permissions(
        administrator=True
    )
    async def memory_cleaner(
        self,
        ctx: commands.Context
    ) -> None:
        """Очистка памяти ИИ.

        Args:
            ctx (commands.Context)
        """
        command_logger(
            global_name=ctx.author.global_name,
            name=ctx.author.name,
            command_name=f"{BOT_PREFIX}сброс_ии"
        )
        
        write_into_json(
            json_path=JSON_PATH,
            data={
                    'role': 'user',
                    'content': f"{ctx.author.global_name}: Я стираю тебе память! \
                        Попрошу высказать своё мнение об этом. Говори на русском и покороче!"
            }
        )
        ## Получаем ответ на запрос от ИИ.
        ai_response: str = get_response()
        ## Пересоздаём JSON с контекстом
        with open(JSON_PATH, "w+", encoding="utf-8") as file:
            json.dump(
                {
                    "history": [
                        {
                            "role": "user",
                            "content": "𝓦𝓪𝓻𝓷𝓲𝓚: Привет! Твоё имя - Just Door's _BOT_. \
                                Ты находишься в discord сервере. С тобой будут общаться разные пользователи, \
                                их имена будут показаны перед сообщением.\
                                Развлекай, отвечай на вопросы и отдыхай со всеми! Буду рад общению с тобой! Все говорят на русском, ты тоже."
                        },
                    ],
                },
                file,
                indent=4,
                ensure_ascii=False
            )
        await ctx.send(f"{ai_response} \n **- Память успешно стёрта!**")


    @commands.command(
        name="очистка",
        brief=f"{BOT_PREFIX}очистка <количество сообщений(изначально: весь канал)>"
    )
    @commands.has_permissions(
        manage_channels=True
    )
    async def clear(
        self,
        ctx: commands.Context,
        messages_count: int = 999_999
    ) -> None:
        """Команда очистки канала. Позволяет производить его очистку полностью.

        Args:
            ctx (commands.Context)
        """
        
        command_logger(
            global_name=ctx.author.global_name,
            name=ctx.author.name,
            command_name=f"{BOT_PREFIX}очистка",
            args=f"messages_count: {messages_count}"
        )
        
        ## Очистка чата Discord.
        await ctx.channel.purge(limit=messages_count)


    @commands.command(
        name="баланс",
        brief = '!баланс @<member>'
    )
    @commands.has_permissions(
        moderate_members=True,
    )
    async def get_balance(
        self,
        ctx: commands.Context,
        member: disnake.Member
    ) -> None:
        """
        Команда просмотра баланса пользователя <member> в деревяшках.

        Args:
            ctx (commands.Context),
            member (disnake.Member): участник сервера, баланс которого будем получать.
        """
        
        command_logger(
            global_name=ctx.author.global_name,
            name=ctx.author.name,
            command_name=f"{BOT_PREFIX}баланс",
            args=f"member: {member}"
        )
        
        if (ctx.author.guild is not None 
        and ctx.author.guild_permissions.view_audit_log):
            
            ## Получаем необходимую информацию о пользователе.
            user_icon: str = member.avatar.url
            balance: float = get_user_balance(user_name=member.name)
        
            await ctx.send(
                embed=disnake.Embed(
                    title="Баланс: ",
                    description=f"{member.global_name}: баланс {balance} деревяшек(и)",
                )
                .set_author(
                    icon_url=user_icon,
                    name=member.global_name
                )
                .set_footer(
                    icon_url=DOOR_IMG_URL,
                    text="Ваша любимая дверь"
                ),
                delete_after=8
            )

        elif ctx.author.guild is None:
            await ctx.send(
                f"Нельзя использовать {BOT_PREFIX}баланс в ЛС",
                ephemeral=True,
                delete_after=4
            )
        else:
            await ctx.send(
                f"У вас недостаточно прав для использования {BOT_PREFIX}баланс",
                ephemeral=True,
                delete_after=4,
            )


    @commands.command(
        name="пинг",
        brief=f"{BOT_PREFIX}пинг"
        )
    @commands.has_permissions(
        administrator=True
    )
    async def ping(
        self,
        ctx: commands.Context
    ) -> None:
        """Команда администрации для проверки работоспособности бота.
        Позволяет узнать количество произошедших ошибок за время работы бота,
        а также скорость интернета в МБ/С.
        
        Args:
            ctx (commands.Context)
        """
        
        command_logger(
            global_name=ctx.author.global_name,
            name=ctx.author.name,
            command_name=f"{BOT_PREFIX}пинг",
        )
        
        ## Показываем, что команда успешно сработала.
        await ctx.send(
            "Ждите... Производится проверка состояния бота.",
            delete_after=5
        )
        
        ## Вычисление скорости сети, получение информации об ошибках.
        download_speed: float = calculate_download_speed()
        dirlist: list = listdir(f"{DIRPATH}/Errors/")
        if dirlist != []:
            bot_status: str = f"Обнаружены ошибки. Ошибок: {len(dirlist)}"
        else:
            bot_status: str = "Ошибки не обнаружены."
            
        ## Вывод информации в чат Discord через Embed.
        await ctx.send(
            embed=disnake.Embed(
                title=f"{ctx.author.global_name}, проверка завершена!",
                timestamp=datetime.datetime.now(),
                color=disnake.Color.green() if bot_status == "Ошибки не обнаружены." else disnake.Color.red()
            )
            .add_field(
                name="Скорость сети:",
                value=f"**{download_speed} МБ/С**"
                )
            .add_field(
                name="Статус бота:",
                value=f"**{bot_status}**"
            )
        )


    @commands.command(
        name="оборот",
        brief=f"{BOT_PREFIX}оборот"
    )
    @commands.has_guild_permissions(
        administrator=True
    )
    async def check_full_balance(
        self,
        ctx: commands.Context
    ) -> None:
        """Проверяет оборот деревяшек во всех JSON файлах и показывает их в чате.

        Args:
            ctx (commands.Context):
        """
        command_logger(
            global_name=ctx.author.global_name,
            name=ctx.author.name,
            command_name=f"{BOT_PREFIX}оборот",
        )
        ## Получаем оборот деревяшек.
        full_balance: float = get_turnover()
        
        await ctx.send(
            content=f"Весь оборот деревяшек: {full_balance}",
            delete_after=8
        )


    @commands.command(
        name="штраф",
        brief = '!штраф @<member> <число>'
    )
    @commands.has_permissions(
        moderate_members=True
    )
    async def take_fine(
        self,
        ctx: commands.Context,
        member: disnake.Member,
        fine: float
    ):
        """Забирает штраф у пользователя.

        Args:
            ctx (commands.Context): 
            member (disnake.Member): Пользователь, у которого взымают штраф.
            fine (float): Сумма штрафа.
        """
        
        fine: float = round(fine, 2)
        
        command_logger(
            global_name=ctx.author.global_name,
            name=ctx.author.name,
            command_name=f"{BOT_PREFIX}штраф",
            args=f"""
                member: {member},
                fine: {fine}
            """
        )
        
        ## Получаем баланс пользователя.
        member_balance: float = get_user_balance(user_name=member.name)
        bot_balance: float = get_bot_money()
        ## Новый баланс.
        new_balance: float = member_balance - fine
        
        write_user_balance(
            member.name,
            count=new_balance
        )

        write_user_balance(
            user_name=BOT_NAME,
            count=bot_balance + fine
        )

        await ctx.send(
            embed=disnake.Embed(
                title="Штраф успешно взят!",
                description=f"С {member.name} взят штраф {fine} деревяшек(и).",
                timestamp=datetime.datetime.now(),
            )
            .set_footer(
                text="Ваша любимая дверь.",
                icon_url=DOOR_IMG_URL
            ),
            delete_after=5,
        )


    @commands.command(
        name="начислить",
        brief = '!начислить @<member> <число>'
        )
    @commands.has_permissions(
        moderate_members=True,
    )
    async def give_money(
        self,
        ctx: commands.Context,
        member: disnake.Member,
        money: float
    ) -> None:
        """Начисляет пользователю баланс из общего оборота.

        Args:
            ctx (commands.Context):
            member (disnake.Member): Пользователь, которому будет проиходить перевод валюты.
            money (float): Сумма перевода.
        """
        
        money: float = round(money, 2)
        
        command_logger(
            global_name=ctx.author.global_name,
            name=ctx.author.name,
            command_name=f"{BOT_PREFIX}начислить",
            args=f"""
                member: {member},
                money: {money}
            """
        )
        
        member_balance: float = get_user_balance(user_name=member.name)
        bot_balance: float = get_bot_money()
        
        new_balance: float = member_balance + money
        
        write_user_balance(
            member.name,
            count=new_balance
        )
        write_user_balance(
            user_name=BOT_NAME,
            count=bot_balance - money
        )

        await ctx.send(
            embed=disnake.Embed(
                title="Деревяшки начисленны!",
                description=f"{member.name} начисленно {money} деревяшек.",
                timestamp=datetime.datetime.now(),
            )
            .set_footer(
                text="Ваша любимая дверь.",
                icon_url=DOOR_IMG_URL)
        )


    @commands.command(
        name="помощь"
    )
    @commands.has_permissions(
        manage_roles=True
    )
    async def help(
        self,
        ctx: commands.Context
    ) -> None:
        """Команда помощи для модерации / администрации сервера. Содержит все
        команды, вызываемые через <BOT_PREFIX>.
        
        Args:
            ctx (commands.Context)
        """
        
        command_logger(
            global_name=ctx.author.global_name,
            name=ctx.author.name,
            command_name=f"{BOT_PREFIX}помощь",
        )
        
        await ctx.send(
            embed=disnake.Embed(
                title="Команды, для которых необходимы повышенные права.",
                description="""
"!оборот" -> показывает оборот деревяшек.

"!пинг" -> Анализ состояния сети и бота.

"!очистка <messages, изначально: весь канал>" -> очищает канал на указанное кол-во сообщений, если не указать, то весь канал.

"!баланс <@username>" -> показывает баланс деревяшек пользователя @username.

"!штраф <@username> <money>" -> взымает с пользователя @username штраф в размере (money).

"!начислить <@username> <money>" -> Выдаёт пользователю @username деревяшки в кол-ве (money). Без комиссии.

"!таймаут" <@username> <минуты> <статья> <причина (Если не указана статья)> -> Выдаёт пользователю тайм-аут.

"!снять-таймаут" <@username> -> Снимает с пользователя тайм-аут.

"!кик" <@username> <статья> <причина (Если не указана статья)> -> Выгоняет пользователя с сервера.

"!бан" <@username> <статья> <причина (Если не указана статья)> -> Банит пользователя на сервере.
""",
                timestamp=datetime.datetime.now(),
                colour=disnake.Color.random(),
            ).set_footer(text="Ваша любимая дверь", icon_url=DOOR_IMG_URL)
        )


    @commands.command(name='бот')
    async def check_bot(
        self,
        ctx: commands.Context
    ) -> None:
        """Получение информации о сервере, канале и пользователях на сервере.

        Args:
            ctx (commands.Context)
        """
        
        command_logger(
            global_name=ctx.author.global_name,
            name=ctx.author.name,
            command_name=f"{BOT_PREFIX}бот",
        )
        
        ## Проверка является ли этот ID одного из главных администраторов.
        if ctx.author.id in CREATOR_ID:
            ## Сбор информации.
            channel: list = [ctx.channel.name, ctx.channel.id]
            server: list = [ctx.guild.name, ctx.guild.id]
            all_members: list = [len(ctx.guild.members), ctx.guild.members]

            logger.info(f"""
                {channel}, \n
                {server}, \n
                {all_members}
                """
            )
            await ctx.send('Информация записана в логи!')
        else:
            await ctx.send('К сожалению, не похоже, что вы создатель данного бота. Данная команда доступна только @Warnik и @JustDoor.')


    @commands.command(
        name="таймаут",
        brief="!таймаут <@member> <минуты> <статья> <причина (если не указана статья)>",
    )
    @commands.has_guild_permissions(
        mute_members=True
    )
    async def timeout(
        self,
        ctx: commands.Context,
        member: disnake.Member,
        minutes: int,
        article: str,
        reason: str = "Статья",
    ) -> None:
        """Отправка пользователя в тайм-аут.

        Args:
            ctx (commands.Context),
            member (disnake.Member) пользователь, которого отправляем в тайм-аут.
            minutes (int) время для отправки в тайм-аут.
            article (str) статья из правил.
            reason (str, optional): Причина. Defaults to "Статья".
        """
        
        command_logger(
            global_name=ctx.author.global_name,
            name=ctx.author.name,
            command_name=f"{BOT_PREFIX}таймаут",
            args=f"""
                member: {member},
                minutes: {minutes},
                article: {article},
                reason: {reason}
            """
        )
        ## Получаем время для тайм-аута.
        time: float = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
        
        try:
            ## Создаём embed окно для окна канала.
            embed: disnake.Embed = disnake.Embed(
                title=f"""Пользователь **{member}** отправлен в тайм-аут на **{minutes}** минут(ы)""",
                description=f"""по статье:
                    \n-> **{article}: {articles.ARTICLES[article]}**
                    \nПричина: {reason}  :white_check_mark:""",
                timestamp=datetime.datetime.now(),
            )
            embed.set_footer(text="Ваша любимая дверь", icon_url=DOOR_IMG_URL)
            embed.set_author(
                name=ctx.author.global_name,
                icon_url=ctx.author.avatar.url
            )
            ## Создаём embed окно, для пользователя, которого отправляют в тайм-аут.
            embed_to_user: disnake.Embed = disnake.Embed(
                title=f""":octagonal_sign: Вы отправлены в тайм-аут на **{minutes}** минут(ы)""",
                description=f"""по статье:\n
                    -> **{article}: {articles.ARTICLES[article]}**
                    \nПричина: {reason} 
                    Сервер: **{self.bot.get_guild(GUILD_ID)}**. В тайм-аут отправлен пользователем: **{ctx.author.global_name}** 🚫""",
                timestamp=datetime.datetime.now(),
            )
            embed_to_user.set_footer(
                text="Ваша любимая дверь",
                icon_url=DOOR_IMG_URL
            )
            embed_to_user.set_author(
                name=ctx.author.global_name,
                icon_url=ctx.author.avatar.url
            )

            ## Оправка всех сообщений и выдача тайм-аута пользователю.
            await ctx.send(embed=embed)
            await member.send(embed=embed_to_user)
            await member.timeout(reason=reason, until=time)
        
        except Exception as err:
            await ctx.send(
                embed=disnake.Embed(
                    title="Произошла ошибка:",
                    description=f"{err}"
                )
            )
            error_write(error=str(err))
            logger.error(err)


    @commands.command(
        name="кик",
        brief="!кик <@member> <статья> <причина (если не указана статья)>"
    )
    @commands.has_guild_permissions(
        kick_members=True
    )
    async def kick(
        self,
        ctx: commands.Context,
        member: disnake.Member,
        article: str,
        reason: str = "Статья",
    ) -> None:
        
        """Удаление пользователя с сервера.

        Args:
            ctx (commands.Context),
            member (disnake.Member) пользователь, которого удаляем с сервера.
            article (str) статья из правил.
            reason (str, optional): Причина. Defaults to "Статья".
        """
        
        command_logger(
            global_name=ctx.author.global_name,
            name=ctx.author.name,
            command_name=f"{BOT_PREFIX}кик",
            args=f"""
                member: {member},
                article: {article},
                reason: {reason}
            """
        )
        
        try:
            ## Embed для отправки в чат.
            embed: disnake.Embed = disnake.Embed(
                title=f"""Пользователь **{member}** был выгнан по статье: """,
                description=f"""\n-> **{article}: {articles.ARTICLES[article]}**
                    \nПричина: {reason}  :white_check_mark:""",
                timestamp=datetime.datetime.now(),
            )
            
            embed.set_footer(
                text="Ваша любимая дверь",
                icon_url=DOOR_IMG_URL
            )
            embed.set_author(
                name=ctx.author.global_name,
                icon_url=ctx.author.avatar.url
            )
            ## Embed для отправки пользователю.
            embed_to_user = disnake.Embed(
                title=f""":octagonal_sign: Вас выгнали с сервера **{self.bot.get_guild(GUILD_ID)}** по причине: """,
                description=f"""-> **{article}: {articles.ARTICLES[article]}**
                    \nПричина: {reason}

                    Выгнан пользователем: **{ctx.author.global_name}** """,
                timestamp=datetime.datetime.now(),
            )
            embed_to_user.set_footer(
                text="Ваша любимая дверь",
                icon_url=DOOR_IMG_URL
            )
            embed_to_user.set_author(
                name=ctx.author.global_name,
                icon_url=ctx.author.avatar.url
            )

            ## Отправка сообщений.
            await ctx.send(embed=embed)
            await member.send(embed=embed_to_user)
            await member.kick(reason=reason)

        except Exception as err:
            logger.error(err)
            error_write(error=str(err))


    @commands.command(
        name="бан",
        brief="!бан <@member> <статья> <причина (если не указана статья)>"
    )
    @commands.has_permissions(
        ban_members=True
    )
    async def ban(
        self,
        ctx: commands.Context,
        member: disnake.Member,
        article: str,
        reason: str = "Статья",
    ) -> None:
        
        """Бан пользователя на сервере.

        Args:
            ctx (commands.Context),
            member (disnake.Member) пользователь, которого баним на сервере.
            article (str) статья из правил.
            reason (str, optional): Причина. Defaults to "Статья".
        """
        
        command_logger(
            global_name=ctx.author.global_name,
            name=ctx.author.name,
            command_name=f"{BOT_PREFIX}бан",
            args=f"""
                member: {member},
                article: {article},
                reason: {reason}
            """
        )
        
        try:
            embed: disnake.Embed = disnake.Embed(
                title=f"""Пользователь **{member}** был забанен по причине: """,
                description=f"""\n-> **{article}: {articles.ARTICLES[article]}**
                    \nПричина: {reason}  ::white_check_mark""",
                timestamp=datetime.datetime.now(),
            )
            embed.set_footer(
                text="Ваша любимая дверь",
                icon_url=DOOR_IMG_URL
            )
            embed.set_author(
                name=ctx.author.global_name,
                icon_url=ctx.author.avatar.url
            )

            embed_to_user: disnake.Embed = disnake.Embed(
                title=f""":octagonal_sign: Вас забанили на сервере **{self.bot.get_guild(GUILD_ID)}** по причине: """,
                description=f"""\n-> **{article}: {articles.ARTICLES[article]}**
                    \nПричина: {reason}  :white_check_mark:

                    Забанен пользователем: **{ctx.author.global_name}** """,
                timestamp=datetime.datetime.now(),
            )
            embed_to_user.set_footer(
                text="Ваша любимая дверь",
                icon_url=DOOR_IMG_URL
            )
            embed_to_user.set_author(
                name=ctx.author.global_name,
                icon_url=ctx.author.avatar.url
            )

            ## Отправка сообщений.
            await ctx.send(embed=embed)
            await member.send(embed=embed_to_user)
            await member.ban(reason=reason, clean_history_duration=604799)

        except Exception as err:
            logger.error(err)
            error_write(error=str(err))


    @commands.command(
        name="снять_таймаут",
        brief="!снять_таймаут <@member>"
    )
    @commands.has_guild_permissions(
        mute_members=True
    )
    async def un_timeout(
        self,
        ctx: commands.Context,
        member: disnake.Member
    ) -> None:
        """Вывод пользователя из тайм-аута.

        Args:
            ctx (commands.Context),
            member (disnake.Member) пользователь, с которого снимаем тайм-аут.
        """
        
        command_logger(
            global_name=ctx.author.global_name,
            name=ctx.author.name,
            command_name=f"{BOT_PREFIX}снять_таймаут",
            args=f"""
                member: {member},
            """
        )
        try:
            embed: disnake.Embed = disnake.Embed(
                title=f"С пользователя **{member}** снят тайм-аут :white_check_mark:",
                timestamp=datetime.datetime.now(),
            )
            embed.set_footer(text="Ваша любимая дверь", icon_url=DOOR_IMG_URL)
            embed.set_author(
                name=ctx.author.global_name,
                icon_url=ctx.author.avatar.url
            )

            embed_to_user: disnake.Embed = disnake.Embed(
                title=f"""С вас снят тайм-аут. Сервер: **{self.bot.get_guild(GUILD_ID)}**.
                    Тайм-аут снят пользователем: **{ctx.author.global_name}**""",
                timestamp=datetime.datetime.now(),
            )
            embed_to_user.set_footer(text="Ваша любимая дверь", icon_url=DOOR_IMG_URL)
            embed_to_user.set_author(
                name=ctx.author.global_name,
                icon_url=ctx.author.avatar.url
            )
            
            ## Отправляем пользователю сообщения.
            await ctx.send(embed=embed)
            await member.send(embed=embed_to_user)
            await member.timeout(reason=None, until=None)
            
        except Exception as err:
            logger.error(err)
            error_write(error=str(err))


    @commands.command(name='выход')
    async def exit_bot(
        self,
        ctx: commands.Context
    ) -> None:
        """Выключение бота.

        Args:
            ctx (commands.Context),
        """
        
        command_logger(
            global_name=ctx.author.global_name,
            name=ctx.author.name,
            command_name=f"{BOT_PREFIX}выход",
        )
        
        if ctx.author.id in CREATOR_ID:
            await ctx.send('Выход!')
            exit()
        else:
            await ctx.send('К сожалению, не похоже, что вы создатель данного бота. Данная команда доступна только @Warnik и @JustDoor.')
    
    
    @commands.command(
        name="начисление",
        )
    async def add_money(
        self,
        ctx: commands.Context,
        member: disnake.Member,
        money: float
    ) -> None:
        """Начисляет пользователю валюту "из воздуха". Не из общего оборота.

        Args:
            ctx (commands.Context),
            member (disnake.Member): пользователь, которому начисляем монеты.
            money (float): количество начисляемых монет.
        """
        
        money: float = round(money, 2)
        
        command_logger(
            global_name=ctx.author.global_name,
            name=ctx.author.name,
            command_name=f"{BOT_PREFIX}начисление",
            args=f"""
                member: {member},
                money: {money}
            """
        )
        ## Проверка является ли этот ID одного из главных администраторов.
        if ctx.author.id in CREATOR_ID:
            member_balance: float = get_user_balance(user_name=member.name)
            new_balance: float = member_balance + money
            write_user_balance(
                member.name,
                count=new_balance
            )

            await ctx.send(
                embed=disnake.Embed(
                    title="Деревяшки начисленны!",
                    description=f"{member.name} начисленно {money} деревяшек.",
                    timestamp=datetime.datetime.now(),
                )
                .set_footer(
                    text="Ваша любимая дверь.",
                    icon_url=DOOR_IMG_URL
                )
            )
        else:
            await ctx.send('К сожалению, не похоже, что вы создатель данного бота. Данная команда доступна только @Warnik и @JustDoor.')


def setup(bot=commands.Bot):
    bot.add_cog(Commands(bot))
    cog_logger(cog_name="Commands")
