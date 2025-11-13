# database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# cargamos las variables de entorno desde el archivo .env (si corremos localmente)
load_dotenv()


# 1. Definir la URL de la base de datos.
# Esto le indica a SQLAlchemy que cree un archivo llamado 'test.db'
# en la carpeta de tu proyecto.

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:

    # Lógica para Render (PostgreSQL)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)

    # Lógica para Local (MySQL)
    # (Ya debería estar correcta en tu .env, pero esto es por si acaso)
    elif DATABASE_URL.startswith("mysql://"):
        DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)
else:
    raise ValueError(
        "DATABASE_URL no está definida. Asegúrate de tener un .env local o de que esté configurada en producción."
    )


# 2. Crear el engine de SQLAlchemy
# El argumento 'check_same_thread' es necesario solo para SQLite.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# 3. Crear la clase SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Crear la clase Base
Base = declarative_base()


# Base de datos de usuarios ficticios. Compatibilidad con implementacion inicial de AUTH.
# TODO: Reemplazar por base de datos real.
fake_user_db = {}
