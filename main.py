import asyncio
import logging
import os 
import re 
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher,types,F
from aiogram.filters import Command
from aiogram.fsm.state import State,StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup,KeyboardButton,WebAppData
from aiogram.fsm.storage.memory import MemoryStorage

#загружаем переменные из env 
load_dotenv()
#настройка
Token = os.getenv('bot_token')
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

#проверяем загруженны ли переменные
if not Token:
    raise ValueError("бот токен не найден")
if not ADMIN_CHAT_ID:
    raise ValueError("ADMIN_CHAT_ID не найден в файле env")

ADMIN_CHAT_ID = int(ADMIN_CHAT_ID)

#настройка логирования 
#левел это короче уровень на который мы настраеваем наш файл
logging.basicConfig(level=logging.INFO)
logger =  logging.getLogger(__name__)
bot = Bot(token=Token)
storage = MemoryStorage()
dp = Dispatcher(storage = storage)

courses = {
    'python':{
        "description":"проф программирование для подростков",
        "price":"7к рублей в меесяц",
        "duration":"4 месяцов",
        "lessons":"32 урока"
    },
    'роблокс':{
        "description":"создание игр в роблокс студио",
        "price":"5к рублей в меесяц",
        "duration":"5 месяцов",
        "lessons":"28 урока"
    }
}

class Form(StatesGroup):
    course=State()
    parent_name=State()
    child_name = State()
    contact = State()
    age = State()

def m_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="записаться на курсы")],
            [KeyboardButton(text="о курсах")],
            [KeyboardButton(text="контакты")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

@dp.message(Command("start"))
async def start(message: types.Message,state:FSMContext):
    await state.clear()
    welcome_text = "здравствуйте"
    await message.answer(welcome_text,parse_mode="Markdown",reply_markup=m_keyboard())

@dp.message(F.text=="записаться на курсы")
async def zapisnacourse(message: types.Message,state:FSMContext):
    start_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="python")],
            [KeyboardButton(text="роблокс")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("отлично,давайте разберем курсы для вашего ребенка",parse_mode="Markdown",reply_markup=start_keyboard)
    await state.set_state(Form.course)

@dp.message(F.text=="о курсах")
async def about_corses(message: types.Message):
    courses_text=(
    '----python\n\n'
        "описание: программирование для подростков\n"
        "цена: 7к рублей в меесяц\n"
        "продолжительность: 4 месяца\n"
        "кол-во уроков: 32 урока\n"
    
    '----роблокс\n\n'
    "описание создание игр в роблокс студио\n"
    "цена 5к рублей в меесяц\n"
    "продолжительность 5 месяца\n"
    "кол-во уроков: 28 урока\n"
    )
    await message.answer(courses_text,parse_mode="Markdown")

@dp.message(F.text=="контакты")
async def contacts(message:types.Message):
    contacts_text=(
        "*контакты*\n"
        "*препод:Александр*\n"
        "*номер телефона:+79126001423*\n"
        "*емейл:sapasm18gmail.com*\n"
        "*рабочее время:\n*"
        "*пн-пт:10:00-19:00*\n"
        "*cб-вс:14:00-19:00*\n"
    )
    await  message.answer(contacts_text,parse_mode="Markdown")

@dp.message(Form.course,F.text.in_(courses.keys()))
async def choose_course(message:types.Message,state:FSMContext):
    course = message.text
    course_info = courses[course]
    await state.update_data(course = course)

    course_text=(
        f"{course_info}\n\n"
        f"{course_info['description']}\n\n"
        f"стоимость:{course_info['price']}\n\n"
        f"продолжительность:{course_info['duration']}\n\n"
        f"количество уроков:{course_info['lessons']}\n\n"
        "теперь напишите пожалуйста *ваша имя(родителя)*"
    )

    await message.answer(course_text,parse_mode="Markdown",reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Form.parent_name)

@dp.message(Form.course)
async def wrong_answer(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="python")],
            [KeyboardButton(text="роблокс")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("выберите один из курсов",reply_markup = keyboard)
    

@dp.message(Form.parent_name)
async def parent_name(message:types.Message,state:FSMContext):
    if len(message.text.strip())<=2:
        await message.answer("введите корректное имя")
        return
    await state.update_data(parent_name = message.text.strip())
    await message.answer("введите: *имя ребенка*",parse_mod = "Markdown")
    await state.set_state(Form.child_name)


@dp.message(Form.child_name)
async def child_name(message:types.Message,state:FSMContext):
    if len(message.text.strip())<=2:
        await message.answer("введите корректное имя")
        return
    
    await state.update_data(child_name = message.text.strip())
    await message.answer("введите возраст ребенка",parse_mode="Markdown")
    await state.set_state(Form.age)


@dp.message(Form.age)
async def age(message:types.Message,state:FSMContext):
    age_text = message.text.strip()
    numbers = re.findall(r'\d+',age_text)

    if not numbers:
        await message.answer("пожалуйста введите корректный возраст(от 6 до 18)")
        return

    age_number = int(numbers[0])

    if not (6<= age_number <=18):
        await message.answer("введите возраст цифрами")
        return
    
    await state.update_data(age=str(age_number))

    contact_kb = ReplyKeyboardMarkup(keyboard=[
       [KeyboardButton(text="отправьте свой телефон",request_contact=True)],
       [KeyboardButton(text="ввести вручную")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True)
    

    await message.answer(f'возраст {age_number} лет принят\n'
                         'теперь оставьте **контакт для связи**',
                         parse_mode="Markdown",
                         reply_markup=contact_kb)
    
    await state.set(Form.contact)

@dp.message(Form.contact,F.contact)
async def contact_from_button(message:types.Message,state:FSMContext):
    contact = message.contact
    phone_number = contact.phone_number

    if not phone_number.startswith('+'):
        phone_number = f'+{phone_number}'
    await process_contact (message,state,phone_number)   


@dp.message(Form.contact,F.text=="ввести вручную")
async def request_manual_contact(message:types.Message,state:FSMContext):
    await message.answer("введите свой номер или юз @username",
                         reply_markup=types.ReplyKeyboardRemove())
    

@dp.message(Form.contact)
async def manual_contact(message:types.Message,state:FSMContext):
    contact_info = message.text.strip()

    if len(contact_info) < 5:
        await message.answer("Пожалуйста введите корректный контакт")
        return
    

    await process_contact(message,state, contact_info)


async def process_contact(message:types.Message,state:FSMContext, contact_info):
    await state.update_data(contact = contact_info)
    data = await state.get_data()


    ad_text = (f"🎓 *НОВАЯ ЗАЯВКА!*\n\n"
        f"👨‍💼 *Родитель:* {data['parent_name']}\n"
        f"👶 *Ребёнок:* {data['child_name']}\n"
        f"🎂 *Возраст:* {data['age']} лет\n"
        f"💻 *Курс:* {data['course']}\n"
        f"📞 *Контакт:* {contact_info}\n\n"
        f"от: @{message.from_user.username or 'без юза'}\n"
        f"ID:{message.from_user.id}\n"
        f"⏰ *Время:* {message.date.strftime('%d.%m.%Y %H:%M')}\n\n"
        f"🎁 *Первое занятие - БЕСПЛАТНО!*")
    
    try:
        if ADMIN_CHAT_ID:
            try:
                await bot.send_message(
                    chat_id= ADMIN_CHAT_ID,
                    text=ad_text,
                    parse_mode="Markdown"
                )
                logger.info(f"заявка оправлена админу {ADMIN_CHAT_ID}")
            except Exception as e:
                logger.error(f"ошибка отправки админу:{e}")
        logger.info(f"Новая заявка от {data['parent_name']}на курс {data['course']}")
        main_keyboard = ReplyKeyboardMarkup(
            keyboard=[
            [KeyboardButton(text="записаться на курсы")],
            [KeyboardButton(text="о курсах")],
            [KeyboardButton(text="контакты")]],
        resize_keyboard=True,
    )
        await message.answer("✅ *Спасибо! Заявка отправлена!*\n\n"
            f"📋 *Данные заявки:*\n"
            f"• Курс: {data['course']}\n"
            f"• Родитель: {data['parent_name']}\n"
            f"• Ребёнок: {data['child_name']}\n"
            f"• Возраст: {data['age']} лет\n"
            f"• Контакт: {contact_info}\n\n"
            "🎯 *Я свяжусь с вами в ближайшее время для уточнения деталей.*\n\n"
            "🎁 *Напоминаю: первое пробное занятие - бесплатно!*",
            parse_mode="Markdown",
            reply_markup=main_keyboard)
        
        print("\n"+"="*50)
        print("НОВАЯ ЗАЯВКА")
        print(f"📋 *Данные заявки:*\n"
            f"• Курс: {data['course']}\n"
            f"• Родитель: {data['parent_name']}\n"
            f"• Ребёнок: {data['child_name']}\n"
            f"• Возраст: {data['age']} лет\n"
            f"• Контакт: {contact_info}\n\n"
            f"• юз: @{message.from_user.username or 'нету'}\n"
            f"• id: {message.from_user.id}")
        print("\n"+"="*50)
        
    except Exception as e :
        logger.error(f"ошибка обработки заявки:{e}")
        await message.answer()


    await state.clear()

@dp.message(Command("cancel"))
async def cancel_handler(message:types.Message,state:FSMContext):
        await state.clear()
        main=(ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="записаться на курсы")],
            [KeyboardButton(text="о курсах")],
            [KeyboardButton(text="контакты")]],
        resize_keyboard=True,
    ))
        await message.answer("заявка отменена",reply_markup=main)



@dp.message()
async def any_message (message:types.Message):
    main = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="записаться на курсы")],
            [KeyboardButton(text="о курсах")],
            [KeyboardButton(text="контакты")]],
        resize_keyboard=True,
    )
    await message.answer("*ДЛЯ ЗАПИСИ НА КУРС НАЖМИТЕ ПОЖАЛУЙСТА КНОПКУ*\n",
                         "*\первое пробное занятие - бесплатно\*\n\n",
                         reply_markup=main,
                         parse_mode="Markdown")
    


async def main():
    logger.info("бот запущен")
    await dp.start_polling(bot)

if __name__ == '__name__':
    asyncio.run(main())
