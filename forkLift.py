# forkLift.py
from random import choice

from debugpy.server.cli import set_target
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
        print(f"[DEBUG] Percorso calcolato da {self.pos} a {target_pos}: {self.current_path}")


    def find_closest_track_to_rack(self, rack_pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Trova la traccia più vicina a un rack"""
        (x, y) = rack_pos
        adjacent_pos = (x, y + 1)
        return adjacent_pos


class UnloadingForkLift(ForkLift):
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
        """Cerca il primo dock con un ordine da scaricare"""
        for dock in self.model.unloading_docks:
            print(f"[DEBUG] Ordine al dock {dock.pos}: {dock.current_order}")
            if dock.current_order is not None and not dock.is_being_served:
                dock_track = self.find_closest_track_to_dock(dock.pos)

                if dock_track:
                    self.current_dock = dock
                    dock.is_being_served = True

                    if self.pos == dock_track:
                        # Già davanti al dock → passa direttamente a LOADING
                        self.state = "LOADING"
                        print(f"[DEBUG] Muletto già davanti al dock {dock.pos}, passo direttamente a LOADING")
                    else:
                        # Muoviti verso il dock
                        self.set_target(dock_track)
                        self.state = "GOING_TO_DOCK"
                        print(f"[DEBUG] Andando verso il dock in {dock.pos}")
                    break

    def move_along_path(self):
        """Muoviti lungo il percorso calcolato"""
        if not self.current_path or len(self.current_path) <= 1:
            self.on_arrival()
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
        if self.state == "GOING_TO_DOCK":
            self.state = "LOADING"

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
        """Carica un solo elemento (di un colore casuale disponibile) dall'ordine del dock"""
        ordine = self.current_dock.current_order

        # Trova tutti i colori con almeno 1 unità disponibile
        colori_disponibili = [colore for colore, qty in ordine.get_tutte_capacita().items() if qty > 0]

        if not colori_disponibili:
            # Ordine completato
            print(f"[INFO] Ordine completato al dock {self.current_dock.pos}")
            self.current_dock.current_order = None
            self.current_dock.is_being_served = False
            self.state = "IDLE"
            return

        # Scegli un colore casuale tra quelli disponibili
        colore_scelto = choice(colori_disponibili)
        colore = colore_scelto.value
        quantita_corrente = ordine.get_capacita_per_colore(colore_scelto)

        # Decrementa di 1 la quantità per quel colore
        ordine.set_capacita_per_colore(colore_scelto, quantita_corrente - 1)

        print(f"[LOADING] Caricato 1 unità di {colore_scelto.value.upper()} dal dock {self.current_dock.pos}")
        print(f"[LOADING] Capacità rimanente per {colore_scelto.value.upper()}: {quantita_corrente - 1}")
        print(f"[LOADING] Capacità totale rimanente: {ordine.get_capacita_totale()}")
        empty_rack_pos = self.find_empty_rack(colore)

        self.set_target(empty_rack_pos)
        # Passa alla fase successiva
        self.state = "GOING_TO_RACK"

    def find_empty_rack(self, color: str):
        """Trova un rack con spazio disponibile per il colore dato, partendo da quello più a destra"""
        # Ordina gli shelves per coordinata x decrescente (più a destra prima)

        for (x, y), rack in self.model.shelves.items():
            rack_color = rack.get_colore()  # supponiamo restituisca stringa o lista di stringhe
            # Se è una singola stringa
            if rack_color == color and rack.get_occupazione_corrente() < 15:
                return (x, y)
        return None


class LoadingForkLift(ForkLift):
    #DAFARE



    def find_empty_rack(self, color):
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
