import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from config import BOT_TOKEN
from database import Database

# Инициализируем базу данных
db = Database()

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Создаем клавиатуру с кнопками
def get_main_keyboard():
    keyboard = [
        ["📝 Создать заметку", "📋 Мои заметки"],
        ["🗑️ Удалить все", "ℹ️ Помощь"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Функция для команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет сообщение когда получена команда /start"""
    user = update.effective_user
    # Добавляем пользователя в базу данных
    db.add_user(user.id, user.username, user.first_name)

    await update.message.reply_html(
        f"Привет {user.mention_html()}! 👋\n"
        f"Я бот для заметок и напоминаний.\n\n"
        f"Просто нажимай на кнопки ниже чтобы управлять заметками!",
        reply_markup=get_main_keyboard()
    )

# Функция для обработки кнопки "Создать заметку"
async def create_note_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Начинает процесс создания заметки"""
    await update.message.reply_text(
        "Напиши текст заметки и я её сохраню:",
        reply_markup=ReplyKeyboardRemove()
    )
    # Сохраняем состояние - пользователь собирается создать заметку
    context.user_data['awaiting_note'] = True

# Функция для обработки текста заметки
async def save_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Сохраняет заметку от пользователя"""
    if context.user_data.get('awaiting_note'):
        user_id = update.effective_user.id
        note_text = update.message.text
        
        # Добавляем заметку в базу данных
        note_id = db.add_note(user_id, note_text)
        
        # Сбрасываем состояние
        context.user_data['awaiting_note'] = False
        
        await update.message.reply_text(
            f"✅ Заметка сохранена!\n\n{note_text}",
            reply_markup=get_main_keyboard()
        )
    else:
        # Если пользователь просто написал текст без контекста
        await update.message.reply_text(
            "Используй кнопки ниже для управления заметками 👇",
            reply_markup=get_main_keyboard()
        )

# Функция для кнопки "Мои заметки"
async def show_notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает все заметки пользователя"""
    user_id = update.effective_user.id
    
    notes = db.get_notes(user_id)
    
    if not notes:
        await update.message.reply_text(
            "📭 У тебя пока нет заметок.\nНажми 'Создать заметку' чтобы добавить первую!",
            reply_markup=get_main_keyboard()
        )
        return
    
    notes_list = "\n".join([f"• {content}" for note_id, content, created_at in notes])
    await update.message.reply_text(
        f"📖 Твои заметки ({len(notes)} шт.):\n\n{notes_list}",
        reply_markup=get_main_keyboard()
    )

# Функция для кнопки "Удалить все"
async def clear_notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Удаляет все заметки пользователя"""
    user_id = update.effective_user.id
    
    deleted_count = db.clear_notes(user_id)
    if deleted_count > 0:
        await update.message.reply_text(
            f"🗑️ Все заметки ({deleted_count} шт.) удалены!",
            reply_markup=get_main_keyboard()
        )
    else:
        await update.message.reply_text(
            "ℹ️ У тебя нет заметок для удаления.",
            reply_markup=get_main_keyboard()
        )

# Функция для кнопки "Помощь"
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает справку"""
    await update.message.reply_text(
        "ℹ️ **Помощь по боту:**\n\n"
        "• **Создать заметку** - добавляет новую заметку\n"
        "• **Мои заметки** - показывает все твои заметки\n"
        "• **Удалить все** - очищает все заметки\n\n"
        "Просто нажимай на кнопки - всё интуитивно понятно! 😊",
        reply_markup=get_main_keyboard()
    )

# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает текстовые сообщения"""
    text = update.message.text
    
    if text == "📝 Создать заметку":
        await create_note_start(update, context)
    elif text == "📋 Мои заметки":
        await show_notes(update, context)
    elif text == "🗑️ Удалить все":
        await clear_notes(update, context)
    elif text == "ℹ️ Помощь":
        await help_command(update, context)
    else:
        # Если это не команда, проверяем, не ожидаем ли мы заметку
        await save_note(update, context)

def main() -> None:
    """Запуск бота"""
    # Создаем Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Добавляем обработчик текстовых сообщений (для кнопок)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()