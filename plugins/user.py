from sqlite3 import connect
from datetime import datetime
from threading import Lock

USERS_STRUCT = """CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY,
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

HS_STRUCT = """
"""

GROUP_STRUCT = """
"""


def create_table(table_type: str, db: str = 'database') -> None:
    types = {
        "users": USERS_STRUCT,
        "hs": HS_STRUCT,
        "group": GROUP_STRUCT
    }
    assert table_type in types.keys(), "Указана несуществующая таблица."

    conn = connect(f'{db}.sql')
    cur = conn.cursor()

    cur.execute(types[table_type])
    conn.commit()

    cur.close()
    conn.close()


class UserProfile:
    def __init__(self, user_id: int):
        self.conn = connect('database.sql', check_same_thread=False)
        self.cur = self.conn.cursor()
        self.cur.execute(f'SELECT name, vk_link, color, group_name, registration_date FROM users WHERE user_id = {user_id}')

        user_data = self.cur.fetchone()
        self.user_id = user_id

        if user_data:
            self.exists = True
            self.user_name  = user_data[0]
            self.user_vk    = user_data[1]
            self.user_color = user_data[2]
            self.user_group = user_data[3]
            self.user_reg   = user_data[4]
        else:
            self.exists = False

    def update(self, column: str, new_value: str | int) -> str:
        _allowed = [word.split()[0] for word in USERS_STRUCT.splitlines()[1:]]
        if column not in _allowed:
            return f"Неизвестная колонна. Доступные значения: {_allowed}"
        
        db_lock = Lock()
        with db_lock:
            self.cur.execute(f'SELECT ? FROM users WHERE user_id = ?', (column, self.user_id))
            old_value = self.cur.fetchone()[0] or "?"

            self.cur.execute(f'UPDATE users SET {column} = ? WHERE user_id = ?', (new_value, self.user_id))
            self.conn.commit()

            return f"Значение изменено с {old_value} на {new_value}."
        
    def delete(self, physically: bool = False) -> str:
        if not self.exists:
            return "Пользователь с таким ID не найден."
        
        b_vklink = f'  Страница ВК: <code>{self.user_vk}</code>'
        b_tgid = f'  ID: <code>{self.user_id}</code>'
        b_color = f'  Цвет: <code>{self.user_color}</code>'
        b_reg = f'  Регистрация: <code>{self.user_reg}</code>'
        
        if physically:
            self.cur.execute(f'DELETE FROM users WHERE user_id = {self.user_id}')
            self.conn.commit()
            return f'Вы физически (безвозвратно) удалили профиль пользователя {self.user_name}:\n{b_vklink}\n{b_tgid}\n{b_color}\n{b_reg}'

        else:
            self.cur.execute(f'UPDATE users SET name = "Удалённый пользователь (Ранее: {self.user_name}, ID: {self.user_id})" WHERE user_id = {self.user_id}')
            self.cur.execute(f'UPDATE users SET user_id = 0 WHERE user_id = {self.user_id}')
            self.conn.commit()
            return f'Вы отключили профиль пользователя {self.user_name}:\n{b_vklink}\n{b_tgid}\n{b_color}\n{b_reg}'

    def __del__(self):
        self.cur.close()
        self.conn.close()


def register_user(message, **custom_data) -> None:
    conn = connect('database.sql')
    cur = conn.cursor()

    _name = custom_data.get("name",       message.from_user.full_name)
    _vk   = custom_data.get("vk_link",    "https://vk.com/example")
    _id   = custom_data.get("user_id",    message.from_user.id)
    _clr  = custom_data.get("color",      "default")
    _lvl  = custom_data.get("level",      100)
    _cnds = custom_data.get("conditions", "Н/Д")
    _hs   = custom_data.get("hs_name",    "УЗ не указано")
    _st   = custom_data.get("hs_struct",  "Структура УЗ не указана")
    _gr   = custom_data.get("group_name", "Группа не указана")
    _date = custom_data.get("reg_date",   datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
    _rl   = custom_data.get("rights",     1)
    _pprs = custom_data.get("papers",     "")

    cur.execute(
        'INSERT INTO Users (name, vk_link, user_id, color, level, conditions, hs_name, hs_struct, group_name, registration_date, rights_level, papers) ' +
        f'VALUES ("{_name}", "{_vk}", {_id}, "{_clr}", {_lvl}, "{_cnds}", "{_hs}", "{_st}", "{_gr}", "{_date}", {_rl}, "{_pprs}")')
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


if __name__ == '__main__':
    print(UserProfile().update("kek", 123))
