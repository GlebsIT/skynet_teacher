# coding: utf-8
# Импортирует поддержку UTF-8.
from __future__ import unicode_literals

# Импортируем модули для работы с JSON и логами.
import datetime
import json
import logging
import sqlite3

# Импортируем подмодули Flask для запуска веб-сервиса.
from flask import Flask, request

app = Flask(__name__)

logging.basicConfig(filename="sample.log", level=logging.DEBUG)

# Хранилище данных о сессиях.
sessionStorage = {}


# Задаем параметры приложения Flask.
@app.route("/", methods=['POST'])
def main():
    # Функция получает тело запроса и возвращает ответ.
    # logging.info('Request: %r', request.json)

    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "end_session": False
        }
    }

    handle_dialog(request.json, response)

    # logging.info('Response: %r', response)

    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
    )


# Функция для непосредственной обработки диалога.
def handle_dialog(req, res):
    user_id = req['session']['user_id']
    sessionStorage[user_id] = {'suggests': []}
    res['response']['buttons'] = get_suggests(user_id)
    session_id = req['session']['session_id']
    message_id = req['session']['message_id']
    request = req['request']['original_utterance']
    database = "project.db"
    response = 'ok';
    button = '';
    id_parents = ''
    id_skill = ''

    conn = create_connection(database)
    message = [user_id, req['session']['message_id'], req['session']['session_id'],
               request]
    results = get__last_message(conn, user_id)

    if results != None:
        logging.info('results: %r \n', results[0])
        id_parents = results[0]

    logging.info('request: %r \n', request)
    skill = get__skill(conn, '', '')

    if skill != None:
        logging.info('skill: %r \n', skill)
        response = skill[0]
        button = skill[1].split(',')
        id_skill = skill[2]

    if req['session']['new']:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.

        sessionStorage[user_id] = {
            'suggests': [
                button
            ]
        }

        res['response']['text'] = response

        # Создание кнопок
        res['response']['buttons'] = get_suggests(user_id)
        message.append(res['response']['text'])
        today = datetime.datetime.today()
        message.append(today)
        message.append(id_skill)
        with conn:
            create_message(conn, message)
        # logging.info('message: %r', type(message))
        return
    #
    #     # try:
    #     #     curmessage.execute("SELECT * FROM messages WHERE session_id = ? ORDER BY message_id DESC LIMIT 1",(session_id))
    #     #     result = curmessage.fetchall()
    #     # except sqlite3.DatabaseError as err:
    #     #     logging.info("Error: %r", err)
    #     # else:
    #     #     conn.commit()
    #
    # if results[0] == "ваше имя":
    #     res['response']['text'] = 'Ваша фамилия'
    #     # create a database connection
    #     with conn:
    #         # create a new teacher
    #         teachers = (request, user_id)
    #         create_teacher(conn, teachers)
    #         message.append(res['response']['text'])
    #         create_message(conn, message)
    #
    #     return
    #
    # if results[0] == "ваше фамилия":
    #     res['response']['text'] = 'Ваша фамилия'
    #     # create a database connection
    #     with conn:
    #         # create a new teacher
    #         teachers = (request, user_id)
    #         create_teacher(conn, teachers)
    #         message.append(res['response']['text'])
    #         create_message(conn, message)
    #     return
    #
    # if results[0] == "ваше отчество":
    #     res['response']['text'] = 'Ваша фамилия'
    #     # create a database connection
    #     with conn:
    #         # create a new teacher
    #         teachers = (request, user_id)
    #         create_teacher(conn, teachers)
    #         message.append(res['response']['text'])
    #         create_message(conn, message)
    #
    #     return
    #
    # if req['request']['original_utterance'].lower() in [
    #     'зарегистрироваться',
    #     'регистрация'
    # ]:
    #     res['response']['text'] = 'Вы учитель или родитель?'
    #     sessionStorage[user_id] = {
    #         'suggests': [
    #             "учитель",
    #             "родитель"
    #         ]
    #     }
    #     res['response']['buttons'] = get_suggests(user_id)
    #     message.append(res['response']['text'])
    #     with conn:
    #         create_message(conn, message)
    #     return
    #
    # if req['request']['original_utterance'].lower() in [
    #     'учитель',
    #     'я преподаватель',
    #     'преподаватель',
    #     'педагог',
    #     'тренер',
    #     'я тренер',
    #     'я преподаватель'
    # ]:
    #     res['response']['text'] = 'Ваше имя'
    #     message.append(res['response']['text'])
    #     with conn:
    #         create_message(conn, message)
    #     return
    #
    #
    #
    # # Пользователь хочет выйти из навыка
    # if req['request']['original_utterance'].lower() in [
    #     'закрыть',
    #     'выйти',
    # ]:
    #     res['response']['text'] = 'Сессия убита'
    #     res['response']['end_session'] = True
    #     message.append(res['response']['text'])
    #     with conn:
    #         create_message(conn, message)
    #     return
    #
    # # Если нет, то убеждаем его купить слона!
    # res['response']['text'] = 'Все говорят "%s", а ты купи слона!' % (
    #     req['request']['original_utterance']
    # )
    # message.append(res['response']['text'])
    # with conn:
    #     create_message(conn, message)
    # res['response']['buttons'] = get_suggests(user_id)


# Функция возвращает две подсказки для ответа.
def get_suggests(user_id):
    session = sessionStorage[user_id]

    # Выбираем две первые подсказки из массива.
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests']
    ]

    # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
    # session['suggests'] = session['suggests'][1:]
    # sessionStorage[user_id] = session

    # Если осталась только одна подсказка, предлагаем подсказку
    # со ссылкой на Яндекс.Маркет.
    # if len(suggests) < 2:
    #    suggests.append({
    #        "title": "Ладно",
    #       "url": "https://market.yandex.ru/search?text=слон",
    #        "hide": True
    #    })

    return suggests


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        logging.info('error bd: %r', e)

    return None


def create_teacher(conn, teacher):
    """
    Create a new project into the projects table
    :param conn:
    :param project:
    :return: project id
    """
    sql = ''' INSERT INTO teachers(name,user_id)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, teacher)
    return cur.lastrowid


def create_message(conn, message):
    """
    Create a new project into the projects table
    :param conn:
    :param message:
    :return: request
    """
    sql = ''' INSERT INTO messages(user_id,message_id,session_id,request,response,data_today,id_skill)
              VALUES(?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, message)
    return cur.lastrowid


def get__last_message(conn, user_id):
    """
    Get message
    :param conn:
    :param session_id:
    :return: rezult
    """

    curmessage = conn.cursor()
    curmessage.execute("SELECT id_skill FROM messages WHERE user_id = ? ORDER BY message_id DESC LIMIT 1",
                       (user_id,))

    return curmessage.fetchone()


def get__skill(conn, id_parents, template):
    """
    Get message
    :param conn:
    :param id_parents:
    :param template:
    :return: rezult
    """

    curskill = conn.cursor()
    curskill.execute("SELECT response, button, id_logic FROM logic_skill WHERE id_parents = ? and template = ? LIMIT 1",
                     (id_parents, template))
    return curskill.fetchone()
