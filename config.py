from pathlib import Path
import os

class Config:
    BASE_DIR = Path(__file__).resolve().parent
    RAW_DATA = Path(r"C:\Users\LENOVO\Desktop\PHYTON\AGUA.csv")
    RESULTS_DIR = BASE_DIR / "results"
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    CAUDAL_ALERTA = 100
    TEST_SIZE = 0.3
    RANDOM_STATE = 42
    COLOR_ALTO = '#e41a1c'
    COLOR_BAJO = '#377eb8'