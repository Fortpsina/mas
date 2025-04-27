from sqlite3 import connect, OperationalError
from datetime import datetime
from json import load, JSONDecodeError
from plugins.command_logger import select_group_by_id
import logging

def sel_group (group_id: int = 1) -> str:
    '''
    Проверяет "groups.json" - проверяет ID группы и превращает его в строку.\n
    По сути, это можно было и через init сделать, но мне было лень переделывать структуру БД, поэтому так сложно //shrug
    '''
    try:
        groups = load(open('groups.json', 'r', encoding='utf-8'))

        for selected_group in groups:
            if selected_group['id'] == group_id:
                return selected_group['name']

    except JSONDecodeError and IndexError:
        return 'Группа неизвестна'

def create_table (name: str = 'database') -> None:
    '''
    Проверяет наличие таблицы users и создаёт её при условии отсутствия.\n
    Применять когда есть шанс, что таблицы нет - позволяет избежать ошибку.
    '''

    conn = connect(f'{name}.sql')
    cur = conn.cursor()

    cur.execute(
        'CREATE TABLE IF NOT EXISTS users' +
        '(id int auto_increment primary key, ' +
        'name varchar(50), ' +
        'pass varshar(50), ' +
        'user_id INTEGER, ' +
        'color varshar(50), ' +
        'social_cred INTEGER, ' +
        'vk_id INTEGER, ' +
        'reserve_1 INTEGER, ' +
        'reserve_2 INTEGER, ' +
        'reserve_3 varshar(50), ' +
        'date varshar(50), ' +
        'banned varshar(50), ' +
        'mailing varshar(50), ' +
        'status varshar(50) ' +
        ')'
    )
    conn.commit()

    cur.close()
    conn.close()

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.FileHandler('logs.log'))


class User:
    '''
    Выдаёт пользователя по ID.\n
    ------------------------------
    Первый аргумент - ID Telegram, по нему пользователь и ищется.\n
    Пример: User(428192863).name - выдать имя юзера по ID.\n
    ------------------------------
    Доступные методы:\n
    User().register()\n
    User().edit()
    '''

    def __init__ (
            self,
            tgid: int = 0,
            name: str = 'User',
            vk_link: str = 'https://vk.com/example',
            color: str = 'default',
            reg: str = '2020-01-01 00:00:00',
            conditions: str = 'Не ознакомлен',
            group = 1,
            *args, **kwargs
    ):
        conn = connect('database.sql')
        cur = conn.cursor()

        try:
            cur.execute(f'SELECT * FROM users WHERE user_id = {tgid}')
            user = cur.fetchall()[0]
            # Определяем первый элемент списка, полученного из БД как найденного пользователя
            # По идее, второй элемент в списке возможен только если такой есть в бд, а взяться ему там неоткуда

            self.name = user[1]
            self.tgid = user[3]
            self.vk_link = user[2]
            self.color = user[4]
            self.reg = user[10][:19]
            self.conditions = user[6]
            self.group = sel_group (user[7])


        except OperationalError and IndexError:
            self.name = name
            self.tgid = tgid
            self.vk_link = vk_link
            self.color = color
            self.reg = reg
            self.conditions = conditions
            self.group = group
            self.user_found = False

        else:
            self.user_found = True

        finally:
            cur.close()
            conn.close()

    def register (
            self,
            date: str = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    ) -> None:
        '''
        Метод register создаёт профиль пользователя на основе имеющихся аргументов.\n
        Пример: User(428192863, "Андрей").register(2022.02.21 12:00:00)\n
        Если не вписать дату, определит её автоматически.\n
        '''

        conn = connect('database.sql')
        cur = conn.cursor()

        cur.execute(
            'INSERT INTO users ' +
            '(name, pass, user_id, color, social_cred, vk_id, reserve_1, reserve_2, reserve_3, date, banned, mailing, status) ' +
            ' VALUES (' +
            f'"{self.name}", ' +            # name          (Имя пользователя)
            f'"{self.vk_link}", ' +         # pass          (Ссылка для вк)
            f'"{self.tgid}", ' +            # user_id       (Telegram ID)
            f'"{self.color}", ' +           # color         (Цвет)
            f'"{100}", ' +                  # social_cred   (Соц. рейтинг)
            f'"{self.conditions}", ' +      # vk_id         (Условия бота)
            f'"{self.group}", ' +           # reserve_1     (ID группы)
            f'"{2}", ' +                    # reserve_2     (запасная)
            f'"reserve", ' +                # reserve_3     (запасная)
            f'"{date}", ' +                 # date          (Время)
            f'"No", ' +                 # banned        (запасная)
            f'"Yes", ' +                # mailing       (запасная)
            f'"User" ' +                # status        (тип объекта)
            ')'
        )
        conn.commit()

        cur.close()
        conn.close()

        logger.info(
            f'{date}_________________________\n' +
            f'Профиль {self.name} был создан.\n' +
            f' -> id = {self.tgid}\n' +
            f' -> vk_link = {self.vk_link}\n'+
            '____________________________________________\n'
        )

    def edit (
            self,
            column,
            new_value,
            initiated_by: str = 'Консоль',
            date: str = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    ) -> None:
        '''
        Метод edit обновляет данные пользователя.\n
        Указывать колонну, новую информацию и инициатора (последнее - необязательно)\n
        Пример: User(428192863).edit('color', 'random')
        '''
        conn = connect('database.sql')
        cur = conn.cursor()

        cur.execute(f'SELECT {column} FROM users WHERE user_id = {self.tgid}')
        old_values = cur.fetchall()

        cur.execute(f'UPDATE users SET {column} = "{new_value}" WHERE user_id = {self.tgid}')
        conn.commit()

        cur.close()
        conn.close()

        for value in old_values:
            logger.info(
                f'{date}_________________________\n' +
                f'Профиль {self.name} был отредактирован.\n' +
                f' -> Старое значение {column}: {value}\n' +
                f' -> Новое значение {column}: {new_value}\n' +
                f' -> Изменил: {initiated_by}\n'+
                '____________________________________________\n'
            )

class UserProfile:
    def __init__(self, user_id: int):
        conn = connect('database.sql')
        cur = conn.cursor()
        cur.execute(f'SELECT name, pass, user_id, color, reserve_1, date FROM users WHERE user_id = {user_id}')

        user_data = cur.fetchone()

        if user_data:
            self.exists = True
            self.user_name  = user_data[0]
            self.user_vk    = user_data[1]
            self.user_id    = user_data[2]
            self.user_color = user_data[3]
            self.user_group = select_group_by_id(user_data[4])
            self.user_reg   = user_data[5]
        else:
            self.exists = False

        cur.close()
        conn.close()
