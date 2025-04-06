import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import folium
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path
import joblib
import warnings
from matplotlib.ticker import FuncFormatter

# ================= CONFIGURACIÓN =================
class Config:
    BASE_DIR = Path(__file__).resolve().parent
    RAW_DATA = Path(r"C:\Users\LENOVO\Desktop\PHYTON\AGUA.csv")
    RESULTS_DIR = BASE_DIR / "results"
    os.makedirs(RESULTS_DIR, exist_ok=True)
    CAUDAL_ALERTA = 100  # Umbral para alertas (L/s)
    TEST_SIZE = 0.3  # Porcentaje para test
    RANDOM_STATE = 42  # Semilla aleatoria
    COLOR_ALTO = '#e41a1c'  # Rojo para caudal alto
    COLOR_BAJO = '#377eb8'  # Azul para caudal bajo

# ================= FUNCIONES DE DATOS =================
def cargar_datos():
    """Carga y valida el archivo de datos"""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df = pd.read_csv(
                Config.RAW_DATA,
                encoding='latin1',
                usecols=["DEPARTAMENTO", "PROVINCIA", "DISTRITO", "COORESTE", "COORNORTE", "CAUDAL", "VOLUMEN", "FECHAINICIO"],
                dtype={'DEPARTAMENTO': 'category', 'PROVINCIA': 'category', 'DISTRITO': 'category'}
            )
        return df
    except Exception as e:
        print(f"🚨 Error al cargar datos: {str(e)}")
        return None

def limpiar_datos(df):
    """Limpia y prepara los datos para análisis"""
    if df is None or df.empty:
        return None
    
    # Conversión numérica
    num_cols = ["COORESTE", "COORNORTE", "CAUDAL", "VOLUMEN"]
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors='coerce')
    df = df.dropna(subset=num_cols)
    
    # Procesamiento de fechas
    df['FECHAINICIO'] = pd.to_datetime(df['FECHAINICIO'], errors='coerce')
    df = df.dropna(subset=['FECHAINICIO'])
    
    # Variables derivadas
    df['MES'] = df['FECHAINICIO'].dt.month
    df['DIA_AÑO'] = df['FECHAINICIO'].dt.dayofyear
    
    # Clasificación de riesgo
    df['RIESGO'] = pd.cut(df['CAUDAL'],
                         bins=[0, 50, 100, 200, float('inf')],
                         labels=["Bajo", "Moderado", "Alto", "Muy Alto"])
    df['ALERTA'] = (df['CAUDAL'] > Config.CAUDAL_ALERTA).astype(int)
    
    return df

# ================= VISUALIZACIONES =================
def crear_mapa(df):
    """Genera mapa interactivo con marcadores mejorados"""
    if df is None or df.empty:
        print("⚠️ No hay datos para el mapa")
        return None
    
    # Configuración base del mapa
    mapa = folium.Map(
        location=[df["COORNORTE"].mean(), df["COORESTE"].mean()],
        zoom_start=6,
        tiles='cartodbpositron'
    )
    
    # Muestra representativa (corrección del error)
    sample_size = min(1000, len(df))  # Toma el mínimo entre 1000 y el tamaño del dataset
    df_sample = df.sample(n=sample_size, replace=False) if len(df) > 1000 else df
    
    # Capa de marcadores
    for _, row in df_sample.iterrows():
        folium.CircleMarker(
            location=[row["COORNORTE"], row["COORESTE"]],
            radius=4 + np.log1p(row["CAUDAL"]),  # Escala logarítmica mejorada
            color=Config.COLOR_ALTO if row["CAUDAL"] > Config.CAUDAL_ALERTA else Config.COLOR_BAJO,
            fill=True,
            fill_opacity=0.7,
            popup=f"""
                <b>Ubicación:</b> {row['DEPARTAMENTO']}<br>
                <b>Caudal:</b> {row['CAUDAL']:,.1f} L/s<br>
                <b>Riesgo:</b> {row['RIESGO']}
            """,
            tooltip="Click para detalles"
        ).add_to(mapa)
    
    # Leyenda interactiva
    legend_html = f"""
    <div style="position: fixed; bottom: 20px; left: 20px; width: 160px;
                padding: 8px; background: white; border-radius: 5px;
                box-shadow: 0 0 5px rgba(0,0,0,0.2); z-index: 1000;
                font-family: Arial; font-size: 12px;">
        <div style="font-weight: bold; margin-bottom: 5px;">LEYENDA</div>
        <div style="display: flex; align-items: center; margin: 3px 0;">
            <div style="background: {Config.COLOR_ALTO}; width: 12px; height: 12px;
                        border-radius: 50%; margin-right: 5px;"></div>
            <span>Alerta (> {Config.CAUDAL_ALERTA} L/s)</span>
        </div>
        <div style="display: flex; align-items: center; margin: 3px 0;">
            <div style="background: {Config.COLOR_BAJO}; width: 12px; height: 12px;
                        border-radius: 50%; margin-right: 5px;"></div>
            <span>Normal (≤ {Config.CAUDAL_ALERTA} L/s)</span>
        </div>
    </div>
    """
    mapa.get_root().html.add_child(folium.Element(legend_html))
    
    mapa.save(str(Config.RESULTS_DIR / "mapa_interactivo.html"))
    print("Mapa interactivo guardado correctamente")
    return mapa

def generar_graficos(df):
    """Genera 3 gráficos integrados con estilo profesional"""
    if df is None or df.empty:
        print("⚠️ No hay datos para graficar")
        return
    
    # Configuración de estilo
    sns.set_style("whitegrid")
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.alpha'] = 0.2
    plt.rcParams['font.size'] = 10
    
    # Crear figura con 3 subplots
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(20, 6))
    fig.suptitle('Análisis de Datos Hidrológicos', y=1.05, fontsize=14, fontweight='bold')
    
    # --- GRÁFICO 1: Histograma de caudal ---
    sns.histplot(df["CAUDAL"], bins=30, kde=True, color='#1a6fdf', edgecolor='white', ax=ax1)
    
    # Percentiles destacados
    percentiles = [25, 50, 75, 95]
    colores = ['#2ca02c', '#ff7f0e', '#d62728', '#9467bd']
    for p, color in zip(percentiles, colores):
        valor = np.percentile(df["CAUDAL"], p)
        ax1.axvline(valor, color=color, linestyle='--', linewidth=1.5)
        ax1.text(valor, ax1.get_ylim()[1]*0.85, 
                f'P{p}: {valor:,.0f} L/s',
                ha='center', va='top', fontsize=9,
                bbox=dict(facecolor='white', alpha=0.8, edgecolor=color))
    
    ax1.set_title('Distribución de Caudal', pad=12)
    ax1.set_xlabel('Caudal (L/s)')
    ax1.set_ylabel('Frecuencia')
    ax1.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:,.0f}'))
    
    # --- GRÁFICO 2: Boxplot por categorías ---
    orden = ["Bajo", "Moderado", "Alto", "Muy Alto"]
    colores = ["#2ca02c", "#ff7f0e", "#d62728", "#9467bd"]
    
    sns.boxplot(data=df, y="RIESGO", x="CAUDAL", order=orden, palette=colores, 
               width=0.6, linewidth=1, ax=ax2)
    
    # Medianas
    medianas = df.groupby("RIESGO")["CAUDAL"].median()
    for i, cat in enumerate(orden):
        ax2.text(medianas[cat], i, f' {medianas[cat]:,.0f} L/s', 
                va='center', ha='left', fontsize=9,
                bbox=dict(facecolor='white', alpha=0.8))
    
    ax2.set_title('Distribución por Categoría de Riesgo', pad=12)
    ax2.set_xlabel('Caudal (L/s)')
    ax2.set_ylabel('')
    ax2.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:,.0f}'))
    
    # --- GRÁFICO 3: Tendencia temporal ---
    df_fechas = df.set_index('FECHAINICIO').resample('M').size().reset_index(name='registros')
    df_fechas['media_movil'] = df_fechas['registros'].rolling(7, center=True).mean()
    
    sns.lineplot(data=df_fechas, x='FECHAINICIO', y='registros', 
                label='Registros mensuales', color='#2ca02c', linewidth=1.5, ax=ax3)
    sns.lineplot(data=df_fechas, x='FECHAINICIO', y='media_movil', 
                label='Media móvil (7 meses)', color='#d62728', linewidth=2.5, ax=ax3)
    
    ax3.set_title('Tendencia Temporal de Registros', pad=12)
    ax3.set_xlabel('Fecha')
    ax3.set_ylabel('Número de Registros')
    ax3.legend(loc='upper left')
    
    # Formato de fechas
    ax3.xaxis.set_major_locator(plt.MaxNLocator(8))
    fig.autofmt_xdate(rotation=45, ha='center')
    
 
    plt.tight_layout()
    plt.savefig(str(Config.RESULTS_DIR / 'graficos_profesionales.png'), 
               dpi=300, bbox_inches='tight')
    print("Gráficos profesionales guardados correctamente")
    plt.show()

# ================= MODELO PREDICTIVO =================
class ModeloHidrologico:
    """Clase para el modelo predictivo de alertas"""
    
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=150,
            max_depth=12,
            random_state=Config.RANDOM_STATE,
            class_weight='balanced',
            n_jobs=-1
        )
        self.features = ['COORNORTE', 'COORESTE', 'VOLUMEN', 'MES', 'DIA_AÑO']
        self.target = 'ALERTA'
    
    def entrenar(self, df):
        """Entrena el modelo con los datos"""
        try:
            X = df[self.features]
            y = df[self.target]
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y,
                test_size=Config.TEST_SIZE,
                random_state=Config.RANDOM_STATE,
                stratify=y
            )
            
            self.model.fit(X_train, y_train)
            
            # Evaluación
            y_pred = self.model.predict(X_test)
            report = classification_report(y_test, y_pred, output_dict=True)
            
            print("\n📊 Resultados del Modelo:")
            print(f"- Exactitud: {report['accuracy']:.2%}")
            print(f"- Precisión (Alerta): {report['1']['precision']:.2%}")
            print(f"- Sensibilidad (Alerta): {report['1']['recall']:.2%}")
            
            return report
        
        except Exception as e:
            print(f"🚨 Error en entrenamiento: {str(e)}")
            return None
    
    def guardar_modelo(self, nombre="modelo_hidrologico.pkl"):
        """Guarda el modelo entrenado en disco"""
        try:
            joblib.dump(self.model, Config.RESULTS_DIR / nombre)
            print(f"✅ Modelo guardado como: {nombre}")
        except Exception as e:
            print(f"🚨 Error al guardar modelo: {str(e)}")

# ================= EJECUCIÓN PRINCIPAL =================
def ejecutar_analisis():
    """Función principal que coordina todo el análisis"""
    
    print("\n" + "="*60)
    print(" SISTEMA DE ANÁLISIS HIDROLÓGICO AVANZADO ".center(60, '#'))
    print("="*60 + "\n")
    
    # 1. Carga y limpieza de datos
    print("[1/4] 📂 Cargando y procesando datos...")
    datos = limpiar_datos(cargar_datos())
    if datos is None:
        return
    
    # 2. Visualización de datos
    print("\n[2/4] 📊 Generando visualizaciones mejoradas...")
    crear_mapa(datos)
    generar_graficos(datos)
    
    # 3. Modelado predictivo
    print("\n[3/4] 🤖 Entrenando modelo predictivo...")
    modelo = ModeloHidrologico()
    metricas = modelo.entrenar(datos)
    
    if metricas:
        modelo.guardar_modelo()
    
    # 4. Resumen final
    print("\n" + "="*60)
    print(" ANÁLISIS COMPLETADO CON ÉXITO ".center(60, '#'))
    print("="*60)
    print(f"\n🎉 Resultados guardados en: {Config.RESULTS_DIR}")
    print("- mapa_interactivo.html (Mapa interactivo mejorado)")
    print("- graficos_profesionales.png (3 gráficos integrados)")
    print("- modelo_hidrologico.pkl (Modelo entrenado)")

if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ejecutar_analisis()