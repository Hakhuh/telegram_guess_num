import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandObject
from random import randint
import json
from json import JSONDecodeError
from collections import defaultdict

load_dotenv()
TOKEN = os.getenv("token")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.startup()
async def read_database():  # загружает файлы с id чатов словарями в код

    print("BOT STARTED")
    global chats
    global chats2

    try:
        with open("chats.json", "r", encoding='utf-8') as f:
            chats = json.load(f)
            print("chats succesfully loaded")
    except FileNotFoundError, JSONDecodeError:
        chats = {}

    try:
        with open("chats2.json", "r", encoding='utf-8') as file:
            my_dict = json.load(file)
            chats2 = defaultdict(dict, my_dict)  # нужен что б можно было создать вложенный словарь без ошибки
            print("chats2 succesfully loaded")
    except FileNotFoundError, JSONDecodeError:
        chats2 = {}
        chats2 = defaultdict(dict)  # нужен что б можно было создать вложенный словарь без ошибки

def set_min(chat_id, num):  # по id телеграм чата ставит минимальное число

    chats2[str(chat_id)]["min"] = num 
    print(f"min number {num} for chat {chat_id} applied")
    

def set_max(chat_id, num):  # по id телеграм чата ставит максимальное число

    chats2[str(chat_id)]["max"] = num
    print(f"max number {num} for chat {chat_id} applied")
    

def are_in_chats2(chat_id: int):  # если пользователь/группа впервые запустил(и) бота
    if str(chat_id) not in chats2:
        set_min(chat_id, 1)
        set_max(chat_id, 100)



async def ugadayka_start(message):  # запускает бота коммандой /start и /again
    if chats2[str(message.chat.id)]["min"] >= chats2[str(message.chat.id)]["max"]:  
        await message.reply("Минимальное значение /min не должно быть больше или равно максимальному значению /max")
        return
    print(f"chat {str(message.chat.id)} started")
    chats[str(message.chat.id)] = randint(chats2[str(message.chat.id)]["min"], chats2[str(message.chat.id)]["max"])
    print(f"new chat and it's num in dict chats ({str(message.chat.id)})")
    await message.reply(f"Здравствуйте! Это числовая угадайка! я загадал число от {chats2[str(message.chat.id)]["min"]} до {chats2[str(message.chat.id)]["max"]}, а вы попробуйте его отгадать" \
                        " \n Пишите, пожалуйста только целые числа для правильной работы бота")


async def ugadayka(message, num: str):  # сама игра
    if chats2[str(message.chat.id)]["min"] >= chats2[str(message.chat.id)]["max"]:
        await message.reply("Минимальное значение /min не должно быть больше или равно максимальному значению /max")
        return

    if str(message.chat.id) not in chats:  # если пользователь впервые
        chats[str(message.chat.id)] = randint(chats2[str(message.chat.id)]["min"], chats2[str(message.chat.id)]["max"])
        print(f"new chat and it's num in dict chats ({str(message.chat.id)})")
    try:
        user_num = int(num)
    except ValueError, TypeError:
        await message.reply("Это НЕ число, пишите, пожалуйста только числа без лишнего текста")
    else:
        if user_num > chats[str(message.chat.id)]:
            await message.reply("Меньше")
        elif user_num < chats[str(message.chat.id)]:
            await message.reply("Больше")
        else:
            await message.reply(f"Вы угадали!!! Число было {user_num}!! Поздравляю!")
            chats[str(message.chat.id)] = randint(chats2[str(message.chat.id)]["min"], chats2[str(message.chat.id)]["max"])
            await message.answer("Я загадал новое число, попробуйте угадать :)")

    

@dp.message(Command("start", "again"), F.chat.type == "private")
async def start_handler(message):
    are_in_chats2(message.chat.id)
    await ugadayka_start(message)


@dp.message(Command("help"), F.chat.type == "private")
async def ugadayka_help(message):
    are_in_chats2(message.chat.id)
    print(f"chat {message.chat.id} need help")
    await message.reply("Это бот числовая угадайка, я загадал для вас число, а вы пробуйте отгадать.\n" \
                        "Если вы хотите попробовать заново введите комманды /start либо /again\n" \
                        "Вы так же можете ввести минимальное значение числа которое я буду загадывать коммандой /min\n" \
                        "Или вы так же можете ввести максимальное значение числа которое я буду загадывать коммандой /max\n")  
    print(f"now chat {message.chat.id} don't need help")

@dp.message(Command("min"), F.chat.type == "private")
async def min_handler(message, command: CommandObject):
    try:
        num = int(command.args)
    except ValueError, TypeError:
        await message.reply("Вы ввели не число")
    else:
        set_min(message.chat.id, num)
        await message.reply(f"Минимальное значение {num} успешно установлено")

@dp.message(Command("max"), F.chat.type == "private")
async def max_handler(message, command: CommandObject):
    try:
        num = int(command.args)
    except ValueError, TypeError:
        await message.reply("Вы ввели не число")
    else:
        set_max(message.chat.id, num)
        await message.reply(f"Максимальное значение {num} успешно установлено")



@dp.message(F.chat.type == "private")
async def ugadayka_handler(message):
    are_in_chats2(message.chat.id)
    await ugadayka(message, message.text)


@dp.message(Command("ugadayka"), F.chat.type.in_({"group", "supergroup"}))  # для сообщений только в группах только коммандой /ugadayka
async def ugadayka_command(message, command: CommandObject):
    are_in_chats2(message.chat.id)
    if command.args is None:
        await message.answer("Вы не ввели ничего в аргументы!")
        return
    
    parts = (command.args).split()  # разделяет аргументы для проверок там где агрументов больше одного, например /ugadayka max 100
    
    if command.args == "start" or command.args == "again":
        await ugadayka_start(message)
    elif command.args == "help":
        await message.answer("Поскольку вы находитесь в чате все комманды нужно прописывать так: \n" \
                            "/ugadayka <комманда> (комманда без знакак /)")
        await ugadayka_help(message)
    elif parts[0] == "min":
        if len(parts) == 2:
            try:
                num = int(parts[1])
            except ValueError, TypeError:
                await message.reply("Вы ввели в аргументы не число, попробуйте снова")
            else:
                set_min(message.chat.id, num)
                await message.reply(f"Минимальное значение {num} успешно установлено")
        else:
            await message.reply(f"После комманды min должен стоять всего 1 целочисленный аргумент")
    elif parts[0] == "max":
        if len(parts) == 2:
            try:
                num = int(parts[1])
            except ValueError, TypeError:
                await message.reply("Вы ввели в аргументы не число, попробуйте снова")
            else:
                set_max(message.chat.id, num)
                await message.reply(f"Максимальное значение {num} успешно установлено")
        else:
            await message.reply(f"После комманды max должен стоять всего 1 целочисленный аргумент")
    else:
        await ugadayka(message, command.args)


@dp.shutdown()
async def save_database():  # сохраняет данные двух файлов при выключении бота
    with open("chats.json", "w", encoding='utf-8') as f:
        json.dump(chats, f)
    with open("chats2.json", "w", encoding='utf-8') as file:
        json.dump(chats2, file)

if __name__ == "__main__":
    dp.run_polling(bot)