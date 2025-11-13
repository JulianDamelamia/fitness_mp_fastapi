# Version de python.  "-slim" para una imagen más ligera
FROM python:3.10

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de requerimientos
COPY requirements.txt .

# Instala las dependencias
# --no-cache-dir para mantener la imagen ligera
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el resto de los archivos al contenedor
COPY . .

# Expone el puerto en el que correrá uvicorn (FastAPI)
EXPOSE 8000

# Comando para correr la aplicación
# OBSERVACION: --host 0.0.0.0 es OBLIGATORIO para que sea accesible desde fuera del contenedor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]