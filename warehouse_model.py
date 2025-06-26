from mesa.model import Model
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid
from mesa.discrete_space import OrthogonalVonNeumannGrid
from mesa.agent import Agent
from forkLift import ForkLift, UnloadingForkLift, LoadingForkLift
from mesa.experimental.devs import ABMSimulator
from dock import Dock, UnloadingDock, LoadingDock


class WarehouseModel(Model):

    def __init__(
            self,
            width=30,
            height=30,
            num_unloading=2,
            num_loading=2,
            num_unloading_forkLift=1,
            num_loading_forkLift=1,
            simulator: ABMSimulator = None,
    ):

        super().__init__()
        self.simulator = simulator
        self.simulator.setup(self)

        self.height = height
        self.width = width
        self.num_unloading = num_unloading
        self.num_loading = num_loading
        self.num_unloading_forkLift = num_unloading_forkLift
        self.num_loading_forkLift = num_loading_forkLift

        self.grid = MultiGrid(width, height, torus=False)

        # Dizionario per tenere traccia degli scaffali
        self.shelves = {}  # {(x, y): {"type": "blue", "occupancy": 0, "max_capacity": 100}}

        self._create_shelves()
        self._create_layout(num_unloading, num_loading, num_unloading_forkLift, num_loading_forkLift)

    def _create_shelves(self):
        """Crea gli scaffali con colori diversi secondo le specifiche"""
        block_size = 10
        spacing = 3
        start_x = 3
        start_y = 4

        # Primo blocco (top-left)
        origin_x, origin_y = start_x, start_y + block_size + spacing
        for dx in range(block_size):
            for dy in range(0, block_size, 2):  # Solo righe pari
                x = origin_x + dx
                y = origin_y + dy

                if dy < 2:  # Prime 2 righe
                    shelf_type = "blue"
                elif dy < 6:  # Seconde 2 righe
                    shelf_type = "red"
                else:  # Ultima riga
                    shelf_type = "green"

                if x < self.width and y < self.height:
                    self.shelves[(x, y)] = {
                        "type": shelf_type,
                        "occupancy": 0,
                        "max_capacity": 100,
                        "occupancy_percentage": 0.0
                    }
        # Secondo blocco
        origin_x, origin_y = start_x + block_size + spacing, start_y + block_size + spacing
        for dx in range(block_size):
            for dy in range(0, block_size, 2):  # Solo righe pari
                x = origin_x + dx
                y = origin_y + dy

                if dy < 2:  # Prime 2 righe
                    shelf_type = "blue"
                elif dy < 6:  # Seconde 2 righe
                    shelf_type = "red"
                else:  # Ultima riga
                    shelf_type = "green"

                if x < self.width and y < self.height:
                    self.shelves[(x, y)] = {
                        "type": shelf_type,
                        "occupancy": 0,
                        "max_capacity": 100,
                        "occupancy_percentage": 0.0
                    }
        # Terzo blocco (bottom-left): prima riga verde, 2a-3a riga gialla, 4a-5a riga arancio
        origin_x, origin_y = start_x, start_y
        for dx in range(block_size):
            for dy in range(0, block_size, 2):  # Solo righe pari
                x = origin_x + dx
                y = origin_y + dy

                if dy < 4:  # Prima riga
                    shelf_type = "green"
                elif dy < 8:  # 2a e 3a riga
                    shelf_type = "yellow"
                else:  # 4a e 5a riga
                    shelf_type = "blue"

                if x < self.width and y < self.height:
                    self.shelves[(x, y)] = {
                        "type": shelf_type,
                        "occupancy": 0,
                        "max_capacity": 100,
                        "occupancy_percentage": 0.0
                    }

        # Quarto blocco
        origin_x, origin_y = start_x + block_size + spacing, start_y
        for dx in range(block_size):
            for dy in range(0, block_size, 2):  # Solo righe pari
                x = origin_x + dx
                y = origin_y + dy

                if dy < 4:  # Prima riga
                    shelf_type = "green"
                elif dy < 8:  # 2a e 3a riga
                    shelf_type = "yellow"
                else:  # 4a e 5a riga
                    shelf_type = "blue"

                if x < self.width and y < self.height:
                    self.shelves[(x, y)] = {
                        "type": shelf_type,
                        "occupancy": 0,
                        "max_capacity": 100,
                        "occupancy_percentage": 0.0
                }

    def add_items_to_shelf(self, pos, quantity):
        """Aggiunge items allo scaffale in posizione pos"""
        if pos in self.shelves:
            shelf = self.shelves[pos]
            if shelf["occupancy"] + quantity <= shelf["max_capacity"]:
                shelf["occupancy"] += quantity
                shelf["occupancy_percentage"] = (shelf["occupancy"] / shelf["max_capacity"]) * 100
                return True
        return False

    def remove_items_from_shelf(self, pos, quantity):
        """Rimuove items dallo scaffale in posizione pos"""
        if pos in self.shelves:
            shelf = self.shelves[pos]
            if shelf["occupancy"] >= quantity:
                shelf["occupancy"] -= quantity
                shelf["occupancy_percentage"] = (shelf["occupancy"] / shelf["max_capacity"]) * 100
                return True
        return False

    def get_shelf_info(self, pos):
        """Ritorna le informazioni dello scaffale in posizione pos"""
        return self.shelves.get(pos, None)

    def is_shelf_position(self, pos):
        """Controlla se la posizione contiene uno scaffale"""
        return pos in self.shelves

    def _create_layout(self, num_unloading, num_loading, num_unloading_forkLift, num_loading_forkLift):
        # Posizionamento muletti nelle zone di scarico
        center_y = self.grid.height // 2
        start_y = center_y - num_unloading // 2
        for i in range(num_unloading_forkLift):
            y = start_y + i
            if 0 <= y < self.grid.height:
                unloading_forklift = UnloadingForkLift(self)
                self.grid.place_agent(unloading_forklift, (self.grid.width - 2, y))

        # Posizionamento muletti nelle zone di carico
        for x in range(num_loading_forkLift):
            loading_forklift = LoadingForkLift(self)
            self.grid.place_agent(loading_forklift, (x, 1))

        # Posizionamento dock scarico
        center_y = self.grid.height // 2
        start_y = center_y - num_unloading // 2
        for i in range(num_unloading):
            y = start_y + i
            if 0 <= y < self.grid.height:
                unloading_dock = UnloadingDock(self)
                self.grid.place_agent(unloading_dock, (self.grid.width - 1, y))

        # Posizionamento dock carico
        for x in range(num_loading):
            loading_dock = LoadingDock(self)
            self.grid.place_agent(loading_dock, (x, 0))

    def step(self):
        self.agents_by_type[UnloadingForkLift].shuffle_do("step")
        self.agents_by_type[LoadingForkLift].shuffle_do("step")

    def is_rack_position(self, pos):
        """Controlla se la posizione contiene un rack (deprecato, usa is_shelf_position)"""
        return self.is_shelf_position(pos)