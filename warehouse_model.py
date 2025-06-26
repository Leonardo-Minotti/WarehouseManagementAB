import random
from collections import deque

from mesa.model import Model
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid
from mesa.discrete_space import OrthogonalVonNeumannGrid
from mesa.agent import Agent
from forkLift import ForkLift
from mesa.experimental.devs import ABMSimulator
from dock import Dock, UnloadingDock, LoadingDock
from order import Order


class WarehouseModel(Model):

    def __init__(
        self,
        width=30,
        height=30,
        num_unloading=2,
        num_loading=2,
        dock_capacity=10,
        order_time=10,
        unloading_order_time=15,  # Tempo per generare ordini di scarico
        simulator: ABMSimulator = None,
    ):

        super().__init__()
        self.simulator = simulator
        self.simulator.setup(self)

        self.height = height
        self.width = width
        self.num_unloading = num_unloading
        self.num_loading = num_loading
        self.dock_capacity = dock_capacity
        self.order_time = order_time
        self.unloading_order_time = unloading_order_time

        # Code per gli ordini in attesa
        self.loading_order_queue = deque()  # Coda per ordini di carico
        self.unloading_order_queue = deque()  # Coda per ordini di scarico

        # Contatori per la generazione degli ordini
        self.step_counter = 0
        self.last_loading_order_step = 0
        self.last_unloading_order_step = 0

        # Liste per tenere traccia dei dock
        self.loading_docks = []
        self.unloading_docks = []

        self.grid = MultiGrid(width, height, torus=False)

        self._create_layout(num_unloading, num_loading)

    def _create_layout(self, num_unloading, num_loading):
        # Posizionamento muletti nelle zone di scarico
        center_y = self.grid.height // 2
        start_y = center_y - num_unloading // 2
        for i in range(num_unloading):
            y = start_y + i
            if 0 <= y < self.grid.height:
                forklift = ForkLift(self)
                self.grid.place_agent(forklift, (self.grid.width - 2, y))

        # Posizionamento dock scarico
        center_y = self.grid.height // 2
        start_y = center_y - num_unloading // 2
        for i in range(num_unloading):
            y = start_y + i
            if 0 <= y < self.grid.height:
                unloading_dock = UnloadingDock(self)
                self.unloading_docks.append(unloading_dock)  # Aggiungi alla lista
                self.grid.place_agent(unloading_dock, (self.grid.width - 1, y))

        # Posizionamento dock carico
        for x in range(num_loading):
            loading_dock = LoadingDock(self)
            self.loading_docks.append(loading_dock)
            self.grid.place_agent(loading_dock, (x, 0))

    def generate_loading_order(self):
        """Genera un nuovo ordine di carico con capacità casuale"""
        capacita_ordine = random.randint(5, self.dock_capacity)
        nuovo_ordine = Order(capacita_ordine)
        print(f"Nuovo ordine di CARICO generato con capacità: {capacita_ordine}")
        return nuovo_ordine

    def generate_unloading_order(self):
        """Genera un nuovo ordine di scarico con capacità casuale"""
        capacita_ordine = random.randint(5, self.dock_capacity)
        nuovo_ordine = Order(capacita_ordine)
        print(f"Nuovo ordine di SCARICO generato con capacità: {capacita_ordine}")
        return nuovo_ordine

    def assign_loading_order_to_dock(self, order):
        """Cerca un dock di loading libero e assegna l'ordine"""
        for dock in self.loading_docks:
            if dock.receive_order(order):
                print(f"Ordine di carico assegnato al dock in posizione {dock.pos}")
                return True
        return False

    def assign_unloading_order_to_dock(self, order):
        """Cerca un dock di unloading libero e assegna l'ordine"""
        for dock in self.unloading_docks:
            if dock.receive_order(order):
                print(f"Ordine di scarico assegnato al dock in posizione {dock.pos}")
                return True
        return False

    def process_loading_order_queue(self):
        """Processa la coda degli ordini di carico"""
        orders_to_remove = []
        
        for order in list(self.loading_order_queue):
            if self.assign_loading_order_to_dock(order):
                orders_to_remove.append(order)
        
        for order in orders_to_remove:
            self.loading_order_queue.remove(order)
            print(f"Ordine di carico rimosso dalla coda e assegnato")

    def process_unloading_order_queue(self):
        """Processa la coda degli ordini di scarico"""
        orders_to_remove = []
        
        for order in list(self.unloading_order_queue):
            if self.assign_unloading_order_to_dock(order):
                orders_to_remove.append(order)
        
        for order in orders_to_remove:
            self.unloading_order_queue.remove(order)
            print(f"Ordine di scarico rimosso dalla coda e assegnato")

    # Mantieni la compatibilità con il codice esistente
    @property
    def order_queue(self):
        """Mantiene compatibilità - restituisce la coda di carico"""
        return self.loading_order_queue

    def step(self):
        self.step_counter += 1

        # Gestione ordini di CARICO
        if self.step_counter - self.last_loading_order_step >= self.order_time:
            nuovo_ordine = self.generate_loading_order()

            if self.assign_loading_order_to_dock(nuovo_ordine):
                print("Ordine di carico assegnato immediatamente")
            else:
                self.loading_order_queue.append(nuovo_ordine)
                print(f"Ordine di carico aggiunto alla coda. Coda attuale: {len(self.loading_order_queue)} ordini")

            self.last_loading_order_step = self.step_counter

        # Gestione ordini di SCARICO
        if self.step_counter - self.last_unloading_order_step >= self.unloading_order_time:
            nuovo_ordine = self.generate_unloading_order()

            if self.assign_unloading_order_to_dock(nuovo_ordine):
                print("Ordine di scarico assegnato immediatamente")
            else:
                self.unloading_order_queue.append(nuovo_ordine)
                print(f"Ordine di scarico aggiunto alla coda. Coda attuale: {len(self.unloading_order_queue)} ordini")

            self.last_unloading_order_step = self.step_counter

        # Processa le code degli ordini
        if self.loading_order_queue:
            self.process_loading_order_queue()

        if self.unloading_order_queue:
            self.process_unloading_order_queue()

        # Usa la classe ForkLift, non il modulo forkLift
        self.agents_by_type[ForkLift].shuffle_do("step")

    def is_rack_position(self, pos):
        """Controlla se la posizione contiene un rack"""
        x, y = pos

        # Parametri dei rack (devono coincidere con quelli in main.py)
        block_size = 10
        spacing = 3
        start_x = 3
        start_y = 4

        block_origins = [
            (start_x, start_y + block_size + spacing),
            (start_x + block_size + spacing, start_y + block_size + spacing),
            (start_x, start_y),
            (start_x + block_size + spacing, start_y)
        ]

        for origin_x, origin_y in block_origins:
            for dx in range(block_size):
                for dy in range(block_size):
                    if dy % 2 == 0:  # Solo le righe pari hanno rack
                        rack_x = origin_x + dx
                        rack_y = origin_y + dy
                        if x == rack_x and y == rack_y:
                            return True
        return False