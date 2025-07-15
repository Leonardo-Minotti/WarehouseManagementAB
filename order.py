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
    """Classe che rappresenta un ordine con capacità divisa per colori"""

    def __init__(self, capacita_totale: int):
        """
        Costruttore della classe Order

        Args:
            capacita_totale (int): La capacità totale dell'ordine da dividere tra i colori
        """

        self._capacita_totale = capacita_totale
        self._capacita_per_colore = self._dividi_capacita_casualmente()

    def _dividi_capacita_casualmente(self) -> Dict[OrderColor, int]:
        """
        Divide la capacità totale in modo casuale tra i 5 colori

        Returns:
            Dict[OrderColor, int]: Dizionario con la capacità per ogni colore
        """
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

    # Getter methods
    def get_capacita_totale(self) -> int:
        """Restituisce la capacità totale dell'ordine"""
        return self._capacita_totale

    def get_capacita_per_colore(self, colore: OrderColor) -> int:
        """
        Restituisce la capacità per un colore specifico

        Args:
            colore (OrderColor): Il colore di cui si vuole conoscere la capacità

        Returns:
            int: La capacità assegnata al colore specificato
        """
        return self._capacita_per_colore.get(colore, 0)

    def get_tutte_capacita(self) -> Dict[OrderColor, int]:
        """Restituisce una copia del dizionario con tutte le capacità per colore"""
        return self._capacita_per_colore.copy()

    # Setter methods
    def set_capacita_per_colore(self, colore: OrderColor, nuova_capacita: int):
        """
        Imposta la capacità per un colore specifico

        Args:
            colore (OrderColor): Il colore da modificare
            nuova_capacita (int): La nuova capacità per il colore
        """
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
        """
        Imposta una nuova capacità totale e ridistribuisce casualmente tra i colori

        Args:
            nuova_capacita_totale (int): La nuova capacità totale
        """
        if nuova_capacita_totale < 0:
            raise ValueError("La capacità totale deve essere maggiore di 0")

        self._capacita_totale = nuova_capacita_totale

    # Print method
    def print_order(self):
        """Stampa le informazioni complete dell'ordine"""
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


