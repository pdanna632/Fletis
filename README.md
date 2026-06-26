# TrackFlota 🚛

**TrackFlota** es una aplicación de escritorio local diseñada para la gestión eficiente de camiones y el control riguroso de sus ciclos de mantenimiento. El sistema permite monitorear en tiempo real el estado de los vehículos (Libres vs. En Mantenimiento), calcular automáticamente los días acumulados en taller y visualizar el rendimiento de la flota mediante analítica dinámica.

## 🚀 Características Clave

* **Gestión de Flota (CRUD):** Registro, consulta y actualización de camiones mediante una base de datos relacional local.
* **Monitoreo en Tiempo Real (Dashboard):** Indicadores clave (KPIs) en la pantalla principal que muestran el total de camiones libres, en taller y una tabla detallada con los días transcurridos de los vehículos actualmente en mantenimiento.
* **Persistencia Híbrida Inteligente:** * **SQLite:** Maneja los estados actuales y datos transaccionales de los camiones.
    * **Pickle (Python):** Almacena y acumula un histórico mensual de días en taller de forma binaria, garantizando cero pérdida de datos al cerrar la aplicación.
* **Módulo de Gráficas Dinámicas:** Renderizado automático de un gráfico de barras (vía Matplotlib) que compara los días acumulados en mantenimiento por vehículo en el mes en curso.

---

## 📂 Estructura del Proyecto

El software está diseñado bajo una arquitectura limpia en capas para facilitar su mantenimiento y escalabilidad:

```text
trackflota/
│
├── main.py                 # Punto de entrada de la aplicación
├── config.py               # Configuraciones globales y rutas de archivos
│
├── database/               # Capa de Datos (SQLite)
│   ├── connection.py       # Inicialización y conexión de la BD
│   └── queries.py          # Consultas CRUD y cambios de estado
│
├── storage/                # Capa de Persistencia Histórica (Pickle)
│   └── pickle_manager.py   # Manipulación del histórico acumulado mensual
│
├── core/                   # Capa de Lógica de Negocio (Controladores)
│   └── fleet_manager.py    # Orquestador de reglas de negocio y cálculo de tiempos
│
└── gui/                    # Capa Visual (Interfaz Gráfica)
    ├── main_window.py      # Ventana principal, dashboard y gráficos
    └── components.py       # Tablas, formularios y modales
