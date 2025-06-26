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


class UnloadingDock(Dock):

    def __init__(
            self,
            model,
            free=True,
    ):
        super().__init__(model)
        self.free = free
        self.current_order = None  # Aggiungo l'attributo per l'ordine corrente

    def receive_order(self, order):
        if self.free:
            self.current_order = order
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

    def receive_order(self, order):
        if self.free:
            self.current_order = order
            self.free = False
            return True
        else:
            return False

    def complete_order(self):
        completed_order = self.current_order
        self.current_order = None
        self.free = True
        return completed_order