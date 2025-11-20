"""
МОДУЛЬ: vizualizergraphof.py
НАЗНАЧЕНИЕ: Визуализация и пошаговое выполнение алгоритмов Дейкстры и Беллмана-Форда
АРХИТЕКТУРА: Приложение использует паттерн плагинов для поддержки multiple алгоритмов
"""

import sys
import math
import heapq
import random
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QComboBox, QRadioButton, QGroupBox,
    QFileDialog, QMessageBox, QTreeWidget, QTreeWidgetItem,
    QSlider, QSplitter, QFrame, QProgressBar, QButtonGroup,
    QGraphicsBlurEffect, QHeaderView, QDialogButtonBox, QDialog, QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import Qt, QTimer, QRect, QSettings 
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPalette, QLinearGradient, QRadialGradient, QKeySequence


# ==================== БАЗОВЫЙ КЛАСС АЛГОРИТМА ====================
class ShortestPathAlgorithm:
    """
    АБСТРАКТНЫЙ БАЗОВЫЙ КЛАСС для алгоритмов поиска кратчайшего пути
    
    Научное обоснование: Реализует паттерн "Strategy", позволяющий единообразно
    работать с различными алгоритмами поиска пути. Это соответствует принципам
    объектно-ориентированного проектирования и упрощает расширяемость системы.
    """
    
    def __init__(self, name, description, supports_negative_weights=False):
        # Инициализация основных свойств алгоритма
        self.name = name
        self.description = description
        # Важное свойство для автоматического выбора алгоритма
        self.supports_negative_weights = supports_negative_weights
        
    def get_name(self):
        return self.name
        
    def get_description(self):
        return self.description
        
    def initialize(self, graph, start_node, positions, end_node=None):
        """
        Инициализация алгоритма перед выполнением
        
        Args:
            graph: словарь рёбер графа в формате {(u, v): weight}
            start_node: начальная вершина
            positions: координаты вершин для визуализации
            end_node: конечная вершина (опционально)
            
        Научный комментарий: Этап инициализации критически важен для корректности
        алгоритмов. Устанавливаются начальные расстояния и подготавливаются
        структуры данных для последующих вычислений.
        """
        raise NotImplementedError("Метод должен быть реализован в подклассе")
        
    def execute_step(self):
        """
        Выполняет один шаг алгоритма (пошаговое выполнение)
        
        Научный комментарий: Пошаговое выполнение позволяет анализировать
        процесс работы алгоритма, что особенно ценно для образовательных целей
        и отладки сложных вычислительных процессов.
        """
        raise NotImplementedError("Метод должен быть реализован в подклассе")
        
    def is_finished(self):
        """Проверяет завершение алгоритма"""
        raise NotImplementedError("Метод должен быть реализован в подклассе")
        
    def get_result(self):
        """Возвращает результат выполнения"""
        raise NotImplementedError("Метод должен быть реализован в подклассе")
        
    def get_current_state(self):
        """
        Возвращает текущее состояние для визуализации
        
        Научный комментарий: Этот метод обеспечивает отделение бизнес-логики
        алгоритма от представления, что соответствует принципу MVC (Model-View-Controller).
        """
        raise NotImplementedError("Метод должен быть реализован в подклассе")


# ==================== ПЛАГИН АЛГОРИТМА ДЕЙКСТРЫ ====================
class DijkstraPlugin(ShortestPathAlgorithm):
    """
    РЕАЛИЗАЦИЯ АЛГОРИТМА ДЕЙКСТРЫ
    
    Научное обоснование: Алгоритм Дейкстры (1956) - жадный алгоритм, находящий
    кратчайшие пути от одной вершины до всех других в графе с неотрицательными весами.
    Временная сложность: O((V+E) log V) при использовании двоичной кучи.
    """
    
    def __init__(self):
        super().__init__(
            name="Дейкстра",
            description="Алгоритм Дейкстры для поиска кратчайшего пути",
            supports_negative_weights=False  # Важное ограничение алгоритма
        )
        self.reset()
        
    def reset(self):
        """
        Сброс состояния алгоритма
        
        Научный комментарий: Подготовка структур данных:
        - distances: хранит текущие наикратчайшие расстояния до вершин
        - visited: множество посещенных вершин (черный набор в терминологии алгоритма)
        - previous: для восстановления пути (хранит предшественников)
        - queue: приоритетная очередь для выбора следующей вершины
        """
        self.distances = {}  # Расстояния до вершин
        self.visited = set() # Посещенные вершины
        self.previous = {}   # Предшественники для восстановления пути
        self.queue = []      # Очередь с приоритетом (min-heap)
        self.current_node = None
        self.final_path = None
        self.algorithm_finished = False
        self.algorithm_result = ""
        self.graph = None
        self.start_node = None
        self.end_node = None
        
    def initialize(self, graph, start_node, positions, end_node=None):
        """
        Инициализация алгоритма Дейкстры
        
        Научный комментарий: Начальные условия:
        - Все расстояния устанавливаются в бесконечность (∞)
        - Расстояние до стартовой вершины = 0
        - Очередь инициализируется стартовой вершиной
        
        Это соответствует теоретическому описанию алгоритма в литературе.
        """
        self.reset()
        self.graph = graph
        self.start_node = start_node
        self.end_node = end_node
        
        # Инициализация расстояний (бесконечность для всех вершин кроме стартовой)
        self.distances = {node: float('inf') for node in positions}
        self.distances[start_node] = 0  # Расстояние до себя = 0
        
        # Использование heapq для эффективной реализации приоритетной очереди
        heapq.heappush(self.queue, (0, start_node))
        
        return self.get_current_state("Инициализация: расстояния установлены в бесконечность, кроме стартовой вершины")
        
    def execute_step(self):
        """
        Выполняет один шаг алгоритма Дейкстры
        
        Научный комментарий: Каждый шаг включает:
        1. Извлечение вершины с минимальным расстоянием из очереди
        2. Помещение её в посещенные
        3. Релаксация всех исходящих рёбер
        4. Проверка условий завершения
        
        Этот процесс демонстрирует жадную стратегию алгоритма.
        """
        if self.algorithm_finished or not self.queue:
            return None
            
        # Извлекаем узел с минимальным расстоянием (жадный выбор)
        current_distance, self.current_node = heapq.heappop(self.queue)
        
        # Пропускаем если уже посещали (может быть в очереди несколько раз)
        if self.current_node in self.visited:
            return self.get_current_state()
            
        self.visited.add(self.current_node)  # Помечаем как посещенный
        
        # Обрабатываем соседей текущей вершины (релаксация рёбер)
        updates = []
        for (u, v), weight in self.graph.items():
            if u == self.current_node and v not in self.visited:
                new_distance = current_distance + weight
                # Если найден более короткий путь - обновляем
                if new_distance < self.distances[v]:
                    old_distance = self.distances[v]
                    self.distances[v] = new_distance
                    self.previous[v] = self.current_node
                    heapq.heappush(self.queue, (new_distance, v))
                    updates.append((v, old_distance, new_distance))
        
        # Проверяем условия завершения
        if self.current_node == self.end_node or not self.queue:
            self.finalize_algorithm()
            
        # Формируем описание шага для визуализации
        description = f"Обрабатываем узел {self.current_node}"
        if updates:
            desc_updates = [f"{v}: {old:.1f}→{new:.1f}" for v, old, new in updates]
            description += f" | Обновления: {', '.join(desc_updates)}"
            
        return self.get_current_state(description)


# ==================== ПЛАГИН АЛГОРИТМА БЕЛЛМАНА-ФОРДА ====================
class BellmanFordPlugin(ShortestPathAlgorithm):
    """
    РЕАЛИЗАЦИЯ АЛГОРИТМА БЕЛЛМАНА-ФОРДА
    
    Научное обоснование: Алгоритм Беллмана-Форда (1958) использует динамическое
    программирование и может обрабатывать графы с отрицательными весами.
    Временная сложность: O(V*E), где V - вершины, E - рёбра.
    Особенность: обнаруживает циклы отрицательного веса.
    """
    
    def __init__(self):
        super().__init__(
            name="Беллман-Форд", 
            description="Алгоритм Беллмана-Форда для графов с отрицательными весами",
            supports_negative_weights=True  # Ключевое преимущество
        )
        self.reset()
        
    def reset(self):
        """
        Сброс состояния алгоритма Беллмана-Форда
        
        Научный комментарий: Алгоритм использует подход динамического программирования:
        - distances: хранит наилучшие найденные расстояния на текущей итерации
        - edges: список всех рёбер для последовательной релаксации
        - iteration: счетчик выполненных итераций
        """
        self.distances = {}
        self.previous = {}
        self.current_node = None
        self.final_path = None
        self.algorithm_finished = False
        self.algorithm_result = ""
        self.iteration = 0          # Текущая итерация
        self.edge_index = 0         # Индекс текущего обрабатываемого ребра
        self.changed = False        # Флаг изменений на итерации
        self.edges = []             # Список всех рёбер
        self.graph = None
        self.start_node = None
        self.end_node = None
        
    def initialize(self, graph, start_node, positions, end_node=None):
        """
        Инициализация алгоритма Беллмана-Форда
        
        Научный комментарий: В отличие от Дейкстры, здесь не используется
        приоритетная очередь. Алгоритм работает через |V|-1 итераций полной
        релаксации всех рёбер графа.
        """
        self.reset()
        self.graph = graph
        self.start_node = start_node
        self.end_node = end_node
        
        # Инициализация расстояний (аналогично Дейкстре)
        self.distances = {node: float('inf') for node in positions}
        self.distances[start_node] = 0
        
        # Создаем список всех рёбер для последовательной обработки
        self.edges = []
        for (u, v), weight in graph.items():
            self.edges.append((u, v, weight))
        
        return self.get_current_state(f"Инициализация: |V| = {len(positions)}, |E| = {len(self.edges)}")
        
    def execute_step(self):
        """
        Выполняет один шаг алгоритма Беллмана-Форда
        
        Научный комментарий: Алгоритм состоит из двух фаз:
        1. |V|-1 итераций релаксации всех рёбер
        2. Проверка на наличие циклов отрицательного веса
        
        Каждый шаг соответствует обработке одного ребра.
        """
        if self.algorithm_finished:
            return None
            
        description = ""
        
        # Фаза 1: Основные итерации релаксации (|V|-1 раз)
        if self.iteration < len(self.distances) - 1:
            if self.edge_index < len(self.edges):
                u, v, weight = self.edges[self.edge_index]
                self.current_node = u
                
                # Релаксация ребра (u, v)
                if self.distances[u] != float('inf') and self.distances[u] + weight < self.distances[v]:
                    old_dist = self.distances[v]
                    self.distances[v] = self.distances[u] + weight
                    self.previous[v] = u
                    self.changed = True  # Запоминаем что были изменения
                    
                    description = f"Итерация {self.iteration + 1}: {u}→{v} ({weight}) - {old_dist:.1f}→{self.distances[v]:.1f}"
                else:
                    description = f"Итерация {self.iteration + 1}: {u}→{v} ({weight}) - без изменений"
                    
                self.edge_index += 1
                
            else:
                # Завершили обработку всех рёбер на текущей итерации
                if self.changed:
                    self.iteration += 1
                    self.edge_index = 0
                    self.changed = False
                    self.current_node = None
                    description = f"Начало итерации {self.iteration + 1}"
                else:
                    # Если изменений не было - досрочное завершение
                    self.iteration = len(self.distances) - 1
                    description = "Переход к проверке отрицательных циклов"
                    
        # Фаза 2: Проверка отрицательных циклов
        else:
            if self.edge_index < len(self.edges):
                u, v, weight = self.edges[self.edge_index]
                self.current_node = u
                
                # Если можно улучшить расстояние - есть отрицательный цикл
                if self.distances[u] != float('inf') and self.distances[u] + weight < self.distances[v]:
                    self.algorithm_finished = True
                    self.algorithm_result = f"Обнаружен цикл отрицательного веса! {u}→{v} ({weight})"
                    description = f"ОШИБКА: {self.algorithm_result}"
                else:
                    description = f"Проверка циклов: {u}→{v} ({weight})"
                    
                self.edge_index += 1
            else:
                # Алгоритм завершен успешно
                self.algorithm_finished = True
                self.finalize_algorithm()
                description = "Алгоритм завершен"
                
        return self.get_current_state(description)


# ==================== КОМПОНЕНТЫ ВИЗУАЛИЗАЦИИ ====================
class GraphCanvas(QWidget):
    """
    КОМПОНЕНТ ДЛЯ ОТРИСОВКИ ГРАФА
    
    Научное обоснование: Реализует визуальное представление графа с учетом
    текущего состояния алгоритма. Использует различные цвета для отображения:
    - Посещенных вершин
    - Текущей вершины  
    - Кратчайшего пути
    - Вершин с отрицательными весами
    """
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setMinimumSize(800, 600)
        self.setMouseTracking(True)  # Включение отслеживания мыши
        
    def paintEvent(self, event):
        """
        Обработчик события отрисовки
        
        Научный комментарий: Этот метод вызывается автоматически при необходимости
        перерисовать виджет. Реализует многослойную отрисовку:
        1. Фон с сеткой
        2. Рёбра графа
        3. Вершины графа
        4. Легенда и информационные блоки
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # Сглаживание
        
        # Многослойная отрисовка
        self.draw_grid(painter)      # Фоновая сетка
        self.draw_edges(painter)     # Рёбра графа
        self.draw_nodes(painter)     # Вершины графа
        self.draw_legend(painter)    # Легенда и информация
        
        painter.end()


class ModernGraphVisualizer(QMainWindow):
    """
    ГЛАВНОЕ ОКНО ПРИЛОЖЕНИЯ
    
    Архитектура: Реализует паттерн Model-View-Controller:
    - Model: граф и состояние алгоритмов
    - View: GraphCanvas и элементы управления  
    - Controller: обработчики событий и управление состоянием
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Визуализация алгоритмов кратчайшего пути - Modern UI")
        self.setGeometry(100, 100, 1400, 900)
        
        # Инициализация темы и данных
        self.dark_mode = True
        self.setup_themes()
        self.apply_theme()
        
        # Данные графа и состояния алгоритма
        self.graph = {}              # Словарь рёбер: {(u, v): weight}
        self.positions = {}          # Координаты вершин для отрисовки
        self.original_positions = {} # Исходные координаты
        self.start_node = None       # Стартовая вершина
        self.end_node = None         # Конечная вершина
        
        # Состояние выполнения алгоритма
        self.distances = {}          # Текущие расстояния до вершин
        self.visited = set()         # Множество посещенных вершин
        self.previous = {}           # Предшественники для восстановления пути
        self.current_node = None     # Текущая обрабатываемая вершина
        self.final_path = None       # Найденный кратчайший путь
        self.algorithm_finished = False
        self.algorithm_result = ""
        
        # История выполнения и управление
        self.history = []            # История состояний для навигации
        self.current_history_index = -1
        self.pause = True            # Флаг паузы выполнения
        
        # Настройки визуализации
        self.zoom_level = 1.0        # Уровень масштабирования
        self.pan_offset_x = 0        # Смещение по X для панорамирования
        self.pan_offset_y = 0        # Смещение по Y для панорамирования
        self.is_panning = False      # Флаг активного панорамирования
        
        # Менеджер алгоритмов
        self.algorithm_manager = AlgorithmPluginManager()
        self.current_algorithm = None
        
        # Инициализация интерфейса
        self.setup_ui()
        self.initialize_default_graph()
        self.initialize_algorithm()
        self.setup_shortcuts()


def main():
    """
    ТОЧКА ВХОДА В ПРИЛОЖЕНИЕ
    
    Научный комментарий: Создание и запуск Qt-приложения с использованием
    современного GUI фреймворка для кроссплатформенной совместимости.
    """
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Современный стиль виджетов
    window = ModernGraphVisualizer()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()