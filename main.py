from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Состояния анкеты
class RequestForm(StatesGroup):
    job_type = State()
    location = State()
    date = State()
    workers = State()
    contact = State()

@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    await message.reply("Привет! Я твой помощник. Напиши /help, если нужна рабочая сила.")

@dp.message_handler(commands=["help"])
async def help_cmd(message: types.Message):
    await message.reply("Какой тип работ вам нужен?")
    await RequestForm.job_type.set()

@dp.message_handler(state=RequestForm.job_type)
async def process_job_type(message: types.Message, state: FSMContext):
    await state.update_data(job_type=message.text)
    await message.reply("Где находится объект?")
    await RequestForm.next()

@dp.message_handler(state=RequestForm.location)
async def process_location(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)
    await message.reply("Когда нужно начать?")
    await RequestForm.next()

@dp.message_handler(state=RequestForm.date)
async def process_date(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text)
    await message.reply("Сколько человек требуется?")
    await RequestForm.next()

@dp.message_handler(state=RequestForm.workers)
async def process_workers(message: types.Message, state: FSMContext):
    await state.update_data(workers=message.text)
    await message.reply("Оставьте ваш номер телефона для связи:")
    await RequestForm.next()

@dp.message_handler(state=RequestForm.contact)
async def process_contact(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    data = await state.get_data()

    summary = (
        f"Заявка от {message.from_user.full_name}:\n"
        f"Тип работ: {data['job_type']}\n"
        f"Местоположение: {data['location']}\n"
        f"Дата начала: {data['date']}\n"
        f"Количество людей: {data['workers']}\n"
        f"Контакт: {data['contact']}"
    )

    await message.reply("Спасибо! Мы свяжемся с вами в ближайшее время.")
    await bot.send_message(message.chat.id, summary)
    await state.finish()