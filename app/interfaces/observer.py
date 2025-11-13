from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Any

class Observer(ABC):

    @abstractmethod
    def update(self, subject: Subject, event_data: Any) -> None:
        pass

class Subject(ABC):

    def __init__(self):
        # Lista privada de observadores
        self._observers: List[Observer] = []

    def registerObserver(self, observer: Observer) -> None:
        """
        Agrega un observador.
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def removeObserver(self, observer: Observer) -> None:
        """
        Quita un observador.
        """
        try:
            self._observers.remove(observer)
        except ValueError:
            pass # No pasa nada si el observer no estaba suscrito

    def notifyObservers(self, event_data: Any) -> None:
        """
        Notifica a todos los observadores.
        """
        # Notificamos a una copia de la lista por si un observer
        # intenta desuscribirse (detach) durante la notificación.
        for observer in self._observers[:]: 
            observer.update(self, event_data)