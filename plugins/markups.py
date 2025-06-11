from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from .user import UserProfile

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
    _nums = ('1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟')
    page_numbers = 1

    prev_page = InlineKeyboardButton(text = '⬅️', callback_data = f'hs page {page - 1 if page > 1 else page_numbers}')
    next_page = InlineKeyboardButton(text = '➡️', callback_data = f'hs page {page + 1 if page < page_numbers else 1}')
    page_counter = InlineKeyboardButton(text = f'{page} / {page_numbers}', callback_data="...")

    hs_add = InlineKeyboardButton(text = '✏️', callback_data = f'hs add')
    hs_options = InlineKeyboardButton(text = '⚙️', callback_data = f'hs menu options')

    hs_markup = InlineKeyboardMarkup()

    for hs in _nums:
        nigger = InlineKeyboardButton(text=hs, callback_data="...")
        hs_markup.row(nigger)

    hs_markup.row(prev_page, page_counter, next_page)
    hs_markup.row(hs_add, hs_options)

    return hs_markup


def feedback_markup() -> InlineKeyboardMarkup:
    feedback_markup = InlineKeyboardMarkup(row_width = 1)
    feedback_markup.add(InlineKeyboardButton(text = 'Оставить отзыв', callback_data = 'feedback send'))
    feedback_markup.add(InlineKeyboardButton(text = 'Читать отзывы', callback_data = 'feedback read'))
    feedback_markup.add(InlineKeyboardButton(text = 'Читать гайд по команде', callback_data = 'feedback guide'))

    return feedback_markup


def call_data() -> InlineKeyboardMarkup:
    call_data_markup = InlineKeyboardMarkup(row_width = 1)
    call_data_markup.add(InlineKeyboardButton(text = 'call', callback_data = 'call'))
    call_data_markup.add(InlineKeyboardButton(text = 'call data', callback_data = 'call data'))

    return call_data_markup
