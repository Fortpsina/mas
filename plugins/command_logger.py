from sqlite3 import connect
import logging
from datetime import datetime
from json import load


logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.FileHandler('logs.log'))


def who_is_requestor (message, group: int = 1, date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")):

    requestor = message.from_user.full_name

    conn = connect('database.sql')
    cur = conn.cursor()

    cur.execute(f'SELECT name, user_id, reserve_1 FROM users WHERE user_id = {message.from_user.id}')
    user = cur.fetchall()
    if len(user) > 0:
        user = user[0]
        requestor = user[0]
        group = user[2]

    cur.close()
    conn.close()

    logger.info(
            f'{date}_________________________\n' +
            f'{requestor} использовал следующую команду:\n' +
            f' -> {message.text}\n' +
            '____________________________________________\n'
    )

    if message.chat.type == 'group':
        requestor = f'{message.chat.title} | {requestor}'

    return (f'{requestor}: {message.text}', group)

def select_color_by_id (id):
    conn = connect('database.sql')
    cur = conn.cursor()

    cur.execute(f'SELECT user_id, color FROM users WHERE user_id = {id}')
    user_clr = cur.fetchall() [0]

    cur.close()
    conn.close()

    return user_clr [1]

class GeoRequest:
    def __init__(self, message):
        self.conn = connect('database.sql')
        self.cur = self.conn.cursor()

        self.requestor = message.from_user.first_name
        self.user_id = message.from_user.id
        self.group_id = None
        self.group_name = None

        self.cur.execute(f'SELECT name, user_id, reserve_1 FROM users WHERE user_id = {message.from_user.id}')
        user = self.cur.fetchall()
        if len(user) > 0:
            user = user[0]
            self.requestor = user[0]
            self.user_id = user[1]
            self.group_id = user[2]
            self.group_name = select_group_by_id (self.group_id)

        self.longitude = float (message.location.longitude)
        self.latitude = float (message.location.latitude)
        self.in_rea = 37.62 <= self.longitude <= 37.64 and 55.72 <= self.latitude <= 55.74
        
    def __del__(self):
        self.cur.close()
        self.conn.close()


def select_group_by_id (id: int) -> str:
    groups = load(open('groups.json', 'r'))

    for group in groups:
        if group['id'] == id:
            return group['name']
    
    return "Группа не определена."
        
def select_group_by_name (name: str) -> int:
    groups = load(open('groups.json', 'r'))

    for group in groups:
        if group['name'] == name:
            return group['id']
        
    return 0
