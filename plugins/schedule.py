'''Модуль предназначен для работы с расписанием и всеми атрибутами расписания.\n
Главный класс модуля - Schedule, собирает основные методы, включая статические.\n
Прочие функции:\n
1) collect_schedule_week_selection_helper\n
2) fill_week_conditional_helper\n
3) return_schedule_select_romb_helper\n
4) attend_reader_helper\n
5) homework_selection_helper\n
------------------------------------------------------------------------
Предназначение: чтение, запись, рендер расписания, отметка посещений, 
разметка раписаний без ограничений по объёму данных.\n
Планируется добавить интеграцию библиотеки и планов (тем докладов).'''

from sqlite3 import connect
from plugins.DayOfWeek import *
from plugins.command_logger import select_group_by_id
from plugins.clr import clr
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, time, timedelta

LESSON_1_START = time (0, 0)   # 00:00
LESSON_1_END   = time (10, 9)  # 10:09

LESSON_2_START = time (10, 10) # 10:10
LESSON_2_END   = time (11, 49) # 11:49

LESSON_3_START = time (11, 50) # 11:50
LESSON_3_END   = time (13, 59) # 13:59

LESSON_4_START = time (14, 0)  # 14:00
LESSON_4_END   = time (15, 39) # 15:39

LESSON_5_START = time (15, 40) # 15:40
LESSON_5_END   = time (17, 19) # 17:19

LESSON_6_START = time (17, 20) # 17:20
LESSON_6_END   = time (18, 54) # 18:54

LESSON_7_START = time (18, 55) # 18:55
LESSON_7_END   = time (20, 29) # 20:29

LESSON_8_START = time (20, 30) # 20:30
LESSON_8_END   = time (23, 59) # 23:59

TIMINGS = {1: ('8:30', '10:00'), 2: ('10:10', '11:40'), 3: ('11:50', '13:20'),  # дневные (1-3) до большой перемены
           3.5: ('13:20', '14:00'),                                             # большая перемена
           4: ('14:00', '15:30'), 5: ('15:40', '17:10'), 6: ('17:20', '18:50'), # дневные (4-6) после большой перемены
           7: ('18:55', '20:25'), 8: ('20:30', '22:00')}                        # вечерние (7-8)

class Schedule:
    '''Хранит данные о расписании в self.data. Пример: Schedule (12345, '11.11.2011', 1).data -> ( (?, ?), (?, ?) )\n
    То же самое, но вместо картежей используются словари с фиксированными ключами: self.dicts_data\n
    Определяет раписание по группе / преподавателю / названию / расположению / дате / номеру пары\n
    Обязательный аргумент - номер группы (цифрами)\n
    ------------------------------------------------------------------------
    Методы:\n
    1) create_schedule - статический войд, создающий таблицу schedule, если таковой нет по директории бота.
    2) setup - создание пары (статический стринг). В аргументы метода указать все данные, которые известны\n
    3) update - изменение значений о паре (выделение пары в аргументах класса, а новые значения в аргументах метода)\n
    4) render - преобразование расписания в картинку. сколько
    пар удастся выделить по аргументам класса, столько пар будет зарендерено.
    Обязательный аргумент - группа и дата. В аргументы метода указать цвет. Если цвет не будет указан, будет выбран стандартный.
    5) delete - удаление пары. критерии для выделения указать в аргументах класса.
    необязательный аргумент метода (operation = 'hide') позволяет не удалить пару, а скрыть.\n
    6) fill_week - статический стринг, принимает в виде первого
    аргумента Ctrl+A + Ctrl+C из rasp.rea, во втором - id группы
    и самостоятельно пишет расписание на всю неделю.\n
    7) collect_schedule - статический список, выдаёт словари
    с расписанием из self.dicts_data для всей недели, имея всего одну дату из недели.\n
    8) attendance - чтение посещаемости. Schedule (123, '11.11.2021', 3)
    .attendance() -> Посещаемость: Вася, Миша, Катя, Саша...\n
    9) attend - Запись посещения (ищет пару, которую нужно посетить)
    и добавляет посещение. Пример: Schedule (123, '11.11.2025', 1).attend ('Andrew')\n
    ------------------------------------------------------------------------
    Ключи к словарю dicts_data:\n
                   0 -> 'Null'              -> id SQL             -> (None)
                   1 -> 'group_id'          -> ID группы          -> (12345)
                   2 -> 'group_name'        -> группа             -> ("Ю05/22б")
                   3 -> 'teacher'           -> преподаватель      -> ("Кошкин А.А.")
                   4 -> 'day_of_week'       -> день недели        -> ("Понедельник")
                   5 -> 'lesson_position'   -> номер занятия      -> (1) // служит ключём для значений в timings
                   6 -> 'lesson_name'       -> название пары      -> ("ОБЖ")
                   7 -> 'lesson_place'      -> расположение пары  -> ("3 корпус - 502")
                   8 -> 'lesson_homework'   -> д/з для пары       -> ("решение файла...")
                   9 -> 'lesson_tasks'      -> темы для пары      -> ("...")
                  10 -> 'lesson_type'       -> вид занятия        -> ("Лекция")
                  11 -> 'lesson_date'       -> число, месяц, год  -> ("11.11.2011")
                  12 -> 'attendance'        -> посещения          -> ("Посещения Ю05/22б: Ыыы, Ййй, Ммм"
    ------------------------------------------------------------------------
    data и dicts_data всегда выдают массив, поэтому элементы нужно перебрать через for\n
    или (если мы выделяем только 1 пару) можно сослаться на индекс 0'''

    def __init__ (self,
                  lesson_date: str = datetime.now().strftime('%d.%m.20%y'),
                  lesson_position: int = None,
                  teacher: str = None,
                  lesson_name: str = None,
                  lesson_place: str = None,
                  group_id: int = 0):
        '''Поиск расписания по введённым в класс параметрам.'''

        self.lesson_position = lesson_position
        self.teacher = teacher
        self.lesson_name = lesson_name
        self.lesson_place = lesson_place
        self.group_id = group_id
        self.group_name = select_group_by_id (group_id)

        if lesson_date == 'now':
            lesson_date = datetime.now().strftime('%d.%m.20%y')

        lesson_date = lesson_date.replace('.', ' ').replace(',', ' ').replace('-', ' ').replace('/', ' ')
        
        day = lesson_date.split()[0]
        month = lesson_date.split()[1]
        year = lesson_date.split()[2]

        if day[0] == '0':
            day = day[1]
        if month[0] == '0':
            month = month[1]

        lesson_date = '.'.join((day, month, year))
        self.lesson_date = lesson_date

        find_by_teacher = ''
        find_by_name = ''
        find_by_place = ''
        find_by_date = ''
        find_by_position = ''

        connection = connect('schedule.sql')
        cursor = connection.cursor()

        params = [group_id]

        if teacher is not None:
            find_by_teacher = ' AND teacher = ?'
            params.append (teacher)

        if lesson_name is not None:
            find_by_name = ' AND lesson_name = ?'
            params.append(lesson_name)

        if lesson_place is not None:
            find_by_place = ' AND lesson_place = ?'
            params.append(lesson_place)

        if lesson_date is not None:
            find_by_date = ' AND lesson_date = ?'
            params.append(lesson_date)

        if lesson_date is not None and lesson_position is not None:
            find_by_position = ' AND lesson_position = ?'
            params.append(lesson_position)
        

        cursor.execute ('SELECT * FROM schedule WHERE group_id = ?' + 
                        find_by_teacher + find_by_name + 
                        find_by_place + find_by_date + 
                        find_by_position, params)
        
        self.data = cursor.fetchall ()
        self.dicts_data = []

        for i in range (0, len (self.data)):
            self.dicts_data.append ({'Null':            self.data [i] [0],
                                     'group_id':        self.data [i] [1],
                                     'group_name':      self.data [i] [2],
                                     'teacher':         self.data [i] [3],
                                     'day_of_week':     self.data [i] [4],
                                     'lesson_position': self.data [i] [5],
                                     'lesson_name':     self.data [i] [6],
                                     'lesson_place':    self.data [i] [7],
                                     'lesson_homework': self.data [i] [8],
                                     'lesson_tasks':    self.data [i] [9],
                                     'lesson_type':     self.data [i] [10],
                                     'lesson_date':     self.data [i] [11],
                                     'attendance':      self.data [i] [12]})

        cursor.close ()
        connection.close ()

    @staticmethod
    def create_schedule (name: str = 'schedule'):
        '''Проверяет наличие таблицы schedule и создаёт её при условии отсутствия.\n
        Применять когда есть шанс, что таблицы нет - позволяет избежать ошибку.'''

        conn = connect(f'{name}.sql')
        cur = conn.cursor()

        cur.execute(
            'CREATE TABLE IF NOT EXISTS schedule' +
            '(id int auto_increment primary key, ' +
            'group_id INTEGER, ' +
            'group_name varshar(50), ' +
            'teacher varshar(50), ' +
            'day_of_week varshar(20), ' +
            'lesson_position INTEGER, ' +
            'lesson_name varshar(150), ' +
            'lesson_place varshar(150), ' +
            'lesson_homework varshar(500), ' +
            'lesson_tasks varshar(4000), ' +
            'lesson_type varshar(50), ' +
            'lesson_date varshar(50), ' +
            'attendance varshar(4000)'
            ')'
        )
        conn.commit()
        
        cur.close()
        conn.close()

    @staticmethod
    def setup (lesson_date: str,
               group_id: int = 0,
               teacher: str = '?',
               lesson_position: int = 8,
               lesson_name: str = 'Название не указано',
               lesson_place: str = '? корпус, ?',
               lesson_homework: str = '?',
               lesson_tasks: str = '?',
               lesson_type: str = '?',
               ignore_limits: bool = False):
        '''Вставка новой пары.'''

        lesson_date = lesson_date.replace('.', ' ').replace(',', ' ').replace('-', ' ').replace('/', ' ')
        if len (lesson_date) < 3:
            return 'Дата не содержит одного или более необходимых для записи элементов.'

        day = lesson_date.split()[0]
        month = lesson_date.split()[1]
        year = lesson_date.split()[2]

        if day[0] == '0':
            day = day[1]
        if month[0] == '0':
            month = month[1]

        lesson_date = '.'.join((day, month, year))

        if int (month) > 12 and int (day) <= 12:
            lesson_date = '.'.join((month, day, year))
        elif int (month) > 12 and int (day) > 12:
            return 'Формат даты не удалось исправить автоматически.'

        day_of_week = DayOfWeek (
            year = int (lesson_date.replace('.', ' ').split()[2]),
            month = int (lesson_date.replace('.', ' ').split()[1]),
            day = int (lesson_date.replace('.', ' ').split()[0])
        ) [0]

        group_name = select_group_by_id (group_id)
        if group_id == 0:
            group_name = '?'

        if not ignore_limits:
            if not 'int' in str (group_id.__class__):
                return 'ID группы может быть только целочисленным рациональным числом.'
            if not 'str' in str (group_name.__class__) or len (group_name) > 50:
                return 'Название группы может быть только строкой короче 51-го символа.'
            if not 'str' in str (teacher.__class__) or len (teacher) > 50:
                return 'Преподаватель может быть только строкой короче 51-го символа.'
            if not 'int' in str (lesson_position.__class__) or not lesson_position in range (1, 9):
                return 'Номер пары может быть только числом от 1 до 8'
            if not 'str' in str (lesson_name.__class__) or len (lesson_name) > 150:
                return 'Название пары может быть только строкой короче 151-го символа.'
            if not 'str' in str (lesson_place.__class__) or len (lesson_place) > 150:
                return 'Расположение пары может быть только строкой короче 151-го символа.'
            if not 'str' in str (lesson_homework.__class__) or len (lesson_homework) > 500:
                return 'Д/З может быть только строкой короче 501-го символа.'
            if not 'str' in str (lesson_tasks.__class__) or len (lesson_tasks) > 500:
                return 'Список тем может быть только строкой короче 4001-го символа.'
            if not 'str' in str (lesson_type.__class__) or len (lesson_tasks) > 500:
                return 'Тип занятия может быть только строкой короче 51-го символа.'
            if not 'str' in str (lesson_date.__class__) or len (lesson_tasks) > 50:
                return 'Дата должна быть строкой, записанной по одной из следующих форм: ДД.ММ.ГГГГ / Д.ММ.ГГГГ / ДД.М.ГГГГ / Д.М.ГГГГ.'


        conn = connect(f'schedule.sql')
        cur = conn.cursor()

        cur.execute (f'SELECT lesson_name FROM schedule WHERE lesson_date = ? AND group_id = ? AND lesson_position = ?', (lesson_date, group_id, lesson_position))
        conflictable_lessons = cur.fetchall()

        if len (conflictable_lessons) > 0: # Сделать интеграцию, если дойдут руки дописать update
            cur.close()
            conn.close()
            return f'Занятие не может быть создано, пока его место занято "{conflictable_lessons[0]}". Попробуйте удалить её или отредактировать.'

        cur.execute (
            'INSERT INTO schedule ' +
            '(group_id, group_name, teacher, day_of_week, lesson_position, lesson_name, lesson_place, lesson_homework, lesson_tasks, lesson_type, lesson_date, attendance) ' +
            ' VALUES (' +
            f'"{group_id}", ' +                       # group_id INTEGER
            f'"{group_name}", ' +                     # group_name varshar(150)
            f'"{teacher}", ' +                        # teacher varshar(50)
            f'"{day_of_week}", ' +                    # day_of_week varshar(20)
            f'"{lesson_position}", ' +                # lesson_position INTEGER // (1 - 8)
            f'"{lesson_name}", ' +                    # lesson_name varshar(50)
            f'"{lesson_place}", ' +                   # lesson_place varshar(150)
            f'"{lesson_homework}", ' +                # lesson_homework varshar(500)
            f'"{lesson_tasks}", ' +                   # lesson_tasks varshar(4000)
            f'"{lesson_type}", ' +                    # lesson_type varshar(50)
            f'"{lesson_date}", ' +                    # lesson_date varshar(50)
            f'"Посещения {group_name}:"' +
            ')'
        )
        conn.commit()

        cur.close()
        conn.close()

        return f'Успешно добавлена {lesson_position} пара ({lesson_type}) на {lesson_date} для группы {group_name}:\n\nНазвание: {lesson_name}\nПреподаватель: {teacher}\nРасположение: {lesson_place}'

    def update (self, ignore_limits: bool = False, **kwargs):
        '''Призывая класс, нужно указать, что нужно отредактировать (сослаться на нужную позицию).\n
        Призывая метод, указываем, что нужно в этом объекте поменять.\n
        Например, Schedule (group_id = 0, lesson_date = 11.11.2011, lesson_position = 3).update (teacher = 'Залупкин H.H.')\n
        ------------------------------------------------------------------------
        Выбираем вариант(ы) для аргументов с ключами:\n

            possible_kwarg_values = {
                'group_id': ('ID Группы', 'int', 1000000000),
                'group_name': ('название группы', 'str', 50),
                'teacher': ('преподаватель', 'str', 50),
                'day_of_week': ('день недели', 'str', 20),
                'lesson_position': ('номер пары', 'int', 8),
                'lesson_name': ('название пары', 'str', 150),
                'lesson_place': ('расположение пары', 'str', 150),
                'lesson_homework': ('д/з', 'str', 500),
                'lesson_tasks': ('темы', 'str', 4000),
                'lesson_type': ('тип пары', 'str', 50),
                'lesson_date': ('дата пары', 'str', 50),
                'attendance': ('посещаемость', 'str', 4000)
            }

        Ключ - один из доступных параметров,\n
        1 элемент массива - расшифровка\n
        2 элемент массива - доступный тип данных\n
        3 элемент массива - длина (для str - количество символов, для int - наибольшее значение)'''

        conn = connect(f'schedule.sql')
        cur = conn.cursor()

        cur.execute (
            'SELECT * FROM schedule WHERE group_id = ? AND lesson_date = ? AND lesson_position = ?',
            (self.group_id, self.lesson_date, self.lesson_position)
        )

        former_values = cur.fetchall()
        if len(former_values) == 0:
            return 'Не найдено занятий по указанным параметрам.'

        possible_kwarg_values = {
            'group_id': ('ID Группы', 'int', 1000000000),
            'group_name': ('название группы', 'str', 50),
            'teacher': ('преподаватель', 'str', 50),
            'day_of_week': ('день недели', 'str', 20),
            'lesson_position': ('номер пары', 'int', 8),
            'lesson_name': ('название пары', 'str', 150),
            'lesson_place': ('расположение пары', 'str', 150),
            'lesson_homework': ('д/з', 'str', 500),
            'lesson_tasks': ('темы', 'str', 4000),
            'lesson_type': ('тип пары', 'str', 50),
            'lesson_date': ('дата пары', 'str', 50),
            'attendance': ('посещаемость', 'str', 4000)
        }

        was_updated = ''
        was_not_updated = ''

        for argument in kwargs:          
            kwargument = kwargs[argument]

            if not ignore_limits:
                if argument not in possible_kwarg_values.keys():
                    was_not_updated += f'{argument} не является допустимым аргументом.\n'
                    continue

                elif possible_kwarg_values [argument] [1] not in str (kwargument.__class__):
                    supposed = possible_kwarg_values [argument] [1]
                    was_not_updated += f'{argument}: указан неверный тип данных. Ожидается: {supposed}.\n'
                    continue

                elif 'str' in str (kwargument.__class__) and len (kwargument) > possible_kwarg_values [argument] [2]:
                    supposed = possible_kwarg_values [argument] [2]
                    was_not_updated += f'{argument}: значение слишком длинное. Допустимое значение: {supposed} и менее.\n'
                    continue

                elif 'int' in str (kwargument.__class__) and kwargument > possible_kwarg_values [argument] [2]:
                    supposed = possible_kwarg_values [argument] [2]
                    was_not_updated += f'{argument}: значение слишком велико. Допустимое значение: {supposed} и менее.\n'
                    continue

            cur.execute (
                f'UPDATE schedule SET {argument} = "{kwargument}" WHERE group_id = ? AND lesson_date = ? AND lesson_position = ?',
                (self.group_id, self.lesson_date, self.lesson_position)
            )
            conn.commit ()


            for former_value in former_values:            
                was_updated += possible_kwarg_values [argument] [0]
                was_updated += f' успешно меняет значение с '
                was_updated += former_value [list (possible_kwarg_values.keys ()).index (argument) + 1]
                was_updated += f'на '
                was_updated += kwargs [argument]
                was_updated += '.\n'

        cur.close()
        conn.close()

        return was_updated + f'\n{was_not_updated}'

    def render (self, color: str = 'default', week_modifier = 0, attender: str = 'Аноним'):
        '''Создаёт картинку расписания на указанную дату.\n
        Параметры класса: указать группу и дату\n
        Параметры метода: указать цвет, модификатор (в днях) 
        и посетителя для окраски квадратиков слева.'''

        IMG_NAMES = {'Понедельник': 'Monday_Image.png',
                     'Вторник': 'Tuesday_Image.png',
                     'Среда': 'Wednesday_Image.png',
                     'Четверг': 'Thursday_Image.png',
                     'Пятница': 'Friday_Image.png',
                     'Суббота': 'Saturday_Image.png',
                     'Воскресенье': 'Sunday_Image.png'}

        cycles_were_passed = 0
        modified_date = adjust_date (self.lesson_date, week_modifier)

        for day in Schedule (group_id = self.group_id, lesson_date = modified_date).collect_schedule (return_arr = True):
            day_of_week = None
            date = None

            days_list = list (collect_schedule_week_selection_helper (
                    date = self.lesson_date, week_modifier = week_modifier
                ).values ())

            if len (day) > 0:
                day_of_week = day [0] ['day_of_week']
                date = day [0] ['lesson_date']

            elif len (day) == 0:
                date = days_list [cycles_were_passed]
                day_of_week = call_DayOfWeek_with_string (date) [0]

            if day_of_week == 'Воскресенье':
                continue

            if color in ('default', 'cyan', 'purple', 'red'):
                img = Image.open (f'background_templates/{color}_{day_of_week}.jpg')
                
            else:
                img = Image.new (mode = 'RGBA', size = (2000, 2000), color = clr (color) ['bg'])

            ImageDraw.Draw (img).text (
                xy = (400, 10),
                text = (day_of_week),
                fill = (clr (color) ['text']),
                font = ImageFont.truetype ('fonts/Seravek-Bold.otf', 100))

            ImageDraw.Draw(img).text(
                xy = (1100, 38),
                text = (date),
                fill = (clr (color) ['ol']),
                font = ImageFont.truetype ('fonts/Seravek-Bold.otf', 70))

            lesson_modifier = 0
            for lesson in day:

                attend_color = clr (color) ['non_attend']
                if attender in lesson ['attendance']:
                    attend_color = clr (color) ['attend']

                ImageDraw.Draw (img).rectangle(
                    xy = (
                        10,                    # Ширина первая точка
                        140 + lesson_modifier, # Высота первая точка
                        300,                   # Ширина вторая
                        400 + lesson_modifier  # Высота вторая
                    ),
                    fill = (attend_color),
                    outline = (clr (color)['ol'])
                )

                ImageDraw.Draw (img).rectangle(
                    xy = (
                        320,
                        140 + lesson_modifier,
                        1990,
                        400 + lesson_modifier
                    ),
                    fill = (clr (color)['frame']),
                    outline = (clr (color)['ol'])
                )

                if len (lesson ['lesson_name']) > 28:
                    lesson ['lesson_name'] = ''.join (el for el in lesson ['lesson_name'] [0:27]) + '...'


                l_pos_1 = TIMINGS [lesson ['lesson_position']] [0]
                l_pos_2 = TIMINGS [lesson ['lesson_position']] [1]

                ImageDraw.Draw (img).text (
                    xy = (50, 175 + lesson_modifier),
                    text = l_pos_1 + '\n' + l_pos_2,
                    fill = (clr (color) ['timings']),
                    font = ImageFont.truetype ('fonts/UNCAGE-Medium.ttf', 80),
                    align = 'right'
                )

                ImageDraw.Draw (img).text (
                    xy = (330, 145 + lesson_modifier),
                    text = lesson ['lesson_name'],
                    fill = (clr (color)['text']),
                    font = ImageFont.truetype ('fonts/Seravek-Bold.otf', 80)
                )

                lesson_homework = lesson ['lesson_homework']
                if lesson_homework == '?':
                    lesson_homework = ''

                if len (lesson_homework) in range (41, 82):
                    lesson_homework = ''.join (el for el in lesson ['lesson_homework'] [0:41]) + '\n'
                    lesson_homework += ''.join (el for el in lesson ['lesson_homework'] [41:82]).strip()
                
                elif len (lesson_homework) in range (82, 123):
                    lesson_homework = ''.join (el for el in lesson ['lesson_homework'] [0:41]) + '\n'
                    lesson_homework += ''.join (el for el in lesson ['lesson_homework'] [41:82]).strip() + '\n'
                    lesson_homework += ''.join (el for el in lesson ['lesson_homework'] [82:123]).strip()

                elif len (lesson_homework) > 122:
                    lesson_homework = ''.join (el for el in lesson ['lesson_homework'] [0:41]) + '\n'
                    lesson_homework += ''.join (el for el in lesson ['lesson_homework'] [41:82]).strip() + '\n'
                    lesson_homework += ''.join (el for el in lesson ['lesson_homework'] [82:123]).strip() + '...'
                
                ImageDraw.Draw (img).text (
                    xy = (330, 240 + lesson_modifier),
                    text = lesson_homework,
                    fill = (clr (color)['ol']),
                    font = ImageFont.truetype ('fonts/ofont.ru_D231.ttf', 60)
                )

                ImageDraw.Draw (img).text (
                    xy = (1900 - len (lesson ['lesson_place'].replace(' ', '')) * 24, 160 + lesson_modifier),
                    text = lesson ['lesson_place'].strip(),
                    fill = (clr (color)['ol']),
                    font = ImageFont.truetype ('fonts/Seravek-Bold.otf', 50),
                    align = 'right'
                )

                lesson_type = '\n'.join(word for word in lesson ['lesson_type'].split())

                ImageDraw.Draw (img).text (
                    xy = (1900 - 20 * max (len (word) for word in lesson_type.splitlines()), 220 + lesson_modifier),
                    text = lesson_type,
                    fill = (clr (color)['ol']),
                    font = ImageFont.truetype ('fonts/LTSuperior-Medium.otf', 50),
                    align = 'right'
                )

                lesson_modifier += 300

            if len (day) == 0:
                ImageDraw.Draw(img).text(xy = (400, 800),
                    text = ('Занятий нет'),
                    fill = (clr (color) ['text']),
                        font = ImageFont.truetype ('fonts/Seravek-Bold.otf', 200))

            #monday_stream = io.BytesIO()
            #Monday_Image.save(monday_stream, format='PNG')
            #monday_stream.seek(0)
            img.save(f'rendered_schedule/{IMG_NAMES [day_of_week]}')
            
            cycles_were_passed += 1

        return {
            'date': date,
            'week_modifier': week_modifier,
            'report': 'Расписание сохранение, ошибки не обнаружено.',
            'reply': f'<b>{self.group_name}</b> | <code>{days_list [0]} - {days_list [5]}</code>\n\n🟩 = Посещение записано\n🟥 = Посещение не записано\n\n 💡 Используйте /attend, чтобы записаться.'
        }

    def delete (self, operation: str = 'delete'):
        conn = connect(f'schedule.sql')
        cur = conn.cursor()

        if len (Schedule(lesson_date = self.lesson_date, lesson_position = self.lesson_position, group_id = self.group_id).data) == 0:
            cur.close()
            conn.close()
            return 'Пара не найдена.'
        
        request_sql = 'DELETE FROM schedule WHERE group_id = ? AND lesson_date = ? AND lesson_position = ?'
        callback = 'удалена физически (безвозвратно)'

        if operation == 'hide':
            request_sql = 'UPDATE schedule SET group_id = 0 WHERE group_id = ? AND lesson_date = ? AND lesson_position = ?'
            callback = 'скрыта (помещена в расписание для группы 0)'

        cur.execute(request_sql, (self.group_id, self.lesson_date, self.lesson_date))
        conn.commit()

        cur.close()
        conn.close()

        return f'Указанная пара ({self.data[0]}) {callback}.'

    @staticmethod
    def fill_week (data: str, group_id: int = 0):
        '''Быстро заполняет расписание на всю неделю.'''

        data += '\nfinal_line'
        report_deleted_lessons = ''
        to_fill_schedule = data.splitlines()
        first_date = '??.??.????'
        last_date = '??.??.????'

        for el in to_fill_schedule:

            if fill_week_conditional_helper (el) ['go']:
                final_line = fill_week_conditional_helper (el) ['next']
                current    = fill_week_conditional_helper (el) ['current']
                index = to_fill_schedule.index(el)

                while final_line not in to_fill_schedule [index]:
                    if 'пара' in to_fill_schedule[index + 1] and 'пара' not in to_fill_schedule[index + 2]:
                        date = el.replace (f'{current}, ', '')
                        lesson_position = int (to_fill_schedule[index + 1].replace (' пара', ''))
                        lesson_name =  to_fill_schedule [index + 4]
                        lesson_place = to_fill_schedule [index + 6].replace (' , пл. Основная', ' ').replace ('+ подгруппы', 'Несколько мест')
                        lesson_type =  to_fill_schedule [index + 5]

                        if first_date == '??.??.????':
                            first_date = date
                        last_date = date

                        if len (Schedule (lesson_date = date, lesson_position = lesson_position, group_id = group_id).data) > 0:
                            Schedule (lesson_date = date, lesson_position = lesson_position, group_id = group_id).delete (operation = 'hide')
                            report_deleted_lessons += f'\n\n{lesson_name} от {date} было перемещено в архив:\n'
                            report_deleted_lessons += f'{lesson_position} пара уже была занята в {current}. За подробной информацией обратитесь на хостинг.'

                        Schedule.setup (
                            lesson_date = date,
                            group_id = group_id,
                            lesson_position = lesson_position,
                            lesson_name = lesson_name,
                            lesson_place = lesson_place,
                            lesson_type = lesson_type,
                        )

                    index += 1

        return f'Расписание успешно обновлено. Заполненная неделя: {first_date}-{last_date}{report_deleted_lessons}'

    def collect_schedule (self,
                          week_modifier: int = 0,
                          return_arr: bool = False,
                          append_empty_days: bool = True) -> dict | list:
        '''Собирает расписание на всю неделю.\n
        В параметры класса указать группу и дату.\n
        В параметры метода - текущую дату и модификатор (он определит, сколько дней вычесть или прибавить к дате)'''

        week_selection = collect_schedule_week_selection_helper (date = self.lesson_date, week_modifier = week_modifier)

        if return_arr:
            output = []

            for day in ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'):
                if append_empty_days or len (Schedule (group_id = self.group_id, lesson_date = week_selection [day]).dicts_data) > 0:
                    output.append (Schedule (group_id = self.group_id, lesson_date = week_selection [day]).dicts_data)

            return output
        
        return {
            'monday':    Schedule (group_id = self.group_id, lesson_date = week_selection ['monday']).dicts_data,
            'tuesday':   Schedule (group_id = self.group_id, lesson_date = week_selection ['tuesday']).dicts_data,
            'wednesday': Schedule (group_id = self.group_id, lesson_date = week_selection ['wednesday']).dicts_data,
            'thursday':  Schedule (group_id = self.group_id, lesson_date = week_selection ['thursday']).dicts_data,
            'friday':    Schedule (group_id = self.group_id, lesson_date = week_selection ['friday']).dicts_data,
            'saturday':  Schedule (group_id = self.group_id, lesson_date = week_selection ['saturday']).dicts_data,
        }

    def checkup_collection (self) -> str:
        '''Проверяет, какие недели были заполнены для определённой группы.\n
        Поиск касается исключительно занятий, проводимых в текущем году,
        чтобы оптимизировать вывод и избежать выдачу слишком больших сообщений.'''

        CurrentYear = str (datetime.now().strftime('20%y'))
        FoundLessons = '<b>Найденные даты расписания:</b>'

        for lesson in self.dicts_data:
            if CurrentYear in lesson ['lesson_date'] and not lesson ['lesson_date'] in FoundLessons:
                FoundLessons += '\n <code>' + lesson ['lesson_date'] + '</code> | ' 
                FoundLessons += len (Schedule (group_id = self.group_id,
                                               lesson_date = lesson ['lesson_date']).data)

        return FoundLessons

    def attendance (self) -> str:
        '''Аргументы класса: группа и дата.'''

        if len (self.data) != 1:
            return f'Выделено {len (self.data)} пар(ы) вместо одной. Укажите более точные параметры фильтрации для корректного ответа.'
        
        l_name = self.dicts_data [0] ['lesson_name']
        l_date = self.dicts_data [0] ['lesson_date']
        l_att = self.dicts_data [0] ['attendance']
        
        return f'<code>{l_name}</code> <i>{l_date}</i>:\n{l_att}'

    def attend (self, attender: str = 'Аноним', operation: str = 'attend', summoned_by_admin: bool = False):
        '''Записывает чьё-либо посещение.\n
        Укажите в перечне аргументов класса ГРУППУ (всегда обязательный аргумент), ДАТУ (или будет бред)\n
        и если не указать НОМЕР ПАРЫ, бот расставит посещения на весь день.\n
        если изменить аргумент operation с attend на любое значение кроме исходного, посещение удаляется.'''

        issues = f'{attender},'
        was_signed_up_already = 'Вы уже записаны'
        was_signed_up = 'Вы успешно записаны'
        was_not_signed_up = 'Вы не были записаны на'
        was_unsigned_up = 'Вы больше не записаны'

        if True:
            issues += '\nотметки на парах через ботавременно отключены.'
            return

        if summoned_by_admin:
            issues = f'Посещения для {attender}:'
            was_signed_up_already = f'{attender} уже был(а) записан(а)'
            was_signed_up = f'{attender} успешно записан(а)'
            was_not_signed_up = f'{attender} не был(а) записан(а)'
            was_unsigned_up = f'{attender} больше не записан(а)'
        
        for lesson in self.dicts_data:
            attendence = list (lesson ['attendance'].splitlines ())
            l_name = lesson ['lesson_name']
            l_date = lesson ['lesson_date']

            if attender in attendence:
                if operation == 'attend':
                    issues += f'\n{was_signed_up_already} на {l_name} {l_date}.'

                else:
                    attendence.remove (attender)
                    issues += f'\n{was_unsigned_up} на {l_name} {l_date}.'

            else:
                if operation == 'attend':
                    attendence.append (f'\n{attender}')
                    issues += f'\n{was_signed_up} на {l_name} {l_date}.'

                else:
                    issues += f'\n{was_not_signed_up} на {l_name} {l_date}.'

            Schedule (
                group_id = lesson ['group_id'],
                lesson_date = lesson ['lesson_date'],
                lesson_position = lesson ['lesson_position']
            ).update (attendance = ''.join (f"👤 {line}" for line in attendence))

        if len (issues.split()) == 1:
            return 'Не найдено ни одной пары по указанным фильтрам.'

        return issues

def collect_schedule_week_selection_helper (date: str, week_modifier: int = 0):
    '''Выделить понедельник, вторник, среду, четверг, пятницу и субботу от недели, которой принадлежит дата.'''

    day_of_week = call_DayOfWeek_with_string (date) [1]

    if day_of_week == 2: # В ПОНЕДЕЛЬНИК
        return {
            'monday':    adjust_date (date_str = date, days = week_modifier + 0),
            'tuesday':   adjust_date (date_str = date, days = week_modifier + 1),
            'wednesday': adjust_date (date_str = date, days = week_modifier + 2),
            'thursday':  adjust_date (date_str = date, days = week_modifier + 3),
            'friday':    adjust_date (date_str = date, days = week_modifier + 4),
            'saturday':  adjust_date (date_str = date, days = week_modifier + 5)
        }

    elif day_of_week == 3: # ВО ВТОРНИК
        return {
            'monday':    adjust_date (date_str = date, days = week_modifier - 1),
            'tuesday':   adjust_date (date_str = date, days = week_modifier + 0),
            'wednesday': adjust_date (date_str = date, days = week_modifier + 1),
            'thursday':  adjust_date (date_str = date, days = week_modifier + 2),
            'friday':    adjust_date (date_str = date, days = week_modifier + 3),
            'saturday':  adjust_date (date_str = date, days = week_modifier + 4)
        }

    elif day_of_week == 4: # В СРЕДУ
        return {
            'monday':    adjust_date (date_str = date, days = week_modifier - 2),
            'tuesday':   adjust_date (date_str = date, days = week_modifier - 1),
            'wednesday': adjust_date (date_str = date, days = week_modifier + 0),
            'thursday':  adjust_date (date_str = date, days = week_modifier + 1),
            'friday':    adjust_date (date_str = date, days = week_modifier + 2),
            'saturday':  adjust_date (date_str = date, days = week_modifier + 3)
        }

    elif day_of_week == 5: # В ЧЕТВЕРГ
        return {
            'monday':    adjust_date (date_str = date, days = week_modifier - 3),
            'tuesday':   adjust_date (date_str = date, days = week_modifier - 2),
            'wednesday': adjust_date (date_str = date, days = week_modifier - 1),
            'thursday':  adjust_date (date_str = date, days = week_modifier + 0),
            'friday':    adjust_date (date_str = date, days = week_modifier + 1),
            'saturday':  adjust_date (date_str = date, days = week_modifier + 2)
        }

    elif day_of_week == 6: # В ПЯТНИЦУ
        return {
            'monday':    adjust_date (date_str = date, days = week_modifier - 4),
            'tuesday':   adjust_date (date_str = date, days = week_modifier - 3),
            'wednesday': adjust_date (date_str = date, days = week_modifier - 2),
            'thursday':  adjust_date (date_str = date, days = week_modifier - 1),
            'friday':    adjust_date (date_str = date, days = week_modifier + 0),
            'saturday':  adjust_date (date_str = date, days = week_modifier + 1)
        }

    elif day_of_week == 0:
        return {
            'monday':    adjust_date (date_str = date, days = week_modifier - 5),
            'tuesday':   adjust_date (date_str = date, days = week_modifier - 4),
            'wednesday': adjust_date (date_str = date, days = week_modifier - 3),
            'thursday':  adjust_date (date_str = date, days = week_modifier - 2),
            'friday':    adjust_date (date_str = date, days = week_modifier - 1),
            'saturday':  adjust_date (date_str = date, days = week_modifier + 0 )
        }

    elif day_of_week == 1:
        return {
            'monday':    adjust_date (date_str = date, days = week_modifier + 1),
            'tuesday':   adjust_date (date_str = date, days = week_modifier + 2),
            'wednesday': adjust_date (date_str = date, days = week_modifier + 3),
            'thursday':  adjust_date (date_str = date, days = week_modifier + 4),
            'friday':    adjust_date (date_str = date, days = week_modifier + 5),
            'saturday':  adjust_date (date_str = date, days = week_modifier + 6)
        }

def fill_week_conditional_helper (string):
    if 'ПОНЕДЕЛЬНИК' in string:
        return {'go': True, 'next': 'ВТОРНИК', 'current': 'ПОНЕДЕЛЬНИК'}

    elif 'ВТОРНИК' in string:
        return {'go': True, 'next': 'СРЕДА', 'current': 'ВТОРНИК'}

    elif 'СРЕДА' in string:
        return {'go': True, 'next': 'ЧЕТВЕРГ', 'current': 'СРЕДА'}

    elif 'ЧЕТВЕРГ' in string:
        return {'go': True, 'next': 'ПЯТНИЦА', 'current': 'ЧЕТВЕРГ'}

    elif 'ПЯТНИЦА' in string:
        return {'go': True, 'next': 'СУББОТА', 'current': 'ПЯТНИЦА'}

    elif 'СУББОТА' in string:
        return {'go': True, 'next': 'final_line', 'current': 'СУББОТА'}

    return {'go': False, 'next': None, 'current': None}

def return_schedule_select_romb_helper (descript: str):
    '''Решает, какой ромб сделать напротив пары, чтобы визуально определять, что будет.'''

    if 'лекция' in descript.lower ():
        return '🔸 '
    elif 'практическое' in descript.lower () or 'ино' in descript.lower ():
        return '🔹 '
    elif 'пересдача' in descript.lower ():
        return '🟥 '
    elif 'зач' in descript.lower ():
        return'🔴 '
    elif 'экзам' in descript.lower ():
        return'🔴 '
    else:
        return '⚪ '

def attend_reader_helper_current (group_id: int, lesson_position: int | float | None = None):
    '''Функция должна давать искать текущую пару.
    Если не найдена текущая пара, дать выбрать из сегодняшних.
    Если сегодня нет пар, дать выбрать из тех, которые были/будут на этой неделе.
    Если на неделе нет пар, уведомить, что нет пар.'''

    current_time_utc3 = datetime.now () + UTC_OFFSET

    if not lesson_position:
        match current_time_utc3.time():
            case t if LESSON_1_START <= t < LESSON_1_END:
                lesson_position = 1
            
            case t if LESSON_2_START <= t < LESSON_2_END:
                lesson_position = 2
            
            case t if LESSON_3_START <= t < LESSON_3_END:
                lesson_position = 3
            
            case t if LESSON_4_START <= t < LESSON_4_END:
                lesson_position = 4
            
            case t if LESSON_5_START <= t < LESSON_5_END:
                lesson_position = 5
            
            case t if LESSON_6_START <= t < LESSON_6_END:
                lesson_position = 6
            
            case t if LESSON_7_START <= t < LESSON_7_END:
                lesson_position = 7
            
            case t if LESSON_8_START <= t < LESSON_8_END:
                lesson_position = 8
            
            case _:
                lesson_position = 3.5

    print (lesson_position)
    print (group_id)
    
    currentSchedule = Schedule (group_id = group_id,
                                lesson_position = lesson_position).attendance ()
    
    if len (currentSchedule) == 0:
        return attend_reader_helper_today (group_id = group_id)

    return {"reply_text": currentSchedule,
            "reply_markup": None}

def attend_reader_helper_today (group_id: int):
    '''Функция ищет все пары за сегодня и предлагает выбрать из найденных,
    чтобы показать пользователю посещения выбранной.
    Если сегодня нет пар, дать выбрать из тех, которые были/будут на этой неделе.
    Если на неделе нет пар, уведомить, что нет пар.'''
    
    currentSchedule = Schedule (group_id = group_id).dicts_data
    
    if len (currentSchedule) == 0:
        return attend_reader_helper_this_week (group_id = group_id)
    
    lesson_viewer_list = [] 
    
    return {"reply_text": "Не нашёл пары, идущей в данный момент.",
            "reply_markup": lesson_viewer_list}

def attend_reader_helper_this_week (group_id: int):
    '''Функция ищет все пары этой недели и даёт пользователю выбрать,
    посещения какой пары проверить.
    Если нет пар за неделю, уведомляет, что нет пар.'''

    days = collect_schedule_week_selection_helper (dateDDMMYYYY (True))
    currentSchedule = []
    
    for day in days.values ():
        currentSchedule.append (Schedule (day, group_id = group_id).dicts_data)

    if len (currentSchedule) == 0:
        return {"reply_text": "Не найдено ни одной пары для вашей группы за ближайшее время.",
                "reply_markup": None}

def attend_writer_helper () -> list:
    '''Определить неделю, затем убрать все дни, которые были до сегодняшнего
    и выбрать из них все пары. Пользователю предложить выбрать, куда записаться.'''

    return

def homework_selection_helper () -> list:
    '''Интерфейс для записи посещений у админа и у обычного пользователя'''

    return

if __name__ == '__main__':
    print (attend_reader_helper_current (1022105))
    #print (Schedule ('24.10.2024', group_id = 1022105, lesson_position = 1).update (
    #    lesson_homework = 'Понял, давайте исправим код, чтобы он корректно добавлял переносы строк и не обрезал текст преждевременно. Вот исправленная версия: цикл для добавления слов в')) 
