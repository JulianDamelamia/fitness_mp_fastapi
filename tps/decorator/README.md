# Ejercitacion para el uso  del patron `decorator`

El objetivo principal es extender funcionalidades de objetos de manera flexible, sin modificar su estructura original aplicando el patrón de diseño **Decorador**. 

## Decisiones de diseño

- **Propagación de `size`**:  
    El atributo `size` se propaga a través de los decoradores, asegurando que cada envoltorio pueda consultar el tamaño del objeto base. Esto se logra delegando la consulta de `size` al componente decorado.

- **Pruebas de totales**:  
    Para verificar el cálculo de totales (por ejemplo, precio o cantidad), se implementaron pruebas unitarias que instancian objetos base y les aplican diferentes decoradores. Se comparan los resultados esperados con los obtenidos, asegurando que la composición de decoradores funcione correctamente. Entre las pruebas se incluyen ejemplos donde se crean bebidas directamente o utilizando una funcion `make_beverage`.

## Estructura basica del proyecto

- **Componentes base**: `Beverages.py` Definen la interfaz común y la funcionalidad principal.
- **Decoradores**: `Condiments.py` Extienden o modifican el comportamiento de los componentes base, siguiendo la interfaz común.
- **Pruebas**: `test_1.py` Archivos de test que validan el correcto funcionamiento de la propagación de atributos y el cálculo de precios.
- **Funciones auxiliares**: `make_beverage.py` Funciones para facilitar la creación de objetos con decoradores aplicados.
- **Impresion de objetos**: `prettyPrintDecorator.py` Decorador para modificar como se imprimen los objetos por consola.
