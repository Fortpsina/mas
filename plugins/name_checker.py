'''Модуль проверяет содержание введённого имени, удаляя все лишние знаки,
чтобы защитить код от SQL-инъекций, а также прочих излишеств.\n
Функция модуля - name_helper.'''

from sqlite3 import connect

MAX_NAME_LENGHT: int = 24

CYRILLIC_SCRIPT: tuple = ("а", "б", "в",
    "г", "д", "е", "ё", "ж", "з", "и", "й", "к", "л",
    "м", "н", "о", "п", "р", "с", "т", "у", "ф", "х",
    "ц", "ч", "ш", "щ", "ъ", "ы", "ь", "э", "ю", "я")

LATINIC_SCRIPT: tuple = ('a', 'b', 'c', 'd', 'e', 'f',
    'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
    'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z')

ADDITIONAL_SYMBOLS: tuple = ('-', '_')


def name_helper (name: str,
                 allow_same_names: bool = False,
                 file_name: str = 'database',
                 table_name: str = 'users') -> dict:

    '''Принимает слово и удаляет все символы, которых нет в латинице и кириллице,
    а также все цифры и знаки, кроме "-" и "_".\n
    Сокращает имя до того количества символов, которое записано в MAX_NAME_LENGHT.\n
    Выдаёт словарь со следующими ключами:\n
    1) name: str = итоговое имя;\n
    2) reply: str = ответ для пользователя;\n
    3) correct: bool = обработан ли ник.'''
    
    if len (name) > 100:
        return {'name': None,
                'reply': f'Имя должно быть короче {MAX_NAME_LENGHT + 1} символов.',
                'correct': False}

    name_letters = []
    name_type = None
    issues = ''

    for letter in name:
        if letter.lower() in CYRILLIC_SCRIPT:
            if len (name_letters) == 0:
                name_type = 'cyrillic'
                name_letters.append (letter)

            elif name_type == 'cyrillic':
                name_letters.append (letter)

            elif 'все символы кириллицы' not in issues:
                issues += '\n\nИз имени удалены все символы кириллицы в целях унификации.'

        elif letter.lower() in LATINIC_SCRIPT:
            if len (name_letters) == 0:
                name_type = 'latinic'
                name_letters.append (letter)
            
            elif name_type == 'latinic':
                name_letters.append (letter)

            elif 'все символы латинского алфавита' not in issues:
                issues += '\n\nИз имени удалены все символы латинского алфавита в целях унификации.'

        elif letter in ADDITIONAL_SYMBOLS:
            name_letters.append (letter)

        elif 'нет в латинице и кириллице' not in issues:
            issues += '\n\nИз имени были удалены символы, которых '
            issues += 'нет в латинице и кириллице, включая цифры '
            issues += 'и все знаки, кроме "-" и "_".'

    result = ''.join (letter for letter in name_letters [0 : MAX_NAME_LENGHT + 1])

    if not allow_same_names:
        conn = connect (file_name + '.sql')
        cur = conn.cursor ()

        cur.execute (f'SELECT name FROM {table_name} WHERE name = "{result}"')
        username_list = cur.fetchall ()

        cur.close ()
        conn.close ()

        if len (username_list) != 0:
            return {'name': result,
                    'reply': f'Имя <code>{result}</code> уже занято.',
                    'correct': False}


    return {'name': result,
            'reply': f'Ваше имя: <code>{result}</code>.{issues}',
            'correct': True}


if __name__ == "__main__":
    pass