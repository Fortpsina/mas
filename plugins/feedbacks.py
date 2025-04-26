from sqlite3 import connect
from datetime import datetime


def create_table_feedback (name: str = 'feedback') -> None:

    conn = connect(f'{name}.sql')
    cur = conn.cursor()

    cur.execute(
        'CREATE TABLE IF NOT EXISTS feedback' +
        '(id int auto_increment primary key, ' +
        'feedback_id INTEGER, ' +
        'name varchar(50), ' +
        'text varchar(4000), ' +
        'author_id INTEGER, ' +
        'author_name varchar(50), ' +
        'date varchar(50), ' +
        'positive_ratings varchar(4000), ' +
        'negative_ratings varchar(4000), ' +
        'is_deleted INTEGER' +
        ')'
    )
    conn.commit()
    
    cur.close()
    conn.close()

def feedback_contents ():
    conn = connect(f'feedback.sql')
    cur = conn.cursor()

    cur.execute('SELECT name FROM feedback')
    all_elements = cur.fetchall()
    result = ''
    i = 1

    for name in all_elements:
        if name[0] in result:
            continue
        result += f'{i}. <code>{name[0]}</code>'

        if i % 3 == 0:
            result += ';\n'
        else:
            result += '; '

        i += 1
    
    cur.close()
    conn.close()

    return result


class Feedback:
    '''
    Отзывы на преподов
    '''

    def __init__ (
            self,
            name: str = 'Что-то',
            text: str = 'Текст отзыва',
            author: str = 'Аноним',
            date: str = datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            positive_ratings: str = '',
            negative_ratings: str = '',
    ):
        self.name = name
        self.text = text
        self.author = author
        self.date = date
        self.positive_ratings = positive_ratings
        self.negative_ratings = negative_ratings

    def set_object (self):
        pass

    def edit_feedback (self, feedback_id: int, column: str = 'text', new_value = ''):
        conn = connect('feedback.sql')
        cur = conn.cursor()

        cur.execute(f'UPDATE feedback SET {column} = "{new_value}" WHERE feedback_id = {feedback_id}')
        conn.commit()

        cur.close()
        conn.close()

    
    def delete_feedback (self, feedback_id: int, delete: bool = True):
        conn = connect('feedback.sql')
        cur = conn.cursor()

        if delete:
            cur.execute(f'UPDATE feedback SET is_deleted = 1 WHERE feedback_id = {feedback_id}')
        else:
            cur.execute(f'UPDATE feedback SET is_deleted = 0 WHERE feedback_id = {feedback_id}')
        conn.commit()

        cur.close()
        conn.close()


    def set_feedback (self, author_id: int = 0):

        conn = connect('feedback.sql')
        cur = conn.cursor()

        cur.execute ('SELECT feedback_id FROM feedback')
        feedback_id = len(cur.fetchall())

        cur.execute(
            'INSERT INTO feedback ' +
            '(feedback_id, name, text, author_id, author_name, date, positive_ratings, negative_ratings, is_deleted) ' +
            ' VALUES (' +
            f'"{feedback_id}", ' +    
            f'"{self.name}", ' +         
            f'"{self.text}", ' +         
            f'"{author_id}", ' +    
            f'"{self.author}", ' +  
            f'"{self.date}", ' +               
            f'"{self.positive_ratings}", ' +   
            f'"{self.negative_ratings}", ' +                 
            f'"{0}"' +
            ')'
        )
        conn.commit()

        cur.close()
        conn.close()



if __name__ == '__main__':
    create_table_feedback()
    Feedback(name = 'Test1', text = 'Test2').set_feedback()