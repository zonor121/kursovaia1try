import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import math
import heapq
from collections import deque

class GraphVisualizerTkinter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Визуализация алгоритмов кратчайшего пути - Tkinter")
        self.root.geometry("1200x900")
        
        # Холст для рисования
        self.canvas = tk.Canvas(self.root, width=1000, height=600, bg='white', highlightthickness=1, highlightbackground="gray")
        self.canvas.pack(pady=10)
        
        # Настройки масштабирования
        self.zoom_level = 1.0
        self.zoom_factor = 1.1
        self.pan_start_x = 0
        self.pan_start_y = 0
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        self.is_panning = False
        
        # Привязка событий мыши для масштабирования и панорамирования
        self.canvas.bind("<MouseWheel>", self.zoom)  # Windows/Mac
        self.canvas.bind("<Button-4>", self.zoom)    # Linux scroll up
        self.canvas.bind("<Button-5>", self.zoom)    # Linux scroll down
        self.canvas.bind("<ButtonPress-2>", self.start_pan)  # Средняя кнопка мыши для панорамирования
        self.canvas.bind("<B2-Motion>", self.pan)
        self.canvas.bind("<ButtonRelease-2>", self.end_pan)
        
        # Панель управления
        self.control_frame = ttk.Frame(self.root)
        self.control_frame.pack(pady=10)
        
        self.step_forward_btn = ttk.Button(self.control_frame, text="Шаг вперед →", command=self.step_forward)
        self.step_forward_btn.pack(side=tk.LEFT, padx=5)
        
        self.step_backward_btn = ttk.Button(self.control_frame, text="← Шаг назад", command=self.step_backward)
        self.step_backward_btn.pack(side=tk.LEFT, padx=5)
        
        self.pause_btn = ttk.Button(self.control_frame, text="▶️ Продолжить", command=self.toggle_pause)
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        
        self.restart_btn = ttk.Button(self.control_frame, text="🔄 Перезапуск", command=self.restart)
        self.restart_btn.pack(side=tk.LEFT, padx=5)
        
        # Кнопка загрузки графа
        self.load_graph_btn = ttk.Button(self.control_frame, text="📁 Загрузить граф", command=self.load_graph_from_file)
        self.load_graph_btn.pack(side=tk.LEFT, padx=5)
        
        # Кнопки масштабирования
        self.zoom_in_btn = ttk.Button(self.control_frame, text="➕ Приблизить", command=lambda: self.zoom_manual(1))
        self.zoom_in_btn.pack(side=tk.LEFT, padx=5)
        
        self.zoom_out_btn = ttk.Button(self.control_frame, text="➖ Отдалить", command=lambda: self.zoom_manual(-1))
        self.zoom_out_btn.pack(side=tk.LEFT, padx=5)
        
        self.reset_view_btn = ttk.Button(self.control_frame, text="🗘 Сброс вида", command=self.reset_view)
        self.reset_view_btn.pack(side=tk.LEFT, padx=5)
        
        # Выбор алгоритма
        self.algorithm_var = tk.StringVar(value="dijkstra")
        algo_frame = ttk.Frame(self.control_frame)
        algo_frame.pack(side=tk.LEFT, padx=20)
        ttk.Radiobutton(algo_frame, text="Дейкстра", variable=self.algorithm_var, value="dijkstra").pack(side=tk.LEFT)
        ttk.Radiobutton(algo_frame, text="Беллман-Форд", variable=self.algorithm_var, value="bellman").pack(side=tk.LEFT)
        
        # Панель скорости
        self.speed_frame = ttk.Frame(self.root)
        self.speed_frame.pack(pady=5)
        
        ttk.Label(self.speed_frame, text="Скорость анимации:", font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        self.speed_options = [
            ("Очень медленно", 2000),
            ("Медленно", 1000),
            ("Нормально", 500),
            ("Быстро", 200),
            ("Очень быстро", 50),
            ("Максимальная", 0)
        ]
        
        self.speed_var = tk.StringVar(value="Нормально")
        self.current_speed_delay = 500
        
        for text, delay in self.speed_options:
            ttk.Radiobutton(
                self.speed_frame, 
                text=text, 
                variable=self.speed_var, 
                value=text,
                command=lambda t=text, d=delay: self.change_speed(t, d)
            ).pack(side=tk.LEFT, padx=5)
        
        # Статус
        self.status_var = tk.StringVar(value="Программа запущена. Нажмите 'Продолжить' для старта")
        self.status_label = ttk.Label(self.root, textvariable=self.status_var, font=('Arial', 12))
        self.status_label.pack(pady=5)
        
        # Данные графа и состояния алгоритма
        self.graph = {}
        self.positions = {}
        self.original_positions = {}  # Сохраняем оригинальные позиции для сброса масштаба
        self.history = []
        self.current_history_index = -1
        self.pause = True
        self.algorithm_finished = False
        self.auto_animation_id = None
        self.algorithm_result = ""
        
        # Инициализация стандартного графа
        self.initialize_default_graph()
        self.initialize_algorithm()
    
    def zoom(self, event):
        """Масштабирование с помощью колесика мыши"""
        if event.delta > 0 or event.num == 4:  # Приближение
            self.zoom_level *= self.zoom_factor
        else:  # Отдаление
            self.zoom_level /= self.zoom_factor
        
        # Ограничиваем масштаб
        self.zoom_level = max(0.1, min(5.0, self.zoom_level))
        
        # Перерисовываем граф с новым масштабом
        self.draw_graph()
        
        # Обновляем статус
        self.status_var.set(f"Масштаб: {self.zoom_level:.1%}")
    
    def zoom_manual(self, direction):
        """Масштабирование с помощью кнопок"""
        if direction > 0:  # Приближение
            self.zoom_level *= self.zoom_factor
        else:  # Отдаление
            self.zoom_level /= self.zoom_factor
        
        # Ограничиваем масштаб
        self.zoom_level = max(0.1, min(5.0, self.zoom_level))
        
        # Перерисовываем граф с новым масштабом
        self.draw_graph()
        
        # Обновляем статус
        self.status_var.set(f"Масштаб: {self.zoom_level:.1%}")
    
    def reset_view(self):
        """Сброс масштаба и положения"""
        self.zoom_level = 1.0
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        self.draw_graph()
        self.status_var.set("Вид сброшен")
    
    def start_pan(self, event):
        """Начало панорамирования"""
        self.is_panning = True
        self.pan_start_x = event.x
        self.pan_start_y = event.y
    
    def pan(self, event):
        """Панорамирование"""
        if self.is_panning:
            dx = event.x - self.pan_start_x
            dy = event.y - self.pan_start_y
            self.pan_offset_x += dx
            self.pan_offset_y += dy
            self.pan_start_x = event.x
            self.pan_start_y = event.y
            self.draw_graph()
    
    def end_pan(self, event):
        """Конец панорамирования"""
        self.is_panning = False
    
    def get_transformed_position(self, x, y):
        """Получает трансформированные координаты с учетом масштаба и панорамирования"""
        # Центр холста
        center_x, center_y = 500, 300
        
        # Применяем масштаб и смещение
        transformed_x = center_x + (x - center_x + self.pan_offset_x) * self.zoom_level
        transformed_y = center_y + (y - center_y + self.pan_offset_y) * self.zoom_level
        
        return transformed_x, transformed_y
    
    def load_graph_from_file(self):
        """Загружает граф из файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите файл с графом",
            filetypes=[
                ("Текстовые файлы", "*.txt"),
                ("Все файлы", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            # Парсинг файла
            edges = []
            start_node = None
            end_node = None
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Обработка START и END команд
                if line.upper().startswith('START'):
                    start_node = line.split()[1]
                    continue
                elif line.upper().startswith('END'):
                    end_node = line.split()[1]
                    continue
                
                # Обработка ребер (формат: A B 5)
                parts = line.split()
                if len(parts) >= 3:
                    u, v = parts[0], parts[1]
                    try:
                        weight = float(parts[2])
                        edges.append((u, v, weight))
                    except ValueError:
                        print(f"Ошибка в весе ребра: {line}")
            
            if not edges:
                messagebox.showerror("Ошибка", "Файл не содержит корректных ребер графа")
                return
            
            # Создаем граф
            self.graph = {}
            for u, v, weight in edges:
                self.graph[(u, v)] = weight
                self.graph[(v, u)] = weight  # Делаем неориентированным
            
            # Автоматическая расстановка позиций
            self.calculate_positions()
            
            # Устанавливаем старт и финиш
            self.start_node = start_node if start_node else list(self.positions.keys())[0]
            self.end_node = end_node if end_node else list(self.positions.keys())[-1]
            
            # Сохраняем оригинальные позиции
            self.original_positions = self.positions.copy()
            
            # Переинициализируем алгоритм
            self.restart()
            
            messagebox.showinfo("Успех", f"Граф загружен!\nРебер: {len(edges)}\nУзлов: {len(self.positions)}\nСтарт: {self.start_node}, Конец: {self.end_node}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{str(e)}")
    
    def calculate_positions(self):
        """Автоматически расставляет позиции узлов на холсте"""
        nodes = list(set([node for edge in self.graph.keys() for node in edge]))
        self.positions = {}
        
        center_x, center_y = 500, 300
        radius = min(400, 50 * len(nodes))  # Автоматический радиус
        
        for i, node in enumerate(nodes):
            angle = 2 * math.pi * i / len(nodes)
            self.positions[node] = (
                center_x + radius * math.cos(angle),
                center_y + radius * math.sin(angle)
            )
        
        # Сохраняем оригинальные позиции
        self.original_positions = self.positions.copy()
    
    def initialize_default_graph(self):
        """Инициализация стандартного графа по умолчанию"""
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
        
        # Позиции узлов
        center_x, center_y = 500, 300
        
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
        
        # Сохраняем оригинальные позиции
        self.original_positions = self.positions.copy()
    
    def change_speed(self, speed_name, delay_ms):
        """Изменяет скорость анимации"""
        self.current_speed_delay = delay_ms
        self.status_var.set(f"Скорость изменена на: {speed_name} ({delay_ms}мс/шаг)")
        
        if not self.pause and not self.algorithm_finished:
            if self.auto_animation_id:
                self.root.after_cancel(self.auto_animation_id)
            self.auto_animate()
    
    def initialize_algorithm(self):
        """Инициализация алгоритма"""
        # Состояние алгоритма
        self.distances = {node: float('inf') for node in self.positions}
        if hasattr(self, 'start_node'):
            self.distances[self.start_node] = 0
        self.visited = set()
        self.previous = {}
        self.current_node = None
        self.final_path = None
        self.algorithm_finished = False
        self.algorithm_result = ""
        
        if self.algorithm_var.get() == "dijkstra" and hasattr(self, 'start_node'):
            self.pq = [(0, self.start_node)]
        else:
            self.edges = self.get_edges_list()
            self.iteration = 0
            self.edge_index = 0
        
        self.history.clear()
        self.save_state("Начальное состояние")
    
    def get_edges_list(self):
        """Преобразует граф в список ребер для Беллмана-Форда"""
        edges = []
        for (u, v), weight in self.graph.items():
            edges.append((u, v, weight))
        return edges
    
    def get_neighbors(self, node):
        """Получает всех соседей узла"""
        neighbors = {}
        for (u, v), weight in self.graph.items():
            if u == node:
                neighbors[v] = weight
            elif v == node:
                neighbors[u] = weight
        return neighbors
    
    def save_state(self, description):
        """Сохраняет текущее состояние в историю"""
        state = {
            'distances': self.distances.copy(),
            'visited': self.visited.copy(),
            'current_node': self.current_node,
            'previous': self.previous.copy(),
            'description': description,
            'final_path': self.final_path.copy() if self.final_path else None,
            'algorithm_finished': self.algorithm_finished,
            'algorithm_result': self.algorithm_result
        }
        if hasattr(self, 'iteration'):
            state['iteration'] = self.iteration
            state['edge_index'] = self.edge_index
        
        self.history.append(state)
        self.current_history_index = len(self.history) - 1
    
    def load_state(self, index):
        """Загружает состояние из истории"""
        if 0 <= index < len(self.history):
            state = self.history[index]
            self.distances = state['distances'].copy()
            self.visited = state['visited'].copy()
            self.current_node = state['current_node']
            self.previous = state['previous'].copy()
            self.final_path = state['final_path'].copy() if state['final_path'] else None
            self.algorithm_finished = state['algorithm_finished']
            self.algorithm_result = state['algorithm_result']
            self.current_history_index = index
            
            if 'iteration' in state:
                self.iteration = state['iteration']
                self.edge_index = state['edge_index']
            return True
        return False
    
    def dijkstra_step(self):
        """Выполняет один шаг алгоритма Дейкстры"""
        if not hasattr(self, 'pq') or not self.pq:
            self.algorithm_finished = True
            self.reconstruct_path()
            return False
        
        current_dist, self.current_node = heapq.heappop(self.pq)
        
        if self.current_node in self.visited:
            return True
        
        self.visited.add(self.current_node)
        self.save_state(f"Обрабатываем узел {self.current_node} (расстояние: {current_dist})")
        
        if hasattr(self, 'end_node') and self.current_node == self.end_node:
            self.algorithm_finished = True
            self.reconstruct_path()
            return False
        
        neighbors = self.get_neighbors(self.current_node)
        updated = False
        for neighbor, weight in neighbors.items():
            if neighbor not in self.visited:
                new_dist = current_dist + weight
                if new_dist < self.distances[neighbor]:
                    self.distances[neighbor] = new_dist
                    heapq.heappush(self.pq, (new_dist, neighbor))
                    self.previous[neighbor] = self.current_node
                    updated = True
        
        if updated:
            self.save_state(f"Обновлены расстояния после узла {self.current_node}")
        
        return True
    
    def bellman_ford_step(self):
        """Выполняет один шаг алгоритма Беллмана-Форда"""
        if not hasattr(self, 'edges'):
            return False
            
        if self.iteration >= len(self.positions) - 1:
            if self.edge_index < len(self.edges):
                u, v, weight = self.edges[self.edge_index]
                if self.distances[u] != float('inf') and self.distances[u] + weight < self.distances[v]:
                    self.algorithm_finished = True
                    self.algorithm_result = f"Обнаружен отрицательный цикл! {u}→{v}"
                    self.save_state(f"Обнаружен отрицательный цикл! {u}→{v}")
                    return False
                self.edge_index += 1
                return True
            else:
                self.algorithm_finished = True
                self.reconstruct_path()
                return False
        
        if self.edge_index < len(self.edges):
            u, v, weight = self.edges[self.edge_index]
            self.current_node = u
            
            old_distance = self.distances[v]
            if self.distances[u] != float('inf') and self.distances[u] + weight < self.distances[v]:
                self.distances[v] = self.distances[u] + weight
                self.previous[v] = u
                self.save_state(f"Итерация {self.iteration+1}: {u}→{v} ({weight}) - обновлено {old_distance}→{self.distances[v]}")
            else:
                self.save_state(f"Итерация {self.iteration+1}: {u}→{v} ({weight}) - без изменений")
            
            self.edge_index += 1
        else:
            self.iteration += 1
            self.edge_index = 0
            self.current_node = None
            self.save_state(f"Начало итерации {self.iteration+1}")
        
        return True
    
    def reconstruct_path(self):
        """Восстанавливает кратчайший путь"""
        if not hasattr(self, 'end_node') or not hasattr(self, 'start_node'):
            self.final_path = None
            self.algorithm_result = "Старт или финиш не установлены"
            self.save_state("Старт или финиш не установлены")
            return
            
        if self.end_node not in self.previous or self.distances[self.end_node] == float('inf'):
            self.final_path = None
            self.algorithm_result = f"Путь от {self.start_node} до {self.end_node} не найден"
            self.save_state(f"Путь от {self.start_node} до {self.end_node} не найден")
        else:
            path = []
            current = self.end_node
            while current != self.start_node:
                path.append(current)
                current = self.previous[current]
            path.append(self.start_node)
            path.reverse()
            self.final_path = path
            path_length = self.distances[self.end_node]
            self.algorithm_result = f"Найден путь: {' → '.join(path)} (длина: {path_length})"
            self.save_state(f"Найден путь: {' → '.join(path)} (длина: {path_length})")
    
    def algorithm_step(self):
        """Выполняет один шаг текущего алгоритма"""
        if not hasattr(self, 'start_node'):
            messagebox.showwarning("Предупреждение", "Сначала загрузите граф и установите стартовый узел")
            return False
            
        if self.algorithm_var.get() == "dijkstra":
            return self.dijkstra_step()
        else:
            return self.bellman_ford_step()
    
    def draw_graph(self):
        """Рисует граф на холсте с текущим состоянием алгоритма"""
        self.canvas.delete("all")
        
        if not self.graph:
            self.canvas.create_text(500, 300, text="Граф не загружен\nНажмите 'Загрузить граф'", 
                                  font=('Arial', 16), fill="gray")
            return
        
        # Рисуем ребра
        for (u, v), weight in self.graph.items():
            if u in self.positions and v in self.positions:
                # Получаем трансформированные координаты
                x1, y1 = self.get_transformed_position(*self.positions[u])
                x2, y2 = self.get_transformed_position(*self.positions[v])
                
                edge_color = "gray"
                edge_width = max(1, int(2 * self.zoom_level))  # Масштабируем ширину линии
                
                if self.final_path and u in self.final_path and v in self.final_path:
                    try:
                        if abs(self.final_path.index(u) - self.final_path.index(v)) == 1:
                            edge_color = "blue"
                            edge_width = max(2, int(4 * self.zoom_level))
                    except ValueError:
                        pass
                
                self.canvas.create_line(x1, y1, x2, y2, width=edge_width, fill=edge_color)
                
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2
                offset_x = (y2 - y1) * 0.1
                offset_y = -(x2 - x1) * 0.1
                
                # Масштабируем размер шрифта
                font_size = max(8, int(10 * self.zoom_level))
                
                self.canvas.create_text(
                    mid_x + offset_x, mid_y + offset_y,
                    text=str(weight), fill="darkblue",
                    font=('Arial', font_size, 'bold')
                )
        
        # Рисуем узлы
        for node, (orig_x, orig_y) in self.positions.items():
            # Получаем трансформированные координаты
            x, y = self.get_transformed_position(orig_x, orig_y)
            
            if node == self.current_node:
                fill_color = "red"
            elif node in self.visited:
                fill_color = "green"
            elif self.final_path and node in self.final_path:
                fill_color = "blue"
            else:
                fill_color = "lightgray"
            
            # Особые цвета для старта и финиша
            if hasattr(self, 'start_node') and node == self.start_node:
                fill_color = "orange"
            if hasattr(self, 'end_node') and node == self.end_node:
                fill_color = "purple"
            
            node_radius = max(15, int(20 * self.zoom_level))  # Масштабируем радиус узла
            self.canvas.create_oval(
                x - node_radius, y - node_radius,
                x + node_radius, y + node_radius,
                fill=fill_color, outline="black", width=max(1, int(2 * self.zoom_level))
            )
            
            text_color = "white" if fill_color in ["red", "green", "blue", "orange", "purple"] else "black"
            font_size = max(8, int(12 * self.zoom_level))
            
            self.canvas.create_text(x, y, text=node, fill=text_color, font=('Arial', font_size, 'bold'))
            
            if node in self.distances and self.distances[node] != float('inf'):
                dist_text = f"{self.distances[node]}"
                dist_font_size = max(6, int(10 * self.zoom_level))
                self.canvas.create_text(
                    x + 30 * self.zoom_level, y - 30 * self.zoom_level,
                    text=dist_text, fill="darkred",
                    font=('Arial', dist_font_size, 'bold')
                )
        
        # Рисуем легенду
        self.draw_legend()
        
        # Обновляем статус
        if self.algorithm_finished and self.algorithm_result:
            # Показываем финальный результат
            status_text = f"✅ {self.algorithm_result}"
        elif self.current_history_index >= 0 and self.history:
            current_state = self.history[self.current_history_index]
            status_text = f"{current_state['description']} | Шаг {self.current_history_index + 1}/{len(self.history)}"
            if hasattr(self, 'iteration'):
                status_text += f" | Итерация: {self.iteration}"
            
            if self.pause and not self.algorithm_finished:
                status_text += " | ⏸️ ПАУЗА"
        else:
            status_text = "⏸️ Программа запущена в режиме паузы"
        
        # Добавляем информацию о масштабе
        if abs(self.zoom_level - 1.0) > 0.01 or self.pan_offset_x != 0 or self.pan_offset_y != 0:
            status_text += f" | Масштаб: {self.zoom_level:.1%}"
        
        self.status_var.set(status_text)
    
    def draw_legend(self):
        """Рисует легенду на холсте"""
        legend_x, legend_y = 20, 20
        legend_items = [
            ("Текущий узел", "red"),
            ("Посещенный", "green"),
            ("Кратчайший путь", "blue"),
            ("Старт", "orange"),
            ("Финиш", "purple"),
            ("Не посещенный", "lightgray")
        ]
        
        for text, color in legend_items:
            self.canvas.create_rectangle(legend_x, legend_y, legend_x + 15, legend_y + 15, fill=color, outline="black")
            self.canvas.create_text(legend_x + 25, legend_y + 7, text=text, anchor=tk.W, font=('Arial', 10))
            legend_y += 25
        
        if hasattr(self, 'start_node') and hasattr(self, 'end_node'):
            algo_name = "Дейкстра" if self.algorithm_var.get() == "dijkstra" else "Беллман-Форд"
            self.canvas.create_text(legend_x, legend_y + 10, text=f"Алгоритм: {algo_name}", anchor=tk.W, font=('Arial', 10, 'bold'))
            self.canvas.create_text(legend_x, legend_y + 30, text=f"Старт: {self.start_node}, Конец: {self.end_node}", anchor=tk.W, font=('Arial', 10))
            
            speed_text = f"Скорость: {self.speed_var.get()} ({self.current_speed_delay}мс/шаг)"
            self.canvas.create_text(legend_x, legend_y + 50, text=speed_text, anchor=tk.W, font=('Arial', 9))
            
            # Информация о масштабе
            scale_text = f"Масштаб: {self.zoom_level:.1%}"
            self.canvas.create_text(legend_x, legend_y + 70, text=scale_text, anchor=tk.W, font=('Arial', 9))
            
            # Информация о состоянии
            if self.algorithm_finished and self.algorithm_result:
                # Показываем сокращенный результат на графе
                if "Найден путь" in self.algorithm_result:
                    result_line = self.algorithm_result.split("(")[0]  # Берем только часть до длины
                    self.canvas.create_text(legend_x, legend_y + 90, text=f"✅ {result_line}", anchor=tk.W, font=('Arial', 9, 'bold'))
                else:
                    self.canvas.create_text(legend_x, legend_y + 90, text=f"❌ {self.algorithm_result}", anchor=tk.W, font=('Arial', 9, 'bold'))
            else:
                state_info = "⏸️ ПАУЗА" if self.pause else "▶️ ВЫПОЛНЕНИЕ"
                self.canvas.create_text(legend_x, legend_y + 90, text=f"Состояние: {state_info}", anchor=tk.W, font=('Arial', 10, 'bold'))
    
    def step_forward(self):
        """Шаг вперед в алгоритме"""
        if not self.algorithm_finished:
            if self.algorithm_step():
                self.draw_graph()
            else:
                self.draw_graph()
    
    def step_backward(self):
        """Шаг назад"""
        if self.current_history_index > 0:
            if self.load_state(self.current_history_index - 1):
                self.draw_graph()
    
    def toggle_pause(self):
        """Переключение паузы"""
        self.pause = not self.pause
        
        if self.pause:
            if self.auto_animation_id:
                self.root.after_cancel(self.auto_animation_id)
                self.auto_animation_id = None
            self.pause_btn.config(text="▶️ Продолжить")
            if self.algorithm_finished and self.algorithm_result:
                self.status_var.set(f"✅ {self.algorithm_result}")
            else:
                self.status_var.set("⏸️ Пауза - используйте кнопки для пошагового выполнения")
        else:
            self.pause_btn.config(text="⏸️ Пауза")
            self.status_var.set("▶️ Выполнение алгоритма...")
            self.auto_animate()
    
    def restart(self):
        """Перезапуск алгоритма"""
        if self.auto_animation_id:
            self.root.after_cancel(self.auto_animation_id)
            self.auto_animation_id = None
        
        self.initialize_algorithm()
        self.pause = True
        self.pause_btn.config(text="▶️ Продолжить")
        self.status_var.set("🔄 Алгоритм перезапущен. Нажмите 'Продолжить' для старта")
        self.draw_graph()
    
    def auto_animate(self):
        """Автоматическая анимация с учетом выбранной скорости"""
        if not self.pause and not self.algorithm_finished:
            self.step_forward()
            self.auto_animation_id = self.root.after(self.current_speed_delay, self.auto_animate)
        elif not self.pause and self.algorithm_finished:
            self.pause = True
            self.pause_btn.config(text="▶️ Продолжить")
            # Показываем результат алгоритма в статусе
            if self.algorithm_result:
                self.status_var.set(f"✅ {self.algorithm_result}")
            else:
                self.status_var.set("✅ Алгоритм завершен!")
    
    def run(self):
        """Запуск приложения"""
        self.draw_graph()
        self.status_var.set("⏸️ Программа запущена в режиме паузы. Нажмите 'Загрузить граф' или 'Продолжить'")
        self.root.mainloop()

# Запуск приложения
if __name__ == "__main__":
    app = GraphVisualizerTkinter()
    print("Tkinter визуализатор алгоритмов запущен!")
    print("Функции:")
    print("  - Загрузка графа из файла (формат: A B 5)")
    print("  - Управление скоростью анимации")
    print("  - Алгоритмы: Дейкстра и Беллман-Форд")
    print("  - Пошаговое выполнение и перемотка")
    print("  - Масштабирование колесиком мыши")
    print("  - Панорамирование средней кнопкой мыши")
    print("  - Кнопки приближения/отдаления")
    print("\nПример файла графа:")
    print("A B 4")
    print("B C 3")
    print("START A")
    print("END C")
    app.run()