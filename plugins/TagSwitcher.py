'''Модуль содержит функцию tags_swither, которая нужна для автоматической
обработки названия предмета, экзамен по которому загружается в бота.\n

Функция должна словарь со следующими ключами:\n
1) tags - тэги (любые слова, по которым бот определит название)
стоить быть внимательнее: если тэг совпадёт у нескольких предметов,
бот будет читать всегда исключительно первый по дате внесения.\n
2) name - непосредственное название предмета.\n
3) file - название для файла (без изменений, бот сам добавляет
.sql к названию уже после работы модуля).\n
4) name_dp - название в дательном падеже, которое было
актуально во время ручной обработки тэгов, но так как
в данный момент вся работа делается автоматически,
дательным падежом бот просто принебрегает ради экономии сил админа.\n
-----------------------------------------
Дополнительный контент - это 2 константы: словари:
1) WRONG_LAYOUT - нужна для замены раскладки (Привет <-> Ghbdtn);\n
2) TRANSLIT_LAYOUT - нужна для транслитерации (Привет <-> Privet).'''

WRONG_LAYOUT = {'q': 'й', 'w': 'ц', 'e': 'у', 'r': 'к', 't': 'е',
                'y': 'н', 'u': 'г', 'i': 'ш', 'o': 'щ', 'p': 'з',
                '[': 'х', ']': 'ъ', 'a': 'ф', 's': 'ы', 'd': 'в',
                'f': 'а', 'g': 'п', 'h': 'р', 'j': 'о', 'k': 'л',
                'l': 'д', ';': 'ж', "'": 'э', 'z': 'я', 'x': 'ч',
                'c': 'с', 'v': 'м', 'b': 'и', 'n': 'т', 'm': 'ь',
                ',': 'б', '.': 'ю', ' ': ' '}

TRANSLIT_LAYOUT = {"а": "a", "б": "b", "в": "v", "г": "g", "д": "d",
                   "е": "e", "ё": "yo", "ж": "zh", "з": "z", "и": "i",
                   "й": "y", "к": "k", "л": "l", "м": "m", "н": "n",
                   "о": "o", "п": "p", "р": "r", "с": "s", "т": "t",
                   "у": "u", "ф": "f", "х": "kh", "ц": "ts", "ч": "ch",
                   "ш": "sh", "щ": "shch", "ъ": "", "ы": "y", "ь": "",
                   "э": "e", "ю": "yu", "я": "ya", " ": " "}

CONSONANT = ("б", "в", "г", "д", "ж", "ж", "й", "к", "л", "м",
             "н", "п", "р", "с", "т", "ф", "х", "ц", "ш", "щ")

def datelniy_padezsh(name: str) -> str:
    words = name.split()
    result = []

    for word in words:
        wl = word.lower ()

        if wl.endswith ("ое"):
            result.append (word[:-2] + "ому")

        elif wl.endswith ("ая"):
            result.append (word[:-2] + "ой")

        elif wl.endswith ("ия"):
            result.append (word[:-1] + "и")

        elif word [-1] in CONSONANT:
            result.append (word + "у")

        elif wl.endswith ("а") or wl.endswith ("шь"):
            result.append (word[:-1] + "е")

        elif wl.endswith ("о"):
            result.append (word[:-1] + "у")

        else:
            result.append (word)

    return ' '.join (result)

def tags_swither (name: str) -> dict:
    wrong_layout_name = ''
    translit_layout_name = ''

    for letter in name:
        for e in WRONG_LAYOUT.items ():
            if letter.lower () == e [0]:
                wrong_layout_name += e [1].lower ()
            elif letter.lower () == e [1]:
                wrong_layout_name += e [0].lower ()

        for e in TRANSLIT_LAYOUT.items ():
            if letter.lower () == e [0]:
                translit_layout_name += e [1].lower ()
            elif letter.lower () == e [1]:
                translit_layout_name += e [0].lower ()

    tags = [name.lower (), wrong_layout_name, translit_layout_name]

    if len (name.split ()) > 1:

        for element in (name, wrong_layout_name, translit_layout_name):

            tags.append (element.split () [0].lower ())
            tags.append (element.replace (' ', '').lower ())

            temp_name_letter_split = ''
            for el in element.split ():
                temp_name_letter_split += el [0]
            tags.append (temp_name_letter_split.lower ())

    capital_letters = ''
    for letter in name:
        if letter.isupper ():
            capital_letters += letter

    if len (capital_letters) > 1:
        tags.append (capital_letters.lower ())

    return {'tags': tags,
            'name': name,
            'file': name,
            'name_dp': datelniy_padezsh (name)}

if __name__ == "__main__":
    print (datelniy_padezsh ("гражданское право"))