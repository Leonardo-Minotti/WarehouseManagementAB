# forkLift.py
from mesa.agent import Agent

class ForkLift(Agent):
    def __init__(self, model):
        super().__init__(model)
        # puoi aggiungere altri attributi qui (ad es. stato, capacità, ecc.)

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

        # Recupera il contenuto della cella di destinazione
        cellmates = self.model.grid.get_cell_list_contents(new_pos)

        # Se trova un ostacolo (es. una StaticTile speciale) resta fermo
        ostacolo = any(
            hasattr(a, 'tile_type') and a.tile_type in ["Rack", "Unloading", "Loading"]
            for a in cellmates
        )
        if ostacolo:
            return  # Muletto bloccato

        # Altrimenti effettua lo spostamento
        self.model.grid.move_agent(self, new_pos)