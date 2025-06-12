from sqlite3 import connect
import logging
from datetime import datetime
from random import randint, choice
from telebot.types import ReactionTypeEmoji
from config import *

if __name__ == "__main__":
    from user import UserProfile
    from langs import not_enough_rights, profile_not_found
else:
    from .user import UserProfile
    from .langs import not_enough_rights, profile_not_found


logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.FileHandler('logs.log'))


class NotEnoughRightsError(Exception): pass
class ProfileNotFoundError(Exception): pass
class ProfileAlreadyExistsError(Exception): pass


class GeoRequest:
    def __init__(self, message):
        self.longitude = float (message.location.longitude)
        self.latitude = float (message.location.latitude)

        self.in_rea = 37.62 <= self.longitude <= 37.64 and 55.72 <= self.latitude <= 55.74


def basic_universal_logger(user: UserProfile, message) -> None:
    name = user.user_name if user.exists else message.from_user.full_name
    date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    _log = f'{date} | [{user.user_id}] {name}: {message.text}'

    logger.info(_log)
    print(_log)


def basic_cmd_logger(func):
    def wrapper(message):
        user = UserProfile(message.from_user.id)
        basic_universal_logger(user, message)

        if randint(0, RANDOM_EMODJI_CHANCE) == 1:
            emoji_reaction(message, choice(RANDOM_EMOJI_EASTERN_EGG))

        if not user.exists or user.rights >= 1:
            try:
                func(message)
            except AssertionError as expected_error_msg:
                bot.reply_to(message, expected_error_msg, parse_mode='html')
            except Exception as error_msg:
                bot.reply_to(message, error_msg, parse_mode='html')
                print(error_msg)
        else:
            bot.reply_to(message, not_enough_rights(message))

    return wrapper


def group_management_cmd_logger(func):
    def wrapper(message):
        user = UserProfile(message.from_user.id)
        basic_universal_logger(user, message)

        _incorrect_group_assets = ('Группа не указана')
        
        if not user.exists:
            bot.reply_to(message, profile_not_found(message, True))
        elif user.rights < 2:
            bot.reply_to(message, not_enough_rights(message))
        elif user.user_group in _incorrect_group_assets:
            bot.reply_to(message, 'Не могу определить Вашу группу. Используйте /profile для её настройки и устранения этой ошибки.')
        else:
            try:
                func(message)
            except AssertionError as expected_error_msg:
                bot.reply_to(message, expected_error_msg, parse_mode='html')
            except Exception as error_msg:
                bot.reply_to(message, error_msg, parse_mode='html')
                print(error_msg)

    return wrapper


def emoji_reaction(message, emoji):
    bot.set_message_reaction(chat_id=message.chat.id,
                             message_id=message.id,
                             reaction=[ReactionTypeEmoji(emoji=emoji)])


def who_is_requestor(message):
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

    logger.info(f'{date} | {requestor}: {message.text}\n')

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
