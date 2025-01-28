import os
import pandas as pd

# Directory per memorizzare i file catalogo
CATALOG_DIR = "catalog_data"
if not os.path.exists(CATALOG_DIR):
    os.makedirs(CATALOG_DIR)

def save_catalog_to_file(products, categories, manufacturers):
    """Salva i dati del catalogo su file."""
    products.to_csv(os.path.join(CATALOG_DIR, "products.csv"), index=False)
    categories.to_csv(os.path.join(CATALOG_DIR, "categories.csv"), index=False)
    manufacturers.to_csv(os.path.join(CATALOG_DIR, "manufacturers.csv"), index=False)

def load_catalog_from_file():
    """Carica i dati del catalogo da file."""
    try:
        products = pd.read_csv(os.path.join(CATALOG_DIR, "products.csv"))
        categories = pd.read_csv(os.path.join(CATALOG_DIR, "categories.csv"))
        manufacturers = pd.read_csv(os.path.join(CATALOG_DIR, "manufacturers.csv"))
        return products, categories, manufacturers
    except FileNotFoundError:
        return None, None, None
