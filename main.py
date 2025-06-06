from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse

import pandas as pd
import joblib
import io
from pydantic import BaseModel
from typing import List

from sklearn.preprocessing import StandardScaler

app = FastAPI()

# Загрузка модели
try:
    model = joblib.load('fraud_model.joblib')
    scaler = joblib.load('scaler.joblib')
except Exception as e:
    raise RuntimeError(f"Failed to load model: {str(e)}")


# Список обязательных признаков
REQUIRED_FEATURES = [
    'Time', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9', 'V10',
    'V11', 'V12', 'V13', 'V14', 'V15', 'V16', 'V17', 'V18', 'V19', 'V20',
    'V21', 'V22', 'V23', 'V24', 'V25', 'V26', 'V27', 'V28', 'Amount'
]

class PredictionResult(BaseModel):
    id: int
    is_fraud: bool
    fraud_probability: float
    fraud_risk: str  # 'low', 'medium', 'high'

class BatchPredictionResponse(BaseModel):
    predictions: List[PredictionResult]

def validate_dataframe(df: pd.DataFrame) -> None:
    """Проверяет наличие всех необходимых признаков в DataFrame"""
    missing_features = [feat for feat in REQUIRED_FEATURES if feat not in df.columns]
    if missing_features:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required features: {', '.join(missing_features)}"
        )
    
def prepare(df: pd.DataFrame) -> pd.DataFrame:
    if 'id' not in df.columns:
        df = df.copy()
        df['id'] = range(1, len(df) + 1)

    ids = df['id']
    scaling_data = df.drop(columns=['id'], errors='ignore')

    try:
        scaled_data = scaler.transform(scaling_data)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка масштабирования данных: {str(e)}"
        )

    result = pd.DataFrame(scaled_data, columns=scaling_data.columns)
    result.insert(0, 'id', ids.values)
    return result


def calculate_risk_level(probability: float) -> str:
    """Определяет уровень риска на основе вероятности"""
    if probability < 0.3:
        return "low"
    elif 0.3 <= probability < 0.7:
        return "medium"
    else:
        return "high"
    
@app.get("/")
async def main():
    """Главная страница приложения"""
    with open("main.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

@app.post("/predict", response_model=BatchPredictionResponse)
async def predict_transactions(file: UploadFile = File(...)):

    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    try:
        contents = await file.read()
        data = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Проверка данных
        validate_dataframe(data)
        data = prepare(data)
        
        features = data[REQUIRED_FEATURES]

        probabilities = model.predict_proba(features)[:, 1]
        
        predictions = []
        for idx, prob in enumerate(probabilities):
            predictions.append({
                "id": int(data['id'].iloc[idx]),
                "is_fraud": bool(prob > 0.5),  # Порог 0.5 для определения мошенничества
                "fraud_probability": float(prob),
                "fraud_risk": calculate_risk_level(prob)
            })

        return {"predictions": predictions}

    except HTTPException:
        raise
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="The CSV file is empty")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )

@app.get("/required-features")
async def get_required_features():
    """Возвращает список обязательных признаков"""
    return {
        "required_features": REQUIRED_FEATURES,
    }
