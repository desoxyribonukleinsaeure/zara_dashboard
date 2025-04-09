import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.title("ZARA Verkaufsdaten")

df = pd.read_csv("zara.csv", sep=';')

# Gesamt-Umsatz KPI
df['Revenue'] = df['Sales Volume'] * df['price']
total_revenue = df['Revenue'].sum()

# Gesamt-Verkäufe KPI
total_sales_volume = df['Sales Volume'].sum()

# Effektivität von Promotionen
promo = df.groupby(['terms', 'Promotion'])['Sales Volume'].sum().reset_index()

promotion_impact = {}
for term in promo['terms'].unique():
    term_data = promo[promo['terms'] == term]
    sales_yes = term_data[term_data['Promotion'] == 'Yes']['Sales Volume'].values
    sales_no = term_data[term_data['Promotion'] == 'No']['Sales Volume'].values

    impact_ratio = (sales_yes[0] / sales_no[0]) - 1
    promotion_impact[term] = impact_ratio

promo_values = list(promotion_impact.values())
mean_promo_impact = np.mean(promo_values)

col1, col2, col3 = st.columns([1, 1, 0.5])
with col1:
    st.metric("Gesamter Umsatz", f"{total_revenue:,.2f} $")

with col2:
    st.metric("Gesamte Verkäufe", f"{total_sales_volume} Stück")

with col3:
    st.metric("Promo-Effekt:", f"{mean_promo_impact:.3f} %")

# Ist ein Produkt besonders populär / profitabel
st.subheader("Produkt Analyse")
products = df.groupby('name')[['Sales Volume', 'Revenue']].sum().reset_index()

most_sold_volume = products.loc[products['Sales Volume'].idxmax()]
most_sold_name = most_sold_volume['name']
least_sold_volume = products.loc[products['Sales Volume'].idxmin()]
least_sold_name = least_sold_volume['name']

most_profitable = products.loc[products['Revenue'].idxmax()]
most_profitable_name = most_profitable['name']
least_profitable = products.loc[products['Revenue'].idxmin()]
least_profitable_name = least_profitable['name']

sales_volume_range = (products['Sales Volume'].max()/products['Sales Volume'].sum()) - (products['Sales Volume'].min()/products['Sales Volume'].sum())
revenue_range = (products['Revenue'].max()/products['Revenue'].sum()) - (products['Revenue'].min()/products['Revenue'].sum())

sales_revenue = st.radio("Wähle anzuzeigene Größe aus:", ['Sales Volume', 'Revenue'])

col1_pop, col2_pop, col3_pop = st.columns([1, 1, 1])
if sales_revenue == 'Sales Volume':
    st.metric("Max verkauftes Item:", f"{most_sold_name}")
    st.metric("Min verkauftes Item:", f"{least_sold_name}")
    col1_pop, col2_pop, col3_pop = st.columns([1, 1, 1])
    with col1_pop:
        st.metric("Max Verkaufzahl:", f"{products['Sales Volume'].max()}")
    with col2_pop:
        st.metric("Min Verkaufzahl:", f"{products['Sales Volume'].min()}")
    with col3_pop:
        st.metric("Unterschied im Gesamtbeitrag:", f"{sales_volume_range:.3f} %")
if sales_revenue == 'Revenue':
    st.metric("Item mit max Umsatz:", f"{most_profitable_name}")
    st.metric("Item mit min Umsatz:", f"{least_profitable_name}")
    col1_pop, col2_pop, col3_pop = st.columns([1, 1, 1])
    with col1_pop:
        st.metric("Max Umsatz:", f"{products['Revenue'].max()}")
    with col2_pop:
        st.metric("Min Umsatz:", f"{products['Revenue'].min()}")
    with col3_pop:
        st.metric("Unterschied im Gesamtbeitrag:", f"{revenue_range:.3f} %")

# Verhältnis seasonal/not seasonal
st.subheader('Verteilung der Saisonalität')
seasonal_counts = df['Seasonal'].value_counts().reset_index()
seasonal_counts.columns = ['Seasonal', 'Count']

fig_seasonal = px.pie(seasonal_counts,
             names='Seasonal',
             values='Count',
             hole=0.5)

st.plotly_chart(fig_seasonal)

# Auswirkung der Product Position auf Anzahl der Verkäufe
st.title("Aggregierte Sales Volume nach Product Position und Terms")

aggregated_df = df.groupby(['terms', 'Product Position'])['Sales Volume'].sum().reset_index()

unique_positions = aggregated_df['Product Position'].nunique()
base_position = 'Aisle'
aisle_volume_per_term = aggregated_df[aggregated_df['Product Position'] == base_position].groupby('terms')['Sales Volume'].transform('first').reset_index(drop=True)
repeated_array = np.repeat(aisle_volume_per_term.values, unique_positions)

aggregated_df['aisle_volume'] = repeated_array
aggregated_df['change_to_base'] = (aggregated_df['Sales Volume'] / aggregated_df['aisle_volume']) - 1
position_effect = aggregated_df.groupby(['Product Position'])['change_to_base'].mean().reset_index()

fig_position = px.bar(position_effect,
             y='Product Position',  # Swap x and y
             x='change_to_base',  # Swap x and y
             labels={'Product Position': 'Product Position', 'change_to_base': 'Change to Base'}, # Update labels
             title='Effect of product positioning on sales volume',)

st.plotly_chart(fig_position)

# welche Produktgruppe am profitablesten / meist verkauft (bei granularität produkt vllt. top 3)
st.title("Meist verkauft / Profitablesten Produktgruppen")
product_groups = df.groupby('terms')[['Sales Volume', 'Revenue']].sum().reset_index()

metric_to_plot = st.selectbox("Select Metric for Bar Chart:", ['Sales Volume', 'Revenue'])

fig_popular_profit = px.bar(product_groups,
             x='terms',
             y=metric_to_plot,
             labels={'terms': 'Terms', metric_to_plot: metric_to_plot},
             title=f"Aggregated {metric_to_plot} by Terms")

st.plotly_chart(fig_popular_profit)





# Item Häufigkeit pro Section (Gibt es z.B. bei den Dame besonders viele Jacken und bei en Herren besonders viele Schuhe?)
section_counts = df['section'].value_counts().reset_index()
section_counts.columns = ['Section', 'Count']

st.title("Section Counts")

# Create the pie chart using Plotly Express
fig_section_spread = px.pie(section_counts,
             names='Section',
             values='Count',
             title='Distribution of Sections')

# Display the pie chart in Streamlit
st.plotly_chart(fig_section_spread)

# Preis unterschiede der gleichen Produktgruppe zw. beiden Sektionen
section_price = df.groupby(['section', 'terms'])['price'].mean().reset_index()
# Split the DataFrame based on the 'section' column
df_woman = section_price[section_price['section'] == 'WOMAN']
df_man = section_price[section_price['section'] == 'MAN']

section_transf = pd.merge(df_woman, df_man, on='terms', suffixes=('_woman', '_man'), how='outer')

# stacked bar chart
fig_section_price = px.bar(section_transf,
             x='terms',
             y=['price_woman', 'price_man'],
             labels={'terms': 'Terms', 'value': 'Price', 'variable': 'Section'},
             title='Price Comparison by Section and Term',
             #color_discrete_map={'price_woman': 'darkblue', 'price_man': 'lightblue'},
             ) 

st.plotly_chart(fig_section_price)