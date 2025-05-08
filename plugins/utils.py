from sqlite3 import connect
import logging
from datetime import datetime
from json import load


logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.FileHandler('logs.log'))


class SqlRequest:
    def __init__(self, database: str = 'database.sql', table: str = 'users'):
        self.connection = connect(database)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.cursor.close()
        self.connection.close()

    def select_one(self):
        self.connection.execute()


class GeoRequest:
    def __init__(self, message):
        self.longitude = float (message.location.longitude)
        self.latitude = float (message.location.latitude)

        self.in_rea = 37.62 <= self.longitude <= 37.64 and 55.72 <= self.latitude <= 55.74


def who_is_requestor (message):
    requestor = message.from_user.full_name
    date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    group = None

    conn = connect('database.sql')
    cur = conn.cursor()

    cur.execute(f'SELECT name, group_name FROM users WHERE user_id = {message.from_user.id}')
    user = cur.fetchone()

    if user:
        requestor = user[0]
        group = user[1]

    cur.close()
    conn.close()

    logger.info(
            f'{date}_________________________\n' +
            f'{requestor} использовал следующую команду:\n' +
            f' -> {message.text}\n' +
            '____________________________________________\n')

    if message.chat.type == 'group':
        requestor = f'{message.chat.title} | {requestor}'

    return (f'{requestor}: {message.text}', group, requestor)


def crypt_anon_id(id: int) -> str:
    return str(id*7)[:-1]


def decrypt_anon_id(id: int) -> int:
    return int(str(id/7)[:-1])


if __name__ == "__main__":
    print(crypt_anon_id(428192863))
    print(crypt_anon_id(299735004))
