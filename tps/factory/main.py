import os

print(os.getcwd())
from simple_factory.store import PizzaStore
from simple_factory.simple_factory import SimplePizzaFactory
from abstract_factory.store import NYPizzaStore, ChicagoPizzaStore


def main():
    # store = PizzaStore(SimplePizzaFactory())
    ny = NYPizzaStore()
    chi = ChicagoPizzaStore()
    for store in [ny, chi]:
        for kind in ["cheese", "veggie", "pepperoni"]:
            p = store.order_pizza(kind)
            print(f"Ordered -> {p}")
            print("-." * 20)


if __name__ == "__main__":
    main()
