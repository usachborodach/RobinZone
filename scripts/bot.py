import os
import common
base_path = os.path.dirname(__file__)
SCENES = common.load_situations()
start_scene = 'nachalo'


#!/usr/bin/env python3.10
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from typing import Any, Optional, Dict, List
import logging
from pathlib import Path
import json

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GameEngine:
    def __init__(self):
        self.player_state: Dict[str, Any] = {
            "health": 100,
            "hunger": 0,
            "thirst": 0,
            "inventory": [],
        }
        self.current_scene = start_scene

    def get_scene(self, scene_id: str) -> Dict[str, Any]:
        """Возвращает данные сцены по ID"""
        return SCENES.get(scene_id, {})

    def update_state(self, changes: Optional[Dict[str, int]] = None) -> None:
        """Обновляет состояние игрока"""
        if changes:
            for key, value in changes.items():
                if key in self.player_state:
                    self.player_state[key] += value

    def get_status_text(self) -> str:
        """Возвращает текст с текущим состоянием игрока"""
        inventory = ", ".join(self.player_state["inventory"]) or "пусто"
        return (
            f"❤️ Здоровье: {self.player_state['health']}% | "
            f"🍗 Голод: {self.player_state['hunger']} | "
            f"💧 Жажда: {self.player_state['thirst']}\n"
            f"🎒 Инвентарь: {inventory}"
        )

# Пример данных сцен (замените своими)
# SCENES = {
#     "start": {
#         "text": "Вы очнулись на берегу необитаемого острова...",
#         "image": "assets/start.jpg",
#         "actions": [
#             {"text": "🔍 Осмотреться", "next": "look_around"},
#             {"text": "🌴 Идти к пальмам", "next": "palm_trees"}
#         ],
#         "state_change": {"thirst": 5}
#     },
#     "look_around": {
#         "text": "Вы видите обломки корабля и пещеру...",
#         "actions": [
#             {"text": "🚢 Исследовать обломки", "next": "shipwreck"},
#             {"text": "🕳️ Зайти в пещеру", "next": "cave_entrance"}
#         ]
#     }
# }

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    context.user_data["game"] = GameEngine()
    
    await update.message.reply_text(
        f"Привет, {user.first_name}! Ты попал на необитаемый остров. "
        "Тебе нужно выжить как можно дольше."
    )
    
    await show_scene(update, context)

async def show_scene(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает текущую сцену"""
    try:
        game = context.user_data["game"]
        scene = game.get_scene(game.current_scene)
        
        # Формируем текст сообщения
        full_text = f"{scene['text']}\n\n{game.get_status_text()}"
        
        # Создаем клавиатуру
        keyboard = []
        for action in scene.get("actions", []):
            if not isinstance(action.get("next"), str):
                logger.error(f"Invalid action: {action}")
                continue
            
            keyboard.append([
                InlineKeyboardButton(
                    text=action["text"],
                    callback_data=action["next"]
                )
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        # Определяем сообщение для ответа
        message = update.callback_query.message if update.callback_query else update.message
        
        # Отправляем контент
        if "image" in scene:
            image_path = Path(os.path.join(base_path, scene["image"]))
            print(image_path)
            print(os.path.abspath(image_path))
            if image_path.exists():
                with open(image_path, "rb") as photo_file:
                    if update.callback_query:
                        await message.edit_text(full_text)
                        await message.reply_photo(
                            photo=photo_file,
                            reply_markup=reply_markup
                        )
                    else:
                        await message.reply_photo(
                            photo=photo_file,
                            caption=full_text,
                            reply_markup=reply_markup
                        )
            else:
                logger.error(f"Image not found: {image_path}")
                await send_text_message(message, full_text, reply_markup)
        else:
            await send_text_message(message, full_text, reply_markup)
            
    except Exception as e:
        logger.error(f"Error in show_scene: {e}", exc_info=True)
        await send_fallback_message(update, context)

async def send_text_message(
    message: Message,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None
) -> None:
    """Универсальная отправка текстового сообщения"""
    try:
        if len(text) > 4096:  # Лимит Telegram
            text = text[:4000] + "... [сообщение сокращено]"
        
        await message.reply_text(
            text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Failed to send text: {e}")

async def handle_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий на кнопки"""
    try:
        query = update.callback_query
        await query.answer()
        
        game = context.user_data["game"]
        game.current_scene = query.data
        
        # Применяем изменения состояния
        scene = game.get_scene(game.current_scene)
        if "state_change" in scene:
            game.update_state(scene["state_change"])
        
        await show_scene(update, context)
    except Exception as e:
        logger.error(f"Error in handle_action: {e}", exc_info=True)
        await send_fallback_message(update, context)

async def send_fallback_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Аварийное сообщение при ошибках"""
    try:
        message = update.callback_query.message if update.callback_query else update.message
        await message.reply_text(
            "⚠️ Произошла ошибка. Попробуйте /start",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.critical(f"Critical failure: {e}")

def validate_scenes() -> None:
    """Проверяет сцены на валидность"""
    for scene_id, scene in SCENES.items():
        if "actions" in scene:
            for i, action in enumerate(scene["actions"]):
                if not isinstance(action.get("next"), str):
                    raise ValueError(f"Invalid 'next' in {scene_id} action {i}")
                if len(action["next"]) > 64:
                    raise ValueError(f"Callback too long in {scene_id} action {i}")

def main() -> None:
    """Запуск приложения"""
    try:
        validate_scenes()
        
        application = Application.builder().token("7875367168:AAHQzuShopUDhEJu4mruq7CweE9KSNfdFsk").build()
        
        # Регистрация обработчиков
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(handle_action))
        application.add_error_handler(error_handler)
        
        logger.info("Bot starting...")
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        logger.critical(f"Failed to start bot: {e}", exc_info=True)
        raise

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Глобальный обработчик ошибок"""
    logger.error("Exception while handling update:", exc_info=context.error)
    
    if isinstance(update, Update):
        if update.callback_query:
            await update.callback_query.message.reply_text("⚠️ Ошибка. Попробуйте еще раз.")
        elif update.message:
            await update.message.reply_text("⚠️ Произошла ошибка. Используйте /start")

if __name__ == "__main__":
    main()