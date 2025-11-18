import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from beverages import *
from condiments import *
from builder import build_beverage
from prettyPrintDecorator import PrettyPrintDecorator


def test_espresso_simple():
    bebida = Espresso()
    assert bebida.cost() == 1.99
    assert "Espresso Normal" in bebida.get_description()


def test_double_mocha():
    bebida = build_beverage("Espresso", "Normal", ["Mocha", "Mocha"])
    assert bebida.cost() == 1.99 + 0.20 + 0.20
    assert (
        "Espresso Normal, Double Mocha"
        in PrettyPrintDecorator(bebida).get_description()
    )


def test_soya_venti():
    bebida = build_beverage("HouseBlend", "Venti", ["Soy"])
    assert bebida.cost() == 0.89 + 0.20 + 0.35
    assert (
        "Café de la Casa Venti, Soja" in PrettyPrintDecorator(bebida).get_description()
    )


def test_triple_crema():
    bebida = build_beverage("HouseBlend", "Grande", ["Soy", "Whip", "Whip", "Whip"])
    assert (
        "Café de la Casa Grande, Soja, Triple Crema"
        in PrettyPrintDecorator(bebida).get_description()
    )
    assert bebida.cost() == 0.89 + 0.15 + 0.30 + 0.10 + 0.10 + 0.10


def test_soya_y_crema():
    bebida = build_beverage("DarkRoast", "Normal", ["Soy", "Whip"])
    assert bebida.cost() == 0.99 + 0.15 + 0.10
    assert (
        "Café Dark Roast Normal, Soja, Crema"
        in PrettyPrintDecorator(bebida).get_description()
    )


def test_bebida_invalida():
    try:
        build_beverage("Latte", "Normal", [])
        assert False, "Deberia lanzar ValueError para bebida desconocida"
    except ValueError:
        pass


def test_tamaño_invalido():
    try:
        build_beverage("HouseBlend", "SuperDuperGrande", [])
        assert False, "Deberia lanzar ValueError para tamaño desconocido"
    except ValueError:
        pass
