import streamlit as st
import pandas as pd
import plotly.express as px

st.title("DATA OVERVIEW")

@st.cache_data
def load_monthly():
    df = pd.read_excel("monthly_attributes_weighted_filtered.xlsx")

    # Normalize column names
    df.columns = df.columns.str.lower()

    # Detect possible month/date column
    month_candidates = ["month", "date", "period", "timestamp"]
    found = False
    for c in month_candidates:
        if c in df.columns:
            df.rename(columns={c: "month"}, inplace=True)
            found = True
            break

    if not found:
        st.error("❌ ERROR: Column 'month/date' not found in CSV.")
        st.write("Columns found:", list(df.columns))
        st.stop()

    # Convert to datetime
    df["month"] = pd.to_datetime(df["month"], errors="coerce")

    # Extract year safely
    df["year"] = df["month"].dt.year

    return df


monthly = load_monthly()
ATTRS = ["taste", "price", "service", "ambience", "hygiene", "staff"]

st.sidebar.header("Filter Overview")
year_min, year_max = int(monthly["year"].min()), int(monthly["year"].max())
year_range = st.sidebar.slider("Year range", year_min, year_max, (2015, year_max))

monthly_filtered = monthly[(monthly["year"] >= year_range[0]) & (monthly["year"] <= year_range[1])].copy()

st.subheader(f"Average Rating {year_range[0]}–{year_range[1]}")

fig_rating = px.line(
    monthly_filtered,
    x="month",
    y="avg_rating",
    markers=True,
    title="Average Rating per Month"
)
fig_rating.update_layout(xaxis_title="Month", yaxis_title="Average Rating", height=350)
st.plotly_chart(fig_rating, width="stretch")

st.subheader("Weighted Sentiment per Attribute")

sentiment_cols = [f"{a}_weighted_sentiment" for a in ATTRS]
df_melt = monthly_filtered.melt(
    id_vars=["month"],
    value_vars=sentiment_cols,
    var_name="attribute",
    value_name="sentiment"
)
df_melt["attribute"] = df_melt["attribute"].str.replace("_weighted_sentiment", "")

attrs_selected = st.multiselect(
    "Pilih atribut yang ingin ditampilkan",
    ATTRS,
    default=ATTRS
)
df_melt = df_melt[df_melt["attribute"].isin(attrs_selected)]

fig_sent = px.line(
    df_melt,
    x="month",
    y="sentiment",
    color="attribute",
    markers=True,
    title="Weighted Sentiment per Attribute"
)
fig_sent.update_layout(xaxis_title="Month", yaxis_title="Weighted Sentiment", height=400)
st.plotly_chart(fig_sent, width="stretch")

st.subheader("Mention Volume per Attribute")

mention_melt = []
for a in ATTRS:
    temp = monthly_filtered[["month", f"{a}_mention"]].copy()
    temp["attribute"] = a
    temp = temp.rename(columns={f"{a}_mention": "mention"})
    mention_melt.append(temp)
mention_melt = pd.concat(mention_melt, ignore_index=True)

mention_melt = mention_melt[mention_melt["attribute"].isin(attrs_selected)]

fig_mention = px.line(
    mention_melt,
    x="month",
    y="mention",
    color="attribute",
    markers=True,
    title="Jumlah Mention per Attribute"
)
fig_mention.update_layout(xaxis_title="Month", yaxis_title="Total Mention", height=400)
st.plotly_chart(fig_mention, width="stretch")

st.markdown("> Halaman ini menjawab: **Apakah rating dan sentiment cenderung naik, turun, atau stagnan sepanjang tahun?**")

