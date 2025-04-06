from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from config import Config
import joblib

class ModeloHidrologico:
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
        try:
            X = df[self.features]
            y = df[self.target]

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=Config.TEST_SIZE,
                random_state=Config.RANDOM_STATE, stratify=y
            )

            self.model.fit(X_train, y_train)
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
        try:
            joblib.dump(self.model, Config.RESULTS_DIR / nombre)
            print(f"✅ Modelo guardado como: {nombre}")
        except Exception as e:
            print(f"🚨 Error al guardar modelo: {str(e)}")