import telebot
from telebot import types
from settings import *

# Замените 'your_token_here' на токен вашего бота, который вы получили от BotFather
bot = telebot.TeleBot(BOT_TOKEN)
user_states = {}
user_orders = {}


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, 'Привет! Я ваш бот для заказа товаров. Напишите "Заказ", чтобы начать.')

@bot.message_handler(commands=['order'])
def handle_order(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    item1 = types.InlineKeyboardButton("Календарь (500 руб)", callback_data='calendar')
    item2 = types.InlineKeyboardButton("Наклейки (150 руб)", callback_data='stickers')
    item3 = types.InlineKeyboardButton("Картина (2000 руб)", callback_data='painting')
    item4 = types.InlineKeyboardButton("Часы (2000000 руб)", callback_data='clock')
    item5 = types.InlineKeyboardButton("Одежда", callback_data='clothing')
    item6 = types.InlineKeyboardButton("Брелок (500 руб)", callback_data='keychain')
    markup.add(item1, item2, item3, item4, item5, item6)
    
    bot.send_message(message.chat.id, "Выберите товар:", reply_markup=markup)
    user_states[message.chat.id] = 'AWAITING_ITEM_SELECTION'


@bot.callback_query_handler(func=lambda call: user_states.get(call.message.chat.id) == 'AWAITING_ITEM_SELECTION')
def callback_inline(call):
    if call.message:
        bot.send_message(call.message.chat.id, f'Вы выбрали {call.data}. Сколько единиц этого товара вы хотите заказать?')
        user_states[call.message.chat.id] = 'AWAITING_QUANTITY'
        user_orders[call.message.chat.id] = {'item': call.data}



@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'AWAITING_QUANTITY')
def handle_quantity(message):
    quantity = message.text
    bot.reply_to(message, f'Вы заказали {quantity} единиц(у). Спасибо за заказ!')
    del user_states[message.chat.id]  # Сброс состояния пользователя после завершения заказа
    user_orders[message.chat.id]['quantity'] = int(message.text)




@bot.message_handler(commands=['start'])
def handle_start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    item1 = types.InlineKeyboardButton("Календарь (500 руб)", callback_data='calendar')
    item2 = types.InlineKeyboardButton("Наклейки (150 руб)", callback_data='stickers')
    item3 = types.InlineKeyboardButton("Картина (2000 руб)", callback_data='painting')
    item4 = types.InlineKeyboardButton("Часы (2000000 руб)", callback_data='clock')
    item5 = types.InlineKeyboardButton("Одежда", callback_data='clothing')
    item6 = types.InlineKeyboardButton("Брелок (500 руб)", callback_data='keychain')
    markup.add(item1, item2, item3, item4, item5, item6)
    
    bot.send_message(message.chat.id, "Привет! Я ваш бот для заказа товаров. Выберите товар:", reply_markup=markup)

@bot.message_handler(commands=['help'])
def handle_help(message):
    help_text = """
    Доступные команды:
    /start - Начать общение с ботом
    /order - Показать меню товаров
    /help - Показать эту справку
    """
    bot.reply_to(message, help_text)


# @bot.callback_query_handler(func=lambda call: True)
# def callback_inline(call):
#     if call.message:
#         if call.data == 'clothing':
#             markup = types.InlineKeyboardMarkup(row_width=2)
#             item1 = types.InlineKeyboardButton("Наклейка (100 руб)", callback_data='sticker_clothing')
#             item2 = types.InlineKeyboardButton("Толстовка (1200 руб)", callback_data='hoodie')
#             markup.add(item1, item2)
            
#             bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                                   text="Выберите тип одежды:", reply_markup=markup)
#         else:
#             bot.send_message(call.message.chat.id, f'Вы выбрали {call.data}')


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'AWAITING_ADDRESS')
def handle_address(message):
    user_orders[message.chat.id]['address'] = message.text
    order = user_orders[message.chat.id]
    item, quantity, address = order['item'], order['quantity'], order['address']
    price_map = {'calendar': 500, 'stickers': 150, 'painting': 2000, 'clock': 2000000, 'clothing': 1200, 'keychain': 500}  # цены товаров
    total_price = price_map[item] * quantity
    summary = f'Вы заказали {item}: {quantity} шт на сумму {total_price} рублей на адрес {address}'
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Всё верно", callback_data="confirm"),
               types.InlineKeyboardButton("Изменить заказ", callback_data="change"))
    bot.send_message(message.chat.id, summary, reply_markup=markup)
    user_states[message.chat.id] = 'AWAITING_CONFIRMATION'


@bot.callback_query_handler(func=lambda call: user_states.get(call.message.chat.id) == 'AWAITING_CONFIRMATION')
def handle_confirmation(call):
    if call.data == 'confirm':
        order = user_orders[call.message.chat.id]
        item, quantity, address = order['item'], order['quantity'], order['address']
        confirmation = f'Заказ от пользователя {call.message.chat.id}: {item}, {quantity} шт, адрес: {address}'
        bot.send_message('@solnannn', confirmation)
        bot.send_message(call.message.chat.id, "Ваш заказ был подтвержден и отправлен. Спасибо!")
        # Удалить данные о заказе и состояние пользователя после подтверждения заказа
        del user_orders[call.message.chat.id]
        del user_states[call.message.chat.id]
    elif call.data == 'change':
        print()


if __name__ == '__main__':
    bot.polling(none_stop=True)
