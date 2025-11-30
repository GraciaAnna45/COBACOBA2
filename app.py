import streamlit as st

st.set_page_config(
    page_title="Dynamic Kano Model – Dessert & Cafe",
    layout="wide"
)

st.title("🍰☕ Dynamic Time-Aware Kano (DTA-Kano) Dashboard")
st.markdown("""
Dashboard ini dibangun dari Yelp Review (Dessert & Cafe) 2015–2021 dan terdiri dari beberapa halaman:

1. **Overview** – Tren rating, sentiment, dan intensitas mention atribut.
2. **Dynamic Kano Timeline & Heatmap** – Pergerakan kategori Kano (Attractive, Must-Be, dll) dari waktu ke waktu.
3. **Attribute Impact (β⁺ / β⁻)** – Seberapa besar pengaruh tiap atribut ke rating.
4. **Seasonality & Forecasting** – Pola bulanan dan prediksi tren ke depan.

Silakan pilih halaman di sidebar (menu **Pages**).
""")
