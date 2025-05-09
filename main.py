from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
import logging
import os

API_TOKEN = os.getenv('API_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', '123456789'))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class OrderForm(StatesGroup):
    city = State()
    service = State()
    phone = State()

main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add(KeyboardButton("Заказать помощь"))
main_kb.add(KeyboardButton("Частые вопросы"), KeyboardButton("Связаться с нами"))

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я помогу найти рабочих в твоём городе. Выбери действие:", reply_markup=main_kb)

@dp.message_handler(Text(equals="Заказать помощь"))
async def order_start(message: types.Message):
    await message.answer("В каком городе нужна помощь?")
    await OrderForm.city.set()

@dp.message_handler(state=OrderForm.city)
async def process_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer("Какая именно помощь нужна? (например: грузчики, разнорабочие)")
    await OrderForm.service.set()

@dp.message_handler(state=OrderForm.service)
async def process_service(message: types.Message, state: FSMContext):
    await state.update_data(service=message.text)
    await message.answer("Оставь свой номер телефона для связи")
    await OrderForm.phone.set()

@dp.message_handler(state=OrderForm.phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    data = await state.get_data()

    text = (
        f"Новый заказ:\n"
        f"Город: {data['city']}\n"
        f"Услуга: {data['service']}\n"
        f"Телефон: {data['phone']}"
    )
    await bot.send_message(ADMIN_ID, text)
    await message.answer("Спасибо! Мы скоро свяжемся с вами.", reply_markup=main_kb)
    await state.finish()

@dp.message_handler(Text(equals="Частые вопросы"))
async def faq(message: types.Message):
    await message.answer("Мы предоставляем рабочих по всей России. Работаем быстро, честно и без посредников. Оплата после выполнения работы.")

@dp.message_handler(Text(equals="Связаться с нами"))
async def contact(message: types.Message):
    await message.answer("Связь с нами: @ваш_ник или напиши сюда прямо.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)