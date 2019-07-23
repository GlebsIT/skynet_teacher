# coding: utf-8
# Импортирует поддержку UTF-8.
from __future__ import unicode_literals

# Импортируем модули для работы с JSON и логами.
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
    database = "project.db"
    conn = create_connection(database)
    message = (user_id, req['session']['message_id'], req['session']['session_id'], req['request']['original_utterance'],res['response']['text'])

    if req['session']['new']:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.

        sessionStorage[user_id] = {
            'suggests': [
                "Войти",
                "Зарегистрироваться",
            ]
        }

        res['response']['text'] = ' \t Добрый день, я помогаю учителям оставлять заметки родителям, родителям узнавать успеваемость и посещаемость детей.' \
        '\n \t Вы хотите войти или зарегистрироваться? 1.0'

        #Создание кнопок
        res['response']['buttons'] = get_suggests(user_id)

        with conn:
            create_message(conn, message)

        return
    else:
        cur = conn.cursor()
        cur.execute("SELECT top 1 * FROM messages ORDER BY message_id DESC WHERE session_id=?",
                    [req['session']['session_id']])
        results = cur.fetchall()
        for row in results:
            print(row)
            logging.info('row: %r', row)

    if req['request']['original_utterance'].lower() in [
        'зарегистрироваться'
        'авторизоваться'
    ]:
        sessionStorage[user_id] = {
            'suggests': [
                "учитель",
                "родитель",
            ]
        }
        res['response']['text'] = 'Вы учитель или родитель?'
        res['response']['buttons'] = get_suggests(user_id)
        create_message(conn, message)
        return

    if req['request']['original_utterance'].lower() in [
        'учитель',
        'я преподаватель',
        'преподаватель',
        'педагог',
        'тренер'
    ]:
        res['response']['text'] = 'Скажите ваше имя'
        create_message(conn, message)
        return

    # Обрабатываем ответ пользователя.
    if req['request']['original_utterance'].lower() in [
        'Глеб'
    ]:
        res['response']['text'] = 'Добавлен учитель'
        # create a database connection
        with conn:
            # create a new teacher
            teachers = ('test', user_id)
            create_teacher(conn, teachers)
            create_message(conn,message)

        return

    # Пользователь хочет выйти из навыка
    if req['request']['original_utterance'].lower() in [
        'закрыть',
        'выйти',
    ]:
        res['response']['text'] = 'Сессия убита'
        res['response']['end_session'] = True
        return

    # Если нет, то убеждаем его купить слона!
    res['response']['text'] = 'Все говорят "%s", а ты купи слона!' % (
        req['request']['original_utterance']
    )
    res['response']['buttons'] = get_suggests(user_id)


# Функция возвращает две подсказки для ответа.
def get_suggests(user_id):
    session = sessionStorage[user_id]

    # Выбираем две первые подсказки из массива.
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests']
    ]

    # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
    #session['suggests'] = session['suggests'][1:]
    #sessionStorage[user_id] = session

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
    :param project:
    :return: project id
    """
    sql = ''' INSERT INTO messages(user_id,message_id,session_id,request,response)
              VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, message)
    return cur.lastrowid
