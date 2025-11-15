"""Módulo que implementa el patrón Observer para notificaciones."""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Any


class Observer(ABC):

    @abstractmethod
    def update(self, subject: Subject, event_data: Any) -> None:
        pass


class Subject(ABC):

    def __init__(self, delegator: Any = None):
        """
        Guarda una referencia al objeto 'dueño' (el User)
        para pasarlo en las notificaciones.
        """
        self._observers: List[Observer] = []
        # Si nos pasan un 'dueño', lo guardamos. Si no, somos nuestro propio dueño.
        self._delegator = delegator if delegator is not None else self

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
            pass  # No pasa nada si el observer no estaba suscrito

    def notifyObservers(self, event_data: Any) -> None:
        """
        Notifica a todos los observadores.
        """
        for observer in self._observers[:]:
            # --- INICIO DE MODIFICACIÓN 2 ---
            # Pasamos el 'dueño' (self._delegator, o sea el User)
            # en lugar de 'self' (el objeto Subject).
            observer.update(self._delegator, event_data)
