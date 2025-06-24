import solara
from warehouse_model import WarehouseModel

# Variabili reattive globali
num_unloading = solara.reactive(2)
num_loading = solara.reactive(2)
model = solara.reactive(None)

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

    def on_click():
        model.value = WarehouseModel(
            width=20,
            height=20,
            num_unloading=num_unloading.value,
            num_loading=num_loading.value
        )
        router.push("magazzino")


    solara.Button("Avvia Simulazione", on_click=on_click)


@solara.component
def WarehouseGrid(model: WarehouseModel):
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
                solara.Div(
                    style={
                        "backgroundColor": color,
                        "width": f"{cell_size_px}px",
                        "height": f"{cell_size_px}px",
                        "border": "1px solid #ccc"
                    }
                )

@solara.component
def SimulationPage():
    solara.Title("Simulazione Magazzino")
    if model.value is None:
        solara.Markdown("⚠️ Nessuna simulazione avviata.")
        return
    WarehouseGrid(model.value)

#Routing
routes = [
    solara.Route(path="/", component=SetupPage),
    solara.Route(path="magazzino", component=SimulationPage),
]


@solara.component
def Page():
    solara.RouteBrowser(routes=routes)
