import solara
from matplotlib import patches, pyplot as plt

from dock import Dock, UnloadingDock, LoadingDock
from forkLift import ForkLift, UnloadingForkLift, LoadingForkLift
from warehouse_model import WarehouseModel
from mesa.experimental.devs import ABMSimulator
from mesa.visualization import (
    Slider,
    SolaraViz,
    make_space_component,
)

# Importa le nuove classi

# Variabile globale per accedere al modello
current_model = None


def forkLiftportrayal(agent):
    if agent is None:
        return

    portrayal = {
        "size": 10,
    }

    if isinstance(agent, UnloadingForkLift):
        if not agent.free:
            portrayal["color"] = "tab:red"
            portrayal["marker"] = "^"
            portrayal["zorder"] = 3
        else:
            portrayal["color"] = "tab:red"
            portrayal["marker"] = "o"
            portrayal["zorder"] = 3
    elif isinstance(agent, LoadingForkLift):
        if not agent.free:
            portrayal["color"] = "tab:orange"
            portrayal["marker"] = "^"
            portrayal["zorder"] = 3
        else:
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

    if hasattr(model, 'last_unloading_order_step'):
        next_unloading_order = model.order_time - (model.step_counter - model.last_unloading_order_step)
        content.append(f"**Prossimo ordine scarico tra:** {next_unloading_order} step")

    return solara.Markdown("\n".join(content))


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

    # === TRACCE DEI MULETTI ===
    # Disegna i percorsi che i muletti possono seguire

    # Colore e stile delle tracce
    track_color = 'gray'
    track_width = 2
    track_alpha = 0.6

    # Corridoio orizzontale principale (tra i blocchi superiori e inferiori)
    corridor_y = (start_y + block_size + spacing / 2) - 0.5
    ax.plot([start_x - 2, model_to_use.width - 2], [corridor_y, corridor_y],
            color=track_color, linewidth=track_width, alpha=track_alpha, zorder=0.5)

    # Corridoio orizzontale alto
    corridor_y = model_to_use.height - 2
    ax.plot([start_x - 2, model_to_use.width - 2], [corridor_y, corridor_y],
            color=track_color, linewidth=track_width, alpha=track_alpha, zorder=0.5)

    # Corridoio orizzontale basso
    corridor_y = start_y - 3
    ax.plot([start_x - 2, model_to_use.width - 2], [corridor_y, corridor_y],
            color=track_color, linewidth=track_width, alpha=track_alpha, zorder=0.5)

    # Corridoi orizzontali all'interno dei blocchi
    for dy in range(1, block_size, 2):  # Tracce tra le righe di rack
        # Bloccchi superiori
        corridor_y1 = start_y + block_size + spacing + dy
        ax.plot([start_x - 2, model_to_use.width - 2], [corridor_y1, corridor_y1],
                color=track_color, linewidth=1, alpha=track_alpha, zorder=0.5)

        # Blocchi inferiori
        corridor_y3 = start_y + dy
        ax.plot([start_x - 2, model_to_use.width - 2], [corridor_y3, corridor_y3],
                color=track_color, linewidth=1, alpha=track_alpha, zorder=0.5)

    # Corridoio verticale centrale (tra i blocchi sinistri e destri)
    corridor_x = (start_x + block_size + spacing / 2) - 0.5
    ax.plot([corridor_x, corridor_x], [start_y - 3, model_to_use.height - 2],
            color=track_color, linewidth=track_width, alpha=track_alpha, zorder=0.5)

    # Corridoio verticale a sinistra
    corridor_x = start_x - 2
    ax.plot([corridor_x, corridor_x], [start_y - 3, model_to_use.height - 2],
            color=track_color, linewidth=track_width, alpha=track_alpha, zorder=0.5)

    # Corridoio verticale a destra
    corridor_x = model_to_use.width - 2
    ax.plot([corridor_x, corridor_x], [start_y - 3, model_to_use.height - 2],
            color=track_color, linewidth=track_width, alpha=track_alpha, zorder=0.5)

    # FINE DISCEGNO TRACCE

    # Disegna Stand-by zone 3x3  in (14, 1) UNLOADING
    square_center_x = 28
    square_center_y = 28
    square_size = 3  # 3x3
    square_color = 'lightgray'

    # Calcola il punto in basso a sinistra
    bottom_left_x = square_center_x - 1
    bottom_left_y = square_center_y - 1

    # Disegna un singolo rettangolo grande
    rect = patches.Rectangle((bottom_left_x - 0.45, bottom_left_y - 0.45),
                             0.92 * square_size, 0.92 * square_size,
                             linewidth=1.5, edgecolor='lightgray',
                             facecolor=square_color, alpha=0.7, zorder=1)
    ax.add_patch(rect)

    # Disegna Stand-by zone 3x3  in (14, 1) LOADING
    square_center_x = 14
    square_center_y = 1

    # Calcola il punto in basso a sinistra
    bottom_left_x = square_center_x - 1
    bottom_left_y = square_center_y - 1

    # Disegna un singolo rettangolo grande
    rect = patches.Rectangle((bottom_left_x - 0.45, bottom_left_y - 0.45),
                             0.92 * square_size, 0.92 * square_size,
                             linewidth=1.5, edgecolor='lightgray',
                             facecolor=square_color, alpha=0.7, zorder=1)
    ax.add_patch(rect)
    ''''
    # === AGGIUNGI QUESTA SEZIONE PER I BORDI DELLE CELLE ===
    # Disegna i bordi di tutte le celle della griglia
    grid_color = 'red'
    grid_alpha = 1
    grid_linewidth = 0.5

    # Linee verticali
    for x in range(model_to_use.width + 1):
        ax.plot([x - 0.5, x - 0.5], [-0.5, model_to_use.height - 0.5],
                color=grid_color, linewidth=grid_linewidth, alpha=grid_alpha, zorder=0.1)

    # Linee orizzontali
    for y in range(model_to_use.height + 1):
        ax.plot([-0.5, model_to_use.width - 0.5], [y - 0.5, y - 0.5],
                color=grid_color, linewidth=grid_linewidth, alpha=grid_alpha, zorder=0.1)
    # === FINE SEZIONE BORDI CELLE ===

    block_size = 10
    spacing = 3
    start_x = 3
    start_y = 4

    # TODO : FINE GRIGLIA DA ELIMINARE
'''''

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


def create_warehouse_plots(model):
    """Crea grafici per visualizzare i dati della simulazione"""

    if not model.data_collector['step']:
        return None

    # Crea una figura con subplots
    fig, axes = plt.subplots(4, 2, figsize=(15, 20))
    fig.suptitle('Analisi Prestazioni Warehouse', fontsize=16, fontweight='bold')

    steps = model.data_collector['step']

    # Grafico 1: Occupazione Magazzino
    ax1 = axes[0, 0]
    ax1.plot(steps, model.data_collector['occupazione_totale'],
             color='blue', linewidth=2, label='Occupazione Totale')
    ax1.set_title('Occupazione Magazzino nel Tempo')
    ax1.set_xlabel('Step')
    ax1.set_ylabel('Occupazione (%)')
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # Grafico 2: Ordini Processati
    ax2 = axes[0, 1]
    ax2.plot(steps, model.data_collector['ordini_carico_processati'],
             color='green', linewidth=2, label='Ordini Carico')
    ax2.plot(steps, model.data_collector['ordini_scarico_processati'],
             color='red', linewidth=2, label='Ordini Scarico')
    ax2.set_title('Ordini Processati')
    ax2.set_xlabel('Step')
    ax2.set_ylabel('Numero Ordini')
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    # Grafico 3: Efficienza Dock
    ax3 = axes[1, 0]
    dock_carico_occupati = [len(model.loading_docks) - liberi
                            for liberi in model.data_collector['dock_carico_liberi']]
    dock_scarico_occupati = [len(model.unloading_docks) - liberi
                             for liberi in model.data_collector['dock_scarico_liberi']]

    ax3.plot(steps, dock_carico_occupati, color='orange', linewidth=2, label='Dock Carico Occupati')
    ax3.plot(steps, dock_scarico_occupati, color='purple', linewidth=2, label='Dock Scarico Occupati')
    ax3.set_title('Utilizzo Dock')
    ax3.set_xlabel('Step')
    ax3.set_ylabel('Numero Dock Occupati')
    ax3.grid(True, alpha=0.3)
    ax3.legend()

    # Grafico 4: Code di Attesa
    ax4 = axes[1, 1]
    ax4.plot(steps, model.data_collector['ordini_carico_in_coda'],
             color='brown', linewidth=2, label='Coda Carico')
    ax4.plot(steps, model.data_collector['ordini_scarico_in_coda'],
             color='pink', linewidth=2, label='Coda Scarico')
    ax4.set_title('Ordini in Coda')
    ax4.set_xlabel('Step')
    ax4.set_ylabel('Numero Ordini in Coda')
    ax4.grid(True, alpha=0.3)
    ax4.legend()

    # Grafico 5: Muletti liberi
    ax5 = axes[2, 0]
    ax5.plot(steps, model.data_collector['muletti_carico_liberi'],
             color='cyan', linewidth=2, label='Muletti Carico Liberi')
    ax5.plot(steps, model.data_collector['muletti_scarico_liberi'],
             color='magenta', linewidth=2, label='Muletti Scarico Liberi')
    ax5.set_title('Muletti Liberi nel Tempo')
    ax5.set_xlabel('Step')
    ax5.set_ylabel('Numero Muletti Liberi')
    ax5.grid(True, alpha=0.3)
    ax5.legend()

    # Grafico 6: Tempo Medio di Processamento Ordini
    ax6 = axes[2, 1]
    ax6.plot(steps, model.data_collector['tempo_medio_ordine_carico'],
             color='green', linewidth=2, label='Tempo Medio Ordine_Carico')
    ax6.plot(steps, model.data_collector['tempo_medio_ordine_scarico'],
             color='red', linewidth=2, label='Tempo Medio Ordine_Scarico')

    ax6.set_title('Tempo Medio di Processamento Ordini carico e scarico')
    ax6.set_xlabel('Step')
    ax6.set_ylabel('Tempo Medio (in step)')
    ax6.grid(True, alpha=0.3)
    ax6.legend()


    # Grafico 7: Distribuzione dei pacchi per colore nel magazzino (con spazio vuoto)
    ax7 = axes[3, 0]
    distribuzioni_colori = model.data_collector.get("distribuzione_colori", [])
    if distribuzioni_colori:
        distribuzione_finale = distribuzioni_colori[-1]  # Ultimo step

        # Rimuovi i colori con quantità 0
        colori = [colore for colore, count in distribuzione_finale.items() if count > 0]
        valori = [count for colore, count in distribuzione_finale.items() if count > 0]

        mappa_colori = {
            'blue': 'blue',
            'red': 'red',
            'green': 'green',
            'yellow': 'gold',
            'orange': 'orange',
            'gray': 'lightgray'
        }
        colori_visuali = [mappa_colori[colore] for colore in colori]

        ax7.pie(valori, labels=colori, autopct='%1.1f%%', colors=colori_visuali)
        ax7.set_title("Distribuzione pacchi per colore (con spazio vuoto)")

    ax8 = axes[3, 1]
    ax8.axis('off')
    plt.tight_layout()
    return fig

# Componente per mostrare i grafici nella visualizzazione Solara
def warehouse_plots_component(model):
    """Componente Solara per visualizzare i grafici"""
    fig = create_warehouse_plots(model)
    if fig:
        return solara.FigureMatplotlib(fig)
    else:
        return solara.Markdown("**Nessun dato disponibile per i grafici**")


model_params = {
    "width": 30,
    "height": 30,
    "num_unloading": Slider("Number of unloading docks", 1, 1, 5),
    "num_loading": Slider("Number of loading docks", 1, 1, 5),
    "dock_capacity": Slider("Maxinum dock capacity", 1, 5, 10),
    "order_time": Slider("Time order", 1, 10, 100),
    "num_unloading_forkLift": Slider("Number of unloading forkLifts", 1, 1, 10),
    "num_loading_forkLift": Slider("Number of loading forkLifts", 1, 1, 10),
    "initial_warehouse_filling": Slider("initial warehouse filling percentage", 1, 1, 100)
}



# Creazione del simulatore e del modello
simulator = ABMSimulator()
model = WarehouseModel(simulator=simulator)


current_model = model  # Inizializza la variabile globale

# Modifica la creazione della pagina per includere i grafici
page = SolaraViz(
    model,
    components=[
        custom_space_component,
        warehouse_status_component,
        warehouse_plots_component,
    ],
    model_params=model_params,
    name="Warehouse",
    simulator=simulator,
)
page