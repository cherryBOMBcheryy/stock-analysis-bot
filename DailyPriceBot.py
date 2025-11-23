import json
import telebot
from telebot import types
from config.config import TELEGRAM_TOKEN, DATABASE_URL
from gigachat_promt import parse_user_query_with_giga, generate_analysis_with_giga
from prompts import PARSE_PROMPT
from analysis import plot_price_chart, compute_stats, query_prices, format_stats
from sqlalchemy import text

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(chat):
    text = ("Привет! Я бот аналитики акций технологических компаний за 2024 год.\n"
            "\n"
            "Ты можешь задать мне следующие типы запросов:\n"
            "- Покажи график цен AAPL за март\n"
            "- Сделай анализ uber за первое полугодие\n"
            "- Статистика MSFT с 1 апреля по 10 декабря")
    bot.send_message(chat.chat.id, text)

@bot.message_handler(func=lambda m: True, content_types=['text'])
def handle_text(message):

    chat_id = message.chat.id
    user_ms = message.text.strip()
    
    bot.send_chat_action(chat_id, 'typing')
    try:

        giga_resp = parse_user_query_with_giga(PARSE_PROMPT, user_ms)
        try:
            parsed = json.loads(giga_resp)
        except Exception:
            cleaned = giga_resp.strip().strip('`')
            parsed = json.loads(cleaned)
    except Exception as e:
        bot.send_message(chat_id, f"К сожалению, не могу обработать ваш запрос( \nПопробуйте еще раз!")
        return
    
    # Извлечь поля
    aim = parsed.get('Aim')
    ticker = parsed.get('ticker')
    start_date = parsed.get('start_date')
    end_date = parsed.get('end_date')

    try:
        df = query_prices(DATABASE_URL, ticker, start_date=start_date, end_date=end_date)
    except:
        bot.send_message(chat_id, f"К сожалению произошла ошибка, повторите попытку еще раз ((")
        return

    if df is None or df.empty:
        bot.send_message(chat_id, "Данные за указанный период / тикер не найдены.")
        return

    if aim == 'график':
        try:
            img_buf = plot_price_chart(df)
        except Exception as e:
            bot.send_message(chat_id, f"Ошибка построения графика: {e}")
            return
        bot.send_photo(chat_id, img_buf)
        stats = compute_stats(df)
        bot.send_message(chat_id, generate_analysis_with_giga(stats))
    
    elif aim == 'статистика':
        stats = compute_stats(df)
        bot.send_message(chat_id, format_stats(stats))
        bot.send_message(chat_id, generate_analysis_with_giga(stats))



bot.polling(none_stop=True)