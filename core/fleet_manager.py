from datetime import datetime
import database.queries as queries
import storage.pickle_manager as pickle_manager

def registrar_nuevo_camion(placa, modelo):
    """Valida los datos e intenta registrar un camión."""
    if not placa or not modelo:
        return False, "La placa y el modelo no pueden estar vacíos."
    
    exito = queries.registrar_camion(placa, modelo)
    if exito:
        return True, f"Camión {placa.upper()} registrado exitosamente."
    else:
        return False, f"El camión con placa {placa.upper()} ya existe."

def enviar_a_mantenimiento(placa):
    """Cambia el estado del camión a 'Mantenimiento' y registra el momento exacto de entrada."""
    camion = queries.obtener_camion_por_placa(placa)
    if not camion:
        return False, "El camión no existe."
    
    if camion[2] == "Mantenimiento":
        return False, "El camión ya se encuentra en mantenimiento."
    
    # Registramos la fecha y hora actual en formato ISO texto (YYYY-MM-DD HH:MM:SS)
    fecha_actual_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    queries.actualizar_estado_camion(placa, "Mantenimiento", fecha_actual_str)
    return True, f"Camión {placa} ingresado a taller el {fecha_actual_str}."

def liberar_de_mantenimiento(placa):
    """
    Saca al camión del taller, calcula los días transcurridos y los 
    acumula de forma persistente en el mes correspondiente dentro del Pickle.
    """
    camion = queries.obtener_camion_por_placa(placa)
    if not camion or camion[2] != "Mantenimiento":
        return False, "El camión no está en mantenimiento o no existe."
    
    fecha_ingreso_str = camion[3]
    fecha_actual = datetime.now()
    
    try:
        fecha_ingreso = datetime.strptime(fecha_ingreso_str, "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        # Resguardo en caso de que el string de la fecha esté corrupto
        fecha_ingreso = fecha_actual
        
    # Calcular la diferencia de tiempo
    diferencia = fecha_actual - fecha_ingreso
    
    # Convertimos los segundos totales a días flotantes (Ej: 12 horas = 0.5 días)
    # Si quieres que el mínimo sea 1 día, podrías aplicar math.ceil(), pero con flotantes es más exacto
    dias_transcurridos = diferencia.total_seconds() / 86400.0
    
    # Evitamos números negativos por desajustes de reloj del sistema
    if dias_transcurridos < 0:
        dias_transcurridos = 0.0

    # Obtener el mes actual para la acumulación en el Pickle (Formato: YYYY-MM)
    mes_actual = fecha_actual.strftime("%Y-%m")
    
    # 1. Guardar y acumular los días en el archivo binario Pickle
    pickle_manager.acumular_dias_mantenimiento(mes_actual, placa, dias_transcurridos)
    
    # 2. Actualizar el estado en la base de datos SQL a 'Libre' y limpiar la fecha
    queries.actualizar_estado_camion(placa, "Libre", None)
    
    return True, f"Camión {placa} liberado. Pasó {round(dias_transcurridos, 2)} días en taller."

def obtener_metricas_dashboard():
    """
    Calcula de forma dinámica las estadísticas para la pantalla principal.
    Retorna: (total, libres, en_mantenimiento, lista_mantenimiento_con_dias)
    """
    todos = queries.obtener_todos_los_camiones()
    
    total = len(todos)
    libres = sum(1 for c in todos if c[2] == "Libre")
    en_mantenimiento = sum(1 for c in todos if c[2] == "Mantenimiento")
    
    # Lista específica para la tabla del taller
    lista_taller = []
    fecha_actual = datetime.now()
    
    for c in todos:
        if c[2] == "Mantenimiento":
            placa, modelo, _, fecha_ingreso_str = c
            try:
                fecha_ingreso = datetime.strptime(fecha_ingreso_str, "%Y-%m-%d %H:%M:%S")
                dias = (fecha_actual - fecha_ingreso).total_seconds() / 86400.0
            except (ValueError, TypeError):
                dias = 0.0
                
            lista_taller.append({
                "placa": placa,
                "modelo": modelo,
                "dias_actuales": round(max(0.0, dias), 2)
            })
            
    return {
        "total": total,
        "libres": libres,
        "mantenimiento": en_mantenimiento,
        "lista_taller": lista_taller
    }