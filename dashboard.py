import streamlit as st

from hpc import config, connection, credentials, slurm

st.set_page_config(page_title="HPC ML Dashboard", page_icon="🖥️", layout="wide")

st.markdown(
    """
    <style>
    .footer {
        position: fixed; bottom: 0; left: 0; width: 100%;
        text-align: center; padding: 6px 0;
        font-size: 0.75rem; color: #888;
        background: var(--background-color);
        border-top: 1px solid #e0e0e022;
        z-index: 999;
    }
    </style>
    <div class="footer">Luna Schon &times; Claude Code</div>
    """,
    unsafe_allow_html=True,
)

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
    st.title("Login — Uni Kassel HPC Cluster")

    st.info(
        "🔒 **Zugang nur aus dem Uni-Netz möglich.**  \n"
        "Von außerhalb bitte zuerst per **Cisco AnyConnect VPN** verbinden: `vpn.uni-kassel.de`",
        icon="ℹ️",
    )

    saved = credentials.load()

    with st.form("login_form"):
        st.text_input("Server", value=cfg["cluster"]["hostname"], disabled=True)
        username = st.text_input(
            "Uni-Kennung (uk...)",
            value=saved.get("username") or cfg["cluster"].get("username", ""),
        )
        password = st.text_input(
            "Passwort",
            type="password",
            value=saved.get("password", ""),
        )
        save_creds = st.checkbox(
            "Zugangsdaten lokal speichern",
            value=bool(saved),
            help="Speichert Kennung und Passwort in .credentials.yaml (nur auf diesem Gerät, nie im Git-Repo).",
        )
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
                    # resolve ~ via the server so it works on any cluster layout
                    stdout, _, _ = conn.run("echo $HOME")
                    home = stdout.strip()
                    raw_workdir = cfg["cluster"]["remote_workdir"]
                    workdir = raw_workdir.replace("~", home) if raw_workdir.startswith("~") else raw_workdir
                    # ensure workdir subdirs exist
                    conn.run(f"mkdir -p {workdir}/logs {workdir}/scripts {workdir}/data")

                    if save_creds:
                        credentials.save(username, password)
                    else:
                        credentials.clear()

                    st.session_state["ssh"] = conn
                    st.session_state["username"] = username
                    st.session_state["workdir"] = workdir
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
        st.page_link("pages/1_Submit_Job.py", label="Job einreichen", icon="🚀")
    with col2:
        st.page_link("pages/2_Monitor.py", label="Jobs überwachen", icon="📊")
    with col3:
        st.page_link("pages/3_Files.py", label="Dateien & Datensätze", icon="📁")
