'''Данный модуль предназначен для регулирования функций и методов чтения\n
и распрстранения получаемых писем, а также их отправки в группы.\n
Предполагаемый спектр возможностей:\n
1) проверить почту, привязанную к определённой группе по команде админа;\n
2) если на почте есть непрочитанные сообщения, собрать текст и загрузить файлы, сохранить их и отправить админу;\n
3) при одобрении отправки письма бот должен отправить содержимое в чат, который привязан к группе.'''

from sqlite3 import connect
from imap_tools import MailBox

CONNECTED_EMAILS = {
    0: {'email': None,
        'password': 'jwywuuuuqflmcpdn',
        'imap_server': 'imap.ya.ru'},

    1022105: {'email': 'hslaw.bac.jur.05.2022@yandex.ru',
              'password': 'cxgnxylxgkyyjbnc',
              'imap_server': 'imap.ya.ru'}
}

class Email:
    '''Главный класс парсера. Применяет нижеперечисленные методы:\n
    1) parser: подключение к почте группы и поиск информации о письмах;\n
    и помоему больше не нужно ничего им'''

    def __init__ (self, group_id: int = 0):
        self.EMAIL: str = CONNECTED_EMAILS [group_id] ['email']
        self.PASSWORD: str = CONNECTED_EMAILS [group_id] ['password']
        self.IMAP_SERVER: str = CONNECTED_EMAILS [group_id] ['imap_server']

    def parser (self, 
                box: str = 'INBOX', 
                limit: int = 1, 
                reverse: bool = True, 
                mark_seen: bool = False) -> list:
        '''Подюключается к почте и собирает данные из писем,
        используются нижеперечисленные параметры:\n
        1) box - название ящика (INBOX - входящие)\n
        2) limit - число писем, проверяемых парсером\n
        3) reverse - начинать с последнего полученного письма.
        Если поставить False, будет проверять с самого старого\n
        4) mark_seen - отмечать письмо прочитанным'''

        with MailBox (self.IMAP_SERVER).login (username = self.EMAIL,
                                               password = self.PASSWORD,
                                               initial_folder = box) as mail:
            collected_mails = []

            for msg in mail.fetch (limit = limit,
                                   reverse = reverse,
                                   mark_seen = mark_seen):
                attachments = []

                for attachment in msg.attachments:
                    attachments.append ({'filename': attachment.filename,
                                         'content_type': attachment.content_type,
                                         'size': attachment.size})

                collected_mails.append ({'from': msg.from_,
                                         'subject': msg.subject,
                                         'date': msg.date_str,
                                         'flags': msg.date_str,
                                         'text': msg.text,
                                         'attachments': attachments})

            return collected_mails
    
if __name__ == '__main__':
    print (Email (1022105).parser (limit = 10))