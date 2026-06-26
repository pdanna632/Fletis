import os

# Obtiene la ruta del directorio actual donde está este archivo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ruta local donde se guardará la base de datos SQLite
DB_PATH = os.path.join(BASE_DIR, "database", "flota.db")

# Ruta local donde se guardará el archivo binario de Pickle
PICKLE_PATH = os.path.join(BASE_DIR, "storage", "historial_mantenimiento.pkl")