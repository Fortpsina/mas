from sqlite3 import connect
from datetime import datetime
from threading import Lock
from .langs import *


USERS_STRUCT = """CREATE TABLE IF NOT EXISTS Users 
    (id INTEGER PRIMARY KEY,
    name TEXT,
    vk_link TEXT,
    user_id INTEGER,
    color TEXT,
    level INTEGER,
    conditions TEXT,
    hs_name TEXT,
    hs_struct TEXT,
    group_name TEXT,
    registration_date DATE,
    rights_level INTEGER,
    papers TEXT)"""

HS_STRUCT = """CREATE TABLE IF NOT EXISTS Hs 
    (id INTEGER PRIMARY KEY,
    name TEXT,
    structs TEXT,
    students INTEGER,
    founder_id INTEGER,
    longtitude REAL,
    lantitude REAL,
    lesson_dates TEXT)"""

GROUP_STRUCT = """CREATE TABLE IF NOT EXISTS Groups 
    (id INTEGER PRIMARY KEY,
    name TEXT,
    students TEXT,
    mail_adress TEXT,
    mail_password INTEGER,
    mail_server TEXT,
    hs_name TEXT,
    hs_struct TEXT,
    prom DATE,
    papers TEXT,
    founder_id INTEGER)"""

RIGHTS_ASSETS = {0: "banned",    1: "user",
                 2: "group_vc",  3: "group_chairman",
                 4: "admin",     5: "fortpsina"}

def create_table(table_type: str, db: str = 'database') -> None:
    _procedures = {"users": USERS_STRUCT,
                   "hs": HS_STRUCT,
                   "group": GROUP_STRUCT}
    assert table_type in _procedures.keys(), "Указана несуществующая таблица."

    conn = connect(f'{db}.sql')
    cur = conn.cursor()

    cur.execute(_procedures[table_type])
    conn.commit()

    cur.close()
    conn.close()


class UserProfile:
    """Collets data of user from sql by id.

    :exists: true|false - was user found or not.
    :pk: int - primary key of user in sql.
    :user_name: str - name of the user.
    :user_vk: str - vk_link of the user if was left.
    :user_color: str - name of the color user prefer to use.
    :level: int - idk why i lest this one here but let it be.
    :hs_name: str - name of the hs.
    :hs_struct: - str - name of the struct of the hs.
    :user_group: - str - name of the group of the user.
    :user_reg: str|date - registration time.
    :rights: int - level of rights (0 - banned, no rights, 5 - absolutely all rights).
    :role: str - level rights but as a str."""

    def __init__(self, user_id: int):
        self.conn = connect('database.sql', check_same_thread=False)
        self.cur = self.conn.cursor()

        assert isinstance(user_id, int), "ID указан неправильно, запрос отменён аварийно."

        self.cur.execute(f'SELECT * FROM Users WHERE user_id = {user_id}')
        user_data = self.cur.fetchone()
        self.user_id = user_id

        if user_data:
            self.exists = True
            self.pk         = user_data[0]
            self.user_name  = user_data[1]
            self.user_vk    = user_data[2]
            self.user_color = user_data[4]
            self.level      = user_data[5]
            self.hs_name    = user_data[7]
            self.hs_struct  = user_data[8]
            self.user_group = user_data[9]
            self.user_reg   = user_data[10]
            self.rights     = user_data[11]
            self.role       = RIGHTS_ASSETS[self.rights]
        else:
            self.exists = False

    def update(self, column: str, new_value: str | int) -> str:
        _allowed = [word.split()[0] for word in USERS_STRUCT.splitlines()[2:]]
        if column not in _allowed:
            return f"Неизвестная колонна. Доступные значения: {', '.join(_allowed)}"
        
        db_lock = Lock()
        with db_lock:
            self.cur.execute(f'SELECT ? FROM Users WHERE user_id = ?', (column, self.user_id))
            old_value = self.cur.fetchone()[0] or "?"

            self.cur.execute(f'UPDATE Users SET {column} = ? WHERE user_id = ?', (new_value, self.user_id))
            self.conn.commit()

            return f"Значение изменено с {old_value} на {new_value}."
        
    def delete(self, physically: bool = False) -> str:
        if not self.exists:
            return PROFILE_NOT_FOUND_ERROR_NOT_OWN['ru']
        
        b_vklink = f'  Страница ВК: <code>{self.user_vk}</code>'
        b_tgid = f'  ID: <code>{self.user_id}</code>'
        b_color = f'  Цвет: <code>{self.user_color}</code>'
        b_reg = f'  Регистрация: <code>{self.user_reg}</code>'
        
        if physically:
            self.cur.execute(f'DELETE FROM users WHERE user_id = {self.user_id}')
            self.conn.commit()
            return PROFILE_UTIL_DELETED_F['ru'] + f'{self.user_name}:\n{b_vklink}\n{b_tgid}\n{b_color}\n{b_reg}'

        else:
            self.cur.execute(f'UPDATE users SET name = "Удалённый пользователь (Ранее: {self.user_name}, ID: {self.user_id})" WHERE user_id = {self.user_id}')
            self.cur.execute(f'UPDATE users SET user_id = 0 WHERE user_id = {self.user_id}')
            self.conn.commit()
            return PROFILE_UTIL_DELETED_V['ru'] + f'{self.user_name}:\n{b_vklink}\n{b_tgid}\n{b_color}\n{b_reg}'

    def __del__(self):
        self.cur.close()
        self.conn.close()


def register_user(message, **custom_data) -> None:
    conn = connect('database.sql')
    cur = conn.cursor()

    _name = custom_data.get("name",       message.from_user.full_name)
    _id   = custom_data.get("user_id",    message.from_user.id)
    _cnds = custom_data.get("conditions", "Н/Д")
    _hs   = custom_data.get("hs_name",    "УЗ не указано")
    _st   = custom_data.get("hs_struct",  "Структура УЗ не указана")
    _gr   = custom_data.get("group_name", "Группа не указана")
    _date = custom_data.get("reg_date",   datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
    _rl   = custom_data.get("rights",     1)

    cur.execute(
        'INSERT INTO Users (name,     user_id, color,     level, conditions, hs_name, hs_struct, group_name, registration_date, rights_level, papers) ' +
        f'VALUES (         "{_name}", {_id},   "default", 100,   "{_cnds}",  "{_hs}", "{_st}",   "{_gr}",    "{_date}",         {_rl},        "")')
    conn.commit()

    cur.close()
    conn.close()


def register_hs(message, **custom_data) -> None:
    conn = connect('database.sql')
    cur = conn.cursor()

    _n = custom_data.get("name",     message.text)
    _v = custom_data.get("structs",  "")
    _p = custom_data.get("students", "")
    _i = custom_data.get("founder_id", message.from_user.id)

    cur.execute(f'INSERT INTO Hs (name, structs, students, founder_id) VALUES (?, ?, ?, ?)', (_n, _v, _p, _i))
    conn.commit()

    cur.close()
    conn.close()


def register_group(message, **custom_data) -> None:
    conn = connect('database.sql')
    cur = conn.cursor()

    _n = custom_data.get("name",       message.from_user.full_name)
    _v = custom_data.get("vk_link",    "https://vk.com/example")
    _c = custom_data.get("color",      "default")
    _h = custom_data.get("hs_name",    "УЗ не указано")
    _s = custom_data.get("hs_struct",  "Структура УЗ не указана")
    _g = custom_data.get("group_name", "Группа не указана")
    _d = custom_data.get("reg_date",   datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
    _p = custom_data.get("papers",     "")
    _i = custom_data.get("founder_id", message.from_user.id)

    cur.execute('INSERT INTO Groups (name, students, mail_adress, mail_password, hs_name, hs_struct, prom, papers, founder_id) ' +
                f'VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (_n, _v, _c, _h, _s, _g, _d, _p, _i))
    conn.commit()

    cur.close()
    conn.close()


def users_list(db: str = 'database') -> str:
    conn = connect(f'{db}.sql')
    cur = conn.cursor()

    chunk_size = 3800
    _to_reply = ''

    cur.execute('SELECT name, user_id FROM users')
    for el in cur.fetchall():
        _name = el[0]
        _id = el[1]
        _to_reply += f"<b>{_name}</b>: <code>{_id}</code>\n"

    cur.close()
    conn.close()

    if len(_to_reply) < chunk_size:
        return _to_reply

    else:
        return _to_reply[0:chunk_size] + "..."


class CmdResponse:
    def __init__(self, message):
        self.requestor = UserProfile(message.from_user.id)

    def log(self): pass


if __name__ == '__main__':
    print(UserProfile(324423).update("iujhugk", "jhkj"))
