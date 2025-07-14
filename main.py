import solara
from matplotlib import patches
from mesa.visualization import SolaraViz, make_plot_component

from dock import Dock, UnloadingDock, LoadingDock
from forkLift import ForkLift, UnloadingForkLift, LoadingForkLift
from warehouse_model import WarehouseModel
from mesa.experimental.devs import ABMSimulator
from mesa.visualization import (
    CommandConsole,
    Slider,
    SolaraViz,
    make_plot_component,
    make_space_component,
)

# Variabile globale per accedere al modello
current_model = None


def forkLiftportrayal(agent):
    if agent is None:
        return

    portrayal = {
        "size": 10,
    }

    if isinstance(agent, UnloadingForkLift):
        portrayal["color"] = "tab:red"
        portrayal["marker"] = "o"
        portrayal["zorder"] = 3
    elif isinstance(agent, LoadingForkLift):
        portrayal["color"] = "tab:orange"
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


def warehouse_status_component(model):
    global current_model
    current_model = model  # Aggiorna la variabile globale

    # Crea il contenuto per i dock di carico
    loading_docks_info = []
    for i, dock in enumerate(model.loading_docks, 1):
        if dock.current_order is not None:
            # Dock occupato - mostra i colori dell'ordine
            colors_info = []
            for color, quantity in dock.current_order.get_tutte_capacita().items():
                if quantity > 0:  # Mostra solo i colori con quantità > 0
                    colors_info.append(f"{color.value.capitalize()}: {quantity}")

            colors_text = ", ".join(colors_info)
            dock_status = f"**Dock Carico {i}:** {colors_text} (Totale: {dock.current_order.get_capacita_totale()})\n"
        else:
            # Dock libero
            dock_status = f"**Dock Carico {i}:** Libero \n"

        loading_docks_info.append(dock_status)

    # Crea il contenuto per i dock di scarico
    unloading_docks_info = []
    for i, dock in enumerate(model.unloading_docks, 1):
        if dock.current_order is not None:
            # Dock occupato - mostra i colori dell'ordine
            colors_info = []
            for color, quantity in dock.current_order.get_tutte_capacita().items():
                if quantity > 0:  # Mostra solo i colori con quantità > 0
                    colors_info.append(f"{color.value.capitalize()}: {quantity}")

            colors_text = ", ".join(colors_info)
            dock_status = f"**Dock Scarico {i}:** {colors_text} (Totale: {dock.current_order.get_capacita_totale()})\n"
        else:
            # Dock libero
            dock_status = f"**Dock Scarico {i}:** Libero \n"

        unloading_docks_info.append(dock_status)

    # Crea il contenuto per la coda di carico
    loading_queue_info = []
    if hasattr(model, 'loading_order_queue') and model.loading_order_queue:
        loading_queue_info.append(f"**Ordini di carico in coda:**")
        for i, order in enumerate(model.loading_order_queue, 1):
            loading_queue_info.append(f" {order.get_capacita_totale()},")
    else:
        loading_queue_info.append("**Ordini di carico in coda:** Nessun ordine in attesa")

    # Crea il contenuto per la coda di scarico
    unloading_queue_info = []
    if hasattr(model, 'unloading_order_queue') and model.unloading_order_queue:
        unloading_queue_info.append(f"**Ordini di scarico in coda:**")
        for i, order in enumerate(model.unloading_order_queue, 1):
            unloading_queue_info.append(f" {order.get_capacita_totale()},")
    else:
        unloading_queue_info.append("**Ordini di scarico in coda:** Nessun ordine in attesa")

    # Ottieni statistiche del magazzino
    stats = model.get_warehouse_stats()

    # Combina tutto il contenuto
    content = []
    content.append("## 📦 Stato Warehouse")

    content.append("### 🚛 Dock di Carico")
    content.extend(loading_docks_info)
    content.append("")  # Riga vuota
    content.extend(loading_queue_info)

    content.append("")  # Riga vuota
    content.append("### 📤 Dock di Scarico")
    content.extend(unloading_docks_info)
    content.append("")  # Riga vuota
    content.extend(unloading_queue_info)

    # Aggiungi statistiche generali
    content.append("")
    content.append("### 📊 Statistiche")
    free_loading_docks = sum(1 for dock in model.loading_docks if dock.free)
    content.append(f"**Dock di carico liberi:** {free_loading_docks}/{len(model.loading_docks)}")

    if hasattr(model, 'unloading_docks'):
        free_unloading_docks = sum(1 for dock in model.unloading_docks if dock.free)
        content.append(f"**Dock di scarico liberi:** {free_unloading_docks}/{len(model.unloading_docks)}")

    content.append(f"**Step corrente:** {model.step_counter}")

    # Gestisci i contatori per la compatibilità
    if hasattr(model, 'last_loading_order_step'):
        next_loading_order = model.order_time - (model.step_counter - model.last_loading_order_step)
        content.append(f"**Prossimo ordine carico tra:** {next_loading_order} step")
    else:
        next_order = model.order_time - (model.step_counter - model.last_order_step)
        content.append(f"**Prossimo ordine tra:** {next_order} step")

    if hasattr(model, 'last_unloading_order_step') and hasattr(model, 'unloading_order_time'):
        next_unloading_order = model.unloading_order_time - (model.step_counter - model.last_unloading_order_step)
        content.append(f"**Prossimo ordine scarico tra:** {next_unloading_order} step")

    return solara.Markdown("\n".join(content))


model_params = {
    "width": 30,
    "height": 30,
    "num_unloading": Slider("Number of unloading docks", 1, 1, 5),
    "num_loading": Slider("Number of loading docks", 1, 1, 5),
    "dock_capacity": Slider("Maxinum dock capacity", 1, 5, 10),
    "order_time": Slider("Time order", 1, 10, 20),
    "num_unloading_forkLift": Slider("Number of unloading forkLifts", 1, 1, 10),
    "num_loading_forkLift": Slider("Number of loading forkLifts", 1, 1, 10),
    "initial_warehouse_filling": Slider("initial warehouse filling percentage", 1, 1, 100)
}


def post_process_space(ax):
    global current_model

    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])

    # Prova a ottenere il modello dall'assi se la variabile globale non è aggiornata
    model_to_use = current_model
    if hasattr(ax, 'figure') and hasattr(ax.figure, 'model'):
        model_to_use = ax.figure.model
    elif hasattr(ax, '_model'):
        model_to_use = ax._model

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

            if x < 30 and y < 30:
                rect = patches.Rectangle((x - 0.45, y - 0.45), 0.92, 0.92,
                                         linewidth=1, edgecolor='black',
                                         facecolor=color, alpha=0.7, zorder=1)
                ax.add_patch(rect)

                # Ottieni l'occupazione dal modello
                occupazione = 0
                if model_to_use and (x, y) in model_to_use.shelves:
                    rack = model_to_use.shelves[(x, y)]
                    occupazione = rack.get_occupazione_corrente()

                display_text = f"{occupazione}"

                ax.text(x, y, display_text,
                        ha='center', va='center',
                        fontsize=5.3, fontweight='bold',
                        color='black', zorder=2)

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

            if x < 30 and y < 30:
                rect = patches.Rectangle((x - 0.45, y - 0.45), 0.92, 0.92,
                                         linewidth=1, edgecolor='black',
                                         facecolor=color, alpha=0.7, zorder=1)
                ax.add_patch(rect)

                occupazione = 0
                if model_to_use and (x, y) in model_to_use.shelves:
                    rack = model_to_use.shelves[(x, y)]
                    occupazione = rack.get_occupazione_corrente()

                display_text = f"{occupazione}"

                ax.text(x, y, display_text,
                        ha='center', va='center',
                        fontsize=5.3, fontweight='bold',
                        color='black', zorder=2)

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

                occupazione = 0
                if model_to_use and (x, y) in model_to_use.shelves:
                    rack = model_to_use.shelves[(x, y)]
                    occupazione = rack.get_occupazione_corrente()

                display_text = f"{occupazione}"

                ax.text(x, y, display_text,
                        ha='center', va='center',
                        fontsize=5.3, fontweight='bold',
                        color='black', zorder=2)

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

                occupazione = 0
                if model_to_use and (x, y) in model_to_use.shelves:
                    rack = model_to_use.shelves[(x, y)]
                    occupazione = rack.get_occupazione_corrente()

                display_text = f"{occupazione}"

                ax.text(x, y, display_text,
                        ha='center', va='center',
                        fontsize=5.3, fontweight='bold',
                        color='black', zorder=2)


def custom_space_component(model):
    """Componente spazio personalizzato che riceve il modello direttamente"""
    global current_model
    current_model = model  # Aggiorna la variabile globale quando questo componente viene chiamato

    def post_process_with_model(ax):
        ax._model = model  # Allega il modello all'asse
        post_process_space(ax)

    return make_space_component(
        forkLiftportrayal, draw_grid=False, post_process=post_process_with_model
    )(model)


simulator = ABMSimulator()
model = WarehouseModel(simulator=simulator)
current_model = model  # Inizializza la variabile globale

page = SolaraViz(
    model,
    components=[custom_space_component, warehouse_status_component, CommandConsole],
    model_params=model_params,
    name="Warehouse",
    simulator=simulator,
)
page