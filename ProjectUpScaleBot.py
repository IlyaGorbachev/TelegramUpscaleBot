#DeepVideoFake_bot
import json
import asyncio
import requests
import urllib.request
from Upscale import func_upscale
from telebot.async_telebot import AsyncTeleBot
from telebot import types
from tokenbot import TOKEN_BOT

#Создаем бота и вносим токен
bot = AsyncTeleBot(TOKEN_BOT)

###Json инфа о пользователях, file_type_await=[None, "document", "audio", "video", "photo"]
#Запись
async def json_dump(id_user, id_chat=None, file_type_await=None, file_path_last=None, first_name=None, last_name=None, username=None, denoise=True):
    data = {
        "id_user": str(id_user),
        "id_chat": str(id_chat),
        "file_type_await": str(file_type_await),
        "file_path_last": str(file_path_last),
        "first_name": str(first_name),
        "last_name": str(last_name),
        "username": str(username),
        "denoise": denoise
    }
    with open("users_info/"+str(id_user)+".json", "w") as json_file:
        json.dump(data, json_file)
#Изменение json
async def json_mod(id_user, id_chat=None, file_type_await=None, file_path_last=None):
    with open("users_info/"+str(id_user)+".json", "r") as json_file:
        data = json.load(json_file)
        json_file.close()
    with open("users_info/"+str(id_user)+".json", "w") as json_file:
        if id_chat!=None: data["id_chat"]=str(id_chat)
        if file_type_await!=None: data["file_type_await"]=file_type_await
        if file_path_last!=None: data["file_path_last"]=file_path_last
        json.dump(data, json_file)
        
#Проверка на тип файла
async def json_check_file(id_user):
    with open("users_info/"+str(id_user)+".json", "r") as json_file:
        data = json.load(json_file)
        return data["file_type_await"] 
#Проверка на denoise
async def json_check_denoise(id_user):
    with open("users_info/"+str(id_user)+".json", "r") as json_file:
        data = json.load(json_file)
        return data["denoise"] 



###Функции для работы
#Функция скачивания файлов  file_29.mp4: формат
async def save_file(message, TOKEN_BOT, content_types):
    if content_types == "audio":
        getfile_type = message.audio
    elif content_types == "document":
        getfile_type = message.document
    elif content_types == "video":
        getfile_type = message.video
    elif content_types == "photo":
        getfile_type = message.photo[-1] #Качество фото зависит от photo[0:1:2:3]

    #Создаем объект file и получаем path - это ссылка на файл. https://api.telegram.org/file/bot<token>/<file_path> качаем отсюда
    file = await bot.get_file(getfile_type.file_id)
    await bot.send_message(message.chat.id, "Грузим файл...")
    urllib.request.urlretrieve("https://api.telegram.org/file/bot"+TOKEN_BOT+"/"+file.file_path, file.file_path)
    await json_mod(id_user=message.from_user.id, file_path_last=file.file_path)
    await bot.send_message(message.chat.id, "Файл загружен")

    if content_types == "photo":
        await bot.send_message(message.chat.id, "Теперь нужно подождать...")
        func_upscale(file.file_path)
        photo = open('aiupscale/output/scaled_3x_denoise.png', 'rb')
        await bot.send_photo(message.chat.id, photo)
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        Button_start = types.KeyboardButton(text="Увеличить качество")
        keyboard.add(Button_start)
        await bot.send_message(message.chat.id, "Готово.", reply_markup=keyboard)
    print("Файл загружен и сохранен", content_types, "Вес: ", getfile_type.file_size)


    
###Emoji ⚙️ 🏠 ✅ ❌

###Всякие кнопки
keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
Button_start = types.KeyboardButton(text="Увеличить качество")
Button_options = types.KeyboardButton(text="⚙️")
Button_home = types.KeyboardButton(text="🏠")
Button_denoise_on = types.KeyboardButton(text="Denoise✅")
Button_denoise_off = types.KeyboardButton(text="Denoise❌")
cort_keyboard = (keyboard, Button_start, Button_options, Button_home, Button_denoise_on, Button_denoise_off)


###Модуль взаимодействия
#content_types=['audio', 'photo', 'voice', 'video', 'document', 'text', 'location', 'contact', 'sticker']
# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message, keyboard=cort_keyboard):
    await json_dump(message.from_user.id, message.chat.id)   
    keyboard[0].add(keyboard[1],keyboard[2])

    await bot.send_message(message.chat.id, "Привет!\nЯ UpScaleImageBot 1.0 и я могу увеличить качество картинки.", reply_markup=keyboard[0])
   
#Основное меню
@bot.message_handler(content_types=["text"])
async def menu_message(message, keyboard=cort_keyboard):
    if message.text == "Увеличить качество":
        await bot.send_message(message.chat.id, "Жду картинку")
        await json_mod(message.from_user.id, file_type_await="photo")
    elif message.text == "⚙️":
        if json_check_denoise(message.from_user.id) == True: 
            keyboard[0].add(keyboard[4], keyboard[3])
        else:
            keyboard[0].add(keyboard[5], keyboard[3])
        await bot.send_message(message.chat.id, "Настройки", reply_markup=keyboard[0])

    else:
        await bot.send_message(message.chat.id, "Неизвестная команда")








#Для документов
@bot.message_handler(content_types=["document"])
async def file_message(message):
    if await json_check_file(message.from_user.id) == "document":
        await save_file(message, TOKEN_BOT, content_types="document")
        await json_mod(message.from_user.id, file_type_await="None")
    else:
        await bot.send_message(message.chat.id, "Я ждал другое...")
     

#Для audio
@bot.message_handler(content_types=["audio"])
async def file_message(message):
    if await json_check_file(message.from_user.id) == "audio":
        await save_file(message, TOKEN_BOT, content_types="audio")
        await json_mod(message.from_user.id, file_type_await="None")
    else:
        await bot.send_message(message.chat.id, "Я ждал другое...")

#Для video
@bot.message_handler(content_types=["video"])
async def file_message(message):
    if await json_check_file(message.from_user.id) == "video":
        await save_file(message, TOKEN_BOT, content_types="video")
        await json_mod(message.from_user.id, file_type_await="None")
        
    else:
        await bot.send_message(message.chat.id, "Я ждал другое...")

#Для photo
@bot.message_handler(content_types=["photo"])
async def file_message(message):
    if await json_check_file(message.from_user.id) == "photo":
        await save_file(message, TOKEN_BOT, content_types="photo")
        await json_mod(message.from_user.id, file_type_await="None")
    else:
        await bot.send_message(message.chat.id, "Я ждал другое...")
    

asyncio.run(bot.polling())
