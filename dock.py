# forkLift.py
from mesa.agent import Agent
from mesa.discrete_space import CellAgent, FixedAgent

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
            return True
        else:
            return False

    def complete_order(self):
        completed_order = self.current_order
        self.current_order = None
        self.free = True
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
            return True
        else:
            return False

    def complete_order(self):
        completed_order = self.current_order
        self.current_order = None
        self.free = True
        return completed_order