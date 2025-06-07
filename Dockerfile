FROM python:3.12-slim

RUN pip install --no-cache-dir \
    fastapi \
    pydantic \
    uvicorn \
    scikit-learn \
    pandas \
    joblib \
    python-multipart

WORKDIR /app

COPY *.py *.html *.joblib ./

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

