import streamlit as st
import json
import os


# Nome del file per la memorizzazione delle sessioni
SESSION_FILE = "utils/user_sessions.json"

# Assicurati che la directory "data/" esista
if not os.path.exists("data"):
    os.makedirs("data")

# Funzione per caricare lo stato delle sessioni da file
def load_session_state():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as file:
            return json.load(file)
    return {}

# Funzione per salvare lo stato delle sessioni su file
def save_session_state(session_data):
    try:
        with open(SESSION_FILE, "w") as file:
            json.dump(session_data, file)
    except Exception as e:
        print(f"Errore nel salvare il file di sessione: {e}")

# Funzione per caricare lo stato delle sessioni da file
def load_session_state():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            print("Errore nel leggere il file di sessione. Creazione di un nuovo file.")
            return {}
    return {}

# Funzione per impostare lo stato dell'utente al login
def set_user_session(username, role):
    session_state = load_session_state()
    if username not in session_state:
        session_state[username] = {"role": role, "last_page": "dashboard", "data": {}}
    session_state[username]["role"] = role
    save_session_state(session_state)
    st.session_state["username"] = username
    st.session_state["role"] = role
    st.session_state["data"] = session_state[username]["data"]

# Funzione per aggiornare e salvare i dati specifici
def update_user_data(key, value):
    if "username" not in st.session_state:
        raise ValueError("L'utente non è autenticato.")
    session_state = load_session_state()
    username = st.session_state["username"]
    if username in session_state:
        session_state[username]["data"][key] = value
        save_session_state(session_state)
        st.session_state["data"] = session_state[username]["data"]

# Funzione per recuperare lo stato dell'utente
def restore_user_session(username):
    session_state = load_session_state()
    if username in session_state:
        user_data = session_state[username]
        st.session_state["username"] = username
        st.session_state["role"] = user_data["role"]
        st.session_state["data"] = user_data["data"]
        return True
    return False

# Funzione per il logout
def logout_user():
    if "username" in st.session_state:
        session_state = load_session_state()
        if st.session_state["username"] in session_state:
            session_state[st.session_state["username"]]["last_page"] = st.session_state["last_page"]
            save_session_state(session_state)
        st.session_state.clear()

# Funzione per verificare se l'utente è autenticato
def is_authenticated():
    return "username" in st.session_state and "role" in st.session_state

# Funzione per ottenere lo stato globale per un determinato campo
def get_global_state(key, default=None):
    if "data" in st.session_state:
        return st.session_state["data"].get(key, default)
    return default

# Funzione per recuperare lo stato dell'utente
def restore_user_session(username):
    session_state = load_session_state()
    if username in session_state:
        user_data = session_state[username]
        st.session_state["username"] = username
        st.session_state["role"] = user_data["role"]
        st.session_state["last_page"] = user_data["last_page"]
        st.session_state["data"] = user_data["data"]
        return True
    return False

# Funzione per il logout
def logout_user():
    if "username" in st.session_state:
        session_state = load_session_state()
        if st.session_state["username"] in session_state:
            session_state[st.session_state["username"]]["last_page"] = st.session_state["last_page"]
            save_session_state(session_state)
        st.session_state.clear()

# Funzione per verificare se l'utente è autenticato
def is_authenticated():
    return "username" in st.session_state and "role" in st.session_state
