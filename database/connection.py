import sqlite3
import os
from config import DB_PATH

def obtener_conexion():
    """Establece y retorna una conexión a la base de datos SQLite."""
    # Asegura que la carpeta 'database' exista antes de crear el archivo .db
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def inicializar_base_datos():
    """Crea la tabla de camiones si no existe en el sistema."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    
    # Creamos la tabla camiones
    # fecha_ingreso_taller almacenará texto en formato ISO (YYYY-MM-DD HH:MM:SS) o NULL si está libre
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS camiones (
            placa TEXT PRIMARY KEY,
            modelo TEXT NOT NULL,
            estado TEXT NOT NULL CHECK(estado IN ('Libre', 'Mantenimiento')),
            fecha_ingreso_taller TEXT
        )
    """)
    
    conexion.commit()
    conexion.close()
    print("Base de datos inicializada correctamente.")