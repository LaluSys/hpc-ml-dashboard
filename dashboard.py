import streamlit as st

from hpc import config, connection, slurm

st.set_page_config(page_title="HPC ML Dashboard", page_icon="", layout="wide")

cfg = config.load()

# --- Sidebar: connection status ---
with st.sidebar:
    st.title("HPC ML Dashboard")
    if "ssh" in st.session_state and st.session_state["ssh"].is_alive():
        st.success(f"Verbunden als **{st.session_state['username']}**")
        st.caption(cfg["cluster"]["hostname"])
        if st.button("Trennen"):
            st.session_state["ssh"].close()
            del st.session_state["ssh"]
            st.rerun()

        try:
            df = slurm.sinfo_summary(st.session_state["ssh"])
            if not df.empty:
                st.caption("Cluster-Partitionen")
                st.dataframe(df, hide_index=True, use_container_width=True)
        except Exception:
            pass
    else:
        st.warning("Nicht verbunden")

# --- Main: Login ---
if "ssh" not in st.session_state or not st.session_state["ssh"].is_alive():
    st.title("Login")

    with st.form("login_form"):
        hostname = st.text_input("Server", value=cfg["cluster"]["hostname"], disabled=True)
        username = st.text_input("Uni-Kennung (uk...)", value=cfg["cluster"].get("username", ""))
        password = st.text_input("Passwort", type="password")
        submitted = st.form_submit_button("Verbinden", type="primary")

    if submitted:
        if not username or not password:
            st.error("Bitte Kennung und Passwort eingeben.")
        else:
            with st.spinner("Verbinde..."):
                try:
                    conn = connection.SSHConnection(
                        hostname=cfg["cluster"]["hostname"],
                        username=username,
                        password=password,
                        port=cfg["cluster"]["port"],
                    )
                    st.session_state["ssh"] = conn
                    st.session_state["username"] = username
                    st.session_state["workdir"] = cfg["cluster"]["remote_workdir"].replace("~", f"/gpfs/home08/{username}")
                    st.session_state["cfg"] = cfg
                    st.success("Verbunden!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Verbindung fehlgeschlagen: {e}")
else:
    st.title("HPC ML Dashboard")
    st.info("Nutze die Navigation links, um Jobs einzureichen, zu überwachen oder Dateien zu verwalten.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.page_link("pages/1_Submit_Job.py", label="Job einreichen", icon="")
    with col2:
        st.page_link("pages/2_Monitor.py", label="Jobs überwachen", icon="")
    with col3:
        st.page_link("pages/3_Files.py", label="Dateien", icon="")
