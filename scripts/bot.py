#!/usr/bin/env python3.10
import logging
from collections.abc import Mapping
from typing import Any, Optional
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

import common
SCENES = common.load_situations()
start_scene = 'Начало'

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)



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
    try:
        game = context.user_data["game"]
        scene = game.get_scene(game.current_scene)
        
        # Логирование всей сцены для диагностики
        from pprint import pformat
        logger.debug(f"Preparing scene:\n{pformat(scene)}")
        
        # 1. Подготовка текста
        scene_text = scene.get("text", "NO TEXT PROVIDED")
        status_text = game.get_status_text()
        
        try:
            full_text = f"{scene_text}\n\n{status_text}"
            if len(full_text) > 4096:  # Лимит Telegram
                full_text = f"{scene_text[:3000]}...\n\n{status_text}"
        except Exception as e:
            logger.error(f"Text formatting error: {e}")
            full_text = "Ошибка формирования текста"

        # 2. Подготовка клавиатуры
        keyboard = []
        for action in scene.get("actions", []):
            try:
                if not isinstance(action.get("next"), str):
                    raise ValueError(f"Invalid 'next': {action.get('next')}")
                
                btn_text = action.get("text", "NO TEXT")
                if len(btn_text) > 64:  # Лимит Telegram для текста кнопки
                    btn_text = btn_text[:61] + "..."
                
                keyboard.append([InlineKeyboardButton(btn_text, callback_data=action["next"])])
            except Exception as e:
                logger.error(f"Invalid button: {action} - {e}")

        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None

        # 3. Определение сообщения для ответа
        message = update.callback_query.message if update.callback_query else update.message
        
        # 4. Отправка контента
        if update.callback_query:
            try:
                await message.edit_text(full_text, reply_markup=reply_markup)
            except Exception as e:
                logger.error(f"Can't edit message: {e}")
                await message.reply_text(full_text, reply_markup=reply_markup)
        else:
            await message.reply_text(full_text, reply_markup=reply_markup)

    except Exception as e:
        logger.critical(f"Fatal scene error: {e}", exc_info=True)
        if 'message' in locals():
            await message.reply_text("⚠️ Произошла ошибка. Попробуйте /start")
        raise


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