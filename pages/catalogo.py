import streamlit as st
import pandas as pd
import numpy as np
import os
import re
import random
from auth import update_user_data, get_global_state
from utils.data_utils import save_catalog_to_file, load_catalog_from_file


# Configurazione del layout
st.set_page_config(page_title="Catalogo Prodotti", layout="wide")

# Controllo dell'accesso
if "username" not in st.session_state:
    st.error("Accesso non autorizzato! Torna al login.")
    st.stop()

# Caricamento dati persistenti
user_data = get_global_state("catalogo_data", default={})
if "products" in user_data:
    st.session_state["products"] = pd.DataFrame(user_data["products"])
if "categories" in user_data:
    st.session_state["categories"] = pd.DataFrame(user_data["categories"])
if "manufacturers" in user_data:
    st.session_state["manufacturers"] = pd.DataFrame(user_data["manufacturers"])

# Funzione per caricare i file
@st.cache_data
def load_data(product_files, category_files, manufacturer_files):
    product_dfs = [pd.read_csv(file, delimiter=';', usecols=['ID', 'NAME', 'DESCRIPTION', 'CATEGORY', 'BRAND', 'PRICE', 'STOCK', 'EAN13', 'IMAGE1'], low_memory=False) for file in product_files]
    products = pd.concat(product_dfs, ignore_index=True)

    category_dfs = [pd.read_csv(file, delimiter=';', usecols=['ID', 'NAME'], low_memory=False) for file in category_files]
    categories = pd.concat(category_dfs, ignore_index=True)

    manufacturer_dfs = [pd.read_csv(file, delimiter=';', usecols=['ID', 'NAME'], low_memory=False) for file in manufacturer_files]
    manufacturers = pd.concat(manufacturer_dfs, ignore_index=True)

    products.columns = products.columns.str.strip()
    categories.columns = categories.columns.str.strip()
    manufacturers.columns = manufacturers.columns.str.strip()

    if 'ID' in categories.columns:
        categories['ID'] = pd.to_numeric(categories['ID'], errors='coerce').fillna(0).astype(int)
    if 'CATEGORY' in products.columns:
        products['CATEGORY'] = products['CATEGORY'].astype(str)
    if 'BRAND' in products.columns:
        products['BRAND'] = pd.to_numeric(products['BRAND'], errors='coerce').fillna(0).astype(int)
    if 'PRICE' in products.columns:
        products['PRICE'] = pd.to_numeric(products['PRICE'], errors='coerce').fillna(0)
    if 'EAN13' in products.columns:
        products['EAN13'] = products['EAN13'].apply(lambda x: f"{int(x):013}" if pd.notnull(x) and x != '' else '')

    return products, categories, manufacturers

# Verifica se i cataloghi sono già memorizzati
if "products" not in st.session_state:
    # Carica i cataloghi salvati sul disco
    products, categories, manufacturers = load_catalog_from_file()
    if products is not None:
        st.session_state["products"] = products
        st.session_state["categories"] = categories
        st.session_state["manufacturers"] = manufacturers
        st.success("Cataloghi caricati correttamente dalla memoria persistente.")
    else:
        st.warning("Nessun catalogo trovato. Caricali per iniziare.")

# Funzione per mappare i dati
@st.cache_data
def map_data(products, categories, manufacturers):
    category_map = categories.set_index('ID')['NAME'].to_dict()

    def map_category_names(category_ids):
        if pd.isnull(category_ids):
            return []
        try:
            id_list = [int(cat.strip()) for cat in re.split(r'[ ,;]+', category_ids) if cat.strip().isdigit()]
            category_names = [category_map.get(cat, f"ID: {cat}") for cat in id_list]
            return category_names
        except ValueError:
            return []

    products['Category_List'] = products['CATEGORY'].apply(map_category_names)
    manufacturer_map = manufacturers.set_index('ID')['NAME'].to_dict()
    products['Manufacturer'] = products['BRAND'].map(manufacturer_map)

    # Suddividere le categorie in colonne separate
    exploded = products.explode('Category_List')
    exploded['Category_Index'] = exploded.groupby('ID').cumcount() + 1
    pivoted = exploded.pivot(index='ID', columns='Category_Index', values='Category_List')
    pivoted.columns = [f"CATEGORY_{col}" for col in pivoted.columns]
    pivoted.reset_index(inplace=True)
    products = pd.merge(products, pivoted, on='ID', how='left')

    return products

# Funzione per salvare i file caricati
@st.cache_data
def save_uploaded_files(uploaded_files, file_type):
    TEMP_DIR = "temp_files"
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    file_paths = []
    for uploaded_file in uploaded_files:
        file_path = os.path.join(TEMP_DIR, f"{file_type}_{uploaded_file.name}")
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        file_paths.append(file_path)

    return file_paths

# Navigazione interna
menu = ["Dashboard", "BigBuy", "Dreamlove", "VidaXL"]
choice = st.sidebar.radio("Navigazione Catalogo", menu)

if choice == "Dashboard":
    st.markdown("<h2 style='text-align: center;'>Dashboard Interattiva</h2>", unsafe_allow_html=True)

    # Visualizzazione di metriche principali
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Prodotti Caricati", value=len(st.session_state.get("products", [])))
    col2.metric("Categorie Disponibili", value=len(st.session_state.get("categories", [])))
    col3.metric("Produttori", value=len(st.session_state.get("manufacturers", [])))
    col4.metric("Stock Totale", value=random.randint(2000, 5000))

    st.markdown("<hr>", unsafe_allow_html=True)

    # Grafici dinamici con numpy
    col1, col2, col3 = st.columns(3)

    # Grafico 1: Distribuzione Prezzi
    with col1:
        st.markdown("<h5>Distribuzione Prezzi</h5>", unsafe_allow_html=True)
        categories = ["Elettronica", "Casa", "Sport", "Moda"]
        prices = [random.randint(10, 100) for _ in categories]
        st.bar_chart(pd.DataFrame({"Categoria": categories, "Prezzo Medio (€)": prices}).set_index("Categoria"))

    # Grafico 2: Stock per Categoria
    with col2:
        st.markdown("<h5>Stock per Categoria</h5>", unsafe_allow_html=True)
        stocks = [random.randint(100, 1000) for _ in categories]
        st.bar_chart(pd.DataFrame({"Categoria": categories, "Stock Totale": stocks}).set_index("Categoria"))

    # Grafico 3: Vendite per Mese
    with col3:
        st.markdown("<h5>Vendite Mensili</h5>", unsafe_allow_html=True)
        months = ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu"]
        sales = [random.randint(100, 500) for _ in months]
        st.line_chart(pd.DataFrame({"Mese": months, "Vendite (€)": sales}).set_index("Mese"))

elif choice == "BigBuy":
    st.markdown("<h2 style='text-align: center;'>Catalogo BigBuy</h2>", unsafe_allow_html=True)
    product_files = st.file_uploader("Carica i file prodotti", type=["csv"], accept_multiple_files=True)
    category_files = st.file_uploader("Carica i file categorie", type=["csv"], accept_multiple_files=True)
    manufacturer_files = st.file_uploader("Carica i file produttori", type=["csv"], accept_multiple_files=True)

    if product_files and category_files and manufacturer_files:
        product_paths = save_uploaded_files(product_files, "products")
        category_paths = save_uploaded_files(category_files, "categories")
        manufacturer_paths = save_uploaded_files(manufacturer_files, "manufacturers")

        st.session_state['products'], st.session_state['categories'], st.session_state['manufacturers'] = load_data(product_paths, category_paths, manufacturer_paths)
        st.session_state['products'] = map_data(st.session_state['products'], st.session_state['categories'], st.session_state['manufacturers'])
        update_user_data('catalogo_data', {
            'products': st.session_state['products'].to_dict(orient='records'),
            'categories': st.session_state['categories'].to_dict(orient='records'),
            'manufacturers': st.session_state['manufacturers'].to_dict(orient='records')
        })

    if st.session_state.get('products') is not None:
        products = st.session_state['products']

        # Filtri dinamici
        st.sidebar.markdown('<div class="sidebar-title">Filtri:</div>', unsafe_allow_html=True)
        keywords_name = st.sidebar.text_input("Parole chiave nel Nome (separate da virgola)", key="keywords_name")
        keywords_description = st.sidebar.text_input("Parole chiave nella Descrizione (separate da virgola)", key="keywords_description")
        keywords_combined = st.sidebar.text_input("Parole chiave combinate (separate da virgola)", key="keywords_combined")

        filtered_products = products.copy()

        # Filtrare in base al Nome con logica AND
        if keywords_name:
            name_keywords = [kw.strip().lower() for kw in keywords_name.split(',')]
            filtered_products = filtered_products[
                filtered_products['NAME'].apply(lambda name: all(kw in name.lower() for kw in name_keywords))
            ]

        # Filtrare in base alla Descrizione con logica AND
        if keywords_description:
            description_keywords = [kw.strip().lower() for kw in keywords_description.split(',')]
            filtered_products = filtered_products[
                filtered_products['DESCRIPTION'].apply(lambda desc: all(kw in desc.lower() for kw in description_keywords))
            ]

        # Filtrare in base alla combinazione personalizzata con logica AND
        if keywords_combined:
            combined_keywords = [kw.strip().lower() for kw in keywords_combined.split(',')]
            filtered_products = filtered_products[
                filtered_products['NAME'].apply(lambda name: any(kw in name.lower() for kw in combined_keywords)) |
                filtered_products['DESCRIPTION'].apply(lambda desc: any(kw in desc.lower() for kw in combined_keywords))
            ]

        # Filtri aggiuntivi
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

        # Opzione per mostrare testo completo nella colonna DESCRIPTION
        show_full_description = st.sidebar.checkbox("Mostra testo completo nella descrizione")

        if not show_full_description:
            filtered_products['DESCRIPTION'] = filtered_products['DESCRIPTION'].apply(
                lambda desc: " ".join(desc.split()[:8]) + "..." if isinstance(desc, str) and len(desc.split()) > 8 else desc
            )

        # Aggiungere la colonna delle immagini e abbreviazione del testo per la descrizione
        filtered_products['IMAG'] = filtered_products['IMAGE1'].apply(
            lambda url: f'<img src="{url}" width="50">' if pd.notnull(url) and url else ""
        )

        # Paginazione
        items_per_page = 20
        total_items = len(filtered_products)
        total_pages = (total_items + items_per_page - 1) // items_per_page

        if 'current_page' not in st.session_state:
            st.session_state['current_page'] = 1

        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("← Pagina precedente"):
                if st.session_state['current_page'] > 1:
                    st.session_state['current_page'] -= 1
        with col3:
            if st.button("Pagina successiva →"):
                if st.session_state['current_page'] < total_pages:
                    st.session_state['current_page'] += 1

        start_idx = (st.session_state['current_page'] - 1) * items_per_page
        end_idx = start_idx + items_per_page

        st.markdown(f"### Prodotti Filtrati ({total_items} totali) - Pagina {st.session_state['current_page']} di {total_pages}")

        # Visualizzazione della tabella filtrata
        st.write(
            filtered_products.iloc[start_idx:end_idx][['IMAG', 'ID', 'EAN13', 'NAME', 'DESCRIPTION', 'CATEGORY_1', 'CATEGORY_2', 'CATEGORY_3', 'Manufacturer', 'STOCK', 'PRICE']]
            .to_html(escape=False, index=False),
            unsafe_allow_html=True
        )

        # Esportazione CSV
        st.sidebar.markdown("## Esporta i Dati Filtrati")
        selected_columns = st.sidebar.multiselect("Seleziona le colonne da esportare:", options=filtered_products.columns.tolist(), default=filtered_products.columns.tolist())

        if st.sidebar.button("Esporta in CSV"):
            csv_data = filtered_products[selected_columns].to_csv(index=False, sep=';')
            st.sidebar.download_button(
                label="Scarica CSV",
                data=csv_data,
                file_name="prodotti_filtrati.csv",
                mime="text/csv"
            )

elif choice == "Dreamlove" or choice == "VidaXL":
    st.markdown(f"<h2 style='text-align: center;'>Catalogo {choice}</h2>", unsafe_allow_html=True)
    st.markdown("<p>Carica i tuoi file per iniziare:</p>", unsafe_allow_html=True)
    uploaded_files = st.file_uploader("Carica file CSV", type=["csv"], accept_multiple_files=True)

    if uploaded_files:
        file_paths = save_uploaded_files(uploaded_files, choice.lower())
        st.success(f"File caricati con successo in temp_files.")
