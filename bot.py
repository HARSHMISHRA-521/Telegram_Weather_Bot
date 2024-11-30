import logging
from telegram.ext import Updater, CommandHandler
import requests
import threading
from time import sleep
from app import create_app, db
from app.models import User
from app.config import Config

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app and database
app = create_app()

# Initialize Updater and Dispatcher
updater = Updater(token=Config.BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# List of cities to fetch weather for
CITIES = ["Delhi", "Mumbai", "Bangalore"]

# Command handlers
def start(update, context):
    chat_id = update.effective_chat.id
    welcome_message = (
        "🌦️ *Welcome to the Weather Bot!*\n\n"
        "Use the following commands to manage your weather updates:\n"
        "/subscribe - Subscribe to receive weather updates every minute.\n"
        "/unsubscribe - Unsubscribe from receiving weather updates."
    )
    context.bot.send_message(chat_id=chat_id, text=welcome_message, parse_mode='Markdown')

def subscribe(update, context):
    chat_id = update.effective_chat.id
    with app.app_context():
        user = User.query.filter_by(chat_id=str(chat_id)).first()
        if user:
            if user.subscribed:
                context.bot.send_message(chat_id=chat_id, text="You are already subscribed to weather updates.")
            else:
                user.subscribed = True
                db.session.commit()
                context.bot.send_message(chat_id=chat_id, text="You have subscribed to weather updates.")
        else:
            user = User(chat_id=str(chat_id), subscribed=True)
            db.session.add(user)
            db.session.commit()
            context.bot.send_message(chat_id=chat_id, text="You have subscribed to weather updates.")

def unsubscribe(update, context):
    chat_id = update.effective_chat.id
    with app.app_context():
        user = User.query.filter_by(chat_id=str(chat_id)).first()
        if user and user.subscribed:
            user.subscribed = False
            db.session.commit()
            context.bot.send_message(chat_id=chat_id, text="You have unsubscribed from weather updates.")
        else:
            context.bot.send_message(chat_id=chat_id, text="You are not subscribed.")

# Add handlers to dispatcher
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('subscribe', subscribe))
dispatcher.add_handler(CommandHandler('unsubscribe', unsubscribe))

# Function to fetch weather data for a city
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={Config.WEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        weather = data['weather'][0]['description']
        temp = data['main']['temp']
        return f"Current weather in {city}:\n{weather.capitalize()}, {temp}°C"
    except requests.RequestException as e:
        logger.error(f"Error fetching weather data for {city}: {e}")
        return f"Unable to fetch weather data for {city} at this time."

# Function to send weather updates
def send_weather_updates():
    while True:
        try:
            logger.info("Fetching subscribed users...")
            with app.app_context():
                subscribed_users = User.query.filter_by(subscribed=True).all()
                if not subscribed_users:
                    logger.info("No subscribed users found.")
                else:
                    logger.info(f"Found {len(subscribed_users)} subscribed users.")
                    weather_updates = [get_weather(city) for city in CITIES]
                    full_update = "\n\n".join(weather_updates)
                    for user in subscribed_users:
                        try:
                            updater.bot.send_message(chat_id=user.chat_id, text=full_update)
                            logger.info(f"Sent weather update to user {user.chat_id}")
                        except Exception as e:
                            logger.error(f"Failed to send message to {user.chat_id}: {e}")
            logger.info("Sleeping for 60 seconds before next update.")
        except Exception as e:
            logger.error(f"Unexpected error in send_weather_updates: {e}")
        finally:
            sleep(3600)  # Wait for 1 hr


# Start the bot
def main():
    # Start the weather update thread
    weather_thread = threading.Thread(target=send_weather_updates, daemon=True)
    weather_thread.start()

    # Start the bot
    updater.start_polling()
    logger.info("Bot started polling.")
    updater.idle()

if __name__ == '__main__':
    main()
