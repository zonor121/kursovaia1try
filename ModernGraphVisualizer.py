import sys
import math
import heapq
import random
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QComboBox, QRadioButton, QGroupBox,
                               QFileDialog, QMessageBox, QTreeWidget, QTreeWidgetItem,
                               QSlider, QSplitter, QFrame, QProgressBar)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPainterPath, QPalette
import json

class ModernGraphVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Визуализация алгоритмов кратчайшего пути - Modern UI")
        self.setGeometry(100, 100, 1400, 900)
        
        # Настройка темной темы по умолчанию
        self.dark_mode = True
        self.setup_themes()
        self.apply_theme()
        
        # Данные графа
        self.graph = {}
        self.positions = {}
        self.original_positions = {}
        self.history = []
        self.current_history_index = -1
        self.pause = True
        self.algorithm_finished = False
        self.algorithm_result = ""
        self.has_negative_weights = False
        self.animation_lines = []
        
        # Настройки анимации
        self.animation_speed = 500
        self.zoom_level = 1.0
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        self.is_panning = False
        
        self.setup_ui()
        self.initialize_default_graph()
        self.initialize_algorithm()
        
        # Анимация для плавных переходов
        self.fade_animation = QPropertyAnimation(self)
        self.fade_animation.setDuration(300)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)

    def setup_themes(self):
        """Настройка цветовых тем"""
        self.themes = {
            'dark': {
                'bg': '#1e1e1e',
                'bg_secondary': '#2d2d2d',
                'bg_tertiary': '#3d3d3d',
                'text': '#ffffff',
                'text_secondary': '#cccccc',
                'accent': '#bb86fc',
                'accent_secondary': '#03dac6',
                'danger': '#cf6679',
                'warning': '#ffb74d',
                'success': '#4caf50',
                'border': '#444444',
                'canvas_bg': '#121212'
            },
            'light': {
                'bg': '#ffffff',
                'bg_secondary': '#f5f5f5',
                'bg_tertiary': '#eeeeee',
                'text': '#212121',
                'text_secondary': '#757575',
                'accent': '#6200ee',
                'accent_secondary': '#018786',
                'danger': '#b00020',
                'warning': '#ff9800',
                'success': '#4caf50',
                'border': '#e0e0e0',
                'canvas_bg': '#fafafa'
            }
        }
        self.current_theme = self.themes['dark']

    def apply_theme(self):
        """Применение текущей темы"""
        palette = QPalette()
        if self.dark_mode:
            palette.setColor(QPalette.Window, QColor(self.current_theme['bg']))
            palette.setColor(QPalette.WindowText, QColor(self.current_theme['text']))
            palette.setColor(QPalette.Base, QColor(self.current_theme['bg_secondary']))
            palette.setColor(QPalette.AlternateBase, QColor(self.current_theme['bg_tertiary']))
            palette.setColor(QPalette.ToolTipBase, QColor(self.current_theme['bg']))
            palette.setColor(QPalette.ToolTipText, QColor(self.current_theme['text']))
            palette.setColor(QPalette.Text, QColor(self.current_theme['text']))
            palette.setColor(QPalette.Button, QColor(self.current_theme['bg_secondary']))
            palette.setColor(QPalette.ButtonText, QColor(self.current_theme['text']))
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(self.current_theme['accent']))
            palette.setColor(QPalette.Highlight, QColor(self.current_theme['accent']))
            palette.setColor(QPalette.HighlightedText, Qt.black)
        else:
            palette.setColor(QPalette.Window, QColor(self.current_theme['bg']))
            palette.setColor(QPalette.WindowText, QColor(self.current_theme['text']))
            palette.setColor(QPalette.Base, QColor(self.current_theme['bg_secondary']))
            palette.setColor(QPalette.AlternateBase, QColor(self.current_theme['bg_tertiary']))
            palette.setColor(QPalette.ToolTipBase, QColor(self.current_theme['bg']))
            palette.setColor(QPalette.ToolTipText, QColor(self.current_theme['text']))
            palette.setColor(QPalette.Text, QColor(self.current_theme['text']))
            palette.setColor(QPalette.Button, QColor(self.current_theme['bg_secondary']))
            palette.setColor(QPalette.ButtonText, QColor(self.current_theme['text']))
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(self.current_theme['accent']))
            palette.setColor(QPalette.Highlight, QColor(self.current_theme['accent']))
            palette.setColor(QPalette.HighlightedText, Qt.white)
        
        QApplication.setPalette(palette)

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Верхняя панель управления
        self.create_top_panel(layout)
        
        # Разделитель для основной области
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Левая панель - холст
        self.canvas_widget = GraphCanvas(self)
        splitter.addWidget(self.canvas_widget)
        
        # Правая панель - управление и информация
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Нижняя панель статуса
        self.create_status_bar()
        
        # Настройка пропорций разделителя
        splitter.setSizes([1000, 400])

    def create_top_panel(self, layout):
        """Создание верхней панели управления"""
        top_frame = QFrame()
        top_frame.setMaximumHeight(80)
        top_frame.setStyleSheet(f"""
            QFrame {{
                background: {self.current_theme['bg_secondary']};
                border: 1px solid {self.current_theme['border']};
                border-radius: 8px;
                padding: 8px;
            }}
        """)
        
        top_layout = QHBoxLayout(top_frame)
        
        # Группа алгоритмов
        algo_group = QGroupBox("Алгоритм")
        algo_layout = QHBoxLayout(algo_group)
        
        self.dijkstra_radio = QRadioButton("Дейкстра")
        self.bellman_radio = QRadioButton("Беллман-Форд")
        self.dijkstra_radio.setChecked(True)
        
        algo_layout.addWidget(self.dijkstra_radio)
        algo_layout.addWidget(self.bellman_radio)
        top_layout.addWidget(algo_group)
        
        # Кнопки управления
        control_layout = QHBoxLayout()
        
        self.step_back_btn = self.create_styled_button("⏪ Назад", self.step_backward)
        self.step_forward_btn = self.create_styled_button("Вперед ⏩", self.step_forward)
        self.pause_btn = self.create_styled_button("▶️ Старт", self.toggle_pause)
        self.restart_btn = self.create_styled_button("🔄 Сброс", self.restart)
        
        control_layout.addWidget(self.step_back_btn)
        control_layout.addWidget(self.step_forward_btn)
        control_layout.addWidget(self.pause_btn)
        control_layout.addWidget(self.restart_btn)
        
        top_layout.addLayout(control_layout)
        
        # Кнопки загрузки
        file_layout = QHBoxLayout()
        
        self.load_btn = self.create_styled_button("📁 Загрузить", self.load_graph_from_file)
        self.random_btn = self.create_styled_button("🎲 Случайный", self.generate_random_graph)
        self.theme_btn = self.create_styled_button("🌙 Тема", self.toggle_theme)
        
        file_layout.addWidget(self.load_btn)
        file_layout.addWidget(self.random_btn)
        file_layout.addWidget(self.theme_btn)
        
        top_layout.addLayout(file_layout)
        
        layout.addWidget(top_frame)

    def create_styled_button(self, text, callback):
        """Создание стилизованной кнопки"""
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.current_theme['bg_tertiary']}, 
                    stop:1 {self.current_theme['bg_secondary']});
                border: 1px solid {self.current_theme['border']};
                border-radius: 6px;
                padding: 8px 12px;
                color: {self.current_theme['text']};
                font-weight: bold;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.current_theme['accent']}, 
                    stop:1 {self.current_theme['accent_secondary']});
                border: 1px solid {self.current_theme['accent']};
            }}
            QPushButton:pressed {{
                background: {self.current_theme['accent_secondary']};
            }}
        """)
        btn.clicked.connect(callback)
        return btn

    def create_right_panel(self):
        """Создание правой панели управления"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(15)
        
        # Группа выбора узлов
        node_group = QGroupBox("Выбор узлов")
        node_group.setStyleSheet(f"QGroupBox {{ color: {self.current_theme['accent']}; font-weight: bold; }}")
        node_layout = QVBoxLayout(node_group)
        
        start_layout = QHBoxLayout()
        start_layout.addWidget(QLabel("Старт:"))
        self.start_combo = QComboBox()
        start_layout.addWidget(self.start_combo)
        node_layout.addLayout(start_layout)
        
        end_layout = QHBoxLayout()
        end_layout.addWidget(QLabel("Конец:"))
        self.end_combo = QComboBox()
        end_layout.addWidget(self.end_combo)
        node_layout.addLayout(end_layout)
        
        self.apply_btn = self.create_styled_button("Применить выбор", self.apply_selection)
        node_layout.addWidget(self.apply_btn)
        
        right_layout.addWidget(node_group)
        
        # Группа скорости
        speed_group = QGroupBox("Скорость анимации")
        speed_group.setStyleSheet(f"QGroupBox {{ color: {self.current_theme['accent']}; font-weight: bold; }}")
        speed_layout = QVBoxLayout(speed_group)
        
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(0, 5)
        self.speed_slider.setValue(2)
        self.speed_slider.valueChanged.connect(self.change_speed)
        speed_layout.addWidget(self.speed_slider)
        
        self.speed_label = QLabel("Средняя скорость")
        speed_layout.addWidget(self.speed_label)
        
        right_layout.addWidget(speed_group)
        
        # Прогресс выполнения
        progress_group = QGroupBox("Прогресс выполнения")
        progress_group.setStyleSheet(f"QGroupBox {{ color: {self.current_theme['accent']}; font-weight: bold; }}")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {self.current_theme['border']};
                border-radius: 5px;
                text-align: center;
                background: {self.current_theme['bg_secondary']};
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.current_theme['accent']}, 
                    stop:1 {self.current_theme['accent_secondary']});
                border-radius: 3px;
            }}
        """)
        progress_layout.addWidget(self.progress_bar)
        
        right_layout.addWidget(progress_group)
        
        # Таблица результатов
        results_group = QGroupBox("Результаты")
        results_group.setStyleSheet(f"QGroupBox {{ color: {self.current_theme['accent']}; font-weight: bold; }}")
        results_layout = QVBoxLayout(results_group)
        
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["Вершина", "Расстояние", "Путь"])
        self.results_tree.setStyleSheet(f"""
            QTreeWidget {{
                background: {self.current_theme['bg_secondary']};
                color: {self.current_theme['text']};
                border: 1px solid {self.current_theme['border']};
                border-radius: 5px;
            }}
            QTreeWidget::item:selected {{
                background: {self.current_theme['accent']};
                color: black;
            }}
        """)
        results_layout.addWidget(self.results_tree)
        
        right_layout.addWidget(results_group)
        
        # Информация о графе
        info_group = QGroupBox("Информация о графе")
        info_group.setStyleSheet(f"QGroupBox {{ color: {self.current_theme['accent']}; font-weight: bold; }}")
        info_layout = QVBoxLayout(info_group)
        
        self.graph_info_label = QLabel("Граф не загружен")
        self.graph_info_label.setWordWrap(True)
        info_layout.addWidget(self.graph_info_label)
        
        right_layout.addWidget(info_group)
        
        right_layout.addStretch()
        
        return right_widget

    def create_status_bar(self):
        """Создание строки статуса"""
        self.status_bar = self.statusBar()
        self.status_label = QLabel("Готов к работе")
        self.status_bar.addWidget(self.status_label)
        
        # Стилизация статусбара
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background: {self.current_theme['bg_secondary']};
                color: {self.current_theme['text']};
                border-top: 1px solid {self.current_theme['border']};
            }}
        """)

    class GraphCanvas(QWidget):
        def __init__(self, parent):
            super().__init__(parent)
            self.parent = parent
            self.setMinimumSize(800, 600)
            self.setMouseTracking(True)
            
        def paintEvent(self, event):
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Фон
            painter.fillRect(self.rect(), QColor(self.parent.current_theme['canvas_bg']))
            
            if not self.parent.graph:
                # Сообщение при отсутствии графа
                painter.setPen(QColor(self.parent.current_theme['text']))
                painter.setFont(QFont("Arial", 16, QFont.Bold))
                painter.drawText(self.rect(), Qt.AlignCenter, "Граф не загружен\nНажмите 'Загрузить' или 'Случайный'")
                return
            
            self.draw_edges(painter)
            self.draw_nodes(painter)
            self.draw_legend(painter)
            
        def draw_edges(self, painter):
            for (u, v), weight in self.parent.graph.items():
                if u in self.parent.positions and v in self.parent.positions:
                    x1, y1 = self.parent.get_transformed_position(*self.parent.positions[u])
                    x2, y2 = self.parent.get_transformed_position(*self.parent.positions[v])
                    
                    # Определение стиля ребра
                    pen = QPen()
                    if weight < 0:
                        pen.setColor(QColor(self.parent.current_theme['danger']))
                        pen.setWidth(3)
                    elif (self.parent.final_path and u in self.parent.final_path and 
                          v in self.parent.final_path and 
                          abs(self.parent.final_path.index(u) - self.parent.final_path.index(v)) == 1):
                        pen.setColor(QColor(self.parent.current_theme['success']))
                        pen.setWidth(4)
                    else:
                        pen.setColor(QColor(self.parent.current_theme['text_secondary']))
                        pen.setWidth(2)
                    
                    painter.setPen(pen)
                    painter.drawLine(int(x1), int(y1), int(x2), int(y2))
                    
                    # Рисование веса ребра
                    if self.parent.zoom_level > 0.3:
                        self.draw_edge_weight(painter, x1, y1, x2, y2, weight)
        
        def draw_edge_weight(self, painter, x1, y1, x2, y2, weight):
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            offset_x = (y2 - y1) * 0.1
            offset_y = -(x2 - x1) * 0.1
            
            painter.setPen(QColor(self.parent.current_theme['text']))
            painter.setFont(QFont("Arial", max(8, int(10 * self.parent.zoom_level)), QFont.Bold))
            painter.drawText(int(mid_x + offset_x), int(mid_y + offset_y), str(weight))
        
        def draw_nodes(self, painter):
            for node, (orig_x, orig_y) in self.parent.positions.items():
                x, y = self.parent.get_transformed_position(orig_x, orig_y)
                
                # Определение цвета узла
                color = self.parent.get_node_color(node)
                brush = QBrush(QColor(color))
                
                # Рисование узла
                radius = max(15, int(20 * self.parent.zoom_level))
                painter.setBrush(brush)
                painter.setPen(QPen(QColor(self.parent.current_theme['border']), 2))
                painter.drawEllipse(int(x - radius), int(y - radius), radius * 2, radius * 2)
                
                # Текст узла
                painter.setPen(QColor("white" if color in ["green", "red", "blue", "purple", "yellow"] else "black"))
                painter.setFont(QFont("Arial", max(8, int(12 * self.parent.zoom_level)), QFont.Bold))
                painter.drawText(int(x - radius), int(y - radius), radius * 2, radius * 2, 
                               Qt.AlignCenter, node)
                
                # Отображение расстояния
                if (node in self.parent.distances and self.parent.distances[node] != float('inf') and 
                    self.parent.zoom_level > 0.5):
                    self.draw_node_distance(painter, x, y, node)
        
        def draw_node_distance(self, painter, x, y, node):
            dist_text = f"{self.parent.distances[node]:.1f}"
            painter.setPen(QColor(self.parent.current_theme['accent']))
            painter.setFont(QFont("Arial", max(6, int(10 * self.parent.zoom_level)), QFont.Bold))
            painter.drawText(int(x + 30 * self.parent.zoom_level), 
                           int(y - 30 * self.parent.zoom_level), dist_text)
        
        def draw_legend(self, painter):
            legend_x, legend_y = 20, 20
            legend_items = [
                ("Текущий узел", self.parent.current_theme['warning']),
                ("Посещенный", self.parent.current_theme['accent']),
                ("Кратчайший путь", self.parent.current_theme['success']),
                ("Старт", "#4CAF50"),
                ("Финиш", "#F44336"),
                ("Не посещенный", self.parent.current_theme['text_secondary'])
            ]
            
            painter.setFont(QFont("Arial", 10))
            
            for text, color in legend_items:
                # Квадратик легенды
                painter.setBrush(QBrush(QColor(color)))
                painter.setPen(QPen(QColor(self.parent.current_theme['border']), 1))
                painter.drawRect(legend_x, legend_y, 15, 15)
                
                # Текст легенды
                painter.setPen(QColor(self.parent.current_theme['text']))
                painter.drawText(legend_x + 25, legend_y + 12, text)
                legend_y += 25
            
            # Дополнительная информация
            if hasattr(self.parent, 'start_node') and hasattr(self.parent, 'end_node'):
                info_y = legend_y + 20
                algo_name = "Дейкстра" if self.parent.dijkstra_radio.isChecked() else "Беллман-Форд"
                
                painter.setFont(QFont("Arial", 11, QFont.Bold))
                painter.drawText(20, info_y, f"Алгоритм: {algo_name}")
                painter.drawText(20, info_y + 25, f"Старт: {self.parent.start_node}, Конец: {self.parent.end_node}")
                
                if self.parent.algorithm_finished and self.parent.algorithm_result:
                    result_color = self.parent.current_theme['success'] if "Найден путь" in self.parent.algorithm_result else self.parent.current_theme['danger']
                    painter.setPen(QColor(result_color))
                    result_text = self.parent.algorithm_result.split("(")[0] if "Найден путь" in self.parent.algorithm_result else self.parent.algorithm_result
                    painter.drawText(20, info_y + 50, result_text)
        
        def mousePressEvent(self, event):
            if event.button() == Qt.MiddleButton:
                self.parent.is_panning = True
                self.parent.pan_start_x = event.position().x()
                self.parent.pan_start_y = event.position().y()
                self.setCursor(Qt.ClosedHandCursor)
        
        def mouseMoveEvent(self, event):
            if self.parent.is_panning:
                dx = event.position().x() - self.parent.pan_start_x
                dy = event.position().y() - self.parent.pan_start_y
                self.parent.pan_offset_x += dx
                self.parent.pan_offset_y += dy
                self.parent.pan_start_x = event.position().x()
                self.parent.pan_start_y = event.position().y()
                self.update()
        
        def mouseReleaseEvent(self, event):
            if event.button() == Qt.MiddleButton:
                self.parent.is_panning = False
                self.setCursor(Qt.ArrowCursor)
        
        def wheelEvent(self, event):
            delta = event.angleDelta().y()
            if delta > 0:
                self.parent.zoom_level *= 1.1
            else:
                self.parent.zoom_level /= 1.1
            
            self.parent.zoom_level = max(0.1, min(5.0, self.parent.zoom_level))
            self.update()

    # Основные методы алгоритмов (аналогичные Tkinter версии)
    def get_node_color(self, node):
        if hasattr(self, 'start_node') and node == self.start_node:
            return "#4CAF50"  # Зеленый
        if hasattr(self, 'end_node') and node == self.end_node:
            return "#F44336"  # Красный
        if node == self.current_node:
            return self.current_theme['warning']  # Желтый/оранжевый
        if node in self.visited:
            return self.current_theme['accent']  # Акцентный цвет
        if self.final_path and node in self.final_path:
            return self.current_theme['success']  # Зеленый успеха
        return self.current_theme['text_secondary']  # Серый

    def get_transformed_position(self, x, y):
        center_x, center_y = self.canvas_widget.width() // 2, self.canvas_widget.height() // 2
        transformed_x = center_x + (x - center_x + self.pan_offset_x) * self.zoom_level
        transformed_y = center_y + (y - center_y + self.pan_offset_y) * self.zoom_level
        return transformed_x, transformed_y

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.current_theme = self.themes['dark'] if self.dark_mode else self.themes['light']
        self.apply_theme()
        self.theme_btn.setText("☀️ Светлая" if self.dark_mode else "🌙 Тёмная")
        self.canvas_widget.update()

    def change_speed(self, value):
        speeds = ["Очень медленно", "Медленно", "Средняя", "Быстро", "Очень быстро", "Максимум"]
        delays = [2000, 1000, 500, 200, 50, 0]
        self.animation_speed = delays[value]
        self.speed_label.setText(f"{speeds[value]} ({delays[value]}мс/шаг)")

    def initialize_default_graph(self):
        edges = [
            ('A', 'B', 4), ('B', 'C', 3), ('C', 'D', 5), 
            ('D', 'E', 2), ('E', 'F', 6), ('F', 'A', 4),
            ('B', 'E', 7), ('C', 'F', 3), ('A', 'D', 8),
            ('G', 'A', 2), ('G', 'B', 5), ('H', 'C', 4),
            ('H', 'D', 3), ('I', 'E', 6), ('I', 'F', 2),
            ('G', 'H', 8), ('H', 'I', 5), ('I', 'G', 7),
        ]
        
        self.graph = {}
        for u, v, weight in edges:
            self.graph[(u, v)] = weight
            self.graph[(v, u)] = weight
        
        center_x, center_y = 400, 300
        
        inner_nodes = ['A', 'B', 'C', 'D', 'E', 'F']
        for i, node in enumerate(inner_nodes):
            angle = 2 * math.pi * i / len(inner_nodes)
            self.positions[node] = (
                center_x + 120 * math.cos(angle),
                center_y + 120 * math.sin(angle)
            )
        
        middle_nodes = ['G', 'H', 'I']
        for i, node in enumerate(middle_nodes):
            angle = 2 * math.pi * i / len(middle_nodes) - math.pi/6
            self.positions[node] = (
                center_x + 250 * math.cos(angle),
                center_y + 250 * math.sin(angle)
            )
        
        self.start_node = 'G'
        self.end_node = 'D'
        self.original_positions = self.positions.copy()
        self.check_negative_weights()
        self.update_selection_comboboxes()
        self.update_graph_info()

    def update_graph_info(self):
        nodes_count = len(self.positions)
        edges_count = len(self.graph) // 2
        negative_weights = "Да" if self.has_negative_weights else "Нет"
        
        info_text = f"""Узлов: {nodes_count}
Ребер: {edges_count}
Отрицательные веса: {negative_weights}
Алгоритм: {'Дейкстра' if self.dijkstra_radio.isChecked() else 'Беллман-Форд'}"""
        
        self.graph_info_label.setText(info_text)

    def update_selection_comboboxes(self):
        if self.positions:
            nodes = list(self.positions.keys())
            self.start_combo.clear()
            self.end_combo.clear()
            self.start_combo.addItems(nodes)
            self.end_combo.addItems(nodes)
            
            if hasattr(self, 'start_node'):
                self.start_combo.setCurrentText(self.start_node)
            if hasattr(self, 'end_node'):
                self.end_combo.setCurrentText(self.end_node)

    def apply_selection(self):
        start = self.start_combo.currentText()
        end = self.end_combo.currentText()
        
        if not start or not end:
            QMessageBox.warning(self, "Предупреждение", "Выберите начальную и конечную точки")
            return
        
        if start == end:
            QMessageBox.warning(self, "Предупреждение", "Начальная и конечная точки не могут совпадать")
            return
        
        self.start_node = start
        self.end_node = end
        self.restart()

    def check_negative_weights(self):
        self.has_negative_weights = any(weight < 0 for weight in self.graph.values())
        return self.has_negative_weights

    def load_graph_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл с графом", "", 
            "Текстовые файлы (*.txt);;Все файлы (*)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            edges = []
            start_node = None
            end_node = None
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if line.upper().startswith('START'):
                    start_node = line.split()[1]
                    continue
                elif line.upper().startswith('END'):
                    end_node = line.split()[1]
                    continue
                
                parts = line.split()
                if len(parts) >= 3:
                    u, v = parts[0], parts[1]
                    try:
                        weight = float(parts[2])
                        edges.append((u, v, weight))
                    except ValueError:
                        print(f"Ошибка в весе ребра: {line}")
            
            if not edges:
                QMessageBox.critical(self, "Ошибка", "Файл не содержит корректных ребер графа")
                return
            
            self.graph = {}
            for u, v, weight in edges:
                self.graph[(u, v)] = weight
                self.graph[(v, u)] = weight
            
            self.calculate_positions()
            
            self.start_node = start_node if start_node else list(self.positions.keys())[0]
            self.end_node = end_node if end_node else list(self.positions.keys())[-1]
            
            self.original_positions = self.positions.copy()
            self.update_selection_comboboxes()
            
            has_negative = self.check_negative_weights()
            
            if has_negative and self.dijkstra_radio.isChecked():
                QMessageBox.warning(
                    self, "Предупреждение", 
                    "Обнаружены отрицательные веса!\n"
                    "Алгоритм Дейкстры не работает с отрицательными весами.\n"
                    "Автоматически переключен на алгоритм Беллмана-Форда."
                )
                self.bellman_radio.setChecked(True)
            
            self.restart()
            self.update_graph_info()
            
            message_text = f"Граф загружен!\nРебер: {len(edges)}\nУзлов: {len(self.positions)}\nСтарт: {self.start_node}, Конец: {self.end_node}"
            if has_negative:
                message_text += f"\n⚠️ Обнаружены отрицательные веса!"
            
            QMessageBox.information(self, "Успех", message_text)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл:\n{str(e)}")

    def calculate_positions(self):
        nodes = list(set([node for edge in self.graph.keys() for node in edge]))
        self.positions = {}
        
        center_x, center_y = 400, 300
        radius = min(300, 40 * len(nodes))
        
        for i, node in enumerate(nodes):
            angle = 2 * math.pi * i / len(nodes)
            self.positions[node] = (
                center_x + radius * math.cos(angle),
                center_y + radius * math.sin(angle)
            )
        
        self.original_positions = self.positions.copy()

    def generate_random_graph(self):
        nodes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        num_nodes = random.randint(6, 8)
        selected_nodes = nodes[:num_nodes]
        
        self.graph = {}
        
        # Создаем базовую связность
        for i in range(len(selected_nodes) - 1):
            u = selected_nodes[i]
            v = selected_nodes[i + 1]
            weight = random.randint(1, 10)
            self.graph[(u, v)] = weight
            self.graph[(v, u)] = weight
        
        # Добавляем случайные ребра
        num_extra_edges = random.randint(num_nodes, num_nodes + 3)
        for _ in range(num_extra_edges):
            u = random.choice(selected_nodes)
            v = random.choice(selected_nodes)
            if u != v and (u, v) not in self.graph:
                weight = random.randint(1, 10)
                if random.random() < 0.1:
                    weight = -random.randint(1, 3)
                self.graph[(u, v)] = weight
                self.graph[(v, u)] = weight
        
        self.calculate_positions()
        self.start_node = random.choice(selected_nodes)
        self.end_node = random.choice([n for n in selected_nodes if n != self.start_node])
        self.original_positions = self.positions.copy()
        self.update_selection_comboboxes()
        
        has_negative = self.check_negative_weights()
        if has_negative and self.dijkstra_radio.isChecked():
            self.bellman_radio.setChecked(True)
        
        self.restart()
        self.update_graph_info()
        
        QMessageBox.information(self, "Случайный граф", 
                               f"Сгенерирован случайный граф!\n"
                               f"Узлов: {len(selected_nodes)}\n"
                               f"Ребер: {len(self.graph)//2}\n"
                               f"Старт: {self.start_node}, Конец: {self.end_node}")

    # Методы алгоритмов (аналогичные Tkinter версии)
    def initialize_algorithm(self):
        self.distances = {node: float('inf') for node in self.positions}
        if hasattr(self, 'start_node'):
            self.distances[self.start_node] = 0
        self.visited = set()
        self.previous = {}
        self.current_node = None
        self.final_path = None
        self.algorithm_finished = False
        self.algorithm_result = ""
        
        if self.dijkstra_radio.isChecked():
            self.queue = [(0, self.start_node)]
        else:
            self.queue = [self.start_node]
        
        self.history = []
        self.current_history_index = -1
        self.save_state()
        self.update_results_table()

    def save_state(self):
        state = {
            'distances': self.distances.copy(),
            'visited': self.visited.copy(),
            'previous': self.previous.copy(),
            'current_node': self.current_node,
            'final_path': self.final_path.copy() if self.final_path else None,
            'algorithm_finished': self.algorithm_finished,
            'algorithm_result': self.algorithm_result
        }
        self.history = self.history[:self.current_history_index + 1]
        self.history.append(state)
        self.current_history_index = len(self.history) - 1

    def step_forward(self):
        if self.algorithm_finished:
            return
        
        if self.dijkstra_radio.isChecked():
            self.dijkstra_step()
        else:
            self.bellman_ford_step()
        
        self.save_state()
        self.update_progress()
        self.update_results_table()
        self.canvas_widget.update()

    def step_backward(self):
        if self.current_history_index > 0:
            self.current_history_index -= 1
            self.restore_state()
            self.update_progress()
            self.update_results_table()
            self.canvas_widget.update()

    def restore_state(self):
        state = self.history[self.current_history_index]
        self.distances = state['distances'].copy()
        self.visited = state['visited'].copy()
        self.previous = state['previous'].copy()
        self.current_node = state['current_node']
        self.final_path = state['final_path'].copy() if state['final_path'] else None
        self.algorithm_finished = state['algorithm_finished']
        self.algorithm_result = state['algorithm_result']

    def dijkstra_step(self):
        if not self.queue:
            self.finalize_algorithm()
            return
        
        current_distance, self.current_node = heapq.heappop(self.queue)
        
        if self.current_node in self.visited:
            return
        
        self.visited.add(self.current_node)
        
        for (u, v), weight in self.graph.items():
            if u == self.current_node and v not in self.visited:
                new_distance = current_distance + weight
                if new_distance < self.distances[v]:
                    self.distances[v] = new_distance
                    self.previous[v] = u
                    heapq.heappush(self.queue, (new_distance, v))
        
        if self.current_node == self.end_node:
            self.finalize_algorithm()

    def bellman_ford_step(self):
        if not hasattr(self, 'bellman_iteration'):
            self.bellman_iteration = 0
            self.bellman_nodes = list(self.positions.keys())
        
        if self.bellman_iteration >= len(self.positions):
            self.finalize_algorithm()
            return
        
        changed = False
        for (u, v), weight in self.graph.items():
            if self.distances[u] != float('inf') and self.distances[u] + weight < self.distances[v]:
                self.distances[v] = self.distances[u] + weight
                self.previous[v] = u
                changed = True
        
        self.bellman_iteration += 1
        self.current_node = None
        
        if not changed:
            self.finalize_algorithm()

    def finalize_algorithm(self):
        self.algorithm_finished = True
        self.current_node = None
        
        if self.end_node in self.previous:
            path = []
            current = self.end_node
            while current is not None:
                path.append(current)
                current = self.previous.get(current)
            self.final_path = path[::-1]
            total_distance = self.distances[self.end_node]
            self.algorithm_result = f"Найден путь: {' -> '.join(self.final_path)}\nОбщее расстояние: {total_distance}"
        else:
            self.final_path = None
            self.algorithm_result = "Путь не найден"
        
        self.update_results_table()
        QMessageBox.information(self, "Алгоритм завершен", self.algorithm_result)

    def toggle_pause(self):
        self.pause = not self.pause
        self.pause_btn.setText("⏸️ Пауза" if not self.pause else "▶️ Старт")
        
        if not self.pause:
            self.animation_timer = QTimer()
            self.animation_timer.timeout.connect(self.auto_step)
            self.animation_timer.start(self.animation_speed)

    def auto_step(self):
        if self.pause or self.algorithm_finished:
            if hasattr(self, 'animation_timer'):
                self.animation_timer.stop()
            return
        
        self.step_forward()

    def restart(self):
        if hasattr(self, 'animation_timer'):
            self.animation_timer.stop()
        
        self.pause = True
        self.pause_btn.setText("▶️ Старт")
        self.initialize_algorithm()
        self.update_progress()
        self.update_results_table()
        self.canvas_widget.update()

    def update_progress(self):
        if not self.positions:
            self.progress_bar.setValue(0)
            return
        
        total_nodes = len(self.positions)
        visited_nodes = len(self.visited)
        progress = int((visited_nodes / total_nodes) * 100)
        self.progress_bar.setValue(progress)

    def update_results_table(self):
        self.results_tree.clear()
        
        if not hasattr(self, 'distances'):
            return
        
        for node in sorted(self.positions.keys()):
            distance = self.distances[node]
            distance_text = f"{distance:.1f}" if distance != float('inf') else "∞"
            
            path = []
            current = node
            while current is not None:
                path.append(current)
                current = self.previous.get(current)
            path_text = " -> ".join(reversed(path)) if path else "-"
            
            item = QTreeWidgetItem([node, distance_text, path_text])
            self.results_tree.addTopLevelItem(item)
            
            if node == self.start_node:
                item.setBackground(0, QColor(self.current_theme['success']))
            elif node == self.end_node:
                item.setBackground(0, QColor(self.current_theme['danger']))
            elif node in self.visited:
                item.setBackground(0, QColor(self.current_theme['accent']))

def main():
    app = QApplication(sys.argv)
    
    # Настройка стиля приложения
    app.setStyle('Fusion')
    
    window = ModernGraphVisualizer()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()