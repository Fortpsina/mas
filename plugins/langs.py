NOT_ENOUGH_RIGHTS_ERROR = {
    'en': 'You are not allowed to use this command.',
    'ru': 'Вы не можете использовать эту команду.',
    'sp': 'No tiene permitido usar este comando.',
    'de': 'Sie dürfen diesen Befehl nicht verwenden.',
    'fr': 'Vous nêtes pas autorisé à utiliser cette commande.',
    'ua': 'Вам не дозволено використовувати цю команду.',
    'pl': 'Nie masz uprawnień do używania tego polecenia.',
    'ar': 'لا يُسمح لك باستخدام هذا الأمر.',
    'ch': '您无权使用此命令。',
    'jp': 'このコマンドを使用することはできません。',
    'kr': '이 명령을 사용할 수 없습니다.',
}

def not_enough_rights(message) -> str:
    # при инициализации lang ставится or 'en' на случай,
    # если из сообщения не удастся извлечь язык пользователя
    lang: str = message.from_user.language_code or 'en'
    # при получении содержимого английский используется как 
    # запасной вариант на случай, если в словаре нет указанного языка
    default: str = NOT_ENOUGH_RIGHTS_ERROR['en']
    return NOT_ENOUGH_RIGHTS_ERROR.get(lang, default)


PROFILE_NOT_FOUND_ERROR = {
    'en': 'Can not find this user info. Register using the following command: <b>/register</b>.',
    'ru': 'Информация о пользователе не найдена. Зарегестрируйтесь командой <b>/register</b>.',
    'sp': 'No se encuentra la información de este usuario. Regístrese con el siguiente comando: <b>/register</b>.',
    'de': 'Diese Benutzerinformationen können nicht gefunden werden. Registrieren Sie sich mit dem folgenden Befehl: <b>/register</b>.',
    'fr': 'Impossible de trouver les informations de cet utilisateur. Inscrivez-vous avec la commande suivante: <b>/register</b>.',
    'ua': 'Не вдається знайти інформацію про цього користувача. Зареєструйтесь за допомогою такої команди: <b>/register</b>.',
    'pl': 'Nie można znaleźć informacji o tym użytkowniku. Zarejestruj się za pomocą następującego polecenia: <b>/register</b>.',
    'ar': 'لم يتم العثور على معلومات هذا المستخدم. سجّل باستخدام الأمر التالي: <b>/register</b>.',
    'ch': '找不到此用户信息。请使用以下命令注册：<b>/register</b>。',
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
    'ar': 'لم يتم العثور على معلومات هذا المستخدم.',
    'ch': '找不到该用户信息。',
    'jp': 'このユーザー情報が見つかりません。',
    'kr': '이 사용자 정보를 찾을 수 없습니다.',
}

def profile_not_found(message, own: bool = False) -> str:
    reference: dict = PROFILE_NOT_FOUND_ERROR if own else PROFILE_NOT_FOUND_ERROR_NOT_OWN
    lang: str = message.from_user.language_code or 'en'
    default: str = reference['en']
    return reference.get(lang, default)



HELP = {
    'ru': '''Основные функции:

<b>/schedule</b> - вывод расписания пар;
<b>/exam</b> - вопросы и ответы к экзаменам;
<b>/profile</b> - просмотр и редактирование профиля;
<b>/feedback</b> - отзывы на что-либо;
<b>/mute</b> - выдача мута в беседах.

<i>Чтобы получить более подробную справку по конкретной команде, используйте</i> <code>/команда ?</code>. <i>Например,</i> <code>/schedule ?</code>.''',

    'en': '''Essential modules:

<b>/schedule</b> - display the lessons schedule;
<b>/exam</b> - answers for the exams;
<b>/profile</b> - edit the profile;
<b>/feedback</b> - feedbacks for anything;
<b>/mute</b> - mute users in group chats.

<i>In order to get more info about each command use</i> <code>/command ?</code>. <i>Example:</i> <code>/schedule ?</code>.'''
}

def help_text(message) -> str:
    lang: str = message.from_user.language_code or 'en'
    default: str = HELP['en']
    return HELP.get(lang, default)



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
<b>Шаг 2/3:</b> Если вы ознакомлены и согласны с этими условиями, отправьте в чат "<code>Ознакомлен, согласен</code>" или "<code>Ознакомлена, согласна</code>".'''
}

REG_3 = {
    'ru': '''<b>Данные сохранены!</b>\n
<i>Теперь вы можете использовать весь функционал бота.
Выберете "Помощь по всем командам" в Меню или используйте <code>/help</code>, чтобы получить справку по командам.</i>\n
<b>Шаг 3/3:</b> Выберете свою группу из списка.'''
}

def reg_text(message, stage: int) -> str:
    reference: dict = (REG_1, REG_2, REG_3)[stage - 1]
    lang: str = message.from_user.language_code or 'en'
    default: str = reference['en']
    return reference.get(lang, default)



EXAM_HELP = {
    'ru': '''Уточните свой запрос, введя 1-2 аргумента, согласно следующим примерам:

<b>Пример 1:</b> <code>/exam мп 13</code> - 13 вопрос по Международному праву <i>(указать предмет можно первыми буквами (МП), первым словом (Международное), полным названием (международноеправо) и т.д.)</i>;

<b>Пример 2:</b> <code>/exam понятие, признаки</code> - поиск вопроса по ключевым словам <i>(чем меньше ключевых слов - тем шире поиск);</i>

<b>Пример 3:</b> <code>/exam фп</code> - открыть меню с вопросами во конкретному предмету;

<b>Пример 4:</b> <code>/exam question zemelnoe</code> - вывести только вопросы к экзамену по земельному праву (question можно заменить на q);

Команды не для просмотра ответов:
1. <code>/exam set Философия</code> - создать постоянный перечень вопросов к экзамену.
2. <code>/exam delete гп</code> - удалить вопросы к экзамену.

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

EXAM_NOT_EXISTING_TAG_ERROR = {
    'ru': '''Вы не указали предмет или указали несуществующий.

Используйте тег предмета, который состоит из одного символа.

Вы можете использовать <code>/exam config</code> для поиска тегов.'''
}


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


POSSIBLE_KEYBOARDS = {
    'ru': 'Доступные клавиатуры:\n',
    'en': 'Possible keyboards:\n'
}

PREVIEW_KEYBOARDS = {
    'ru': 'Предпросмотр клавиатуры',
    'en': 'Preview of the keyboard'
}


PROFILE_UTIL_DELETED_V = {
    'en': "You have disconnected the user from M.A.S. I don't parse his profile anymore but You can recover it via host server.",
    'ru': 'Вы отключили профиль пользователя.',
}

PROFILE_UTIL_DELETED_F = {
    'en': "You have phisically (irrevocably) deleted the user's profile.",
    'ru': 'Вы физически (безвозвратно) удалили профиль пользователя.',

}
