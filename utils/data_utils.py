import pandas as pd
import re
import os
import streamlit as st

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

    return products, categories, manufacturers

# Funzione per mappare i dati
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

    return products

# Sinonimi predefiniti
synonyms = {
    "animali": ["pets", "cani", "gatti", "cuccioli"],
    "casa": ["home", "abitazione", "interni", "arredamento"],
}

# Espansione delle keyword
def expand_keywords(keywords):
    expanded_keywords = set(keywords)
    for kw in keywords:
        expanded_keywords.update(synonyms.get(kw, []))
    return list(expanded_keywords)

# Ricerca fuzzy
def fuzzy_search(text, keywords, threshold=80):
    if pd.isnull(text) or not isinstance(text, str):
        return False
    for kw in keywords:
        if fuzz.partial_ratio(text.lower(), kw.lower()) >= threshold:
            return True
    return False

# Evidenziazione delle keyword
def highlight_keywords_fuzzy(text, keywords):
    if pd.isnull(text) or not isinstance(text, str):
        return text
    for kw in keywords:
        matches = process.extract(kw, text.split(), limit=5, scorer=fuzz.partial_ratio)
        for match, score in matches:
            if score >= 80:
                text = text.replace(match, f"**{match}**")
    return text
