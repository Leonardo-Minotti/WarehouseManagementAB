from mesa.model import Model
from mesa.space import MultiGrid
from mesa.agent import Agent

class StaticTile(Agent):
    def __init__(self, unique_id, model, tile_type):
        super().__init__(model)
        self.tile_type = tile_type

class WarehouseModel(Model):
    def __init__(self, width=10, height=10, num_unloading=2, num_loading=2):
        super().__init__()
        self.grid = MultiGrid(width, height, torus=False)
        self.agents.do("step")
        self.next_id_val = 0  # Custom ID counter

        self._create_layout(num_unloading, num_loading)

    def _create_layout(self, num_unloading, num_loading):
        for x in range(num_unloading):
            self._place_tile(x, 0, "Unloading")

        for x in range(self.grid.width - num_loading, self.grid.width):
            self._place_tile(x, 0, "Loading")

        for x in range(3, self.grid.width - 3):
            for y in range(2, self.grid.height - 2):
                if x % 2 == 0:
                    self._place_tile(x, y, "Rack")

    def _place_tile(self, x, y, tile_type):
        tile = StaticTile(self.next_id_val, self, tile_type)
        self.grid.place_agent(tile, (x, y))
        self.next_id_val += 1

    def step(self):
        self.schedule.step()
