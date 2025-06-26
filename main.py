import solara
from matplotlib import patches
from mesa.visualization import SolaraViz, make_plot_component

from dock import Dock, UnloadingDock, LoadingDock
from forkLift import ForkLift
from warehouse_model import WarehouseModel
from mesa.experimental.devs import ABMSimulator
from mesa.visualization import (
    CommandConsole,
    Slider,
    SolaraViz,
    make_plot_component,
    make_space_component,
)


def forkLiftportrayal(agent):
    if agent is None:
        return

    portrayal = {
        "size": 10,
    }

    if isinstance(agent, ForkLift):
        portrayal["color"] = "tab:red"
        portrayal["marker"] = "o"
        portrayal["zorder"] = 3
    elif isinstance(agent, UnloadingDock):
        portrayal["color"] = "tab:green"
        portrayal["marker"] = "s"
        portrayal["zorder"] = 2
    elif isinstance(agent, LoadingDock):
        portrayal["color"] = "tab:blue"
        portrayal["marker"] = "s"
        portrayal["zorder"] = 2
    return portrayal


model_params = {
    "width": 30,
    "height": 30,
    "num_unloading": Slider("Number of unloading docks", 1, 1, 5),
    "num_loading": Slider("Number of loading docks", 1, 1, 5),
    "num_unloading_forkLift": Slider("Number of unloading forkLifts", 1, 1, 10),
    "num_loading_forkLift": Slider("Number of loading forkLifts", 1, 1, 10),
}


def post_process_space(ax):
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])

    # Parametri del warehouse (valori fissi per evitare errori)
    width = 30
    height = 30
    num_unloading = 2
    num_loading = 2

    # Colori per i tipi di scaffali
    color_map = {
        "blue": "blue",
        "red": "red",
        "green": "green",
        "yellow": "yellow",
        "orange": "orange"
    }

    # Disegna gli scaffali dal modello
    # Nota: dovrai passare il modello a questa funzione o accedervi in altro modo
    # Per ora, ricreiamo la logica degli scaffali

    block_size = 10
    spacing = 3
    start_x = 3
    start_y = 4

    # Primo blocco
    origin_x, origin_y = start_x, start_y + block_size + spacing
    for dx in range(block_size):
        for dy in range(0, block_size, 2):
            x = origin_x + dx
            y = origin_y + dy

            if dy < 2:
                color = "blue"
            elif dy < 6:
                color = "red"
            else:
                color = "green"

            if x < 30 and y < 30:  # Assuming 30x30 grid
                rect = patches.Rectangle((x - 0.45, y - 0.45), 0.92, 0.92,
                                         linewidth=1, edgecolor='black',
                                         facecolor=color, alpha=0.7, zorder=1)
                ax.add_patch(rect)

        # Secondo blocco
    origin_x, origin_y = start_x + block_size + spacing, start_y + block_size + spacing
    for dx in range(block_size):
        for dy in range(0, block_size, 2):
            x = origin_x + dx
            y = origin_y + dy

            if dy < 2:
                color = "blue"
            elif dy < 6:
                color = "red"
            else:
                color = "green"

            if x < 30 and y < 30:  # Assuming 30x30 grid
                rect = patches.Rectangle((x - 0.45, y - 0.45), 0.92, 0.92,
                                            linewidth=1, edgecolor='black',
                                            facecolor=color, alpha=0.7, zorder=1)
                ax.add_patch(rect)
    # Terzo blocco
    origin_x, origin_y = start_x, start_y
    for dx in range(block_size):
        for dy in range(0, block_size, 2):
            x = origin_x + dx
            y = origin_y + dy

            if dy < 4:
                color = "orange"
            elif dy < 8:
                color = "yellow"
            else:
                color = "blue"

            if x < 30 and y < 30:
                rect = patches.Rectangle((x - 0.45, y - 0.45), 0.92, 0.92,
                                         linewidth=1, edgecolor='black',
                                         facecolor=color, alpha=0.7, zorder=1)
                ax.add_patch(rect)

    # Quarto blocco
    origin_x, origin_y = start_x + block_size + spacing, start_y
    for dx in range(block_size):
        for dy in range(0, block_size, 2):
            x = origin_x + dx
            y = origin_y + dy

            if dy < 4:
                color = "orange"
            elif dy < 8:
                color = "yellow"
            else:
                color = "blue"

            if x < 30 and y < 30:
                rect = patches.Rectangle((x - 0.45, y - 0.45), 0.92, 0.92,
                                         linewidth=1, edgecolor='black',
                                         facecolor=color, alpha=0.7, zorder=1)
                ax.add_patch(rect)

def post_process_lines(ax):
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.9))

space_component = make_space_component(
    forkLiftportrayal, draw_grid=False, post_process=post_process_space
)

simulator = ABMSimulator()
model = WarehouseModel(simulator=simulator)

page = SolaraViz(
    model,
    components=[space_component, CommandConsole],
    model_params=model_params,
    name="Warehouse",
    simulator=simulator,
)
page