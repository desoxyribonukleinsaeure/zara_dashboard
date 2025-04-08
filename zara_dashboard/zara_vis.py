import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.title("ZARA Verkaufsdaten")

df = pd.read_csv("zara.csv", sep=';')

# Gesamt-Umsatz KPI
df['Revenue'] = df['Sales Volume'] * df['price']
total_revenue = df['Revenue'].sum()
st.metric("Gesamter Umsatz", f"{total_revenue:,.2f} $")

# Gesamt-Verkäufe KPI
total_sales_volume = df['Sales Volume'].sum()
st.metric("Gesamte Verkäufe", f"{total_sales_volume}")

# Verhältnis seasonal/not seasonal
seasonal_counts = df['Seasonal'].value_counts().reset_index()
seasonal_counts.columns = ['Seasonal', 'Count']

fig = px.pie(seasonal_counts,
             names='Seasonal',
             values='Count',
             title='Verteilung der Saisonalität',
             hole=0.3)

st.plotly_chart(fig)

# Auswirkung der Product Position auf Anzahl der Verkäufe
st.title("Aggregierte Sales Volume nach Product Position und Terms")

# 1. Aggregieren nach Product Position und terms und Summe des Sales Volume
aggregated_df = df.groupby(['terms', 'Product Position'])['Sales Volume'].sum().reset_index()
st.dataframe(aggregated_df)

# Erstelle eine neue Spalte 'aisle_volume_per_term'
# Finde den Sales Volume für 'aisle' für jede 'terms'-Gruppe
unique_positions = aggregated_df['Product Position'].nunique()
base_position = 'Aisle'
aisle_volume_per_term = aggregated_df[aggregated_df['Product Position'] == base_position].groupby('terms')['Sales Volume'].transform('first').reset_index(drop=True)
repeated_array = np.repeat(aisle_volume_per_term.values, unique_positions)

# Füge diese Werte als neue Spalte zum aggregierten DataFrame hinzu
aggregated_df['aisle_volume'] = repeated_array
aggregated_df['change_to_base'] = (aggregated_df['Sales Volume'] / aggregated_df['aisle_volume']) - 1
position_effect = aggregated_df.groupby(['Product Position'])['change_to_base'].mean().reset_index()
st.dataframe(position_effect)

# welche Produkt/gruppe am profitablesten / meist verkauft (bei granularität produkt vllt. top 3)