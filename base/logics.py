from sqlalchemy import delete, create_engine, MetaData, Table, Integer, String, \
    Column, DateTime, ForeignKey, Numeric, SmallInteger, Boolean, sql, func, update
import sqlite3

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

import base.models
import base.models as models

from sqlalchemy.orm import Session, sessionmaker

from datetime import datetime
import config


# Создать базу данных
def make_clear_base(db='sqlite:///sqlite3.db'):
    engine = create_engine(db)
    Base = models.Base
    Base.metadata.create_all(engine)
    return True


# удалить базу данных
def clear_base(db='sqlite:///sqlite3.db'):
    engine = create_engine(db)
    Base = models.Base
    Base.metadata.drop_all(engine)
    return True


def set_default_admin(db='sqlite:///sqlite3.db'):
    engine = create_engine(db)
    session = Session(bind=engine)
    u1 = config.default_admin
    u1.updated = datetime.now()
    print(u1)
    session.add(u1)
    session.commit()
    session.invalidate()
    engine.dispose()
    return


def get_users(db='sqlite:///sqlite3.db'):
    engine = create_engine(db)
    session = Session(bind=engine)
    # проверяем есть ли данные в базе, и, если нет, добавляем админа
    if session.query(base.models.User).first() is None:
        print(f'похоже база пустая, добавляю админа - тебя')  # отправить об этом сообщение
        try:
            set_default_admin(db)
        except Exception as e:
            print(f'Не удалось добавить админа.\n'
                  f'Причина - {e}')
            get_users_result = False
        else:
            get_users_result = True
    else:
        get_users_result = True
        count_users = session.query(base.models.User).count()
        print(f'база на месте, в ней {count_users} записей.')
    return get_users_result


def get_last_date():
    engine = create_engine(config.base)
    session = Session(bind=engine)
    try:
        youngest_date = session.query(func.max(models.Subscription.lastMessageTime)).scalar()
        # print(f'самая свежая дата - "{youngest_date}"')
    except sqlite3.OperationalError as e:
        print(f'Похоже таблица новая? - {e}')
        return config.oldest_date
    except Exception as e:
        print(f'Ошибка работы с базой данных продолжение работы невозможно. - {e}')
        youngest_date = None
        runner = False  # Todo проверять перед важными событиями и пускать в While
    else:
        return youngest_date
    return False


def is_base_clear(db='sqlite:///sqlite3.db'):
    print(f'Фиктивно проверили пустая ли база')
    return True


def date_or_none(date):
    # Todo Добавить проверку не является ли запрос уже нужным форматом.

    try:
        p = datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
    except TypeError:
        if isinstance(date, datetime):
            return date
        else:
            print(f'Ошибка формата переданной для разбора даты - {type(date)}')
            return None
    except Exception as e:
        # print(f'Ошибка форматирования даты, пробую без времени')
        try:
            p = datetime.strptime(date, '%Y-%m-%d')
        except Exception as e:
            try:
                p = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f')
            except Exception as e:
                try:
                    p = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
                except Exception as e:
                    print(f'Заменить формат даты "{date}" не удалось ошибка {e}')
                else:
                    return p
            else:
                # print(f'распознана дата - {p}')
                return p
        else:
            # print(f'распознана дата - {p}')
            return p
    else:
        # print(p)
        return p




def get_last_checked_message_time(chatRoomId, db='sqlite:///sqlite3.db'):
    engine = create_engine(config.base)
    session = Session(bind=engine)
    try:
        last_mess_time = session.query(func.max(models.Chat_Message.last_checked_time).filter
                                       (models.Chat_Message.chatRoomId == chatRoomId)
                                       ).scalar()

    except sqlite3.OperationalError as e:
        print(f'Похоже таблица новая? - {e}')
        return config.oldest_date
    except Exception as e:
        print(f'Ошибка работы с базой данных продолжение работы невозможно. - {e}')
        youngest_date = None
        runner = False  # Todo проверять перед важными событиями и пускать в While
    else:
        return last_mess_time
    return False



async def add_user(data, db='sqlite:///sqlite3.db'):  # не используется
    engine = create_engine(db)
    # print(db)
    # engine.connect()
    session = Session(bind=engine)

    # Готовим данные для записи и
    # Создаём сессии для записи в базу.
    # print(models.Subscription.SYMBOLS)
    # добавляем пустые значения в словарь,
    for sym in models.Subscription.SYMBOLS:
        data[sym] = data.get(sym, None)  # Если в ответе нет подходящего ключа, заменяем его на None
        # print(data[key])

    #             'paymentDate': '2000-00-01 14:38:26.224', 'endDate': '2023-07-01 00:00:00.000',

    data['subscriptionServiceMap'] = None  # Набор подписок вносим в виде строки. Или убрать его нахер?
    print(data)

    subscription = models.Subscription(
        id=data["id"],
        name=data["name"],
        price=data['price'],
        updated=datetime.strptime(data['updated'], '%Y-%m-%d'),
        # datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')
        subscriptionServiceMap=data['subscriptionServiceMap'],  # Или убрать его нахер?
        number=data['number'],
        type=data['type'],
        inserted=datetime.strptime(data['inserted'], '%Y-%m-%d %H:%M:%S.%f'),  # 2022-07-01 17:41:23.573
        paymentDate=date_or_none(data['paymentDate']),
        endDate=date_or_none(data['endDate']),
        status=data['status'],
        customerId=data['customerId'],
        supplierId=data['supplierId'],
        chatRoomId=data['chatRoomId'],
        lastMessageTime=datetime.strptime(data['lastMessageTime'], '%Y-%m-%d %H:%M:%S.%f'),
        unreadMessageCount=data['unreadMessageCount'],
        senderUUID=data['senderUUID'],
        lastName=data['lastName'],
        firstName=data['lastName'],
        # middle
    )
    session.add(subscription)

    try:
        session.commit()
    except Exception as e:
        print(f'При добавлении базы возникла ошибка {e}')
    else:
        print(f'Добавили пользователeй, последний -  {data["number"]}')
        return True


def get_no_name_subscribers():
    engine = create_engine(config.base)
    session = Session(bind=engine)
    no_name_subscribers_count = 0
    no_name_array = []
    try:
        no_name_array = session.query(models.Subscription).filter(models.Subscription.firstName == None)
    except Exception as e:
        print(f'Ошибка работы с базой данных продолжение работы невозможно. - {e}')
        return False
    else:
        no_name_subscribers_count = no_name_array.count()
        print(f' найдено {no_name_subscribers_count} подписок без имён')

    return no_name_array


def set_subscribers_name(number, name_elements):
    engine = create_engine(config.base)
    session = Session(bind=engine)
    # - дурацкая обработка ----
    if "lastName" in name_elements:
        lastName = name_elements["lastName"]
    else:
        lastName = None
    if "firstName" in name_elements:
        firstName = name_elements["firstName"]
    else:
        firstName = None
    if "middleName" in name_elements:
        middleName = name_elements["middleName"]
    else:
        middleName = None

    # -------------------------

    q = session.query(models.Subscription).filter(models.Subscription.number == number)
    if session.query(q.exists()).scalar():
        # Если есть, то переписываем значения, которые могут измениться. Commit не нужен
        try:
            session.query(models.Subscription).filter(
                models.Subscription.number == number).update(
                        {
                            "lastName": lastName,
                            "firstName": firstName,
                            "middleName": middleName,
                        },
                        synchronize_session='fetch')

        except Exception as e:
            print(f'Ошибка при добавлении сессион ОБНОВЛЕНИЯ {e}')
        else:
            # print(f'Удалось обновить  {number}')
            try:
                session.commit()
            except Exception as e:
                print(f'При добавлении базы возникла ошибка {e}')
            else:
                # print(f'Залили все комиты -  {session}')
                return True

    else:
        print(f'Подписки {number} в базе нет, проверь!')
    return

# for c in no_name_array:
#     print(c.lastName, c.firstName, c.number)
# # print(f'самая свежая дата - "{no_name_array}"')

def add_new_column():
    # Make a connection to the SQLite DB
    dbCon = sqlite3.connect("sqlite3.db")
    # Obtain a Cursor object to execute SQL statements
    cur = dbCon.cursor()
    # Add a new column to student table
    # addColumn = "ALTER TABLE subscriptions ADD COLUMN middleName varchar(32)"
    # renameColumn = "ALTER TABLE chat_messages RENAME COLUMN message_id TO id"
    delColumn = "ALTER TABLE chat_messages DROP COLUMN uid"
    cur.execute(delColumn)
    # Retrieve the SQL statment for the tables and check the schema
    masterQuery = "select * from sqlite_master"
    cur.execute(masterQuery)
    tableList = cur.fetchall()

    for table in tableList:
        print("Database Object Type: %s" % (table[0]))
        print("Database Object Name: %s" % (table[1]))
        print("Table Name: %s" % (table[2]))
        print("Root page: %s" % (table[3]))
        print("**SQL Statement**: %s" % (table[4]))

    # close the database connection
    dbCon.close()


def get_less_message_subscriptions():
    # Todo - часть чатов не собирается, т.к. в Подписках нет ИД чата.
    #  Надо вытаскивать по дате последнего сообщения! т.к. иногда senderUUID не передаётся.



    engine = create_engine(config.base)
    session = Session(bind=engine)
    update_message_array = []  # [{"chatRoomId": '', "last_checked_time": ''},... ]
    current_time = datetime.now()

    try:
        is_message_in_sub = session.query(models.Subscription).filter(
            models.Subscription.senderUUID != None,
        )
    except Exception as ex:
        print(f'Ошибка работы с базой данных продолжение работы невозможно. - {ex}')
        return False
    else:
        # print(is_message_in_sub.count())
        for sub in is_message_in_sub:
            # print(sub.number)
            q_chat_room_id = session.query(models.Chat_Message).filter(
                models.Chat_Message.chatRoomId == sub.chatRoomId, )
            q_chat_room_id_exist = session.query(q_chat_room_id.exists()).scalar()  # Если сообщений нет вообще

            q_last_msg_time = session.query(func.max(models.Chat_Message.last_checked_time).filter(
                models.Chat_Message.chatRoomId == sub.chatRoomId
                )).scalar()

            sub_to_update_chat = {'chatRoomId': sub.chatRoomId}  # переменная для формирования списка словарей

            if not q_chat_room_id_exist:
                print(f' У подписки {sub.number} нет сообщений в базе')
                sub_to_update_chat['last_checked_time'] = None
                update_message_array.append(sub_to_update_chat)  # Собираем в список чаты для обновить или собрать

            elif sub.lastMessageTime > q_last_msg_time:  # Если есть, то сравниваем дату
                print(f' У подписки {sub.number} есть сообщения в базе, но они не актуализированы\n')
                #      f'в подписке {sub.lastMessageTime} > в чате {q_last_msg_time}')

                sub_to_update_chat['last_checked_time'] = q_last_msg_time

                update_message_array.append(sub_to_update_chat)  # Собираем в список чаты для обновить или собрать

            else:
                # print(f'Неопознанное состояние наличия сообщений в базе у подписки {sub.number}')
                # print(f' У подписки {sub.number} есть сообщения в базе, но что с ними?\n'
                #       f'в подписке {sub.lastMessageTime} > в чате {q_last_msg_time}')
                #
                # print(sub)
                None

        print(f'! - Нужно загрузить сообщения {len(update_message_array)} подписок')

    return update_message_array


def store_subscriber_messages(chatRoomId, messages):
    contents = None
    cont = []  # Определяем хранилище для сведений о вложениях
    engine = create_engine(config.base)
    session = Session(bind=engine)

    for message in messages:
        # print(f'- перебираю {message["chatId"]}')
        # Заменили отсутствующие на None
        for sym in models.Chat_Message.items:  # Если в data нет подходящего ключа, заменяем его на None
            message[sym] = message.get(sym, None)
#        message.pop('uid', None)
        message['time'] = date_or_none(message['time'])  # проверяем дату в поле
        message['author'] = message['author']['id']  # вытаскиваем id из словаря

        if len(message['contentItem']) == 0:
            is_content = False
        else:
            is_content = True
            contents = message['contentItem']
            # message['contentItem'] = is_content

        if len(message['elements']) != 0:
            print(f'! - В чате {chatRoomId} в сообщении {message["id"]} elements не пуст - ПРОВЕРЬ!\n'
                  f'{message["elements"]}')

        message['elements'] = "None"

        # Проверим, есть ли это сообщение уже в базе
        q_chat_mdg_id = session.query(models.Chat_Message).filter(models.Chat_Message.messageUuid == message['messageUuid'])
        if session.query(q_chat_mdg_id.exists()).scalar():
            # Если есть, то переписываем значения, которые могут измениться. Commit не нужен
            print(f'Сообщение есть в базе, пропускаю')
            continue
            # try:
            #     session.query(models.Chat_Message).filter(
            #         models.Chat_Message.messageUuid == message['messageUuid']).update(
            #                 {
            #                     'author': message['author'],
            #                     'chatId': message['chatId'],
            #                     'elements': message['elements'],
            #                     'id': message['id'],
            #                     'messageUuid': message['messageUuid'],
            #                     'read': message['read'],
            #                     'time': message['time'],
            #                     'type': message['type'],
            #                     'value': message['value'],
            #                     'chatRoomId': message['chatRoomId']
            #                 },
            #                 synchronize_session='fetch')
            # except Exception as e:
            #     print(f'Ошибка при обновлении сессии {e}')

        else:
            # Если подписка новая, то формируем класс? для добавления в базу
            # mess = models.Chat_Message(**message)
            mess = models.Chat_Message(
                    uid=message['uid'],
                    author=message['author'],
                    chatId=message['chatId'],
                    elements=message['elements'],
                    is_content=is_content,
                    id=message['id'],
                    messageUuid=message['messageUuid'],
                    read=message['read'],
                    time=message['time'],
                    type=message['type'],
                    value=message['value'],
                    chatRoomId=message['chatRoomId'],
                    last_checked_time=message['last_checked_time']
            )
            if is_content == True:
                print('В письме есть вложение')
                for content in contents:
                    content['messageUuid'] = message['messageUuid']
                    cont.append(content)

            try:
                # print(f'Пробую закоммитить {datetime.now()}')
                session.add(mess) # Todo - вынести коммит выше в цикле на уровень
            except Exception as e:
                print(f'Ошибка при добавлении в коммит {e}')
            else:
                # print(f'Удалось добавить в комит {datetime.now()}= ')
                None



        try:
            session.commit()
        except Exception as e:
            print(f'При добавлении базы возникла ошибка {e}')
        else:
            # print(f'Залили все комиты -  {session}')
            None
            # return True

    # Проверить тут ретёрн
    # print(cont)
    return cont

def store_content_files(content):
    engine = create_engine(config.base)
    session = Session(bind=engine)
    # print(content)
    content_to_base = models.Content(**content)
    try:
        # print(f'Пробую закоммитить {datetime.now()}')
        session.add(content_to_base)  # Todo - вынести коммит выше в цикле на уровень
    except Exception as e:
        print(f'Ошибка при добавлении в коммит вложений {e}')
    else:
        # print(f'Удалось добавить в комит {datetime.now()}= ')
        None
    try:
        session.commit()
    except Exception as e:
        print(f'При добавлении базы возникла ошибка {e}')
    else:
        # print(f'Залили все комиты -  {session}')
        None
        # return True

def delete_table():
    engine = create_engine(config.base)
    session = Session(bind=engine)

    # Удалить столбец в таблице
    # smt = delete(models.Chat_Message)
    # session.add(smt)

    # удалить строку со значением.
    # session.query(models.Chat_Message).filter(
    #     models.Chat_Message.uid == "1").delete(synchronize_session='evaluate')

    # удалить и создать таблицу
    task = 'Удалить и создать таблицу в БД'
    models.Content.__table__.drop(engine)
    models.Chat_Message.__table__.drop(engine)
    make_clear_base()
    session.commit()
    print(task)


if __name__ == "__main__":
    try:
        # delete_table()  # Удаляем таблицу Chat_Message
        # set_subscriber_messages()
        # date_or_none("2022-07-12T20:28:16.17")
        # get_less_message_subscriptions()
        # add_new_column()
        # get_no_name_subscribers()
        # add_or_update()
        # add_subs_to_base()
        # get_last_date()
        # clear_base()
        # make_clear_base()
        set_default_admin()
        None

    except Exception as e:
        print(f'Не выполнил поставленную задачу по причине - {e}')
    else:
        print(f'Выполнил задачу без ошибок')
    # try:
    #     make_clear_base()
    # except Exception as e:
    #     print(f'Не создал базу, по причине {e}')
    # else:
    #     print(f'Создал базу по запросу пользователя')





