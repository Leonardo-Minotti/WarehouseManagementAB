# forkLift.py
from mesa.agent import Agent
from mesa.discrete_space import CellAgent, FixedAgent

class Dock(FixedAgent):


    def __init__(
            self,
            model,
            capacity = 3,
            free = True,
    ):
        super().__init__(model)
        self.capacity = capacity
        self.free = free


class UnloadingDock(Dock):

    def __init__(
            self,
            model,
            capacity=3,
            free=True,
    ):
        super().__init__(model)
        self.capacity = capacity
        self.free = free

class LoadingDock(Dock):

    def __init__(
            self,
            model,
            capacity=3,
            free=True,
    ):
        super().__init__(model)
        self.capacity = capacity
        self.free = free
