# database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Definir la URL de la base de datos.
# Esto le indica a SQLAlchemy que cree un archivo llamado 'test.db'
# en la carpeta de tu proyecto.
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# 2. Crear el engine de SQLAlchemy
# El argumento 'check_same_thread' es necesario solo para SQLite.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. Crear la clase SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Crear la clase Base
Base = declarative_base()


# Base de datos de usuarios ficticios. Compatibilidad con implementacion inicial de AUTH.
# TODO: Reemplazar por base de datos real.
fake_user_db = {}
