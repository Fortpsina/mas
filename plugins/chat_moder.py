from json import load, dump, JSONDecodeError
from datetime import datetime, timedelta, timezone
from sqlite3 import connect
from random import randint
from pytz import timezone
from re import compile


LOCALZONE = None
TIME_OFFSET = timezone('Europe')


def parse_time(custom_time: str) -> timedelta:
    time_pattern = compile(r'(?P<value>d+)(?P<unit>[wdhmns])')
    total_seconds = 0
    
    for match in time_pattern.finditer(custom_time):
        value = int(match.group('value'))
        unit = match.group('unit')
        
        if unit == 'w':
            total_seconds += value * 7 * 24 * 3600
        elif unit == 'd':
            total_seconds += value * 24 * 3600
        elif unit == 'h':
            total_seconds += value * 3600
        elif unit == 'm':
            total_seconds += value * 60
        elif unit == 's':
            total_seconds += value

    return timedelta(seconds=total_seconds)

def add_time_to_utc_now(time_str):
    current_utc_time = datetime.now(timezone.utc)
    time_delta = parse_time(time_str)
    new_time = current_utc_time + time_delta
    return new_time

# Пример использования
if __name__ == "__main__":
    input_time = input("Укажите время (например, 1d12h30m5s): ")
    result_time = add_time_to_utc_now(input_time)
    print("Новое время (UTC):", result_time)



class Mute:
    def __init__(self, for_who: str, by_who: str, reason: str, time: str):
        self.for_who = for_who
        self.by_who = by_who
        
        self.reason = reason

        self.since = datetime.utcnow()
        self.until: datetime = self.since + timedelta()

        self.since_DDMMYYYY: datetime = self.since.strftime("%d:%m:%Y %H:%M:%S")
        self.until_DDMMYYYY: datetime = self.until.strftime("%d.%m.%Y %H:%M:%S")

        self.data = {
            'for_who': self.for_who,
            'by_who': self.by_who,
            'reason': self.reason,
            'punishment_id': randint(1, 1000000),
            'time': add_time_to_utc_now(time)
        }
    
    def append(self) -> str:
        dump(self.data,
             open('punishments.json', 'w', encoding='utf-8'),
             ensure_ascii=False,
             indent=4)
        
        return f'Выдача мута пользователю {self.for_who}:\n Причина: <code>{self.reason}</code>;\n\nНачало мута: <code>{self.since_DDMMYYYY}</code>\nКонец мута: <code>{self.until_DDMMYYYY}</code>'


def pun_wipe(message):
    try:
        pun_logs = load(open('punishments.json', 'r', encoding='utf-8'))

    except JSONDecodeError:
        pun_logs = []

    dump([],
         open('punishments.json', 'w', encoding='utf-8'),
         ensure_ascii=False,
         indent=4)

    for log in pun_logs:
        print(log)

    return 'Вы удалили все имеющиеся наказания:' + '\n'.join(pun_logs)


def pun_append(for_who, by_who, reason, pun_time):
    try:
        data = load(open('punishments.json', 'r', encoding='utf-8'))

    except JSONDecodeError:
        data = []

    first_date_readable = f'{datetime.now().strftime("%d:%m:%Y %H:%M:%S")}'

    if False:
        actual_time = datetime.now() + timedelta(hours=3)
        first_date_readable = f'{actual_time.strftime("%d.%m.%Y %H:%M:%S")}'

    data.append(
        {
            'for_who': for_who,
            'by_who': by_who,
            'reason': reason,
            'punishment_id': randint(1, 1000000),
            'time': pun_time
        }
    )

def unmute_user(muted: int) -> str:
    try:
        data = load(open('punishments.json', 'r', encoding='utf-8'))
        for el in data:
            if int(el['for_who']) == muted:
                data.remove(el)
                dump(data, open('punishments.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
                return f'Мут с {muted} снят.'

    except JSONDecodeError:
        return f'Не удалось найти у пользователя {muted}.'

    return f'Не удалось найти у пользователя {muted}.'
