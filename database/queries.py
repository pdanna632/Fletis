import sqlite3
from database.connection import obtener_conexion

def registrar_camion(placa, modelo):
    """Inserta un nuevo camión en la base de datos en estado 'Libre'."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        cursor.execute(
            "INSERT INTO camiones (placa, modelo, estado, fecha_ingreso_taller) VALUES (?, ?, ?, NULL)",
            (placa.upper().strip(), modelo.strip(), 'Libre')
        )
        conexion.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # La placa ya existe
    finally:
        conexion.close()

def obtener_todos_los_camiones():
    """Retorna una lista de tuplas con todos los camiones registrados."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT placa, modelo, estado, fecha_ingreso_taller FROM camiones")
    camiones = cursor.fetchall()
    conexion.close()
    return camiones

def actualizar_estado_camion(placa, nuevo_estado, fecha_ingreso=None):
    """Actualiza el estado de un camión y su fecha de ingreso al taller."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE camiones SET estado = ?, fecha_ingreso_taller = ? WHERE placa = ?",
        (nuevo_estado, fecha_ingreso, placa)
    )
    conexion.commit()
    conexion.close()

def obtener_camion_por_placa(placa):
    """Busca un camión específico por su placa."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT placa, modelo, estado, fecha_ingreso_taller FROM camiones WHERE placa = ?", (placa,))
    camion = cursor.fetchone()
    conexion.close()
    return camion

def eliminar_camion_por_placa(placa):
    """Elimina permanentemente un camión de la base de datos SQLite."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM camiones WHERE placa = ?", (placa,))
    conexion.commit()
    conexion.close()