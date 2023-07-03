from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage  # MemoryStorage - модуль для хранения состояний
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.handler import CancelHandler  # создан для вызова ошибки
from aiogram.dispatcher.middlewares import BaseMiddleware
import datetime
import os  # для получения переменных окружения
from dotenv import load_dotenv, find_dotenv  # для получения доступа к переменным окружения
from sqlite import db_start, create_user


load_dotenv(find_dotenv())  # находит в нашем проекте .env
bot = Bot(os.getenv('TOKEN'))

store = MemoryStorage()  # экземпляр класса MemoryStorage (для состояний)
dp = Dispatcher(bot=bot, storage=store)

greeting = '''
⚜️<b>Привет, <i>{}!</i></b>⚜️
Я бот, который улучшается с каждым днем. 
Пока я не обладаю большим функционалом, но все поправимо!)'''
navigation = '''
Вот мои команды:
    <b>/help</b> - узнать информацию о командах ⚙️
    <b>/suma</b> - просуммировать числа ➕
    <b>/id</b> - узнать свой id Telegram🕵️
    <b>/ip</b> - узнать свой сетевой адрес 🌐
    <b>/cancel</b> - Отмена текущей команды ❌*
'''


class ClientsStateGroup(StatesGroup):  # класс состояний
    count_sum = State()


class Middleware(BaseMiddleware):
    async def on_post_process_update(self, update: types.Update, result, data: dict) -> None:
        # если юзер отправит не текстовое сообщение, то предупреждаем его
        if 'text' not in dict(update['message']).keys():
            # если пользователь отправил нам не текстовое сообщение, то обрабатывать его мы и не будем
            await update.message.answer('Простите, но у меня нет обработчиков на такой формат данных...')
            CancelHandler()


def get_keyboard() -> types.ReplyKeyboardMarkup():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # resize_keyboard - клавиатура автоматически определяет красивый размер

    helps = types.KeyboardButton('/help')
    adder = types.KeyboardButton('/suma')
    tg_identifier = types.KeyboardButton('/id')
    id_identifier = types.KeyboardButton('/ip')

    return keyboard.add(helps).add(adder).add(tg_identifier).add(id_identifier)


def get_cancel() -> types.ReplyKeyboardMarkup():
    cancel = types.KeyboardButton('/cancel')
    return types.ReplyKeyboardMarkup(resize_keyboard=True).add(cancel)


async def date_on_info(_) -> None:
    my_name = await bot.get_me()
    print(my_name.first_name)
    print(f'Сервер запущен {datetime.datetime.today().strftime("%d %b %Yг. в %H:%M")}')
    await db_start()  # подключение БД


@dp.message_handler(commands=['start'])
async def start(message: types.Message) -> None:
    await message.delete()
    await message.answer(greeting.format(message.from_user.first_name) + navigation,
                         parse_mode='HTML',
                         reply_markup=get_keyboard())
    await create_user(message.from_user.id, message.from_user.username)


@dp.message_handler(commands=['help'])
async def get_info(message: types.Message) -> None:
    await message.delete()
    await message.answer(navigation, parse_mode='HTML')


@dp.message_handler(commands=['id'])
async def id_helper(message: types.Message) -> None:
    await message.delete()
    await message.answer(f'Твой ID:{message.from_user.id}')


@dp.message_handler(commands=['ip'])
async def ip_helper(message: types.Message) -> None:
    await message.delete()
    ikb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text='IP-API', url='http://ip-api.com/json'))
    await message.answer('Чтобы узнать IP перейди по ссылке ниже', reply_markup=ikb)


@dp.message_handler(commands=['suma'])
async def suma(message: types.Message):
    await ClientsStateGroup.count_sum.set()
    await message.delete()
    await message.answer('Введи числа через пробел', reply_markup=get_cancel())


# Данный handler сработает, если все предыдущие не сработали
@dp.message_handler()
async def simple_handler(message: types.Message) -> None:
    await message.answer('Простите, но у меня нет обработчиков на данное сообщение...', reply_markup=get_keyboard())


@dp.message_handler(state=ClientsStateGroup.count_sum)
async def count_sum(message: types.Message, state: FSMContext) -> None:
    if message.text == '/cancel':
        await state.finish()
        await message.delete()
        await message.answer('Операция отменена', reply_markup=get_keyboard())
        return
    try:
        string = [float(x) for x in message.text.split()]
    except ValueError:
        await message.answer('Ошибка в формате! Попробуй еще раз')
        return
    await state.finish()
    await message.answer(f'{" + ".join(message.text.split())} = {sum(string)}', reply_markup=get_keyboard())


dp.middleware.setup(Middleware())
executor.start_polling(dp, skip_updates=True, on_startup=date_on_info)  # skip_updates - не обрабатывать действия,
# сделанные пользователем, когда бот был в offline режиме;
# on_startup - функция, которая будет вызываться сразу же при включении сервера
