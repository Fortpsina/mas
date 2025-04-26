from random import randint

COLOR_THEME_LIST = (
    'default',
    'red',
    'pink',
    'olive',
    'blue',
    'ochre',
    'yellow',
    'white',
    'black',
    'cyan',
    'purple'
)

def clr (color: str = 'default') -> dict:
    '''bg (background) - цвет, используемый в виде заднего фона.\n
    frame - цвет фона рамки (отображается под каждой парой).\n
    ol (outline) - в старой версии использовалась только для обводки рамки с парой,
    сейчас используется также и для некоторых надписей (дата, место, тип занятия, д/з).\n
    text - цвет основного текста (день недели, название пары).\n
    timings - цвет, которым пишется время занятия.\n
    attend - цвет выделения квадратиков для тех пар, где посещение не зафиксировано.\n
    non_attend - ставится в квадратике, если посещение найдено.\n
    
    Подбор цветов RGB: https://colorscheme.ru/html-colors.html'''

    if color == 'random':
        color = COLOR_THEME_LIST [randint (0, len (COLOR_THEME_LIST) - 1)]

    if color == 'red':
        return {
            'bg': (139, 0, 0),
            'frame': (128, 0, 0),
            'ol': (255, 0, 0),
            'text': (255, 192, 203),
            'timings': (255, 192, 203),
            'attend': (0, 128, 0),
            'non_attend': (139, 0, 0)
        }

    elif color == 'pink':
        return {
            'bg': (239, 152, 197),
            'frame': (255, 182, 193),
            'ol': (139, 0, 139),
            'text': (128, 0, 128),
            'timings': (255, 192, 203),
            'attend': (0, 128, 0),
            'non_attend': (139, 0, 0)
        }

    elif color == 'olive':
        return {
            'bg': (143, 188, 143),
            'frame': (85, 107, 47),
            'ol': (139, 69, 19),
            'text': (255, 248, 220),
            'timings': (255, 192, 203),
            'attend': (0, 128, 0),
            'non_attend': (139, 0, 0)
        }

    elif color == 'blue':
        return {
            'bg': (25, 25, 112),
            'frame': (0, 0, 128),
            'ol': (30, 144, 255),
            'text': (135, 206, 235),
            'timings': (255, 192, 203),
            'attend': (0, 128, 0),
            'non_attend': (139, 0, 0)
        }

    elif color == 'ochre':
        return {
            'bg': (189, 183, 107),
            'frame': (238, 232, 170),
            'ol': (255, 255, 224),
            'text': (139, 69, 19),
            'timings': (255, 192, 203),
            'attend': (0, 128, 0),
            'non_attend': (139, 0, 0)
        }

    elif color == 'yellow':
        return {
            'bg': (255, 215, 0),
            'frame': (255, 255, 0),
            'ol': (184, 134, 11),
            'text': (255, 69, 0),
            'timings': (255, 192, 203),
            'attend': (0, 128, 0),
            'non_attend': (139, 0, 0)
        }

    elif color == 'white':
        return {
            'bg': (211, 211, 211),
            'frame': (255, 255, 255),
            'ol': (0, 0, 0),
            'text': (0, 0, 0),
            'timings': (255, 192, 203),
            'attend': (0, 128, 0),
            'non_attend': (139, 0, 0)
        }

    elif color == 'black':
        return {
            'bg': (10, 10, 10),
            'frame': (0, 0, 0),
            'ol': (47, 79, 79),
            'text': (248, 248, 255),
            'timings': (255, 192, 203),
            'attend': (0, 128, 0),
            'non_attend': (139, 0, 0)
        }

    elif color == 'cyan':
        return {
            'bg': (60, 80, 80),
            'frame': (47, 79, 79),
            'ol': (175, 238, 238),
            'text': (255, 240, 245),
            'timings': (255, 192, 203),
            'attend': (0, 128, 0),
            'non_attend': (139, 0, 0)
        }

    elif color == 'purple':
        return {
            'bg': (64, 0, 64),
            'frame': (32, 0, 32),
            'ol': (255, 105, 180),
            'text': (255, 20, 147),
            'timings': (175, 238, 238),
            'attend': (0, 128, 0),
            'non_attend': (139, 0, 0)
        }

    elif color == 'default':
        return {
            'bg': (30, 16, 2),
            'frame': (28, 25, 22),
            'ol': (255, 255, 255),
            'text': (250, 189, 128),
            'timings': (255, 192, 203),
            'attend': (0, 100, 0),
            'non_attend': (139, 0, 0)
        }