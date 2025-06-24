import threading
import time

import solara
from warehouse_model import WarehouseModel

# Variabili reattive globali
num_unloading = solara.reactive(2)
num_loading = solara.reactive(2)
order_frequency = solara.reactive(5)  # ogni quanti step arriva un ordine
truck_capacity = solara.reactive(10)  # quanti pacchi può trasportare un camion
model = solara.reactive(None)
tick = solara.reactive(0)
order_thread_started = False


# Colori celle
color_map = {
    "Unloading": "orange",
    "Loading": "blue",
    "Rack": "gray",
    "Empty": "white"
}
cell_size_px = 30

@solara.component
def SetupPage():
    solara.Title("Setup Magazzino")
    router = solara.use_router()  # ✅ Ottieni il router all’interno del componente

    solara.Markdown("### Seleziona quante zone di scarico e carico vuoi")

    with solara.Row():
        solara.SliderInt("Zone di Scarico", value=num_unloading, min=1, max=5)
        solara.SliderInt("Zone di Carico", value=num_loading, min=1, max=5)

    with solara.Row():
        solara.SliderInt("Frequenza ordini (step)", value=order_frequency, min=10, max=25)
        solara.SliderInt("Capacità camion", value=truck_capacity, min=5, max=20)

    def on_click():
        model.value = WarehouseModel(
            width=30,
            height=30,
            num_unloading=num_unloading.value,
            num_loading=num_loading.value,
            order_frequency = order_frequency.value,
            truck_capacity = truck_capacity.value
        )
        router.push("magazzino")


    solara.Button("Avvia Simulazione", on_click=on_click)


@solara.component
def WarehouseGrid(model: WarehouseModel):
    _ = tick.value

    styles = {
        "display": "grid",
        "gridTemplateColumns": f"repeat({model.grid.width}, {cell_size_px}px)",
        "gridTemplateRows": f"repeat({model.grid.height}, {cell_size_px}px)",
        "gap": "1px"
    }

    with solara.Div(style=styles):
        for y in reversed(range(model.grid.height)):
            for x in range(model.grid.width):
                agents = model.grid.get_cell_list_contents((x, y))
                if agents:
                    color = color_map.get(agents[0].tile_type, "white")
                else:
                    color = color_map["Empty"]

                # 👇 Check se c’è un ordine in questa cella
                order = model.orders_on_grid.get((x, y))
                if order is not None:
                    content = str(order)
                else:
                    content = ""

                # 👇 Disegna la cella con l’eventuale ordine
                solara.Div(
                    style={
                        "backgroundColor": color,
                        "width": f"{cell_size_px}px",
                        "height": f"{cell_size_px}px",
                        "border": "1px solid #ccc",
                        "display": "flex",
                        "justifyContent": "center",
                        "alignItems": "center",
                        "fontWeight": "bold"                    },
                    children=[solara.Text(content)]
                )


@solara.component
def SimulationPage():
    solara.Title("Simulazione Magazzino")

    _ = tick.value
    if model.value is None:
        solara.Markdown("Nessuna simulazione avviata.")
        return

    # Reactive per forzare il refresh
    global order_thread_started
    if not order_thread_started:
        def order_loop():
            while True:
                time.sleep(model.value.order_frequency)
                model.value.generate_order()
                tick.value += 1  # Forza Solara a ridisegnare la UI

        threading.Thread(target=order_loop, daemon=True).start()
        order_thread_started = True

    with solara.Row():
        WarehouseGrid(model.value)
        with solara.Column():
            solara.Markdown("### Ordini in coda:")
            if model.value.order_queue:
                orders_str = ", ".join(str(order) for order in model.value.order_queue)
                solara.Text(orders_str)
            else:
                solara.Text("Nessun ordine in coda")


#Routing
routes = [
    solara.Route(path="/", component=SetupPage),
    solara.Route(path="magazzino", component=SimulationPage),
]


@solara.component
def Page():
    solara.RouteBrowser(routes=routes)
