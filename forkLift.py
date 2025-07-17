# forkLift.py
from random import choice
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
        elif self.state == "GOING_TO_STANDBY":
            self.move_along_path()


    def look_for_dock_with_order(self):
        """Cerca il primo dock con un ordine da scaricare"""
        has_work = False

        for dock in self.model.unloading_docks:

            if dock.current_order is not None and dock.divisione_temp is not None:
                # Controlla se l'ordine è realmente completato guardando ENTRAMBI
                ordine_completato = dock.current_order.get_capacita_totale() == 0
                divisione_temp_completata = dock.divisione_temp.get_capacita_totale() == 0

                # Procedi solo se entrambi hanno ancora items
                if not ordine_completato and not divisione_temp_completata:
                    # Cerca un rack con items per l'ordine usando divisione_temp
                    ordine_temp = dock.divisione_temp

                    # Trova un colore disponibile nell'ordine temporaneo
                    colori_richiesti = [colore for colore, qty in ordine_temp.get_tutte_capacita().items() if qty > 0]

                    if colori_richiesti:
                        # Scegli un colore casuale tra quelli richiesti
                        colore_scelto = choice(colori_richiesti)
                        dock_track = self.find_closest_track_to_dock(dock.pos)

                        if dock_track:
                            has_work = True
                            self.current_dock = dock
                            self.current_color = colore_scelto

                            # Decrementa dalla divisione_temp per prenotare l'item
                            quantita_corrente = ordine_temp.get_capacita_per_colore(colore_scelto)
                            ordine_temp.set_capacita_per_colore(colore_scelto, quantita_corrente - 1)

                            print(f"[RESERVATION] Prenotato 1 unità di {colore_scelto.value.upper()} da divisione_temp")

                            if self.pos == dock_track:
                                # Già davanti al rack → passa direttamente a LOADING
                                self.state = "LOADING"
                            else:
                                # Muoviti verso il rack
                                self.set_target(dock_track)
                                self.state = "GOING_TO_DOCK"
                            break

        # Se non c'è lavoro da fare, vai al punto standby
        if not has_work:
            standby_pos = (28, 28)
            if self.pos != standby_pos:
                self.set_target(standby_pos)
                self.state = "GOING_TO_STANDBY"
            # Se è già al punto standby, rimane IDLE senza muoversi

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
        if self.state == "GOING_TO_DOCK":
            self.state = "LOADING"
        if self.state == "GOING_TO_RACK":
            self.state = "UNLOADING"
        elif self.state == "GOING_TO_STANDBY":
            self.state = "IDLE"

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
            self.current_dock.current_order = None

            self.state = "IDLE"
            return

        # Scegli un colore casuale tra quelli disponibili
        colore_scelto = choice(colori_disponibili)
        colore = colore_scelto.value
        quantita_corrente = ordine.get_capacita_per_colore(colore_scelto)

        # Decrementa di 1 la quantità per quel colore
        ordine.set_capacita_per_colore(colore_scelto, quantita_corrente - 1)

        empty_rack_pos = self.find_empty_rack(colore)


        self.set_target(empty_rack_pos)
        # Passa alla fase successiva
        self.free = False
        if ordine.get_capacita_totale() == 0:
            self.current_dock.complete_order()
        self.state = "GOING_TO_RACK"

    def find_empty_rack(self, color: str):
        """Trova un rack con spazio disponibile per il colore dato, partendo da quello più a destra"""
        # Ordina gli scaffali per coordinata x decrescente (da destra a sinistra)
        sorted_shelves = sorted(self.model.shelves.items(), key=lambda item: item[0][0], reverse=True)

        for (x, y), rack in sorted_shelves:
            rack_color = rack.get_colore()  # supponiamo restituisca una stringa
            if rack_color == color and rack.get_occupazione_corrente() < 15:
                return (x, y + 1)
        return None

    def unload_items_to_rack(self):
        """Scarica gli items nel rack"""
        rack_pos = self.target_position
        print(f"[LOADING] POSIZOINE {rack_pos}")
        self.target_position = None
        posizione = (rack_pos[0], rack_pos[1] - 1)
        if posizione:
            rack = self.model.shelves[posizione]
            print(f"RACKK {posizione}")
            # Aggiungi gli items al rack
            rack.aggiungi_items(1)
            self.free = True
            self.carried_items = 0
            self.target_rack = None
            self.current_dock = None
            self.state = "IDLE"



class LoadingForkLift(ForkLift):
    def __init__(self, model, free=True):
        super().__init__(model, free)
        self.state = "IDLE"  # Stati: IDLE, GOING_TO_RACK, LOADING, GOING_TO_DOCK, UNLOADING
        self.carried_items = 0
        self.current_dock = None
        self.target_rack = None
        self.current_color = None  # Colore dell'item trasportato
        self.standby_position = (14, 1)

    def step(self):
        if self.state == "IDLE":
            self.look_for_dock_with_order()

        elif self.state == "GOING_TO_DOCK":
            self.move_along_path()

        elif self.state == "LOADING":
            self.load_items_from_rack()

        elif self.state == "GOING_TO_RACK":
            self.move_along_path()

        elif self.state == "UNLOADING":
            self.unload_items_to_dock()

        elif self.state == "GOING_TO_STANDBY":
            self.move_along_path()

    def look_for_dock_with_order(self):
        """Cerca il primo dock con un ordine da caricare"""
        has_work = False

        for dock in self.model.loading_docks:
            # Verifica che ci sia sia un ordine che una divisione_temp
            if dock.current_order is not None and dock.divisione_temp is not None:
                # Controlla se l'ordine è realmente completato guardando ENTRAMBI
                ordine_completato = dock.current_order.get_capacita_totale() == 0
                divisione_temp_completata = dock.divisione_temp.get_capacita_totale() == 0

                # Procedi solo se entrambi hanno ancora items
                if not ordine_completato and not divisione_temp_completata:
                    # Cerca un rack con items per l'ordine usando divisione_temp
                    ordine_temp = dock.divisione_temp

                    # Trova un colore disponibile nell'ordine temporaneo
                    colori_richiesti = [colore for colore, qty in ordine_temp.get_tutte_capacita().items() if qty > 0]

                    if colori_richiesti:
                        # Scegli un colore casuale tra quelli richiesti
                        colore_scelto = choice(colori_richiesti)
                        rack_pos = self.find_rack_with_items(colore_scelto.value)

                        if rack_pos:
                            has_work = True
                            self.current_dock = dock
                            self.current_color = colore_scelto

                            # Decrementa dalla divisione_temp per prenotare l'item
                            quantita_corrente = ordine_temp.get_capacita_per_colore(colore_scelto)
                            ordine_temp.set_capacita_per_colore(colore_scelto, quantita_corrente - 1)

                            print(f"[RESERVATION] Prenotato 1 unità di {colore_scelto.value.upper()} da divisione_temp")

                            if self.pos == rack_pos:
                                # Già davanti al rack → passa direttamente a LOADING
                                self.state = "LOADING"
                            else:
                                # Muoviti verso il rack
                                self.set_target(rack_pos)
                                self.state = "GOING_TO_RACK"
                            break

        # Se non c'è lavoro da fare, vai al punto standby
        if not has_work:
            if self.pos != self.standby_position:
                self.set_target(self.standby_position)
                self.state = "GOING_TO_STANDBY"
            # Se è già al punto standby, rimane IDLE senza muoversi

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

        if self.state == "GOING_TO_RACK":
            self.state = "LOADING"
        elif self.state == "GOING_TO_DOCK":
            self.state = "UNLOADING"
        elif self.state == "GOING_TO_STANDBY":
            self.state = "IDLE"

    def load_items_from_rack(self):
        """Carica un solo elemento dal rack"""

        # Trova il rack in posizione adiacente
        rack_pos = (self.pos[0], self.pos[1] - 1)

        if rack_pos in self.model.shelves:
            rack = self.model.shelves[rack_pos]

            # Verifica che il rack abbia items del colore richiesto
            if rack.get_colore() == self.current_color.value and rack.get_occupazione_corrente() > 0:
                # Rimuovi 1 item dal rack
                if rack.rimuovi_items(1):
                    self.carried_items = 1
                    print(f"[LOADING] Caricato 1 unità di {self.current_color.value.upper()} dal rack {rack_pos}")
                    self.free = False
                    # Muoviti verso il dock
                    dock_track = self.find_closest_track_to_dock(self.current_dock.pos)
                    if dock_track:

                        self.set_target(dock_track)
                        self.state = "GOING_TO_DOCK"
                    else:
                        print("[ERROR] Impossibile trovare traccia per il dock")
                        self._restore_item_and_go_standby()
                else:
                    print("[ERROR] Impossibile rimuovere item dal rack")
                    self._restore_item_and_go_standby()
            else:
                print(f"[ERROR] Rack non ha items del colore richiesto: {self.current_color.value}")
                self._restore_item_and_go_standby()
        else:
            print(f"[ERROR] Nessun rack trovato in posizione {rack_pos}")
            self._restore_item_and_go_standby()

    def _restore_item_and_go_standby(self):
        """Metodo helper per ripristinare l'item e andare al punto standby"""
        # Riaggiunge l'item alla divisione_temp
        if self.current_dock and self.current_dock.divisione_temp and self.current_color:
            ordine_temp = self.current_dock.divisione_temp
            quantita_corrente = ordine_temp.get_capacita_per_colore(self.current_color)
            ordine_temp.set_capacita_per_colore(self.current_color, quantita_corrente + 1)

        # Reset dello stato e vai al punto standby
        self.reset_state()
        self.set_target(self.standby_position)
        self.state = "GOING_TO_STANDBY"

    def unload_items_to_dock(self):
        """Scarica l'item al dock"""
        if self.carried_items > 0 and self.current_dock:
            ordine = self.current_dock.current_order

            # Decrementa la quantità richiesta nell'ordine SOLO qui quando l'item viene consegnato
            quantita_corrente = ordine.get_capacita_per_colore(self.current_color)
            ordine.set_capacita_per_colore(self.current_color, quantita_corrente - 1)

            self.carried_items = 0
            print(f"[UNLOADING] Scaricato 1 unità di {self.current_color.value.upper()} al dock {self.current_dock.pos}")
            print(f"[UNLOADING] Capacità rimanente per {self.current_color.value.upper()}: {quantita_corrente}")
            print(f"[UNLOADING] Capacità totale rimanente: {ordine.get_capacita_totale()}")
            self.free = True
            # Controlla se l'ordine è completato usando SOLO l'ordine originale
            if ordine.get_capacita_totale() == 0:
                self.current_dock.current_order = None
                self.reset_state()
                self.state = "IDLE"
            else:
                # Continua con l'ordine - cerca il prossimo item
                self.reset_state()
                self.state = "IDLE"
        else:
            print("[ERROR] Nessun item da scaricare o dock non valido")
            self.reset_state()
            self.state = "IDLE"

    def find_closest_track_to_dock(self, dock_pos):
        """Trova la traccia più vicina a un dock"""
        x, y = dock_pos
        # Controlla le posizioni adiacenti al dock
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            adjacent_pos = (x + dx, y + dy)
            if self.model.is_track_position(adjacent_pos):
                return adjacent_pos
        return None

    def find_rack_with_items(self, color: str):
        """Trova un rack con items del colore specificato"""
        for (x, y), rack in self.model.shelves.items():
            if rack.get_colore() == color and rack.get_occupazione_corrente() > 0 and rack.get_occupazione_temp() > 0:
                # Decrementa l'occupazione_temp del rack
                rack.set_occupazione_temp(rack.get_occupazione_temp() - 1)
                # Restituisce la posizione della traccia adiacente al rack
                return (x, y + 1)
        return None

    def reset_state(self):
        """Resetta lo stato del muletto"""
        self.target_rack = None
        self.current_dock = None
        self.current_color = None
        self.target_position = None
        self.current_path = []


