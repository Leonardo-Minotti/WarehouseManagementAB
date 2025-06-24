import random

from mesa.model import Model
from mesa.space import MultiGrid
from mesa.agent import Agent
from collections import deque


class StaticTile(Agent):
    def __init__(self, unique_id, model, tile_type):
        super().__init__(model)
        self.tile_type = tile_type

class WarehouseModel(Model):
    def __init__(self, width=10, height=10, num_unloading=2, num_loading=2, order_frequency=10, truck_capacity=5):
        super().__init__()
        self.grid = MultiGrid(width, height, torus=False)
        self.num_unloading = num_unloading
        self.num_loading = num_loading
        self.agents.do("step")
        self.order_frequency = order_frequency
        self.truck_capacity = truck_capacity
        self.next_id_val = 0  # Custom ID counter
        self.order_queue = deque()
        self.loading_positions = []  # Da riempire con le coordinate della zona di carico
        self.orders_on_grid = {}  # {(x, y): ordine_size}
        self._create_layout(num_unloading, num_loading)

    def _create_layout(self, num_unloading, num_loading):

        #Posizionamento zona scarico
        center_y = self.grid.height // 2
        start_y = center_y - num_unloading // 2
        for i in range(num_unloading):
            y = start_y + i
            if 0 <= y < self.grid.height:
                self._place_tile(self.grid.width - 1, y, "Unloading")

        #Posizionamento zona carico
        for x in range(num_loading):
            self._place_tile(x, 0, "Loading")
            self.loading_positions.append((x, 0))
            #Posizionamento Rack
            block_size = 10
            spacing = 3

            start_x = 3  # (30 - (10*2 + 3)) / 2
            start_y = 4

            # Posizioni dei 4 blocchi
            block_origins = [
                (start_x, start_y + block_size + spacing),  # Top-left
                (start_x + block_size + spacing, start_y + block_size + spacing),  # Top-right
                (start_x, start_y),  # Bottom-left
                (start_x + block_size + spacing, start_y)  # Bottom-right
            ]

            for origin_x, origin_y in block_origins:
                for dx in range(block_size):
                    for dy in range(block_size):
                        if dy % 2 == 0:
                            x = origin_x + dx
                            y = origin_y + dy
                            if x < self.grid.width and y < self.grid.height:
                                self._place_tile(x, y, "Rack")

    def _place_tile(self, x, y, tile_type):
        tile = StaticTile(self.next_id_val, self, tile_type)
        self.grid.place_agent(tile, (x, y))
        self.next_id_val += 1



    def generate_order(self):
        #print("Stato ordini su griglia:", self.orders_on_grid)
        order_size = random.randint(5, self.truck_capacity)
        print("Size: ", order_size)
        placed = False
        for pos in self.loading_positions:
            if pos not in self.orders_on_grid:
                self.orders_on_grid[pos] = order_size
                placed = True
                break
        if not placed:
            self.order_queue.append(order_size)

    def step(self):
        self.schedule.step()
