import streamlit as st
import pandas as pd
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import os

# Configurazione del layout
st.set_page_config(page_title="Dashboard Interattiva Prodotti", layout="wide")

# Directory temporanea per salvare i file caricati
TEMP_DIR = "temp_files"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# Funzione per salvare i file caricati
@st.cache_data
def save_uploaded_files(uploaded_files, file_type):
    file_paths = []
    for uploaded_file in uploaded_files:
        file_path = os.path.join(TEMP_DIR, f"{file_type}_{uploaded_file.name}")
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        file_paths.append(file_path)
    return file_paths

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

# Funzione per mappare le categorie e i produttori
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

# Sinonimi predefiniti
synonyms = {
    "animali": ["pets", "cani", "gatti", "cuccioli"],
    "casa": ["home", "abitazione", "interni", "arredamento"],
    # Aggiungi altri sinonimi rilevanti
}

# Funzione per espandere le keyword con sinonimi
def expand_keywords(keywords):
    expanded_keywords = set(keywords)
    for kw in keywords:
        expanded_keywords.update(synonyms.get(kw, []))
    return list(expanded_keywords)

# Funzione per ricerca fuzzy
def fuzzy_search(text, keywords, threshold=80):
    if pd.isnull(text) or not isinstance(text, str):
        return False
    for kw in keywords:
        if fuzz.partial_ratio(text.lower(), kw.lower()) >= threshold:
            return True
    return False

# Funzione per evidenziare le keyword in modo fuzzy
def highlight_keywords_fuzzy(text, keywords):
    if pd.isnull(text) or not isinstance(text, str):
        return text
    for kw in keywords:
        matches = process.extract(kw, text.split(), limit=5, scorer=fuzz.partial_ratio)
        for match, score in matches:
            if score >= 80:  # Soglia di similarità
                text = text.replace(match, f"**{match}**")
    return text

# Persistenza dei dati
if 'products' not in st.session_state:
    st.session_state['products'] = None
if 'categories' not in st.session_state:
    st.session_state['categories'] = None
if 'manufacturers' not in st.session_state:
    st.session_state['manufacturers'] = None
if 'profile' not in st.session_state:
    st.session_state['profile'] = None

# Pagina di selezione del profilo
if st.session_state['profile'] is None:
    st.markdown("# Seleziona il tuo profilo")
    
    # Crea i pulsanti per la selezione del profilo
    if st.button("Admin"):
        st.session_state['profile'] = "Admin"
    elif st.button("Shop Manager"):
        st.session_state['profile'] = "Shop Manager"
    
else:
    profile = st.session_state['profile']

    # Sezione del profilo
    st.markdown(f"### Profilo: {profile}")
    
    # Pulsante per tornare indietro (riporta alla selezione del profilo)
    if st.button("Torna indietro"):
        st.session_state['profile'] = None

    # Menu di navigazione
    if profile == "Admin":
        menu_options = ["Dashboard", "Profilo", "Catalogo", "Finanze"]
        menu_icons = ["📊", "👤", "📦", "💰"]
    elif profile == "Shop Manager":
        menu_options = ["Dashboard", "Profilo", "Catalogo"]
        menu_icons = ["📊", "👤", "📦"]

    menu_selection = st.sidebar.radio(
        "Seleziona una sezione:",
        options=menu_options,
        format_func=lambda x: f"{menu_icons[menu_options.index(x)]} {x}"
    )

    if menu_selection == "Dashboard":
        # Codice della sezione Dashboard
        st.markdown("<h2 style='text-align: center;'>Dashboard</h2>", unsafe_allow_html=True)
        st.write("Questa è la dashboard interattiva.")

    elif menu_selection == "Profilo":
        # Codice della sezione Profilo
        st.markdown("<h2 style='text-align: center;'>Profilo</h2>", unsafe_allow_html=True)
        st.write("Gestisci le impostazioni del tuo profilo.")

    elif menu_selection == "Catalogo":
        # Codice della sezione Catalogo
        st.markdown("<h2 style='text-align: center;'>Catalogo Prodotti</h2>", unsafe_allow_html=True)
        product_files = st.file_uploader("Carica i file prodotti", type=["csv"], accept_multiple_files=True)
        category_files = st.file_uploader("Carica i file categorie", type=["csv"], accept_multiple_files=True)
        manufacturer_files = st.file_uploader("Carica i file produttori", type=["csv"], accept_multiple_files=True)

        if product_files and category_files and manufacturer_files:
            product_paths = save_uploaded_files(product_files, "products")
            category_paths = save_uploaded_files(category_files, "categories")
            manufacturer_paths = save_uploaded_files(manufacturer_files, "manufacturers")

            st.session_state['products'], st.session_state['categories'], st.session_state['manufacturers'] = load_data(
                product_paths, category_paths, manufacturer_paths)

            st.session_state['products'] = map_data(st.session_state['products'], st.session_state['categories'], st.session_state['manufacturers'])

        if st.session_state['products'] is not None:
            products = st.session_state['products']

            # Filtri dinamici specifici per campi
            st.sidebar.markdown('<div class="sidebar-title">Filtri:</div>', unsafe_allow_html=True)
            keywords_name = st.sidebar.text_input("Parole chiave nel Nome (separate da virgola)", key="keywords_name")
            keywords_description = st.sidebar.text_input("Parole chiave nella Descrizione (separate da virgola)", key="keywords_description")
            keywords_combined = st.sidebar.text_input("Parole chiave combinate (separate da virgola)", key="keywords_combined")

            filtered_products = products.copy()

            # Filtrare in base al Nome con logica AND
            if keywords_name:
                name_keywords = [kw.strip().lower() for kw in keywords_name.split(',')]
                expanded_name_keywords = expand_keywords(name_keywords)
                filtered_products = filtered_products[
                    filtered_products['NAME'].apply(
                        lambda name: fuzzy_search(name, expanded_name_keywords)
                    )
                ]
                filtered_products['NAME'] = filtered_products['NAME'].apply(
                    lambda name: highlight_keywords_fuzzy(name, expanded_name_keywords) if isinstance(name, str) else name
                )

            # Filtrare in base alla Descrizione con logica AND
            if keywords_description:
                description_keywords = [kw.strip().lower() for kw in keywords_description.split(',') if kw.strip()]
                expanded_description_keywords = expand_keywords(description_keywords)
                filtered_products = filtered_products[
                    filtered_products['DESCRIPTION'].apply(
                        lambda desc: fuzzy_search(desc, expanded_description_keywords)
                    )
                ]
                filtered_products['DESCRIPTION'] = filtered_products['DESCRIPTION'].apply(
                    lambda desc: highlight_keywords_fuzzy(desc, expanded_description_keywords) if isinstance(desc, str) else desc
                )

            # Filtrare in base alla combinazione personalizzata con logica AND
            if keywords_combined:
                combined_keywords = [kw.strip().lower() for kw in keywords_combined.split(',')]
                expanded_combined_keywords = expand_keywords(combined_keywords)
                filtered_products = filtered_products[
                    filtered_products['NAME'].apply(
                        lambda name: fuzzy_search(name, expanded_combined_keywords)
                    ) |
                    filtered_products['DESCRIPTION'].apply(
                        lambda desc: fuzzy_search(desc, expanded_combined_keywords)
                    )
                ]
                filtered_products['NAME'] = filtered_products['NAME'].apply(
                    lambda name: highlight_keywords_fuzzy(name, expanded_combined_keywords) if isinstance(name, str) else name
                )
                filtered_products['DESCRIPTION'] = filtered_products['DESCRIPTION'].apply(
                    lambda desc: highlight_keywords_fuzzy(desc, combined_keywords) if isinstance(desc, str) else desc
                )


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

            # Aggiungere la colonna delle immagini e abbreviazione del testo per la descrizione
            filtered_products['IMAG'] = filtered_products['IMAGE1'].apply(
                lambda url: f'<img src="{url}" width="50">' if pd.notnull(url) and url else "")

            if not show_full_description:
                filtered_products['DESCRIPTION'] = filtered_products['DESCRIPTION'].apply(
                    lambda desc: " ".join(desc.split()[:8]) + "..." if isinstance(desc, str) and len(desc.split()) > 8 else desc
                )

            # Visualizzazione della tabella filtrata
            st.write(
                filtered_products.iloc[start_idx:end_idx][['IMAG', 'ID', 'EAN13', 'NAME', 'DESCRIPTION', 'CATEGORY_1', 'CATEGORY_2', 'CATEGORY_3', 'Manufacturer', 'STOCK', 'PRICE']]
                .to_html(escape=False, index=False),
                unsafe_allow_html=True
            )

    elif menu_selection == "Finanze":
        # Codice della sezione Finanze
        st.markdown("<h2 style='text-align: center;'>Finanze</h2>", unsafe_allow_html=True)
        st.write("Gestisci report e dati finanziari.")
