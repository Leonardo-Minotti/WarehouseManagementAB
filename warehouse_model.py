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
        simulator: ABMSimulator = None,
    ):

        super().__init__()
        self.simulator = simulator
        self.simulator.setup(self)

        self.height = height
        self.width = width
        self.num_unloading = num_unloading  # Salva per la visualizzazione
        self.num_loading = num_loading      # Salva per la visualizzazione
        self.dock_capacity = dock_capacity  # Capacità massima degli ordini
        self.order_time = order_time  # Intervallo di tempo per generare ordini (in step)

        # Coda per gli ordini in attesa
        self.order_queue = deque()

        # Contatore per la generazione degli ordini
        self.step_counter = 0
        self.last_order_step = 0
        # Lista per tenere traccia dei dock di loading
        self.loading_docks = []

        self.grid = MultiGrid(width, height, torus=False)

        self._create_layout(num_unloading, num_loading)

    def _create_layout(self, num_unloading, num_loading):
        # Posizionamento muletti nelle zone di scarico
        center_y = self.grid.height // 2
        start_y = center_y - num_unloading // 2
        for i in range(num_unloading):
            y = start_y + i
            if 0 <= y < self.grid.height:
                # Crea il muletto posizionandolo alla sinistra della dock di scarico
                forklift = ForkLift(self)
                self.grid.place_agent(forklift, (self.grid.width - 2, y))

        #Posizionamento dock scarico
        center_y = self.grid.height // 2
        start_y = center_y - num_unloading // 2
        for i in range(num_unloading):
            y = start_y + i
            if 0 <= y < self.grid.height:
                unloading_dock = UnloadingDock(self)
                self.grid.place_agent(unloading_dock, (self.grid.width - 1, y))

        #Posizionamento dock carico
        for x in range(num_loading):
                loading_dock = LoadingDock(self)
                self.loading_docks.append(loading_dock)  # Aggiungi alla lista
                self.grid.place_agent(loading_dock, (x, 0))

    def generate_order(self):
        """Genera un nuovo ordine con capacità casuale tra 5 e dock_capacity"""
        capacita_ordine = random.randint(5, self.dock_capacity)
        nuovo_ordine = Order(capacita_ordine)

        print(f"Nuovo ordine generato con capacità: {capacita_ordine}")
        return nuovo_ordine

    def assign_order_to_dock(self, order):
        """
        Cerca un dock di loading libero e assegna l'ordine

        Args:
            order: L'ordine da assegnare

        Returns:
            bool: True se l'ordine è stato assegnato, False se tutti i dock sono occupati
        """
        for dock in self.loading_docks:
            if dock.receive_order(order):
                print(f"Ordine assegnato al dock in posizione {dock.pos}")
                return True

        # Se arriviamo qui, tutti i dock sono occupati
        return False

    def step(self):
        self.step_counter += 1

        # Controlla se è il momento di generare un nuovo ordine
        if self.step_counter - self.last_order_step >= self.order_time:
            nuovo_ordine = self.generate_order()

            # Prova ad assegnare l'ordine a un dock libero
            if self.assign_order_to_dock(nuovo_ordine):
                print("Ordine assegnato immediatamente")
            else:
                # Se tutti i dock sono occupati, metti l'ordine in coda
                self.order_queue.append(nuovo_ordine)
                print(f"Ordine aggiunto alla coda. Coda attuale: {len(self.order_queue)} ordini")

            self.last_order_step = self.step_counter

        # Processa la coda degli ordini per vedere se qualche dock si è liberato
        #if self.order_queue:
            #self.process_order_queue()

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
