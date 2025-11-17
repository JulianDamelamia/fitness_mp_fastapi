import pytest
from ..store import NYPizzaStore, ChicagoPizzaStore
from ..ingredients import NYPizzaIngredientFactory, ChicagoPizzaIngredientFactory

'''
* Que una pizza de queso de NY (`CheesePizza` creada por `NYPizzaStore`) contiene los ingredientes correctos de NY (ej: `Thin Crust Dough`).
* Que una pizza de almejas de Chicago (`ClamPizza` creada por `ChicagoPizzaStore`) contiene los ingredientes correctos de Chicago (ej: `Frozen Clams`).
'''
def test_NYPizzaStore_makes_NYStylePizza():
    '''Que `NYPizzaStore` efectivamente crea una pizza de tipo `NYStyle...`'''
    store = NYPizzaStore()
    assert isinstance(store.factory, NYPizzaIngredientFactory)

def test_ChicagoPizzaStore_makes_ChicagoStylePizza():
    '''Que `ChicagoPizzaStore` crea una pizza de tipo `ChicagoStyle...`'''
    store = ChicagoPizzaStore()
    assert isinstance(store.factory, ChicagoPizzaIngredientFactory)


# parametrizo esta prueba con pares de argumentos (ingrediente, valor_esperado). Me permite dejar los tests bien compactos y testear múltiples ingredientes a la vez
# podría haber hecho 
# assert condicion_a and condicion_b and condicion_c
# o es tres asserts uno abajo del otro pero así queda más canchero (y más escalable, también se alinea mejor con DRY)

# Observación(es): si quisiera testear otro tipo de pizza estilo NY tedría que cambiar no sólo el fixture
# sino también la parametrización de la función test. No estoy seguro de si esto es lo más conveniente.
# También los nombres de las funciones test podrían ser más generales pero como el caso es de juguete
# es irrelevante tal vez

@pytest.fixture
def ny_cheese_pizza():
    store = NYPizzaStore()
    return store.order_pizza("cheese")


@pytest.fixture
def chicago_clam_pizza():
    store = ChicagoPizzaStore()
    return store.order_pizza("clam")

@pytest.mark.parametrize(
    "ingredient, expected",
    [
        ("dough", "Thin Crust Dough"),
        ("sauce", "Marinara Sauce"),
        ("cheese", "Reggiano Cheese"),
    ],
)
def test_ny_store_cheese_pizza(ny_cheese_pizza, ingredient, expected):
    assert str(getattr(ny_cheese_pizza, ingredient)) == expected




@pytest.mark.parametrize(
    "ingredient, expected",
    [
        ("dough", "Thick Crust Dough"),
        ("sauce", "Plum Tomato Sauce"),
        ("clam", "Frozen Clams"),
    ],
)
def test_chicago_store_clam_pizza(chicago_clam_pizza, ingredient, expected):
    assert str(getattr(chicago_clam_pizza, ingredient)) == expected