import streamlit as st
import pandas as pd
import datetime
import uuid
import plotly.express as px

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
        fig = px.line(
            df,
            x="Mese",
            y=["Entrate (€)", "Uscite (€)"],
            labels={"value": "Euro", "variable": "Tipologia"},
            title="Andamento Finanziario"
        )
        st.plotly_chart(fig, use_container_width=True)

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

        # Inizializzazione dello stato per le fatture
        if "invoices" not in st.session_state:
            st.session_state["invoices"] = []

        # Modulo per creare una nuova fattura
        with st.form(key="new_invoice_form"):
            col1, col2 = st.columns(2)

            with col1:
                cliente = st.text_input("Cliente")
                data_emissione = st.date_input("Data di Emissione", datetime.date.today())
            with col2:
                importo = st.number_input("Importo Totale (€)", min_value=0.0, step=0.01)
                stato = st.selectbox("Stato", options=["Pagata", "In attesa"])

            prodotti_servizi = st.text_area("Descrizione Prodotti/Servizi")

            # Pulsante per salvare la fattura
            if st.form_submit_button("Salva Fattura"):
                nuova_fattura = {
                    "ID": str(uuid.uuid4()),
                    "Cliente": cliente,
                    "Data": data_emissione,
                    "Importo (€)": importo,
                    "Stato": stato,
                    "Dettagli": prodotti_servizi
                }
                st.session_state["invoices"].append(nuova_fattura)
                st.success("Fattura salvata con successo!")

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        # Sezione: Elenco Fatture
        if st.session_state["invoices"]:
            fatture_df = pd.DataFrame(st.session_state["invoices"])

            # Tabella interattiva per visualizzare le fatture
            st.data_editor(
                fatture_df,
                column_config={
                    "ID": "ID Fattura",
                    "Cliente": "Cliente",
                    "Data": "Data Emissione",
                    "Importo (€)": "Importo Totale",
                    "Stato": {
                        "type": "select",
                        "options": ["Pagata", "In attesa"],
                    },
                    "Dettagli": "Prodotti/Servizi"
                },
                hide_index=True,
            )

            # Opzione per esportare le fatture
            if st.button("Esporta in CSV"):
                csv_data = fatture_df.to_csv(index=False, sep=';')
                st.download_button(
                    label="Scarica CSV",
                    data=csv_data,
                    file_name="fatture.csv",
                    mime="text/csv"
                )

        else:
            st.warning("Non ci sono fatture al momento.")

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        # Grafico riepilogativo delle fatture
        if st.session_state["invoices"]:
            fatture_df = pd.DataFrame(st.session_state["invoices"])

            fatture_df["Anno"] = fatture_df["Data"].apply(lambda x: x.year)
            fatture_riepilogo = fatture_df.groupby("Anno")["Importo (€)"].sum().reset_index()

            st.bar_chart(fatture_riepilogo, x="Anno", y="Importo (€)")

    elif choice == "Cost":
        st.markdown("<div class='section-header'>Gestione Costi</div>", unsafe_allow_html=True)
        st.info("Questa sezione permetterà di gestire i costi aziendali.")

    elif choice == "Supplier":
        st.markdown("<div class='section-header'>Gestione Fornitori</div>", unsafe_allow_html=True)
        st.info("Questa sezione permetterà di gestire i fornitori.")

if __name__ == "__main__":
    sistema_fatturazione()