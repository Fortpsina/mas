from telebot import TeleBot

mas = True
massuportbot_token = None
fortpsinabot_token = None
bot = TeleBot(massuportbot_token if mas else fortpsinabot_token)
Fortpsinabot = TeleBot(fortpsinabot_token)

admin_id = None

groups = None

# Host: https://cloud.amvera.ru/projects
# Password: 1341Ab310
# Username: Fortpsina