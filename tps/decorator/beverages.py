# beverages.py
# Contiene el Componente y los Componentes Concretos del patrón.

from abc import ABC, abstractmethod


# --- Componente Abstracto ---
class Beverage(ABC):
    """
    La clase base para todas las bebidas. Utiliza el módulo abc para
    definir que es una clase abstracta.
    """

    def __init__(self):
        self.description = "Bebida Desconocida"
        self.size = "Normal"

    def get_description(self) -> str:
        """
        Devuelve la descripción de la bebida.
        """
        return f"{self.description} {self.size}"

    @abstractmethod
    def cost(self) -> float:
        """
        Método abstracto que las subclases deben implementar para devolver
        el costo de la bebida.
        """
        pass

    def set_size(self, size: str):
        """
        Método para establecer el tamaño de la bebida.
        """
        if size not in ["Tall", "Grande", "Venti", "Normal"]:
            raise ValueError(
                "Tamaño inválido. Usar 'Tall', 'Grande', 'Venti' o 'Normal'."
            )

        self.size = size

    def get_size(self) -> str:
        """
        Método para obtener el tamaño de la bebida.
        """
        return self.size


# --- Componentes Concretos ---
class HouseBlend(Beverage):
    """
    Café de la casa, un tipo específico de bebida.
    """

    def __init__(self):
        self.size = "Normal"  # Tamaño por defecto
        self.description = "Café de la Casa"

    def cost(self) -> float:
        tamaño = self.get_size()
        if tamaño == "Normal":
            extra = 0.0
        elif tamaño == "Tall":
            extra = 0.10
        elif tamaño == "Grande":
            extra = 0.15
        else:
            extra = 0.20
        return 0.89 + extra


class DarkRoast(Beverage):
    """
    Café Dark Roast, un tipo específico de bebida.
    """

    def __init__(self):
        self.size = "Normal"  # Tamaño por defecto
        self.description = "Café Dark Roast"

    def cost(self) -> float:
        tamaño = self.get_size()
        if tamaño == "Normal":
            extra = 0.0
        elif tamaño == "Tall":
            extra = 0.10
        elif tamaño == "Grande":
            extra = 0.15
        else:
            extra = 0.20
        return 0.99 + extra


class Decaf(Beverage):
    """
    Café Descafeinado, un tipo específico de bebida.
    """

    def __init__(self):
        self.size = "Normal"  # Tamaño por defecto
        self.description = "Café Descafeinado"

    def cost(self) -> float:
        tamaño = self.get_size()
        if tamaño == "Normal":
            extra = 0.0
        elif tamaño == "Tall":
            extra = 0.10
        elif tamaño == "Grande":
            extra = 0.15
        else:
            extra = 0.20
        return 1.05 + extra


class Espresso(Beverage):
    """
    Café Espresso, un tipo específico de bebida.
    """

    def __init__(self):
        self.size = "Normal"
        self.description = "Espresso"

    def cost(self) -> float:
        tamaño = self.get_size()
        if tamaño == "Normal":
            extra = 0.0
        elif tamaño == "Tall":
            extra = 0.10
        elif tamaño == "Grande":
            extra = 0.15
        else:
            extra = 0.20
        return 1.99 + extra
