import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.title("DYNAMIC KANO EVOLUTION")

# ----------------------------------------------------------
# LOAD KANO DATA
# ----------------------------------------------------------
@st.cache_data
def load_kano():
    df = pd.read_csv("kano_dynamic.csv")
    df["year"] = df["month"].str[:4].astype(int)
    return df

df_raw = load_kano()
ATTRS = df_raw["attribute"].unique().tolist()

CATEGORY_ORDER = ["Reverse", "Indifferent", "Attractive", "One-Dimensional", "Must-Be"]
CAT_MAP = {cat: i for i, cat in enumerate(CATEGORY_ORDER)}

# ----------------------------------------------------------
# SIDEBAR FILTER
# ----------------------------------------------------------
st.sidebar.header("Filter Kano Evolution")

year_min, year_max = df_raw["year"].min(), df_raw["year"].max()
year_range = st.sidebar.slider("Year range", int(year_min), int(year_max), (2015, int(year_max)))

selected_attrs = st.sidebar.multiselect(
    "Select attributes to analyze",
    ATTRS,
    default=["taste", "service", "hygiene"]
)

# filter data
df = df_raw[(df_raw["year"] >= year_range[0]) & (df_raw["year"] <= year_range[1])].copy()
df["cat_num"] = df["category"].map(CAT_MAP)

# ----------------------------------------------------------
# 1) STEP CHART FOR CATEGORY MOVEMENT
# ----------------------------------------------------------
st.subheader("Category Evolution (Step Chart)")

fig = go.Figure()

for a in selected_attrs:
    sub = df[df["attribute"] == a]
    fig.add_trace(go.Scatter(
        x=sub["month"],
        y=sub["cat_num"],
        mode="lines",
        line_shape="hv",
        name=a,
        hovertemplate="Month=%{x}<br>Category=%{y}"
    ))

fig.update_layout(
    height=450,
    yaxis=dict(
        tickmode="array",
        tickvals=list(CAT_MAP.values()),
        ticktext=list(CAT_MAP.keys()),
        title="Kano Category"
    ),
    xaxis_title="Month",
    title="Step-wise Evolution of Kano Categories",
    margin=dict(l=10, r=10, t=30, b=10)
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("""
### Cara Baca Step Chart
- Garis **naik** → kategori menjadi lebih penting (Indifferent → Attractive → O-dim → Must-Be)  
- Garis **turun** → kategori menurun (Attractive → Indifferent)  
- Garis **datar** → kategori stabil  
""")

# ----------------------------------------------------------
# 2) STACKED CATEGORY COMPOSITION CHART
# ----------------------------------------------------------
st.subheader("Overall Category Composition Over Time")

composition = df.groupby(["month", "category"]).size().reset_index(name="count")

fig2 = px.area(
    composition,
    x="month",
    y="count",
    color="category",
    category_orders={"category": CATEGORY_ORDER},
    title="Category Composition Over Time (All Attributes Combined)"
)

fig2.update_layout(height=450, margin=dict(l=10, r=10, t=30, b=10))
st.plotly_chart(fig2, use_container_width=True)

st.markdown("""
### Insight dari Stacked Chart
- Melihat apakah industri **bergerak ke arah lebih Attractive**  
- Atau malah makin **Indifferent** di periode tertentu  
- Memberikan gambaran keseluruhan customer perception shift  
""")

# ----------------------------------------------------------
# 3) ATTRIBUTE VOLATILITY (FREQUENCY OF CATEGORY SWITCHING)
# ----------------------------------------------------------
st.subheader("Attribute Category Switching Frequency")

switch_data = []
for a in ATTRS:
    sub = df[df["attribute"] == a].copy()
    sub["prev"] = sub["cat_num"].shift(1)
    switches = (sub["cat_num"] != sub["prev"]).sum()
    switch_data.append([a, switches])

switch_df = pd.DataFrame(switch_data, columns=["attribute", "switch_count"])
switch_df = switch_df.sort_values("switch_count", ascending=False)

fig3 = px.bar(
    switch_df,
    x="attribute",
    y="switch_count",
    color="switch_count",
    color_continuous_scale="Viridis",
    title="How Often Does Each Attribute Change Category?"
)

fig3.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=10))
st.plotly_chart(fig3, use_container_width=True)

# ----------------------------------------------------------
# 4) PREMIUM CONCLUSION CARD (SMART INSIGHT)
# ----------------------------------------------------------
st.subheader("Summary Insight (Automated)")

most_dynamic = switch_df.iloc[0]
most_stable = switch_df.iloc[-1]

# detect category shifts from first -> last
shift_notes = []
for a in ATTRS:
    sub = df[df["attribute"] == a].copy()
    first_cat = sub["category"].iloc[0]
    last_cat = sub["category"].iloc[-1]
    if first_cat != last_cat:
        shift_notes.append(f"- **{a.title()}**: {first_cat} → **{last_cat}**")

shift_text = (
    "<br>".join(shift_notes)
    if len(shift_notes) > 0
    else "No significant transitions — categories mostly stable."
)

# dynamic color logic
if most_dynamic["switch_count"] >= 8:
    card_color = "#e74c3c"   # red = very volatile
elif most_dynamic["switch_count"] >= 4:
    card_color = "#f39c12"   # orange = moderate
else:
    card_color = "#2ecc71"   # green = stable

# render card
st.markdown(f"""
<div style="
    padding:18px;
    background-color:#f8f9fa;
    border-left:6px solid {card_color};
    border-radius:10px;
    font-size:16px;
">
<b>Most Dynamic Attribute:</b> {most_dynamic['attribute'].title()}  
→ {most_dynamic['switch_count']} category changes  

<b>Most Stable Attribute:</b> {most_stable['attribute'].title()}  
→ {most_stable['switch_count']} changes  

<b>Key Transitions:</b><br>
{shift_text}<br><br>

<b>Interpretation:</b><br>
High-volatility attributes indicate changing customer expectations or inconsistent service delivery.<br>
Stable attributes show consistent customer perception — customers know what to expect.
</div>
""", unsafe_allow_html=True)
