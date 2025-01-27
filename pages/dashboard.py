import streamlit as st
import datetime
import pandas as pd
import random
import plotly.express as px

# Funzione per caricare il CSS
def load_css():
    css_path = "assets/styles.css"
    with open(css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Funzione per la pagina Dashboard
def dashboard_page():
    st.set_page_config(page_title="Dashboard", layout="wide")

    # Caricamento CSS personalizzato
    load_css()

    # Header della Dashboard
    st.markdown("<div class='dashboard-header'>Benvenuto nella Dashboard 🎉</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='welcome-message'>Ciao, <strong>{st.session_state.get('username', 'Utente')}</strong>! Oggi è {datetime.datetime.now().strftime('%A, %d %B %Y')}.</div>", unsafe_allow_html=True)

    # Layout per metriche principali con card stilizzate
    st.markdown("<div class='metrics-container'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>Task Completate</h3>
            <p><strong>15</strong></p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>Task Pianificate</h3>
            <p><strong>25</strong></p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>Task in Scadenza</h3>
            <p><strong>5</strong></p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Sezione con grafico dinamico
    st.markdown("<div class='section-header'>Distribuzione delle Task</div>", unsafe_allow_html=True)
    task_data = {
        "Categorie": ["Lavoro", "Personale", "Studio"],
        "Numero di Task": [10, 20, 15]
    }
    df_task = pd.DataFrame(task_data)

    fig = px.bar(
        df_task,
        x="Categorie",
        y="Numero di Task",
        color="Categorie",
        title="Distribuzione delle Task",
        labels={"Numero di Task": "Task"},
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Sezione per visualizzare prossime task con tabella interattiva
    st.markdown("<div class='section-header'>Prossime Task</div>", unsafe_allow_html=True)
    sample_data = {
        "Data": [datetime.date.today() + datetime.timedelta(days=i) for i in range(1, 6)],
        "Descrizione": [f"Task {i}" for i in range(1, 6)],
        "Stato": ["In corso", "Completata", "In ritardo", "Completata", "In corso"]
    }

    task_df = pd.DataFrame(sample_data)

    # Trasformare la tabella in interattiva
    st.data_editor(
        task_df,
        column_config={
            "Data": "Data di scadenza",
            "Descrizione": "Dettagli Task",
            "Stato": {
                "type": "select",
                "options": ["In corso", "Completata", "In ritardo"],
            },
        },
        hide_index=True,
    )

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Sezione per prodotti dinamici con card dettagliate
    st.markdown("<div class='section-header'>Prodotti in Evidenza</div>", unsafe_allow_html=True)
    product_data = {
        "Nome": ["Prodotto A", "Prodotto B", "Prodotto C"],
        "Prezzo (€)": [19.99, 29.99, 39.99],
        "Disponibilità": ["Disponibile", "Esaurito", "Disponibile"],
        "Immagine": [
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150",
            "https://via.placeholder.com/150"
        ]
    }

    product_df = pd.DataFrame(product_data)

    col1, col2, col3 = st.columns(3)
    for i, row in product_df.iterrows():
        with [col1, col2, col3][i % 3]:
            st.markdown(f"""
            <div class='product-card'>
                <img src="{row['Immagine']}" alt="{row['Nome']}" class='product-image'>
                <h4>{row['Nome']}</h4>
                <p>Prezzo: <strong>{row['Prezzo (€)']}€</strong></p>
                <p>Stato: <strong>{row['Disponibilità']}</strong></p>
                <button class='custom-button'>Acquista</button>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Collegamenti rapidi
    st.markdown("<div class='section-header'>Collegamenti Rapidi</div>", unsafe_allow_html=True)
    st.markdown("<div class='quick-links-container'>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="quick-link-card">
            <img src="https://via.placeholder.com/100" class="quick-link-icon" alt="Calendario">
            <p>Calendario</p>
            <button class="custom-button" onclick="alert('Vai al Calendario')">Vai</button>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="quick-link-card">
            <img src="https://via.placeholder.com/100" class="quick-link-icon" alt="Statistiche">
            <p>Statistiche</p>
            <button class="custom-button" onclick="alert('Vai alle Statistiche')">Vai</button>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="quick-link-card">
            <img src="https://via.placeholder.com/100" class="quick-link-icon" alt="Profilo">
            <p>Profilo Utente</p>
            <button class="custom-button" onclick="alert('Vai al Profilo Utente')">Vai</button>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    dashboard_page()
