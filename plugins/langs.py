"""Данный модуль содержит фразы, используемые в ответах бота на следующих языках:
английский, русский, испанский, немецкий, французский, украинский, польский, японский и корейский."""


# Сообщить, что команда не может быть исполнена
# ввиду несоответствия уровня прав команде.
NOT_ENOUGH_RIGHTS_ERROR = {
    'en': 'You are not allowed to use this command.',
    'ru': 'Вы не можете использовать эту команду.',
    'sp': 'No tiene permitido usar este comando.',
    'de': 'Sie dürfen diesen Befehl nicht verwenden.',
    'fr': 'Vous nêtes pas autorisé à utiliser cette commande.',
    'ua': 'Вам не дозволено використовувати цю команду.',
    'pl': 'Nie masz uprawnień do używania tego polecenia.',
    'jp': 'このコマンドを使用することはできません。',
    'kr': '이 명령을 사용할 수 없습니다.',
}

def not_enough_rights(message) -> str:
    '''"You are not allowed to use this command." in different languages'''
    # при инициализации lang ставится or 'en' на случай,
    # если из сообщения не удастся извлечь язык пользователя
    lang: str = message.from_user.language_code or 'en'
    # при получении содержимого английский используется как 
    # запасной вариант на случай, если в словаре нет указанного языка
    default: str = NOT_ENOUGH_RIGHTS_ERROR['en']
    return NOT_ENOUGH_RIGHTS_ERROR.get(lang, default)



# Сообщить, что значение чего-либо выше установленной
# максимальной длины и подсказать, что делать
TOO_LONG_MESSAGE_ERROR = {
    'en': 'This is <b>too long</b> value: <code>%s</code> symbols. Enter something not longer than <code>%s</code> symbols and it will work.',
    'ru': 'Слишком длинное значение (%s символов). Укажите значение не более %s символов.',
    'sp': 'Este valor es demasiado largo: <code>%s</code> símbolos. Introduzca un valor no mayor a <code>%s</code> símbolos y funcionará.',
    'de': 'Dies ist ein <b>zu langer</b> Wert: <code>%s</code> Zeichen. Geben Sie einen Wert ein, der nicht länger als <code>%s</code> Zeichen ist, dann funktioniert es.',
    'fr': 'Cette valeur est trop longue: <code>%s</code> symboles. Saisissez une valeur ne dépassant pas <code>%s</code> symboles et cela fonctionnera.',
    'ua': 'Це <b>занадто довге</b> значення: <code>%s</code> символів. Введіть значення не довше за <code>%s</code> символів, і воно працюватиме.',
    'pl': 'To jest <b>zbyt długa</b> wartość: <code>%s</code> symboli. Wprowadź coś nie dłuższego niż <code>%s</code> symboli i zadziała.',
    'jp': 'この値は<b>長すぎます: <code>%s</code>文字です。<code>%s</code>文字以内の値を入力すると正常に動作します。',
    'kr': '이 값은 <b>너무 깁니다: <code>%s</code>자. <code>%s</code>자 이하로 입력하면 됩니다.',
}

def too_long_value(message, actual: int, maximum: int) -> str:
    '''"This is <b>too long</b> value: <code>?</code> symbols.
    Enter something not longer than <code>?</code> symbols and it will work." in different languages'''
    lang: str = message.from_user.language_code or 'en'
    default: str = TOO_LONG_MESSAGE_ERROR['en']
    return TOO_LONG_MESSAGE_ERROR.get(lang, default) % (actual, maximum)



# Сообщить, что взаимодействие с личным профилем невозможно,
# поскольку искомого профиля несуществует.
PROFILE_NOT_FOUND_ERROR = {
    'en': 'Can not find this user info. Register using the following command: <b>/register</b>.',
    'ru': 'Информация о пользователе не найдена. Зарегестрируйтесь командой <b>/register</b>.',
    'sp': 'No se encuentra la información de este usuario. Regístrese con el siguiente comando: <b>/register</b>.',
    'de': 'Diese Benutzerinformationen können nicht gefunden werden. Registrieren Sie sich mit dem folgenden Befehl: <b>/register</b>.',
    'fr': 'Impossible de trouver les informations de cet utilisateur. Inscrivez-vous avec la commande suivante: <b>/register</b>.',
    'ua': 'Не вдається знайти інформацію про цього користувача. Зареєструйтесь за допомогою такої команди: <b>/register</b>.',
    'pl': 'Nie można znaleźć informacji o tym użytkowniku. Zarejestruj się za pomocą następującego polecenia: <b>/register</b>.',
    'jp': 'このユーザー情報が見つかりません。次のコマンドを使用して登録してください: <b>/register</b>',
    'kr': '이 사용자 정보를 찾을 수 없습니다. 다음 명령을 사용하여 등록하세요: <b>/register</b>.',
}

PROFILE_NOT_FOUND_ERROR_NOT_OWN = {
    'en': 'Can not find this user.',
    'ru': 'Информация о пользователе не найдена.',
    'sp': 'No se encuentra la información de este usuario.',
    'de': 'Diese Benutzerinformationen können nicht gefunden werden.',
    'fr': 'Impossible de trouver les informations de cet utilisateur.',
    'ua': 'Не вдається знайти інформацію про цього користувача.',
    'pl': 'Nie można znaleźć informacji o tym użytkowniku.',
    'jp': 'このユーザー情報が見つかりません。',
    'kr': '이 사용자 정보를 찾을 수 없습니다.',
}

def profile_not_found(message, own: bool = False) -> str:
    '''"Can not find this user info. Register using the following command: <b>/register</b>." in different languages'''
    reference: dict = PROFILE_NOT_FOUND_ERROR if own else PROFILE_NOT_FOUND_ERROR_NOT_OWN
    lang: str = message.from_user.language_code or 'en'
    default: str = reference['en']
    return reference.get(lang, default)



# Выдать информацию о профиле, если профиль существует.
PROFILE_INFO_TEXT = {
    'en': '''<b>%s</b> profile:\n
    Group: <code>%s</code>
    Hs: <code>%s</code>
    VK: <code>%s</code>
    ID: <code>%s</code>
    Color: <code>%s</code>
    Reg: <code>%s</code>
    Status: <code>%s</code>''',

    'ru': '''Профиль <b>%s</b>:\n
    Группа: <code>%s</code>
    Организация: <code>%s</code>
    ВК: <code>%s</code>
    ID: <code>%s</code>
    Цвет: <code>%s</code>
    Регистрация: <code>%s</code>
    Статус: <code>%s</code>'''
}

RIGHTS_ASSETS = {
    0: {
        'en': 'Banned user',
        'ru': 'Заблокированный пользователь'
    },
    1: {
        'en': 'User',
        'ru': 'Пользователь'
    },
    2: {
        'en': 'Vice Chairman of the group',
        'ru': 'Зам. председателя группы'
    },
    3: {
        'en': 'Chairman of the group',
        'ru': 'Председатель группы'
    },
    4: {
        'en': 'Admin',
        'ru': 'Администратор'
    },
    5: {
        'en': 'Senior admin',
        'ru': 'mas senior admin'
    }
}

def profile_info(message, profile) -> str:
    '''<code>%s</code> profile:\n
    Group: <code>%s</code>\n
    Hs: <code>%s</code>\n
    VK: <code>%s</code>\n
    ID: <code>%s</code>\n
    Color: <code>%s</code>\n
    Reg: <code>%s</code>\n
    Status: <code>%s</code>'''
    
    lang: str = message.from_user.language_code or 'en'
    default: str = PROFILE_INFO_TEXT['en']
    profile_data = (
        profile.user_name,
        profile.user_group,
        profile.hs_name,
        profile.user_vk,
        profile.user_id,
        profile.user_color,
        profile.user_reg,
        RIGHTS_ASSETS[profile.rights][lang]
    )
    return PROFILE_INFO_TEXT.get(lang, default) % profile_data



# Сообщить, что пользователю отказано в регистрации,
# поскольку он уже был зарегестрирован.
PROFILE_ALREADY_EXISTS_ERROR = {
    'en': 'You had been registered in M.A.S. already.',
    'ru': 'Вы уже зарегестрированы в боте.',
    'sp': 'Usted ya estaba registrado en el M.A.S.',
    'de': 'Sie waren bereits im M.A.S. eingeschrieben.',
    'fr': 'Vous étiez déjà inscrit au M.A.S.',
    'ua': 'Ви вже були зареєстровані в M.A.S.',
    'pl': 'Byłeś już zarejestrowany w M.A.S.',
    'jp': 'あなたはすでにM.A.S.に登録されていました。',
    'kr': '당신은 이미 M.A.S.에 등록되어 있었습니다.',
}

def frofile_exists_already(message) -> str:
    lang: str = message.from_user.language_code or 'en'
    default: str = PROFILE_ALREADY_EXISTS_ERROR['en']
    return PROFILE_ALREADY_EXISTS_ERROR.get(lang, default)



# Сообщить, что ник нарушает правила регстрации и
# вместо указанного использован ник, взятый из message
INCORRECT_NAME_WARNING = {
    'en': 'This name can not be accepted due to a serious violation of the form for registering an account. Your Telegram name is set as the name: <b>%s</b>.\n<i>To change your data, use the following command /profile</i>',
    'ru': 'Данный ник не может быть принят ввиду серьёзного нарушения формы регистрации аккаунта. В качестве имени установлен Ваше имя из Telegram: <b>%s</b>.\n<i>Чтобы поменять свои данные, воспользуйтесь /profile</i>',
    'sp': 'Este nombre no se puede aceptar debido a una infracción grave del formulario de registro de cuenta. Tu nombre de Telegram es <b>%s</b>. <i>Para cambiar tus datos, usa el siguiente comando: /profile</i>.',
    'de': 'Dieser Name kann aufgrund eines schwerwiegenden Verstoßes gegen das Formular zur Kontoregistrierung nicht akzeptiert werden. Ihr Telegrammname ist als Name festgelegt: <b>%s</b>.\n<i>Um Ihre Daten zu ändern, verwenden Sie den folgenden Befehl /profile</i>',
    'fr': "Ce nom ne peut être accepté en raison d'une violation grave du formulaire d'inscription. Votre nom Telegram est défini comme: <b>%s</b>.\n<i>Pour modifier vos données, utilisez la commande suivante: /profile</i>",
    'ua': 'Цей нік не може бути прийнятий через серйозне порушення форми реєстрації облікового запису. В якості імені встановлено Ваше імя з Telegram: <b>%s</b>.\n<i>Щоб змінити свої дані, скористайтесь /profile</i>',
    'pl': 'Ta nazwa nie może zostać zaakceptowana z powodu poważnego naruszenia formularza rejestracji konta. Twoja nazwa Telegram jest ustawiona jako nazwa: <b>%s</b>.\n<i>Aby zmienić swoje dane, użyj następującego polecenia /profile</i>',
    'jp': 'この名前はアカウント登録フォームに重大な違反があるため、受け付けられません。Telegram名は<b>%s</b>に設定されています。\n<i>データを変更するには、次のコマンド/profileを使用してください</i>',
    'kr': '계정 등록 양식을 심각하게 위반하여 이 이름을 사용할 수 없습니다. Telegram 이름이 <b>%s</b>(으)로 설정되어 있습니다.\n<i>데이터를 변경하려면 다음 명령어를 사용하세요. /profile</i>',
}

def incorrect_name(message) -> str:
    lang: str = message.from_user.language_code or 'en'
    default: str = INCORRECT_NAME_WARNING['en']
    return INCORRECT_NAME_WARNING.get(lang, default) % message.from_user.full_name



# Рассказать о существующих командах или предложить справку.
HELP_TEXT_GENERAL = {
    'ru': '''Основные функции:\n
<b>/schedule</b> - вывод расписания пар;
<b>/exam</b> - вопросы и ответы к экзаменам;
<b>/profile</b> - просмотр и редактирование профиля;
<b>/feedback</b> - отзывы на что-либо;
<b>/mute</b> - выдача мута в беседах.\n
<i>Чтобы получить более подробную справку по конкретной команде, используйте</i> <code>/команда ?</code>. <i>Например,</i> <code>/schedule ?</code>.''',

    'en': '''Essential modules:\n
<b>/schedule</b> - display the lessons schedule;
<b>/exam</b> - answers for the exams;
<b>/profile</b> - edit the profile;
<b>/feedback</b> - feedbacks for anything;
<b>/mute</b> - mute users in group chats.\n
<i>In order to get more info about each command use</i> <code>/command ?</code>. <i>Example:</i> <code>/schedule ?</code>.'''
}

def help_text(message, module: str) -> str:
    reference = {
        'general': HELP_TEXT_GENERAL,
    } [module]
    lang: str = message.from_user.language_code or 'en'
    default: str = reference['en']
    return reference.get(lang, default)




DONATE_TEXT_GENERAL = {
    'en': """Donate text
    1.
    2.
    3. """,

    'ru': """Текст при покупке доната
    1.
    2.
    3. """
}

def donate_helper(message) -> str:
    lang: str = message.from_user.language_code or 'en'
    default: str = DONATE_TEXT_GENERAL['en']
    return DONATE_TEXT_GENERAL.get(lang, default)


# Сопровождать пользователя при его регистрации.
REG_1 = {
    'en': '''<b>Welcome to M.A.S. (A.S. Martinow) support bot!</b>\n
This bot is to improve the experience of studying and automize some routine work.\n
Firstly, You have to register. It won't take a lot of time.\n
<b>Step 1/3:</b> Enter the name you want me to call you.\n
<i>The name must contain only cyrillic or latinic script with no numbers nor any symbols except of "-" and "_".</i>''',

    'ru': '''<b>Добро пожаловать.</b>\n
Данный бот был создан для улучшенея опыта работы студенческих групп и автоматизации бытовых действий.\n
Для начала вам нужно пройти быстрый процесс регистрации.\n
<b>Шаг 1/3</b>: Укажите своё имя. Имя <b><u>НЕ</u> должно</b>:
<i>1. быть длиннее 24 символов;
2. быть на нескольких раскладках (<u>V</u>ася, <u>Z</u>а<u>L</u>упа и т.д.);
3. содержать цифры и знаки препинания.</i>''',

    'ua': '''<b>Ласкаво просимо до бота підтримки M.A.S. (A.S. Martinow)!</b>\n
Цей бот створений для покращення процесу навчання та автоматизації деякої рутинної роботи.\n
По-перше, вам потрібно зареєструватися. Це не займе багато часу.\n
<b>Крок 1/3:</b> Введіть ім'я, яким ви хочете, щоб я вас називав.\n
<i>Ім'я повинно містити лише кирилицю або латиницю без цифр та будь-яких символів, окрім "-" та "_".</i>''',
}

REG_2 = {
    'ru': '''Регистрируясь, вы принимаете условия пользования ботом:\n
1. Все возможности в боте предоставляются как есть.
Разработчик бота и его администраторы не несут никаких обязательств по администрированию бота.\n
2. Любые действия пользователей могут логироваться с целью исправления багов и обеспечения безопасности пользователей.\n
3. Блокируя бота, вы добровольно отказываетесь от получения важной информации, которая через него может отправляться.\n
4. Используя бота, вы и только вы несёте ответсвенность за свои действия.
Запрещено искать уязвимости бота, пытаться дестабилизировать его хостинг и совершать с ним любые аморальные действия.
В качестве наказания за нарушения правил может применяться блокировка определённых команд для пользователя.\n
<b>Шаг 2/3:</b> Если вы ознакомлены и согласны с этими условиями, отправьте в чат "<code>Ознакомлен, согласен</code>" или "<code>Ознакомлена, согласна</code>".''',

    'en': '''You...''',

    'sp': '''Tu...''',
}

REG_3 = {
    'ru': '''<b>Данные сохранены!</b>\n
<i>Теперь вы можете использовать весь функционал бота.
Выберете "Помощь по всем командам" в Меню или используйте <code>/help</code>, чтобы получить справку по командам.</i>\n
<b>Шаг 3/3:</b> Выберете свою группу из списка.''',

    'en': '''<b>Your data was saved succesfuly!</b>\n
<i>Now you can use...
</i>\n
<b>Step 3/3:</b> Select your group.''',
}

def reg_text(message, stage: int) -> str:
    reference: dict = (REG_1, REG_2, REG_3)[stage - 1]
    lang: str = message.from_user.language_code or 'en'
    default: str = reference['en']
    return reference.get(lang, default)



EXAM_HELP = {
    'en': '''There are some tips for the command:\n
<b>Example 1:</b> <code>/exam мп 13</code> - 13 question for "Международное право" <i>(the exam can be determined by first letters (МП), first word (Международное), full-name (международноеправо) etc.)</i>;\n
<b>Example 2:</b> <code>/exam понятие, признаки</code> - find a question <i>(less words - wider searching);</i>\n
<b>Example 3:</b> <code>/exam фп</code> - open slide-bar with questions and answers of a certain exam;\n
<b>Example 4:</b> <code>/exam question zemelnoe</code> - output only questions as a list for a certain exam ("question" can be replaced as "q");\n
Non answer-viewing commands:
1. <code>/exam set Философия</code> - set up a question base for a certain exam.
2. <code>/exam delete гп</code> - delete all questions for a certain exam.\n
<b>Or open a slide-bar with questions and answers for a certain exam:</b>''',
    
    'ru': '''Уточните свой запрос, введя 1-2 аргумента, согласно следующим примерам:\n
<b>Пример 1:</b> <code>/exam мп 13</code> - 13 вопрос по Международному праву <i>(указать предмет можно первыми буквами (МП), первым словом (Международное), полным названием (международноеправо) и т.д.)</i>;\n
<b>Пример 2:</b> <code>/exam понятие, признаки</code> - поиск вопроса по ключевым словам <i>(чем меньше ключевых слов - тем шире поиск);</i>\n
<b>Пример 3:</b> <code>/exam фп</code> - открыть меню с вопросами во конкретному предмету;\n
<b>Пример 4:</b> <code>/exam question zemelnoe</code> - вывести только вопросы к экзамену по земельному праву (question можно заменить на q);\n
Команды не для просмотра ответов:
1. <code>/exam set Философия</code> - создать постоянный перечень вопросов к экзамену.
2. <code>/exam delete гп</code> - удалить вопросы к экзамену.\n
<b>Предварительно предлагаю выбрать перечень вопросов и ответов к одму из следующих экзаменов:</b>'''
}

EXAM_CONFIGS = {
    'ru': '''Состав словаря:

tags - все тэги экзамена
file - имя файла (указывается при exam set)
name - название для показа пользователю
name_dp - название в дательном падеже


'''
}

EXAM_NOT_FOUND_ERROR = {
    'en': 'No exam found by this tag. Only one-word tags are usable. Enter <code>/exam config</code> to search usable tag.',

    'ru': '''Вы не указали предмет или указали несуществующий.\n
Используйте тег предмета, который состоит из одного символа.\n
Вы можете использовать <code>/exam config</code> для поиска тегов.''',
}

def exam_tip_swithcer(message):
    lang: str = message.from_user.language_code or 'en'
    default: str = EXAM_NOT_FOUND_ERROR['en']
    return EXAM_NOT_FOUND_ERROR.get(lang, default)

DEFAULT_EXAM_ANSWER = 'Пока что ответа нет, но Вы можете его установить или подождать, когда он повяится.'



DEV_HELP = {
    'ru': """<b>/dev - набор команд для разработчика бота</b>

Формат: <code>/dev действие аргумент доп.аргумент</code>

Виды действий:
<code>users</code>* - пользователи
<code>delete</code>* - удаление пользователя. полный формат: delete id type, где id - уникальный id пользователя, а type - это вид удаления (physically или visually)
<code>id</code> - выдаёт message.from_user.id
<code>message</code> - выдаёт message
<code>markup</code>* - проверка клавиатуры
<code>execute</code>* - произвольный код

* - требует права администратора."""
}

FEEDBACKS_HELP = {
    'ru': """<b>Продолжая использовать эту функцию, вы принимаете следующие условия:</b>

1. За авторством каждого из отзывов стоит какой-либо пользователь. Администрация бота к нему не имеет никакого отношения.
2. Публикация любых оскорбительных и неправдивых отзывов запрещена. Такие отзывы будут удаляться по мере обнаружения.
3. Если вы считаете какой-либо из отзывов недопустимым, свяжитесь с любым администратором для его удаления.

Выберете, что вы хотите сделать:"""
}

MUTE_HELP = {
    'en': '',
    'ru': 'Формат команды:\n<code>/mute [Пользователь*] [Время в секундах] [Причина]</code>\n\n*Указать можно одно из следующих значений:\n<i>1) Telegram ID (указан в расширенном профиле бота, если пользователь зарегестрирован, в противом случае можно проверить через консоль);\n2) Тэг пользователя (Можно скопировать через просмотр профиля в ТГ);\n3) Имя пользователя в Telegram, если его ID не отображается и Тэг в профиле скрыт.</i>',
}

def help_switcher(message, command: str) -> str:
    reference = {
        'exam': EXAM_HELP,
        'exam config': EXAM_CONFIGS,
        'exam doesnt exist'
        'dev': DEV_HELP,
        'feedback': FEEDBACKS_HELP,
        'mute': MUTE_HELP,
    } [command]

    lang: str = message.from_user.language_code or 'en'
    default: str = reference['en']
    return reference.get(lang, default)


ATTENDANCE_HANDLING_MSG = {
    'en': '...',
    'ru': 'Отправьте своё местоположение для подтверждения посещения пары.\n\nДля отправки местоположения нужно использовать кнопку <i><b>"Отправить местоположение для отметки"</b></i> внизу экрана. Она отправит запрос на отправку локации, необходимо разрешить боту её использовать.',
}

ATTENDANCE_BUTTON_TEXT = {
    'en': '...',
    'ru': 'Отправить местоположение для отметки',
}

ATTENDANCE_AWAIT_ERROR = {
    'en': '...',
    'ru': 'Вы уже ввели команду для отметки и теперь должны отправить геопозицию. Данная функция работает только на мобильных устройствах (Android, iPhone, iPad, Windows Phone). Если локацию отправить не получается, разрешите в настройках устройства доступ к геолокации для Telegram и перезапустите его.',
}

ATTENDANCE_CANT_FIND_USER_ERROR = {
    'en': '...',
    'ru': 'Невозможно определить Ваше посещение, поскольку Вы не зарегестрированы. Зарегестрируйтесь командой /register',
}

def attendance_text(message, stage: str) -> str:
    reference = {
        'handle': ATTENDANCE_HANDLING_MSG,
        'button': ATTENDANCE_BUTTON_TEXT,
        'await': ATTENDANCE_AWAIT_ERROR,
        'cannotfind': ATTENDANCE_CANT_FIND_USER_ERROR
    } [stage]
    lang: str = message.from_user.language_code or 'en'
    default: str = reference['en']
    return reference.get(lang, default)



POSSIBLE_KEYBOARDS = {
    'ru': 'Доступные клавиатуры:\n',
    'en': 'Possible keyboards:\n'
}

PREVIEW_KEYBOARDS = {
    'ru': 'Предпросмотр клавиатуры',
    'en': 'Preview of the keyboard'
}

def dev_keyboard_preview(message, operation: str) -> str:
    reference = {
        'possible': POSSIBLE_KEYBOARDS,
        'preview': PREVIEW_KEYBOARDS
    } [operation]
    lang: str = message.from_user.language_code or 'en'
    default: str = reference['en']
    return reference.get(lang, default)


PROFILE_UTIL_DELETED_V = {
    'en': "You have disconnected the user from M.A.S. I don't parse his profile anymore but You can recover it via host server...",
    'ru': 'Вы отключили профиль пользователя ',
}

PROFILE_UTIL_DELETED_F = {
    'en': "You have phisically (irrevocably) deleted the user's profile.",
    'ru': 'Вы физически (безвозвратно) удалили профиль пользователя.',

}



FILL_SCHEDULE_INSTRUCTION_TEXT = {
    'en': '',

    'ru': '''<b>Инструкция:</b>\n\n1. Откройте <a href="https://rasp.rea.ru/?q=15.30д-ю05%2F22б#today">эту страницу</a> с компьютера;\n
2. Используйте <code>Ctrl + A</code> для выделения;\n
3. Используйте <code>Ctrl + C</code> для копирования;\n
4. Отправьте в этот чат то, что скопировалось.\n\n
<i>Копируйте то расписание, которое вы хотите вставить для своей группы. Бот сам разберётся, что куда записать.</i>\n\n''',

    'sp': ''
}

def fill_schedule_instruction(message):
    lang: str = message.from_user.language_code or 'en'
    default: str = FILL_SCHEDULE_INSTRUCTION_TEXT['en']
    return FILL_SCHEDULE_INSTRUCTION_TEXT.get(lang, default)



SCHEDULE_ATTENDANCE_REPORT_BAR = {
    'en': '\n\n🟩 = Your visit is recorded\n🟥 = Not recorded\n\n 💡 Use the following command to register your attendance <b>/attend</b>.',
    'ru': '\n\n🟩 = Посещение записано\n🟥 = Посещение не записано\n\n 💡 Используйте /attend, чтобы записаться.',
}

def attendance_bar(message) -> str:
    lang: str = message.from_user.language_code or 'en'
    default: str = SCHEDULE_ATTENDANCE_REPORT_BAR['en']
    return SCHEDULE_ATTENDANCE_REPORT_BAR.get(lang, default)



MESSAGE_WAS_DELETED_WARNING_TEXT = {
    'en': '''⚠️ Your message was deleted because You have been muted.\n
Text of the message: <code>%s</code>''',

    'ru': '''⚠️ Ваше сообщение было удалено, потому что Вам был выдан мут.\n
Текст сообщения: <code>%s</code>'''
}

def message_was_deleted(message) -> str:
    lang: str = message.from_user.language_code or 'en'
    default: str = MESSAGE_WAS_DELETED_WARNING_TEXT['en']
    return MESSAGE_WAS_DELETED_WARNING_TEXT.get(lang, default) % message.text
