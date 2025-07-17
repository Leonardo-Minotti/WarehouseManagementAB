import random
from enum import Enum
from typing import Dict


class OrderColor(Enum):
    """Enum per rappresentare i 5 colori degli ordini"""
    ROSSO = "red"
    VERDE = "green"
    GIALLO = "yellow"
    BLU = "blue"
    ARANCIONE = "orange"


class Order:

    def __init__(self, capacita_totale: int):
        self._capacita_totale = capacita_totale
        self._capacita_per_colore = self._dividi_capacita_casualmente()

    def _dividi_capacita_casualmente(self) -> Dict[OrderColor, int]:
        colori = list(OrderColor)
        capacita_rimanente = self._capacita_totale
        divisione = {}

        # Assegna casualmente la capacità ai primi 4 colori
        for i in range(4):
            if capacita_rimanente > 1:
                # Assegna un valore casuale tra 0 e la capacità rimanente
                valore = random.randint(0, capacita_rimanente - (4 - i))
                divisione[colori[i]] = valore
                capacita_rimanente -= valore
            else:
                divisione[colori[i]] = 0

        # L'ultimo colore prende tutta la capacità rimanente
        divisione[colori[4]] = capacita_rimanente
        return divisione


    def get_capacita_totale(self) -> int:
        return self._capacita_totale

    def get_capacita_per_colore(self, colore: OrderColor) -> int:
        return self._capacita_per_colore.get(colore, 0)

    def get_tutte_capacita(self) -> Dict[OrderColor, int]:
        return self._capacita_per_colore.copy()

    #Set capacità per colore passando il colore e quantità nuova
    def set_capacita_per_colore(self, colore: OrderColor, nuova_capacita: int):
        if nuova_capacita < 0:
            raise ValueError("La capacità non può essere negativa")

        vecchia_capacita = self._capacita_per_colore.get(colore, 0)
        differenza = nuova_capacita - vecchia_capacita

        # Verifica che la modifica non renda la capacità totale negativa
        if self._capacita_totale + differenza < 0:
            raise ValueError("La modifica renderebbe la capacità totale negativa")
        self._capacita_per_colore[colore] = nuova_capacita
        self._capacita_totale += differenza

    def set_capacita_totale(self, nuova_capacita_totale: int):
        if nuova_capacita_totale < 0:
            raise ValueError("La capacità totale deve essere maggiore di 0")
        self._capacita_totale = nuova_capacita_totale

    # Print method
    def print_order(self):
        print(f"=== ORDINE ===")
        print(f"Capacità totale: {self._capacita_totale}")
        print(f"Divisione per colori:")

        for colore, capacita in self._capacita_per_colore.items():
            percentuale = (capacita / self._capacita_totale * 100) if self._capacita_totale > 0 else 0
            print(f"  {colore.value.capitalize()}: {capacita} ({percentuale:.1f}%)")

        # Verifica che la somma corrisponda alla capacità totale
        somma = sum(self._capacita_per_colore.values())
        print(f"Verifica somma: {somma} (dovrebbe essere {self._capacita_totale})")
        print("=" * 15)

    def __str__(self) -> str:
        return f"Order(capacità_totale={self._capacita_totale}, divisione={dict(self._capacita_per_colore)})"

    def __repr__(self) -> str:
        return self.__str__()


