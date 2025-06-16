from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot.types import KeyboardButton, ReplyKeyboardMarkup
from .user import UserProfile, Hs
from typing import Optional
from sqlite3 import connect
from math import ceil


class _TypeOfSorting:
    def __init__(self): pass


def color_chooser_markup() -> InlineKeyboardMarkup:
    choose_color_default = InlineKeyboardButton (text = 'Стандартный 🟤', callback_data = 'choose_color_default')
    choose_color_red =     InlineKeyboardButton (text = '🔴 Красный',     callback_data = 'choose_color_red')
    choose_color_pink =    InlineKeyboardButton (text = 'Розовый 🌺 ',    callback_data = 'choose_color_pink')
    choose_color_random =  InlineKeyboardButton (text = 'Рандомный 🎲',   callback_data = 'choose_color_random')
    choose_color_olive =   InlineKeyboardButton (text = 'Оливковый 🫒',    callback_data = 'choose_color_olive')
    choose_color_blue =    InlineKeyboardButton (text = '🔵 Синий',       callback_data = 'choose_color_blue')
    choose_color_ochre =   InlineKeyboardButton (text = 'Охра 🐪',        callback_data = 'choose_color_ochre')
    choose_color_yellow =  InlineKeyboardButton (text = '🟡 Жёлтый',      callback_data = 'choose_color_yellow')
    choose_color_purple =  InlineKeyboardButton (text = '🟣 Фиолетовый',  callback_data = 'choose_color_purple')
    choose_color_cyan =    InlineKeyboardButton (text = 'Циановый 🐋',    callback_data = 'choose_color_cyan')
    choose_color_white =   InlineKeyboardButton (text = '⚪ Белый',       callback_data = 'choose_color_white')
    choose_color_black =   InlineKeyboardButton (text = '⚫ Чёрный',      callback_data = 'choose_color_black')

    choose_color = InlineKeyboardMarkup()

    choose_color.row (choose_color_red, choose_color_olive)
    choose_color.row (choose_color_blue, choose_color_pink)
    choose_color.row (choose_color_yellow, choose_color_ochre)
    choose_color.row (choose_color_purple, choose_color_cyan)
    choose_color.row (choose_color_white, choose_color_default)
    choose_color.row (choose_color_black, choose_color_random)

    return choose_color


def profile_options_markup() -> InlineKeyboardMarkup:
    profile_settings_markup = InlineKeyboardMarkup ()

    profile_settings_markup_name  = InlineKeyboardButton (text = 'Смена имени',  callback_data = 'profile change Name')
    profile_settings_markup_vk    = InlineKeyboardButton (text = 'Смена ВК',     callback_data = 'profile change VK')
    profile_settings_markup_group = InlineKeyboardButton (text = 'Смена группы', callback_data = 'profile change Group')
    profile_settings_markup_color = InlineKeyboardButton (text = 'Цвет',         callback_data = 'profile change Color')
    
    profile_settings_markup.row(profile_settings_markup_name, profile_settings_markup_vk)
    profile_settings_markup.row(profile_settings_markup_group, profile_settings_markup_color)

    return profile_settings_markup


def select_hs_markup(page: int = 1, sort: _TypeOfSorting | None = None) -> InlineKeyboardMarkup:
    conn = connect('database.sql', check_same_thread=False)
    cur = conn.cursor()
    LIMIT = 10

    cur.execute("SELECT COUNT(*) FROM Hs")
    total_hs_pages: int = ceil(cur.fetchone()[0] / LIMIT)

    prev_page = InlineKeyboardButton(text = '⬅️', callback_data = f'hs page {page - 1 if page > 1 else total_hs_pages}')
    next_page = InlineKeyboardButton(text = '➡️', callback_data = f'hs page {page + 1 if page < total_hs_pages else 1}')
    page_counter = InlineKeyboardButton(text = f'{page} / {total_hs_pages}', callback_data="hs counter")

    hs_add = InlineKeyboardButton(text = '✏️', callback_data = f'hs add')
    hs_options = InlineKeyboardButton(text = '⚙️', callback_data = f'hs options')

    hs_markup = InlineKeyboardMarkup()


    cur.execute(f'SELECT id, name FROM Hs ORDER BY id DESC LIMIT {LIMIT}')
    for hs in cur.fetchall():
        hs_id, name = hs[0], hs[1]
        to_show = f'{hs_id} | {name}'
        hs_markup.row(InlineKeyboardButton(text=to_show, callback_data=f"hs view {name}"))

    if total_hs_pages > 1:
        hs_markup.row(prev_page, page_counter, next_page)

    hs_markup.row(hs_add, hs_options)

    return hs_markup


def select_group_markup() -> InlineKeyboardMarkup:
    group_markup = InlineKeyboardMarkup()

    back = InlineKeyboardButton(text = '↩', callback_data = f'groups back')
    group_add = InlineKeyboardButton(text = '✏️', callback_data = f'groups add')

    group_markup.row(back, group_add)
    
    return group_markup


def feedback_markup() -> InlineKeyboardMarkup:
    feedback_markup = InlineKeyboardMarkup(row_width = 1)
    feedback_markup.add(InlineKeyboardButton(text = 'Оставить отзыв', callback_data = 'feedback send'))
    feedback_markup.add(InlineKeyboardButton(text = 'Читать отзывы', callback_data = 'feedback read'))
    feedback_markup.add(InlineKeyboardButton(text = 'Читать гайд по команде', callback_data = 'feedback guide'))

    return feedback_markup


def exam_choosing_markup(exams) -> InlineKeyboardMarkup:
    exam_type_choosing = InlineKeyboardMarkup(row_width = 1)

    for exam in exams: # какие экзамены бывают
        exam_type_choosing.add(InlineKeyboardButton(text=f'{exam["name"]}',
                                                    callback_data = f'task previous 1 {exam["file"]}'))

    return exam_type_choosing


def exam_slidebar_markup(filename: str, additional_rights = False, index_of_task: int = 0) -> InlineKeyboardMarkup:
    task_menu = InlineKeyboardMarkup()

    previous_task = InlineKeyboardButton(text = '⬅️', callback_data = f'task previous {index_of_task} {filename}')
    edit_task = InlineKeyboardButton(text = '✏️', callback_data = f'task edit {index_of_task} {filename}')
    next_task = InlineKeyboardButton(text = '➡️', callback_data = f'task next {index_of_task} {filename}')
    delete_task = InlineKeyboardButton(text = '🗑', callback_data = f'task delete {index_of_task} {filename}')

    if additional_rights:
        task_menu.row(previous_task, edit_task, delete_task, next_task)
        
    else:
        task_menu.row(previous_task, edit_task, next_task)

    return task_menu


def donate_markup() -> InlineKeyboardMarkup:
    donate_markup_keyboard = InlineKeyboardMarkup(row_width = 1)

    donate_markup_keyboard.add(InlineKeyboardButton(text=f'Chairman', callback_data = f'donate Chairman'))

    return donate_markup_keyboard


def attendance_checker(text) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(KeyboardButton(text=text, request_location=True))
    return keyboard


def geo_help_markup(longitude: Optional[float], latitude: Optional[float]) -> InlineKeyboardMarkup:
    details_geo = InlineKeyboardMarkup()
    callback_data = f"geo details {longitude or '-'} {latitude or '-'}"
    details = InlineKeyboardButton(text = "❓", callback_data = callback_data)
    details_geo.add(details)
    return details_geo


def call_data() -> InlineKeyboardMarkup:
    call_data_markup = InlineKeyboardMarkup(row_width = 1)
    call_data_markup.add(InlineKeyboardButton(text = 'call', callback_data = 'call'))
    call_data_markup.add(InlineKeyboardButton(text = 'call data', callback_data = 'call data'))

    return call_data_markup


possible_markups = {'color_chooser_markup': color_chooser_markup,
                    'profile_options_markup': profile_options_markup,
                    'select_hs_markup': select_hs_markup,
                    'select_group_markup': select_group_markup,
                    'feedback_markup': feedback_markup,
                    'exam_choosing_markup': exam_choosing_markup,
                    'exam_slidebar_markup': exam_slidebar_markup,
                    'donate_markup': donate_markup,
                    'attendance_checker': attendance_checker,
                    'geo_help_markup': geo_help_markup,
                    'call_data': call_data}
