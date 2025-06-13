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


async def show_scene(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает текущую сцену с обработкой ошибок отправки фото"""
    game = context.user_data["game"]
    scene = game.get_scene(game.current_scene)
    print(scene)
    
    full_text = f"{scene['text']}\n\n{game.get_status_text()}"
    
    # Создаем клавиатуру
    keyboard = [
        [InlineKeyboardButton(action["text"], callback_data=action["next"])]
        for action in scene.get("actions", [])
            
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        # Определяем сообщение для ответа
        message = update.callback_query.message if update.callback_query else update.message
        
        if "image" in scene:
            try:
                # Открываем файл изображения в бинарном режиме
                with open(scene["image"], "rb") as photo_file:
                    if update.callback_query:
                        # Редактируем существующее сообщение
                        await message.edit_text(full_text)
                        await message.reply_photo(
                            photo=photo_file,
                            caption="Дополнительное изображение:",
                            reply_markup=reply_markup
                        )
                    else:
                        # Отправляем новое сообщение
                        await message.reply_photo(
                            photo=photo_file,
                            caption=full_text,
                            reply_markup=reply_markup
                        )
            except FileNotFoundError:
                logger.error(f"Image file not found: {scene['image']}")
                await message.reply_text(
                    "[Изображение не найдено]\n\n" + full_text,
                    reply_markup=reply_markup
                )
        else:
            if update.callback_query:
                await message.edit_text(
                    text=full_text,
                    reply_markup=reply_markup
                )
            else:
                await message.reply_text(
                    full_text,
                    reply_markup=reply_markup
                )
                
    except Exception as e:
        logger.error(f"Error in show_scene: {e}")
        await error_handler(update, context)


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