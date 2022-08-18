import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
# работа с базой данных
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import base.logics
from base.models import User, Purchase

# Работа с файловой системой и пр.
from os import getenv
from sys import exit
# Для превращения словарей в объекты (хз чет не догоняю)
from munch import DefaultMunch
import datetime

# Пользовательские материалы в проекте
# from content.descriptions import instructions, help, greetings, admins_start
import config


# Todo - выбрать способ наполнения базы текстами


# Todo Добавить продажу: кнопка, ссылка на акк. и  его проверка, оплата, уведомление об оплате со ссылкой.
# Todo Учёт заданий. Создано, оплачено, выполнено.

# Todo Заказать анализы: кнопка - сслыка - проверка - оплата -?контроль оплаты
#  - сообщение об оплате - сообщение о заказе админу.

# состояние пользователя в чате - возможно удалить
class dialog(StatesGroup):
    spam = State()
    blacklist = State()
    whitelist = State()


# Включение бота и диспетчера
bot_token = getenv("BOT_TOKEN")
if not bot_token:
    exit("Error: no token provided")
storage = MemoryStorage()
bot = Bot(token=bot_token)
dp = Dispatcher(bot=bot, storage=storage)
logging.basicConfig(level=logging.INFO)

# запускаем движок базы данных
engine = create_engine(config.database)


# Пример админ меню на развитие функционала
kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
kb.add(types.InlineKeyboardButton(text="Рассылка"))
kb.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
kb.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
kb.add(types.InlineKeyboardButton(text="Статистика"))


# Хороший генератор кнопок. Если потребуются разные форматы на 3 и более столбца, то применять. Пока как пример.
def build_menu(buttons, n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


def initiation():

    if base.logics.get_users():
        print(f'С базой всё ОК, запускаем сервис')
    else:
        None
    # Todo Если с базой не ОК - не работать дальше.




async def first_time_user(message):
    session = Session(bind=engine)
    d = session.query(User.id).filter(User.id == message.from_user.id).scalar()
    f = message.from_user
    if d is None:
        print(f'Такого пользователя нет')
        user = User(id=f.id,
                    is_bot=f.is_bot,
                    first_name=f.first_name,
                    username=f.username,
                    last_name=f.last_name,
                    language_code=f.language_code,
                    can_join_groups=f.can_join_groups,
                    can_read_all_group_messages=f.can_read_all_group_messages,
                    supports_inline_queries=f.supports_inline_queries,
                    role='user',
                    updated=datetime.datetime.now()
                    )
        try:
            session.add(user)
            session.commit()
        except Exception as e:
            print(f'При добавлении базы возникла ошибка {e}')
        else:
            print(f'Добавили пользователя {f.first_name}')
            return True
    else:
        print(f'Стартанул пользователь {message.from_user.first_name}')
        return False


async def admin_user(message):
    session = Session(bind=engine)
    d = session.query(User.role).filter(User.id == message.from_user.id).scalar()
    print(d)
    if d == 'admin':
        print(f'Зашёл Админ')
        return True
    else:
        return False


async def start(message: types.Message):
    session = Session(bind=engine)
    if await first_time_user(message):
        await message.answer(greetings)
        await message.answer(help)
    elif await admin_user(message):
        # Создание клавиатуры со switch-кнопками и отправка сообщения для админа
        switch_keyboard = types.InlineKeyboardMarkup()
        switch_keyboard.add(types.InlineKeyboardButton(
            text="Отправить бота",
            switch_inline_query=""))
        switch_keyboard.add(types.InlineKeyboardButton(
            text="Вызвать бота здесь",
            switch_inline_query_current_chat=""))
        await message.answer(admins_start, reply_markup=switch_keyboard)
    else:
        await message.answer(help)


# Todo проработать передачу данных и состояний через
data = []
i_key = str()
i_value = str()


async def instruction_key(message: types.Message):
    global i_key
    keyboard = types.InlineKeyboardMarkup(row_width=2, inline_keyboard=None)
    buttons = []
    for note_type in instructions.keys():
        buttons.append(types.InlineKeyboardButton(text=note_type, callback_data=note_type))
    keyboard.add(*buttons)

    await message.answer("Выбери <u>вид записи</u>.", reply_markup=keyboard, parse_mode=types.ParseMode.HTML)


@dp.callback_query_handler(lambda call: call.data == 'back_to_instruction')
async def back_to_instruction(call: types.CallbackQuery):
    await call.answer()
    await bot.edit_message_reply_markup(call.message.chat.id,
                                        message_id=call.message.message_id)  # удаляем кнопки у последнего сообщения
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

    await instruction_key(call.message)


@dp.callback_query_handler(lambda call: call.data in instructions.keys())
async def instruction_value(call: types.CallbackQuery):

    await call.answer()
    print(f'Запрос от пользователя "{call.from_user.first_name}" - "{call.data}"')
    global data, i_key
    i_key = call.data
    await bot.edit_message_reply_markup(call.message.chat.id,
                                        message_id=call.message.message_id)  # удаляем кнопки у последнего сообщения
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    # Собираем меню кнопок
    buttons = []
    for element in instructions[i_key]:
        buttons.append(types.InlineKeyboardButton(text=element, callback_data=element))
    keyboard.add(*buttons)
    # отдельно добавляем кнопку Назад, чтобы она всегда была внизу и одна
    keyboard.add(types.InlineKeyboardButton(text="Назад", callback_data="back_to_instruction"))
    data = instructions[i_key].keys()
    await call.message.edit_text(f'и элемент из "{call.data}" ? ', reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data in data)
async def instruction_notice(call: types.CallbackQuery):
    global i_value
    i_value = call.data
    # print(data)
    # print(i_key)
    # print(i_value)
    # print(call)
    print(f'Запрос деталей от пользователя "{call.from_user.first_name}" - "{call.data}"')
    await bot.answer_callback_query(callback_query_id=call.id,
                                    show_alert=True,
                                    text=f'В {call.data} важно:\n {instructions[i_key][i_value]}')
    await call.answer()


# Система хранения состояний. Пока не разобрался.
async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


async def main():
    initiation()
    try:
        dp.register_message_handler(start, commands={"start"})
        dp.register_message_handler(instruction_key, commands={"ads_formats"})
        await dp.start_polling()
    finally:
        await bot.close()

asyncio.run(main())
