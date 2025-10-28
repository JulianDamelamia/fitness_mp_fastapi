
fitness_mp_fastapi/
├── app/
│   ├── api/
│   │   ├── routes/                      # Capa 1: Puntos de Entrada HTTP (FastAPI)
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                  # Rutas de autenticación (login, register, me)
│   │   │   ├── plans.py                 # Rutas de PlanDeEntrenamiento
│   │   │   └── users.py                 # Rutas de Clientes y Entrenadores
│   │   └── dependencies.py              # Dependencias de inyección de FastAPI (ej: get_db)
│   
│   ├── core/
│   │   ├── config.py                    # Configuración central (SECRET_KEY, DB_URL, etc.)
│   │   └── security.py                  # Hashing de contraseñas y gestión de JWT
│
│   ├── db/                              # Configuración de persistencia (SQLAlchemy)
│   │   ├── __init__.py                  # Aquí se define la clase Base de SQLAlchemy
│   │   └── session.py                   # Función para obtener la sesión de la DB (get_db)
│
│   ├── models/                          # Capa 2: Modelos de Persistencia (SQLAlchemy ORM)
│   │   ├── __init__.py
│   │   ├── user.py                      # Clases: Usuario(Base), Cliente, Entrenador
│   │   └── fitness.py                   # Clases: PlanDeEntrenamiento, Rutina, Sesión, Serie, Ejercicio
│   
│   ├── schemas/                         # Pydantic Schemas (Input/Output/Validación)
│   │   └── user.py                      # Schemas de Usuario, Cliente, Entrenador, Token, etc.
│   
│   ├── services/                        # Capa 3: Lógica de Negocio + Acceso a Datos (¡Nueva Responsabilidad!)
│   │   ├── auth_service.py              # Lógica de login/registro (Incluye las consultas a la DB)
│   │   ├── plan_service.py              # Lógica de PublicarPlan, ComprarPlan (Incluye consultas a la DB)
│   │   └── routine_service.py           # Lógica de Rutinas
│
│   ├── strategies/                      # Implementación del Patrón Strategy
│   │   └── progression_strategy.py      # y sus implementaciones (Linear, Ondulante, etc.)
│
│   ├── factories/                       # Implementación del Patrón Factory
│   │   └── routine_factory.py
│
│   ├── interfaces/                      # Implementación de las Interfaces/Abstractas
│   │   ├── calculable.py                # Implementa MusculosCalculables, TiempoEstimable
│   │   └── observer.py                  # Implementa Observer y Sujeto
│
│   └── templates/                       # Archivos HTML (login.html, register.html)
│       └── ...
│
├── tests/
│   └── ...
├── main.py                              # Punto de entrada
└── .gitignore
