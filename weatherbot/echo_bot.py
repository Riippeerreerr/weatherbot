import asyncio
import json
import logging
from weatherbot.client_websocket import WssClient
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

LOG = logging.getLogger()
my_ch = logging.StreamHandler()
my_ch.setLevel(logging.DEBUG)
formatter_console = logging.Formatter(
    '%(asctime)s %(levelname) -10s %(name) -10s %(lineno) -5d  %(message)s'
)
my_ch.setFormatter(formatter_console)
LOG.setLevel(logging.INFO)
LOG.addHandler(my_ch)

API_TOKEN = '5596301670:AAHp8Zm0_Wjzal9Qcbzdys1x4D-efcutiEA'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")


@dp.message_handler(regexp='(^cat[s]?$|puss)')
async def cats(message: types.Message):
    with open('data/cats.jpg', 'rb') as photo:
        '''
        # Old fashioned way:
        await bot.send_photo(
            message.chat.id,
            photo,
            caption='Cats are here 😺',
            reply_to_message_id=message.message_id,
        )
        '''

        await message.reply_photo(photo, caption='Cats are here 😺')


button1 = InlineKeyboardButton(text="brasov", callback_data="brasov")
button2 = InlineKeyboardButton(text="bucuresti", callback_data="bucuresti")
button3 = InlineKeyboardButton(text="corbeanca", callback_data="corbeanca")
keyboard = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(button1).add(button2).add(button3)


@dp.message_handler(commands=['weather'])
async def weather(message: types.Message):
    # keyboard = InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(button1).add(button2).add(
    # button3)
    await message.reply('keyboard', reply_markup=keyboard)


# html markup telegram

async def on_wss_msg(message):
    LOG.info(message)
    msg = json.loads(message)
    name = msg.get("username")
    location = msg.get("location")
    chatID = msg.get("chatID")
    max_temp = msg.get("max temperature")
    precipitations = msg.get("precipitations")
    msg = (
        f'Buna ziua, <b>{name}</b>!\n'
        f'Vremea aleasa este pentru locatia <i>{location}</i>.\n'
        f'Maxima temperaturii de astazi va fi de {max_temp} grade.\n'
        f"Precipitatiile astazi {'vor' if precipitations else 'nu vor'} exista."
    )
    if chatID:
        await bot.send_message(chatID, msg, parse_mode="HTML")


@dp.callback_query_handler(text=["brasov", "bucuresti", "corbeanca"])
async def process_weather_callback(call: types.CallbackQuery):
    weather_json = WS.get_weather_msg(call.data, call.from_user.first_name, chat_id=call.from_user.id)
    await WS.ws_client.send(weather_json)


@dp.message_handler()
async def echo(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)

    await message.answer(message.text)


WS = WssClient(on_wss_msg)


def main():
    loop = asyncio.get_event_loop()
    loop.create_task(WS.start_wsclient())
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
