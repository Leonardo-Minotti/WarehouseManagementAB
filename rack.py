class Rack:

    def __init__(self, capienza: int, colore: str):
        self._capienza = capienza
        self._colore = colore
        self._occupazione_corrente = 0
        self._occupazione_temp = 0

    # Getter per capienza
    def get_capienza(self) -> int:
        return self._capienza

    # Setter per capienza
    def set_capienza(self, nuova_capienza: int) -> None:
        if nuova_capienza < 0:
            raise ValueError("La capienza non può essere negativa")
        self._capienza = nuova_capienza

    def get_occupazione_temp(self) -> int:
        return self._occupazione_temp

    def set_occupazione_temp(self, nuova_occupazione: int) -> None:
        if nuova_occupazione < 0:
            raise ValueError("L'occupazione non può essere negativa")
        if nuova_occupazione > self._capienza:
            raise ValueError("L'occupazione non può superare la capienza massima")
        self._occupazione_temp = nuova_occupazione

    # Getter per colore
    def get_colore(self) -> str:
        return self._colore

    # Setter per colore
    def set_colore(self, nuovo_colore: str) -> None:
        self._colore = nuovo_colore

    # Getter per occupazione corrente
    def get_occupazione_corrente(self) -> int:
        return self._occupazione_corrente

    # Setter per occupazione corrente
    def set_occupazione_corrente(self, occupazione: int) -> None:
        if occupazione < 0:
            raise ValueError("L'occupazione non può essere negativa")
        if occupazione > self._capienza:
            raise ValueError("L'occupazione non può superare la capienza massima")
        self._occupazione_corrente = occupazione

    # Metodi di utilità
    def get_spazio_disponibile(self) -> int:
        return self._capienza - self._occupazione_corrente

    def get_percentuale_occupazione(self) -> float:
        if self._capienza == 0:
            return 0.0
        return (self._occupazione_corrente / self._capienza) * 100

    def is_pieno(self) -> bool:
        return self._occupazione_corrente >= self._capienza

    def aggiungi_items(self, quantita: int) -> bool:
        if quantita <= 0:
            return False
        if self._occupazione_corrente + quantita <= self._capienza:
            self._occupazione_corrente += quantita
            return True
        return False

    def rimuovi_items(self, quantita: int) -> bool:
        if quantita <= 0:
            return False
        if self._occupazione_corrente >= quantita:
            self._occupazione_corrente -= quantita
            return True
        return False

    def get_display_text(self) -> str:
        return f"{self._occupazione_corrente}/{self._capienza}"

    def get_display_text_short(self) -> str:
        return str(self._occupazione_corrente)

    def __str__(self) -> str:
        return f"Rack(colore={self._colore}, capienza={self._capienza}, occupazione={self._occupazione_corrente})"

    def __repr__(self) -> str:
         return f"Rack({self._capienza}, '{self._colore}')"