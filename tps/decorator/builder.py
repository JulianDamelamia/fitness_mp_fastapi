from beverages import *
from condiments import *


def build_beverage(base: str, size: str, condiments: list):

    bases = {
        "Espresso": Espresso,
        "DarkRoast": DarkRoast,
        "HouseBlend": HouseBlend,
        "Decaf": Decaf,
    }
    conds = {"Milk": Milk, "Mocha": Mocha, "Soy": Soy, "Whip": Whip, "Caramel": Caramel}

    if base not in bases:
        raise ValueError(f"Bebida base desconocida: {base}")

    # Crear la bebida base
    beverage = bases[base]()
    beverage.set_size(size)
    # Agregar condimentos
    for cond in condiments:
        if cond not in conds:
            raise ValueError(f"Condimento desconocido: {cond}")
        beverage = conds[cond](beverage)
    return beverage
