# fastapi-fraud-model
Simple FastAPI app to upload the credit card `.csv` dataset and predict fraud transactions.

## Использование

1. Склонируйте проект: `git clone https://github.com/OSerge/fastapi-fraud-model.git`
2. Перейдите в директорию проекта: `cd fastapi-fraud-model/`
3. Запуск docker-образов с их сборкой: `docker-compose up --build`. После корректной сборки можно запускать с помощью `docker-compose up -d`.
4. После этого будут доступны сервисы:
    * `http://localhost:8000/` - главная страница (FastAPI) с краткими пояснениями по работе сервиса.
    * `http://localhost:8501/` - Streamlit App для удобной загрузки файлов `.csv` с датасетами.
5. Можно также загрузить файл из консоли: 
```
curl -X 'POST' \
  'http://127.0.0.1:8000/predict' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@test_100.csv;type=text/csv'
```
