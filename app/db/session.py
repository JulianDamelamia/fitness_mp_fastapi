# database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# cargamos las variables de entorno desde el archivo .env (si corremos localmente)
load_dotenv()


# 1. Definir la URL de la base de datos y crear el engine.
# Esto le indica a SQLAlchemy que cree un archivo llamado 'test.db'
# en la carpeta de tu proyecto.

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:

    # Lógica para Render (PostgreSQL)
    if DATABASE_URL.startswith("postgresql"):
        engine = create_engine(DATABASE_URL)

    # Lógica para Local (MySQL)
    elif DATABASE_URL.startswith("mysql://"):
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    raise ValueError(
        "DATABASE_URL no está definida. Asegúrate de tener un .env local o de que esté configurada en producción."
    )


# 3. Crear la clase SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Crear la clase Base
Base = declarative_base()


# Base de datos de usuarios ficticios. Compatibilidad con implementacion inicial de AUTH.
# TODO: Reemplazar por base de datos real.
fake_user_db = {}
