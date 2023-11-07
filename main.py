import telebot
from settings import BOT_TOKEN, preview_text, hello_text
from handlers import *
import json

bot = telebot.TeleBot(BOT_TOKEN)
file_users_path = "users.json"

# help command
@bot.message_handler(commands=['help'])
def command_help(message):
    handle_help(message, bot)
    

# start command
@bot.message_handler(commands=['start'])
def on_start(message):
    user_data = {
        "first_name": message.from_user.first_name,
        "last_name": message.from_user.last_name,
        "username": f"@{message.from_user.username}",
        "chat_id": message.chat.id
    }
    with open(file_users_path, "r") as file:
        users_list = json.load(file)
        # if len(users_list) < 4: users_list = []
        
    # Добавляем данные нового пользователя в список
    users_list.append(user_data)
    
    # Перемещаем указатель файла на начало файла,
    # чтобы перезаписать его новыми данными
    # file.seek(0)
    
    # Запись новых данных в файл в формате JSON
    with open(file_users_path, "w") as file:
        json.dump(users_list, file, ensure_ascii=False, indent=4)
    
    # Очищаем оставшиеся данные после предыдущего содержимого файла,
    # если новые данные меньше по размеру
    # file.truncate()




    # with open("users.txt", "a") as file:
    #     file.write("{" + f"'first_name': '{message.from_user.first_name}', 'last_name': {message.from_user.last_name}', 'username': '@{message.from_user.username}', 'chat_id': '{message.chat.id}'" + "},\n")
    handle_start(message, bot)
    print(f"{preview_text}starting chat with: {message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username} {message.chat.id}")

# oder command
@bot.message_handler(commands=['order'])
def on_order(message):
    print(f"{preview_text}starting order: {message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username} {message.chat.id}")
    handle_order(message, bot)
    

@bot.callback_query_handler(func=lambda call: user_states.get(call.message.chat.id) == 'AWAITING_ITEM_SELECTION')
def selected_order_callback(message):
    callback_inline(message, bot)
    # print(f"{preview_text}await items from: {message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username} {message.chat.id}")

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'AWAITING_QUANTITY')
def count_confirmation(message):
    handle_quantity(message, bot)

# await address
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'AWAITING_ADDRESS')
def handle_await_address(message):
    handle_address(message, bot)
# if anything changed wrong:
@bot.callback_query_handler(func=lambda call: user_states.get(call.message.chat.id) == 'AWAITING_CHANGE')
def handle_change_handler(message):
    handle_change(message, bot)
# confirm address
@bot.callback_query_handler(func=lambda call: user_states.get(call.message.chat.id) == 'AWAITING_CONFIRMATION')
def handle_true_confirmation(message):
    handle_confirmation(message, bot)


if __name__ == '__main__':
    print(hello_text)
    bot.polling(none_stop=True)