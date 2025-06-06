# fastapi-fraud-model
Simple FastAPI app to upload the credit card `.csv` dataset and predict fraud transactions.

## Использование

1. Склонируйте проект: `git clone https://github.com/OSerge/fastapi-fraud-model.git`
2. Перейдите в директорию проекта: `cd fastapi-fraud-model/`
3. Соберите docker-образ: `docker build -t fastapi-fraud-model .`
4. Запустите его: `docker run --rm -p 8000:8000 fastapi-fraud-model`
5. Перейдите на главную страницу `http://localhost:8000/` с краткими пояснениями по работе сервиса.
6. Для загрузки файла с тестовым датасетом (например, `test_100.csv`) используйте Swagger UI по адресу `http://localhost:8000/docs#/default/predict_transactions_predict_post`
7. Можно также загрузить файл из консоли: 
```
curl -X 'POST' \
  'http://127.0.0.1:8000/predict' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@test_100.csv;type=text/csv'
```
