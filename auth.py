import streamlit as st

# Funzione per verificare l'utente (mock)
def authenticate(username, password):
    # Utenti mock: username, password, ruolo (user/admin)
    users = {"admin": ("password123", "admin"), "user": ("password", "user")}
    if username in users and users[username][0] == password:
        return users[username][1]  # Restituisce il ruolo dell'utente
    return None

# Funzione per il routing delle pagine
def route_pages(page):
    if page == "profilo":
        import pages.profilo as profilo
        profilo.profilo_page()
    elif page == "catalogo":
        import pages.catalogo as catalogo
        catalogo.catalogo_page()
    elif page == "catologo_def":
        import pages.catologo_def as catologo_def
        catologo_def.catologo_def_page()
    elif page == "dashboard":
        import pages.dashboard as dashboard
        dashboard.dashboard_page()
    elif page == "finanze" and st.session_state.get("role") == "admin":
        import pages.finanze as finanze
        finanze.finanze_page()
    else:
        st.error("Pagina non trovata o accesso negato!")

# Pagina Login
def login_page():
    st.title("Login e Registrazione")

    # Input dell'utente
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        role = authenticate(username, password)
        if role:
            st.success(f"Benvenuto {username}!")
            # Salva lo stato della sessione
            st.session_state["username"] = username
            st.session_state["role"] = role
            st.session_state["authenticated"] = True
            # Simula il reindirizzamento impostando parametri nella query
            st.query_params.update({"page": "profilo"})  # Redirect alla pagina profilo
        else:
            st.error("Credenziali non valide!")

# Check stato utente
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Routing
if st.session_state["authenticated"]:
    # Ottieni i parametri dalla query per capire quale pagina mostrare
    query_params = st.query_params
    page = query_params.get("page", ["profilo"])[0]
    route_pages(page)
else:
    login_page()
