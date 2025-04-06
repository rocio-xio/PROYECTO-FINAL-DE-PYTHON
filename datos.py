import pandas as pd
import warnings
from config import Config

def cargar_datos():
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
    if df is None or df.empty:
        return None

    num_cols = ["COORESTE", "COORNORTE", "CAUDAL", "VOLUMEN"]
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors='coerce')
    df = df.dropna(subset=num_cols)

    df['FECHAINICIO'] = pd.to_datetime(df['FECHAINICIO'], errors='coerce')
    df = df.dropna(subset=['FECHAINICIO'])

    df['MES'] = df['FECHAINICIO'].dt.month
    df['DIA_AÑO'] = df['FECHAINICIO'].dt.dayofyear

    df['RIESGO'] = pd.cut(df['CAUDAL'],
                         bins=[0, 50, 100, 200, float('inf')],
                         labels=["Bajo", "Moderado", "Alto", "Muy Alto"])
    df['ALERTA'] = (df['CAUDAL'] > Config.CAUDAL_ALERTA).astype(int)

    return df