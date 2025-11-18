# main.py
# Script principal para probar el patrón Decorator.

from beverages import Espresso, DarkRoast, HouseBlend
from condiments import Mocha, Whip, Soy, Caramel, Milk
from builder import build_beverage
from prettyPrintDecorator import PrettyPrintDecorator


def main():
    """
    Función principal que simula la preparación de cafés en Starbuzz.
    """
    print("Bienvenido a Starbuzz Coffee!")
    print("--- Preparando pedidos ---")

    # Pedido 1: Un Espresso simple, sin condimentos.
    beverage1 = Espresso()
    beverage1 = PrettyPrintDecorator(beverage1)
    print(f"Pedido 1: {beverage1.get_description()} ${beverage1.cost():.2f}")

    # Pedido 2: Un DarkRoast con doble Mocha y Crema.
    beverage2 = DarkRoast()
    beverage2 = Mocha(beverage2)  # Envolvemos con el primer Mocha
    beverage2 = Mocha(beverage2)  # Envolvemos con el segundo Mocha
    beverage2 = Whip(beverage2)  # Envolvemos con Crema
    beverage2 = PrettyPrintDecorator(beverage2)  # Aplicamos el decorador pretty print
    print(f"Pedido 2: {beverage2.get_description()} ${beverage2.cost():.2f}")

    # Pedido 3: Un HouseBlend con Soja, Mocha y Crema.
    beverage3 = HouseBlend()
    beverage3 = Soy(beverage3)
    beverage3 = Mocha(beverage3)
    beverage3 = Whip(beverage3)
    beverage3 = PrettyPrintDecorator(beverage3)
    print(f"Pedido 3: {beverage3.get_description()} ${beverage3.cost():.2f}")

    # Pedido 4: Un Espresso con triple Caramelo.
    beverage4 = Espresso()
    beverage4 = Caramel(beverage4)
    beverage4 = Caramel(beverage4)
    beverage4 = Caramel(beverage4)
    beverage4 = Caramel(beverage4)
    beverage4 = PrettyPrintDecorator(beverage4)
    print(f"Pedido 4: {beverage4.get_description()} ${beverage4.cost():.2f}")

    # Pedido 5: Un Decaf Grande con leche y soja
    beverage5 = DarkRoast()
    beverage5.set_size("Grande")
    beverage5 = Milk(beverage5)
    beverage5 = Soy(beverage5)
    beverage5 = PrettyPrintDecorator(beverage5)
    print(f"Pedido 5: {beverage5.get_description()} ${beverage5.cost():.2f}")

    # Pedido 6: Un HouseBLend Venti con soja
    beverage6 = HouseBlend()
    beverage6.set_size("Venti")
    beverage6 = Soy(beverage6)
    beverage6 = PrettyPrintDecorator(beverage6)
    print(f"Pedido 6: {beverage6.get_description()} ${beverage6.cost():.2f}")

    # Pedido 7: Usando el builder para un HouseBlend Venti con Soja, Mocha y Crema
    beverage7 = build_beverage("HouseBlend", "Venti", ["Soy", "Mocha", "Whip"])
    beverage7 = PrettyPrintDecorator(beverage7)
    print(f"Pedido 7: {beverage7.get_description()} ${beverage7.cost():.2f}")

    beverage8 = build_beverage("DarkRoast", "Tall", ["Mocha", "Mocha", "Whip"])
    beverage8 = PrettyPrintDecorator(beverage8)
    print(f"Pedido 8: {beverage8.get_description()} ${beverage8.cost():.2f}")


if __name__ == "__main__":
    main()
