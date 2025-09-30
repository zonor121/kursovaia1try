import tkinter as tk
from tkinter import ttk
import math
import heapq
from collections import deque

class GraphVisualizerTkinter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Визуализация алгоритмов кратчайшего пути - Tkinter")
        self.root.geometry("1200x800")
        
        # Холст для рисования
        self.canvas = tk.Canvas(self.root, width=1000, height=600, bg='white', highlightthickness=1, highlightbackground="gray")
        self.canvas.pack(pady=10)
        
        # Панель управления
        self.control_frame = ttk.Frame(self.root)
        self.control_frame.pack(pady=10)
        
        self.step_forward_btn = ttk.Button(self.control_frame, text="Шаг вперед →", command=self.step_forward)
        self.step_forward_btn.pack(side=tk.LEFT, padx=5)
        
        self.step_backward_btn = ttk.Button(self.control_frame, text="← Шаг назад", command=self.step_backward)
        self.step_backward_btn.pack(side=tk.LEFT, padx=5)
        
        self.pause_btn = ttk.Button(self.control_frame, text="⏸️ Пауза", command=self.toggle_pause)
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        
        self.restart_btn = ttk.Button(self.control_frame, text="🔄 Перезапуск", command=self.restart)
        self.restart_btn.pack(side=tk.LEFT, padx=5)
        
        # Выбор алгоритма
        self.algorithm_var = tk.StringVar(value="dijkstra")
        algo_frame = ttk.Frame(self.control_frame)
        algo_frame.pack(side=tk.LEFT, padx=20)
        ttk.Radiobutton(algo_frame, text="Дейкстра", variable=self.algorithm_var, value="dijkstra").pack(side=tk.LEFT)
        ttk.Radiobutton(algo_frame, text="Беллман-Форд", variable=self.algorithm_var, value="bellman").pack(side=tk.LEFT)
        
        # Статус
        self.status_var = tk.StringVar(value="Запуск алгоритма...")
        self.status_label = ttk.Label(self.root, textvariable=self.status_var, font=('Arial', 12))
        self.status_label.pack(pady=5)
        
        # Данные графа и состояния алгоритма
        self.graph = {}
        self.positions = {}
        self.history = []
        self.current_history_index = -1
        self.pause = False  # Теперь начинаем без паузы!
        self.algorithm_finished = False
        
        # Инициализация
        self.initialize_graph()
        self.initialize_algorithm()
        
    def initialize_graph(self):
        """Инициализация тестового графа"""
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
    
    def initialize_algorithm(self):
        """Инициализация алгоритма"""
        self.start_node = 'G'
        self.end_node = 'D'
        
        # Состояние алгоритма
        self.distances = {node: float('inf') for node in self.positions}
        self.distances[self.start_node] = 0
        self.visited = set()
        self.previous = {}
        self.current_node = None
        self.final_path = None
        self.algorithm_finished = False
        
        if self.algorithm_var.get() == "dijkstra":
            self.pq = [(0, self.start_node)]
        else:  # bellman-ford
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
            'algorithm_finished': self.algorithm_finished
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
            self.current_history_index = index
            
            if 'iteration' in state:
                self.iteration = state['iteration']
                self.edge_index = state['edge_index']
            return True
        return False
    
    def dijkstra_step(self):
        """Выполняет один шаг алгоритма Дейкстры"""
        if not self.pq:
            self.algorithm_finished = True
            self.reconstruct_path()
            return False
        
        current_dist, self.current_node = heapq.heappop(self.pq)
        
        # Пропускаем если уже посещен
        if self.current_node in self.visited:
            return True
        
        self.visited.add(self.current_node)
        self.save_state(f"Обрабатываем узел {self.current_node} (расстояние: {current_dist})")
        
        # Проверяем достигли ли конечной точки
        if self.current_node == self.end_node:
            self.algorithm_finished = True
            self.reconstruct_path()
            return False
        
        # Обрабатываем соседей
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
        if self.iteration >= len(self.positions) - 1:
            # Проверка на отрицательные циклы
            if self.edge_index < len(self.edges):
                u, v, weight = self.edges[self.edge_index]
                if self.distances[u] != float('inf') and self.distances[u] + weight < self.distances[v]:
                    self.algorithm_finished = True
                    self.save_state(f"Обнаружен отрицательный цикл! {u}→{v}")
                    return False
                self.edge_index += 1
                return True
            else:
                self.algorithm_finished = True
                self.reconstruct_path()
                return False
        
        # Основная релаксация
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
            # Конец итерации
            self.iteration += 1
            self.edge_index = 0
            self.current_node = None
            self.save_state(f"Начало итерации {self.iteration+1}")
        
        return True
    
    def reconstruct_path(self):
        """Восстанавливает кратчайший путь"""
        if self.end_node not in self.previous or self.distances[self.end_node] == float('inf'):
            self.final_path = None
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
            self.save_state(f"Найден путь: {' → '.join(path)} (длина: {self.distances[self.end_node]})")
    
    def algorithm_step(self):
        """Выполняет один шаг текущего алгоритма"""
        if self.algorithm_var.get() == "dijkstra":
            return self.dijkstra_step()
        else:
            return self.bellman_ford_step()
    
    def draw_graph(self):
        """Рисует граф на холсте с текущим состоянием алгоритма"""
        self.canvas.delete("all")
        
        # Рисуем ребра
        for (u, v), weight in self.graph.items():
            if u in self.positions and v in self.positions:
                x1, y1 = self.positions[u]
                x2, y2 = self.positions[v]
                
                # Определяем цвет ребра
                edge_color = "gray"
                edge_width = 2
                
                if self.final_path and u in self.final_path and v in self.final_path:
                    try:
                        if abs(self.final_path.index(u) - self.final_path.index(v)) == 1:
                            edge_color = "blue"
                            edge_width = 4
                    except ValueError:
                        pass
                
                # Рисуем линию ребра
                self.canvas.create_line(x1, y1, x2, y2, width=edge_width, fill=edge_color)
                
                # Подписываем вес ребра
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2
                offset_x = (y2 - y1) * 0.1
                offset_y = -(x2 - x1) * 0.1
                
                self.canvas.create_text(
                    mid_x + offset_x, mid_y + offset_y,
                    text=str(weight), fill="darkblue",
                    font=('Arial', 10, 'bold')
                )
        
        # Рисуем узлы
        for node, (x, y) in self.positions.items():
            # Определяем цвет узла
            if node == self.current_node:
                fill_color = "red"  # Текущий обрабатываемый узел
            elif node in self.visited:
                fill_color = "green"  # Посещенные узлы
            elif self.final_path and node in self.final_path:
                fill_color = "blue"  # Узлы конечного пути
            else:
                fill_color = "lightgray"  # Непосещенные узлы
            
            # Рисуем узел
            node_radius = 20
            self.canvas.create_oval(
                x - node_radius, y - node_radius,
                x + node_radius, y + node_radius,
                fill=fill_color, outline="black", width=2
            )
            
            # Подписываем узел
            text_color = "white" if fill_color in ["red", "green", "blue"] else "black"
            self.canvas.create_text(x, y, text=node, fill=text_color, font=('Arial', 12, 'bold'))
            
            # Отображаем расстояние
            if node in self.distances and self.distances[node] != float('inf'):
                dist_text = f"{self.distances[node]}"
                self.canvas.create_text(
                    x + 30, y - 30,
                    text=dist_text, fill="darkred",
                    font=('Arial', 10, 'bold')
                )
        
        # Рисуем легенду
        self.draw_legend()
        
        # Обновляем статус
        if self.current_history_index >= 0 and self.history:
            current_state = self.history[self.current_history_index]
            status_text = f"{current_state['description']} | Шаг {self.current_history_index + 1}/{len(self.history)}"
            if hasattr(self, 'iteration'):
                status_text += f" | Итерация: {self.iteration}"
            self.status_var.set(status_text)
    
    def draw_legend(self):
        """Рисует легенду на холсте"""
        legend_x, legend_y = 20, 20
        legend_items = [
            ("Текущий узел", "red"),
            ("Посещенный", "green"),
            ("Кратчайший путь", "blue"),
            ("Не посещенный", "lightgray")
        ]
        
        for text, color in legend_items:
            self.canvas.create_rectangle(legend_x, legend_y, legend_x + 15, legend_y + 15, fill=color, outline="black")
            self.canvas.create_text(legend_x + 25, legend_y + 7, text=text, anchor=tk.W, font=('Arial', 10))
            legend_y += 25
        
        # Информация об алгоритме
        algo_name = "Дейкстра" if self.algorithm_var.get() == "dijkstra" else "Беллман-Форд"
        self.canvas.create_text(legend_x, legend_y + 10, text=f"Алгоритм: {algo_name}", anchor=tk.W, font=('Arial', 10, 'bold'))
        self.canvas.create_text(legend_x, legend_y + 30, text=f"Старт: {self.start_node}, Конец: {self.end_node}", anchor=tk.W, font=('Arial', 10))
    
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
            self.pause_btn.config(text="▶️ Продолжить")
            self.status_var.set("Пауза")
        else:
            self.pause_btn.config(text="⏸️ Пауза")
            self.status_var.set("Выполнение...")
            self.auto_animate()
    
    def restart(self):
        """Перезапуск алгоритма"""
        self.initialize_algorithm()
        self.pause = False  # Автоматически продолжаем после перезапуска
        self.pause_btn.config(text="⏸️ Пауза")
        self.status_var.set("Перезапуск...")
        self.draw_graph()
        # Запускаем автоматическую анимацию после перезапуска
        self.root.after(500, self.auto_animate)
    
    def auto_animate(self):
        """Автоматическая анимация"""
        if not self.pause and not self.algorithm_finished:
            self.step_forward()
            self.root.after(800, self.auto_animate)  # Задержка 800ms между шагами
        elif not self.pause and self.algorithm_finished:
            self.pause = True
            self.pause_btn.config(text="▶️ Продолжить")
            self.status_var.set("Алгоритм завершен!")
    
    def run(self):
        """Запуск приложения"""
        self.draw_graph()
        # Запускаем автоматическую анимацию при старте
        self.root.after(1000, self.auto_animate)  # Начинаем через 1 секунду
        self.root.mainloop()

# Запуск приложения
if __name__ == "__main__":
    app = GraphVisualizerTkinter()
    print("Tkinter визуализатор алгоритмов запущен!")
    print("Алгоритмы: Дейкстра и Беллман-Форд")
    print("Старт: G, Конец: D")
    print("Программа запустится автоматически через 1 секунду...")
    app.run()