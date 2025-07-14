# forkLift.py
from mesa.agent import Agent
from mesa.discrete_space import CellAgent, FixedAgent
from pathfindingA import find_path
from typing import List, Tuple, Optional

class ForkLift(CellAgent):
    def __init__(
            self,
            model,
            free = True,
    ):
        super().__init__(model)
        self.current_path = [] #Percorso attuale
        self.current_order = None #Posizione obiettivo
        self.target_position = None #Pacco corrente
        self.free = free

    def set_target(self, target_pos: Tuple[int, int]):
        """Imposta una nuova destinazione e calcola il percorso"""
        self.target_position = target_pos
        self.current_path = find_path(self.model, self.pos, target_pos)

    def move_along_path(self):
        """Muoviti lungo il percorso calcolato"""
        if not self.current_path or len(self.current_path) <= 1:
            return

        # Prendi il prossimo passo nel percorso
        next_pos = self.current_path[1]

        # Muoviti semplicemente senza controlli di collisione
        self.model.grid.move_agent(self, next_pos)
        self.current_path.pop(0)

        # Se hai raggiunto la destinazione
        if self.pos == self.target_position:
            self.on_arrival()

    def on_arrival(self):
        """Chiamata quando il muletto raggiunge la destinazione"""
        self.current_path = []
        self.target_position = None
        self.free = True

    def find_closest_track_to_rack(self, rack_pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Trova la traccia più vicina a un rack"""
        x, y = rack_pos
        adjacent_pos = (x, y + 1)
        return adjacent_pos


class UnloadingForkLift(ForkLift):
    def step(self):
        if self.free:
            # Cerca un ordine di scarico da processare
            if hasattr(self.model, 'unloading_order_queue') and self.model.unloading_order_queue:
                order = self.model.unloading_order_queue.pop(0)
                self.current_order = order
                self.free = False

                # Trova il rack più vicino con spazio
                target_rack = self.find_empty_rack()
                if target_rack:
                    self.set_target(target_rack)
        else:
            # Segui il percorso verso la destinazione
            self.move_along_path()

        def find_empty_rack(self):
            """Trova un rack vuoto per lo scarico"""
            for (x, y), rack in self.model.shelves.items():
                if rack.get_occupazione_corrente() < rack.capacity:
                    closest_track = self.find_closest_track_to_rack((x, y))
                    if closest_track:
                        return closest_track
            return None


class LoadingForkLift(ForkLift):
    def __init__(self, model, free=True):
        super().__init__(model, free)
        self.state = "IDLE"  # Stati: IDLE, GOING_TO_DOCK, LOADING, GOING_TO_RACK, UNLOADING
        self.carried_items = 0
        self.current_dock = None
        self.target_rack = None

    def step(self):
        if self.state == "IDLE":
            self.look_for_dock_with_order()

        elif self.state == "GOING_TO_DOCK":
            self.move_along_path()

        elif self.state == "LOADING":
            self.load_items_from_dock()

        elif self.state == "GOING_TO_RACK":
            self.move_along_path()

        elif self.state == "UNLOADING":
            self.unload_items_to_rack()

    def look_for_dock_with_order(self):
        """Cerca il primo dock con un ordine disponibile"""
        for dock in self.model.unloading_docks:
            if dock.current_order and not dock.is_being_served:
                # Trova la traccia più vicina al dock
                dock_track = self.find_closest_track_to_dock(dock.pos)
                if dock_track:
                    self.current_dock = dock
                    dock.is_being_served = True  # Marca il dock come servito
                    self.set_target(dock_track)
                    self.state = "GOING_TO_DOCK"
                    print(f"LoadingForkLift: Andando al dock in {dock.pos}")
                    break

    def find_closest_track_to_dock(self, dock_pos):
        """Trova la traccia più vicina a un dock"""
        x, y = dock_pos
        # Controlla le posizioni adiacenti al dock
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            adjacent_pos = (x + dx, y + dy)
            if self.model.is_track_position(adjacent_pos):
                return adjacent_pos
        return None

    def load_items_from_dock(self):
        """Carica gli items dal dock"""
        if self.current_dock and self.current_dock.current_order:
            # Simula il caricamento (prende tutti gli items dell'ordine)
            self.carried_items = self.current_dock.current_order.capacity

            # Completa l'ordine e libera il dock
            self.current_dock.complete_order()
            self.current_dock.is_being_served = False

            print(f"LoadingForkLift: Caricati {self.carried_items} items dal dock")

            # Trova un rack per scaricare
            target_rack = self.find_empty_rack()
            if target_rack:
                self.target_rack = target_rack
                self.set_target(target_rack)
                self.state = "GOING_TO_RACK"
                print(f"LoadingForkLift: Andando al rack in {target_rack}")
            else:
                print("LoadingForkLift: Nessun rack disponibile!")
                self.state = "IDLE"
                self.carried_items = 0

    def find_empty_rack(self):
        """Trova un rack con spazio disponibile"""
        for (x, y), rack in self.model.shelves.items():
            if rack.get_occupazione_corrente() < rack.capacity:
                closest_track = self.find_closest_track_to_rack((x, y))
                if closest_track:
                    return closest_track
        return None

    def unload_items_to_rack(self):
        """Scarica gli items nel rack"""
        if self.target_rack and self.carried_items > 0:
            # Trova il rack più vicino alla traccia corrente
            rack_pos = self.find_rack_near_track(self.target_rack)
            if rack_pos:
                rack = self.model.shelves[rack_pos]
                # Calcola quanti items può contenere il rack
                space_available = rack.capacity - rack.get_occupazione_corrente()
                items_to_unload = min(self.carried_items, space_available)

                # Aggiungi gli items al rack
                if rack.aggiungi_items(items_to_unload):
                    self.carried_items -= items_to_unload
                    print(f"LoadingForkLift: Scaricati {items_to_unload} items nel rack {rack_pos}")

                    # Se ha finito di scaricare, torna IDLE
                    if self.carried_items == 0:
                        self.state = "IDLE"
                        self.target_rack = None
                        self.current_dock = None
                        print("LoadingForkLift: Lavoro completato, torno IDLE")
                    else:
                        # Se ha ancora items, trova un altro rack
                        target_rack = self.find_empty_rack()
                        if target_rack:
                            self.target_rack = target_rack
                            self.set_target(target_rack)
                            self.state = "GOING_TO_RACK"
                        else:
                            print("LoadingForkLift: Nessun rack disponibile per items rimanenti!")
                            self.state = "IDLE"
                            self.carried_items = 0
                else:
                    print("LoadingForkLift: Errore nello scarico nel rack")
                    self.state = "IDLE"
                    self.carried_items = 0

    def find_rack_near_track(self, track_pos):
        """Trova il rack più vicino a una traccia"""
        x, y = track_pos
        # Controlla le posizioni adiacenti alla traccia
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            adjacent_pos = (x + dx, y + dy)
            if self.model.is_shelf_position(adjacent_pos):
                return adjacent_pos
        return None

    def on_arrival(self):
        """Chiamata quando il muletto raggiunge la destinazione"""
        super().on_arrival()

        if self.state == "GOING_TO_DOCK":
            self.state = "LOADING"
            print("LoadingForkLift: Raggiunto il dock, inizio caricamento")

        elif self.state == "GOING_TO_RACK":
            self.state = "UNLOADING"
            print("LoadingForkLift: Raggiunto il rack, inizio scaricamento")
