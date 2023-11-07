from telebot import types
from states import user_states, user_orders


products_data = {
    'calendar': {'name': 'Календарь', 'price': 500},
    'stickers': {'name': 'Наклейки', 'price': 150},
    'painting': {'name': 'Картина', 'price': 2000},
    'clock': {'name': 'Часы', 'price': 2000000},
    'sticker_clothing': {'name': 'Майка', 'price': 1200},
    'big_clothing': {'name': 'толстовка', 'price': 1212},  # предполагая, что выбрана толстовка
    'keychain': {'name': 'Брелок', 'price': 500}
}




def handle_help(message, bot):
    help_text = """
    Доступные команды:
    /start - Начать общение с ботом
    /order - Показать меню товаров
    /help - Показать эту справку
    """
    
    bot.reply_to(message, help_text)



# ░█████╗░░█████╗░███╗░░░███╗░█████╗░███╗░░██╗██████╗░░██████╗
# ██╔══██╗██╔══██╗████╗░████║██╔══██╗████╗░██║██╔══██╗██╔════╝
# ██║░░╚═╝██║░░██║██╔████╔██║███████║██╔██╗██║██║░░██║╚█████╗░
# ██║░░██╗██║░░██║██║╚██╔╝██║██╔══██║██║╚████║██║░░██║░╚═══██╗
# ╚█████╔╝╚█████╔╝██║░╚═╝░██║██║░░██║██║░╚███║██████╔╝██████╔╝
# ░╚════╝░░╚════╝░╚═╝░░░░░╚═╝╚═╝░░╚═╝╚═╝░░╚══╝╚═════╝░╚═════╝░

# order command
def handle_order(message, bot):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(f"{product_data['name']} ({product_data['price']} руб)", callback_data=product_key)
        for product_key, product_data in products_data.items() if product_key != 'clothing'
    ]
    clothing_button = types.InlineKeyboardButton("Одежда", callback_data='clothing')
    buttons.append(clothing_button)
    markup.add(*buttons)
    
    bot.send_message(message.chat.id, "Выберите товар:", reply_markup=markup)
    user_states[message.chat.id] = 'AWAITING_ITEM_SELECTION'


# start command
def handle_start(message, bot):
    handle_order(message, bot)

# receive count for order
def handle_quantity(message, bot):
    try:
        quantity = int(message.text)
    except ValueError:
        bot.reply_to(message, 'Пожалуйста, введите корректное число.')
        return  # Возвращаемся раньше, если пользователь не ввел корректное число

    item_key = user_orders[message.chat.id]['item']
    item_data = products_data[item_key]
    item_name = item_data['name']
    item_price = item_data['price']
    total_price = item_price * quantity

    bot.reply_to(message, f'Вы заказали {item_name}: {quantity} единиц(у). Стоимость заказа: {total_price} рублей. Теперь введите адрес доставки:')
    user_states[message.chat.id] = 'AWAITING_ADDRESS'  # Устанавливаем новое состояние пользователя
    user_orders[message.chat.id]['quantity'] = quantity  # Сохраняем количество в заказе пользователя







# ░█████╗░░█████╗░██╗░░░░░██╗░░░░░██████╗░░█████╗░░█████╗░██╗░░██╗░██████╗
# ██╔══██╗██╔══██╗██║░░░░░██║░░░░░██╔══██╗██╔══██╗██╔══██╗██║░██╔╝██╔════╝
# ██║░░╚═╝███████║██║░░░░░██║░░░░░██████╦╝███████║██║░░╚═╝█████═╝░╚█████╗░
# ██║░░██╗██╔══██║██║░░░░░██║░░░░░██╔══██╗██╔══██║██║░░██╗██╔═██╗░░╚═══██╗
# ╚█████╔╝██║░░██║███████╗███████╗██████╦╝██║░░██║╚█████╔╝██║░╚██╗██████╔╝
# ░╚════╝░╚═╝░░╚═╝╚══════╝╚══════╝╚═════╝░╚═╝░░╚═╝░╚════╝░╚═╝░░╚═╝╚═════╝░

# sending "вы выбрали" for choice users by /oder or /start commands
def callback_inline(call, bot):
    if call.message:
        if call.data == 'clothing':
            markup = types.InlineKeyboardMarkup(row_width=2)
            item1 = types.InlineKeyboardButton("Наклейка (100 руб)", callback_data='sticker_clothing')
            item2 = types.InlineKeyboardButton("Толстовка (1200 руб)", callback_data='hoodie')
            markup.add(item1, item2)
            
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Выберите тип одежды:", reply_markup=markup)
        else:
            product_name = products_data[call.data]['name']
            bot.send_message(call.message.chat.id, f'Вы выбрали {product_name}. Сколько единиц этого товара вы хотите заказать?')
            user_states[call.message.chat.id] = 'AWAITING_QUANTITY'
            user_orders[call.message.chat.id] = {'item': call.data}






def handle_address(message, bot):
    user_orders[message.chat.id]['address'] = message.text
    order = user_orders[message.chat.id]
    item_key, quantity, address = order['item'], order['quantity'], order['address']
    item_data = products_data[item_key]
    item_name = item_data['name']
    item_price = item_data['price']
    total_price = item_price * quantity
    summary = f'Вы заказали {item_name}: {quantity} шт на сумму {total_price} рублей на адрес {address}'
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Всё верно", callback_data="confirm"),
        types.InlineKeyboardButton("Изменить заказ", callback_data="change")
    )
    bot.send_message(message.chat.id, summary, reply_markup=markup)
    user_states[message.chat.id] = 'AWAITING_CONFIRMATION'


def handle_confirmation(call, bot):
    if call.data == 'confirm':
        order = user_orders[call.message.chat.id]
        item, quantity, address = order['item'], order['quantity'], order['address']
        confirmation = f'Заказ от пользователя {call.message.chat.id}: {item}, {quantity} шт, адрес: {address}'
        bot.send_message(call.message.chat.id, confirmation)
        print(call.message.chat.id)
        bot.send_message(call.message.chat.id, "Ваш заказ был подтвержден и отправлен. Спасибо!")
        # Удалить данные о заказе и состояние пользователя после подтверждения заказа
        del user_orders[call.message.chat.id]
        del user_states[call.message.chat.id]
    elif call.data == 'change':
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("Изменить товар", callback_data="change_item"),
            types.InlineKeyboardButton("Изменить количество", callback_data="change_quantity"),
            types.InlineKeyboardButton("Изменить адрес", callback_data="change_address")
        )
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Что вы хотите изменить?", reply_markup=markup)
        user_states[call.message.chat.id] = 'AWAITING_CHANGE'


# change choice 
def handle_change(call, bot):
    if call.data == 'change_item':
        handle_order(call.message, bot)
    elif call.data == 'change_quantity':
        bot.send_message(call.message.chat.id, 'Введите новое количество:')
        user_states[call.message.chat.id] = 'AWAITING_QUANTITY'
    elif call.data == 'change_address':
        bot.send_message(call.message.chat.id, 'Введите новый адрес:')
        user_states[call.message.chat.id] = 'AWAITING_ADDRESS'