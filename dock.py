# forkLift.py
from mesa.agent import Agent
from mesa.discrete_space import CellAgent, FixedAgent

class Dock(FixedAgent):


    def __init__(
            self,
            model,
            free = True,
    ):
        super().__init__(model)
        self.free = free
        self.current_order = None
        self.is_being_served = False


class UnloadingDock(Dock):

    def __init__(
            self,
            model,
            free=True,
    ):
        super().__init__(model)
        self.free = free
        self.current_order = None  # Aggiungo l'attributo per l'ordine corrente
        self.is_being_served = False  # Aggiunta per tracciare se un muletto sta servendo questo dock

    def receive_order(self, order):
        if self.free:
            self.current_order = order
            self.free = False
            self.is_being_served = False  # Aggiunta per tracciare se un muletto sta servendo questo dock
            return True
        else:
            return False

    def complete_order(self):
        completed_order = self.current_order
        self.current_order = None
        self.free = True
        self.is_being_served = False  # Aggiunta per tracciare se un muletto sta servendo questo dock
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
        self.is_being_served = False  # Aggiunta per tracciare se un muletto sta servendo questo dock

    def receive_order(self, order):
        if self.free:
            self.current_order = order
            self.is_being_served = False  # Reset quando riceve un nuovo ordine

            self.free = False
            return True
        else:
            return False

    def complete_order(self):
        completed_order = self.current_order
        self.current_order = None
        print(f"LoadingDock in {self.pos}: Ordine completato")

        self.is_being_served = False

        self.free = True
        return completed_order