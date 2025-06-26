import threading
import time

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

    # Correzione: usa isinstance con due argomenti
    if isinstance(agent, ForkLift):  # Corretto: usa la classe ForkLift, non il modulo
        portrayal["color"] = "tab:red"
        portrayal["marker"] = "o"
        portrayal["zorder"] = 1
    elif isinstance(agent, UnloadingDock):
        portrayal["color"] = "tab:green"
        portrayal["marker"] = "s"
        portrayal["zorder"] = 200
    elif isinstance(agent, LoadingDock):
        portrayal["color"] = "tab:blue"
        portrayal["marker"] = "s"
        portrayal["zorder"] = 200
    return portrayal


def warehouse_status_component(model):
    """Componente personalizzato per mostrare lo stato dei dock e della coda"""

    # Crea il contenuto HTML per i dock
    docks_info = []

    for i, dock in enumerate(model.loading_docks, 1):
        if dock.current_order is not None:
            # Dock occupato - mostra i colori dell'ordine
            colors_info = []
            for color, quantity in dock.current_order.get_tutte_capacita().items():
                if quantity > 0:  # Mostra solo i colori con quantità > 0
                    colors_info.append(f"{color.value.capitalize()}: {quantity}")

            colors_text = ", ".join(colors_info)
            dock_status = f"**Dock {i}:** {colors_text} (Totale: {dock.current_order.get_capacita_totale()})"
        else:
            # Dock libero
            dock_status = f"**Dock {i}:** Libero"

        docks_info.append(dock_status)

    # Crea il contenuto HTML per la coda
    queue_info = []
    if model.order_queue:
        queue_info.append(f"**Ordini in coda:**")
        for i, order in enumerate(model.order_queue, 1):
            queue_info.append(f" {order.get_capacita_totale()},")
    else:
        queue_info.append("**Ordini in coda:** Nessun ordine in attesa")

    # Combina tutto il contenuto
    content = []
    content.append("## 📦 Stato Warehouse")
    content.append("### 🚛 Dock di Carico")
    content.extend(docks_info)
    content.append("")  # Riga vuota
    content.extend(queue_info)

    # Aggiungi statistiche generali
    content.append("")
    content.append("### 📊 Statistiche")
    free_docks = sum(1 for dock in model.loading_docks if dock.free)
    content.append(f"**Dock liberi:** {free_docks}/{len(model.loading_docks)}")
    content.append(f"**Step corrente:** {model.step_counter}")
    content.append(f"**Prossimo ordine tra:** {model.order_time - (model.step_counter - model.last_order_step)} step")

    return solara.Markdown("\n".join(content))


model_params = {
    "width": 30,
    "height": 30,
    "num_unloading": Slider("Number of unloading docks", 1, 1, 5),
    "num_loading": Slider("Number of loading docks", 1, 1, 5),
    "dock_capacity": Slider("Maxinum dock capacity", 1, 5, 10),
    "order_time": Slider("Time order", 1, 10, 20)
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
    components=[space_component,warehouse_status_component, CommandConsole],
    model_params=model_params,
    name="Warehouse",
    simulator=simulator,
)
page  # noqa