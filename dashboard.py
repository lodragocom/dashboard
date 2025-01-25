import streamlit as st
import pandas as pd
import re

# Configurazione del layout
st.set_page_config(page_title="Dashboard Interattiva Prodotti", layout="wide")

# Funzione per caricare i file
@st.cache_data
def load_data(product_files, category_files, manufacturer_files):
    # Unisci tutti i file prodotti, caricando solo le colonne necessarie
    product_dfs = [pd.read_csv(file, delimiter=';', usecols=['ID', 'NAME', 'DESCRIPTION', 'CATEGORY', 'BRAND', 'PRICE', 'STOCK', 'EAN13', 'IMAGE1'], low_memory=False) for file in product_files]
    products = pd.concat(product_dfs, ignore_index=True)

    # Unisci tutti i file categorie, caricando solo le colonne necessarie
    category_dfs = [pd.read_csv(file, delimiter=';', usecols=['ID', 'NAME'], low_memory=False) for file in category_files]
    categories = pd.concat(category_dfs, ignore_index=True)

    # Unisci tutti i file produttori, caricando solo le colonne necessarie
    manufacturer_dfs = [pd.read_csv(file, delimiter=';', usecols=['ID', 'NAME'], low_memory=False) for file in manufacturer_files]
    manufacturers = pd.concat(manufacturer_dfs, ignore_index=True)

    # Rinomina colonne per semplificare
    products.columns = products.columns.str.strip()
    categories.columns = categories.columns.str.strip()
    manufacturers.columns = manufacturers.columns.str.strip()

    # Converti ID categorie e produttori in interi se possibile
    if 'ID' in categories.columns:
        categories['ID'] = pd.to_numeric(categories['ID'], errors='coerce').fillna(0).astype(int)
    if 'CATEGORY' in products.columns:
        products['CATEGORY'] = products['CATEGORY'].astype(str)
    if 'BRAND' in products.columns:
        products['BRAND'] = pd.to_numeric(products['BRAND'], errors='coerce').fillna(0).astype(int)
    if 'ID' in manufacturers.columns:
        manufacturers['ID'] = pd.to_numeric(manufacturers['ID'], errors='coerce').fillna(0).astype(int)
    if 'PRICE' in products.columns:
        products['PRICE'] = pd.to_numeric(products['PRICE'], errors='coerce').fillna(0)
    if 'EAN13' in products.columns:
        products['EAN13'] = products['EAN13'].apply(lambda x: f"{int(x):013}" if pd.notnull(x) and x != '' else '')  # Formatta EAN13 come stringa di 13 cifre

    return products, categories, manufacturers

# Funzione per mappare le categorie e i produttori
@st.cache_data
def map_data(products, categories, manufacturers):
    # Crea una mappa ID -> Nome categoria
    category_map = categories.set_index('ID')['NAME'].to_dict()

    # Mappare gli ID delle categorie ai nomi
    def map_category_names(category_ids):
        if pd.isnull(category_ids):
            return []
        try:
            # Gestire ID separati da virgole, spazi o altri separatori
            id_list = [int(cat.strip()) for cat in re.split(r'[ ,;]+', category_ids) if cat.strip().isdigit()]
            category_names = [category_map.get(cat, f"ID: {cat}") for cat in id_list]
            return category_names
        except ValueError:
            return []

    products['Category_List'] = products['CATEGORY'].apply(map_category_names)

    # Mappare i produttori ai prodotti
    manufacturer_map = manufacturers.set_index('ID')['NAME'].to_dict()
    products['Manufacturer'] = products['BRAND'].map(manufacturer_map)

    return products

# Titolo della Dashboard
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        color: #2E3B55;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sidebar-title {
        font-size: 1.2rem;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Dashboard Interattiva Prodotti</div>', unsafe_allow_html=True)

# Sezione per il caricamento dei file
with st.expander("Carica i file", expanded=True):
    st.sidebar.markdown('<div class="sidebar-title">Carica i file:</div>', unsafe_allow_html=True)
    product_files = st.file_uploader("File prodotti", type=["csv"], accept_multiple_files=True)
    category_files = st.file_uploader("File categorie", type=["csv"], accept_multiple_files=True)
    manufacturer_files = st.file_uploader("File produttori", type=["csv"], accept_multiple_files=True)

if product_files and category_files and manufacturer_files:
    # Caricamento dati
    products, categories, manufacturers = load_data(product_files, category_files, manufacturer_files)

    # Mappare categorie e produttori
    products = map_data(products, categories, manufacturers)

    # Dividi CATEGORY_NAME in CATEGORY_1, CATEGORY_2, ...
    try:
        exploded = products.explode('Category_List')
        exploded['Category_Index'] = exploded.groupby('ID').cumcount() + 1
        pivoted = exploded.pivot(index='ID', columns='Category_Index', values='Category_List')
        pivoted.columns = [f"CATEGORY_{col}" for col in pivoted.columns]
        pivoted.reset_index(inplace=True)
        products = pd.merge(products, pivoted, on='ID', how='left')
    except Exception as e:
        st.error(f"Errore durante la suddivisione delle categorie: {e}")

    # Sidebar Filtri
    st.sidebar.markdown('<div class="sidebar-title">Filtri:</div>', unsafe_allow_html=True)
    keyword_filters = []
    for i in range(1, 4):
        keyword = st.sidebar.text_input(f"Parola chiave {i}", key=f"keyword_{i}")
        if keyword:
            keyword_filters.append(keyword.lower())

    filtered_products = products.copy()

    if keyword_filters:
        for keyword in keyword_filters:
            filtered_products = filtered_products[filtered_products['NAME'].str.lower().str.contains(keyword) | filtered_products['DESCRIPTION'].str.lower().str.contains(keyword)]

    available_categories = sorted(set(cat for sublist in filtered_products['Category_List'] for cat in sublist))
    category_filter = st.sidebar.multiselect("Categorie", options=available_categories)
    if category_filter:
        filtered_products = filtered_products[filtered_products['Category_List'].apply(lambda x: any(cat in x for cat in category_filter))]

    available_brands = filtered_products['Manufacturer'].dropna().unique()
    manufacturer_filter = st.sidebar.multiselect("Produttori", options=available_brands)
    if manufacturer_filter:
        filtered_products = filtered_products[filtered_products['Manufacturer'].isin(manufacturer_filter)]

    min_price = st.sidebar.number_input("Prezzo Minimo (€)", value=float(filtered_products['PRICE'].min()), step=0.01)
    max_price = st.sidebar.number_input("Prezzo Massimo (€)", value=float(filtered_products['PRICE'].max()), step=0.01)
    filtered_products = filtered_products[(filtered_products['PRICE'] >= min_price) & (filtered_products['PRICE'] <= max_price)]

    stock_filter = st.sidebar.checkbox("Mostra solo prodotti in stock")
    if stock_filter:
        filtered_products = filtered_products[filtered_products['STOCK'] > 0]

    filtered_products['PRICE'] = filtered_products['PRICE'].apply(lambda x: f"{x:.2f} €" if pd.notnull(x) else "")
    filtered_products['Short_Description'] = filtered_products['DESCRIPTION'].apply(lambda x: ' '.join(x.split()[:8]) if isinstance(x, str) else '')

    st.markdown(f"### Prodotti Filtrati ({len(filtered_products)} totali)")

    items_per_page = 10
    total_pages = (len(filtered_products) + items_per_page - 1) // items_per_page

    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← Pagina precedente"):
            if st.session_state.current_page > 1:
                st.session_state.current_page -= 1
    with col3:
        if st.button("Pagina successiva →"):
            if st.session_state.current_page < total_pages:
                st.session_state.current_page += 1

    st.write(f"Pagina {st.session_state.current_page} di {total_pages}")

    start_idx = (st.session_state.current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    current_data = filtered_products.iloc[start_idx:end_idx]

    current_data['IMAG'] = current_data['IMAGE1'].apply(
        lambda url: f'<img src="{url}" width="50">' if pd.notnull(url) and url else "")

    current_data['Popup_Description'] = current_data['DESCRIPTION'].apply(
        lambda desc: f'<div style="position:relative; white-space: pre-wrap;" title="{desc}">{desc[:50]}...</div>' if isinstance(desc, str) and len(desc) > 50 else desc
    )

    st.write(
        current_data[['IMAG', 'ID', 'EAN13', 'NAME', 'Popup_Description', 'CATEGORY_1', 'CATEGORY_2', 'CATEGORY_3', 'Manufacturer', 'STOCK', 'PRICE']]
        .rename(columns={'Popup_Description': 'DESCRIPTION', 'Manufacturer': 'MANUFACTURER'})
        .to_html(escape=False, index=False),
        unsafe_allow_html=True
    )

    if st.button("Esporta SKU"):
        sku_export = filtered_products[['ID']].rename(columns={'ID': 'SKU'})
        csv = sku_export.to_csv(index=False).encode('utf-8')
        st.download_button("Scarica CSV", data=csv, file_name="sku_filtrati.csv", mime='text/csv')
else:
    st.info("Carica i file prodotti, categorie e produttori per iniziare.")