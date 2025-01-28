import streamlit as st
import pandas as pd
import datetime
import uuid
import numpy as np
from auth import update_user_data, get_global_state
from utils.data_utils import load_catalog_from_file

# Funzione per caricare il CSS
def load_css():
    css_path = "assets/styles.css"
    with open(css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Funzione per gestire il sistema di fatturazione
def sistema_fatturazione():
    st.set_page_config(page_title="Sistema di Fatturazione", layout="wide")

    # Caricamento CSS personalizzato
    load_css()

    # Header della pagina
    st.markdown("<div class='finance-header'>Gestione Finanze 🧾</div>", unsafe_allow_html=True)

    # Navigazione interna alla pagina Finanze
    menu = ["Dashboard", "Invoice", "Cost", "Supplier"]
    choice = st.sidebar.radio("Navigazione Finanze", menu)

    # Carica le fatture salvate
    if "invoices" not in st.session_state:
        st.session_state["invoices"] = get_global_state("invoices", default=[])

    # Recupera il catalogo se non è disponibile in sessione
    if "products" not in st.session_state:
        products, categories, manufacturers = load_catalog_from_file()
        if products is not None:
            st.session_state["products"] = products
        else:
            st.error("Devi prima caricare i prodotti nella sezione Catalogo.")
            st.stop()

    # Verifica se il catalogo è caricato
    if "products" in st.session_state and st.session_state["products"] is not None:
        products_df = st.session_state["products"]
    else:
        st.error("Il catalogo non è stato caricato correttamente.")
        st.stop()

    if choice == "Dashboard":
        st.markdown("<div class='section-header'>Dashboard Finanziaria</div>", unsafe_allow_html=True)

        # Dati simulati per il grafico
        data = {
            "Mese": ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio"],
            "Entrate (€)": [1200, 1500, 1700, 2000, 1800],
            "Uscite (€)": [800, 900, 1100, 1000, 950]
        }
        df = pd.DataFrame(data)

        # Grafico dinamico delle entrate e uscite
        st.line_chart(data=df.set_index("Mese"), use_container_width=True)

        # Riepilogo metriche
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Entrate Totali (€)", value=sum(df["Entrate (€)"]))
        with col2:
            st.metric(label="Uscite Totali (€)", value=sum(df["Uscite (€)"]))
        with col3:
            st.metric(label="Saldo Netto (€)", value=sum(df["Entrate (€)"]) - sum(df["Uscite (€)"]))

    elif choice == "Invoice":
        st.markdown("<div class='section-header'>Sistema di Fatturazione</div>", unsafe_allow_html=True)

        # Selezione del tipo di cliente
        tipo_cliente = st.radio("Seleziona il tipo di cliente", ["Privato", "Business"])

        # Modulo per cliente privato
        if tipo_cliente == "Privato":
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("Nome")
                cognome = st.text_input("Cognome")
            with col2:
                indirizzo = st.text_area("Indirizzo")
                telefono = st.text_input("Numero di Telefono")
                email = st.text_input("Email")

        # Modulo per cliente business
        elif tipo_cliente == "Business":
            col1, col2 = st.columns(2)
            with col1:
                nome_azienda = st.text_input("Nome Azienda")
                partita_iva = st.text_input("Partita IVA")
            with col2:
                indirizzo = st.text_area("Indirizzo")
                telefono = st.text_input("Numero di Telefono")
                email = st.text_input("Email")

        # Selezione dei prodotti
        st.markdown("### Seleziona Prodotti dal Catalogo")
        prodotti_selezionati = st.multiselect(
            "Scegli i prodotti",
            options=products_df["NAME"].tolist(),
            format_func=lambda x: f"{x}",
        )

        # Calcolo totale
        totale = products_df[products_df["NAME"].isin(prodotti_selezionati)]["PRICE"].sum()

        st.markdown(f"### Totale: €{totale:.2f}")

        # Salvataggio fattura
        if st.button("Genera Fattura"):
            fattura = {
                "ID": str(uuid.uuid4()),
                "Tipo Cliente": tipo_cliente,
                "Nome": nome if tipo_cliente == "Privato" else nome_azienda,
                "Indirizzo": indirizzo,
                "Telefono": telefono,
                "Email": email,
                "Prodotti": prodotti_selezionati,
                "Totale (€)": totale,
                "Data": datetime.date.today().isoformat(),
            }
            st.session_state["invoices"].append(fattura)
            update_user_data("invoices", st.session_state["invoices"])
            st.success("Fattura generata con successo!")

        # Visualizzazione delle fatture
        if st.session_state["invoices"]:
            st.markdown("### Elenco Fatture")
            fatture_df = pd.DataFrame(st.session_state["invoices"])
            st.table(fatture_df)

    elif choice == "Cost":
        st.markdown("<div class='section-header'>Gestione Costi</div>", unsafe_allow_html=True)
        st.info("Questa sezione permetterà di gestire i costi aziendali.")

    elif choice == "Supplier":
        st.markdown("<div class='section-header'>Gestione Fornitori</div>", unsafe_allow_html=True)
        st.info("Questa sezione permetterà di gestire i fornitori.")

if __name__ == "__main__":
    sistema_fatturazione()