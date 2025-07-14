import heapq
from typing import List, Tuple, Optional


def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    """Distanza di Manhattan tra due punti"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
    """Ottieni i vicini navigabili di una posizione"""
    x, y = pos
    neighbors = []

    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        new_x, new_y = x + dx, y + dy
        new_pos = (new_x, new_y)

        # Verifica se la nuova posizione è dentro la griglia e navigabile
        if (0 <= new_x < self.width and
                0 <= new_y < self.height and
                self.is_track_position(new_pos)):
            neighbors.append(new_pos)

    return neighbors


def find_path(model, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
    """Algoritmo A* per trovare il percorso più breve"""
    if start == goal:
        return [start]

    # Coda di priorità per A*
    open_set = []
    heapq.heappush(open_set, (0, start))

    # Dizionari per tracciare il percorso
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        current = heapq.heappop(open_set)[1]

        if current == goal:
            # Ricostruisci il percorso
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]  # Inverti per avere il percorso corretto

        for neighbor in get_neighbors(model, current):
            tentative_g_score = g_score[current] + 1

            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return None  # Percorso non trovato
