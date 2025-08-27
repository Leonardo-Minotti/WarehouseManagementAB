# forkLift.py
from mesa.discrete_space import FixedAgent

from order import Order


class Dock(FixedAgent):


    def __init__(
            self,
            model,
            free = True,
    ):
        super().__init__(model)
        self.free = free
        self.current_order = None


class UnloadingDock(Dock):

    def __init__(
            self,
            model,
            free=True,
    ):
        super().__init__(model)
        self.free = free
        self.current_order = None  # Aggiungo l'attributo per l'ordine corrente
        self.divisione_temp = None


    def receive_order(self, order):
        if self.free:
            self.current_order = order
            self.divisione_temp = Order(order.get_capacita_totale())
            for colore, qty in order.get_tutte_capacita().items():
                self.divisione_temp.set_capacita_per_colore(colore, qty)
            self.free = False
            self.current_order.step_inizio = self.model.steps
            return True
        else:
            return False

    def complete_order(self):
        completed_order = self.current_order
        self.current_order.step_fine = self.model.steps
        durata = self.current_order.step_fine - self.current_order.step_inizio

        self.model.ordini_scarico_durata_processamento.append(durata)
        self.model.ordini_scarico_completati += 1
        self.current_order = None
        self.free = True
        self._order_completed = True  # Aggiungi questo flag


        return completed_order


class LoadingDock(Dock):

    def __init__(
            self,
            model,
            free=True,
    ):
        super().__init__(model)
        self.free = free
        self.current_order = None  # Aggiungo l'attributo per l'ordine corrente
        self.divisione_temp = None

    def receive_order(self, order):
        if self.free:
            self.current_order = order
            # Crea una copia dell'ordine per le prenotazioni
            self.divisione_temp = Order(order.get_capacita_totale())
            # Copia le capacità per colore
            for colore, qty in order.get_tutte_capacita().items():
                self.divisione_temp.set_capacita_per_colore(colore, qty)

            self.free = False
            self.current_order.step_inizio = self.model.steps

            return True
        else:
            return False

    def complete_order(self):
        completed_order = self.current_order
        self.current_order.step_fine = self.model.steps
        durata = self.current_order.step_fine - self.current_order.step_inizio
        self.model.ordini_carico_durata_processamento.append(durata)
        self.model.ordini_carico_completati += 1
        self.current_order = None
        self.free = True
        self._order_completed = True  # Aggiungi questo flag
        return completed_order