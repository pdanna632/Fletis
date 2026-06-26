import sys
import os

# Asegura que Python reconozca la raíz del proyecto para las importaciones
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import inicializar_base_datos
from gui.main_window import arrancar_aplicacion

if __name__ == "__main__":
    # 1. Creamos la base de datos y tablas locales si no existen
    inicializar_base_datos()
    
    # 2. Lanzamos la interfaz gráfica de usuario
    arrancar_aplicacion()