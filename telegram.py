import sqlite3

from telebot import types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReactionTypeEmoji, InputMediaPhoto

import datetime
from datetime import timedelta

import sys, json
from pathlib import Path

from plugins.user import *
from plugins.feedbacks import *
from plugins.schedule import *
from plugins.markups import *
from plugins.name_checker import *
from plugins.langs import *
from plugins.utils import *
from plugins.chat_moder import *

from plugins.DayOfWeek import is_date
from plugins.TagSwitcher import tags_swither

from config import *


PROJECT_ROOT = Path(__file__).parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@bot.message_handler(commands=['start', 'reg', 'register'])
@basic_cmd_logger
def start(message):
    new_user = UserProfile(message.from_user.id)

    if len(message.text.split()) == 2 and new_user.rights >= 4:
        return bot.reply_to(message, register_another_user(
            int(message.text.split()[1])))
    
    if new_user.exists:
        raise ProfileAlreadyExistsError(frofile_exists_already(message))

    if CONTROL_USERS_TABLE:
        create_table("users")
        reg_notify(message)

    register_user(message.from_user.full_name, message.from_user.id)
    new_user.exists = True

    bot.send_message(message.chat.id, reg_text(message, 1), parse_mode='html')
    bot.register_next_step_handler(message, user_name, new_user)

def user_name(message, new_user: UserProfile):
    _name_params = name_helper(message.text.strip())
    new_user.update('name', _name_params['name'])

    emoji = "🔥" if  not _name_params['anything_was_deleted'] else "🤡"
    emoji_reaction(message, emoji)

    bot.send_message(message.chat.id, reg_text(message, 2), parse_mode='html')
    bot.register_next_step_handler(message, user_pass, new_user)

def user_pass(message, new_user: UserProfile):
    new_user.update('conditions', message.text.strip())
    bot.send_message (message.chat.id, reg_text(message, 3), parse_mode = 'html', reply_markup = select_hs_markup())

@bot.message_handler(commands=['forcereg'])
def forcereg(message):
    if message.from_user.id == fortpsina_id:
        create_table("users")
        register_user(message.from_user.full_name,
                      message.from_user.id,
                      conditions = 'Ознакомлен, согласен',
                      rights = 5)
        bot.reply_to(message, 'Пользователь зарегестрирован.')


@bot.message_handler(commands=['help', '?', 'commands', 'команды', 'помощь', 'tutorial'])
@basic_cmd_logger
def help(message):
    bot.reply_to(message, help_text(message, 'general'), parse_mode='html')


@bot.message_handler(commands=['fill'])
@group_management_cmd_logger
def update_the_schedule_step_1 (message):
    bot.reply_to(message, fill_schedule_instruction(message), parse_mode = 'html')
    bot.register_next_step_handler(message, update_the_schedule_step_2)

def update_the_schedule_step_2 (message):
    requestors_group = UserProfile(message.from_user.id).user_group
    bot.reply_to (message, Schedule.fill_week(message.text, requestors_group), parse_mode='html')


@bot.message_handler(commands=['attend'])
def attend (message):
    global expect_geo
    if message.from_user.id in expect_geo:
        bot.reply_to(message, attendance_text(message, 'await'))
        return
    expect_geo.append(message.from_user.id)

    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text = attendance_text(message, 'button'), request_location = True))

    bot.reply_to (message, text = attendance_text(message, 'handle'), reply_markup = keyboard, parse_mode = 'html')


@bot.message_handler(content_types=['location'])
def location_handler(message):
    requestor = UserProfile(message.from_user.id)
    if not requestor.exists:
        bot.reply_to(message, attendance_text(message, 'cannotfind'))
        return

    geo = GeoRequest(message)

    global expect_geo
    if message.from_user.id in expect_geo:
        expect_geo.remove(message.from_user.id)

    if geo.in_rea:
        bot.reply_to (message, Schedule(requestor.user_group).attend(requestor.user_name))
    else:
        details_geo = InlineKeyboardMarkup()
        details_geo.add(InlineKeyboardButton(text = "Подробнее", callback_data = f"geo details {geo.longitude} {geo.latitude}"))
        bot.reply_to(message, 'В отметке отказано, вы не на паре.', reply_markup = details_geo)


@bot.message_handler(commands=['attendance'])
@group_management_cmd_logger
def attendance(message):
    user = UserProfile(message.from_user.id)
    bot.reply_to(message, Schedule(group_id=user.user_group).attendance())


@bot.message_handler(commands=['schedule', 's', 'с', 'расписание', 'р'])
@basic_cmd_logger
def schedule (message):
    requestor = UserProfile(message.from_user.id)

    if not requestor.exists:
        raise ProfileNotFoundError(profile_not_found(message, True))
    
    week_modifier = 0
    lesson_date = datetime.now().strftime('%d.%m.20%y')

    _basic_schedule = Schedule(lesson_date=lesson_date, group=requestor.user_group)

    if len(message.text.split()) > 1:
        arg = message.text.split()[1]

        if '+' in arg and arg.replace('+', '').isdigit():
            week_modifier += int(arg.replace('+', ''))
        elif '-' in arg and arg.replace('-', '').isdigit():
            week_modifier -= int(arg.replace('-', ''))
        elif message.text.split()[1] == 'create_table':
            bot.reply_to(message, _basic_schedule.create_schedule())

    temp_msg_notify = bot.reply_to(message, 'Готовлю для вас ваше расписание...')

    render_schedule = _basic_schedule.render(color=requestor.user_color, week_modifier=week_modifier*7)

    media_group = []
    for photo in ('rendered_schedule/Monday_Image.png',
                  'rendered_schedule/Tuesday_Image.png',
                  'rendered_schedule/Wednesday_Image.png',
                  'rendered_schedule/Thursday_Image.png',
                  'rendered_schedule/Friday_Image.png',
                  'rendered_schedule/Saturday_Image.png'):

        if 'Monday' in photo:
            to_reply = render_schedule['reply'] + attendance_bar(message)
            media_group.append(InputMediaPhoto(open(photo, 'rb'), caption=to_reply, parse_mode='html'))

        else:
            media_group.append(InputMediaPhoto(open(photo, 'rb')))

    bot.send_media_group (message.chat.id, media = media_group, reply_to_message_id = message.id)
    bot.delete_message (message_id = temp_msg_notify.message_id, chat_id = message.chat.id)


@bot.message_handler(commands=['цвет', 'color'])
@basic_cmd_logger
def settings(message):
    bot.send_message (message.chat.id, f'Выбор темы', reply_markup=color_chooser_markup())


@bot.message_handler(commands=['dev'])
@basic_cmd_logger
def dev_tools(message):
    command = message.text.split()
    user = UserProfile(message.from_user.id)

    assert len(command) >= 2, DEV_HELP

    if user.rights >= 4 and command[1] == 'users':
        bot.reply_to(message, users_list(), parse_mode='html')

    elif message.from_user.id == fortpsina_id and command[1] == 'rights':
        # /dev rights 428192863 5
        bot.reply_to(message, UserProfile(int(command[2])).update('rights_level', int(command[3])))

    elif len(command) > 2 and command[1] == 'delete':
        to_delete = UserProfile(int(command[2]))

        if not user.rights >= 4:
            raise NotEnoughRightsError(not_enough_rights(message))
        
        elif not to_delete.exists:
            raise ProfileNotFoundError(profile_not_found(message, False))
        
        physically = len(command) == 4 and command[3] == "physically"
        bot.reply_to(message, to_delete.delete(physically), parse_mode='html')

    elif command[1] == 'id':
        bot.reply_to(message, f'<code>{message.from_user.id}</code>', parse_mode='html')

    elif command[1] == 'message':
        bot.send_message(message.chat.id, message)

    elif user.rights >= 4 and command[1] == 'markup':
        _possible_markups = {'color_chooser_markup': color_chooser_markup,
                                'profile_options_markup': profile_options_markup,
                                'select_hs_markup': select_hs_markup,
                                'feedback_markup': feedback_markup}
        
        possibles = '\n'.join([f"<code>{m}</code>" for m in _possible_markups.keys()])

        if len(command) < 3:
            bot.reply_to(message, text=dev_keyboard_preview(message, "possible")+possibles, parse_mode='html')
            return
        
        bot.send_message(message.chat.id, dev_keyboard_preview(message, "preview"), reply_markup=_possible_markups.get(command[2])())

    elif user.rights == 5 and command[1] == "execute":
        exec(message.text.replace('/dev execute ', '', 1))


@bot.message_handler(commands=['profile', 'prof', 'профиль'])
@basic_cmd_logger
def interactive_profile(message):
    cmd = message.text.split()
    _id = message.from_user.id
    _own_prifile = True

    if len(cmd) == 3 and cmd[2].isdigit():
        _id = int(cmd[2])
        _own_prifile = False
    elif len(cmd) == 2 and cmd[1].isdigit():
        _id = int(cmd[1])
        _own_prifile = False

    profile = UserProfile(_id)
    assert profile.exists, profile_not_found(message, _own_prifile)
    
    _to_reply = f"Профиль <b>{profile.user_name}</b>:\n\n"
    _to_reply += f"  Группа: <code>{profile.user_group}</code>\n"
    _to_reply += f"  ВК: <code>{profile.user_vk}</code>\n"
    _to_reply += f"  ID: <code>{profile.user_id}</code>\n"
    _to_reply += f"  Цвет: <code>{profile.user_color}</code>\n"
    _to_reply += f"  Регистрация: <code>{profile.user_reg}</code>\n"

    bot.reply_to(message, _to_reply, parse_mode='html', reply_markup=profile_options_markup() if _own_prifile else None)

@basic_cmd_logger
def set_new_profile_name(message):
    profile = UserProfile(message.from_user.id)

    assert profile.exists, profile_not_found(message, True)

    new_name = name_helper(message.text.strip())['name']
    bot.reply_to(message, profile.update('name', new_name), parse_mode = 'html')

@basic_cmd_logger
def set_new_profile_vk(message):
    profile = UserProfile(message.from_user.id)

    MAX_LINK_LENGHT = 48
    assert profile.exists, profile_not_found(message, True)
    assert len(message.text) < MAX_LINK_LENGHT, too_long_value(message, len(message.text), MAX_LINK_LENGHT)

    bot.reply_to(message, profile.update('vk_link', message.text.strip()))


@bot.message_handler(commands=['exam'])
@basic_cmd_logger
def find_answer_for_exam (message):
    exams = json.load(open('answers.json', 'r'))

    all_tags = []
    all_files = []

    for el in exams:
        all_files.append (el ['file'])
        for tag in el ['tags']:
            all_tags.append (tag)

    if len (message.text.split()) == 1:
        exam_type_choosing = InlineKeyboardMarkup(row_width = 1)

        for el in exams: # какие экзамены бывают
            exam_type_choosing.add(InlineKeyboardButton(text = f'{el["name"]}', callback_data = f'task previous 1 {el["file"]}'))

        bot.reply_to(message, help_switcher(message, 'exam'), parse_mode = 'html', reply_markup = exam_type_choosing)

    elif len (message.text.split()) == 2 and message.text.split()[1].lower() == 'config':
        bot.reply_to (message, EXAM_CONFIGS + exams)

    elif len (message.text.split()) > 2 and message.text.split()[1].lower() == 'delete':
        if len (message.text.split()) == 2 or len (message.text.split()) > 3 or message.text.split()[2] not in all_tags:
            bot.reply_to(message, EXAM_NOT_EXISTING_TAG_ERROR, parse_mode = 'html')
            return

        bot.reply_to(message, not_enough_rights(message))
        return

    elif len (message.text.split()) == 2 and message.text.split()[1].lower() in all_tags:
        for el in exams:
            if message.text.split()[1] in el['tags']:

                conn = sqlite3.connect(f'{el["file"]}.sql')
                cur = conn.cursor()

                cur.execute('SELECT * FROM exam_tasks')
                tasks = cur.fetchall()

                i = len (tasks)
                index_of_task = 0
                q = tasks[index_of_task]

                previous_task = InlineKeyboardButton(text = '⬅️', callback_data = f'task previous {index_of_task} {el["file"]}')
                edit_task = InlineKeyboardButton(text = '✏️', callback_data = f'task edit {index_of_task} {el["file"]}')
                next_task = InlineKeyboardButton(text = '➡️', callback_data = f'task next {index_of_task} {el["file"]}')

                task_menu = InlineKeyboardMarkup()
                task_menu.row(previous_task, edit_task, next_task)
                print (task_menu)

                text_to_reply = f'Вопрос <b>{q[1]} / {i}</b>:\n{q[2]}\n\n<i>{q[3]}</i>\n\n{q[4]}'

                cur.close()
                conn.close()

                bot.reply_to (message, text_to_reply, parse_mode = 'html', reply_markup = task_menu)

    elif len(message.text) >= 3 and message.text.split()[2].lower() in all_tags and message.text.split()[1].lower() in ("q", "questions", "question"):
        for el in exams:
            if message.text.split()[2] in el['tags']:
                _filename = el['file']
                conn = sqlite3.connect(f'{_filename}.sql')
                cur = conn.cursor()
                cur.execute('SELECT task_id, question, authors FROM exam_tasks')

                _name_dp = el['name_dp']
                to_reply = f"Вопросы к <b>{_name_dp}</b>:\n"
                all_tasks = cur.fetchall()

                chunk_size = 4000

                for _task in all_tasks:
                    _has_answer = "✅" if len(_task[2]) > 15 else "❌"
                    _numeration = "" if _task[1].strip()[0].isdigit() else f"{_task[0]}. "
                    #_do_wraping: bool = (len(to_reply) + len(_task) + 13 <= chunk_size) or (len(to_reply) > chunk_size and chunk_size + len(_task) + 13 <= chunk_size*2)
                    #wraping_entry = "<code>" if _do_wraping else ""
                    #wraping_exit = "</code>" if _do_wraping else ""
                    to_reply += f"{_numeration}{_task[1].strip()} | {_has_answer}\n"
                to_reply += "\n(галочкой отмечены вопросы с ответами, крестиком - без ответов)"

                if len(to_reply) <= chunk_size:
                    bot.reply_to(message, to_reply, parse_mode="html")
                else:
                    chunks = [to_reply[i:i+chunk_size] for i in range(0, len(to_reply), chunk_size)]

                    # Первое сообщение отправляем как reply
                    bot.reply_to(message, chunks[0], parse_mode="html")

                    # Остальные части отправляем как новые сообщения
                    for chunk in chunks[1:]:
                        bot.send_message(message.chat.id, chunk, parse_mode="html")

                cur.close()
                conn.close()
                return

        else:
            bot.reply_to(message, f"Не удалось найти экзамен по запросу <code>{message.text.split()[2].lower()}</code>", parse_mode="html")

    elif len (message.text.split()) == 3 and message.text.split()[2].isnumeric():
        task_number = message.text.split()[2]
        exam_type = message.text.split()[1]

        if exam_type not in all_tags:

            to_reply = ''
            for el in exams:
                to_reply += f'\n<b>{el["name"]}</b>: '
                for tag in el['tags']:
                    to_reply += f'<code>{tag}</code>, '

            bot.reply_to(message, f'Доступные предметы:\n{to_reply}\n\n<i>Используйте один из алиасов, выделенных <code>моноширинным</code> шрифтом. Их можно скопировать при нажатии.</i>', parse_mode = 'html')
            return

        for el in exams:

            for tag in el['tags']:
                if tag == exam_type:

                    conn = sqlite3.connect(f'{el["file"]}.sql')
                    cur = conn.cursor()

                    cur.execute('SELECT * FROM exam_tasks')
                    tasks = cur.fetchall()

                    if int (task_number) > len (tasks):
                        bot.reply_to(message, f'По <b>{el["name_dp"]}</b> существует всего <b>{len(tasks)}</b> вопросов.', parse_mode = 'html')
                        return

                    for task in tasks:
                        if int (task_number) == int (task[1]):
                            bot.reply_to(message, f'<b>Вопрос №{task_number}. <code>{task[2]}</code></b>\n\n<i>{task[3]}</i>\n\n{task[4]}', parse_mode = 'html')

                    cur.close()
                    conn.close()

    elif len (message.text.split()) >= 3 and message.text.split()[1].lower() == 'set':
        discipline = message.text.replace('/exam set ', '')
        max_name_len = 24

        if len (discipline) > max_name_len:
            optional_name_offer_1 = ''
            optional_name_offer_2 = ''
            optional_name_offer_3 = ''

            optional_name_offer_1 += discipline[0].upper()
            for el in discipline[1:max_name_len - 1]:
                optional_name_offer_1 += el

            for el in discipline.split():
                if len (optional_name_offer_2) + len (el) <= max_name_len:
                    optional_name_offer_2 += f'{el}'.replace(f'{el[0]}', f'{el[0].upper()}')


            if 1 < len (discipline.split()) < max_name_len + 1:
                for el in discipline.split():
                    optional_name_offer_3 += el[0].upper()

            bot.reply_to(message,
                            f'Максимальная длина названия: <b>{max_name_len}</b>.\n' +
                            f'Ваша длина: <b>{len(discipline)}</b>\n\n' +
                            f'Предлагаю варианты:\n<code>{optional_name_offer_1}</code>\n' +
                            f'<code>{optional_name_offer_2}</code>\n' +
                            f'<code>{optional_name_offer_3}</code>',
                            parse_mode = 'html')
            return


        try:
            data = json.load (open('answers.json', 'r', encoding='utf-8'))

        except json.JSONDecodeError:
            data = []

        for dict in data:
            if discipline in dict.values ():
                break
        else:
            data.append (tags_swither (discipline))
            json.dump (data, open ('answers.json', 'w', encoding='utf-8'), ensure_ascii = False, indent = 4)

        bot.reply_to(message, f'Вы создали новую таблицу <b>"{discipline}"</b>.\n\nОтправьте в чат список вопросов по принципу заполнения плана.\n\n<b>Правила оформлени перечня:</b>\n<i>1. В списке НЕ должно быть номеров вопросов;\n2. В списке НЕ должно быть лишних отступов;\n3. Одна строчка = 1 вопрос;\n4. Избегайте любых ковычек, поскольку они ломают скрипты;\n5. Учитывайте, что перечень вопросов может быть больше максимальной длины сообщения. Если в одно сообщение не поместятся все вопросы, просто повторите команду <code>{message.text}</code> и отправьте только те вопросы, которые не поместились изначально - они будут добавлены к общему перечню.</i>', parse_mode = 'html')

        conn = sqlite3.connect(f'{discipline}.sql')
        cur = conn.cursor()

        cur.execute(
            'CREATE TABLE IF NOT EXISTS exam_tasks ' +
            '(id int auto_increment primary key, task_id INTEGER, question varshar(256), answer varshar(4096), authors varshar(512), is_deleted varshar (10))'
        )
        conn.commit()

        cur.execute('SELECT * FROM exam_tasks')
        tasks = cur.fetchall()
        cur.close()
        conn.close()

        bot.register_next_step_handler (message, set_tasks_for_exam, discipline)

    else:
        request_key = message.text.replace('/exam ', '').lower()
        all_results = []

        for el in all_files:
            conn = sqlite3.connect(f'{el}.sql')
            cur = conn.cursor()

            cur.execute('SELECT * FROM exam_tasks')
            tasks = cur.fetchall()

            for task in tasks:
                if request_key in task[2].lower():
                    all_results.append(f'<code>{task[2]}</code>\n\n<i>{task[3]}</i>\n\n{task[4]}')

            cur.close()
            conn.close()

        if len(all_results) > 20:
            bot.reply_to(message, f'По запросу "<code>{request_key}</code>" найдено слишком много результатов: <b>{len(all_results)}</b>. Детализируйте свой поисковой запрос.', parse_mode = 'html')
            return

        bot.reply_to(message, f'По запросу "{request_key}" найдено {len (all_results)} результатов.', parse_mode = 'html', disable_notification = True)
        for el in all_results:
            bot.send_message(message.chat.id, el, parse_mode = 'html', disable_notification = True)

def set_tasks_for_exam (message, discipline):
    try:
        all_tasks = message.text.splitlines()

        for el in all_tasks:
            if len(el) < 2:
                all_tasks.remove(el)

        conn = sqlite3.connect(f'{discipline}.sql')
        cur = conn.cursor()

        cur.execute('SELECT * FROM exam_tasks')
        tasks = cur.fetchall()

        i = len (tasks) + 1

        for el in all_tasks:
            cur.execute (
                'INSERT INTO exam_tasks ' +
                '(task_id, question, answer, authors, is_deleted) ' +
                'VALUES ("%s", "%s", "%s", "%s", "%s")' % (i, el, 'Пока что ответа нет, но Вы можете его установить или подождать, когда он повяится.', f'<b>Авторы:</b>', 'False')
            )
            i += 1

        conn.commit()

        cur.execute('SELECT * FROM exam_tasks')
        tasks = cur.fetchall()

        to_reply = f'Записаны следующие вопросы к экзамену по предмету <i><b>"{discipline}"</b></i>:\n'
        for task in tasks:
            to_reply += f'\n{task[1]}. <i>{task[2]}</i>'
            print (f'task: {task}')

        try:
            bot.send_message(message.chat.id, f'{to_reply}\n\nДля ответа на вопросы используйте команду <code>/examanswer [Предмет] [Номер вопроса] [Ответ]</code>', parse_mode = 'html')

        except:
            bot.send_message(message.chat.id, f'Число вопросов по {discipline} в б/д: <b>{len(to_reply.splitlines()) - 2}</b>.\n\nДля ответа на вопросы используйте команду <code>/examanswer [Предмет] [Номер вопроса] [Ответ]</code>', parse_mode = 'html')

        bot.delete_message(message_id = message.id, chat_id = message.chat.id)

        if mas == True:
            bot.send_message (428192863, f'Указанные вопросы:\n{message.text}')

        cur.close()
        conn.close()

    except Exception as _ex:
        print (_ex)
        bot.reply_to(message, 'Произошла непредвиденная ошибка.')


@bot.message_handler(commands=['examanswer'])
@basic_cmd_logger
def examanswer (message):
    user = UserProfile(message.from_user.id)
    cmd = message.text.split()

    RIGHTS_LEVEL_TO_DELETE_EDIT_STORY = 3
    ADMIN_TIP = "<i>Вы можете использовать <b>cstory</b> вместо аргумента [Ответ], чтобы удалить историю редактирований.</i>" if user.rights >= RIGHTS_LEVEL_TO_DELETE_EDIT_STORY else ""
    
    if not user.exists:
        raise ProfileNotFoundError(profile_not_found(message, True))
    
    assert len(cmd) >= 4, f'Формат команды: <code>/examanswer [Предмет] [Номер вопроса] [Ответ]</code>\n\n{ADMIN_TIP}'

    filename = cmd[1]
    task_id = int(cmd[2])
    date = datetime.now().strftime("%d:%m:%Y %H:%M:%S")
    exams = json.load(open('answers.json', 'r'))

    for el in exams:
        if cmd[1] in el['tags']:
            filename = el['file']
            break
    else:
        bot.reply_to(message, f'Не найден список вопросов к предмету "{cmd[1]}".')
        return

    conn = connect(f'{filename}.sql')
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM exam_tasks WHERE task_id = {task_id}')
    exam_task = cur.fetchone()
    new_authors = f''

    if cmd[3] == 'cstory':
        new_authors = f'Записи о редакциях были удалены {date}'

        if not user.rights >= 3:
            raise NotEnoughRightsError(not_enough_rights(message))

    else:
        text_of_the_question = exam_task[2]
        old_authors = exam_task[4]
        new_authors = f'{old_authors}\n{user.user_name} (ред. от {date})'

    new_answer = ' '.join(message.text.split()[3:])

    if cmd[3] != 'cstory':
        cur.execute('UPDATE exam_tasks SET answer = ? WHERE task_id = ?', (new_answer, task_id))
    cur.execute('UPDATE exam_tasks SET authors = ? WHERE task_id = ?', (new_authors, task_id))
    conn.commit()

    bot.reply_to(message, f'{f"Установлен ответ на вопрос №{task_id} ({text_of_the_question})." if cmd[3] != "cstory" else "История изменений была удалена."}', parse_mode = 'html')

    cur.close()
    conn.close()

def examanswer_markup (message, calldata, requestor, temp_msg, filename, call):

    index_of_task = int (calldata.split()[2])

    if len (message.text) > 3600:
        bot.reply_to(message, f'Максимальная длина ответа: 3600 символов. <i>Ваша длина: <b>{len(message.text)}</b>.</i>\n\n<i>Постарайтесь сократить решение и повторить попытку.</i>', parse_mode = 'html')
        return

    try:
        conn = sqlite3.connect(f'{filename}.sql')
        cur = conn.cursor()
        cur.execute('SELECT * FROM exam_tasks')
        exam_tasks = cur.fetchall()

        for el in exam_tasks:
            if int (el [1]) == int (index_of_task + 1):

                new_authors = f'{el [4]}\n{requestor} (ред. от {datetime.now().strftime("%d:%m:%Y %H:%M:%S")})'

                if mas:
                    actual_time = datetime.now() + timedelta(hours=3)
                    new_authors = f'{el [4]}\n{requestor} (ред. от {actual_time.strftime("%d.%m.%Y %H:%M:%S")})'

                answer = str (message.text)
                answer = answer.replace ('"', '')
                answer = answer.replace ("'", '')

                cur.execute (f'UPDATE exam_tasks SET answer = "{answer}" WHERE task_id = {int (el [1])}')
                cur.execute (f'UPDATE exam_tasks SET authors = "{new_authors}" WHERE task_id = {int (el [1])}')
                conn.commit ()

                bot.delete_message (message_id = temp_msg.message_id, chat_id = temp_msg.chat.id)
                bot.delete_message (message_id = message.message_id, chat_id = message.chat.id)
                bot.answer_callback_query (callback_query_id = call.id,
                                           show_alert = True,
                                           text = f'Ответ №{index_of_task + 1} установлен.')

        cur.close ()
        conn.close ()

    except Exception as _ex:
        print ('Произошла непредвиденная ошибка: ', _ex)
        bot.answer_callback_query (callback_query_id = call.id,
                                    text = f'Произошла непредвиденная ошибка{f": {_ex}" if len (str (_ex)) < 300 else ""}')
        #bot.reply_to(message, f'Произошла непредвиденная ошибка{f": {_ex}" if len (str (_ex)) < 1000 else ""}')


@bot.message_handler(commands=['mute'])
@basic_cmd_logger
def mute_user (message):
    requestor = UserProfile(message.from_user.id)
    command = message.text.split()

    if requestor.rights < 4:
        raise NotEnoughRightsError(not_enough_rights(message))
    
    if len(command) < 3 or command[1] == '?':
        raise CommandStructureError(help_switcher(message, 'mute'))
    
    if len(command) > 1 and command [1] == 'wipe':
        try:
            pun_logs = json.load(open('punishments.json', 'r', encoding='utf-8'))

        except json.JSONDecodeError:
            pun_logs = []

        bot.reply_to (message, 'Вы удалили все имеющиеся наказания. Отправляю вам их перечень.')

        for el in pun_logs:
            bot.send_message (message.from_user.id, f'{el}')
            print (el)

        json.dump([], open('punishments.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

        return

    reason = ''.join(command[2:]) or "Не указано"

    if not command[2].isdigit():
        bot.reply_to (message, 'Укажите время мута в секундах.')
        return

    elif int(command[2]) > 315360000:
        bot.reply_to(message, 'Максимальное время, на которое можно выдать мут:\n\n - <code>315360000</code> секунд \n - <code>10</code> лет.', parse_mode = 'html')
        return

    first_date_readable = f'{datetime.now().strftime("%d:%m:%Y %H:%M:%S")}'
    if mas:
        actual_time = datetime.now() + timedelta(hours=3)
        first_date_readable = f'{actual_time.strftime("%d.%m.%Y %H:%M:%S")}'

    second_date = datetime.now() + timedelta(seconds = int (command[2]))
    second_date_readable = second_date.strftime("%d.%m.%Y %H:%M:%S")
    if mas:
        actual_time = datetime.now() + timedelta(hours=3) + timedelta(seconds = int (command[2]))
        second_date_readable = f'{actual_time.strftime("%d.%m.%Y %H:%M:%S")}'

    pun_append (punnished_id = command[1],
                reason = reason,
                pun_author = requestor.user_name,
                pun_type = message.text.split()[0].replace('/', ''),
                first_date = message.json['date'],
                pun_time = int (command[2]),
                second_date_readable = second_date_readable)


    bot.reply_to(message, parse_mode = 'html',
                 text=f'''Выдача мута пользователю {command[1]}:\n Причина: <code>{reason}</code>;\n\nНачало мута: <code>{first_date_readable}</code>\nКонец мута: <code>{second_date_readable}</code>''',)


@bot.message_handler(commands=['unmute'])
def unmute_user (message):
    if message.from_user.id not in admin_id:
        bot.reply_to(message, not_enough_rights(message))
        return

    if len (message.text.split()) == 1:
        bot.reply_to(message, 'Неверный формат:\n<code>/unmute [ID]</code>', parse_mode = 'html')
        return

    if message.text.split()[1].isdigit() == False:
        bot.reply_to (message, 'ID указан неверно.')
        return

    mute_id = int (message.text.split()[1]) - 1

    try:
        data = json.load(open('punishments.json', 'r', encoding='utf-8'))

    except json.JSONDecodeError:
        data = []

    for el in data:
        if int (el['punishment_id']) == mute_id:
            if len(message.text.split()) > 2 and message.text.split()[2] == 'perm':
                el['ignore_punishment'] = True
                data[mute_id] = el
                json.dump(data, open('punishments.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
                bot.reply_to(message, f'Мут №{message.text.split()[1]} снят.\nСледующие муты этого пользователя бот будет игнорировать.')

            else:
                data.remove(el)
                json.dump(data, open('punishments.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
                bot.reply_to(message, f'Мут №{message.text.split()[1]} снят.')

            break

    else:
        bot.reply_to(message, f'Не удалось найти мут с номером "{message.text.split()[1]}".')
        return


@bot.message_handler(commands=['feedback', 'fb', 'отзыв', 'фидбэк', 'фидбек', 'фб', 'отзывы'])
@basic_cmd_logger
def feedback_menu (message):
    if len (message.text.split()) == 1:
        bot.reply_to (message=message, text=FEEDBACKS_HELP, reply_markup = feedback_markup(), parse_mode = 'html')

    elif len(message.text.split()) == 2 and message.text.split()[1] in ('view', 'смотреть', 'read', 'читать', 'см'):
        read_feedback (chat_id = message.chat.id, summoned_by_cmd = True, message_id = None, feedback_id = 0)

    elif len(message.text.split()) > 1 and message.text.split()[1] in ('оставить', 'send'):
        bot.send_message (
            message.chat.id, 'Шаг 1/2. Укажите, на КОГО вы пишите отзыв.\n\n' +
            '<b>Если вы найдёте нужный объект отзыва в списке ниже, скопируйте его, нажав на него.</b> Это позволит отнести текущий отзыв к группе отзывов по одной и той же теме, что в будущем может облегчить поиск.\n\n' +
            f'{feedback_contents()}', parse_mode = 'html')
        bot.register_next_step_handler (message, set_new_feedback, message.text.split()[2] == 'anon')

    elif len(message.text.split()) == 2 and message.text.split()[1] == 'set_table':
        create_table_feedback()
        bot.reply_to(message, 'Таблица feedback успешно создана.')

    elif len(message.text.split()) == 2 and message.text.split()[1] == 'contents':
        bot.reply_to(message, f'Все названия:\n\n{feedback_contents()}', parse_mode = 'html')

    else:
        requested_feedback = message.text.replace(f'{message.text.split()[0]}', '').strip()

        if requested_feedback.isdigit():
            bot.reply_to(message, f'Результаты поиска по {requested_feedback}')
            read_feedback (chat_id = message.chat.id, summoned_by_cmd = True, message_id = None, feedback_id = int(requested_feedback))

        else:
            conn = sqlite3.connect('feedback.sql')
            cur = conn.cursor()
            bot.reply_to(message, f'Результаты поиска по {requested_feedback}')

            cur.execute(f'SELECT feedback_id FROM feedback WHERE name = "{requested_feedback}"')
            for feedback_id in cur.fetchall():
                read_feedback (chat_id = message.chat.id, summoned_by_cmd = True, message_id = None, feedback_id = feedback_id[0])

            cur.close()
            conn.close()

def read_feedback (chat_id, summoned_by_cmd: bool, message_id = None, feedback_id = 0, backscroll: bool = False):
    conn = sqlite3.connect('feedback.sql')
    cur = conn.cursor()

    cur.execute ('SELECT feedback_id FROM feedback')
    max_feedback = len(cur.fetchall())

    cur.execute (f'SELECT * FROM feedback WHERE feedback_id = {feedback_id}')
    feedback_contents = cur.fetchall()[0]
    messege_is_deleted = False

    if feedback_contents[9] == 1: # Пропуск удалённых отзывов
        if chat_id != feedback_contents[4] and chat_id not in admin_id: # Показать сообщение автору
            if backscroll: # Если пользователь листает назад
                read_feedback (chat_id = chat_id, summoned_by_cmd = summoned_by_cmd, message_id = message_id, feedback_id = feedback_id - 1, backscroll = True)
            else:
                if max_feedback > feedback_id: # Если следующего сообщения нет, то
                    read_feedback (chat_id = chat_id, summoned_by_cmd = summoned_by_cmd, message_id = message_id, feedback_id = feedback_id + 1)
                else:
                    read_feedback (chat_id = chat_id, summoned_by_cmd = summoned_by_cmd, message_id = message_id, feedback_id = 0)
            return

        else:
            messege_is_deleted = True


    feedback_like = InlineKeyboardButton(text = f'👍 {len(feedback_contents[7].split())}', callback_data=f'feedback like {feedback_id}')
    feedback_dislike = InlineKeyboardButton(text = f'👎 {len(feedback_contents[8].split())}', callback_data=f'feedback dislike {feedback_id}')
    feedback_next = InlineKeyboardButton(text = '▶', callback_data=f'feedback next {feedback_id}')
    feedback_prev = InlineKeyboardButton(text = '◀', callback_data=f'feedback prev {feedback_id}')

    feedback_slider = InlineKeyboardMarkup()

    if chat_id == feedback_contents[4] or chat_id in admin_id:
        feedback_delete = InlineKeyboardButton(text = 'Удалить', callback_data=f'feedback delete {feedback_id}')
        feedback_edit = InlineKeyboardButton(text = 'Редактировать', callback_data=f'feedback edit {feedback_id}')
        feedback_slider.row(feedback_delete, feedback_edit)

    feedback_slider.row(feedback_like, feedback_dislike)
    feedback_slider.row(feedback_prev, feedback_next)

    if summoned_by_cmd:

        deleted_notification = ''
        if messege_is_deleted:
            deleted_notification = '\n\n❌ <i>Отзыв удалён. Нажмите "Удалить" ещё один раз, чтобы восстановить</i>'

        bot.send_message (
            chat_id,
            text = f'Отзыв №{feedback_id} на <b>{feedback_contents[2]}</b>:\n\n' +
            f'<i>{feedback_contents[3]}</i>\n\n' +
            f'Оставил {feedback_contents[5]} {feedback_contents[6]}' +
            f'{deleted_notification}',
            parse_mode = 'html',
            reply_markup = feedback_slider
        )

    else:

        deleted_notification = ''
        if messege_is_deleted:
            deleted_notification = '\n\n❌ <i>Отзыв удалён. Нажмите "Удалить" ещё один раз, чтобы восстановить</i>'

        bot.edit_message_text (
            message_id = message_id,
            chat_id = chat_id,
            text = f'Отзыв №{feedback_id} на <b>{feedback_contents[2]}</b>:\n\n' +
            f'<i>{feedback_contents[3]}</i>\n\n' +
            f'Оставил {feedback_contents[5]} {feedback_contents[6]}' +
            f'{deleted_notification}',
            parse_mode = 'html',
            reply_markup = feedback_slider
        )

def set_new_feedback (message, anon):
    feedback_name = message.text.strip()

    if len (feedback_name) > 48:
        bot.reply_to(message, f'Слишком длинное название. Повторите попытку, указав не более 48-и символов.')
        return

    bot.send_message (message.chat.id, f'Шаг 2/2. Напишите сам отзыв про {feedback_name}.\nУместите его в 3500 символов для корректного отображения.')
    bot.register_next_step_handler (message, setting_the_feedback, feedback_name, anon)

def setting_the_feedback (message, feedback_name, anon):
    author = who_is_requestor(message)[1] if not anon else "Аноним"
    Feedback (name = feedback_name, text = message.text, author = author).set_feedback(message.chat.id)
    bot.reply_to (message, 'Регистрация отзыва успешно завершена.')

def edit_feedback (message, feedback_id):
    Feedback().edit_feedback(feedback_id = feedback_id, column = 'text', new_value = message.text)
    bot.reply_to(message, 'Отзыв обновлён.')


@basic_cmd_logger
def register_hs_markup(message):
    if message.text == 'cancel':
        emoji_reaction(message, '👌')
        return
    
    MAX_NAME_LEN = 22
    if len(message.text) > MAX_NAME_LEN:
        raise HsRegistrationError(f'Слишком длинное название. Необходимо указать не более чем {MAX_NAME_LEN} символа.')
    
    if Hs(message.text).exists:
        raise HsRegistrationError('Организация с таким названием уже существует.')
    
    register_hs(message)
    bot.reply_to(message, f'Вы успешно создали организацию.')


@bot.callback_query_handler(func = lambda call: True)
def button_menu_universal_func(call):
    requestor = UserProfile(call.message.chat.id)
    name: str = requestor.user_name if requestor.exists else call.from_user.full_name
    date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    _log: str = f'{date} | [{call.message.chat.id}] {name}: {call.data}'
    print(_log)
    logger.info(_log)

    cmd: str = call.data.split()

    if 'choose_color_' in call.data:
        new_color = call.data.replace("choose_color_", "")
        markup = color_chooser_markup() if requestor.exists else None

        bot.edit_message_text(requestor.update('color', new_color),
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=markup,
                              parse_mode='html')


    elif "geo" == cmd[0]:
        if cmd[1] == "details":
            lng = cmd[2]
            ltt = cmd[3]
            query = f'Долгота: {lng}\nШирота: {ltt}\n\nЕсли данный отказ вызван ошибкой и на самом деле вы присутствуете, отправьте скриншот этого сообщения разработчику.'
            bot.answer_callback_query(callback_query_id = call.id, show_alert = True, text = query)


    elif 'task' == cmd[0]:
        type_of_operation = cmd[1]
        index_of_task = int (cmd[2])
        filename = cmd[3]

        if len(cmd) > 4:
            filename = ' '.join(word for i, word in enumerate (cmd) if i >= 3)

        conn = sqlite3.connect(f'{filename}.sql')
        cur = conn.cursor()

        cur.execute('SELECT * FROM exam_tasks WHERE is_deleted = "False"')
        tasks = cur.fetchall()

        i = len (tasks)

        if type_of_operation == 'previous':
            try:
                index_of_task -= 1
                if index_of_task < 0:
                    index_of_task = i - 1

                q = tasks[index_of_task]
                answer_authors = q[4] if  len (q[4]) > 15 else ''
                text_to_reply = f'Вопрос <b>{q[1]} / {i}</b>:\n<code>{q[2]}</code>\n\n<i>{q[3]}</i>\n\n{answer_authors}'
            except:
                bot.send_message (call.message.chat.id, 'Не удалось найти вопросы. Возможно, они были удалены.')

        elif type_of_operation == 'next':
            try:
                if index_of_task + 1 >= i:
                    index_of_task = 0
                    q = tasks[index_of_task]
                    answer_authors = q[4] if  len (q[4]) > 15 else ''
                    text_to_reply = f'Вопрос <b>{q[1]} / {i}</b>:\n<code>{q[2]}</code>\n\n<i>{q[3]}</i>\n\n{answer_authors}'

                    #bot.answer_callback_query(callback_query_id = call.id, show_alert = True, text=f'Вопрос {index_of_task + 2} не установлен.')
                    #return

                else:
                    index_of_task += 1
                    q = tasks[index_of_task]
                    answer_authors = q[4] if  len (q[4]) > 15 else ''
                    text_to_reply = f'Вопрос <b>{q[1]} / {i}</b>:\n<code>{q[2]}</code>\n\n<i>{q[3]}</i>\n\n{answer_authors}'
            except:
                bot.send_message (call.message.chat.id, 'Не удалось найти вопросы. Возможно, они были удалены.')

        elif type_of_operation == 'edit':
            temp_msg = bot.send_message (call.message.chat.id, f'Отправьте в чат свою версию решения. Вы будете добавлены в перечень авторов ответа. Постарайтесь ограничиться длиной в <b>3000</b> символов (чтобы сообщение могло корректно отобразиться в Telegram).\n\nВыбранная тема: <code>{tasks[index_of_task][2]}</code>', parse_mode = 'html')
            bot.register_next_step_handler (call.message, examanswer_markup, call.data, requestor, temp_msg, filename, call)

        elif type_of_operation == 'delete':
            for el in tasks:
                if int (el[1]) == int (index_of_task + 1):
                    cur.execute (f'DELETE FROM exam_tasks WHERE task_id = {int (el[1])}')
                    conn.commit ()

            bot.answer_callback_query (callback_query_id = call.id, show_alert = True, text = f'Вопрос удалён.')

        q = tasks[index_of_task]
        answer_authors = q[4] if len (q[4]) > 15 else ''
        text_to_reply = f'Вопрос <b>{q[1]} / {i}</b>:\n<code>{q[2]}</code>\n\n<i>{q[3]}</i>\n\n{answer_authors}'

        cur.close()
        conn.close()

        previous_task = InlineKeyboardButton(text = '⬅️', callback_data = f'task previous {index_of_task} {filename}')
        edit_task = InlineKeyboardButton(text = '✏️', callback_data = f'task edit {index_of_task} {filename}')
        next_task = InlineKeyboardButton(text = '➡️', callback_data = f'task next {index_of_task} {filename}')

        if call.message.chat.id in admin_id:
            delete_task = InlineKeyboardButton(text = '🗑', callback_data = f'task delete {index_of_task} {filename}')

        task_menu = InlineKeyboardMarkup()

        if call.message.chat.id in admin_id:
            task_menu.row (previous_task, edit_task, delete_task, next_task)
        else:
            task_menu.row (previous_task, edit_task, next_task)

        bot.edit_message_text (message_id = call.message.id, chat_id = call.message.chat.id, text = text_to_reply, parse_mode = 'html', reply_markup = task_menu)


    elif 'group' == cmd[0]:
        conn = sqlite3.connect('database.sql')
        cur = conn.cursor()

        cur.execute(f'UPDATE users SET reserve_1 = "{cmd[2]}" WHERE user_id = {call.message.chat.id}')
        conn.commit()

        user_group_to_detect = 'Неизвестная группа'

        for group in groups:
            if group['id'] == int (cmd[2]):
                user_group_to_detect = group['name']

        bot.edit_message_text(message_id = call.message.message_id, chat_id = call.message.chat.id,
                              text = call.message.text.replace('Выберете свою группу из списка.', f' ({user_group_to_detect})  <i>Вы можете изменить введённые настройки командой <b>/profile</b>.</i>'), parse_mode = 'html')

        cur.close()
        conn.close()


    elif 'profile' == cmd[0]:
        if 'change' in cmd[1]:
            if 'Name' == cmd[2]:
                bot.send_message (call.message.chat.id, 'Укажите новое имя. В имени должна быть только 1 раскладка (или латиница или кириллица), не должно быть цифр и любых знаков, кроме нижнего подчёркивания и дефиса.')
                bot.register_next_step_handler (call.message, set_new_profile_name)

            elif 'VK' == cmd[2]:
                bot.send_message (call.message.chat.id, 'Укажите новую ссылку. Формат: <code>https://vk.com/example</code>.', parse_mode='html')
                bot.register_next_step_handler (call.message, set_new_profile_vk)

            elif 'Group' == cmd[2]:
                bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id,
                                        text = f'Выберете свою группу из списка.', reply_markup = select_hs_markup())

            elif 'Color' == cmd[2]:
                bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id,
                                        text = '<b>Выберете цветовую тему:</b>', parse_mode = 'html', reply_markup = color_chooser_markup())


    elif 'feedback' == cmd[0]:
        if cmd[1] == 'send':
            bot.send_message (call.message.chat.id,
                'Шаг 1/2. Укажите, на КОГО вы пишите отзыв.\n\n' +
                '<b>Если вы найдёте нужный объект отзыва в списке ниже, скопируйте его, нажав на него.</b> Это позволит отнести текущий отзыв к группе отзывов по одной и той же теме, что в будущем может облегчить поиск.\n\n' +
                f'{feedback_contents()}', parse_mode = 'html')
            bot.register_next_step_handler (call.message, set_new_feedback)

        elif cmd[1] == 'read':
            read_feedback(chat_id = call.message.chat.id,
                summoned_by_cmd = False, message_id = call.message.id, feedback_id = 0)

        elif cmd[1] in ('like', 'dislike'):
            conn = sqlite3.connect('feedback.sql')
            cur = conn.cursor()

            if cmd[1] == 'like':
                cur.execute(f'SELECT positive_ratings FROM feedback WHERE feedback_id = {cmd[2]}')
                old_value = str (cur.fetchall()[0][0])
                if str(call.message.chat.id) not in old_value:
                    Feedback().edit_feedback(feedback_id = cmd[2],
                        column = 'positive_ratings', new_value = f'{old_value} {str(call.message.chat.id)}')
                else:
                    Feedback().edit_feedback (feedback_id = cmd[2], column = 'positive_ratings',
                        new_value = old_value.replace(f'{str(call.message.chat.id)}', ''))
                    
                read_feedback(chat_id = call.message.chat.id,
                    summoned_by_cmd = False, message_id = call.message.id, feedback_id = cmd[2])

            elif cmd[1] == 'dislike':
                cur.execute(f'SELECT negative_ratings FROM feedback WHERE feedback_id = {cmd[2]}')
                old_value = str (cur.fetchall()[0][0])
                if str(call.message.chat.id) not in old_value:
                    Feedback().edit_feedback(feedback_id = cmd[2],
                        column = 'negative_ratings', new_value = f'{old_value} {str(call.message.chat.id)}')
                else:
                    Feedback().edit_feedback(feedback_id = cmd[2],
                        column = 'negative_ratings', new_value = old_value.replace(f'{str(call.message.chat.id)}', ''))
                    
                read_feedback (chat_id = call.message.chat.id,
                    summoned_by_cmd = False, message_id = call.message.id, feedback_id = cmd[2])

            cur.close()
            conn.close()

        elif cmd[1] in ('next', 'prev'):
            conn = sqlite3.connect('feedback.sql')
            cur = conn.cursor()

            if cmd[1] == 'next':
                try:
                    read_feedback(chat_id = call.message.chat.id,
                        summoned_by_cmd = False, message_id = call.message.id, feedback_id = int (cmd[2]) + 1)

                except IndexError:
                    read_feedback(chat_id = call.message.chat.id,
                        summoned_by_cmd = False, message_id = call.message.id, feedback_id = 0)

            elif cmd[1] == 'prev':
                if int (cmd[2]) > 0:
                    read_feedback (chat_id = call.message.chat.id,
                        summoned_by_cmd = False, message_id = call.message.id,
                        feedback_id = int (cmd[2]) - 1, backscroll = True)

                else:
                    bot.answer_callback_query(callback_query_id = call.id, show_alert = True, text=f'Вы на самом первом отзыве.')

            cur.close()
            conn.close()

        elif call.data.split () [1] in ('delete', 'edit'):
            conn = sqlite3.connect ('feedback.sql')
            cur = conn.cursor ()

            if call.data.split () [1] == 'delete':
                if int(cmd[2]) == 0:
                    bot.answer_callback_query (callback_query_id = call.id, show_alert = True, text = f'Это сообщение нельзя удалить.')
                    cur.close ()
                    conn.close ()
                    return

                cur.execute(f'SELECT is_deleted FROM feedback WHERE feedback_id = {cmd[2]}')
                feedback = cur.fetchall()[0]
                if feedback[0] == 0:
                    cur.execute(f'UPDATE feedback SET is_deleted = 1 WHERE feedback_id = {cmd[2]}')
                    conn.commit()
                    bot.answer_callback_query(callback_query_id = call.id, show_alert = True, text=f'Сообщение №{cmd[2]} успешно удалено.')
                elif feedback[0] == 1:
                    cur.execute(f'UPDATE feedback SET is_deleted = 0 WHERE feedback_id = {cmd[2]}')
                    conn.commit()
                    bot.answer_callback_query(callback_query_id = call.id, show_alert = True, text=f'Сообщение №{cmd[2]} успешно восстановлено.')


            elif cmd[1] == 'edit':
                bot.send_message (call.message.chat.id, 'Укажите новый текст отзыва.')
                bot.register_next_step_handler (call.message, edit_feedback, cmd[2])

            cur.close()
            conn.close()

        elif cmd[1] == 'guide':
            bot.edit_message_text (
                message_id = call.message.message_id,
                chat_id = call.message.chat.id,
                text = 'Аргументы команды /feedback (/fb):\n\n' +
                '1. Нет аргументов - выдать меню, через которое пользователь может перейти к чтению или отправке.\n' +
                '2.1. send - отправка отзыва\n' +
                '2.2. send anon - отправка анонимного отзыва (Имя не отобразится при чтении)\n' +
                '3.1. read - читать отзывы\n'
                '3.2. Номер - открыть отзывы на определённом номере\nпример 1: <code>/feedback 13</code> - выдаст отзыв №13\n' +
                '3.3. Тема - отправить все отзывы по определённой теме\nпример 2: <code>/feedback Иванец Г.И.</code> - выдаст все отзывы на Иванец Г.И.)\n' +
                '4. contents - просмотр всех имеющихся тем\n\n' +
                'Все эти аргументы пишутся после самой команды:\n/feedback Аргумент.\nПример: <code>/feedback send anon</code>\n\n',
                parse_mode = 'html')

        else:
            bot.answer_callback_query(callback_query_id = call.id, show_alert = True, text=f'Произошла ошибка. Инструкции для запроса {call.data} не существует.')


    elif 'hs' == cmd[0]:
        if cmd[1] == 'add':
            _organisation = Hs(call.message.chat.id)

            if _organisation.exists:
                _org_name: str = _organisation.name
                bot.send_message(call.message.chat.id, f'Вы уже создали свою организацию: <code>{_org_name}</code>.', parse_mode='html')
                return
            
            create_table('hs')
            bot.send_message(call.message.chat.id, 'Сейчас Вы создаёте новую организацию. Укажите её название и в дальнейшем Вы сможете изменить другие параметры организации.\n\nВы не можете создать больше одной организации. Если вы хотите отменить её создание,  отправьте в чат "<code>cancel</code>".', parse_mode='html')
            bot.register_next_step_handler(call.message, register_hs_markup)
        
        elif cmd[1] == 'options':
            bot.send_message(call.message.chat.id, 'В разработке...')

        elif cmd[1] == 'page':
            bot.send_message(call.message.chat.id, 'В разработке...')

        elif cmd[1] == 'counter':
            bot.send_message(call.message.chat.id, 'В разработке...')

        elif cmd[1] == 'view':
            hs_name = ' '.join(cmd[2:])
            bot.edit_message_text(
                text=f'Выберете группу в организации "<code>{hs_name}</code>", либо создайте её.',
                chat_id=call.message.chat.id, message_id=call.message.id,
                parse_mode='html', reply_markup=select_group_markup())
            
    elif 'groups' == cmd[0]:
        if cmd[1] == 'back':
            bot.edit_message_text(
                text=f'Выберете организацию или создайте её.',
                chat_id=call.message.chat.id, message_id=call.message.id,
                reply_markup=select_hs_markup())
        
        else:
            bot.send_message(call.message.chat.id, 'В разработке...')


# @bot.message_handler(func = lambda message: True)
@bot.message_handler(content_types = ["text", "audio", "document", "photo", "sticker", "video", "video_note", "voice"])
def chat_control (message):

    if message.chat.type == 'private':
        print ('[Не распознано] ' + who_is_requestor(message)[0])

        if message.text[0] == '/':
            bot.reply_to(message, 'Команда не была указана или была указана, но неверно.\nОтправьте <b>/help</b> для просмотра доступных команд.', parse_mode = 'html')


    elif 'group' in message.json['chat']['type']:
        try:
            pun_logs = json.load(open('punishments.json', 'r', encoding='utf-8'))

        except json.JSONDecodeError:
            pun_logs = []

        for el in pun_logs:
            punished_byusername = False
            punished_byid = False

            if message.from_user.username in el['punished_id']:
                punished_byusername = True

            elif message.from_user.first_name == el['punished_id']:
                punished_byusername = True

            elif el['punished_id'].isdigit():
                if int (message.from_user.id) == int (el['punished_id']):
                    punished_byid = True

            if punished_byusername or punished_byid:
                if el['ignore_punishment']:
                    print ('[Не распознано] ' + who_is_requestor(message)[0])

                if message.json['date'] < el ['last_date']:
                    print ('[Удалено] ' + who_is_requestor(message)[0])
                    bot.delete_message (chat_id=message.chat.id, message_id=message.message_id)
                    bot.send_message (message.from_user.id, f'''⚠️ Ваше сообщение было удалено.

Содержание сообщения: <code>{message.text}</code>;

Выдал мут: <code>{el['pun_author']}</code>;
Причина мута: <code>{el['reason']}</code>;
Номер мута: <code>{el['punishment_id'] + 1}</code>.

Начало мута: <code>{el['first_date_readable']}</code>
Конец мута: <code>{el['second_date_readable']}</code>''', parse_mode = 'html')
                    return

                break
        else:
            if message.chat.id not in (0, 1):
                print ('[Не распознано] ' + who_is_requestor(message)[0])


bot.infinity_polling()
