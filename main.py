import pygame
import heapq
import math
import sys
from collections import deque
import copy

class AdvancedGraphVisualizer:
    def __init__(self, width=1000, height=800):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Визуализация алгоритма Дейкстры - Расширенная версия")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 20)
        self.large_font = pygame.font.Font(None, 28)
        self.title_font = pygame.font.Font(None, 32)
        
        # История для перемотки
        self.saved_states = deque(maxlen=100)
        self.current_history_index = -1
        
    def save_state(self, distances, visited, current, previous, pq, description):
        """Сохраняет текущее состояние для истории"""
        state = {
            'distances': copy.deepcopy(distances),
            'visited': copy.deepcopy(visited),
            'current': current,
            'previous': copy.deepcopy(previous),
            'pq': copy.deepcopy(pq),
            'description': description
        }
        self.saved_states.append(state)
        self.current_history_index = len(self.saved_states) - 1
    
    def load_state(self, index):
        """Загружает состояние из истории"""
        if 0 <= index < len(self.saved_states):
            state = self.saved_states[index]
            self.current_history_index = index
            return state
        return None
    
    def draw_complex_graph(self, graph, positions, current_node=None, visited=None, path=None, distances=None, status="", show_info=True):
        self.screen.fill((240, 240, 240))
        
        # Рисуем ребра
        for (u, v), weight in graph.items():
            if u in positions and v in positions:
                start_pos = positions[u]
                end_pos = positions[v]
                
                # Цвет ребра
                if path and u in path and v in path:
                    try:
                        if abs(path.index(u) - path.index(v)) == 1:
                            edge_color = (0, 200, 0)  # Зеленый для пути
                        else:
                            edge_color = (100, 100, 100)
                    except ValueError:
                        edge_color = (100, 100, 100)
                else:
                    edge_color = (100, 100, 100)
                
                pygame.draw.line(self.screen, edge_color, start_pos, end_pos, 2)  # Уменьшил толщину
                
                # Вес ребра
                mid_x = (start_pos[0] + end_pos[0]) // 2
                mid_y = (start_pos[1] + end_pos[1]) // 2
                offset_x = (end_pos[1] - start_pos[1]) * 0.15  # Уменьшил смещение
                offset_y = -(end_pos[0] - start_pos[0]) * 0.15
                
                text = self.font.render(str(weight), True, (0, 0, 139))
                self.screen.blit(text, (mid_x + offset_x, mid_y + offset_y))
        
        # Рисуем узлы
        for node, pos in positions.items():
            if node == current_node:
                color = (255, 0, 0)  # Красный - текущий
            elif visited and node in visited:
                color = (50, 168, 82)  # Зеленый - посещенный
            elif path and node in path:
                color = (30, 144, 255)  # Синий - путь
            else:
                color = (70, 70, 70)  # Серый - непосещенный
            
            pygame.draw.circle(self.screen, color, pos, 20)  # Уменьшил размер узлов
            pygame.draw.circle(self.screen, (255, 255, 255), pos, 18, 2)  # Уменьшил обводку
            
            # Текст узла
            node_text = self.large_font.render(node, True, (255, 255, 255))
            text_rect = node_text.get_rect(center=pos)
            self.screen.blit(node_text, text_rect)
            
            # Отображаем текущее расстояние
            if distances and node in distances and distances[node] != float('inf'):
                dist_text = self.font.render(str(distances[node]), True, (139, 0, 0))
                self.screen.blit(dist_text, (pos[0] + 25, pos[1] - 25))  # Уменьшил смещение
        
        # Легенда и статус
        if show_info:
            self.draw_legend(status)
        
        pygame.display.flip()
    
    def draw_legend(self, status=""):
        legend_y = 10
        
        # Статус программы
        if status:
            status_text = self.title_font.render(status, True, (139, 0, 0))
            status_rect = status_text.get_rect(center=(500, legend_y + 15))
            self.screen.blit(status_text, status_rect)
            legend_y += 40
        
        # Цветовая легенда
        legends = [
            ("Текущий узел", (255, 0, 0)),
            ("Посещенный", (50, 168, 82)),
            ("Кратчайший путь", (30, 144, 255)),
            ("Не посещенный", (70, 70, 70))
        ]
        
        for text, color in legends:
            pygame.draw.rect(self.screen, color, (10, legend_y, 18, 18))  # Уменьшил квадратики
            legend_text = self.font.render(text, True, (0, 0, 0))
            self.screen.blit(legend_text, (33, legend_y))  # Подвинул текст
            legend_y += 28  # Уменьшил расстояние
        
        legend_y += 8
        
        # Управление
        controls = [
            "SPACE - пауза/продолжение",
            "→ - шаг вперед",
            "← - шаг назад", 
            "HOME - в начало",
            "END - в конец",
            "R - перезапуск",
            "ESC - выход"
        ]
        
        for control in controls:
            control_text = self.font.render(control, True, (0, 0, 139))
            self.screen.blit(control_text, (10, legend_y))
            legend_y += 23  # Уменьшил расстояние между строками
        
        # Информация о истории
        if self.saved_states:
            history_text = self.font.render(f"История: {self.current_history_index + 1}/{len(self.saved_states)}", True, (0, 100, 0))
            self.screen.blit(history_text, (10, legend_y))
    
    def get_neighbors(self, graph, node):
        """Получаем всех соседей узла"""
        neighbors = {}
        for (u, v), weight in graph.items():
            if u == node:
                neighbors[v] = weight
            elif v == node:
                neighbors[u] = weight
        return neighbors
    
    def show_final_path(self, graph, positions, start, end, visited, previous, distances):
        """Показывает финальный путь"""
        if end not in previous:
            print(f"Путь от {start} до {end} не найден!")
            self.draw_complex_graph(graph, positions, None, visited, None, distances, "ПУТЬ НЕ НАЙДЕН")
            pygame.display.flip()
            pygame.time.delay(2000)
            return False
        
        path = []
        current = end
        while current != start:
            path.append(current)
            current = previous[current]
        path.append(start)
        path.reverse()
        
        print(f"Кратчайший путь: {' -> '.join(path)}")
        print(f"Длина пути: {distances[end]}")
        
        # Показываем финальный путь
        self.draw_complex_graph(graph, positions, None, visited, path, distances, f"ФИНАЛЬНЫЙ ПУТЬ: {distances[end]}")
        pygame.display.flip()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return True
                    elif event.key == pygame.K_r:
                        return False
                    elif event.key == pygame.K_SPACE:
                        waiting = False
            
            self.clock.tick(60)
            
        return True

    def execute_single_step(self, graph, distances, visited, previous, pq, current_node=None):
        """Выполняет один шаг алгоритма Дейкстры"""
        if not pq:
            return None, True  # Алгоритм завершен
            
        current_dist, current = heapq.heappop(pq)
        
        # Пропускаем уже посещенные узлы
        while pq and current in visited:
            if not pq:
                return None, True
            current_dist, current = heapq.heappop(pq)
            
        if current in visited:
            return None, True
            
        visited.add(current)
        
        # Обрабатываем соседей
        neighbors = self.get_neighbors(graph, current)
        for neighbor, weight in neighbors.items():
            if neighbor not in visited:
                new_dist = current_dist + weight
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    heapq.heappush(pq, (new_dist, neighbor))
                    previous[neighbor] = current
        
        return current, False
    
    def animate_dijkstra(self, graph, positions, start, end):
        # Очищаем историю
        self.saved_states.clear()
        self.current_history_index = -1
        
        # Проверяем что start и end существуют в графе
        all_nodes = set()
        for u, v in graph.keys():
            all_nodes.add(u)
            all_nodes.add(v)
        
        if start not in all_nodes or end not in all_nodes:
            print(f"Ошибка: стартовая или конечная вершина не найдена в графе")
            return
        
        # Инициализация
        distances = {node: float('inf') for node in all_nodes}
        distances[start] = 0
        pq = [(0, start)]
        visited = set()
        previous = {}
        current_node = None
        
        running = True
        pause = True  # Начинаем с паузы
        algorithm_finished = False
        
        # Сохраняем начальное состояние
        self.save_state(distances, visited, current_node, previous, pq, "Начальное состояние")
        
        print(f"Поиск пути от {start} до {end}")
        print("Алгоритм начался в режиме паузы. Нажмите → для шага вперед")
        
        while running:
            # Обработка событий в первую очередь
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        pause = not pause
                        print("Пауза:", "вкл" if pause else "выкл")
                    
                    elif event.key == pygame.K_RIGHT and pause and not algorithm_finished:
                        # Шаг вперед
                        current_node, finished = self.execute_single_step(graph, distances, visited, previous, pq, current_node)
                        
                        if current_node:
                            description = f"Обработка: {current_node}"
                            if current_node == end:
                                description = f"НАЙДЕН КОНЕЦ: {current_node}"
                                algorithm_finished = True
                                print(f"Найден конечный узел {end}!")
                            
                            self.save_state(distances, visited, current_node, previous, pq, description)
                            
                            # Показываем следующее состояние (после обработки соседей)
                            current_node, finished = self.execute_single_step(graph, distances, visited, previous, pq, current_node)
                            if not finished:
                                self.save_state(distances, visited, None, previous, pq, f"После {current_node}")
                        
                        if finished:
                            algorithm_finished = True
                            print("Алгоритм завершен!")
                    
                    elif event.key == pygame.K_LEFT and pause and self.current_history_index > 0:
                        # Шаг назад
                        self.current_history_index -= 1
                        state = self.load_state(self.current_history_index)
                        if state:
                            distances.clear()
                            distances.update(state['distances'])
                            visited.clear()
                            visited.update(state['visited'])
                            previous.clear()
                            previous.update(state['previous'])
                            pq.clear()
                            pq.extend(state['pq'])
                            current_node = state['current']
                            algorithm_finished = (state['current'] == end) if state['current'] else False
                            print(f"Шаг назад: {state['description']}")
                    
                    elif event.key == pygame.K_HOME and pause and self.saved_states:
                        # В начало
                        state = self.load_state(0)
                        if state:
                            distances.clear()
                            distances.update(state['distances'])
                            visited.clear()
                            visited.update(state['visited'])
                            previous.clear()
                            previous.update(state['previous'])
                            pq.clear()
                            pq.extend(state['pq'])
                            current_node = state['current']
                            algorithm_finished = False
                            print("Вернулись в начало")
                    
                    elif event.key == pygame.K_END and pause and self.saved_states:
                        # В конец
                        state = self.load_state(len(self.saved_states) - 1)
                        if state:
                            distances.clear()
                            distances.update(state['distances'])
                            visited.clear()
                            visited.update(state['visited'])
                            previous.clear()
                            previous.update(state['previous'])
                            pq.clear()
                            pq.extend(state['pq'])
                            current_node = state['current']
                            algorithm_finished = (state['current'] == end) if state['current'] else False
                            print("Перешли в конец")
                    
                    elif event.key == pygame.K_r:
                        # Перезапуск
                        print("Перезапуск алгоритма...")
                        return self.animate_dijkstra(graph, positions, start, end)
                    
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            
            # Автоматическое выполнение когда не на паузе
            if not pause and not algorithm_finished:
                current_node, finished = self.execute_single_step(graph, distances, visited, previous, pq, current_node)
                
                if current_node:
                    description = f"Обработка: {current_node}"
                    if current_node == end:
                        description = f"НАЙДЕН КОНЕЦ: {current_node}"
                        algorithm_finished = True
                        print(f"Найден конечный узел {end}!")
                    
                    self.save_state(distances, visited, current_node, previous, pq, description)
                    
                    # Задержка для анимации
                    pygame.time.delay(800)
                
                if finished:
                    algorithm_finished = True
            
            # Отрисовка текущего состояния
            current_state = self.load_state(self.current_history_index) if self.saved_states else None
            if current_state:
                status = "ПАУЗА" if pause else "ВЫПОЛНЕНИЕ"
                if algorithm_finished:
                    status = "АЛГОРИТМ ЗАВЕРШЕН"
                
                # Показываем путь если алгоритм завершен
                final_path = None
                if algorithm_finished and end in previous:
                    path = []
                    current = end
                    while current != start:
                        path.append(current)
                        current = previous[current]
                    path.append(start)
                    path.reverse()
                    final_path = path
                
                self.draw_complex_graph(graph, positions, 
                                      current_state['current'], 
                                      current_state['visited'], 
                                      final_path, 
                                      current_state['distances'], 
                                      f"{status} | {current_state['description']}")
            else:
                status = "ПАУЗА" if pause else "ВЫПОЛНЕНИЕ"
                self.draw_complex_graph(graph, positions, current_node, visited, None, distances, status)
            
            # Если алгоритм завершен, показываем результат
            if algorithm_finished and not pause:
                if self.show_final_path(graph, positions, start, end, visited, previous, distances):
                    running = False
                else:
                    # Перезапуск
                    return self.animate_dijkstra(graph, positions, start, end)
            
            self.clock.tick(60)
        
        pygame.quit()

def create_complex_graph():
    """Создает симметричный граф (неориентированный)"""
    edges = [
        ('A', 'B', 4), ('B', 'C', 3), ('C', 'D', 5), 
        ('D', 'E', 2), ('E', 'F', 6), ('F', 'A', 4),
        ('B', 'E', 7), ('C', 'F', 3), ('A', 'D', 8),
        ('G', 'A', 2), ('G', 'B', 5), ('H', 'C', 4),
        ('H', 'D', 3), ('I', 'E', 6), ('I', 'F', 2),
        ('G', 'H', 8), ('H', 'I', 5), ('I', 'G', 7),
        ('J', 'G', 3), ('J', 'H', 4), ('K', 'H', 2),
        ('K', 'I', 5), ('L', 'G', 6), ('L', 'I', 3),
        ('J', 'K', 3), ('K', 'L', 4), ('L', 'J', 5)
    ]
    
    graph = {}
    for u, v, weight in edges:
        graph[(u, v)] = weight
        graph[(v, u)] = weight
    
    positions = {}
    center_x, center_y = 500, 450  # Сдвинул центр ниже
    
    # Уменьшил радиусы на 25%
    inner_nodes = ['A', 'B', 'C', 'D', 'E', 'F']
    for i, node in enumerate(inner_nodes):
        angle = 2 * math.pi * i / len(inner_nodes)
        positions[node] = (int(center_x + 90 * math.cos(angle)), int(center_y + 90 * math.sin(angle)))  # 120 * 0.75 = 90
    
    middle_nodes = ['G', 'H', 'I']
    for i, node in enumerate(middle_nodes):
        angle = 2 * math.pi * i / len(middle_nodes) - math.pi/6
        positions[node] = (int(center_x + 187 * math.cos(angle)), int(center_y + 187 * math.sin(angle)))  # 250 * 0.75 = 187
    
    outer_nodes = ['J', 'K', 'L']
    for i, node in enumerate(outer_nodes):
        angle = 2 * math.pi * i / len(outer_nodes) + math.pi/6
        positions[node] = (int(center_x + 285 * math.cos(angle)), int(center_y + 285 * math.sin(angle)))  # 380 * 0.75 = 285
    
    return graph, positions

if __name__ == "__main__":
    try:
        graph, positions = create_complex_graph()
        visualizer = AdvancedGraphVisualizer()
        
        print("=" * 60)
        print("Визуализация алгоритма Дейкстры - Расширенная версия")
        print("Старт: G, Конец: K")
        print("=" * 60)
        print("Управление:")
        print("  SPACE - пауза/продолжение")
        print("  → - шаг вперед (в режиме паузы)")
        print("  ← - шаг назад по истории")
        print("  HOME - перейти в начало истории") 
        print("  END - перейти в конец истории")
        print("  R - перезапуск алгоритма")
        print("  ESC - выход")
        print("=" * 60)
        print("Программа начинается в режиме паузы!")
        print("Нажимайте → для пошагового выполнения")
        
        visualizer.animate_dijkstra(graph, positions, 'G', 'K')
        
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit()