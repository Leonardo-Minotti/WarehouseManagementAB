import random
from collections import deque

from mesa.model import Model
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid
from mesa.discrete_space import OrthogonalVonNeumannGrid
from mesa.agent import Agent
from forkLift import ForkLift, UnloadingForkLift, LoadingForkLift
from mesa.experimental.devs import ABMSimulator
from dock import Dock, UnloadingDock, LoadingDock
from order import Order
from rack import Rack


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
            num_unloading_forkLift=1,
            num_loading_forkLift=1,
            initial_warehouse_filling=50,  # Percentuale di riempimento iniziale
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
        self.initial_warehouse_filling = initial_warehouse_filling

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
        self.num_unloading_forkLift = num_unloading_forkLift
        self.num_loading_forkLift = num_loading_forkLift

        self.grid = MultiGrid(width, height, torus=False)

        # Dizionario per tenere traccia degli scaffali
        self.shelves = {}  # {(x, y): Rack}
        self._create_shelves()
        self._create_track_system()


        self._create_layout(num_unloading, num_loading, num_unloading_forkLift, num_loading_forkLift)

    def _create_shelves(self):
        """Crea gli scaffali usando la classe Rack e li riempie secondo la percentuale globale"""
        block_size = 10
        spacing = 3
        start_x = 3
        start_y = 4

        # Lista temporanea per tenere traccia di tutte le posizioni dei rack
        all_rack_positions = []

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
                    nuovo_rack = Rack(capienza=15, colore=shelf_type)
                    self.shelves[(x, y)] = nuovo_rack
                    all_rack_positions.append((x, y))

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
                    nuovo_rack = Rack(capienza=15, colore=shelf_type)
                    self.shelves[(x, y)] = nuovo_rack
                    all_rack_positions.append((x, y))

        # Terzo blocco (bottom-left)
        origin_x, origin_y = start_x, start_y
        for dx in range(block_size):
            for dy in range(0, block_size, 2):  # Solo righe pari
                x = origin_x + dx
                y = origin_y + dy

                if dy < 4:  # Prime 2 righe
                    shelf_type = "orange"
                elif dy < 8:  # 2a e 3a riga
                    shelf_type = "yellow"
                else:  # 4a e 5a riga
                    shelf_type = "blue"

                if x < self.width and y < self.height:
                    nuovo_rack = Rack(capienza=15, colore=shelf_type)
                    self.shelves[(x, y)] = nuovo_rack
                    all_rack_positions.append((x, y))

        # Quarto blocco
        origin_x, origin_y = start_x + block_size + spacing, start_y
        for dx in range(block_size):
            for dy in range(0, block_size, 2):  # Solo righe pari
                x = origin_x + dx
                y = origin_y + dy

                if dy < 4:  # Prime 2 righe
                    shelf_type = "orange"
                elif dy < 8:  # 2a e 3a riga
                    shelf_type = "yellow"
                else:  # 4a e 5a riga
                    shelf_type = "blue"

                if x < self.width and y < self.height:
                    nuovo_rack = Rack(capienza=15, colore=shelf_type)
                    self.shelves[(x, y)] = nuovo_rack
                    all_rack_positions.append((x, y))

        # Ora riempi i rack secondo la percentuale globale
        self._fill_warehouse_by_percentage(all_rack_positions)

    def _create_track_system(self):
        """Crea il sistema di tracce navigabili per i muletti"""
        self.tracks = set()  # Insieme delle posizioni navigabili

        block_size = 10
        spacing = 3
        start_x = 3
        start_y = 4

        # Corridoio orizzontale principale
        corridor_y = (start_y + block_size + spacing / 2) - 1
        for x in range(1, self.width - 1):
            self.tracks.add((x, int(corridor_y)))

        # Corridoio verticale centrale
        corridor_x = start_x + block_size + spacing / 2
        for y in range(1, self.height - 1):
            self.tracks.add((int(corridor_x), y))

            # Corridoi orizzontali all'interno dei blocchi (spostati in alto di 2)
            for dy in range(1, block_size, 2):  # Solo righe dispari (1, 3, 5, 7, 9)
                # Blocchi superiori (entrambi: sinistro e destro) - spostati in alto di 2
                corridor_y_upper = start_y + block_size + spacing + dy - 2
                for x in range(1, self.width - 1):
                    self.tracks.add((x, corridor_y_upper))

                # Blocchi inferiori (entrambi: sinistro e destro) - spostati in alto di 2
                corridor_y_lower = start_y + dy - 2
                for x in range(1, self.width - 1):
                    self.tracks.add((x, corridor_y_lower))

            # Corridoi orizzontali esterni (alto e basso)
            corridor_y_top = self.height - 2
            corridor_y_bottom = start_y - 3
            for x in range(1, self.width - 1):
                self.tracks.add((x, corridor_y_top))
                self.tracks.add((x, corridor_y_bottom))

            # Corridoi verticali esterni (sinistro e destro)
            corridor_x_left = start_x - 2
            corridor_x_right = self.width - 2
            for y in range(start_y - 3, self.height - 1):
                self.tracks.add((corridor_x_left, y))
                self.tracks.add((corridor_x_right, y))

    def is_track_position(self, pos):
        """Verifica se una posizione è una traccia navigabile"""
        return pos in self.tracks


    def _fill_warehouse_by_percentage(self, all_positions):
        """Riempie il magazzino: prima riempie completamente i rack, poi parzialmente l'ultimo se necessario"""
        # Calcola la capacità totale del magazzino
        total_capacity = len(all_positions) * 15  # Ogni rack ha capacità 15

        # Calcola il numero totale di items da distribuire
        total_items_to_place = int((self.initial_warehouse_filling / 100) * total_capacity)

        print(f"Magazzino: {len(all_positions)} rack, capacità totale: {total_capacity}")
        print(f"Percentuale: {self.initial_warehouse_filling}%, items da piazzare: {total_items_to_place}")

        # Mescola casualmente le posizioni per una distribuzione random
        random.shuffle(all_positions)

        # FASE 1: Calcola quanti rack riempire completamente e quanti items rimangono
        rack_completi = total_items_to_place // 15  # Divisione intera
        items_rimanenti = total_items_to_place % 15  # Resto della divisione

        print(f"Strategia: {rack_completi} rack completi (15 items) + 1 rack parziale ({items_rimanenti} items)")

        items_placed = 0

        # FASE 2: Riempi completamente i primi rack_completi
        for i in range(min(rack_completi, len(all_positions))):
            pos = all_positions[i]
            rack = self.shelves[pos]
            rack.set_occupazione_corrente(15)
            items_placed += 15

        # FASE 3: Se ci sono items rimanenti, riempi parzialmente il prossimo rack
        if items_rimanenti > 0 and rack_completi < len(all_positions):
            pos = all_positions[rack_completi]  # Il rack successivo a quelli completi
            rack = self.shelves[pos]
            rack.set_occupazione_corrente(items_rimanenti)
            items_placed += items_rimanenti

        print(f"Items piazzati: {items_placed}")

        # Statistiche finali per debug
        rack_distribution = {}
        for pos in all_positions:
            occupancy = self.shelves[pos].get_occupazione_corrente()
            rack_distribution[occupancy] = rack_distribution.get(occupancy, 0) + 1

        print("Distribuzione rack per occupazione:")
        for occupancy, count in sorted(rack_distribution.items()):
            if count > 0:  # Mostra solo i valori con count > 0
                print(f"  {occupancy} items: {count} rack")


    def add_items_to_shelf(self, pos, quantity):
        """Aggiunge items allo scaffale in posizione pos"""
        if pos in self.shelves:
            rack = self.shelves[pos]
            return rack.aggiungi_items(quantity)
        return False

    def remove_items_from_shelf(self, pos, quantity):
        """Rimuove items dallo scaffale in posizione pos"""
        if pos in self.shelves:
            rack = self.shelves[pos]
            return rack.rimuovi_items(quantity)
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
            self.grid.place_agent(loading_forklift, (x + 1, 1))

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
            self.grid.place_agent(loading_dock, (x + 1, 0))

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

        self.agents_by_type[UnloadingForkLift].shuffle_do("step")
        self.agents_by_type[LoadingForkLift].shuffle_do("step")

    def get_warehouse_stats(self):
        """Ritorna statistiche del magazzino"""
        total_racks = len(self.shelves)
        total_capacity = total_racks * 15
        total_occupied = sum(rack.get_occupazione_corrente() for rack in self.shelves.values())
        current_percentage = (total_occupied / total_capacity * 100) if total_capacity > 0 else 0

        return {
            "total_racks": total_racks,
            "total_capacity": total_capacity,
            "total_occupied": total_occupied,
            "current_percentage": current_percentage
        }

    def is_rack_position(self, pos):
        """Controlla se la posizione contiene un rack (deprecato, usa is_shelf_position)"""
        return self.is_shelf_position(pos)