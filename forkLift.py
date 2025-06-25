# forkLift.py
from mesa.agent import Agent
from mesa.discrete_space import CellAgent, FixedAgent

class ForkLift(CellAgent):


    def __init__(
            self,
            model,
            free = True,
    ):
        super().__init__(model)
        self.free = free

    def step(self):
        # Recupera la posizione attuale
        current_pos = self.pos  # (x, y)
        x, y = current_pos

        # Calcola la posizione a sinistra
        new_x = x - 1
        new_pos = (new_x, y)

        # Verifica se nuova posizione è dentro la griglia
        if new_x < 0:
            return  # Blocca se uscirebbe fuori dalla griglia

        # Verifica se la nuova posizione contiene un rack
        if self.model.is_rack_position(new_pos):
            return  # Muletto bloccato dal rack

        # Recupera il contenuto della cella di destinazione per altri ostacoli
        cellmates = self.model.grid.get_cell_list_contents(new_pos)

        # Se trova un altro agente (es. un altro muletto) resta fermo
        if len(cellmates) > 0:
            return  # Muletto bloccato da altro agente

        # Altrimenti effettua lo spostamento
        self.model.grid.move_agent(self, new_pos)
