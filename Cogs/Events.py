
## Модули Disnake.
import disnake
from disnake.ext import commands
from disnake.ext import tasks
import disnake.http

## Другие модули.
from loguru import logger
import asyncio
import datetime
import random
import os
from typing import Union
from time import time

## Модули бота.
from main import CREATOR_ID, STREAMER_NAME, DONAT, \
    DOOR_GIF_URL, DOOR_IMG_URL, ITS_OPENING_IMG_URL, \
    HELLO_IMG_URL, BOT_NAME, TWITCH, STREAM_NOTIFICATION_CHANNEL, \
    PREFIX_COMMANDS, FOOTER_TEXT
from bot_modules.check_stream import check_stream
from bot_modules.credit.write_credit_file import get_info_from_credit, directory_path
from bot_modules.casino_game.json_write import get_bot_money, get_user_balance, write_user_balance
from bot_modules.private_channels.text_channels import WriteJsonFile
from bot_modules.private_channels.voice_channels import WriteJsonFileVoice
from bot_modules.investions.set_invest import InvestJsonActions
from bot_modules.investions.invest_graph import CourseJsonWriter
from bot_modules.BotStats.ErrorsWriter import error_write
from bot_modules.ai_response.ai_response import get_response
from bot_modules.ai_response.json_writter import write_into_json, JSON_PATH
from bot_modules.command_logger import event_logger, cog_logger, command_logger, error_logger
from bot_modules.work_game.user_work_writer import get_user_work_info, WORK_PATH

## Прочие константы.
DIR_CREDIT_PATH = directory_path


class Events(commands.Cog):
    def __init__(
        self,
        bot = commands.Bot
    ) -> None:
        self.bot = bot
        ## Значение False/True влияет на проверку начала стрима.
        self.checking_streamer = True
    
    
    @commands.Cog.listener("on_ready")
    async def on_ready(self) -> None:
        """
        Запуск всего необходимого при загрузке бота.
        """
        ## Получаем объект канала для логирования.
        self.logs_channel: disnake.TextChannel = self.bot.get_channel(1268855280566009876)
        
        ## Информирование о запуске бота.
        logger.info(">>> Bot: Just Door's __BOT__ ---> Online.")
        ## Запуск всех "loop" задач и ивентов.
        self.check_users_count.start()
        self.check_streamer.start()
        self.take_credit.start()
        self.checking_stream.start()
        self.check_delete_private_text_channel.start()
        self.check_delete_private_voice_channel.start()
        self.set_investions.start()
        self.check_user_work.start()
    
    
    @tasks.loop(minutes=5)
    async def check_user_work(
        self
    ) -> None:
        """
        Каждые 5 минут проверяем файл работы пользователя для его удаления и начисления деревяшек.
        """
        
        event_logger(
            bot_name=BOT_NAME,
            event_name="check_user_work"
        )
        
        ## Все файлы директории WORK_PATH
        all_work_files: list = os.listdir(WORK_PATH)
        ## Перечисляем все файлы в директории.
        for work_file in all_work_files:
            ## Получаем информацию о пользователе.
            user_work_info: tuple = get_user_work_info(
                user_name=work_file.replace(".json", "")
            )
            ## Структурируем информацию.
            work_start_time: float = user_work_info[0]
            add_wood: bool = user_work_info[1]
            user_id: int = user_work_info[2]
            
            ## Получаем объект пользователя.
            user_to_check: disnake.User = self.bot.get_user(user_id)
            
            ## Проверка достаточно ли прошло времени.
            if time() - work_start_time <= 14_400:
                return None
            
            ## Получаем баланс пользователя.
            user_balance: float = get_user_balance(
                user_name=user_to_check.name
            )
            
            ## Если пользователю необходимо добавлять деревяшки.
            if add_wood is True:
                ## Создаём новый баланс пользователя.
                new_user_balance: float = user_balance + 100
                
                ## Попытка отправить сообщение пользователю.
                try:
                    await user_to_check.send(
                        embed=disnake.Embed(
                            title="Ваша работа завершилась!",
                            description=f"""
Уважаемый {user_to_check.mention}, вы получаете **100** деревяшек за свою работу.
Ваш баланс на данный момент: {new_user_balance}
                            """,
                            color=disnake.Color.green(),
                            timestamp=datetime.datetime.now()
                        )
                        .set_author(
                            name=BOT_NAME,
                            icon_url=DOOR_IMG_URL
                        )
                        .set_footer(
                            text=FOOTER_TEXT,
                            icon_url=DOOR_IMG_URL
                        )
                    )
                ## Если пользователь не принимает сообщения.
                except Exception as error:
                    error_logger(
                        error=error,
                        command_name="check_user_work",
                        line=92
                    )
                ## Запись баланса пользователя.
                finally:
                    write_user_balance(
                        user_name=user_to_check.name,
                        count=new_user_balance
                    )
                    os.remove(f"{WORK_PATH}/{user_to_check.name}.json")
            else:
                ## Попытка отправить сообщение пользователю.
                try:
                    await user_to_check.send(
                        embed=disnake.Embed(
                            title="Ваша работа завершилась!",
                            description=f"""
Уважаемый {user_to_check.mention}, к сожалению, ваша работа закончилась неудачей!
Ваш баланс на данный момент: {user_balance}
                            """,
                            color=disnake.Color.red(),
                            timestamp=datetime.datetime.now()
                        )
                        .set_author(
                            name=BOT_NAME,
                            icon_url=DOOR_IMG_URL
                        )
                        .set_footer(
                            text=FOOTER_TEXT,
                            icon_url=DOOR_IMG_URL
                        )
                    )
                ## Если пользователь не принимает сообщения.
                except Exception as error:
                    error_logger(
                        error=error,
                        command_name="check_user_work",
                        line=142
                    )
                
                finally:
                    os.remove(f"{WORK_PATH}/{user_to_check.name}.json")


    @tasks.loop(minutes=1)
    async def check_users_count(self) -> None:
        """
        Каждую минуту делать проверку количества пользователей на сервере и записывать их число в название канала.
        """
        event_logger(
            bot_name=BOT_NAME,
            event_name="check_users_count"
        )
        
        counter_channel: disnake.TextChannel = self.bot.get_channel(1268244585184886936)
        guild: disnake.Guild = self.bot.guilds[0]
        member_count: int = guild.member_count
        await counter_channel.edit(name=f"Участников: {member_count}")
    
    @tasks.loop(minutes=5)
    async def set_investions(self) -> None:
        """
        Раз в пять минут делать проверку инвестиций
        """
        event_logger(
            bot_name=BOT_NAME,
            event_name="set_investitions"
        )
        
        class_invest: InvestJsonActions = InvestJsonActions()
        class_invest.set_new_course()
        invest: float = class_invest.read_course_invest()
        course: CourseJsonWriter = CourseJsonWriter(invest)
        course.write_new_course()
    
    
    @tasks.loop(hours=4)
    async def checking_stream(self) -> None:
        """
        Раз в 4 часа включать проверку стримера принудительно.
        """
        event_logger(
            bot_name=BOT_NAME,
            event_name="checking_stream"
        )
        
        if self.checking_streamer is False:
            self.checking_streamer = True


    @tasks.loop(minutes=5)
    async def check_delete_private_text_channel(self) -> None:
        """
        Каждые 5 минут делать проверку на необходимость удаление приватных текстовых каналов.
        """
        
        event_logger(
            bot_name=BOT_NAME,
            event_name="check_delete_private_text_channel"
        )
        
        channel_info: Union[int, bool]  = WriteJsonFile.get_text_channel_info()
        if channel_info:
            channel: disnake.TextChannel = self.bot.get_channel(channel_info)
            await channel.delete()
    
    
    @tasks.loop(minutes=5)
    async def check_delete_private_voice_channel(self) -> None:
        
        event_logger(
            bot_name=BOT_NAME,
            event_name="check_delete_private_voice_channel"
        )
        
        channel_info: Union[dict[int, str], bool] = WriteJsonFileVoice.get_voice_channel_info()
        if channel_info:
            channel_id: int = channel_info[0]
            channel: disnake.TextChannel = self.bot.get_channel(channel_id)
            if channel.members == []:
                WriteJsonFileVoice.delete_voice_channel_file(channel_name=channel_info[1])
                await channel.delete()


    @tasks.loop(minutes=5)
    async def take_credit(self) -> None:
        """
        Проверка необходимости на сбор кредита с пользователя.
        """
        
        event_logger(
            bot_name=BOT_NAME,
            event_name="take_credit"
        )
        
        info: Union[list, bool] = get_info_from_credit()
        if info is not False and info is not None:
            user_balance: float = get_user_balance(user_name=info[0])
            bot_balance: float = get_bot_money()
            taked_credit_money: float = info[1] + info[1] * 0.1
            
            write_user_balance(
                user_name=info[0],
                count=user_balance - taked_credit_money
            )
            write_user_balance(
                user_name=BOT_NAME,
                count=bot_balance + taked_credit_money
            )
            ## Удаляем файл с записью кредита после его взятия.
            os.remove(f'{DIR_CREDIT_PATH}//{info[0]}.credit')
            
            user: disnake.User = self.bot.get_user(info[3])
            await user.send(
                embed = disnake.Embed(
                    title='Автовыплата кредита',
                    description=f'''Мы автоматически забрали у вас кредит на сумму **{taked_credit_money}** (с **10-ти%** ставкой равной).''',
                    timestamp=datetime.datetime.now()
                )
                .set_footer(
                    text='Ваша любимая дверь',
                    icon_url=DOOR_IMG_URL
                )
            )


    @tasks.loop(minutes=5)
    async def check_streamer(self) -> None:
        """
        Уведомление для пользователей о начале стрима у NoniFow.
        """
        ## Если необходимость проверки стримов выключена.
        if self.checking_streamer is False:
            return None
        
        try:
            ## Если стрим начался
            if check_stream():
                description: str = '''Хэй, лучший стример начал трансляцию! Заходи скорее! :video_camera:'''
                embed: disnake.Embed = disnake.Embed(
                    title=f'У {STREAMER_NAME} стрим! Залетай!',
                    description=description,
                    url=TWITCH, color=disnake.colour.Color.red(),
                    timestamp=datetime.datetime.now()
                )
                
                embed.set_author(
                    name=STREAMER_NAME,
                    icon_url=DOOR_IMG_URL
                )
                embed.set_footer(
                    text="Ваша любимая дверь",
                    icon_url=DOOR_IMG_URL
                )
                embed.set_thumbnail(
                    url=ITS_OPENING_IMG_URL
                )
                embed.set_image(
                    url=DOOR_GIF_URL
                )
                embed.add_field(
                    name="Donate:",
                    value=DONAT,
                    inline=False
                )
                channel: disnake.NewsChannel = self.bot.get_channel(STREAM_NOTIFICATION_CHANNEL)

                await channel.send('@everyone')
                await channel.send(embed=embed)
                await self.bot.change_presence(
                    activity=disnake.Streaming(name='Commands: >',
                            url='https://www.twitch.tv/nonifow',
                            details='https://www.twitch.tv/nonifow')
                )
                logger.info('Создано окно embed. Начало стрима.')
                self.checking_streamer = False
                
            else:
                await self.bot.change_presence(
                    activity=disnake.Game(name='Дверное казино', platform='Python')
                )
        
        except Exception:
                pass


    # Обработка ошибок: ======================================
    ## Ошибки commands
    @commands.Cog.listener("on_command_error")
    async def on_command_error(
        self,
        ctx: commands.Context,
        error
    ) -> None:
        """Обработчик ошибок. Перехватывает исключения при использовании комманд, если получено неизвестное - запись в файл важных ошибок.

        Args:
            ctx (commands.Context)
            error (_type_): Произошедшая ошибка.
        """
        ## Нехватка прав.
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f':octagonal_sign: Уважаемый **{ctx.author.global_name}**, недостаточно прав для исполнения команды')
            
        ## Отсутствие таковой команды.
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send(':octagonal_sign: Команда не найдена')
            
        ## Неправильное использование команды.
        elif isinstance(error, commands.UserInputError):
            await ctx.send(f':octagonal_sign: Неправильный ввод команды "{ctx.command.name}". Правильное использование: {ctx.command.brief}')

        ## Непредвиденная ошибка.
        else:
            error_write(error=str(error))
            error_logger(
                error=error,
                command_name="on_command_error",
                line=391
            )
            await ctx.send(f":octagonal_sign: Произошла ошибка: {error}")

    ## Ошибки slash_commands
    @commands.Cog.listener("on_slash_command_error")
    async def on_slash_command_error(
        self,
        inter: disnake.AppCommandInteraction,
        error
    ) -> None:
        if isinstance(error, commands.errors.NoPrivateMessage):
            await inter.response.send_message(
                f'Уважаемый {inter.author.mention}, вы не можете использовать эту команду в личных сообщениях! :octagonal_sign:',
                ephemeral=True
            )
            error_logger(
                error=error,
                command_name="on_slash_command_error",
                user_name=inter.author.name,
                line=412
            )
        
        else:
            await inter.response.send_message(
                f'Произошла ошибка: {error}. :octagonal_sign:',
                ephemeral=True
            )
            error_logger(
                error=error,
                command_name="on_slash_command_error",
                user_name=inter.author.name,
                line=418
            )
            error_write(
                error=error
            )
            
    
    
    @commands.Cog.listener("on_error")
    async def on_error(
        self,
        error
    ) -> None:
        ## Записываем ошибку в папку для таковых.
        error_write(error=str(error))
        error_logger(
            error=error,
            command_name="on_error",
            line=286
        )
        for creator in CREATOR_ID:
            creator: disnake.User = self.bot.get_user(creator)
            await creator.send("""
`Непредвиденная критическая ошибка. Если ВЫ видите это сообщение,
значит необходимо срочно обратится к разработчику: ему сообщение не пришло по какой-то причине.
Если этого не сделать - могут произойти серьёзные проблемы.
Просто передайте: "Смотри логи и папку ошибок."

Отдельная благодарность за понимание.

Сообщение доставляется только высшей администрации.`
"""
            )
            


    ## Запись событий в логи сервера для их анализа и отладки.
## ============================================================
    @commands.Cog.listener("on_message_delete")
    async def on_message_delete(
        self, 
        message: disnake.Message
    ) -> None:
        ## Получаем автора сообщения
        message_author: disnake.Member = message.author
        
        if message.content == "":
            return None 
        if message_author.name == BOT_NAME:
            return None
        
        await self.logs_channel.send(
            embed=disnake.Embed(
                title="Лог удаления сообщений.",
                description=f"""
Удалено сообщение: ```{message.content}```

`В канале:` **{message.channel.mention}**.

`Автор:` **{message_author.mention}**.

`Сообщение создано:` **{message.created_at}**. """,
            color=disnake.Color.red(),
            timestamp=datetime.datetime.now(),
            )
            .set_author(
                name=message_author.name,
                icon_url=message_author.avatar.url
            )
            .set_footer(
                text=FOOTER_TEXT,
                icon_url=DOOR_IMG_URL
            )
        )


    @commands.Cog.listener("on_message_edit")
    async def on_message_edit(
        self,
        message_before: disnake.Message,
        message_after: disnake.Message
    ) -> None:
        ## получаем автора изменяемого сообщения.
        message_author: disnake.Member = message_before.author
        
        if message_author.name == BOT_NAME:
            return None
        
        await self.logs_channel.send(
            embed=disnake.Embed(
                title="Лог изменения сообщений.",
                description=f"""
`Изменено сообщение:` 
    Было: ```{message_before.content}```
    Стало: ```{message_after.content}```

`В канале:` **{message_before.channel.mention}**.

`Автор:` **{message_author.mention}**.

`Сообщение создано:` **{message_before.created_at}**. 

`Измененено:` **{message_after.edited_at}**.
            """,
            color=disnake.Color.red(),
            timestamp=datetime.datetime.now(),
            )
            .set_author(
                name=message_author.name,
                icon_url=message_author.avatar.url
            )
            .set_footer(
                text=FOOTER_TEXT,
                icon_url=DOOR_IMG_URL
            )
        )


    @commands.Cog.listener("on_member_remove")
    async def on_member_remove(
        self,
        member: disnake.Member,
    ) -> None:
        """При выходе пользователя добавляет информацию об этом в логи сервера.

        Args:
            member (disnake.Member): Уходящий участник сервера.
        """
        ## Логируем выход пользователя с сервера.
        await self.logs_channel.send(
            embed=disnake.Embed(
                title="Лог пользователей.",
                description=f"""
`Участник:` **{member.mention}**.
`Вышел с сервера.` """,
            color=disnake.Color.red(),
            timestamp=datetime.datetime.now(),
            )
            .set_image(
                url=member.avatar.url
            )
            .set_footer(
                text=FOOTER_TEXT,
                icon_url=DOOR_IMG_URL
            )
        )


    
    @commands.Cog.listener()
    async def on_member_join(
        self,
        member: disnake.Member,
        channel: disnake.NewsChannel = None
    ) -> None:
        """При входе нового пользователя на сервер приветствует его.

        Args:
            member (disnake.Member): Новый участник сервера.
            channel (disnake.NewsChannel, optional): Новостной канал. Defaults to None.
        """
        await asyncio.sleep(2)
        channel: disnake.NewsChannel = self.bot.get_channel(1209206013115371601)
        role_to_add: disnake.Role = member.guild.get_role(1208763394115764254)
        
        embed: disnake.Embed = disnake.Embed(
            title=f'ПРИВЕТСТВУЮ, дорогой {member.global_name}! :wave:',
            description=f'''НАДЕЕМСЯ ты прекрасно проведёшь время, ЕСЛИ что-то НЕ ПОНЯТНО пользуйся ПУТЕВОДИТЕЛЕМ! 
            
Приятного ВРЕМЯПРЕПРОВОЖДЕНИЯ! {random.choice([':star_struck:', ':fire:', ':love_letter:' ])}''',
            timestamp=datetime.datetime.now(),
            color=disnake.Color.random()
        )
        embed.set_thumbnail(url=HELLO_IMG_URL)
        embed.set_footer(
            text='Ваша любимая дверь',
            icon_url=DOOR_IMG_URL
        )
        write_user_balance(
            user_name=member.name,
            count=0.0
        )
        await member.add_roles(role_to_add)
        await channel.send(
            content='Встретим новенького!',
            embed=embed
        )
        
        ## Логируем вход пользователя на сервер.
        await self.logs_channel.send(
            embed=disnake.Embed(
                title="Лог пользователей.",
                description=f"""
`Участник:` **{member.mention}**.
`Присоединился к серверу.` """,
            color=disnake.Color.green(),
            timestamp=datetime.datetime.now(),
            )
            .set_image(
                url=member.avatar.url
            )
            .set_footer(
                text=FOOTER_TEXT,
                icon_url=DOOR_IMG_URL
            )
        )


    @commands.Cog.listener('on_message')
    async def ai_response(
        self,
        message: disnake.Message
    ) -> None:
        """Общение с AI. При упоминании бота отвечает пользователю.

        Args:
            message (disnake.Message): Последнее переданное сообщение.
        """
        try:
            if  message.author.id != 1179137296629514260 and\
                (
                    "<@1179137296629514260>" in message.content or\
                    message.reference.resolved.author.id == 1179137296629514260 
                ):
                
                ## Проверка происходит ли упоминание бота в команде.
                for command_name in PREFIX_COMMANDS:
                    if command_name in message.content:
                        return None
                
                
                command_logger(
                    global_name=message.author.global_name,
                    name=message.author.name,
                    command_name="ai_response",
                    args=f"message.content: {message.content}"
                )
                
                write_into_json(
                    json_path=JSON_PATH,
                    data={'role': 'user', 'content': f"{message.author.global_name}: {message.content}. Говори на русском, ответ уложи в 2000 символов! Можешь использовать эмодзи."}
                )
                channel: disnake.TextChannel = self.bot.get_channel(message.channel.id)
                ai_response: str = get_response()
                
                write_into_json(
                    json_path=JSON_PATH,
                    data={'role': 'assistant', 'content': ai_response}
                )
                await channel.send(f"<@{message.author.id}>, {ai_response}")
        
        except disnake.HTTPException:
            with open(file=f"{os.path.dirname(JSON_PATH)}//ai_response.txt", mode="w", encoding="utf-8") as file:
                file.write(ai_response)
                
            await channel.send(
                content=f"<@{message.author.id}>,",
                file=disnake.File(
                    fp=f"{os.path.dirname(JSON_PATH)}//ai_response.txt",
                    filename="ai_response.txt"
                )
            )
            os.remove(f"{os.path.dirname(JSON_PATH)}//ai_response.txt")
        except Exception:
            pass


    @commands.Cog.listener('on_message')
    async def on_message(
        self,
        message: disnake.Message
    ) -> None:
        """Поиск рекламы серверов в сообщении.

        Args:
            message (disnake.Message): Последнее переданное сообщение.
        """
        if 'https://discord.gg' in message.content or 'https://discord.com/invite' in message.content:
            await message.delete()
            logger.info(f'>>> Удалена ссылка - реклама сервера {message}, {message.content}')
            
            try:
                    ## На всякий выдаём мут пользователю.
                    await message.author.timeout(
                        duration=3600,
                        reason="Распространение рекламы на сервере. (Читай законодательство: 1.4)"
                    )
            except Exception:
                pass

            try:
                for creator in CREATOR_ID:
                    user: disnake.User = self.bot.get_user(creator)
                    await user.send(embed=disnake.Embed(
                        title='У нас кто-то пытается рекламировать свой сервер!!!',
                        description=f'''
                        Сообщение: **{message.content}**.
                        Автор: **{message.author.global_name} ({message.author.name})**.
                        Ссылка на аватар пользователя: **{message.author.avatar.url}**.
                        Канал: **{message.channel.name}**
                        Необходимо обратить на это внимание!!!
                        '''
                        )
                    )
                
            except Exception as err:
                error_write(error=str(err))
                error_logger(
                    error=err,
                    command_name="on_message",
                    line=513,
                )
                    
                for creator in CREATOR_ID:
                    user: disnake.User = self.bot.get_user(creator)
                    await user.send('У нас кто-то пытается рекламировать свой сервер!!!')


def setup(bot =  commands.Bot):
    bot.add_cog(Events(bot))
    cog_logger(cog_name="Events")