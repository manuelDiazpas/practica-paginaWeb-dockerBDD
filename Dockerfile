# Imagen base de Python
FROM python:3.11-slim

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código y la carpeta templates
COPY . .

# Exponer el puerto de Flask
EXPOSE 5000

# Ejecutar la aplicación
CMD ["python", "app.py"]