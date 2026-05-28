import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page config 
st.set_page_config(
 page_title="Light = Life | Global Electricity Access",
 page_icon="",
 layout="wide",
 initial_sidebar_state="expanded",
)

# Region mapping 
REGION_MAP = {
 "Sub-Saharan Africa": [
 "Angola","Benin","Botswana","Burkina Faso","Burundi","Cameroon",
 "Central African Republic","Chad","Comoros","Congo","Djibouti",
 "Equatorial Guinea","Eritrea","Eswatini","Ethiopia","Gabon","Gambia",
 "Ghana","Guinea","Guinea-Bissau","Kenya","Lesotho","Liberia",
 "Madagascar","Malawi","Mali","Mauritania","Mauritius","Mozambique",
 "Namibia","Niger","Nigeria","Rwanda","Sao Tome and Principe","Senegal",
 "Seychelles","Sierra Leone","Somalia","South Africa","South Sudan",
 "Sudan","Tanzania","Togo","Uganda","Zambia","Zimbabwe","Nauru",
 "Kiribati","Tuvalu",
 ],
 "North Africa & Middle East": [
 "Algeria","Bahrain","Egypt","Iraq","Israel","Jordan","Kuwait",
 "Lebanon","Libya","Malta","Morocco","Oman","Qatar","Saudi Arabia",
 "Tunisia","Turkey","United Arab Emirates","Yemen",
 ],
 "South Asia": [
 "Afghanistan","Bangladesh","Bhutan","India","Maldives","Myanmar",
 "Nepal","Pakistan","Sri Lanka",
 ],
 "East Asia & Pacific": [
 "Australia","Cambodia","China","Fiji","Indonesia","Japan","Kiribati",
 "Malaysia","Mongolia","Myanmar","Nauru","New Caledonia","New Zealand",
 "Papua New Guinea","Philippines","Samoa","Singapore","Solomon Islands",
 "South Korea","Thailand","Tonga","Tuvalu","Vanuatu",
 ],
 "Europe & Central Asia": [
 "Albania","Armenia","Austria","Azerbaijan","Belarus","Belgium",
 "Bosnia and Herzegovina","Bulgaria","Croatia","Cyprus","Czechia",
 "Denmark","Estonia","Finland","France","Georgia","Germany","Greece",
 "Hungary","Iceland","Ireland","Italy","Kazakhstan","Kyrgyzstan",
 "Latvia","Lithuania","Luxembourg","Montenegro","Netherlands",
 "North Macedonia","Norway","Poland","Portugal","Romania","Russia",
 "Serbia","Slovakia","Slovenia","Spain","Sweden","Switzerland",
 "Tajikistan","Turkmenistan","Ukraine","United Kingdom","Uzbekistan",
 "Aruba","Bermuda","Cayman Islands","Puerto Rico",
 ],
 "Latin America & Caribbean": [
 "Antigua and Barbuda","Argentina","Bahamas","Barbados","Belize",
 "Bolivia","Brazil","Chile","Colombia","Costa Rica","Cuba","Dominica",
 "Dominican Republic","Ecuador","El Salvador","French Guiana",
 "Grenada","Guatemala","Guyana","Haiti","Honduras","Jamaica","Mexico",
 "Nicaragua","Panama","Paraguay","Peru","Saint Kitts and Nevis",
 "Saint Lucia","Saint Vincent and the Grenadines","Suriname",
 "Trinidad and Tobago","Uruguay","Venezuela",
 ],
 "North America": [
 "Canada","United States",
 ],
}

def assign_region(entity):
 for region, countries in REGION_MAP.items():
 if entity in countries:
 return region
 return "Other"

# Colour palette (accessible, no red-green) 
REGION_COLOURS = {
 "Sub-Saharan Africa": "#E07B39", # warm orange
 "North Africa & Middle East":"#C9AB82", # sand
 "South Asia": "#5B8DB8", # steel blue
 "East Asia & Pacific": "#2E7D8C", # teal
 "Europe & Central Asia": "#6A4C93", # purple
 "Latin America & Caribbean":"#3D8B5E", # forest green
 "North America": "#B5446E", # rose
 "Other": "#AAAAAA",
}

# Load & clean data 
@st.cache_data
def load_data():
 df = pd.read_csv("global-data-on-sustainable-energy.csv")
 df.columns = df.columns.str.strip()
 # Rename long columns for convenience
 df = df.rename(columns={
 "Access to electricity (% of population)": "elec_access",
 "Access to clean fuels for cooking": "clean_cooking",
 "Renewable energy share in the total final energy consumption (%)": "renew_share",
 "Electricity from fossil fuels (TWh)": "fossil_twh",
 "Electricity from renewables (TWh)": "renew_twh",
 "Low-carbon electricity (% electricity)": "low_carbon_pct",
 "Value_co2_emissions_kt_by_country": "co2_kt",
 "gdp_per_capita": "gdp_pc",
 "gdp_growth": "gdp_growth",
 "Primary energy consumption per capita (kWh/person)": "energy_pc",
 "Financial flows to developing countries (US $)": "fin_flows",
 "Renewable-electricity-generating-capacity-per-capita": "renew_cap_pc",
 "Entity": "country",
 "Year": "year",
 })
 df["year"] = pd.to_numeric(df["year"], errors="coerce")
 df["region"] = df["country"].apply(assign_region)

 num_cols = ["elec_access","clean_cooking","renew_share","fossil_twh",
 "renew_twh","low_carbon_pct","co2_kt","gdp_pc",
 "gdp_growth","energy_pc","fin_flows","renew_cap_pc"]
 for c in num_cols:
 if c in df.columns:
 df[c] = pd.to_numeric(df[c], errors="coerce")

 return df

df = load_data()

# Sidebar 
with st.sidebar:
 st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Sustainable_Development_Goal_07.png/200px-Sustainable_Development_Goal_07.png", width=80)
 st.title(" Light = Life")
 st.caption("Global Electricity Access · 2000 – 2020")
 st.markdown("---")

 all_regions = sorted([r for r in df["region"].unique() if r != "Other"])
 sel_regions = st.multiselect("Filter by Region", all_regions, default=all_regions)

 year_range = st.slider("Year Range", 2000, 2020, (2000, 2020))

 st.markdown("---")
 st.markdown(
 "**Dataset:** Global Data on Sustainable Energy \n"
 "**Source:** Our World in Data / World Bank \n"
 "**Countries:** 176 · **Years:** 2000–2020"
 )

# Filter data 
mask = (
 df["region"].isin(sel_regions) &
 df["year"].between(year_range[0], year_range[1])
)
dff = df[mask].copy()

# Header 
st.markdown(
 "<h1 style='color:#2E7D8C;margin-bottom:0'> Light = Life</h1>"
 "<p style='font-size:1.1rem;color:#555;margin-top:4px'>"
 "The global electricity access gap — who's still in the dark, what drives progress, "
 "and what it means for human development.</p>",
 unsafe_allow_html=True,
)
st.markdown("---")

# KPI row 
col1, col2, col3, col4 = st.columns(4)

latest = df[df["year"] == 2020]
earliest = df[df["year"] == 2000]

avg_2020 = latest["elec_access"].mean()
avg_2000 = earliest["elec_access"].mean()
still_low = (latest["elec_access"] < 50).sum()
top_mover_gain = (
 latest.set_index("country")["elec_access"] -
 earliest.set_index("country")["elec_access"]
).dropna().max()

col1.metric("Global Avg Access (2020)", f"{avg_2020:.1f}%", f"+{avg_2020-avg_2000:.1f}pp since 2000")
col2.metric("Countries Below 50% (2020)", int(still_low), delta=None)
col3.metric("Biggest Single-Country Gain", f"+{top_mover_gain:.1f}pp", delta=None)
col4.metric("Years of Data", f"2000 – 2020", delta=None)

st.markdown("---")

# 
# CHART 1 — Choropleth World Map
# 
st.subheader(" Chart 1: The Global Picture — Electricity Access by Country")
st.caption("Use the year slider to trace progress country by country from 2000 to 2020.")

map_year = st.slider("Select Year (Map)", 2000, 2020, 2020, key="map_yr")
map_df = df[df["year"] == map_year]

fig_map = px.choropleth(
 map_df,
 locations="country",
 locationmode="country names",
 color="elec_access",
 color_continuous_scale=[
 [0.0, "#1A1A2E"], # near-black (no access)
 [0.25, "#C1440E"], # deep terracotta
 [0.55, "#E8A838"], # amber
 [0.80, "#C9E8A0"], # light green
 [1.0, "#2E7D8C"], # teal (full access)
 ],
 range_color=[0, 100],
 labels={"elec_access": "Access (%)"},
 title=f"Electricity Access — {map_year}",
 hover_name="country",
 hover_data={"elec_access": ":.1f", "year": False},
)
fig_map.update_layout(
 height=440,
 margin=dict(l=0, r=0, t=40, b=0),
 coloraxis_colorbar=dict(title="Access %", ticksuffix="%"),
 paper_bgcolor="#FAFAFA",
 geo=dict(showframe=False, showcoastlines=True, coastlinecolor="#CCCCCC",
 bgcolor="#FAFAFA"),
)
st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")

# 
# CHART 2 — Still in the Dark: countries below 50% in 2020
# 
st.subheader(" Chart 2: Still in the Dark — Countries Below 50% Electricity Access (2020)")
st.caption(
 "Each bar shows a country's access in 2020. Colour encodes the gain since 2000 — "
 "darker bars made the most progress; paler bars remain nearly static."
)

dark_df = latest[latest["elec_access"] < 50].copy()
gains = (
 latest.set_index("country")["elec_access"] -
 earliest.set_index("country")["elec_access"]
).rename("gain_since_2000").reset_index()
dark_df = dark_df.merge(gains, on="country", how="left")
dark_df = dark_df.sort_values("elec_access")

fig_dark = px.bar(
 dark_df,
 x="elec_access",
 y="country",
 orientation="h",
 color="gain_since_2000",
 color_continuous_scale=["#C9AB82", "#2E7D8C"],
 labels={"elec_access": "Access (%)", "country": "", "gain_since_2000": "Gain since 2000 (pp)"},
 title="Countries Below 50% Electricity Access in 2020",
 hover_data={"gain_since_2000": ":.1f", "elec_access": ":.1f"},
)
fig_dark.add_vline(x=50, line_dash="dot", line_color="#C1440E",
 annotation_text="50% threshold", annotation_position="top right")
fig_dark.update_layout(
 height=max(380, len(dark_df) * 22),
 paper_bgcolor="#FAFAFA", plot_bgcolor="#FAFAFA",
 margin=dict(l=10, r=20, t=40, b=40),
 coloraxis_colorbar=dict(title="Gain (pp)"),
 xaxis=dict(range=[0, 55], ticksuffix="%"),
)
fig_dark.update_traces(marker_line_width=0)
st.plotly_chart(fig_dark, use_container_width=True)

st.markdown("---")

# 
# CHART 3 — Progress Race: biggest improvers
# 
st.subheader(" Chart 3: The Progress Race — Biggest Gains in Electricity Access (2000–2020)")
st.caption("Countries ranked by total percentage-point improvement. Colour encodes world region.")

c2000 = df[df["year"] == 2000][["country","elec_access","region"]].rename(columns={"elec_access":"acc_2000"})
c2020 = df[df["year"] == 2020][["country","elec_access"]].rename(columns={"elec_access":"acc_2020"})
race_df = c2000.merge(c2020, on="country").dropna(subset=["acc_2000","acc_2020"])
race_df["gain"] = race_df["acc_2020"] - race_df["acc_2000"]
race_df = race_df.sort_values("gain", ascending=False).head(25)

fig_race = go.Figure()
for region in race_df["region"].unique():
 sub = race_df[race_df["region"] == region]
 color = REGION_COLOURS.get(region, "#AAAAAA")
 fig_race.add_trace(go.Bar(
 y=sub["country"], x=sub["gain"], orientation="h",
 name=region, marker_color=color,
 customdata=np.stack([sub["acc_2000"], sub["acc_2020"]], axis=-1),
 hovertemplate="<b>%{y}</b><br>Gain: +%{x:.1f}pp<br>2000: %{customdata[0]:.1f}%<br>2020: %{customdata[1]:.1f}%<extra></extra>",
 ))

fig_race.update_layout(
 title="Top 25 Countries by Electricity Access Gain (2000→2020)",
 height=600, barmode="stack",
 paper_bgcolor="#FAFAFA", plot_bgcolor="#FAFAFA",
 yaxis=dict(categoryorder="total ascending", tickfont=dict(size=11)),
 xaxis=dict(title="Percentage-Point Gain", ticksuffix="pp"),
 legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
 margin=dict(l=10, r=20, t=60, b=40),
)
st.plotly_chart(fig_race, use_container_width=True)

st.markdown("---")

# 
# CHART 4 — Electricity Access vs GDP per Capita
# 
st.subheader(" Chart 4: Wealth and Light — Does GDP Drive Electricity Access?")
st.caption(
 "Each bubble is a country in the selected year. X-axis is GDP/capita (log scale), "
 "Y-axis is electricity access. Bubble size reflects primary energy consumption per capita. "
 "Colour encodes region."
)

scatter_yr = st.slider("Select Year (Scatter)", 2000, 2020, 2020, key="scatter_yr")
sc_df = dff[dff["year"] == scatter_yr].dropna(subset=["gdp_pc","elec_access","energy_pc"])

fig_scatter = px.scatter(
 sc_df,
 x="gdp_pc", y="elec_access",
 size="energy_pc", size_max=40,
 color="region",
 color_discrete_map=REGION_COLOURS,
 log_x=True,
 hover_name="country",
 labels={
 "gdp_pc": "GDP per Capita (USD, log scale)",
 "elec_access": "Electricity Access (%)",
 "energy_pc": "Primary Energy / Capita (kWh)",
 "region": "Region",
 },
 title=f"Electricity Access vs GDP per Capita — {scatter_yr}",
 hover_data={"gdp_pc": ":,.0f", "elec_access": ":.1f", "energy_pc": ":.0f"},
)
fig_scatter.update_layout(
 height=480, paper_bgcolor="#FAFAFA", plot_bgcolor="#FAFAFA",
 xaxis=dict(showgrid=True, gridcolor="#E5E5E5"),
 yaxis=dict(showgrid=True, gridcolor="#E5E5E5", ticksuffix="%"),
 margin=dict(l=10, r=20, t=40, b=40),
 legend=dict(orientation="v", x=1.01),
)
fig_scatter.update_traces(marker=dict(opacity=0.75, line=dict(width=0.5, color="white")))
st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# 
# CHART 5 — Clean Cooking Connection
# 
st.subheader(" Chart 5: The Human Connection — Electricity Access vs Clean Cooking Fuels")
st.caption(
 "Electricity access and clean cooking fuel access are tightly linked. "
 "Countries unable to provide one rarely provide the other — a double burden on the poorest households."
)

cc_df = dff[dff["year"] == 2020].dropna(subset=["elec_access","clean_cooking"])

fig_cc = px.scatter(
 cc_df,
 x="elec_access", y="clean_cooking",
 color="region",
 color_discrete_map=REGION_COLOURS,
 hover_name="country",
 trendline="ols",
 trendline_scope="overall",
 trendline_color_override="#555555",
 labels={
 "elec_access": "Electricity Access (%)",
 "clean_cooking": "Clean Cooking Fuel Access (%)",
 "region": "Region",
 },
 title="Electricity Access vs Clean Cooking Fuel Access (2020)",
)
fig_cc.update_layout(
 height=460, paper_bgcolor="#FAFAFA", plot_bgcolor="#FAFAFA",
 xaxis=dict(showgrid=True, gridcolor="#E5E5E5", ticksuffix="%"),
 yaxis=dict(showgrid=True, gridcolor="#E5E5E5", ticksuffix="%"),
 margin=dict(l=10, r=20, t=40, b=40),
 legend=dict(orientation="v", x=1.01),
)
fig_cc.update_traces(
 selector=dict(mode="markers"),
 marker=dict(opacity=0.75, size=8, line=dict(width=0.5, color="white"))
)
st.plotly_chart(fig_cc, use_container_width=True)

st.markdown("---")

# 
# CHART 6 — Regional Trend Lines
# 
st.subheader(" Chart 6: Regional Trends — Which Regions Are Catching Up Fastest?")
st.caption(
 "Average electricity access by world region from 2000 to 2020. "
 "Sub-Saharan Africa shows the steepest rise — but still lags far behind."
)

region_trend = (
 dff.groupby(["year","region"])["elec_access"]
 .mean().reset_index()
)

fig_trend = px.line(
 region_trend,
 x="year", y="elec_access",
 color="region",
 color_discrete_map=REGION_COLOURS,
 markers=True,
 labels={
 "year": "Year",
 "elec_access":"Avg Electricity Access (%)",
 "region": "Region",
 },
 title="Average Electricity Access by Region (2000–2020)",
)
fig_trend.update_layout(
 height=420, paper_bgcolor="#FAFAFA", plot_bgcolor="#FAFAFA",
 xaxis=dict(showgrid=True, gridcolor="#E5E5E5", dtick=2),
 yaxis=dict(showgrid=True, gridcolor="#E5E5E5", ticksuffix="%", range=[0,102]),
 legend=dict(orientation="v", x=1.01),
 margin=dict(l=10, r=20, t=40, b=40),
)
fig_trend.update_traces(marker=dict(size=5), line=dict(width=2.5))
st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")

# 
# CHART 7 — Country Spotlight
# 
st.subheader(" Chart 7: Country Spotlight — Trace Any Country's Journey")
st.caption("Select one or more countries to compare their electricity access trajectory over 21 years.")

all_countries = sorted(df["country"].unique())
default_picks = ["Ethiopia","Bangladesh","India","Nigeria","Haiti","Bolivia"]
spotlight_countries = st.multiselect(
 "Choose countries to compare:",
 all_countries,
 default=[c for c in default_picks if c in all_countries],
)

if spotlight_countries:
 spot_df = df[df["country"].isin(spotlight_countries)]
 color_seq = list(REGION_COLOURS.values())[:len(spotlight_countries)]

 fig_spot = px.line(
 spot_df, x="year", y="elec_access",
 color="country",
 markers=True,
 labels={"year":"Year","elec_access":"Electricity Access (%)","country":"Country"},
 title="Electricity Access Over Time — Selected Countries",
 color_discrete_sequence=color_seq,
 )
 fig_spot.update_layout(
 height=420, paper_bgcolor="#FAFAFA", plot_bgcolor="#FAFAFA",
 xaxis=dict(showgrid=True, gridcolor="#E5E5E5", dtick=2),
 yaxis=dict(showgrid=True, gridcolor="#E5E5E5", ticksuffix="%", range=[0,102]),
 legend=dict(orientation="v", x=1.01),
 margin=dict(l=10, r=20, t=40, b=40),
 )
 fig_spot.update_traces(marker=dict(size=5), line=dict(width=2.5))
 st.plotly_chart(fig_spot, use_container_width=True)
else:
 st.info("Select at least one country above to display the chart.")

st.markdown("---")

# Footer 
st.caption(
 "Data: Global Data on Sustainable Energy (Our World in Data / World Bank) · "
 "Built with Streamlit & Plotly · UC3DVS10 Data Visualisation · Ceazar Jay Mamburam"
)
