import telebot
from config import *
from logic import *

bot = telebot.TeleBot(TOKEN)

manager = DB_Map(DATABASE)
manager.create_user_table()
manager.create_settings_table()

# ---------- START / HELP ----------

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(
        message.chat.id,
        "Привет! Я бот, который показывает города на карте 🌍\n\n"
        "Напиши /help чтобы увидеть все команды."
    )

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(
        message.chat.id,
        "/remember_city <City> — сохранить город\n"
        "/show_my_cities — показать мои города\n"
        "/show_city — показать все города\n"
        "/set_color <color> — цвет маркеров\n\n"
        "Примеры:\n"
        "/remember_city Tokyo\n"
        "/set_color blue"
    )

# ---------- ПОКАЗАТЬ ВСЕ ГОРОДА ----------

@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    cities = manager.select_all_cities()
    if cities:
        path = manager.create_grapf('all_cities.png', cities, message.chat.id)
        bot.send_photo(message.chat.id, open(path, 'rb'))
    else:
        bot.send_message(message.chat.id, "В базе нет городов.")

# ----------  ----------

@bot.message_handler(commands=['remember_city'])
def handle_remember_city(message):
    user_id = message.chat.id
    city_name = message.text.split()[-1]
    if manager.add_city(user_id, city_name):
        bot.send_message(message.chat.id, f'Город {city_name} успешно сохранен!')
    else:
        bot.send_message(message.chat.id, 'Такого города я не знаю. Убедись, что он написан на английском!')

@bot.message_handler(commands=['show_my_cities'])
def handle_show_visited_cities(message):
    cities = manager.select_cities(message.chat.id)
    if cities:
        path = manager.create_grapf('1.png', cities, message.chat.id)
        bot.send_photo(message.chat.id, open(path,'rb'))
    else:
        bot.send_message(message.chat.id, 'У вас нет городов')
        
@bot.message_handler(commands=['show_country'])
def handle_show_country(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Используй: /show_country France")
        return

    country = parts[1]
    cities = manager.select_cities_by_country(country)

    if not cities:
        bot.send_message(message.chat.id, "Города не найдены.")
        return

    path = manager.create_grapf('country.png', cities, message.chat.id)
    bot.send_photo(message.chat.id, open(path, 'rb'))
# ---------- ЦВЕТ ----------

@bot.message_handler(commands=['set_color'])
def set_color_cmd(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Используй: /set_color red")
        return

    color = parts[1]
    manager.set_color(message.chat.id, color)
    bot.send_message(message.chat.id, f"Цвет маркеров установлен: {color}")

# ---------- RUN ----------

if __name__ == "__main__":
    bot.polling(none_stop=True)
