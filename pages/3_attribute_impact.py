import streamlit as st
import pandas as pd
import plotly.express as px

st.title("ATTRIBUTE IMPACT (β⁺ / β⁻)")

@st.cache_data
def load_kano():
    df = pd.read_excel("kano_dynamic.xlsx")
    df["year"] = df["month"].str[:4].astype(int)
    return df

kano = load_kano()
ATTRS = ["taste", "price", "service", "ambience", "hygiene", "staff"]

st.sidebar.header("Filter Impact")
year_min, year_max = int(kano["year"].min()), int(kano["year"].max())
year_range = st.sidebar.slider("Year range", year_min, year_max, (2015, year_max))

kano_filtered = kano[(kano["year"] >= year_range[0]) & (kano["year"] <= year_range[1])].copy()

st.subheader(f"Rata-rata β⁺ per atribut ({year_range[0]}–{year_range[1]})")

beta_mean = kano_filtered.groupby("attribute")[["beta_plus", "beta_minus"]].mean().reset_index()

fig_bar = px.bar(
    beta_mean,
    x="attribute",
    y="beta_plus",
    title="Rata-rata β⁺ (Positive Impact) per Atribut",
)
fig_bar.update_layout(xaxis_title="Attribute", yaxis_title="Mean β⁺", height=400)
st.plotly_chart(fig_bar, width="stretch")

st.subheader("Tren β⁺ per atribut")

attr_selected = st.multiselect(
    "Pilih atribut",
    ATTRS,
    default=ATTRS
)

kano_beta = kano_filtered[kano_filtered["attribute"].isin(attr_selected)].copy()

fig_beta_trend = px.line(
    kano_beta,
    x="month",
    y="beta_plus",
    color="attribute",
    markers=True,
    title="Tren β⁺ per Atribut"
)
fig_beta_trend.update_layout(xaxis_title="Month", yaxis_title="β⁺", height=400)
st.plotly_chart(fig_beta_trend, width="stretch")

st.markdown("""
**Interpretasi β⁺:**
- Semakin besar β⁺ → peningkatan atribut tersebut (sentiment positif) semakin kuat menaikkan rating.
- Atribut dengan β⁺ tertinggi → kandidat fitur yang bisa dijadikan *delighter* atau prioritas utama peningkatan kualitas.
""")

