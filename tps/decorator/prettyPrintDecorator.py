from beverages import Beverage
from collections import Counter

class PrettyPrintDecorator(Beverage):
    def __init__(self, beverage: Beverage):
        self._beverage = beverage

    def get_description(self) -> str:
        desc = self._beverage.get_description()
        # Separar base y condimentos
        partes = desc.split(", ")
        base = partes[0]
        conds = partes[1:]
        # Contar repeticiones

        counts = Counter(conds)
        pretty_conds = []
        for cond, count in counts.items():
            if count == 1:
                pretty_conds.append(cond)
            elif count == 2:
                pretty_conds.append(f"Double {cond}")
            elif count == 3:
                pretty_conds.append(f"Triple {cond}")
            else:
                pretty_conds.append(f"{count}x {cond}")
        if pretty_conds:
            return base + ", " + ", ".join(pretty_conds)
        else:
            return base

    def cost(self) -> float:
        return self._beverage.cost()

    def set_size(self, size: str):
        self._beverage.set_size(size)

    def get_size(self) -> str:
        return self._beverage.get_size()