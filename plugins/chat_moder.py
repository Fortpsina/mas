import json
from datetime import datetime, timedelta
from sqlite3 import connect


def pun_append (punnished_id, reason, pun_author, pun_type, first_date, pun_time, second_date_readable):
    try:
        data = json.load(open('punishments.json', 'r', encoding='utf-8'))

    except json.JSONDecodeError:
        data = []

    first_date_readable = f'{datetime.now().strftime("%d:%m:%Y %H:%M:%S")}'

    if False:
        actual_time = datetime.now() + timedelta(hours=3)
        first_date_readable = f'{actual_time.strftime("%d.%m.%Y %H:%M:%S")}'

    data.append(
        {
            'punished_id': punnished_id,
            'punishment_id': len(data),
            'reason': reason,
            'pun_author': pun_author,
            'pun_type': pun_type,
            'first_date': first_date,
            'last_date': int (first_date) + pun_time,
            'first_date_readable': first_date_readable,
            'second_date_readable': second_date_readable,
            'ignore_punishment': False
        }
    )
    json.dump(data, open('punishments.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
