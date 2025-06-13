import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QFrame, QListWidget, QGridLayout)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap


class TextAdventureGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RobinZone: adventure island")
        self.setGeometry(0, 0, 1920, 1080)
        
        # Главный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной макет
        main_layout = QGridLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # Создаем 5 областей интерфейса
        self.create_inventory_area()    # 1
        self.create_scene_area()        # 2
        self.create_illustration_area() # 3
        self.create_map_area()          # 4
        self.create_status_area()      # 5
        
        # Добавляем области в макет
        main_layout.addWidget(self.inventory_frame, 0, 0, 2, 1)      # 1 - верхний левый
        main_layout.addWidget(self.scene_frame, 2, 1, 1, 1)          # 2 - центр
        main_layout.addWidget(self.illustration_frame, 0, 2, 2, 1)   # 3 - верхний правый
        main_layout.addWidget(self.map_frame, 2, 0, 1, 1)            # 4 - нижний левый
        main_layout.addWidget(self.status_frame, 2, 2, 1, 1)         # 5 - нижний правый
        
        # Настройка пропорций
        main_layout.setRowStretch(0, 2)
        main_layout.setRowStretch(1, 1)
        main_layout.setRowStretch(2, 2)
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 2)
        main_layout.setColumnStretch(2, 1)
        
        # Инициализация игровых данных
        self.init_game_data()
        self.update_ui()
    
    def create_inventory_area(self):
        """Создает область инвентаря (1)"""
        self.inventory_frame = QFrame()
        self.inventory_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.inventory_frame.setLineWidth(2)
        
        layout = QVBoxLayout(self.inventory_frame)
        
        title = QLabel("ИНВЕНТАРЬ")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        
        self.inventory_list = QListWidget()
        self.inventory_list.setStyleSheet("font-size: 14px;")
        
        layout.addWidget(title)
        layout.addWidget(self.inventory_list)
    
    def create_scene_area(self):
        """Создает область сцены и действий (2)"""
        self.scene_frame = QFrame()
        self.scene_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.scene_frame.setLineWidth(2)
        
        layout = QVBoxLayout(self.scene_frame)
        
        self.scene_text = QLabel()
        self.scene_text.setWordWrap(True)
        self.scene_text.setStyleSheet("font-size: 14px;")
        self.scene_text.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.actions_layout = QVBoxLayout()
        
        scroll_area = QWidget()
        scroll_area.setLayout(QVBoxLayout())
        scroll_area.layout().addWidget(self.scene_text)
        scroll_area.layout().addStretch(1)
        
        scroll = QWidget()
        scroll.setLayout(QVBoxLayout())
        scroll.layout().addWidget(scroll_area)
        scroll.layout().addLayout(self.actions_layout)
        
        layout.addWidget(scroll)
    
    def create_illustration_area(self):
        """Создает область иллюстрации (3)"""
        self.illustration_frame = QFrame()
        self.illustration_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.illustration_frame.setLineWidth(2)
        
        layout = QVBoxLayout(self.illustration_frame)
        
        title = QLabel("ИЛЛЮСТРАЦИЯ")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        
        self.illustration_label = QLabel()
        self.illustration_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.illustration_label.setMinimumSize(QSize(400, 400))
        
        layout.addWidget(title)
        layout.addWidget(self.illustration_label)
        layout.addStretch(1)
    
    def create_map_area(self):
        """Создает область карты (4)"""
        self.map_frame = QFrame()
        self.map_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.map_frame.setLineWidth(2)
        
        layout = QVBoxLayout(self.map_frame)
        
        title = QLabel("КАРТА МЕСТНОСТИ")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        
        self.map_label = QLabel()
        self.map_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.map_label.setMinimumSize(QSize(300, 300))
        
        layout.addWidget(title)
        layout.addWidget(self.map_label)
        layout.addStretch(1)
    
    def create_status_area(self):
        """Создает область статуса (5)"""
        self.status_frame = QFrame()
        self.status_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.status_frame.setLineWidth(2)
        
        layout = QVBoxLayout(self.status_frame)
        
        title = QLabel("СТАТУС")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        
        self.health_label = QLabel("Здоровье: 100/100")
        self.mood_label = QLabel("Настроение: Нормальное")
        self.hunger_label = QLabel("Голод: Удовлетворён")
        self.time_label = QLabel("Время: 08:00")
        self.day_label = QLabel("День 1 на острове")
        
        for label in [self.health_label, self.mood_label, self.hunger_label, self.time_label, self.day_label]:
            label.setStyleSheet("font-size: 14px;")
            layout.addWidget(label)
        
        layout.addStretch(1)
    
    def init_game_data(self):
        """Инициализация игровых данных"""
        self.inventory = ["Нож", "Фляга с водой", "Аптечка"]
        self.health = 100
        self.mood = "Нормальное"
        self.hunger = "Удовлетворён"
        self.time = "08:00"
        self.day = 1
        self.current_scene = "start"
        
        self.scenes = {
            "start": {
                "text": """Сознание возвращается медленно, сквозь густой туман боли.
  
  Вы лежите на мокром песке, и каждый вдох даётся с трудом. Голова раскалывается — будто внутри бьётся чугунное ядро, оставляя после каждого удара волны тошноты. Тело ноет: ссадины горят, будто обожжённые солнцем, а мышцы отзываются на движение тупой, выматывающей болью.
  
  Память пуста.
 
  Ни имени, ни того, как вы здесь оказались, — только белый шум в висках и навязчивое, животное чувство опасности. Желудок сводит судорогой от голода, но сильнее всего мучает жажда — горло пересохло настолько, что каждый глоток воздуха обжигает, как песок.
  
  Волны.
  
  Они накатывают ритмично, с шипящим шепотом, то и дело омывая ваши ноги ледяной пеной. Шум прибоя глухой, далёкий, будто доносящийся из другого мира. Ветер несёт с собой запах соли и чего-то чужого, дикого — этого острова, на котором вы теперь совершенно одни.""",
                "image": "beach.png",
                "map": "island_start.png",
                "actions": [
                    {"text": "Осмотреться вокруг", "target": "look_around"},
                    {"text": "Проверить карманы", "target": "check_pockets"},
                    {"text": "Пойти вглубь острова", "target": "go_inland"}
                ]
            },
            "look_around": {
                "text": "Вы видите пальмы с кокосами, джунгли начинающиеся в 100 метрах от берега, и какие-то обломки на песке вдалеке. Волны накатывают на берег, но ничего полезного не приносят.",
                "image": "beach_view.png",
                "map": "island_start.png",
                "actions": [
                    {"text": "Подойти к обломкам", "target": "go_to_debris"},
                    {"text": "Попробовать сбить кокос", "target": "get_coconut"},
                    {"text": "Вернуться к исходной точке", "target": "start"}
                ]
            }
        }
    
    def update_ui(self):
        """Обновление интерфейса на основе текущего состояния игры"""
        # Обновляем инвентарь
        self.inventory_list.clear()
        self.inventory_list.addItems(self.inventory)
        
        # Обновляем текущую сцену
        scene = self.scenes[self.current_scene]
        self.scene_text.setText(scene["text"])
        
        # Очищаем старые кнопки действий
        while self.actions_layout.count():
            item = self.actions_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Добавляем новые кнопки действий
        for action in scene["actions"]:
            btn = QPushButton(action["text"])
            btn.setStyleSheet("font-size: 14px; padding: 8px;")
            btn.clicked.connect(lambda _, t=action["target"]: self.change_scene(t))
            self.actions_layout.addWidget(btn)
        
        # Обновляем статус
        self.health_label.setText(f"Здоровье: {self.health}/100")
        self.mood_label.setText(f"Настроение: {self.mood}")
        self.hunger_label.setText(f"Голод: {self.hunger}")
        self.time_label.setText(f"Время: {self.time}")
        self.day_label.setText(f"День {self.day} на острове")
        
        # Здесь должны быть загрузки изображений, но для примера оставим пустые метки
        self.illustration_label.setText("[Иллюстрация: {}]".format(scene["image"]))
        self.map_label.setText("[Карта: {}]".format(scene["map"]))
    
    def change_scene(self, scene_id):
        """Переход к другой сцене"""
        self.current_scene = scene_id
        self.update_ui()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = TextAdventureGame()
    game.show()
    sys.exit(app.exec())