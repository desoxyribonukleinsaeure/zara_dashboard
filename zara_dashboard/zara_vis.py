# Falls das README nicht funktioniert, ist hier nochmal der Inhalt der README:

# Setup
# change directory auf zara_dashboard in Terminal (cd zara_dashboard)
# aktiviere die venv (source .venv/bin/activate)
# zara_vis.py laufen lassen (streamlit run zara_vis.py)

# Aufteilung
# Planung des Dashboards: Yaren, Laélia
# Umsetzung des Dashboards: Laélia
# Aufwandsteilung für das Dashboard: 90% Laélia, 10% Yaren



# 0. Notwendige Packages importieren
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.title("ZARA Verkaufsdaten")

# Whitespace
st.columns(1)[0].write("")
st.columns(1)[0].write("")

# 1. Daten laden
df = pd.read_csv("zara.csv", sep=';')

# 2. Gesamt-Umsatz KPI
df['Revenue'] = df['Sales Volume'] * df['price']
total_revenue = df['Revenue'].sum()

# 3. Gesamt-Verkäufe KPI
total_sales_volume = df['Sales Volume'].sum()

# 4. Effektivität von Promotionen KPI
promo = df.groupby(['terms', 'Promotion'])['Sales Volume'].sum().reset_index()

# 4.1 Änderung in Verkaufszahlen pro Produktgruppe berechnen
# (Die Daten wurden gescrapt, d.h. bilden eine Art Momentaufnahme ab.
# Ein Produkt kann also in diesen Daten nicht gleichzeitig in Promotion und nicht in Promotion sein.
# Man kann also die Verkaufszahlen desselben Produktes nicht vor und nach einer Promo vergleichen.
# Daher wurde auf Produktgruppen-Ebene (Spalte 'terms') verglichen.)
promotion_impact = {}
for term in promo['terms'].unique():
    term_data = promo[promo['terms'] == term]
    sales_yes = term_data[term_data['Promotion'] == 'Yes']['Sales Volume'].values
    sales_no = term_data[term_data['Promotion'] == 'No']['Sales Volume'].values

    impact_ratio = (sales_yes[0] / sales_no[0]) - 1
    promotion_impact[term] = impact_ratio

promo_values = list(promotion_impact.values())
mean_promo_impact = np.mean(promo_values)

# Alle drei KPIs darstellen
col1, col2, col3 = st.columns([1, 1, 0.5])
with col1:
    st.markdown(f"<font color='green'><h2>{total_revenue:,.2f} $</h2></font>", unsafe_allow_html=True)
    st.caption("Gesamter Umsatz")

with col2:
    st.markdown(f"<font color='green'><h2>{total_sales_volume} Stück</h2></font>", unsafe_allow_html=True)
    st.caption("Gesamte Verkäufe")

with col3:
    st.markdown(f"<font color='darkred'><h2>{mean_promo_impact:.3f} %</h2></font>", unsafe_allow_html=True)
    st.caption("Promo-Effekt")

# Whitespace
st.columns(1)[0].write("")
st.columns(1)[0].write("")
st.columns(1)[0].write("")
st.columns(1)[0].write("")

col_season, col_pad, col_section = st.columns([1, 0.2, 1])
# 5. Verhältnis seasonal/not seasonal
with col_season:
    st.subheader('Saisonalität')
    seasonal_counts = df['Seasonal'].value_counts().reset_index()
    seasonal_counts.columns = ['Seasonal', 'Count']

    seasonal_mapping = {'Yes': 'Saisonal', 'No': 'Nicht<br>Saisonal'}
    # Zeilenumbruch in 'Nicht<br>Saisonal', damit die Legende weniger horizontalen Platz einnimmt und
    # das Ringdiagramm gleichgroß ist wie das für die Sektionen (folgendes Diagramm)

    seasonal_counts['Seasonal_Display'] = seasonal_counts['Seasonal'].map(seasonal_mapping)

    # 5.1 Ring-Diagramm zur Darstellung, da es hier um Verhälnisse geht, die insg. 100% ergeben müssen
    fig_seasonal = px.pie(seasonal_counts,
                names='Seasonal_Display',
                values='Count',
                hole=0.6,
                labels={'Seasonal_Display': 'Saisonalität'},
                color='Seasonal_Display',
                color_discrete_map={'Saisonal': 'green', 'Nicht<br>Saisonal': 'lightgray'})

    st.plotly_chart(fig_seasonal, use_container_width=True)

# 6. Häufigkeit pro Sektion (Fragestellung: Gibt es mehr Artikel in der Damen bzw. Herren Sektion?)
with col_section:
    st.subheader("Sektionen")

    section_counts = df['section'].value_counts().reset_index()
    section_counts.columns = ['Section', 'Count']

    # 6.1 Darstellung
    fig_section_spread = px.pie(section_counts,
                names='Section',
                values='Count',
                hole=0.6,
                color='Section',
                color_discrete_map={'WOMAN': 'lightcoral', 'MAN': 'dodgerblue'})

    st.plotly_chart(fig_section_spread, use_container_width=True)



# 7. Preis unterschiede der gleichen Produktgruppe zw. beiden Sektionen
# (mögl. Fragestellung: Sind Herren-Produktgruppen im Schnitt teuerer/günstiger als Damen-Produktgruppen?)
st.subheader('Preisvergleich nach Sektion')
section_price = df.groupby(['section', 'terms'])['price'].mean().reset_index()

df_woman = section_price[section_price['section'] == 'WOMAN'].rename(columns={'price': 'Preis WOMAN'})
df_man = section_price[section_price['section'] == 'MAN'].rename(columns={'price': 'Preis MAN'})
section_transf = pd.merge(df_woman, df_man, on='terms', how='outer')

# Man wollte zunächst die Preis-Spalte der Damen-Sektion mit der Preis-Spalte der Herren-Sektion substrahieren und diese Differenz plotten.
# Daher die Auspaltung und das Zusammenführen der Dataframes, da man einfach df[Spalte 1] - df[Spalte 2] machen könnte.
# Es stellte sich aber heraus, dass dieser Datensatz nur Sweater in der Damen-Sektion hatte.
# Deswegen hat man sich entschieden, die Durchschnittspreise als gestapeltes Balkendiagramm darzustellen, statt die Differenz.

# 7.1 Darstellung
fig_section_price = px.bar(section_transf,
             x='terms',
             y=['Preis WOMAN', 'Preis MAN'],
             labels={'terms': 'Produktgruppe', 'value': 'Preis', 'variable': 'Sektion'},
             color_discrete_map={'Preis WOMAN': 'lightcoral', 'Preis MAN': 'dodgerblue'},
             )

st.plotly_chart(fig_section_price)

# Whitespace
st.columns(1)[0].write("")
st.columns(1)[0].write("")
st.columns(1)[0].write("")
st.columns(1)[0].write("")

# 8. Max-Min Produkt-Popularität/-Profitabilität
# (mögl. Fragestellungen: Ist ein Produkt besonders populär/profitabel?
# Werden Artikel eher gleichmäßig gekauft oder einige viel, einige fast nicht?)
st.subheader("Produkt Analyse")

# Whitespace
st.columns(1)[0].write("")

products = df.groupby('name')[['Sales Volume', 'Revenue']].sum().reset_index()

# 8.1 Meist/wenigste verkaufte Produkt und seine Verkaufszahl
most_sold_volume = products.loc[products['Sales Volume'].idxmax()]
most_sold_name = most_sold_volume['name']
least_sold_volume = products.loc[products['Sales Volume'].idxmin()]
least_sold_name = least_sold_volume['name']

# 8.2 Produkt, welches am meisten/wenigsten Umsatz gemacht hat und seine Umsatzzahl
most_profitable = products.loc[products['Revenue'].idxmax()]
most_profitable_name = most_profitable['name']
least_profitable = products.loc[products['Revenue'].idxmin()]
least_profitable_name = least_profitable['name']

# 8.3 Unterschied im Gesamtbeitrag
# Diese Rechnung dient zum Herausfinden, wie verschieden sie zum gesamten Verkauf/Umsatz beigetragen haben,
# also ob das beste Produkt viel mehr beigetragen hat als das schlechteste.
# Maximal-Wert wäre hier 100%, was bedeuten würde, dass das beste Produkt hat den gesamten Verkauf/Umsatz ausgemacht und das schlechteste hat nichts beigetragen.
# Minimal-Wert wäre hier 0%, was bedeuten würde, dass das beste und schlechteste Produkt gleichviel beigetragen haben.
sales_volume_range = (products['Sales Volume'].max()/products['Sales Volume'].sum()) - (products['Sales Volume'].min()/products['Sales Volume'].sum())
revenue_range = (products['Revenue'].max()/products['Revenue'].sum()) - (products['Revenue'].min()/products['Revenue'].sum())

sales_revenue = st.radio("Wähle anzuzeigene Größe aus:", ['Sales Volume', 'Revenue'])

# 8.4 Layout / Darstellung
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

# Whitespace
st.columns(1)[0].write("")
st.columns(1)[0].write("")
st.columns(1)[0].write("")
st.columns(1)[0].write("")

# 9. Auswirkung der Produkt Position auf Anzahl der Verkäufe
# (Fragestellung: Werden Produkte in der End-Cap bzw. in Front of Store mehr oder weniger gekauft als in der Aisle?)
# Zu Beachten: End-Cap und Front of Store haben weniger Fläche als Aisle und werden in absoluten Verkaufszahlen wahrscheinlich generell geringer sein.
# Für die genauste Betrachtung müsste man dasselbe Produkt in derselben Menge an verschieden Positionen platzieren und die Verkaufszahlen beobachten.
# Da die Daten nur eine Momentaufnahme sind, wurde die Auswirkung der Position hier ebenfalls auf Produktgruppen-Ebene verglichen und dann zusammengefasst.
st.subheader("Auswirkung der Produkt Positionierung auf Verkaufszahl")

aggregated_df = df.groupby(['terms', 'Product Position'])['Sales Volume'].sum().reset_index()

unique_positions = aggregated_df['Product Position'].nunique()
base_position = 'Aisle'
aisle_volume_per_term = aggregated_df[aggregated_df['Product Position'] == base_position].groupby('terms')['Sales Volume'].transform('first').reset_index(drop=True)
repeated_array = np.repeat(aisle_volume_per_term.values, unique_positions)

# Hinweis: Da Aisle als Basis fungiert, wird dafür immer 0 rauskommen
aggregated_df['aisle_volume'] = repeated_array
aggregated_df['change_to_base'] = (aggregated_df['Sales Volume'] / aggregated_df['aisle_volume']) - 1
position_effect = aggregated_df.groupby(['Product Position'])['change_to_base'].mean().reset_index()

# 9.1 Darstellung
fig_position = px.bar(position_effect,
             y='Product Position',
             x='change_to_base',
             labels={'Product Position': 'Produkt Position', 'change_to_base': 'Änderung verglichen mit Aisle'},
             color_discrete_sequence=['darkred']
             )

st.plotly_chart(fig_position)

# Whitespace
st.columns(1)[0].write("")
st.columns(1)[0].write("")
st.columns(1)[0].write("")
st.columns(1)[0].write("")

# 10. Popularität/Profitabilität nach Produktgruppe
# (Fragestellung: Welche Produktgruppe ist am profitablesten / wird am meisten verkauft?)
st.subheader("Meist verkauften / profitablesten Produktgruppen")

product_groups = df.groupby('terms')[['Sales Volume', 'Revenue']].sum().reset_index()

metric_to_plot = st.selectbox("Wähle anzuzeigene Größe aus:", ['Sales Volume', 'Revenue'])
sort_by = st.radio("Sortiere Balken nach:", ['Größe', 'Alphabet'])

if sort_by == 'Größe':
    product_groups_sorted = product_groups.sort_values(by=metric_to_plot, ascending=False)
elif sort_by == 'Alphabet':
    product_groups_sorted = product_groups.sort_values(by='terms')
else:
    product_groups_sorted = product_groups  # Default Reihenfolge

# 10.1 Darstellung
fig_popular_profit = px.bar(product_groups_sorted,
             x='terms',
             y=metric_to_plot,
             labels={'terms': 'Produktgruppe', metric_to_plot: metric_to_plot},
             color_discrete_sequence=['lightcoral'])

st.plotly_chart(fig_popular_profit)