import sys
import math
import heapq
import random
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QComboBox, QRadioButton, QGroupBox,
    QFileDialog, QMessageBox, QTreeWidget, QTreeWidgetItem,
    QSlider, QSplitter, QFrame, QProgressBar, QButtonGroup,
    QGraphicsBlurEffect
)
from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPalette, QLinearGradient, QRadialGradient


class GradientLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.gradient_pos = 0.0
        self.setMinimumHeight(40)
        
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_gradient)
        self.animation_timer.start(50)
        
    def animate_gradient(self):
        self.gradient_pos = (self.gradient_pos + 0.02) % 1.0
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(max(0, self.gradient_pos - 0.5), QColor('#bb86fc'))
        gradient.setColorAt(self.gradient_pos, QColor('#03dac6'))
        gradient.setColorAt(min(1, self.gradient_pos + 0.5), QColor('#cf6679'))
        
        pen = QPen()
        pen.setBrush(QBrush(gradient))
        painter.setPen(pen)
        
        font = QFont("Segoe UI", 16, QFont.Bold)
        painter.setFont(font)
        
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())
        
        painter.end()


class GraphCanvas(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setMinimumSize(800, 600)
        self.setMouseTracking(True)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Рисуем фон с сеткой
        self.draw_grid(painter)
        
        if not self.parent.graph:
            painter.setPen(QColor(self.parent.current_theme['text']))
            painter.setFont(QFont("Arial", 16, QFont.Bold))
            painter.drawText(self.rect(), Qt.AlignCenter, "Граф не загружен\nНажмите 'Загрузить' или 'Случайный'")
            painter.end()
            return
        
        self.draw_edges(painter)
        self.draw_nodes(painter)
        self.draw_legend(painter)
        
        painter.end()
        
    def draw_grid(self, painter):
        """Рисует сетку на фоне с эффектом параллакса"""
        # Основной фон
        painter.fillRect(self.rect(), QColor(self.parent.current_theme['canvas_bg']))
        
        # Параллакс эффект - сетка двигается при панорамировании
        parallax_factor = 0.3
        offset_x = self.parent.pan_offset_x * parallax_factor
        offset_y = self.parent.pan_offset_y * parallax_factor
        
        grid_size = 50 * self.parent.zoom_level
        small_grid_size = 10 * self.parent.zoom_level
        
        # Мелкая сетка (светлая)
        pen_small = QPen(QColor(40, 40, 40, 30))
        pen_small.setWidth(1)
        painter.setPen(pen_small)
        
        # Вертикальные линии мелкой сетки
        start_x = (offset_x % small_grid_size) - small_grid_size
        for x in range(int(start_x), self.width(), int(small_grid_size)):
            painter.drawLine(x, 0, x, self.height())
        
        # Горизонтальные линии мелкой сетки
        start_y = (offset_y % small_grid_size) - small_grid_size
        for y in range(int(start_y), self.height(), int(small_grid_size)):
            painter.drawLine(0, y, self.width(), y)
        
        # Основная сетка (ярче)
        pen_main = QPen(QColor(60, 60, 60, 50))
        pen_main.setWidth(1)
        painter.setPen(pen_main)
        
        # Вертикальные линии основной сетки
        start_x = (offset_x % grid_size) - grid_size
        for x in range(int(start_x), self.width(), int(grid_size)):
            painter.drawLine(x, 0, x, self.height())
        
        # Горизонтальные линии основной сетки
        start_y = (offset_y % grid_size) - grid_size
        for y in range(int(start_y), self.height(), int(grid_size)):
            painter.drawLine(0, y, self.width(), y)
        
        # Центральные оси (еще ярче)
        center_x = self.width() // 2 + offset_x
        center_y = self.height() // 2 + offset_y
        
        pen_axis = QPen(QColor(80, 80, 80, 80))
        pen_axis.setWidth(2)
        painter.setPen(pen_axis)
        
        painter.drawLine(center_x, 0, center_x, self.height())
        painter.drawLine(0, center_y, self.width(), center_y)
        
    def draw_edges(self, painter):
        drawn_edges = set()
        
        for (u, v), weight in self.parent.graph.items():
            edge_key = tuple(sorted([u, v]))
            if edge_key in drawn_edges:
                continue
                
            drawn_edges.add(edge_key)
            
            if u in self.parent.positions and v in self.parent.positions:
                x1, y1 = self.parent.get_transformed_position(*self.parent.positions[u])
                x2, y2 = self.parent.get_transformed_position(*self.parent.positions[v])
                
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
                
                if self.parent.zoom_level > 0.3:
                    self.draw_edge_weight(painter, x1, y1, x2, y2, weight)
    
    def draw_edge_weight(self, painter, x1, y1, x2, y2, weight):
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        offset_x = (y2 - y1) * 0.1
        offset_y = -(x2 - x1) * 0.1
        
        # Фон для текста веса
        text_rect = QRect(int(mid_x + offset_x - 15), int(mid_y + offset_y - 10), 30, 20)
        painter.setBrush(QColor(30, 30, 30, 200))
        painter.setPen(QPen(QColor(self.parent.current_theme['border']), 1))
        painter.drawRoundedRect(text_rect, 5, 5)
        
        painter.setPen(QColor(self.parent.current_theme['text']))
        painter.setFont(QFont("Arial", max(8, int(10 * self.parent.zoom_level)), QFont.Bold))
        painter.drawText(text_rect, Qt.AlignCenter, str(weight))
    
    def draw_nodes(self, painter):
        for node, (orig_x, orig_y) in self.parent.positions.items():
            x, y = self.parent.get_transformed_position(orig_x, orig_y)
            
            color = self.parent.get_node_color(node)
            
            # Тень узла с параллаксом
            shadow_offset = 4 * self.parent.zoom_level
            painter.setBrush(QColor(0, 0, 0, 80))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(x - 15 + shadow_offset), 
                              int(y - 15 + shadow_offset), 
                              30, 30)
            
            # Основной узел с градиентом
            radius = max(15, int(20 * self.parent.zoom_level))
            gradient = QRadialGradient(x, y, radius)
            gradient.setColorAt(0, QColor(color).lighter(150))
            gradient.setColorAt(0.7, QColor(color))
            gradient.setColorAt(1, QColor(color).darker(120))
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(QColor(self.parent.current_theme['border']), 2))
            painter.drawEllipse(int(x - radius), int(y - radius), radius * 2, radius * 2)
            
            # Текст узла
            text_color = "white" if color in ["#4CAF50", "#F44336", "#bb86fc", "#4caf50", "#ffb74d"] else "black"
            painter.setPen(QColor(text_color))
            painter.setFont(QFont("Arial", max(8, int(12 * self.parent.zoom_level)), QFont.Bold))
            painter.drawText(int(x - radius), int(y - radius), radius * 2, radius * 2, 
                           Qt.AlignCenter, node)
            
            # Отображение расстояния
            if (node in self.parent.distances and self.parent.distances[node] != float('inf') and 
                self.parent.zoom_level > 0.5):
                self.draw_node_distance(painter, x, y, node)
    
    def draw_node_distance(self, painter, x, y, node):
        dist_text = f"{self.parent.distances[node]:.1f}"
        
        # Фон для текста расстояния
        text_rect = QRect(int(x + 25 * self.parent.zoom_level), 
                         int(y - 35 * self.parent.zoom_level), 
                         40, 20)
        painter.setBrush(QColor(30, 30, 30, 200))
        painter.setPen(QPen(QColor(self.parent.current_theme['border']), 1))
        painter.drawRoundedRect(text_rect, 5, 5)
        
        painter.setPen(QColor(self.parent.current_theme['accent']))
        painter.setFont(QFont("Arial", max(6, int(10 * self.parent.zoom_level)), QFont.Bold))
        painter.drawText(text_rect, Qt.AlignCenter, dist_text)
    
    def draw_legend(self, painter):
        # Создаем эффект размытия для фона легенды
        legend_bg_rect = QRect(15, 15, 220, 200)
        
        # Основной фон с размытым эффектом
        painter.setBrush(QColor(20, 20, 20, 180))
        painter.setPen(QPen(QColor(self.parent.current_theme['border']), 1))
        painter.drawRoundedRect(legend_bg_rect, 12, 12)
        
        # Внутренний отступ
        inner_rect = legend_bg_rect.adjusted(8, 8, -8, -8)
        painter.setBrush(QColor(30, 30, 30, 150))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(inner_rect, 8, 8)
        
        legend_x, legend_y = 25, 30
        legend_items = [
            ("Текущий узел", self.parent.current_theme['warning']),
            ("Посещенный", self.parent.current_theme['accent']),
            ("Кратчайший путь", self.parent.current_theme['success']),
            ("Старт", "#4CAF50"),
            ("Финиш", "#F44336"),
            ("Не посещенный", self.parent.current_theme['text_secondary'])
        ]
        
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        
        for text, color in legend_items:
            # Иконка легенды с тенью
            icon_size = 16
            painter.setBrush(QColor(0, 0, 0, 80))
            painter.setPen(Qt.NoPen)
            painter.drawRect(legend_x + 1, legend_y + 1, icon_size, icon_size)
            
            # Основная иконка
            painter.setBrush(QBrush(QColor(color)))
            painter.setPen(QPen(QColor(self.parent.current_theme['border']), 1))
            painter.drawRect(legend_x, legend_y, icon_size, icon_size)
            
            # Текст легенды
            painter.setPen(QColor(self.parent.current_theme['text']))
            painter.drawText(legend_x + 25, legend_y + 12, text)
            legend_y += 28
        
        # Информационный блок с параллаксом
        if hasattr(self.parent, 'start_node') and hasattr(self.parent, 'end_node'):
            info_bg_rect = QRect(15, legend_y + 15, 250, 100)
            
            painter.setBrush(QColor(20, 20, 20, 180))
            painter.setPen(QPen(QColor(self.parent.current_theme['border']), 1))
            painter.drawRoundedRect(info_bg_rect, 12, 12)
            
            inner_info_rect = info_bg_rect.adjusted(8, 8, -8, -8)
            painter.setBrush(QColor(30, 30, 30, 150))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(inner_info_rect, 8, 8)
            
            info_y = legend_y + 30
            algo_name = "Дейкстра" if self.parent.dijkstra_radio.isChecked() else "Беллман-Форд"
            
            painter.setFont(QFont("Arial", 11, QFont.Bold))
            painter.setPen(QColor(self.parent.current_theme['text']))
            painter.drawText(25, info_y, f"Алгоритм: {algo_name}")
            painter.drawText(25, info_y + 25, f"Старт: {self.parent.start_node}, Конец: {self.parent.end_node}")
            
            if self.parent.algorithm_finished and self.parent.algorithm_result:
                result_color = self.parent.current_theme['success'] if "Найден путь" in self.parent.algorithm_result else self.parent.current_theme['danger']
                painter.setPen(QColor(result_color))
                result_text = self.parent.algorithm_result.split("(")[0] if "Найден путь" in self.parent.algorithm_result else self.parent.algorithm_result
                painter.drawText(25, info_y + 50, result_text)
    
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


class ModernGraphVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Визуализация алгоритмов кратчайшего пути - Modern UI")
        self.setGeometry(100, 100, 1400, 900)
        
        self.dark_mode = True
        self.setup_themes()
        self.apply_theme()
        
        self.graph = {}
        self.positions = {}
        self.original_positions = {}
        self.history = []
        self.current_history_index = -1
        self.pause = True
        self.algorithm_finished = False
        self.algorithm_result = ""
        self.has_negative_weights = False
        
        self.animation_speed = 500
        self.zoom_level = 1.0
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        self.is_panning = False
        
        self.bellman_iteration = 0
        self.bellman_edge_index = 0
        self.bellman_changed = False
        
        self.setup_ui()
        self.initialize_default_graph()
        self.initialize_algorithm()

    def setup_themes(self):
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
            }
        }
        self.current_theme = self.themes['dark']

    def apply_theme(self):
        palette = QPalette()
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
        
        QApplication.setPalette(palette)

    def create_animated_header(self):
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 5, 0, 5)
        header_layout.setSpacing(2)
        
        title_label = GradientLabel("GRAPH VISUALIZER PRO", self)
        title_label.setAlignment(Qt.AlignCenter)
        
        subtitle_text = f"""
        <html>
        <head/>
        <body>
        <p style="color: {self.current_theme['text_secondary']}; font-size: 12px; margin: 0; padding: 0; text-align: center;">
        <span style="color: {self.current_theme['accent']}; font-weight: bold;">Дейкстра</span> • 
        <span style="color: {self.current_theme['accent']}; font-weight: bold;">Беллман-Форд</span> • 
        Визуализация графов • Анализ алгоритмов
        </p>
        </body>
        </html>
        """
        
        subtitle_label = QLabel()
        subtitle_label.setText(subtitle_text)
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        
        return header_widget

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.create_top_panel(layout)
        
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        self.canvas_widget = GraphCanvas(self)
        splitter.addWidget(self.canvas_widget)
        
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        self.create_status_bar()
        
        splitter.setSizes([1000, 400])

    def create_top_panel(self, layout):
        top_frame = QFrame()
        top_frame.setMinimumHeight(100)
        top_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.current_theme['bg_secondary']},
                    stop:1 {self.current_theme['bg']});
                border-bottom: 2px solid {self.current_theme['accent']};
                border-radius: 0px;
                padding: 12px;
            }}
        """)
        
        top_layout = QHBoxLayout(top_frame)
        top_layout.setSpacing(15)
        
        header_widget = self.create_animated_header()
        top_layout.addWidget(header_widget)
        
        top_layout.addStretch(1)
        
        algo_group = QGroupBox("Выбор алгоритма")
        algo_group.setStyleSheet(f"""
            QGroupBox {{
                color: {self.current_theme['accent']};
                font-weight: bold;
                font-size: 12px;
                border: 1px solid {self.current_theme['border']};
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 8px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """)
        algo_layout = QHBoxLayout(algo_group)
        algo_layout.setSpacing(10)
        
        self.algorithm_group = QButtonGroup(self)
        
        self.dijkstra_radio = QRadioButton("Дейкстра")
        self.bellman_radio = QRadioButton("Беллман-Форд")
        self.dijkstra_radio.setChecked(True)
        
        radio_style = f"""
            QRadioButton {{
                color: {self.current_theme['text']};
                font-weight: normal;
                font-size: 11px;
                padding: 4px 8px;
                border: 1px solid transparent;
                border-radius: 4px;
            }}
            QRadioButton:hover {{
                background: {self.current_theme['bg_tertiary']};
                border: 1px solid {self.current_theme['accent']};
            }}
            QRadioButton::indicator {{
                width: 14px;
                height: 14px;
            }}
            QRadioButton::indicator::unchecked {{
                border: 2px solid {self.current_theme['text_secondary']};
                border-radius: 7px;
                background: {self.current_theme['bg_tertiary']};
            }}
            QRadioButton::indicator::checked {{
                border: 2px solid {self.current_theme['accent']};
                border-radius: 7px;
                background: {self.current_theme['accent']};
            }}
        """
        
        self.dijkstra_radio.setStyleSheet(radio_style)
        self.bellman_radio.setStyleSheet(radio_style)
        
        self.algorithm_group.addButton(self.dijkstra_radio)
        self.algorithm_group.addButton(self.bellman_radio)
        
        algo_layout.addWidget(self.dijkstra_radio)
        algo_layout.addWidget(self.bellman_radio)
        top_layout.addWidget(algo_group)
        
        top_layout.addStretch(1)
        
        control_layout = QHBoxLayout()
        control_layout.setSpacing(8)
        
        self.step_back_btn = self.create_control_button("◀◀", "Назад", self.step_backward)
        self.step_forward_btn = self.create_control_button("▶▶", "Вперед", self.step_forward)
        self.pause_btn = self.create_control_button("❚❚", "Пауза", self.toggle_pause)
        self.restart_btn = self.create_control_button("↺", "Сброс", self.restart)
        
        control_layout.addWidget(self.step_back_btn)
        control_layout.addWidget(self.step_forward_btn)
        control_layout.addWidget(self.pause_btn)
        control_layout.addWidget(self.restart_btn)
        
        top_layout.addLayout(control_layout)
        
        top_layout.addStretch(1)
        
        file_layout = QHBoxLayout()
        file_layout.setSpacing(8)
        
        self.load_btn = self.create_styled_button("📁 Загрузить", self.load_graph_from_file)
        self.random_btn = self.create_styled_button("🎲 Случайный", self.generate_random_graph)
        
        file_layout.addWidget(self.load_btn)
        file_layout.addWidget(self.random_btn)
        
        top_layout.addLayout(file_layout)
        
        layout.addWidget(top_frame)

    def create_control_button(self, icon, tooltip, callback):
        btn = QPushButton(icon)
        btn.setToolTip(tooltip)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {self.current_theme['bg_tertiary']};
                border: 2px solid {self.current_theme['border']};
                border-radius: 8px;
                padding: 10px;
                color: {self.current_theme['text']};
                font-weight: bold;
                font-size: 16px;
                min-width: 50px;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background: {self.current_theme['accent']};
                border: 2px solid {self.current_theme['accent_secondary']};
                color: {self.current_theme['bg']};
            }}
            QPushButton:pressed {{
                background: {self.current_theme['accent_secondary']};
                border: 2px solid {self.current_theme['accent']};
            }}
            QPushButton:disabled {{
                background: {self.current_theme['bg_secondary']};
                border: 2px solid {self.current_theme['text_secondary']};
                color: {self.current_theme['text_secondary']};
            }}
        """)
        btn.clicked.connect(callback)
        return btn

    def create_styled_button(self, text, callback):
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
                font-size: 11px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.current_theme['accent']}, 
                    stop:1 {self.current_theme['accent_secondary']});
                border: 1px solid {self.current_theme['accent']};
                color: black;
            }}
            QPushButton:pressed {{
                background: {self.current_theme['accent_secondary']};
            }}
        """)
        btn.clicked.connect(callback)
        return btn

    def create_right_panel(self):
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(15)
        
        node_group = QGroupBox("Выбор узлов")
        node_group.setStyleSheet(self.get_groupbox_style())
        node_layout = QVBoxLayout(node_group)
        
        start_layout = QHBoxLayout()
        start_layout.addWidget(QLabel("Старт:"))
        self.start_combo = QComboBox()
        self.start_combo.setStyleSheet(self.get_combobox_style())
        start_layout.addWidget(self.start_combo)
        node_layout.addLayout(start_layout)
        
        end_layout = QHBoxLayout()
        end_layout.addWidget(QLabel("Конец:"))
        self.end_combo = QComboBox()
        self.end_combo.setStyleSheet(self.get_combobox_style())
        end_layout.addWidget(self.end_combo)
        node_layout.addLayout(end_layout)
        
        self.apply_btn = self.create_styled_button("Применить выбор", self.apply_selection)
        node_layout.addWidget(self.apply_btn)
        
        right_layout.addWidget(node_group)
        
        speed_group = QGroupBox("Скорость анимации")
        speed_group.setStyleSheet(self.get_groupbox_style())
        speed_layout = QVBoxLayout(speed_group)
        speed_layout.setContentsMargins(12, 15, 12, 15)
        speed_layout.setSpacing(10)
        
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(0, 5)
        self.speed_slider.setValue(2)
        self.speed_slider.valueChanged.connect(self.change_speed)
        self.speed_slider.setStyleSheet(self.get_slider_style())
        self.speed_slider.setMinimumHeight(30)
        speed_layout.addWidget(self.speed_slider)
        
        self.speed_label = QLabel("Средняя скорость")
        self.speed_label.setStyleSheet(f"color: {self.current_theme['text']}; font-size: 11px; padding: 5px;")
        speed_layout.addWidget(self.speed_label)
        
        right_layout.addWidget(speed_group)
        
        progress_group = QGroupBox("Прогресс выполнения")
        progress_group.setStyleSheet(self.get_groupbox_style())
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {self.current_theme['border']};
                border-radius: 5px;
                text-align: center;
                background: {self.current_theme['bg_secondary']};
                color: {self.current_theme['text']};
                font-weight: bold;
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
        
        results_group = QGroupBox("Результаты")
        results_group.setStyleSheet(self.get_groupbox_style())
        results_layout = QVBoxLayout(results_group)
        
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["Вершина", "Расстояние", "Путь"])
        self.results_tree.setStyleSheet(f"""
            QTreeWidget {{
                background: {self.current_theme['bg_secondary']};
                color: {self.current_theme['text']};
                border: 1px solid {self.current_theme['border']};
                border-radius: 5px;
                font-size: 10px;
            }}
            QTreeWidget::item {{
                padding: 4px;
                border-bottom: 1px solid {self.current_theme['border']};
            }}
            QTreeWidget::item:selected {{
                background: {self.current_theme['accent']};
                color: black;
            }}
            QHeaderView::section {{
                background: {self.current_theme['bg_tertiary']};
                color: {self.current_theme['text']};
                padding: 6px;
                border: 1px solid {self.current_theme['border']};
                font-weight: bold;
            }}
        """)
        self.results_tree.setColumnWidth(0, 80)
        self.results_tree.setColumnWidth(1, 100)
        self.results_tree.setColumnWidth(2, 200)
        results_layout.addWidget(self.results_tree)
        
        right_layout.addWidget(results_group)
        
        info_group = QGroupBox("Информация о графе")
        info_group.setStyleSheet(self.get_groupbox_style())
        info_layout = QVBoxLayout(info_group)
        
        self.graph_info_label = QLabel("Граф не загружен")
        self.graph_info_label.setWordWrap(True)
        self.graph_info_label.setStyleSheet(f"""
            color: {self.current_theme['text']}; 
            font-size: 11px; 
            padding: 8px;
            line-height: 1.4;
        """)
        info_layout.addWidget(self.graph_info_label)
        
        right_layout.addWidget(info_group)
        
        right_layout.addStretch()
        
        return right_widget

    def get_groupbox_style(self):
        return f"""
            QGroupBox {{
                color: {self.current_theme['accent']};
                font-weight: bold;
                font-size: 12px;
                border: 1px solid {self.current_theme['border']};
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 8px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """

    def get_combobox_style(self):
        return f"""
            QComboBox {{
                background: {self.current_theme['bg_tertiary']};
                color: {self.current_theme['text']};
                border: 1px solid {self.current_theme['border']};
                border-radius: 4px;
                padding: 4px;
                min-width: 60px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 1px solid {self.current_theme['border']};
                padding: 4px;
            }}
            QComboBox QAbstractItemView {{
                background: {self.current_theme['bg_secondary']};
                color: {self.current_theme['text']};
                selection-background-color: {self.current_theme['accent']};
            }}
        """

    def get_slider_style(self):
        return f"""
            QSlider::groove:horizontal {{
                border: 1px solid {self.current_theme['border']};
                height: 8px;
                background: {self.current_theme['bg_tertiary']};
                border-radius: 4px;
                margin: 2px 0px;
            }}
            QSlider::handle:horizontal {{
                background: {self.current_theme['accent']};
                border: 2px solid {self.current_theme['accent_secondary']};
                width: 20px;
                height: 20px;
                margin: -8px 0px;
                border-radius: 10px;
            }}
            QSlider::sub-page:horizontal {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.current_theme['accent']}, 
                    stop:1 {self.current_theme['accent_secondary']});
                border-radius: 4px;
            }}
        """

    def create_status_bar(self):
        self.status_bar = self.statusBar()
        self.status_label = QLabel("Готов к работе. Загрузите граф или создайте случайный.")
        self.status_bar.addWidget(self.status_label)
        
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background: {self.current_theme['bg_secondary']};
                color: {self.current_theme['text']};
                border-top: 1px solid {self.current_theme['border']};
                font-size: 11px;
            }}
        """)

    def get_node_color(self, node):
        if hasattr(self, 'start_node') and node == self.start_node:
            return "#4CAF50"
        if hasattr(self, 'end_node') and node == self.end_node:
            return "#F44336"
        if node == self.current_node:
            return self.current_theme['warning']
        if node in self.visited:
            return self.current_theme['accent']
        if self.final_path and node in self.final_path:
            return self.current_theme['success']
        return self.current_theme['text_secondary']

    def get_transformed_position(self, x, y):
        center_x, center_y = self.canvas_widget.width() // 2, self.canvas_widget.height() // 2
        transformed_x = center_x + (x - center_x + self.pan_offset_x) * self.zoom_level
        transformed_y = center_y + (y - center_y + self.pan_offset_y) * self.zoom_level
        return transformed_x, transformed_y

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
Отрицательные веса: {negative_weights}"""
        
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
        
        for i in range(len(selected_nodes) - 1):
            u = selected_nodes[i]
            v = selected_nodes[i + 1]
            weight = random.randint(1, 10)
            self.graph[(u, v)] = weight
            self.graph[(v, u)] = weight
        
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
        
        self.bellman_iteration = 0
        self.bellman_edge_index = 0
        self.bellman_changed = False
        self.bellman_edges = self.get_edges_list()
        
        if self.dijkstra_radio.isChecked():
            self.queue = []
            heapq.heappush(self.queue, (0, self.start_node))
        
        self.history = []
        self.current_history_index = -1
        self.save_state("Инициализация: расстояния установлены в бесконечность, кроме стартовой вершины")
        self.update_results_table()
        self.update_progress()

    def get_edges_list(self):
        edges = []
        for (u, v), weight in self.graph.items():
            edges.append((u, v, weight))
        return edges

    def save_state(self, description=""):
        state = {
            'distances': self.distances.copy(),
            'visited': self.visited.copy(),
            'previous': self.previous.copy(),
            'current_node': self.current_node,
            'final_path': self.final_path.copy() if self.final_path else None,
            'algorithm_finished': self.algorithm_finished,
            'algorithm_result': self.algorithm_result,
            'bellman_iteration': self.bellman_iteration,
            'bellman_edge_index': self.bellman_edge_index,
            'bellman_changed': self.bellman_changed,
            'description': description
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
        self.bellman_iteration = state.get('bellman_iteration', 0)
        self.bellman_edge_index = state.get('bellman_edge_index', 0)
        self.bellman_changed = state.get('bellman_changed', False)

    def dijkstra_step(self):
        if not self.queue:
            self.finalize_algorithm()
            return
        
        current_distance, self.current_node = heapq.heappop(self.queue)
        
        if self.current_node in self.visited:
            return
        
        self.visited.add(self.current_node)
        self.save_state(f"Обрабатываем узел {self.current_node} (расстояние: {current_distance})")
        
        for (u, v), weight in self.graph.items():
            if u == self.current_node and v not in self.visited:
                new_distance = current_distance + weight
                if new_distance < self.distances[v]:
                    old_dist = self.distances[v]
                    self.distances[v] = new_distance
                    self.previous[v] = u
                    heapq.heappush(self.queue, (new_distance, v))
                    self.save_state(f"Обновлено расстояние до {v}: {old_dist} -> {new_distance}")
        
        if self.current_node == self.end_node:
            self.finalize_algorithm()

    def bellman_ford_step(self):
        if self.bellman_iteration < len(self.positions) - 1:
            if self.bellman_edge_index < len(self.bellman_edges):
                u, v, weight = self.bellman_edges[self.bellman_edge_index]
                self.current_node = u
                
                if self.distances[u] != float('inf') and self.distances[u] + weight < self.distances[v]:
                    old_dist = self.distances[v]
                    self.distances[v] = self.distances[u] + weight
                    self.previous[v] = u
                    self.bellman_changed = True
                    
                    description = f"Итерация {self.bellman_iteration + 1}: Ребро {u}→{v} ({weight}) - обновлено {old_dist:.1f}→{self.distances[v]:.1f}"
                    self.save_state(description)
                else:
                    if self.bellman_edge_index % 3 == 0:
                        description = f"Итерация {self.bellman_iteration + 1}: Ребро {u}→{v} ({weight}) - без изменений"
                        self.save_state(description)
                
                self.bellman_edge_index += 1
                return True
            else:
                if self.bellman_changed:
                    self.bellman_iteration += 1
                    self.bellman_edge_index = 0
                    self.bellman_changed = False
                    self.current_node = None
                    self.save_state(f"Начало итерации {self.bellman_iteration + 1}")
                    return True
                else:
                    self.bellman_iteration = len(self.positions) - 1
                    self.check_negative_cycle()
                    return True
        else:
            return self.check_negative_cycle()

    def check_negative_cycle(self):
        if self.bellman_edge_index < len(self.bellman_edges):
            u, v, weight = self.bellman_edges[self.bellman_edge_index]
            self.current_node = u
            
            if self.distances[u] != float('inf') and self.distances[u] + weight < self.distances[v]:
                self.algorithm_finished = True
                self.algorithm_result = f"Обнаружен цикл отрицательного веса! Ребро {u}→{v} ({weight})"
                self.save_state(f"ОШИБКА: {self.algorithm_result}")
                self.update_progress()
                QMessageBox.warning(self, "Обнаружен отрицательный цикл", self.algorithm_result)
                return False
            
            self.bellman_edge_index += 1
            if self.bellman_edge_index % 3 == 0:
                self.save_state(f"Проверка на отрицательные циклы: ребро {u}→{v}")
            return True
        else:
            self.algorithm_finished = True
            self.finalize_algorithm()
            return False

    def finalize_algorithm(self):
        self.algorithm_finished = True
        self.current_node = None
        
        if self.end_node in self.previous and self.distances[self.end_node] != float('inf'):
            path = []
            current = self.end_node
            max_steps = len(self.positions)
            
            while current != self.start_node and max_steps > 0:
                path.append(current)
                if current not in self.previous:
                    break
                current = self.previous[current]
                max_steps -= 1
            
            if max_steps > 0:
                path.append(self.start_node)
                path.reverse()
                self.final_path = path
                total_distance = self.distances[self.end_node]
                self.algorithm_result = f"Найден путь: {' -> '.join(path)} (длина: {total_distance})"
            else:
                self.final_path = None
                self.algorithm_result = "Не удалось построить путь"
        else:
            self.final_path = None
            self.algorithm_result = f"Путь от {self.start_node} до {self.end_node} не найден"
        
        self.save_state(f"Завершено: {self.algorithm_result}")
        self.status_label.setText(self.algorithm_result)
        self.update_progress()

    def toggle_pause(self):
        self.pause = not self.pause
        if not self.pause:
            self.pause_btn.setText("❚❚")
            self.pause_btn.setToolTip("Пауза")
        else:
            self.pause_btn.setText("▶")
            self.pause_btn.setToolTip("Старт")
        
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
        self.pause_btn.setText("▶")
        self.pause_btn.setToolTip("Старт")
        self.initialize_algorithm()
        self.update_progress()
        self.update_results_table()
        self.canvas_widget.update()
        self.status_label.setText("Алгоритм перезапущен. Нажмите 'Старт' для начала.")

    def update_progress(self):
        if not self.positions:
            self.progress_bar.setValue(0)
            return
        
        if self.algorithm_finished:
            self.progress_bar.setValue(100)
        elif self.dijkstra_radio.isChecked():
            total_nodes = len(self.positions)
            visited_nodes = len(self.visited)
            progress = int((visited_nodes / total_nodes) * 100)
            self.progress_bar.setValue(progress)
        else:
            total_iterations = len(self.positions)
            if self.bellman_iteration < total_iterations - 1:
                progress = int((self.bellman_iteration / (total_iterations - 1)) * 100)
            else:
                total_edges = len(self.bellman_edges)
                if total_edges > 0:
                    progress = 80 + int((self.bellman_edge_index / total_edges) * 20)
                else:
                    progress = 100
            self.progress_bar.setValue(min(progress, 100))

    def update_results_table(self):
        self.results_tree.clear()
        
        if not hasattr(self, 'distances'):
            return
        
        for node in sorted(self.positions.keys()):
            distance = self.distances[node]
            distance_text = f"{distance:.1f}" if distance != float('inf') else "∞"
            
            path = []
            current = node
            max_steps = len(self.positions)
            
            while current != self.start_node and current in self.previous and max_steps > 0:
                path.append(current)
                current = self.previous[current]
                max_steps -= 1
            
            if max_steps > 0 and current == self.start_node:
                path.append(self.start_node)
                path.reverse()
                path_text = " -> ".join(path)
            else:
                path_text = "-"
            
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
    app.setStyle('Fusion')
    window = ModernGraphVisualizer()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()