#!/usr/bin/env python3.10
from telegram import Update, Message, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,  # <-- Добавлен этот импорт
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from typing import Any, Optional, Dict, List
import os
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


import common
SCENES = common.load_situations()
start_scene = 'nachalo'

# ========== ИГРОВОЙ ДВИЖОК ==========
class GameEngine:
    def __init__(self):
        self.player_state = {
            'health': 100,
            'hunger': 0,
            'thirst': 0,
            'inventory': [],
        }
        self.current_scene = start_scene

    def get_scene(self, scene_id: str) -> dict[str, Any]:
        """Возвращает данные сцены по ID"""
        return SCENES.get(scene_id, {})

    def update_state(self, changes: Optional[dict] = None) -> None:
        """Обновляет состояние игрока"""
        if changes:
            for key, value in changes.items():
                if key in self.player_state:
                    self.player_state[key] += value

    def get_status_text(self) -> str:
        """Возвращает текст с текущим состоянием игрока"""
        return (
            f"❤️ Здоровье: {self.player_state['health']}% | "
            f"🍗 Голод: {self.player_state['hunger']} | "
            f"💧 Жажда: {self.player_state['thirst']}\n"
            f"🎒 Инвентарь: {', '.join(self.player_state['inventory']) or 'пусто'}"
        )

# ========== СЦЕНЫ ИГРЫ ==========
# SCENES = {
#     "start": {
#         "text": (
#             "Вы очнулись на берегу необитаемого острова. Песок, пальмы и бескрайний океан. "
#             "Голова раскалывается, во рту пересохло. Что будете делать?"
#         ),
#         "image": "assets/start.jpg",
#         "actions": [
#             {"text": "🔍 Осмотреться вокруг", "next": "look_around"},
#             {"text": "🌴 Идти к пальмам", "next": "palm_trees"},
#             {"text": "💧 Искать воду", "next": "find_water"},
#         ],
#     },
#     "look_around": {
#         "text": (
#             "Осмотревшись, вы видите:\n"
#             "- Обломки корабля на берегу\n"
#             "- Группу кокосовых пальм\n"
#             "- Пещеру в скале неподалеку\n"
#             "- Следы, ведущие в джунгли"
#         ),
#         "image": "assets/look_around.jpg",
#         "actions": [
#             {"text": "🚢 Подойти к обломкам", "next": "shipwreck"},
#             {"text": "🥥 Собирать кокосы", "next": "get_coconuts"},
#             {"text": "🕳️ Исследовать пещеру", "next": "explore_cave"},
#         ],
#         "state_change": {"thirst": 5, "hunger": 5},
#     },
#     "get_coconuts": {
#         "text": (
#             "Вы сбиваете несколько кокосов. Один разбивается, но другой удается расколоть.\n"
#             "Сок утоляет жажду, мякоть немного унимает голод."
#         ),
#         "image": "assets/coconuts.jpg",
#         "actions": [
#             {"text": "↩️ Вернуться на берег", "next": "start"},
#             {"text": "🛠️ Сделать инструмент", "next": "make_tool"},
#         ],
#         "state_change": {"thirst": -20, "hunger": -15, "inventory": ["кокос"]},
#     },
#     # Добавьте другие сцены по аналогии
# }

# ========== ОБРАБОТЧИКИ ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    context.user_data["game"] = GameEngine()
    
    await update.message.reply_text(
        f"Привет, {user.first_name}! Ты попал на необитаемый остров. "
        "Тебе нужно выжить как можно дольше.\n"
        "Используй кнопки для выбора действий."
    )
    
    await show_scene(update, context)


async def show_scene(update: Update, context: ContextTypes.DEFAULT_TYPE):
    game = context.user_data["game"]
    scene = game.get_scene(game.current_scene)
    
    # Формируем текст сообщения
    status = game.get_status_text()
    full_text = f"{scene['text']}\n\n{status}"

    # Создаем клавиатуру
    keyboard = [
        [InlineKeyboardButton(action["text"], callback_data=action["next"])]
        for action in scene.get("actions", [])
    ]
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None

    # Определяем тип сообщения (новое/редактирование)
    is_callback = bool(update.callback_query)
    message = update.callback_query.message if is_callback else update.message

    try:
        if "image" in scene:
            await handle_scene_with_image(
                message=message,
                image_path=scene["image"],
                caption=full_text,
                reply_markup=reply_markup,
                is_editing=is_callback
            )
        else:
            await handle_text_only_scene(
                message=message,
                text=full_text,
                reply_markup=reply_markup,
                is_editing=is_callback
            )
    except Exception as e:
        logger.error(f"Scene error: {e}")
        await send_fallback_message(message, full_text)

async def handle_scene_with_image(
    message: Message,
    image_path: str,
    caption: str,
    reply_markup: Optional[InlineKeyboardMarkup],
    is_editing: bool
) -> None:
    """Обрабатывает сцену с изображением"""
    try:
        # Проверяем существование файла
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        with open(image_path, "rb") as photo_file:
            if is_editing:
                # Для редактирования: сначала меняем текст, затем отправляем фото
                await message.edit_text(caption, reply_markup=reply_markup)
                await message.reply_photo(photo=photo_file)
            else:
                # Для нового сообщения: отправляем фото с текстом
                await message.reply_photo(
                    photo=photo_file,
                    caption=caption,
                    reply_markup=reply_markup
                )
    except Exception as e:
        logger.error(f"Image sending failed: {e}")
        # Фолбэк на текстовое сообщение
        await handle_text_only_scene(message, caption, reply_markup, is_editing)

async def handle_text_only_scene(
    message: Message,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup],
    is_editing: bool
) -> None:
    """Обрабатывает текстовую сцену"""
    try:
        if is_editing:
            await message.edit_text(text, reply_markup=reply_markup)
        else:
            await message.reply_text(text, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Text message failed: {e}")
        await send_fallback_message(message, text)

async def send_fallback_message(message: Message, text: str) -> None:
    """Аварийный вариант отправки"""
    try:
        await message.reply_text(f"⚠️ Ошибка отображения сцены\n\n{text[:1000]}")
    except Exception as e:
        logger.critical(f"Complete message failure: {e}")


async def handle_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    game = context.user_data["game"]
    game.current_scene = query.data
    
    # Применяем изменения состояния
    scene = game.get_scene(game.current_scene)
    game.update_state(scene.get("state_change"))
    
    await show_scene(update, context)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок"""
    logger.error("Exception while handling an update:", exc_info=context.error)
    
    if update and hasattr(update, "effective_message"):
        await update.effective_message.reply_text(
            "Произошла ошибка. Игра перезапущена. Используйте /start"
        )

# ========== ЗАПУСК БОТА ==========
def main() -> None:
    """Запуск приложения"""
    application = Application.builder().token("7875367168:AAHQzuShopUDhEJu4mruq7CweE9KSNfdFsk").build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_action))
    application.add_error_handler(error_handler)
    
    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()