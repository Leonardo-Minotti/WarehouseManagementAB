
import solara
from matplotlib import patches
from mesa.visualization import SolaraViz, make_plot_component
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

    # Correzione: usa isinstance con due argomenti
    if isinstance(agent, ForkLift):  # Corretto: usa la classe ForkLift, non il modulo
        portrayal["color"] = "tab:red"
        portrayal["marker"] = "o"
        portrayal["zorder"] = 1
    return portrayal


model_params = {
    "width": 30,
    "height": 30,
    "num_unloading": Slider("Number of unloading docks", 1, 1, 5),
    "num_loading": Slider("Number of loading docks", 1, 1, 5)
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

    # Disegna le zone di unloading (giallo) - lato destro
    center_y = height // 2
    start_y = center_y - num_unloading // 2
    for i in range(num_unloading):
        y = start_y + i
        if 0 <= y < height:
            # Crea un rettangolo giallo per la zona unloading
            rect = patches.Rectangle((width - 1 - 0.5, y - 0.5), 1, 1,
                                     linewidth=1, edgecolor='black',
                                     facecolor='yellow', alpha=0.7, zorder=0)
            ax.add_patch(rect)

    # Disegna le zone di loading (blu) - parte inferiore
    for x in range(num_loading):
        # Crea un rettangolo blu per la zona loading
        rect = patches.Rectangle((x - 0.5, -0.5), 1, 1,
                                 linewidth=1, edgecolor='black',
                                 facecolor='blue', alpha=0.7, zorder=0)
        ax.add_patch(rect)

    # Disegna i rack (grigio)
    block_size = 10
    spacing = 3
    start_x = 3
    start_y = 4

    # Posizioni dei 4 blocchi
    block_origins = [
        (start_x, start_y + block_size + spacing),  # Top-left
        (start_x + block_size + spacing, start_y + block_size + spacing),  # Top-right
        (start_x, start_y),  # Bottom-left
        (start_x + block_size + spacing, start_y)  # Bottom-right
    ]

    for origin_x, origin_y in block_origins:
        for dx in range(block_size):
            for dy in range(block_size):
                if dy % 2 == 0:
                    x = origin_x + dx
                    y = origin_y + dy
                    if x < width and y < height:
                        rect = patches.Rectangle((x - 0.5, y - 0.5), 1, 1,
                                                 linewidth=1, edgecolor='black',
                                                 facecolor='gray', alpha=0.5, zorder=0)
                        ax.add_patch(rect)


def post_process_lines(ax):
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.9))

space_component = make_space_component(
    forkLiftportrayal, draw_grid=False, post_process=post_process_space
)

# Variabili reattive globali (se necessarie per implementazioni future)
# num_unloading = solara.reactive(2)
# num_loading = solara.reactive(2)
# model = solara.reactive(None)
# tick = solara.reactive(0)

simulator = ABMSimulator()
model = WarehouseModel(simulator=simulator)

page = SolaraViz(
    model,
    components=[space_component, CommandConsole],
    model_params=model_params,
    name="Warehouse",
    simulator=simulator,
)
page  # noqa