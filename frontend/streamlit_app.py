import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Fraud Detection")

st.title("🚨 Мошеннические транзакции")

API_URL = "http://backend:8000/predict"

uploaded_file = st.file_uploader("📁 Загрузите CSV-файл", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.write("📄 Предварительный просмотр данных:")
        st.dataframe(df.head())

        if st.button("🔍 Проверить на мошенничество"):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
            response = requests.post(API_URL, files=files)

            if response.status_code == 200:
                result = response.json()
                st.success("✅ Предсказание получено!")
                st.dataframe(pd.DataFrame(result["predictions"]))
            else:
                st.error(f"❌ Ошибка сервера: {response.status_code}")
                st.text(response.text)
    except Exception as e:
        st.error(f"Ошибка обработки: {e}")
else:
    st.info("Пожалуйста, загрузите CSV-файл.")
