import streamlit as st
from pathlib import Path
import calendar
from datetime import datetime

# Funzione per caricare il CSS
def load_css():
    css_path = Path("assets/styles.css")
    with open(css_path, "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Funzione per nascondere la sidebar
def hide_sidebar():
    hide_style = """
        <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        </style>
    """
    st.markdown(hide_style, unsafe_allow_html=True)

# Pagina iniziale neutra
def home_page():
    st.set_page_config(layout="wide")  # Imposta il layout senza sidebar
    hide_sidebar()  # Nasconde la sidebar
    load_css()  # Carica il CSS personalizzato
    st.title("Benvenuto!")
    st.image("assets/logo.png", width=200)  # Mostra il logo
    st.write("Benvenuto nella nostra piattaforma! Scegli un'opzione per continuare.")

    col1, col2 = st.columns([1, 1])  # Due colonne uguali
    with col1:
        if st.button("Login"):
            st.session_state["page"] = "login"  # Passa alla pagina di login
    with col2:
        if st.button("Registrazione"):
            st.session_state["page"] = "registration"  # Passa alla pagina di registrazione

# Pagina di Login
def login_page():
    st.set_page_config(layout="wide")  # Imposta il layout senza sidebar
    hide_sidebar()  # Nasconde la sidebar
    load_css()  # Carica il CSS personalizzato
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Accedi"):
            # Mock di autenticazione
            users = {"admin": ("password123", "admin"), "user": ("password", "user")}
            if username in users and password == users[username][0]:
                st.success(f"Benvenuto, {username}!")
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.session_state["role"] = users[username][1]
                st.session_state["page"] = "dashboard"  # Vai alla dashboard

                # Aggiorna i parametri della query per forzare il refresh
                st.experimental_set_query_params(page="dashboard")
            else:
                st.error("Credenziali non valide!")

    with col2:
        if st.button("Torna Indietro"):
            st.session_state["page"] = "home"  # Torna alla pagina iniziale
            st.experimental_set_query_params(page="home")
            
# Pagina di Registrazione
def registration_page():
    st.set_page_config(layout="wide")  # Imposta il layout senza sidebar
    hide_sidebar()  # Nasconde la sidebar
    load_css()  # Carica il CSS personalizzato
    st.title("Registrazione")
    username = st.text_input("Crea il tuo Username")
    password = st.text_input("Crea la tua Password", type="password")
    confirm_password = st.text_input("Conferma la tua Password", type="password")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Registrati"):
            if password != confirm_password:
                st.error("Le password non corrispondono!")
            elif username.strip() == "" or password.strip() == "":
                st.error("Username e Password non possono essere vuoti!")
            else:
                st.success("Registrazione completata! Ora puoi effettuare il login.")
                st.session_state["page"] = "login"  # Redirige alla pagina di login

    with col2:
        if st.button("Torna Indietro"):
            st.session_state["page"] = "home"  # Torna alla pagina iniziale

# Pagina con calendario e task
def calendar_page():
    st.title("Calendario e Task")
    load_css()  # Carica il CSS personalizzato

    # Visualizza il mese corrente
    today = datetime.today()
    year, month = today.year, today.month

    # Genera il calendario
    st.markdown(f"### {calendar.month_name[month]} {year}")
    cal = calendar.TextCalendar()
    st.text(cal.formatmonth(year, month))

    # Aggiungi una task
    st.markdown("### Aggiungi una nuova task")
    task_date = st.date_input("Data della task", value=today)
    task_description = st.text_area("Descrizione della task")

    if st.button("Aggiungi Task"):
        if "tasks" not in st.session_state:
            st.session_state["tasks"] = []
        st.session_state["tasks"].append({"date": task_date, "description": task_description})
        st.success("Task aggiunta con successo!")

    # Visualizza le task
    if "tasks" in st.session_state and st.session_state["tasks"]:
        st.markdown("### Task Pianificate")
        for task in st.session_state["tasks"]:
            st.write(f"- **{task['date']}**: {task['description']}")

# Dashboard con navigazione laterale
def dashboard():
    st.set_page_config(layout="wide")  # Mostra il layout con sidebar
    load_css()  # Carica il CSS personalizzato
    if st.session_state.get("authenticated"):
        menu = ["Profilo Utente", "Calendario e Task", "Statistiche"]

        choice = st.sidebar.radio("Navigazione", menu)

        # Gestisci le pagine
        if choice == "Profilo Utente":
            st.title("Profilo Utente")
            st.write("Gestisci le impostazioni del tuo profilo.")
        elif choice == "Calendario e Task":
            calendar_page()
        elif choice == "Statistiche":
            st.title("Statistiche")
            st.write("Visualizza statistiche e report.")
    else:
        st.error("Devi prima effettuare il login.")
        st.session_state["page"] = "login"
        st.experimental_rerun()

# Controllo dello stato di autenticazione
if "page" not in st.session_state:
    st.session_state["page"] = "home"

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Routing condizionale
if not st.session_state.get("authenticated") and st.session_state["page"] in ["dashboard", "gestione prodotti", "statistiche"]:
    st.session_state["page"] = "login"

# Mostra la pagina corrente
if st.session_state["page"] == "home":
    home_page()
elif st.session_state["page"] == "login":
    login_page()
elif st.session_state["page"] == "registration":
    registration_page()
elif st.session_state["page"] == "dashboard" and st.session_state.get("authenticated"):
    dashboard()
else:
    st.error("Accesso non autorizzato! Torna al Login.")


    