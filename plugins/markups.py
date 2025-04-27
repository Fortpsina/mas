from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

def main_help_markup(admin_version: bool = True) -> InlineKeyboardMarkup:
    help_menu = InlineKeyboardMarkup(row_width = 1)

    help_menu.add(InlineKeyboardButton(text = 'Команды для расписания', callback_data = 'help_menu_schedule'))
    if admin_version:
        help_menu.add(InlineKeyboardButton(text = 'Меню заданий', callback_data = 'help_menu_plan'))
        help_menu.add(InlineKeyboardButton(text = 'Административные команды', callback_data = 'help_menu_admin'))
    help_menu.add(InlineKeyboardButton(text = 'Прочие команды', callback_data = 'help_menu_other'))

    return help_menu


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
    profile_settings_markup_name =  InlineKeyboardButton (text = 'Смена имени',  callback_data = 'profile change Name')
    profile_settings_markup_vk =    InlineKeyboardButton (text = 'Смена ВК',     callback_data = 'profile change VK')
    profile_settings_markup_group = InlineKeyboardButton (text = 'Смена группы', callback_data = 'profile change Group')
    profile_settings_markup_color = InlineKeyboardButton (text = 'Цвет',         callback_data = 'profile change Color')
    
    profile_settings_markup = InlineKeyboardMarkup ()
    
    profile_settings_markup.row (profile_settings_markup_name, profile_settings_markup_vk)
    profile_settings_markup.row (profile_settings_markup_group, profile_settings_markup_color)

    return profile_settings_markup


def group_chooser_markup() -> InlineKeyboardMarkup:
    from config import groups
    
    group_menu = InlineKeyboardMarkup(row_width = 1)
    for group in groups:
        group_menu.add(InlineKeyboardButton(text = group['name'], callback_data = f'group set {group["id"]}'))
    group_menu.add(InlineKeyboardButton(text = 'Нет моей группы', callback_data = f'group set {1}'))

    return group_menu
