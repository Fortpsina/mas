'''Модуль DayOfWeek выдаёт по одноимённой функции день недели
(картеж c названием и индексом) при указании даты.\n
Функция call_DayOfWeek_with_string возвращает то же самое,
но принимает не отдельные день, месяц, год, но строку в формате DD.MM.YYYY.\n
Нули в начале числе удаляются автоматически.'''

from datetime import datetime, timedelta

UTC_OFFSET = timedelta (hours = 3)

def DayOfWeek (year: int = 1, month: int = 1, day: int = 1):
    '''Определяет день недели, опираясь на алгоритм Зеллера'''

    if str(month)[0] == '0':
        month = int (str (month)[1])
    if str(day)[0] == '0':
        day = int (str (day)[1])
        
    if month < 3:
        month += 12
        year -= 1

    k = year % 100
    j = year // 100
    f = day + (13 * (month + 1)) // 5 + k + (k // 4) + (j // 4) - (2 * j)
    
    return (
        ('Суббота',     0),
        ('Воскресенье', 1),
        ('Понедельник', 2),
        ('Вторник',     3),
        ('Среда',       4),
        ('Четверг',     5),
        ('Пятница',     6)
    ) [f % 7]


def call_DayOfWeek_with_string (date: str):
    '''Вызывает функцию DayOfWeek с единым аргументом.'''

    return DayOfWeek (
        year = int (date.replace('.', ' ').split()[2]),
        month = int (date.replace('.', ' ').split()[1]),
        day = int (date.replace('.', ' ').split()[0])
    )


def adjust_date (date_str: str, days: int):
    '''Определяет дату через n дней,
    преобразовывая входную данную в объект времени
    и прибавляя или вычитая данные'''

    date = datetime.strptime(date_str, "%d.%m.%Y")
    new_date = date + timedelta(days=days)
    
    return new_date.strftime("%d.%m.%Y")

def replace_dots_helper (date: str) -> str:
    date = date.replace ('.', ' ')
    date = date.replace (',', ' ')
    date = date.replace ('-', ' ')
    date = date.replace ('_', ' ')
    date = date.replace ('/', ' ')
    date = date.replace (':', ' ')
    date = date.replace ('|', ' ')
    return date


def is_date (date: str):
    date = replace_dots_helper (date)

    if len (date.split ()) == 3:
        for el in date.split():
            if not el.isdigit () or el > 2300 or el < 1:
                return False
            
        if date.split() [0] not in range (1, 32):
            return False
        
        elif date.split() [1] not in range (1, 13):
            return date.split() [0] in range (1, 13)

        return True

    elif len (date.split ()) == 2:
        for el in date.split():
            if not el.isdigit () or el > 31 or el < 1:
                return False
            
        if date.split() [0] not in range (1, 32):
            return False
        
        elif date.split() [1] not in range (1, 13):
            return date.split() [0] in range (1, 13)


        return True

    elif len (date.split ()) == 1:
        if not date.isdigit() or date not in range (1, 32):
            return False
        
        return True

    return False

def dateDDMMYYYY (add_offset: bool = False) -> datetime:
    return datetime.now ().strftime ('%d.%m.20%y') + UTC_OFFSET if add_offset else None

def timeHHMMSS (add_offset: bool = False) -> datetime:
    return datetime.now ().strftime ('%H:%M:%S') + UTC_OFFSET if add_offset else None


if __name__ == '__main__':
    while True:
        date = str (input ('the date must correspond to the following form: DD MM YYYY\n')).split()
        print (DayOfWeek (day = int (date[0]), month = int (date[1]), year = int (date[2])))

