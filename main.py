from datos import cargar_datos, limpiar_datos
from visualizaciones import crear_mapa, generar_graficos
from modelo import ModeloHidrologico

def ejecutar_analisis():
    print("="*60)
    print(" SISTEMA DE ANÁLISIS HIDROLÓGICO AVANZADO ".center(60, '#'))
    print("="*60)

    print("[1/4] 📂 Cargando y procesando datos...")
    datos = limpiar_datos(cargar_datos())
    if datos is None:
        return

    print("[2/4] 🗺️ Generando mapa interactivo...")
    crear_mapa(datos)

    print("[3/4] 📈 Generando gráficos profesionales...")
    generar_graficos(datos)

    print("[4/4] 🧠 Entrenando modelo predictivo...")
    modelo = ModeloHidrologico()
    modelo.entrenar(datos)
    modelo.guardar_modelo()

if __name__ == "__main__":
    ejecutar_analisis()