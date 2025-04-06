import folium
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from config import Config
from matplotlib.ticker import FuncFormatter

def crear_mapa(df):
    if df is None or df.empty:
        print("⚠️ No hay datos para el mapa")
        return None

    mapa = folium.Map(
        location=[df["COORNORTE"].mean(), df["COORESTE"].mean()],
        zoom_start=6,
        tiles='cartodbpositron'
    )

    sample_size = min(1000, len(df))
    df_sample = df.sample(n=sample_size, replace=False)

    for _, row in df_sample.iterrows():
        folium.CircleMarker(
            location=[row["COORNORTE"], row["COORESTE"]],
            radius=4 + np.log1p(row["CAUDAL"]),
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

    legend_html = f"""
    <div style="position: fixed; bottom: 20px; left: 20px; width: 160px;
                padding: 8px; background: white; border-radius: 5px;
                box-shadow: 0 0 5px rgba(0,0,0,0.2); z-index: 1000;
                font-family: Arial; font-size: 12px;">
        <div style="font-weight: bold; margin-bottom: 5px;">LEYENDA</div>
        <div><span style="background:{Config.COLOR_ALTO};display:inline-block;width:12px;height:12px;border-radius:50%;margin-right:5px;"></span>Alerta (> {Config.CAUDAL_ALERTA} L/s)</div>
        <div><span style="background:{Config.COLOR_BAJO};display:inline-block;width:12px;height:12px;border-radius:50%;margin-right:5px;"></span>Normal (≤ {Config.CAUDAL_ALERTA} L/s)</div>
    </div>
    """
    mapa.get_root().html.add_child(folium.Element(legend_html))
    mapa.save(str(Config.RESULTS_DIR / "mapa_interactivo.html"))
    print("✅ Mapa interactivo guardado correctamente")
    return mapa

def generar_graficos(df):
    if df is None or df.empty:
        print("⚠️ No hay datos para graficar")
        return

    sns.set_style("whitegrid")
    plt.rcParams['figure.facecolor'] = 'white'
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(20, 6))
    fig.suptitle('Análisis de Datos Hidrológicos', y=1.05)

    sns.histplot(df["CAUDAL"], bins=30, kde=True, color='#1a6fdf', ax=ax1)
    ax1.set_title('Distribución de Caudal')
    ax1.set_xlabel('Caudal (L/s)')
    ax1.set_ylabel('Frecuencia')

    orden = ["Bajo", "Moderado", "Alto", "Muy Alto"]
    colores = ["#2ca02c", "#ff7f0e", "#d62728", "#9467bd"]
    sns.boxplot(data=df, y="RIESGO", x="CAUDAL", order=orden, palette=colores, ax=ax2)
    ax2.set_title('Categoría de Riesgo')
    ax2.set_xlabel('Caudal (L/s)')
    ax2.set_ylabel('')

    df_fechas = df.set_index('FECHAINICIO').resample('M').size().reset_index(name='registros')
    df_fechas['media_movil'] = df_fechas['registros'].rolling(7, center=True).mean()
    sns.lineplot(data=df_fechas, x='FECHAINICIO', y='registros', label='Registros mensuales', ax=ax3)
    sns.lineplot(data=df_fechas, x='FECHAINICIO', y='media_movil', label='Media móvil', ax=ax3)
    ax3.set_title('Tendencia Temporal')
    ax3.set_xlabel('Fecha')
    ax3.set_ylabel('N° de Registros')

    plt.tight_layout()
    plt.savefig(str(Config.RESULTS_DIR / 'graficos_profesionales.png'), dpi=300)
    plt.show()