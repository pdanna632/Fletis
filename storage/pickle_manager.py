import pickle
import os
from config import PICKLE_PATH

def cargar_historial():
    """Carga el historial del archivo pickle. Si no existe, retorna un diccionario vacío."""
    if not os.path.exists(PICKLE_PATH):
        # Asegura que la carpeta 'storage' exista
        os.makedirs(os.path.dirname(PICKLE_PATH), exist_ok=True)
        return {}
    
    try:
        with open(PICKLE_PATH, "rb") as archivo:
            return pickle.load(archivo)
    except (pickle.PickleError, EOFError):
        return {}  # Retorna vacío si el archivo está corrupto o vacío

def guardar_historial(historial):
    """Guarda el diccionario de historial en el archivo binario pickle."""
    with open(PICKLE_PATH, "wb") as archivo:
        pickle.dump(historial, archivo)

def acumular_dias_mantenimiento(mes, placa, dias):
    """
    Suma los días de mantenimiento a un camión específico en un mes dado.
    Estructura del diccionario: { "YYYY-MM": { "PLACA1": dias, "PLACA2": dias } }
    """
    historial = cargar_historial()
    
    # Si el mes no existe en el registro, lo inicializamos
    if mes not in historial:
        historial[mes] = {}
        
    # Si la placa no tiene registro en ese mes, inicia en 0.0
    if placa not in historial[mes]:
        historial[mes][placa] = 0.0
        
    # Acumulamos el tiempo transcurrido
    historial[mes][placa] += round(dias, 2)
    
    # Guardamos físicamente en el disco local
    guardar_historial(historial)
    
def obtener_resumen_historico():
    """Retorna un consolidado de días acumulados por placa sumando todos los meses."""
    historial = cargar_historial()
    consolidado = {}
    
    for mes in historial:
        for placa, dias in historial[mes].items():
            consolidado[placa] = consolidado.get(placa, 0.0) + dias
            
    return consolidado