import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import math
import heapq

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
        
        # Привязка событий мыши
        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<Button-4>", self.zoom)
        self.canvas.bind("<Button-5>", self.zoom)
        self.canvas.bind("<ButtonPress-2>", self.start_pan)
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
        
        self.dijkstra_radio = ttk.Radiobutton(algo_frame, text="Дейкстра", variable=self.algorithm_var, value="dijkstra", command=self.on_algorithm_change)
        self.dijkstra_radio.pack(side=tk.LEFT)
        
        self.bellman_radio = ttk.Radiobutton(algo_frame, text="Беллман-Форд", variable=self.algorithm_var, value="bellman", command=self.on_algorithm_change)
        self.bellman_radio.pack(side=tk.LEFT)
        
        # Панель выбора начальной и конечной точек
        self.selection_frame = ttk.Frame(self.root)
        self.selection_frame.pack(pady=5)
        
        ttk.Label(self.selection_frame, text="Старт:", font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        self.start_var = tk.StringVar()
        self.start_combo = ttk.Combobox(self.selection_frame, textvariable=self.start_var, width=5, state="readonly")
        self.start_combo.pack(side=tk.LEFT, padx=5)
        self.start_combo.bind('<<ComboboxSelected>>', self.on_start_change)
        
        ttk.Label(self.selection_frame, text="Конец:", font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        self.end_var = tk.StringVar()
        self.end_combo = ttk.Combobox(self.selection_frame, textvariable=self.end_var, width=5, state="readonly")
        self.end_combo.pack(side=tk.LEFT, padx=5)
        self.end_combo.bind('<<ComboboxSelected>>', self.on_end_change)
        
        self.apply_btn = ttk.Button(self.selection_frame, text="Применить", command=self.apply_selection)
        self.apply_btn.pack(side=tk.LEFT, padx=10)
        
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
        
        # Таблица результатов для Беллмана-Форда
        self.results_frame = ttk.Frame(self.root)
        self.results_frame.pack(pady=5, fill=tk.X, padx=10)
        
        ttk.Label(self.results_frame, text="Результаты Беллмана-Форда:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        # Создаем Treeview для таблицы
        self.results_tree = ttk.Treeview(self.results_frame, height=6, show='headings')
        self.results_tree.pack(fill=tk.X, pady=5)
        
        # Данные графа
        self.graph = {}
        self.positions = {}
        self.original_positions = {}
        self.history = []
        self.current_history_index = -1
        self.pause = True
        self.algorithm_finished = False
        self.auto_animation_id = None
        self.algorithm_result = ""
        self.has_negative_weights = False
        
        # Инициализация
        self.initialize_default_graph()
        self.initialize_algorithm()
    
    def update_results_table(self):
        """Обновляет таблицу результатов для Беллмана-Форда"""
        # Очищаем таблицу
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Настраиваем колонки
        self.results_tree['columns'] = ('node', 'distance', 'path')
        self.results_tree.column('node', width=80, anchor=tk.CENTER)
        self.results_tree.column('distance', width=120, anchor=tk.CENTER)
        self.results_tree.column('path', width=200, anchor=tk.W)
        
        self.results_tree.heading('node', text='Вершина')
        self.results_tree.heading('distance', text='Расстояние')
        self.results_tree.heading('path', text='Путь')
        
        # Заполняем таблицу данными
        if hasattr(self, 'distances') and hasattr(self, 'start_node'):
            for node in sorted(self.distances.keys()):
                distance = self.distances[node]
                if distance == float('inf'):
                    distance_str = "∞"
                    path_str = "Недостижима"
                else:
                    distance_str = f"{distance:.1f}"
                    # Восстанавливаем путь для этой вершины
                    path = self.reconstruct_path_to_node(node)
                    path_str = " → ".join(path) if path else "Старт"
                
                self.results_tree.insert('', 'end', values=(node, distance_str, path_str))
    
    def reconstruct_path_to_node(self, target_node):
        """Восстанавливает путь до указанной вершины"""
        if not hasattr(self, 'start_node') or not hasattr(self, 'previous'):
            return []
        
        if target_node == self.start_node:
            return [self.start_node]
        
        if target_node not in self.previous or self.distances[target_node] == float('inf'):
            return []
        
        path = []
        current = target_node
        while current != self.start_node:
            path.append(current)
            if current not in self.previous:
                return []
            current = self.previous[current]
        path.append(self.start_node)
        path.reverse()
        return path
    
    def update_selection_comboboxes(self):
        """Обновляет списки выбора начальной и конечной точек"""
        if self.positions:
            nodes = list(self.positions.keys())
            self.start_combo['values'] = nodes
            self.end_combo['values'] = nodes
            
            # Устанавливаем значения по умолчанию если они не установлены
            if not self.start_var.get() and hasattr(self, 'start_node'):
                self.start_var.set(self.start_node)
            if not self.end_var.get() and hasattr(self, 'end_node'):
                self.end_var.set(self.end_node)
    
    def on_start_change(self, event=None):
        """Обрабатывает изменение начальной точки"""
        new_start = self.start_var.get()
        if new_start and hasattr(self, 'start_node') and new_start != self.start_node:
            self.start_node = new_start
            self.status_var.set(f"Стартовая точка изменена на: {new_start}")
            self.restart()
    
    def on_end_change(self, event=None):
        """Обрабатывает изменение конечной точки"""
        new_end = self.end_var.get()
        if new_end and hasattr(self, 'end_node') and new_end != self.end_node:
            self.end_node = new_end
            self.status_var.set(f"Конечная точка изменена на: {new_end}")
            self.restart()
    
    def apply_selection(self):
        """Применяет выбранные начальную и конечную точки"""
        start = self.start_var.get()
        end = self.end_var.get()
        
        if not start or not end:
            messagebox.showwarning("Предупреждение", "Выберите начальную и конечную точки")
            return
        
        if start == end:
            messagebox.showwarning("Предупреждение", "Начальная и конечная точки не могут совпадать")
            return
        
        self.start_node = start
        self.end_node = end
        self.status_var.set(f"Установлены: Старт={start}, Конец={end}")
        self.restart()
    
    def check_negative_weights(self):
        """Проверяет наличие отрицательных весов в графе"""
        self.has_negative_weights = any(weight < 0 for weight in self.graph.values())
        return self.has_negative_weights
    
    def on_algorithm_change(self):
        """Обрабатывает изменение выбора алгоритма"""
        if self.algorithm_var.get() == "dijkstra" and self.has_negative_weights:
            messagebox.showwarning(
                "Предупреждение", 
                "Алгоритм Дейкстры не работает с отрицательными весами!\n"
                "Автоматически переключен на алгоритм Беллмана-Форда."
            )
            self.algorithm_var.set("bellman")
        
        # Показываем/скрываем таблицу результатов в зависимости от алгоритма
        if self.algorithm_var.get() == "bellman":
            self.results_frame.pack(pady=5, fill=tk.X, padx=10)
        else:
            self.results_frame.pack_forget()
        
        self.restart()
    
    def zoom(self, event):
        if event.delta > 0 or event.num == 4:
            self.zoom_level *= self.zoom_factor
        else:
            self.zoom_level /= self.zoom_factor
        
        self.zoom_level = max(0.1, min(5.0, self.zoom_level))
        self.draw_graph()
    
    def zoom_manual(self, direction):
        if direction > 0:
            self.zoom_level *= self.zoom_factor
        else:
            self.zoom_level /= self.zoom_factor
        
        self.zoom_level = max(0.1, min(5.0, self.zoom_level))
        self.draw_graph()
    
    def reset_view(self):
        self.zoom_level = 1.0
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        self.draw_graph()
    
    def start_pan(self, event):
        self.is_panning = True
        self.pan_start_x = event.x
        self.pan_start_y = event.y
    
    def pan(self, event):
        if self.is_panning:
            dx = event.x - self.pan_start_x
            dy = event.y - self.pan_start_y
            self.pan_offset_x += dx
            self.pan_offset_y += dy
            self.pan_start_x = event.x
            self.pan_start_y = event.y
            self.draw_graph()
    
    def end_pan(self, event):
        self.is_panning = False
    
    def get_transformed_position(self, x, y):
        center_x, center_y = 500, 300
        transformed_x = center_x + (x - center_x + self.pan_offset_x) * self.zoom_level
        transformed_y = center_y + (y - center_y + self.pan_offset_y) * self.zoom_level
        return transformed_x, transformed_y
    
    def load_graph_from_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите файл с графом",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
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
                messagebox.showerror("Ошибка", "Файл не содержит корректных ребер графа")
                return
            
            self.graph = {}
            for u, v, weight in edges:
                self.graph[(u, v)] = weight
                self.graph[(v, u)] = weight
            
            self.calculate_positions()
            
            # Устанавливаем старт и финиш из файла или по умолчанию
            self.start_node = start_node if start_node else list(self.positions.keys())[0]
            self.end_node = end_node if end_node else list(self.positions.keys())[-1]
            
            self.original_positions = self.positions.copy()
            
            # Обновляем комбобоксы выбора
            self.update_selection_comboboxes()
            
            # Проверяем отрицательные веса
            has_negative = self.check_negative_weights()
            
            # Если есть отрицательные веса и выбран Дейкстра - переключаем
            if has_negative and self.algorithm_var.get() == "dijkstra":
                messagebox.showwarning(
                    "Предупреждение", 
                    "Обнаружены отрицательные веса!\n"
                    "Алгоритм Дейкстры не работает с отрицательными весами.\n"
                    "Автоматически переключен на алгоритм Беллмана-Форда."
                )
                self.algorithm_var.set("bellman")
            
            # Показываем/скрываем таблицу результатов
            if self.algorithm_var.get() == "bellman":
                self.results_frame.pack(pady=5, fill=tk.X, padx=10)
            else:
                self.results_frame.pack_forget()
            
            self.restart()
            
            message_text = f"Граф загружен!\nРебер: {len(edges)}\nУзлов: {len(self.positions)}\nСтарт: {self.start_node}, Конец: {self.end_node}"
            if has_negative:
                message_text += f"\n⚠️ Обнаружены отрицательные веса!"
            
            messagebox.showinfo("Успех", message_text)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{str(e)}")
    
    def calculate_positions(self):
        nodes = list(set([node for edge in self.graph.keys() for node in edge]))
        self.positions = {}
        
        center_x, center_y = 500, 300
        radius = min(400, 50 * len(nodes))
        
        for i, node in enumerate(nodes):
            angle = 2 * math.pi * i / len(nodes)
            self.positions[node] = (
                center_x + radius * math.cos(angle),
                center_y + radius * math.sin(angle)
            )
        
        self.original_positions = self.positions.copy()
    
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
        self.original_positions = self.positions.copy()
        self.check_negative_weights()
        self.update_selection_comboboxes()
    
    def change_speed(self, speed_name, delay_ms):
        self.current_speed_delay = delay_ms
        self.status_var.set(f"Скорость изменена на: {speed_name} ({delay_ms}мс/шаг)")
        
        if not self.pause and not self.algorithm_finished:
            if self.auto_animation_id:
                self.root.after_cancel(self.auto_animation_id)
            self.auto_animate()
    
    def initialize_algorithm(self):
        # Шаг 1: Инициализация расстояний
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
            # Для Беллмана-Форда создаем список всех ребер
            self.edges = self.get_edges_list()
            self.iteration = 0
            self.edge_index = 0
            self.relaxation_occurred = False
        
        self.history.clear()
        self.save_state("Шаг 1: Инициализация расстояний")
        
        # Обновляем таблицу результатов для Беллмана-Форда
        if self.algorithm_var.get() == "bellman":
            self.update_results_table()
    
    def get_edges_list(self):
        """Создает список всех ребер для Беллмана-Форда"""
        edges = []
        for (u, v), weight in self.graph.items():
            edges.append((u, v, weight))
        return edges
    
    def get_neighbors(self, node):
        neighbors = {}
        for (u, v), weight in self.graph.items():
            if u == node:
                neighbors[v] = weight
            elif v == node:
                neighbors[u] = weight
        return neighbors
    
    def save_state(self, description):
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
            state['relaxation_occurred'] = getattr(self, 'relaxation_occurred', False)
        
        self.history.append(state)
        self.current_history_index = len(self.history) - 1
        
        # Обновляем таблицу результатов для Беллмана-Форда
        if self.algorithm_var.get() == "bellman":
            self.update_results_table()
    
    def load_state(self, index):
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
                self.relaxation_occurred = state['relaxation_occurred']
            
            # Обновляем таблицу результатов для Беллмана-Форда
            if self.algorithm_var.get() == "bellman":
                self.update_results_table()
            
            return True
        return False
    
    def dijkstra_step(self):
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
        """Корректный алгоритм Беллмана-Форда согласно описанию"""
        if not hasattr(self, 'edges'):
            return False
        
        # Шаг 2: |V|-1 итераций релаксации
        if self.iteration < len(self.positions) - 1:
            if self.edge_index < len(self.edges):
                u, v, weight = self.edges[self.edge_index]
                self.current_node = u
                
                # Релаксация ребра: если dist[v] > dist[u] + weight(u,v)
                if self.distances[u] != float('inf') and self.distances[u] + weight < self.distances[v]:
                    old_dist = self.distances[v]
                    self.distances[v] = self.distances[u] + weight
                    self.previous[v] = u
                    self.relaxation_occurred = True
                    self.save_state(f"Итерация {self.iteration+1}: {u}→{v} ({weight}) - обновлено {old_dist:.1f}→{self.distances[v]:.1f}")
                else:
                    self.save_state(f"Итерация {self.iteration+1}: {u}→{v} ({weight}) - без изменений")
                
                self.edge_index += 1
                return True
            else:
                # Завершили проход по всем ребрам для текущей итерации
                if self.relaxation_occurred:
                    # Были изменения - переходим к следующей итерации
                    self.iteration += 1
                    self.edge_index = 0
                    self.relaxation_occurred = False
                    self.current_node = None
                    self.save_state(f"Начало итерации {self.iteration+1}")
                    return True
                else:
                    # Не было изменений - алгоритм завершен
                    self.algorithm_finished = True
                    self.reconstruct_path()
                    return False
        
        # Шаг 3: Проверка на отрицательные циклы
        else:
            if self.edge_index < len(self.edges):
                u, v, weight = self.edges[self.edge_index]
                # Если dist[v] > dist[u] + weight(u,v) - найден отрицательный цикл
                if self.distances[u] != float('inf') and self.distances[u] + weight < self.distances[v]:
                    self.algorithm_finished = True
                    self.algorithm_result = f"Обнаружен отрицательный цикл! {u}→{v}"
                    self.save_state(f"Обнаружен отрицательный цикл! {u}→{v}")
                    return False
                self.edge_index += 1
                return True
            else:
                # Алгоритм завершен успешно
                self.algorithm_finished = True
                self.reconstruct_path()
                return False
    
    def reconstruct_path(self):
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
        if not hasattr(self, 'start_node'):
            messagebox.showwarning("Предупреждение", "Сначала загрузите граф и установите стартовый узел")
            return False
            
        if self.algorithm_var.get() == "dijkstra":
            if self.has_negative_weights:
                messagebox.showerror("Ошибка", "Алгоритм Дейкстры не работает с отрицательными весами!\nИспользуйте алгоритм Беллмана-Форда.")
                return False
            return self.dijkstra_step()
        else:
            return self.bellman_ford_step()
    
    def draw_graph(self):
        self.canvas.delete("all")
        
        if not self.graph:
            self.canvas.create_text(500, 300, text="Граф не загружен\nНажмите 'Загрузить граф'", 
                                  font=('Arial', 16), fill="gray")
            return
        
        # Рисуем ребра
        for (u, v), weight in self.graph.items():
            if u in self.positions and v in self.positions:
                x1, y1 = self.get_transformed_position(*self.positions[u])
                x2, y2 = self.get_transformed_position(*self.positions[v])
                
                edge_color = "gray"
                edge_width = max(1, int(2 * self.zoom_level))
                
                # Подсвечиваем отрицательные веса красным
                if weight < 0:
                    edge_color = "red"
                    edge_width = max(2, int(3 * self.zoom_level))
                
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
                
                font_size = max(8, int(10 * self.zoom_level))
                weight_color = "red" if weight < 0 else "darkblue"
                self.canvas.create_text(
                    mid_x + offset_x, mid_y + offset_y,
                    text=str(weight), fill=weight_color,
                    font=('Arial', font_size, 'bold')
                )
        
        # Рисуем узлы
        for node, (orig_x, orig_y) in self.positions.items():
            x, y = self.get_transformed_position(orig_x, orig_y)
            
            if node == self.current_node:
                fill_color = "red"
            elif node in self.visited:
                fill_color = "green"
            elif self.final_path and node in self.final_path:
                fill_color = "blue"
            else:
                fill_color = "lightgray"
            
            if hasattr(self, 'start_node') and node == self.start_node:
                fill_color = "orange"
            if hasattr(self, 'end_node') and node == self.end_node:
                fill_color = "purple"
            
            node_radius = max(15, int(20 * self.zoom_level))
            self.canvas.create_oval(
                x - node_radius, y - node_radius,
                x + node_radius, y + node_radius,
                fill=fill_color, outline="black", width=max(1, int(2 * self.zoom_level))
            )
            
            text_color = "white" if fill_color in ["red", "green", "blue", "orange", "purple"] else "black"
            font_size = max(8, int(12 * self.zoom_level))
            self.canvas.create_text(x, y, text=node, fill=text_color, font=('Arial', font_size, 'bold'))
            
            if node in self.distances and self.distances[node] != float('inf'):
                dist_text = f"{self.distances[node]:.1f}"
                dist_font_size = max(6, int(10 * self.zoom_level))
                self.canvas.create_text(
                    x + 30 * self.zoom_level, y - 30 * self.zoom_level,
                    text=dist_text, fill="darkred",
                    font=('Arial', dist_font_size, 'bold')
                )
        
        # Рисуем легенду
        self.draw_legend()
        
        # Обновляем статус (без информации о масштабе)
        if self.algorithm_finished and self.algorithm_result:
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
        
        self.status_var.set(status_text)
    
    def draw_legend(self):
        legend_x, legend_y = 20, 20
        legend_items = [
            ("Текущий узел", "red"),
            ("Посещенный", "green"),
            ("Кратчайший путь", "blue"),
            ("Старт", "orange"),
            ("Финиш", "purple"),
            ("Не посещенный", "lightgray")
        ]
        
        # Добавляем пункт для отрицательных весов если они есть
        if self.has_negative_weights:
            legend_items.append(("Отрицательный вес", "red"))
        
        for text, color in legend_items:
            self.canvas.create_rectangle(legend_x, legend_y, legend_x + 15, legend_y + 15, fill=color, outline="black")
            self.canvas.create_text(legend_x + 25, legend_y + 7, text=text, anchor=tk.W, font=('Arial', 10))
            legend_y += 25
        
        if hasattr(self, 'start_node') and hasattr(self, 'end_node'):
            algo_name = "Дейкстра" if self.algorithm_var.get() == "dijkstra" else "Беллман-Форд"
            algo_color = "red" if (self.algorithm_var.get() == "dijkstra" and self.has_negative_weights) else "black"
            self.canvas.create_text(legend_x, legend_y + 10, text=f"Алгоритм: {algo_name}", anchor=tk.W, font=('Arial', 10, 'bold'), fill=algo_color)
            self.canvas.create_text(legend_x, legend_y + 30, text=f"Старт: {self.start_node}, Конец: {self.end_node}", anchor=tk.W, font=('Arial', 10))
            
            speed_text = f"Скорость: {self.speed_var.get()} ({self.current_speed_delay}мс/шаг)"
            self.canvas.create_text(legend_x, legend_y + 50, text=speed_text, anchor=tk.W, font=('Arial', 9))
            
            # Предупреждение об отрицательных весах
            if self.has_negative_weights:
                warning_text = "⚠️ Обнаружены отрицательные веса!"
                self.canvas.create_text(legend_x, legend_y + 70, text=warning_text, anchor=tk.W, font=('Arial', 9, 'bold'), fill="red")
                legend_y += 20
            
            if self.algorithm_finished and self.algorithm_result:
                if "Найден путь" in self.algorithm_result:
                    result_line = self.algorithm_result.split("(")[0]
                    self.canvas.create_text(legend_x, legend_y + 70, text=f"✅ {result_line}", anchor=tk.W, font=('Arial', 9, 'bold'))
                else:
                    self.canvas.create_text(legend_x, legend_y + 70, text=f"❌ {self.algorithm_result}", anchor=tk.W, font=('Arial', 9, 'bold'))
            else:
                state_info = "⏸️ ПАУЗА" if self.pause else "▶️ ВЫПОЛНЕНИЕ"
                self.canvas.create_text(legend_x, legend_y + 70, text=f"Состояние: {state_info}", anchor=tk.W, font=('Arial', 10, 'bold'))
        
        # Информация о масштабе внизу холста
        scale_y = 580
        scale_text = f"Масштаб: {self.zoom_level:.1%}"
        self.canvas.create_text(legend_x, scale_y, text=scale_text, anchor=tk.W, font=('Arial', 10, 'bold'), fill="darkblue")
        
        if self.pan_offset_x != 0 or self.pan_offset_y != 0:
            pan_text = f"Смещение: ({self.pan_offset_x:.0f}, {self.pan_offset_y:.0f})"
            self.canvas.create_text(legend_x + 120, scale_y, text=pan_text, anchor=tk.W, font=('Arial', 10), fill="darkblue")
    
    def step_forward(self):
        if not self.algorithm_finished:
            if self.algorithm_step():
                self.draw_graph()
            else:
                self.draw_graph()
    
    def step_backward(self):
        if self.current_history_index > 0:
            if self.load_state(self.current_history_index - 1):
                self.draw_graph()
    
    def toggle_pause(self):
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
        if self.auto_animation_id:
            self.root.after_cancel(self.auto_animation_id)
            self.auto_animation_id = None
        
        self.initialize_algorithm()
        self.pause = True
        self.pause_btn.config(text="▶️ Продолжить")
        self.status_var.set("🔄 Алгоритм перезапущен. Нажмите 'Продолжить' для старта")
        self.draw_graph()
    
    def auto_animate(self):
        if not self.pause and not self.algorithm_finished:
            self.step_forward()
            self.auto_animation_id = self.root.after(self.current_speed_delay, self.auto_animate)
        elif not self.pause and self.algorithm_finished:
            self.pause = True
            self.pause_btn.config(text="▶️ Продолжить")
            if self.algorithm_result:
                self.status_var.set(f"✅ {self.algorithm_result}")
            else:
                self.status_var.set("✅ Алгоритм завершен!")
    
    def run(self):
        self.draw_graph()
        self.status_var.set("⏸️ Программа запущена в режиме паузы. Нажмите 'Загрузить граф' или 'Продолжить'")
        self.root.mainloop()

if __name__ == "__main__":
    app = GraphVisualizerTkinter()
    print("Tkinter визуализатор алгоритмов запущен!")
    print("Функции:")
    print("  - Загрузка графа из файла (формат: A B 5)")
    print("  - Управление скоростью анимации")
    print("  - Алгоритмы: Дейкстра и Беллман-Форд")
    print("  - Автоматическое определение отрицательных весов")
    print("  - Автопереключение на Беллмана-Форда при отрицательных весах")
    print("  - Выбор начальной и конечной точек через интерфейс")
    print("  - Таблица результатов для Беллмана-Форда (расстояния до всех вершин)")
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