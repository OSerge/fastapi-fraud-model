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
    # Если 'id' нет — создаём
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
    result.insert(0, 'id', ids.values)  # modifies result in place
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
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Проектный практикум</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f4f4f4;
        }
        h1 {
            color: #333;
        }
        p {
            color: #555;
        }
        pre {
            background-color: #f8f8f8;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }
        a {
            color: #007bff;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        code {
            background-color: #f8f8f8;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: monospace;
        }
    </style>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="API для предсказания мошеннических транзакций с использованием модели RandomForestClassifier.">
    <meta name="keywords" content="API, fraud detection, machine learning, RandomForest, FastAPI">
    <meta name="author" content="Serge Podkolzin ">
</head>
<body>
    <h1>Добро пожаловать!</h1>
    <p>Это API для предсказания мошеннических транзакций. За предсказания отвечает модель RandomForest.</p>
    <p> Используйте <a href="http://localhost:8000/docs">OpenAPI (Swagger UI)</a> для удобной загрузки файлов с датасетами.</p>
    <p>Используйте <code>/predict</code> для отправки CSV-файла с транзакциями.</p>
    <p>Пример запроса:</p>
    <pre>
curl -X POST "http://localhost:8000/predict" -F "file=@your_file.csv"</pre>
    <p>Пример ответа:</p>
    <pre>
{
    "predictions": [
        {
            "id": 1,
            "is_fraud": false,
            "fraud_probability": 0.01,
            "fraud_risk": "low"
        },
        {
            "id": 2,
            "is_fraud": true,
            "fraud_probability": 0.85,
            "fraud_risk": "high"
        }
    ]
}
    </pre>
    <p>Для получения списка обязательных признаков используйте <code>/required-features</code>.</p>
</body>
</html>
"""
    return HTMLResponse(content=html_content)

@app.post("/predict", response_model=BatchPredictionResponse)
async def predict_transactions(file: UploadFile = File(...)):

    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    try:
        # Чтение CSV
        contents = await file.read()
        data = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Проверка данных
        validate_dataframe(data)
        data = prepare(data)
        
        # Если нет колонки 'id', создаем ее
        # if 'id' not in data.columns:
        #     data['id'] = range(1, len(data)+1)

        # Выбираем только нужные признаки
        features = data[REQUIRED_FEATURES]
        
        # Предсказание
        probabilities = model.predict_proba(features)[:, 1]
        
        # Формирование результатов
        predictions = []
        for idx, prob in enumerate(probabilities):
            predictions.append({
                "id": int(data['id'].iloc[idx]),
                "is_fraud": bool(prob > 0.5),  # Порог можно настроить
                "fraud_probability": float(prob),
                "fraud_risk": calculate_risk_level(prob)
            })

        return {"predictions": predictions}

    except HTTPException:
        raise  # Перебрасываем уже обработанные ошибки
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