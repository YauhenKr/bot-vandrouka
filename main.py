import telebot
import yaml
import csv
import shutil
import os
from tempfile import NamedTemporaryFile
from telebot import types

bot = telebot.TeleBot('5559498524:AAEGomo_B0eZ7yAeEk3nGyNlt5zkYnbbBdo')   # token (name = Vandrouka_Mensk)

user_dict = {}  # fullname, number
text_from_file = {}

# open file bel or rus
def get_text_data(language_file):
    with open(language_file, 'r', encoding="utf-8") as f:

        return yaml.load(f, Loader=yaml.FullLoader)


# return name of file
def set_language_file(message):
    global text_from_file

    if message.text == 'Беларуская':
        language_file = 'text_bel.yaml'
    elif message.text == 'Русский':
        language_file = 'text_rus.yaml'

    text_from_file = get_text_data(language_file)


@bot.message_handler(commands=['start'])
def choice_lang(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True , resize_keyboard=True, row_width=2)
    bel = types.KeyboardButton('Беларуская')
    rus = types.KeyboardButton('Русский')
    markup.add(bel, rus)
    msg = bot.send_message(message.chat.id, 'Абярыце мову / Выберете язык', reply_markup=markup)
    types.ReplyKeyboardRemove(selective=False)
    bot.register_next_step_handler(msg, check_code)


def check_code(message):
    global text_from_file

    set_language_file(message)
    user_exists = search_user_id(message.from_user.id)

    if user_exists:
        check_name(message)
    else:
        msg = bot.send_message(message.chat.id, text_from_file["unicode"])
        bot.register_next_step_handler(msg, search_code)


def search_user_id(id):
    with open("user.csv", mode="r", encoding='utf-8') as r_user:
        fields = ['ID', 'Name']
        file_reader = csv.DictReader(r_user, fieldnames=fields, delimiter=";")
        for row in file_reader:
            if row['ID'] == str(id):
                return True
        return False


def search_code(message):
    global text_from_file

    with open('passwords.txt', 'r+', encoding="utf-8") as psw_file:
        lst = [line.strip() for line in psw_file]
    if message.text in lst:
        deactivate_code(message)
        fields = ['ID', 'Name']
        with open("user.csv", mode="a", encoding='utf-8') as write:
            writer = csv.DictWriter(write, fieldnames=fields, delimiter=";")
            row = {'ID': str(message.from_user.id)}
            writer.writerow(row)
        check_name(message)
    else:
        wrong = bot.send_message(message.chat.id, text_from_file["wrong_code"])
        bot.register_next_step_handler(wrong, search_code)


def deactivate_code(message):
    with open("passwords.txt", mode="r", encoding='utf-8') as old:
        reader = old.read()
    writer = reader.replace(message.text, f'-{message.text}')

    with open("passwords_temp.txt", mode="w", encoding='utf-8') as temp:
        temp.write(writer)

    os.remove("passwords.txt")
    os.rename("passwords_temp.txt", "passwords.txt")


def check_name(message):
    global text_from_file

    name_exists = search_name(message.from_user.id)

    if name_exists:
        send_rules(message)
    else:
        msg = bot.send_message(message.chat.id, text_from_file["name"])
        bot.register_next_step_handler(msg, validate_name)


def search_name(id):
    fields = ['ID', 'Name']
    with open("user.csv", mode="r", encoding='utf-8') as r_user:
        file_reader = csv.DictReader(r_user, fieldnames=fields, delimiter=";")
        for row in file_reader:
            if row['ID'] == str(id):
                if row['Name'] == '':
                    return False
                else:
                    bot.send_message(id, f'{text_from_file["hi"]} {row["Name"]}')
                    return True


def validate_name(message):
    if is_name_valid(message):
        save_name(message)
    else:
        msg = bot.send_message(message.chat.id, text_from_file['wrong_name'])
        bot.register_next_step_handler(msg, validate_name)


def is_name_valid(message):
    global text_from_file
    letters_eng = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    letters_bel = 'абвгдеёжзіийклмнопрстуўфхцчшщъыьэюяАБВГДЕЁЖЗІИЙКЛМНОПРСТУЎФХЦЧШЩЪЫЬЭЮЯ'
    symbols = "' -"
    allowed_chars = letters_bel + letters_eng + symbols
    if 2 > len(message.text) or len(message.text) > 20:
        return False

    for letter in message.text:
        if letter not in allowed_chars:
            return False

    return True


def save_name(message):
    global text_from_file
    fields = ['ID', 'Name']
    tempfile = NamedTemporaryFile(mode='w', encoding='utf-8', delete=False)
    with open("user.csv", mode="r", encoding='utf-8') as old, tempfile:
        reader = csv.DictReader(old, fieldnames=fields, delimiter=";")
        writer = csv.DictWriter(tempfile, fieldnames=fields, delimiter=";")
        for row in reader:
            if row['ID'] == str(message.from_user.id):
                row['Name'] = message.text
            row = {'ID': row['ID'], 'Name': row['Name']}
            writer.writerow(row)

    shutil.move(tempfile.name, 'user.csv')
    bot.send_message(message.chat.id, f'{text_from_file["hi"]} {message.text}')
    send_rules(message)


def send_rules(message):
    global text_from_file

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=1)
    first_place = types.KeyboardButton(text_from_file['task']['first']['place'])
    markup.add(first_place)
    msg = bot.send_message(message.chat.id, f'{text_from_file["rules"]}', reply_markup=markup, parse_mode='html')
    types.ReplyKeyboardRemove(selective=False)
    bot.register_next_step_handler(msg, first_task, text_from_file)


def first_task(message, text_from_file):
    markup = types.InlineKeyboardMarkup(row_width=1)
    answ_1 = types.InlineKeyboardButton(text_from_file['task']['first']['answer_1'], callback_data='a_1')
    answ_2 = types.InlineKeyboardButton(text_from_file['task']['first']['answer_2'], callback_data='a_2')    # true
    answ_3 = types.InlineKeyboardButton(text_from_file['task']['first']['answer_3'], callback_data='a_3')
    markup.add(answ_1, answ_2, answ_3)
    msg = bot.send_message(message.chat.id, text_from_file['task']['first']['first_info'], reply_markup=markup)


@bot.callback_query_handler(func=lambda call:True)
def callback_first_task(call):
    global text_from_file
    if call.data == 'a_2':
        bot.send_message(call.message.chat.id, text_from_file['task']['first']['right_answer'])
        bot.send_message(call.message.chat.id, text_from_file['task']['first']['history_first'])

        photo_1 = open('images/f_1.JPG', 'rb')
        photo_2 = open('images/f_2.jpg', 'rb')
        photo_3 = open('images/f_3.jpg', 'rb')
        photo_4 = open('images/f_4.jpg', 'rb')
        photo_5_1 = open('images/f_5_1.jpg', 'rb')
        photo_5_2 = open('images/f_5_2.jpg', 'rb')
        photo_5_3 = open('images/f_5_3.jpg', 'rb')
        photo_6 = open('images/f_6.jpg', 'rb')
        photo_7 = open('images/f_7.jpg', 'rb')
        bot.send_photo(call.message.chat.id, photo_1, text_from_file['task']['first']['photos_1']['photo_1'])
        bot.send_photo(call.message.chat.id, photo_2, text_from_file['task']['first']['photos_1']['photo_2'])
        bot.send_photo(call.message.chat.id, photo_3, text_from_file['task']['first']['photos_1']['photo_3'])
        bot.send_photo(call.message.chat.id, photo_4, text_from_file['task']['first']['photos_1']['photo_4'])
        bot.send_photo(call.message.chat.id, photo_5_1, text_from_file['task']['first']['photos_1']['photo_5'])
        bot.send_photo(call.message.chat.id, photo_5_2, text_from_file['task']['first']['photos_1']['photo_5'])
        bot.send_photo(call.message.chat.id, photo_5_3, text_from_file['task']['first']['photos_1']['photo_5'])
        bot.send_photo(call.message.chat.id, photo_6, text_from_file['task']['first']['photos_1']['photo_6'])
        bot.send_photo(call.message.chat.id, photo_7, text_from_file['task']['first']['photos_1']['photo_7'])
        return

    bot.send_message(call.message.chat.id, text_from_file['task']['first']['wrong_answer'])


bot.polling(none_stop=True)