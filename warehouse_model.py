from mesa.model import Model
from mesa.space import MultiGrid
from mesa.agent import Agent

class StaticTile(Agent):
    def __init__(self, unique_id, model, tile_type):
        super().__init__(model)
        self.tile_type = tile_type

class WarehouseModel(Model):
    def __init__(self, width=30, height=30, num_unloading=2, num_loading=2):
        super().__init__()
        self.grid = MultiGrid(width, height, torus=False)
        self.agents.do("step")
        self.next_id_val = 0  # Custom ID counter

        self._create_layout(num_unloading, num_loading)

    def _create_layout(self, num_unloading, num_loading):
        w = self.grid.width
        h = self.grid.height

        # --- Posiziona zone di carico (Loading) sul margine sinistro (colonna 0) ---
        for x in range(num_loading):
            self._place_tile(x, 0, "Loading")

        # --- Posiziona zone di scarico (Unloading) sul margine sinistro, centrate verticalmente ---
        center_y = h // 2
        start_y = center_y - (num_unloading // 2)
        for i in range(num_unloading):
            self._place_tile(w-1, start_y + i, "Unloading")

        # --- Blocchi di scaffali, ognuno fatto da più righe ---
        block_gap = 3  # spazio tra gruppi/blocchi
        block_w = 10  # larghezza del blocco (in colonne/celle)
        row_gap = 1  # spazio tra le righe all'interno di un blocco

        # Blocchi nei 4 quadranti
        block_origins = [
            (block_gap, block_gap),  # alto sinistra
            (w // 2 + block_gap // 2, block_gap),  # alto destra
            (block_gap, h // 2 + block_gap // 2),  # basso sinistra
            (w // 2 + block_gap // 2, h // 2 + block_gap // 2)  # basso destra
        ]

        # Popola 4 blocchi, ognuno con N righe di scaffali parallele separate da row_gap
        for origin_x, origin_y in block_origins:
            n_rows_per_block = 5
            for ri in range(n_rows_per_block):
                y = origin_y + ri * (1 + row_gap)
                if y >= h - 1:  # evita di uscire dai limiti
                    break
                for x in range(origin_x, min(origin_x + block_w, w - 1)):
                    self._place_tile(x, y, "Rack")

    def _place_tile(self, x, y, tile_type):
        tile = StaticTile(self.next_id_val, self, tile_type)
        self.grid.place_agent(tile, (x, y))
        self.next_id_val += 1

    def step(self):
        self.schedule.step()
